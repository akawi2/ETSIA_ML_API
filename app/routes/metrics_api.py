"""
Routes API pour les métriques et le monitoring
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Query, HTTPException
from app.core.metrics import (
    MetricsService,
    ModelStats,
    LatencyPercentiles,
    Alert,
    AlertSeverity
)
from app.core.metrics.metrics_models import MetricsSummary
from app.core.metrics.database import db
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])

metrics = MetricsService()


@router.get("/health")
async def metrics_health():
    """Health check du système de métriques"""
    try:
        db_healthy = await db.health_check()
        return {
            "status": "healthy" if db_healthy else "degraded",
            "database": "connected" if db_healthy else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=168, description="Période en heures (max 7 jours)")
):
    """
    Récupère un résumé global des métriques.
    
    Inclut:
    - Total des prédictions
    - Total des erreurs
    - Alertes actives
    - Statistiques par modèle
    """
    return await metrics.get_summary(hours=hours)


@router.get("/models", response_model=List[ModelStats])
async def get_model_stats(
    model_name: Optional[str] = Query(None, description="Filtrer par nom de modèle"),
    hours: int = Query(24, ge=1, le=168, description="Période en heures")
):
    """
    Récupère les statistiques détaillées par modèle.
    
    Inclut:
    - Latence (avg, p50, p95, p99)
    - Taux d'erreur et de fallback
    - Distribution des prédictions
    """
    return await metrics.get_model_stats(model_name=model_name, hours=hours)


@router.get("/models/{model_name}/latency", response_model=LatencyPercentiles)
async def get_model_latency(
    model_name: str,
    hours: int = Query(24, ge=1, le=168, description="Période en heures")
):
    """
    Récupère les percentiles de latence pour un modèle spécifique.
    """
    result = await metrics.get_latency_percentiles(model_name=model_name, hours=hours)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune donnée trouvée pour le modèle '{model_name}'"
        )
    return result


@router.get("/errors")
async def get_recent_errors(
    model_name: Optional[str] = Query(None, description="Filtrer par nom de modèle"),
    limit: int = Query(50, ge=1, le=500, description="Nombre maximum d'erreurs")
):
    """
    Récupère les erreurs récentes.
    """
    errors = await metrics.get_recent_errors(model_name=model_name, limit=limit)
    return {
        "count": len(errors),
        "errors": errors
    }


@router.get("/alerts", response_model=List[Alert])
async def get_active_alerts():
    """
    Récupère les alertes actives.
    
    Les alertes sont triées par sévérité (critical > warning > info).
    """
    return await metrics.get_active_alerts()


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: UUID):
    """
    Résout une alerte.
    """
    success = await metrics.resolve_alert(alert_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Alerte '{alert_id}' non trouvée"
        )
    return {"status": "resolved", "alert_id": str(alert_id)}


@router.get("/prometheus")
async def prometheus_metrics():
    """
    Expose les métriques au format Prometheus.
    
    Compatible avec Prometheus scraping.
    """
    try:
        summary = await metrics.get_summary(hours=1)
        
        lines = [
            "# HELP etsia_predictions_total Total number of predictions",
            "# TYPE etsia_predictions_total counter",
            f"etsia_predictions_total {summary.total_predictions}",
            "",
            "# HELP etsia_errors_total Total number of errors",
            "# TYPE etsia_errors_total counter",
            f"etsia_errors_total {summary.total_errors}",
            "",
            "# HELP etsia_alerts_active Number of active alerts",
            "# TYPE etsia_alerts_active gauge",
            f"etsia_alerts_active {summary.active_alerts}",
            ""
        ]
        
        # Métriques par modèle
        for model in summary.models:
            model_label = f'model="{model.model_name}",provider="{model.provider}"'
            
            lines.extend([
                f"# HELP etsia_model_requests_total Total requests per model",
                f"# TYPE etsia_model_requests_total counter",
                f"etsia_model_requests_total{{{model_label}}} {model.total_requests}",
                "",
                f"# HELP etsia_model_latency_avg_ms Average latency in milliseconds",
                f"# TYPE etsia_model_latency_avg_ms gauge",
                f"etsia_model_latency_avg_ms{{{model_label}}} {model.avg_latency_ms:.2f}",
                ""
            ])
            
            if model.p50_latency_ms:
                lines.extend([
                    f"# HELP etsia_model_latency_p50_ms P50 latency in milliseconds",
                    f"# TYPE etsia_model_latency_p50_ms gauge",
                    f"etsia_model_latency_p50_ms{{{model_label}}} {model.p50_latency_ms:.2f}",
                    ""
                ])
            
            if model.p95_latency_ms:
                lines.extend([
                    f"# HELP etsia_model_latency_p95_ms P95 latency in milliseconds",
                    f"# TYPE etsia_model_latency_p95_ms gauge",
                    f"etsia_model_latency_p95_ms{{{model_label}}} {model.p95_latency_ms:.2f}",
                    ""
                ])
            
            lines.extend([
                f"# HELP etsia_model_error_rate Error rate percentage",
                f"# TYPE etsia_model_error_rate gauge",
                f"etsia_model_error_rate{{{model_label}}} {model.error_rate:.2f}",
                "",
                f"# HELP etsia_model_fallback_rate Fallback rate percentage",
                f"# TYPE etsia_model_fallback_rate gauge",
                f"etsia_model_fallback_rate{{{model_label}}} {model.fallback_rate:.2f}",
                ""
            ])
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Erreur génération métriques Prometheus: {e}")
        return f"# Error generating metrics: {e}"
