"""
Script de test pour envoyer des données simulées vers Supabase Edge Function
Usage: python scripts/send_test_data.py
"""

import requests
import random
import time
import os
from datetime import datetime

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jxyzkqrdghawvyzdvjku.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp4eXprcXJkZ2hhd3Z5emR2amt1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgxMTUxOTIsImV4cCI6MjA4MzY5MTE5Mn0.gbEhh-QKLkPnhw9A_z5M2F4zAczuf5MsV6uWfXI-tmg")

EDGE_FUNCTION_URL = f"{SUPABASE_URL}/functions/v1/evaluate-alerts"

HEADERS = {
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

# Configuration complète des modèles (8 modèles)
MODELS = {
    # HATE COMMENT DETECTION
    "google-bert-multilingual": {
        "provider": "huggingface",
        "service": "hate_comment",
        "endpoint": "/api/v1/hate/predict",
        "latency_range": (50, 600),
        "predictions": ["HATE", "NORMAL"],
        "severities": None,
        "metrics": ["precision", "recall", "f1_score", "false_positive_rate"]
    },
    
    # DEPRESSION DETECTION
    "camembert-depression": {
        "provider": "huggingface",
        "service": "depression_detection",
        "endpoint": "/api/v1/depression/predict",
        "latency_range": (30, 250),
        "predictions": ["DÉPRESSION", "NORMAL"],
        "severities": ["Aucune", "Faible", "Moyenne", "Élevée", "Critique"],
        "metrics": ["confidence", "precision", "recall"]
    },
    "qwen-depression": {
        "provider": "ollama",
        "service": "depression_detection",
        "endpoint": "/api/v1/depression/predict",
        "latency_range": (200, 1200),
        "predictions": ["DÉPRESSION", "NORMAL"],
        "severities": ["Aucune", "Faible", "Moyenne", "Élevée", "Critique"],
        "metrics": ["confidence"]
    },
    "xlm-roberta-depression": {
        "provider": "huggingface",
        "service": "depression_detection",
        "endpoint": "/api/v1/depression/predict",
        "latency_range": (100, 550),
        "predictions": ["DÉPRESSION", "NORMAL"],
        "severities": ["Aucune", "Faible", "Moyenne", "Élevée", "Critique"],
        "metrics": ["confidence"]
    },
    
    # CONTENT GENERATION
    "llama-generation": {
        "provider": "ollama",
        "service": "content_generation",
        "endpoint": "/api/v1/content/generate",
        "latency_range": (5000, 35000),
        "predictions": ["SUCCESS", "PARTIAL", "FAILED"],
        "severities": None,
        "metrics": ["ttr", "repetition_rate"]
    },
    "llama-fallback": {
        "provider": "ollama",
        "service": "content_generation",
        "endpoint": "/api/v1/content/generate",
        "latency_range": (2000, 12000),
        "predictions": ["SUCCESS", "PARTIAL", "FAILED"],
        "severities": None,
        "metrics": ["ttr"]
    },
    
    # IMAGE CAPTIONING
    "git-large-captioning": {
        "provider": "huggingface",
        "service": "image_captioning",
        "endpoint": "/api/v1/caption/generate",
        "latency_range": (800, 3500),
        "predictions": ["SAFE", "SENSITIVE", "BLOCKED"],
        "severities": None,
        "metrics": ["bleu_score", "keyword_coverage"]
    },
    "opus-mt-translation": {
        "provider": "huggingface",
        "service": "image_captioning",
        "endpoint": "/api/v1/translate",
        "latency_range": (50, 300),
        "predictions": ["SUCCESS"],
        "severities": None,
        "metrics": []
    }
}


def send_prediction(model_name: str, config: dict) -> dict:
    """Envoie une prédiction simulée"""
    
    latency = random.uniform(*config["latency_range"])
    prediction = random.choice(config["predictions"])
    confidence = random.uniform(0.5, 0.99) if prediction not in ["FAILED", "BLOCKED"] else random.uniform(0.3, 0.6)
    severity = random.choice(config["severities"]) if config["severities"] else None
    fallback = random.random() < 0.05
    
    payload = {
        "event_type": "prediction",
        "model_name": model_name,
        "provider": config["provider"],
        "endpoint": config["endpoint"],
        "request_id": f"req_{int(time.time() * 1000)}",
        "prediction": prediction,
        "confidence": confidence,
        "severity": severity,
        "latency_ms": latency,
        "fallback_used": fallback,
        "input_length": random.randint(50, 500),
        "batch_size": 1
    }
    
    try:
        response = requests.post(EDGE_FUNCTION_URL, json=payload, headers=HEADERS, timeout=10)
        return {"status": response.status_code, "data": response.json(), "model": model_name, "service": config["service"]}
    except Exception as e:
        return {"status": "error", "error": str(e), "model": model_name}


def send_error(model_name: str, config: dict) -> dict:
    """Envoie une erreur simulée"""
    
    error_types = ["timeout", "memory", "inference", "connection", "validation"]
    error_type = random.choice(error_types)
    
    payload = {
        "event_type": "error",
        "model_name": model_name,
        "provider": config["provider"],
        "error_type": error_type,
        "error_message": f"Simulated {error_type} error for {model_name}",
        "endpoint": config["endpoint"],
        "request_id": f"req_{int(time.time() * 1000)}",
        "input_length": random.randint(50, 500)
    }
    
    try:
        response = requests.post(EDGE_FUNCTION_URL, json=payload, headers=HEADERS, timeout=10)
        return {"status": response.status_code, "data": response.json(), "model": model_name, "type": "error"}
    except Exception as e:
        return {"status": "error", "error": str(e), "model": model_name}


def send_health_check(model_name: str, config: dict) -> dict:
    """Envoie un health check simulé"""
    
    status = random.choices(["healthy", "degraded", "unhealthy"], weights=[85, 10, 5])[0]
    
    # RAM selon le modèle
    ram_ranges = {
        "camembert-depression": (400, 700),
        "qwen-depression": (2000, 3500),
        "llama-generation": (4000, 7000),
        "llama-fallback": (2000, 3500),
        "google-bert-multilingual": (500, 800),
        "xlm-roberta-depression": (500, 800),
        "git-large-captioning": (1000, 2000),
        "opus-mt-translation": (300, 500)
    }
    ram = random.uniform(*ram_ranges.get(model_name, (500, 1000)))
    
    payload = {
        "event_type": "health_check",
        "model_name": model_name,
        "provider": config["provider"],
        "status": status,
        "latency_ms": random.uniform(10, 100),
        "memory_mb": ram,
        "details": {
            "message": f"Health check at {datetime.now().isoformat()}",
            "service": config["service"]
        }
    }
    
    try:
        response = requests.post(EDGE_FUNCTION_URL, json=payload, headers=HEADERS, timeout=10)
        return {"status": response.status_code, "data": response.json(), "model": model_name, "health": status}
    except Exception as e:
        return {"status": "error", "error": str(e), "model": model_name}


def send_system_metrics() -> dict:
    """Envoie des métriques système simulées"""
    
    payload = {
        "event_type": "system_metrics",
        "cpu_percent": random.uniform(20, 95),
        "memory_percent": random.uniform(40, 90),
        "memory_used_mb": random.uniform(2000, 12000),
        "memory_available_mb": random.uniform(4000, 16000),
        "disk_usage_percent": random.uniform(30, 85),
        "disk_used_gb": random.uniform(50, 200),
        "disk_available_gb": random.uniform(50, 200),
        "hostname": "yansnet-api-server",
        "process_name": "uvicorn"
    }
    
    try:
        response = requests.post(EDGE_FUNCTION_URL, json=payload, headers=HEADERS, timeout=10)
        return {"status": response.status_code, "data": response.json(), "type": "system"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_simulation(num_events: int = 50, delay: float = 0.5):
    """Lance une simulation complète"""
    
    print(f"🚀 Démarrage de la simulation ({num_events} événements)")
    print(f"📡 URL: {EDGE_FUNCTION_URL}")
    print(f"🤖 Modèles: {len(MODELS)} ({', '.join(MODELS.keys())})")
    print("-" * 60)
    
    stats = {
        "predictions": 0, 
        "errors": 0, 
        "health_checks": 0, 
        "system": 0, 
        "failed": 0,
        "alerts": 0,
        "by_service": {}
    }
    
    for i in range(num_events):
        event_type = random.choices(
            ["prediction", "error", "health_check", "system"],
            weights=[70, 8, 17, 5]
        )[0]
        
        model_name = random.choice(list(MODELS.keys()))
        config = MODELS[model_name]
        service = config["service"]
        
        if service not in stats["by_service"]:
            stats["by_service"][service] = 0
        
        if event_type == "prediction":
            result = send_prediction(model_name, config)
            stats["predictions"] += 1
            stats["by_service"][service] += 1
        elif event_type == "error":
            result = send_error(model_name, config)
            stats["errors"] += 1
        elif event_type == "health_check":
            result = send_health_check(model_name, config)
            stats["health_checks"] += 1
        else:
            result = send_system_metrics()
            stats["system"] += 1
        
        if result.get("status") == 200:
            alerts = result.get("data", {}).get("alerts_triggered", 0)
            stats["alerts"] += alerts
            alert_str = f" ⚠️ {alerts} alertes" if alerts > 0 else ""
            print(f"[{i+1}/{num_events}] ✅ {event_type} - {result.get('model', 'system')} ({service if event_type != 'system' else 'sys'}){alert_str}")
        else:
            stats["failed"] += 1
            print(f"[{i+1}/{num_events}] ❌ {event_type} - {result}")
        
        time.sleep(delay)
    
    print("-" * 60)
    print("📊 Résumé:")
    print(f"   Prédictions: {stats['predictions']}")
    print(f"   Erreurs: {stats['errors']}")
    print(f"   Health checks: {stats['health_checks']}")
    print(f"   Système: {stats['system']}")
    print(f"   Alertes générées: {stats['alerts']}")
    print(f"   Échecs: {stats['failed']}")
    print("\n📈 Par service:")
    for service, count in stats["by_service"].items():
        print(f"   {service}: {count}")
    print("✅ Simulation terminée!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Envoyer des données de test vers Supabase")
    parser.add_argument("-n", "--num", type=int, default=50, help="Nombre d'événements")
    parser.add_argument("-d", "--delay", type=float, default=0.3, help="Délai entre événements (s)")
    parser.add_argument("--single", action="store_true", help="Envoyer un seul événement")
    parser.add_argument("--model", type=str, help="Tester un modèle spécifique")
    
    args = parser.parse_args()
    
    if args.single:
        model = args.model or "camembert-depression"
        if model not in MODELS:
            print(f"❌ Modèle inconnu: {model}")
            print(f"   Modèles disponibles: {', '.join(MODELS.keys())}")
        else:
            print(f"📤 Envoi d'un événement de test pour {model}...")
            result = send_prediction(model, MODELS[model])
            print(f"Résultat: {result}")
    else:
        run_simulation(args.num, args.delay)
