import time
import random
import requests
import os
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI(title="Yansnet API")

BRIDGE_URL = "http://ga4-bridge:5000/log_metric"


def emit_metric(service: str,
                event_name: str,
                params: dict,
                model: str = None):
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

    emit_metric(service="api_gateway",
                event_name="api_request",
                params={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "latency": int(process_time)
                })
    return response


# --- Endpoints Métiers Simulés ---


# 1. Hate Comment Detection
@app.post("/predict_hatecomment")
def predict_hate():
    # Simulation Latence & Modèle
    time.sleep(random.uniform(0.05, 0.6))  # Parfois > 500ms (Alerte)

    result = {
        "is_hate": random.choice([True, False]),
        "confidence": random.uniform(0.7, 0.99)
    }

    emit_metric(service="hate_comment",
                event_name="detect_hate",
                model="google-bert-multilingual",
                params={
                    "latency": int(random.uniform(50, 600)),
                    "precision": 0.82,
                    "recall": 0.86,
                    "f1_score": 0.87,
                    "false_positive_rate": 0.12
                })
    return result


# 2. Depression Detection
@app.post("/predict_depression")
def predict_depression(model_type: str = "camembert"):
    # Seuils latence: Camembert > 500ms, Qwen > 1000ms
    if model_type == "qwen":
        model_name = "qwen2.5:1.5b"
        latency = random.uniform(200, 1100)
    else:
        model_name = "camembert-base"
        latency = random.uniform(30, 550)

    confidence = random.uniform(0.5, 0.99)  # Parfois < 0.6 (Alerte)

    emit_metric(service="depression_detection",
                event_name="detect_depression",
                model=model_name,
                params={
                    "latency":
                    int(latency),
                    "confidence":
                    confidence,
                    "ram_usage":
                    random.choice([500, 2100]),
                    "severity":
                    random.choice(["Critique", "Élevée", "Moyenne", "Faible"])
                })
    return {"status": "analyzed"}


# 3. Depression Detection
@app.post("/generate_content")
def generate_content():
    # Simulation Génération (PDF Page 8-9)
    # Latence parfois > 30s (Critique)
    metrics = {
        "latency": int(random.uniform(5000, 35000)),
        "inappropriate_content_rate": 0.005
    }
    emit_metric("content_generation",
                "generate_post",
                metrics,
                model="llama3.2:3b")
    return {"content": "Post généré..."}


# 4. Depression Detection
@app.post("/caption_image")
def caption_image():
    # Simulation Captioning (PDF Page 2-3)
    metrics = {
        "latency": int(random.uniform(800, 2500)),
        "bleu_score": random.uniform(0.1, 0.5)
    }
    emit_metric("image_captioning", "image_scan", metrics, model="git-large")
    return {"caption": "Une photo de..."}


# --- Endpoints Health ---
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/models")
def list_models():
    return ["camembert-base", "qwen2.5:1.5b", "google-bert", "llama3.2:3b"]
