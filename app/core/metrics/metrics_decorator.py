"""
Décorateur et helpers pour l'enregistrement automatique des métriques
"""
import time
import traceback
import asyncio
from functools import wraps
from typing import Callable, Optional
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def record_prediction_metric(
    model_name: str,
    provider: str,
    endpoint: str,
    prediction: str,
    confidence: Optional[float],
    severity: Optional[str],
    latency_ms: float,
    fallback_used: bool = False,
    input_length: Optional[int] = None,
    request_id: Optional[str] = None
):
    """
    Enregistre une métrique de prédiction de manière asynchrone.
    
    Cette fonction peut être appelée depuis du code synchrone.
    """
    if not settings.ENABLE_METRICS:
        return
    
    async def _record():
        try:
            from app.core.metrics import MetricsService, PredictionMetric
            
            metric = PredictionMetric(
                model_name=model_name,
                provider=provider,
                endpoint=endpoint,
                prediction=prediction,
                confidence=confidence,
                severity=severity,
                latency_ms=latency_ms,
                fallback_used=fallback_used,
                input_length=input_length,
                request_id=request_id
            )
            
            service = MetricsService()
            await service.record_prediction(metric)
        except Exception as e:
            logger.debug(f"Erreur enregistrement métrique (non bloquant): {e}")
    
    # Exécuter de manière asynchrone sans bloquer
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_record())
        else:
            loop.run_until_complete(_record())
    except RuntimeError:
        # Pas de boucle d'événements, ignorer silencieusement
        pass


def record_error_metric(
    model_name: str,
    provider: str,
    error_type: str,
    error_message: Optional[str] = None,
    endpoint: Optional[str] = None,
    input_length: Optional[int] = None,
    request_id: Optional[str] = None
):
    """
    Enregistre une métrique d'erreur de manière asynchrone.
    """
    if not settings.ENABLE_METRICS:
        return
    
    async def _record():
        try:
            from app.core.metrics import MetricsService, ErrorMetric
            
            metric = ErrorMetric(
                model_name=model_name,
                provider=provider,
                error_type=error_type,
                error_message=error_message,
                endpoint=endpoint,
                input_length=input_length,
                request_id=request_id,
                stack_trace=traceback.format_exc() if error_message else None
            )
            
            service = MetricsService()
            await service.record_error(metric)
        except Exception as e:
            logger.debug(f"Erreur enregistrement erreur (non bloquant): {e}")
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_record())
        else:
            loop.run_until_complete(_record())
    except RuntimeError:
        pass


async def record_prediction_async(
    model_name: str,
    provider: str,
    endpoint: str,
    prediction: str,
    confidence: Optional[float],
    severity: Optional[str],
    latency_ms: float,
    fallback_used: bool = False,
    input_length: Optional[int] = None,
    request_id: Optional[str] = None
):
    """
    Version asynchrone pour enregistrer une métrique de prédiction.
    À utiliser dans les routes FastAPI.
    """
    if not settings.ENABLE_METRICS:
        return
    
    try:
        from app.core.metrics import MetricsService, PredictionMetric
        
        metric = PredictionMetric(
            model_name=model_name,
            provider=provider,
            endpoint=endpoint,
            prediction=prediction,
            confidence=confidence,
            severity=severity,
            latency_ms=latency_ms,
            fallback_used=fallback_used,
            input_length=input_length,
            request_id=request_id
        )
        
        service = MetricsService()
        await service.record_prediction(metric)
    except Exception as e:
        logger.debug(f"Erreur enregistrement métrique async: {e}")


async def record_error_async(
    model_name: str,
    provider: str,
    error_type: str,
    error_message: Optional[str] = None,
    endpoint: Optional[str] = None,
    input_length: Optional[int] = None,
    request_id: Optional[str] = None
):
    """
    Version asynchrone pour enregistrer une métrique d'erreur.
    """
    if not settings.ENABLE_METRICS:
        return
    
    try:
        from app.core.metrics import MetricsService, ErrorMetric
        
        metric = ErrorMetric(
            model_name=model_name,
            provider=provider,
            error_type=error_type,
            error_message=error_message,
            endpoint=endpoint,
            input_length=input_length,
            request_id=request_id,
            stack_trace=traceback.format_exc() if error_message else None
        )
        
        service = MetricsService()
        await service.record_error(metric)
    except Exception as e:
        logger.debug(f"Erreur enregistrement erreur async: {e}")
