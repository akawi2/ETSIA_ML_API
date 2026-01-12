import os
import json
import logging
import asyncio
import httpx
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Configuration
GA4_MEASUREMENT_ID = os.getenv("GA4_MEASUREMENT_ID")
GA4_API_SECRET = os.getenv("GA4_API_SECRET")
GA4_ENDPOINT = f"https://www.google-analytics.com/mp/collect?measurement_id={GA4_MEASUREMENT_ID}&api_secret={GA4_API_SECRET}"

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GA4-Bridge")

# Load Metrics Catalog
try:
    with open("metrics_catalog.json", "r") as f:
        CATALOG = json.load(f)
except FileNotFoundError:
    logger.warning("metrics_catalog.json not found. Alerting logic will be disabled.")
    CATALOG = []

app = FastAPI(title="GA4-Bridge Middleware")

# --- Pydantic Models ---
class MetricEvent(BaseModel):
    service: str
    event_name: str
    model_name: Optional[str] = None
    params: Dict[str, Any]
    client_id: str = "yansnet_system" 

# --- Core Logic ---

def check_alerts(event: MetricEvent) -> Dict[str, Any]:
    """Enrichit les params avec des indicateurs d'alerte si les seuils sont franchis."""
    alerts = {}

    for rule in CATALOG:
        # Filtrage par service et modèle (si spécifié dans la règle)
        if rule["service"] != event.service:
            continue
        if "model" in rule and rule["model"] and rule["model"] != event.model_name:
            continue

        metric_key = rule["metric"]
        if metric_key in event.params:
            value = event.params[metric_key]
            threshold = rule["threshold"]
            operator = rule["operator"]

            is_alert = False
            if operator == ">" and value > threshold:
                is_alert = True
            elif operator == "<" and value < threshold:
                is_alert = True
            elif operator == ">=" and value >= threshold:
                [cite_start]is_alert = True # Pour les cas critiques comme sévérité dépression [cite: 30]

            if is_alert:
                alerts["alert_triggered"] = "true" # GA4 string param
                alerts["alert_reason"] = f"{metric_key}_{operator}_{threshold}"
                alerts["alert_priority"] = rule["priority"]
                logger.warning(f"ALERT: {event.service} {metric_key}={value} (Threshold {operator} {threshold})")

    return alerts

async def send_to_ga4(payload: dict):
    async with httpx.AsyncClient() as client:
        try:
            # GA4 Measurement Protocol Payload Structure
            ga4_body = {
                "client_id": payload.get("client_id", "yansnet_system"),
                "events": [{
                    "name": payload["event_name"],
                    "params": {
                        "service": payload["service"],
                        "model_name": payload["model_name"] or "default",
                        **payload["params"]
                    }
                }]
            }

            response = await client.post(GA4_ENDPOINT, json=ga4_body)
            if response.status_code != 204:
                logger.error(f"GA4 Error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to send to GA4: {e}")

# --- Endpoints ---

@app.post("/log_metric")
async def log_metric(event: MetricEvent, background_tasks: BackgroundTasks):
    """Réçoit une métrique brute, évalue les alertes, envoie à GA4."""

    # 1. Vérification des seuils
    alert_params = check_alerts(event)
    event.params.update(alert_params)

    # 2. Envoi asynchrone (Non-blocking)
    background_tasks.add_task(send_to_ga4, event.dict())

    return {"status": "queued"}

@app.get("/health")
def health_check():
    [cite_start]"""Conforme à [cite: 69]"""
    return {"status": "ok", "service": "ga4-bridge"}