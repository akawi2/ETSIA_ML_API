## Monitoring avec GA4 
On fera selon cette architecture
```
┌─────────────────────────────────────────────────────┐
│ FastAPI (Yansnet) + Modèles ML                      │
│ (HateCommentBert, SensitiveImageCaption, etc.)      │
└─────────────────┬──────────────────────────────────┘
                  │
                  │ Événements ML
                  │ (latence, scores, erreurs)
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 🐳 Docker: Middleware "GA4-Bridge"                  │
│                                                      │
│  - Reçoit métriques (via socket/queue/logs)        │
│  - Transforme en GA4 events                         │
│  - Envoie via Measurement Protocol API              │
└─────────────────┬──────────────────────────────────┘
                  │
                  │ HTTPS POST
                  │ Measurement Protocol
                  │
                  ▼
        ┌─────────────────────┐
        │  Google Analytics 4  │ ☁️ (en ligne)
        │  Dashboards / Rapports
        └─────────────────────┘

```

### 1. Architecture Logique
Nous allons implémenter le schéma suivant pour garantir le découplage entre notre application métier et l'analytique :

```mermaid
graph LR
    A[Client/Utilisateur] -->|Requête API| B(FastAPI Yansnet)
    B -->|Log Metric (Async)| C{GA4-Bridge}
    C -->|Validation & Alerting| C
    C -->|Measurement Protocol| D[Google Analytics 4]
    style C fill:#f9f,stroke:#333,stroke-width:2px

```

---

### 2. Source de Vérité : `metrics_catalog.json`
Ce fichier est le cœur du système. Il traduit les exigences du PDF en règles machine pour le Bridge. Il permet de modifier les seuils sans toucher au code.

```json
[
  {
    "service": "hate_comment",
    "metric": "latency",
    "threshold": 500,
    "operator": ">",
    "unit": "ms",
    "priority": "Moyenne",
    [cite_start]"source_ref": "[cite: 4]"
  },
  {
    "service": "hate_comment",
    "metric": "false_positive_rate",
    "threshold": 0.10,
    "operator": ">",
    "unit": "ratio",
    "priority": "Critique",
    [cite_start]"source_ref": "[cite: 4]"
  },
  {
    "service": "image_captioning",
    "metric": "latency",
    "threshold": 2000,
    "operator": ">",
    "unit": "ms",
    "priority": "Moyenne",
    [cite_start]"source_ref": "[cite: 10]"
  },
  {
    "service": "image_captioning",
    "metric": "bleu_score",
    "threshold": 0.25,
    "operator": "<",
    "unit": "score",
    "priority": "Haute",
    [cite_start]"source_ref": "[cite: 10]"
  },
  {
    "service": "depression_detection",
    "model": "camembert-base",
    "metric": "latency",
    "threshold": 500,
    "operator": ">",
    "unit": "ms",
    "priority": "Moyenne",
    [cite_start]"source_ref": "[cite: 28, 33]"
  },
  {
    "service": "depression_detection",
    "model": "qwen2.5:1.5b",
    "metric": "latency",
    "threshold": 1000,
    "operator": ">",
    "unit": "ms",
    "priority": "Moyenne",
    [cite_start]"source_ref": "[cite: 28, 35]"
  },
  {
    "service": "depression_detection",
    "metric": "confidence",
    "threshold": 0.60,
    "operator": "<",
    "unit": "probability",
    "priority": "Moyenne",
    [cite_start]"source_ref": "[cite: 28, 30]"
  },
  {
    "service": "depression_detection",
    "metric": "ram_usage",
    "model": "camembert-base",
    "threshold": 600,
    "operator": ">",
    "unit": "MB",
    "priority": "Moyenne",
    [cite_start]"source_ref": "[cite: 33]"
  },
  {
    "service": "content_generation",
    "metric": "latency",
    "threshold": 30000,
    "operator": ">",
    "unit": "ms",
    "priority": "Moyenne",
    [cite_start]"source_ref": "[cite: 47]"
  },
  {
    "service": "content_generation",
    "metric": "inappropriate_content_rate",
    "threshold": 0.01,
    "operator": ">",
    "unit": "ratio",
    "priority": "Critique",
    [cite_start]"source_ref": "[cite: 47]"
  }
]

```

---

### 3. Le Middleware (GA4-Bridge)
Ce service reçoit les logs, vérifie les seuils du catalogue ci-dessus, injecte des flags d'alerte et envoie à GA4.

**Structure des fichiers :**

* `ga4_bridge/Dockerfile`
* `ga4_bridge/requirements.txt` (`fastapi`, `uvicorn`, `httpx`, `pydantic`)
* `ga4_bridge/main.py`

**Fichier : `ga4_bridge/main.py**`

```python
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

```

---

### 4. L'Application Yansnet (FastAPI Instrumentée)
Voici comment ton application principale doit envoyer les données. Nous avons inclus les endpoints simulés et le middleware de latence.

**Fichier : `fastapi_app/app/main.py**`

