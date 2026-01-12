"""
Modèles Pydantic pour le système de métriques
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID


class AlertSeverity(str, Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """États des alertes"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class PredictionMetric(BaseModel):
    """Métrique d'une prédiction"""
    model_name: str
    model_version: Optional[str] = None
    provider: str
    endpoint: str
    request_id: Optional[str] = None
    prediction: str
    confidence: Optional[float] = Field(None, ge=0, le=1)
    severity: Optional[str] = None
    latency_ms: float
    fallback_used: bool = False
    input_length: Optional[int] = None
    batch_size: int = 1
    created_at: Optional[datetime] = None


class ErrorMetric(BaseModel):
    """Métrique d'une erreur"""
    model_name: str
    provider: str
    error_type: str
    error_message: Optional[str] = None
    endpoint: Optional[str] = None
    request_id: Optional[str] = None
    input_length: Optional[int] = None
    stack_trace: Optional[str] = None
    created_at: Optional[datetime] = None


class HealthCheckMetric(BaseModel):
    """Métrique d'un health check"""
    model_name: str
    provider: str
    status: str  # healthy, unhealthy, degraded
    latency_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    checked_at: Optional[datetime] = None


class LatencyPercentiles(BaseModel):
    """Percentiles de latence agrégés"""
    model_name: str
    provider: str
    period_start: datetime
    period_end: datetime
    p50_ms: Optional[float] = None
    p95_ms: Optional[float] = None
    p99_ms: Optional[float] = None
    avg_ms: Optional[float] = None
    min_ms: Optional[float] = None
    max_ms: Optional[float] = None
    total_requests: int
    error_count: int = 0
    fallback_count: int = 0


class ThroughputMetric(BaseModel):
    """Métrique de débit"""
    model_name: str
    provider: str
    requests_per_second: Optional[float] = None
    requests_per_minute: Optional[int] = None
    concurrent_requests: Optional[int] = None
    window_seconds: int = 60
    recorded_at: Optional[datetime] = None


class Alert(BaseModel):
    """Alerte du système de monitoring"""
    id: Optional[UUID] = None
    alert_type: str
    severity: AlertSeverity
    model_name: Optional[str] = None
    provider: Optional[str] = None
    message: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class ModelStats(BaseModel):
    """Statistiques agrégées d'un modèle"""
    model_name: str
    provider: str
    total_requests: int
    avg_latency_ms: float
    p50_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    min_latency_ms: Optional[float] = None
    max_latency_ms: Optional[float] = None
    avg_confidence: Optional[float] = None
    fallback_count: int = 0
    fallback_rate: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    depression_count: int = 0
    normal_count: int = 0
    period: str = "24h"


class MetricsSummary(BaseModel):
    """Résumé global des métriques"""
    total_predictions: int
    total_errors: int
    active_alerts: int
    models: List[ModelStats]
    period_start: datetime
    period_end: datetime
