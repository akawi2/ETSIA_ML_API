import os
import json
import logging
import asyncio
import httpx
from fastapi import FastAPI, BackgroundTasks, HTTPException
from schemas import MetricEvent
from typing import List, Dict, Any

# --- Configuration ---
GA4_MEASUREMENT_ID = os.getenv("GA4_MEASUREMENT_ID")
GA4_API_SECRET = os.getenv("GA4_API_SECRET")
GA4_URL = f"https://www.google-analytics.com/mp/collect?measurement_id={GA4_MEASUREMENT_ID}&api_secret={GA4_API_SECRET}"
CATALOG_PATH = "metrics_catalog.json"

# --- Logger ---
logger = logging.getLogger("ga4_bridge")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# --- Chargement du Catalogue ---
def load_catalog():
    try:
        with open(CATALOG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Impossible de charger le catalogue: {e}")
        return []

CATALOG = load_catalog()

app = FastAPI(title="GA4 Monitoring Bridge")

# --- Logique d'Alerte ---
def evaluate_alerts(event: MetricEvent) -> Dict[str, str]:
    """Compare les métriques reçues avec le catalogue et retourne des tags d'alerte."""
    alert_tags = {}

    for rule in CATALOG:
        # 1. Filtre par service
        if rule["service"] != event.service:
            continue

        # 2. Filtre par modèle (si spécifié dans la règle)
        if "model" in rule and rule["model"]:
            if rule["model"] != event.model_name:
                continue

        # 3. Vérification de la métrique
        metric_key = rule["metric"]
        if metric_key in event.params:
            val = event.params[metric_key]
            thresh = rule["threshold"]
            op = rule["operator"]

            triggered = False
            if op == ">" and val > thresh: triggered = True
            elif op == "<" and val < thresh: triggered = True
            elif op == ">=" and val >= thresh: triggered = True
            elif op == "<=" and val <= thresh: triggered = True

            if triggered:
                logger.warning(f"ALERTE: {event.service} - {metric_key}: {val} {op} {thresh}")
                # On ajoute ces champs pour qu'ils soient filtrables dans GA4
                alert_tags["alert_triggered"] = "true"
                alert_tags["alert_reason"] = f"{metric_key}_fail"
                alert_tags["alert_priority"] = rule["priority"]

    return alert_tags

# --- Envoi vers GA4 ---
async def send_to_ga4(event_data: dict):
    async with httpx.AsyncClient() as client:
        try:
            # Structure stricte Measurement Protocol
            payload = {
                "client_id": event_data["client_id"],
                "events": [{
                    "name": event_data["event_name"],
                    "params": event_data["params"]
                }]
            }

            # Debug log
            # logger.info(f"Sending to GA4: {payload}")

            resp = await client.post(GA4_URL, json=payload)
            if resp.status_code != 204:
                logger.error(f"Erreur GA4 ({resp.status_code}): {resp.text}")

        except Exception as e:
            logger.error(f"Exception réseau GA4: {e}")

@app.post("/log_metric")
async def log_metric(event: MetricEvent, background_tasks: BackgroundTasks):
    """Endpoint principal appelé par l'application métier."""

    if not GA4_MEASUREMENT_ID or not GA4_API_SECRET:
        logger.error("GA4 Credentials manquants")
        return {"status": "error", "message": "Missing config"}

    # 1. Enrichir avec les alertes
    alert_tags = evaluate_alerts(event)
    event.params.update(alert_tags)

    # 2. Standardisation obligatoire (strings pour les dimensions)
    event.params["service"] = str(event.service)
    event.params["model_name"] = str(event.model_name)

    # 3. Envoi asynchrone (ne bloque pas l'API appelante)
    background_tasks.add_task(send_to_ga4, event.dict())

    return {"status": "queued", "alerts": bool(alert_tags)}

@app.get("/health")
def health():
    return {"status": "ok", "catalog_rules": len(CATALOG)}