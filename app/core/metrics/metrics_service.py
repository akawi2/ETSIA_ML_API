"""
Service de métriques pour le monitoring des modèles ML
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
import json
from app.core.metrics.database import db
from app.core.metrics.metrics_models import (
    PredictionMetric,
    ErrorMetric,
    HealthCheckMetric,
    LatencyPercentiles,
    ThroughputMetric,
    Alert,
    AlertSeverity,
    AlertStatus,
    ModelStats,
    MetricsSummary
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MetricsService:
    """Service pour collecter et récupérer les métriques"""
    
    _instance: Optional['MetricsService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    # =========================================================================
    # ENREGISTREMENT DES MÉTRIQUES
    # =========================================================================
    
    async def record_prediction(self, metric: PredictionMetric) -> None:
        """Enregistre une prédiction dans la base de données"""
        try:
            await db.execute("""
                INSERT INTO model_predictions (
                    model_name, model_version, provider, endpoint, request_id,
                    prediction, confidence, severity, latency_ms, fallback_used,
                    input_length, batch_size
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
                metric.model_name,
                metric.model_version,
                metric.provider,
                metric.endpoint,
                metric.request_id,
                metric.prediction,
                metric.confidence,
                metric.severity,
                metric.latency_ms,
                metric.fallback_used,
                metric.input_length,
                metric.batch_size
            )
            logger.debug(f"Métrique enregistrée: {metric.model_name} - {metric.latency_ms}ms")
        except Exception as e:
            logger.error(f"Erreur enregistrement métrique: {e}")
    
    async def record_error(self, metric: ErrorMetric) -> None:
        """Enregistre une erreur dans la base de données"""
        try:
            await db.execute("""
                INSERT INTO model_errors (
                    model_name, provider, error_type, error_message,
                    endpoint, request_id, input_length, stack_trace
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                metric.model_name,
                metric.provider,
                metric.error_type,
                metric.error_message,
                metric.endpoint,
                metric.request_id,
                metric.input_length,
                metric.stack_trace
            )
            logger.warning(f"Erreur enregistrée: {metric.model_name} - {metric.error_type}")
            
            # Vérifier si une alerte doit être créée
            await self._check_error_rate_alert(metric.model_name, metric.provider)
        except Exception as e:
            logger.error(f"Erreur enregistrement erreur: {e}")
    
    async def record_health_check(self, metric: HealthCheckMetric) -> None:
        """Enregistre un health check dans la base de données"""
        try:
            details_json = json.dumps(metric.details) if metric.details else None
            await db.execute("""
                INSERT INTO model_health_checks (
                    model_name, provider, status, latency_ms, memory_mb, details
                ) VALUES ($1, $2, $3, $4, $5, $6::jsonb)
            """,
                metric.model_name,
                metric.provider,
                metric.status,
                metric.latency_ms,
                metric.memory_mb,
                details_json
            )
        except Exception as e:
            logger.error(f"Erreur enregistrement health check: {e}")
    
    async def record_throughput(self, metric: ThroughputMetric) -> None:
        """Enregistre une métrique de débit"""
        try:
            await db.execute("""
                INSERT INTO throughput_metrics (
                    model_name, provider, requests_per_second,
                    requests_per_minute, concurrent_requests, window_seconds
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
                metric.model_name,
                metric.provider,
                metric.requests_per_second,
                metric.requests_per_minute,
                metric.concurrent_requests,
                metric.window_seconds
            )
        except Exception as e:
            logger.error(f"Erreur enregistrement throughput: {e}")
    
    # =========================================================================
    # RÉCUPÉRATION DES MÉTRIQUES
    # =========================================================================
    
    async def get_model_stats(
        self, 
        model_name: Optional[str] = None,
        hours: int = 24
    ) -> List[ModelStats]:
        """Récupère les statistiques des modèles"""
        try:
            query = """
                SELECT 
                    model_name,
                    provider,
                    COUNT(*) as total_requests,
                    AVG(latency_ms) as avg_latency_ms,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50_latency_ms,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency_ms,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_latency_ms,
                    MIN(latency_ms) as min_latency_ms,
                    MAX(latency_ms) as max_latency_ms,
                    AVG(confidence) as avg_confidence,
                    SUM(CASE WHEN fallback_used THEN 1 ELSE 0 END) as fallback_count,
                    SUM(CASE WHEN prediction = 'DÉPRESSION' THEN 1 ELSE 0 END) as depression_count,
                    SUM(CASE WHEN prediction = 'NORMAL' THEN 1 ELSE 0 END) as normal_count
                FROM model_predictions
                WHERE created_at > NOW() - INTERVAL '%s hours'
            """
            
            if model_name:
                query += " AND model_name = $1"
                query += " GROUP BY model_name, provider"
                rows = await db.fetch(query % hours, model_name)
            else:
                query += " GROUP BY model_name, provider"
                rows = await db.fetch(query % hours)
            
            stats = []
            for row in rows:
                total = row['total_requests']
                fallback = row['fallback_count'] or 0
                
                # Récupérer le nombre d'erreurs
                error_query = """
                    SELECT COUNT(*) FROM model_errors
                    WHERE model_name = $1 AND provider = $2
                    AND created_at > NOW() - INTERVAL '%s hours'
                """
                error_count = await db.fetchval(
                    error_query % hours, 
                    row['model_name'], 
                    row['provider']
                ) or 0
                
                stats.append(ModelStats(
                    model_name=row['model_name'],
                    provider=row['provider'],
                    total_requests=total,
                    avg_latency_ms=float(row['avg_latency_ms'] or 0),
                    p50_latency_ms=float(row['p50_latency_ms']) if row['p50_latency_ms'] else None,
                    p95_latency_ms=float(row['p95_latency_ms']) if row['p95_latency_ms'] else None,
                    p99_latency_ms=float(row['p99_latency_ms']) if row['p99_latency_ms'] else None,
                    min_latency_ms=float(row['min_latency_ms']) if row['min_latency_ms'] else None,
                    max_latency_ms=float(row['max_latency_ms']) if row['max_latency_ms'] else None,
                    avg_confidence=float(row['avg_confidence']) if row['avg_confidence'] else None,
                    fallback_count=fallback,
                    fallback_rate=(fallback / total * 100) if total > 0 else 0,
                    error_count=error_count,
                    error_rate=(error_count / total * 100) if total > 0 else 0,
                    depression_count=row['depression_count'] or 0,
                    normal_count=row['normal_count'] or 0,
                    period=f"{hours}h"
                ))
            
            return stats
        except Exception as e:
            logger.error(f"Erreur récupération stats: {e}")
            return []
    
    async def get_latency_percentiles(
        self,
        model_name: str,
        hours: int = 24
    ) -> Optional[LatencyPercentiles]:
        """Récupère les percentiles de latence pour un modèle"""
        try:
            row = await db.fetchrow("""
                SELECT 
                    model_name,
                    provider,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50_ms,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_ms,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_ms,
                    AVG(latency_ms) as avg_ms,
                    MIN(latency_ms) as min_ms,
                    MAX(latency_ms) as max_ms,
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN fallback_used THEN 1 ELSE 0 END) as fallback_count
                FROM model_predictions
                WHERE model_name = $1
                AND created_at > NOW() - INTERVAL '%s hours'
                GROUP BY model_name, provider
            """ % hours, model_name)
            
            if not row:
                return None
            
            now = datetime.utcnow()
            return LatencyPercentiles(
                model_name=row['model_name'],
                provider=row['provider'],
                period_start=now - timedelta(hours=hours),
                period_end=now,
                p50_ms=float(row['p50_ms']) if row['p50_ms'] else None,
                p95_ms=float(row['p95_ms']) if row['p95_ms'] else None,
                p99_ms=float(row['p99_ms']) if row['p99_ms'] else None,
                avg_ms=float(row['avg_ms']) if row['avg_ms'] else None,
                min_ms=float(row['min_ms']) if row['min_ms'] else None,
                max_ms=float(row['max_ms']) if row['max_ms'] else None,
                total_requests=row['total_requests'],
                fallback_count=row['fallback_count'] or 0
            )
        except Exception as e:
            logger.error(f"Erreur récupération percentiles: {e}")
            return None
    
    async def get_recent_errors(
        self,
        model_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Récupère les erreurs récentes"""
        try:
            if model_name:
                rows = await db.fetch("""
                    SELECT * FROM model_errors
                    WHERE model_name = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, model_name, limit)
            else:
                rows = await db.fetch("""
                    SELECT * FROM model_errors
                    ORDER BY created_at DESC
                    LIMIT $1
                """, limit)
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Erreur récupération erreurs: {e}")
            return []
    
    async def get_summary(self, hours: int = 24) -> MetricsSummary:
        """Récupère un résumé global des métriques"""
        try:
            now = datetime.utcnow()
            
            # Total prédictions
            total_predictions = await db.fetchval("""
                SELECT COUNT(*) FROM model_predictions
                WHERE created_at > NOW() - INTERVAL '%s hours'
            """ % hours) or 0
            
            # Total erreurs
            total_errors = await db.fetchval("""
                SELECT COUNT(*) FROM model_errors
                WHERE created_at > NOW() - INTERVAL '%s hours'
            """ % hours) or 0
            
            # Alertes actives
            active_alerts = await db.fetchval("""
                SELECT COUNT(*) FROM alerts WHERE status = 'active'
            """) or 0
            
            # Stats par modèle
            models = await self.get_model_stats(hours=hours)
            
            return MetricsSummary(
                total_predictions=total_predictions,
                total_errors=total_errors,
                active_alerts=active_alerts,
                models=models,
                period_start=now - timedelta(hours=hours),
                period_end=now
            )
        except Exception as e:
            logger.error(f"Erreur récupération summary: {e}")
            return MetricsSummary(
                total_predictions=0,
                total_errors=0,
                active_alerts=0,
                models=[],
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow()
            )
    
    # =========================================================================
    # ALERTES
    # =========================================================================
    
    async def create_alert(self, alert: Alert) -> Optional[UUID]:
        """Crée une nouvelle alerte"""
        try:
            result = await db.fetchval("""
                INSERT INTO alerts (
                    alert_type, severity, model_name, provider,
                    message, threshold_value, actual_value, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """,
                alert.alert_type,
                alert.severity.value,
                alert.model_name,
                alert.provider,
                alert.message,
                alert.threshold_value,
                alert.actual_value,
                alert.status.value
            )
            logger.warning(f"Alerte créée: {alert.alert_type} - {alert.severity.value}")
            return result
        except Exception as e:
            logger.error(f"Erreur création alerte: {e}")
            return None
    
    async def get_active_alerts(self) -> List[Alert]:
        """Récupère les alertes actives"""
        try:
            rows = await db.fetch("""
                SELECT * FROM alerts
                WHERE status = 'active'
                ORDER BY 
                    CASE severity 
                        WHEN 'critical' THEN 1 
                        WHEN 'warning' THEN 2 
                        ELSE 3 
                    END,
                    created_at DESC
            """)
            
            return [Alert(
                id=row['id'],
                alert_type=row['alert_type'],
                severity=AlertSeverity(row['severity']),
                model_name=row['model_name'],
                provider=row['provider'],
                message=row['message'],
                threshold_value=float(row['threshold_value']) if row['threshold_value'] else None,
                actual_value=float(row['actual_value']) if row['actual_value'] else None,
                status=AlertStatus(row['status']),
                created_at=row['created_at']
            ) for row in rows]
        except Exception as e:
            logger.error(f"Erreur récupération alertes: {e}")
            return []
    
    async def resolve_alert(self, alert_id: UUID) -> bool:
        """Résout une alerte"""
        try:
            await db.execute("""
                UPDATE alerts
                SET status = 'resolved', resolved_at = NOW()
                WHERE id = $1
            """, alert_id)
            return True
        except Exception as e:
            logger.error(f"Erreur résolution alerte: {e}")
            return False
    
    async def _check_error_rate_alert(
        self, 
        model_name: str, 
        provider: str,
        threshold: float = 10.0
    ) -> None:
        """Vérifie si le taux d'erreur dépasse le seuil et crée une alerte"""
        try:
            # Compter les erreurs de la dernière heure
            error_count = await db.fetchval("""
                SELECT COUNT(*) FROM model_errors
                WHERE model_name = $1 AND provider = $2
                AND created_at > NOW() - INTERVAL '1 hour'
            """, model_name, provider) or 0
            
            # Compter les requêtes de la dernière heure
            request_count = await db.fetchval("""
                SELECT COUNT(*) FROM model_predictions
                WHERE model_name = $1 AND provider = $2
                AND created_at > NOW() - INTERVAL '1 hour'
            """, model_name, provider) or 0
            
            if request_count > 0:
                error_rate = (error_count / request_count) * 100
                
                if error_rate > threshold:
                    # Vérifier si une alerte similaire existe déjà
                    existing = await db.fetchval("""
                        SELECT id FROM alerts
                        WHERE model_name = $1 AND alert_type = 'error_rate_high'
                        AND status = 'active'
                    """, model_name)
                    
                    if not existing:
                        await self.create_alert(Alert(
                            alert_type="error_rate_high",
                            severity=AlertSeverity.CRITICAL if error_rate > 20 else AlertSeverity.WARNING,
                            model_name=model_name,
                            provider=provider,
                            message=f"Taux d'erreur élevé: {error_rate:.1f}% (seuil: {threshold}%)",
                            threshold_value=threshold,
                            actual_value=error_rate
                        ))
        except Exception as e:
            logger.error(f"Erreur vérification taux d'erreur: {e}")


# Instance globale
metrics_service = MetricsService()
