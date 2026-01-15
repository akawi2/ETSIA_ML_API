"""
Client de monitoring pour envoyer les métriques au GA4-Bridge
"""
import os
import time
import requests
from functools import wraps
from typing import Dict, Any, Optional, Callable
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MonitoringClient:
    """Client pour envoyer des métriques au système de monitoring GA4-Bridge"""
    
    def __init__(self):
        self.bridge_url = os.getenv("BRIDGE_URL", "http://ga4-bridge:5000/log_metric")
        self.enabled = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.timeout = float(os.getenv("METRICS_TIMEOUT", "0.5"))
        self.client_id = os.getenv("CLIENT_ID", "etsia_ml_api_v2")
        
        if self.enabled:
            logger.info(f"Monitoring activé → {self.bridge_url}")
        else:
            logger.info("Monitoring désactivé")
    
    def emit(
        self,
        service: str,
        event_name: str,
        params: Dict[str, Any],
        model_name: Optional[str] = None
    ) -> bool:
        """
        Envoie une métrique au GA4-Bridge
        
        Args:
            service: Nom du service (hate_comment, depression_detection, etc.)
            event_name: Nom de l'événement (detect_hate, generate_content, etc.)
            params: Paramètres de la métrique (latency, precision, etc.)
            model_name: Nom du modèle utilisé (optionnel)
        
        Returns:
            True si l'envoi a réussi, False sinon
        """
        if not self.enabled:
            return False
        
        try:
            payload = {
                "service": service,
                "event_name": event_name,
                "model_name": model_name or "default",
                "params": params,
                "client_id": self.client_id
            }
            
            response = requests.post(
                self.bridge_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("alerts"):
                    logger.warning(
                        f"⚠️ ALERTE: {service}/{model_name} - "
                        f"Seuils dépassés pour {event_name}"
                    )
                return True
            else:
                logger.error(
                    f"Erreur monitoring ({response.status_code}): {response.text}"
                )
                return False
                
        except requests.exceptions.Timeout:
            logger.debug(f"Timeout monitoring (normal, {self.timeout}s)")
            return False
        except Exception as e:
            logger.debug(f"Erreur monitoring: {e}")
            return False


# Instance globale
_monitoring_client = MonitoringClient()


def emit_metric(
    service: str,
    event_name: str,
    params: Dict[str, Any],
    model_name: Optional[str] = None
) -> bool:
    """
    Fonction helper pour émettre une métrique
    
    Usage:
        emit_metric(
            service="hate_comment",
            event_name="detect_hate",
            params={"latency": 250, "precision": 0.85},
            model_name="bert-multilingual"
        )
    """
    return _monitoring_client.emit(service, event_name, params, model_name)


def monitor_prediction(
    service: str,
    event_name: str,
    model_name: Optional[str] = None,
    extract_metrics: Optional[Callable] = None
):
    """
    Décorateur pour monitorer automatiquement les prédictions
    
    Args:
        service: Nom du service
        event_name: Nom de l'événement
        model_name: Nom du modèle (optionnel)
        extract_metrics: Fonction pour extraire des métriques supplémentaires du résultat
    
    Usage:
        @monitor_prediction(
            service="hate_comment",
            event_name="detect_hate",
            model_name="bert-multilingual"
        )
        def predict(self, text: str):
            # ... code de prédiction
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Exécuter la fonction
                result = func(*args, **kwargs)
                
                # Calculer la latence
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Métriques de base
                params = {"latency": latency_ms}
                
                # Extraire des métriques supplémentaires si fourni
                if extract_metrics and callable(extract_metrics):
                    try:
                        extra_metrics = extract_metrics(result)
                        if extra_metrics:
                            params.update(extra_metrics)
                    except Exception as e:
                        logger.debug(f"Erreur extraction métriques: {e}")
                
                # Émettre la métrique
                emit_metric(service, event_name, params, model_name)
                
                return result
                
            except Exception as e:
                # En cas d'erreur, émettre une métrique d'échec
                latency_ms = int((time.time() - start_time) * 1000)
                emit_metric(
                    service,
                    f"{event_name}_error",
                    {
                        "latency": latency_ms,
                        "error": str(e)[:100]
                    },
                    model_name
                )
                raise
        
        return wrapper
    return decorator
