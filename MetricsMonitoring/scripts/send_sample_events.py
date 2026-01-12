import requests
import random
import time

URL = "http://localhost:5000/log_metric"

def test_alert():
    print("--- Envoi d'une alerte Dépression (Latence Critique) ---")
    payload = {
        "service": "depression_detection",
        "model_name": "camembert-base",
        "event_name": "model_prediction",
        "params": {
            [cite_start]"latency": 600, # Seuil est 500ms [cite: 33] -> Doit déclencher alerte
            "confidence": 0.9,
            "ram_usage": 500
        }
    }
    r = requests.post(URL, json=payload)
    print(f"Status: {r.status_code}, Response: {r.json()}")

def test_ok():
    print("--- Envoi d'un event OK ---")
    payload = {
        "service": "hate_comment",
        "model_name": "bert",
        "event_name": "model_prediction",
        "params": {
            "latency": 100,
            "precision": 0.95
        }
    }
    r = requests.post(URL, json=payload)
    print(f"Status: {r.status_code}, Response: {r.json()}")

if __name__ == "__main__":
    test_ok()
    test_alert()