```python
import time
import random
import requests
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="Yansnet API")

BRIDGE_URL = "http://ga4-bridge:5000/log_metric"

def emit_metric(service: str, event_name: str, params: dict, model: str = None):
    try:
        payload = {
            "service": service,
            "event_name": event_name,
            "model_name": model,
            "params": params,
            "client_id": "yansnet_prod_v1"
        }
        # Timeout très court pour ne pas ralentir l'app métier
        requests.post(BRIDGE_URL, json=payload, timeout=0.5)
    except Exception as e:
        print(f"Monitoring Error: {e}")

# --- Middleware Global de Latence API ---
@app.middleware("http")
async def monitor_latency(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    emit_metric(
        service="api_gateway",
        event_name="api_request",
        params={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "latency": int(process_time)
        }
    )
    return response

# --- Endpoints Métiers Simulés ---

# [cite_start]1. Hate Comment Detection [cite: 3]
@app.post("/predict_hatecomment")
def predict_hate():
    # Simulation Latence & Modèle
    [cite_start]time.sleep(random.uniform(0.05, 0.6)) # Parfois > 500ms (Alerte [cite: 4])
    
    result = {
        "is_hate": random.choice([True, False]),
        "confidence": random.uniform(0.7, 0.99)
    }
    
    emit_metric(
        service="hate_comment",
        event_name="detect_hate",
        model="google-bert-multilingual",
        params={
            "latency": int(random.uniform(50, 600)),
            "precision_alert_check": 0.82, # Mock value for metric
            "recall_alert_check": 0.86
        }
    )
    return result

# [cite_start]2. Depression Detection [cite: 22]
@app.post("/predict_depression")
def predict_depression(model_type: str = "camembert"):
    # [cite_start]Seuils latence: Camembert > 500ms, Qwen > 1000ms [cite: 28]
    if model_type == "qwen":
        model_name = "qwen2.5:1.5b"
        latency = random.uniform(200, 1100) 
    else:
        model_name = "camembert-base"
        latency = random.uniform(30, 550)

    [cite_start]confidence = random.uniform(0.5, 0.99) # Parfois < 0.6 (Alerte [cite: 30])
    
    emit_metric(
        service="depression_detection",
        event_name="detect_depression",
        model=model_name,
        params={
            "latency": int(latency),
            "confidence": confidence,
            "ram_usage": random.choice([500, 2100]), # Mock MB
            "severity": random.choice(["Critique", "Élevée", "Moyenne", "Faible"])
        }
    )
    return {"status": "analyzed"}

# [cite_start]--- Endpoints Health [cite: 69] ---
@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/api/v1/models")
def list_models():
    [cite_start]# [cite: 37, 18, 59]
    return ["camembert-base", "qwen2.5:1.5b", "google-bert", "llama3.2:3b"]

```

---

### 5. Orchestration (Docker Compose)Fichier `docker-compose.yml` pour tout lancer.

```yaml
services:
  ga4-bridge:
    build: ./ga4_bridge
    ports:
      - "5000:5000"
    volumes:
      - ./metrics_catalog.json:/app/metrics_catalog.json
    environment:
      - GA4_MEASUREMENT_ID=${GA4_MEASUREMENT_ID}
      - GA4_API_SECRET=${GA4_API_SECRET}
    command: uvicorn main:app --host 0.0.0.0 --port 5000

  fastapi-app:
    build: ./fastapi_app
    ports:
      - "8000:8000"
    depends_on:
      - ga4-bridge
    environment:
      - BRIDGE_URL=http://ga4-bridge:5000/log_metric

```

Fichier `.env` (ne pas commiter) :

```
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=xXxXxXxXxXxXxXx

```

---

### 6. Guide de Configuration Google Analytics 4 
L'infrastructure ne sert à rien si GA4 n'est pas configuré pour recevoir ces données "custom".

**Étape 1 : Création des Définitions Personnalisées**
Dans GA4 > Admin > Définitions personnalisées (Custom definitions), créez les dimensions et métriques suivantes pour qu'elles apparaissent dans vos rapports.

**Dimensions (Scope: Event)**

* `service` (ex: hate_comment, depression_detection)
* `model_name` (ex: camembert-base, qwen)
* `alert_triggered` (valeur "true" si un seuil est franchi)
* `alert_reason` (ex: latency_>_500)
* `alert_priority` (Critique, Moyenne)
* 
`severity` (pour dépression : Critique, Élevée...) 



**Métriques (Scope: Event, Unité: Standard ou Durée)**

* `latency` (Unité: ms)
* `confidence` (Standard, décimal)
* `ram_usage` (Standard, MB)
* `bleu_score` (Standard)
* `inappropriate_content_rate` (Standard)

**Étape 2 : Créer un Rapport d'Exploration (Dashboard)**

1. Aller dans "Explorer".
2. Créer un rapport "Monitoring Yansnet".
3. **Technique** : Glisser `Event Name` en ligne et `latency` (Moyenne) en valeur.
4. **Alerte** : Créer un tableau filtré où `alert_triggered` est "true". Cela vous donnera la liste exacte des incidents de monitoring (Dépression Latence > 500ms, etc.).

### 7. Scripts de validation
Pour tester sans lancer toute l'app, utilise ce script Python simple (`send_sample_events.py`) :

```python
import requests
import random

BRIDGE = "http://localhost:5000/log_metric"

# [cite_start]Test Alert Dépression Latence [cite: 33]
data_alert = {
    "service": "depression_detection",
    "event_name": "detect_depression",
    "model_name": "camembert-base",
    "params": {
        "latency": 600, # > 500ms -> Doit déclencher une alerte
        "confidence": 0.8
    }
}

requests.post(BRIDGE, json=data_alert)
print("Event envoyé. Vérifiez le Realtime GA4 pour 'alert_triggered=true'.")

```
https://www.youtube.com/watch?v=r_eoeU2qUn0