"""
ETSIA ML API - Metrics System

Provides metrics collection, storage, and retrieval for model monitoring.
"""
from app.core.metrics.metrics_service import MetricsService
from app.core.metrics.metrics_models import (
    PredictionMetric,
    ErrorMetric,
    HealthCheckMetric,
    LatencyPercentiles,
    ThroughputMetric,
    Alert,
    AlertSeverity,
    ModelStats
)
from app.core.metrics.metrics_decorator import (
    record_prediction_metric,
    record_error_metric,
    record_prediction_async,
    record_error_async
)

__all__ = [
    "MetricsService",
    "PredictionMetric",
    "ErrorMetric", 
    "HealthCheckMetric",
    "LatencyPercentiles",
    "ThroughputMetric",
    "Alert",
    "AlertSeverity",
    "ModelStats",
    "record_prediction_metric",
    "record_error_metric",
    "record_prediction_async",
    "record_error_async"
]
