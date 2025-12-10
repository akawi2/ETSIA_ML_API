-- ============================================================================
-- ETSIA ML API - Schema de base de données pour les métriques
-- ============================================================================

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: model_predictions
-- Stocke toutes les prédictions effectuées par les modèles
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Informations sur le modèle
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    provider VARCHAR(50) NOT NULL,  -- camembert, qwen, llama, etc.
    
    -- Informations sur la requête
    endpoint VARCHAR(200) NOT NULL,
    request_id VARCHAR(100),
    
    -- Résultats de la prédiction
    prediction VARCHAR(100) NOT NULL,  -- DÉPRESSION, NORMAL, etc.
    confidence DECIMAL(5,4),  -- 0.0000 à 1.0000
    severity VARCHAR(50),  -- Aucune, Faible, Moyenne, Élevée, Critique
    
    -- Performance
    latency_ms DECIMAL(10,2) NOT NULL,
    fallback_used BOOLEAN DEFAULT FALSE,
    
    -- Métadonnées
    input_length INTEGER,
    batch_size INTEGER DEFAULT 1,
    
    -- Index pour les requêtes fréquentes
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

-- Index pour les requêtes de performance
CREATE INDEX idx_predictions_model ON model_predictions(model_name);
CREATE INDEX idx_predictions_created ON model_predictions(created_at);
CREATE INDEX idx_predictions_provider ON model_predictions(provider);
CREATE INDEX idx_predictions_endpoint ON model_predictions(endpoint);

-- ============================================================================
-- TABLE: model_errors
-- Stocke les erreurs rencontrées lors des prédictions
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_errors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Informations sur le modèle
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    -- Informations sur l'erreur
    error_type VARCHAR(100) NOT NULL,  -- timeout, memory, inference, etc.
    error_message TEXT,
    endpoint VARCHAR(200),
    request_id VARCHAR(100),
    
    -- Contexte
    input_length INTEGER,
    stack_trace TEXT
);

CREATE INDEX idx_errors_model ON model_errors(model_name);
CREATE INDEX idx_errors_created ON model_errors(created_at);
CREATE INDEX idx_errors_type ON model_errors(error_type);

-- ============================================================================
-- TABLE: model_health_checks
-- Stocke l'historique des health checks
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    status VARCHAR(20) NOT NULL,  -- healthy, unhealthy, degraded
    latency_ms DECIMAL(10,2),
    memory_mb DECIMAL(10,2),
    
    details JSONB
);

CREATE INDEX idx_health_model ON model_health_checks(model_name);
CREATE INDEX idx_health_checked ON model_health_checks(checked_at);
CREATE INDEX idx_health_status ON model_health_checks(status);

-- ============================================================================
-- TABLE: latency_percentiles
-- Stocke les percentiles de latence agrégés (calculés périodiquement)
-- ============================================================================
CREATE TABLE IF NOT EXISTS latency_percentiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    -- Percentiles
    p50_ms DECIMAL(10,2),
    p95_ms DECIMAL(10,2),
    p99_ms DECIMAL(10,2),
    avg_ms DECIMAL(10,2),
    min_ms DECIMAL(10,2),
    max_ms DECIMAL(10,2),
    
    -- Compteurs
    total_requests INTEGER NOT NULL,
    error_count INTEGER DEFAULT 0,
    fallback_count INTEGER DEFAULT 0,
    
    UNIQUE(period_start, period_end, model_name)
);

CREATE INDEX idx_percentiles_model ON latency_percentiles(model_name);
CREATE INDEX idx_percentiles_period ON latency_percentiles(period_start, period_end);

-- ============================================================================
-- TABLE: throughput_metrics
-- Stocke les métriques de débit (requêtes par seconde)
-- ============================================================================
CREATE TABLE IF NOT EXISTS throughput_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    
    -- Métriques de débit
    requests_per_second DECIMAL(10,4),
    requests_per_minute INTEGER,
    concurrent_requests INTEGER,
    
    -- Période de mesure
    window_seconds INTEGER DEFAULT 60
);

CREATE INDEX idx_throughput_model ON throughput_metrics(model_name);
CREATE INDEX idx_throughput_recorded ON throughput_metrics(recorded_at);

-- ============================================================================
-- TABLE: alerts
-- Stocke les alertes générées par le système de monitoring
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Type d'alerte
    alert_type VARCHAR(100) NOT NULL,  -- latency_high, error_rate_high, etc.
    severity VARCHAR(20) NOT NULL,  -- info, warning, critical
    
    -- Contexte
    model_name VARCHAR(100),
    provider VARCHAR(50),
    
    -- Détails
    message TEXT NOT NULL,
    threshold_value DECIMAL(10,4),
    actual_value DECIMAL(10,4),
    
    -- État
    status VARCHAR(20) DEFAULT 'active',  -- active, acknowledged, resolved
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created ON alerts(created_at);
CREATE INDEX idx_alerts_model ON alerts(model_name);

-- ============================================================================
-- VUES pour faciliter les requêtes
-- ============================================================================

-- Vue: Statistiques des dernières 24h par modèle
CREATE OR REPLACE VIEW v_model_stats_24h AS
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
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY model_name, provider;

-- Vue: Taux d'erreur par modèle (dernière heure)
CREATE OR REPLACE VIEW v_error_rates_1h AS
SELECT 
    e.model_name,
    e.provider,
    COUNT(e.id) as error_count,
    COALESCE(p.total_requests, 0) as total_requests,
    CASE 
        WHEN COALESCE(p.total_requests, 0) > 0 
        THEN (COUNT(e.id)::DECIMAL / p.total_requests) * 100 
        ELSE 0 
    END as error_rate_percent
FROM model_errors e
LEFT JOIN (
    SELECT model_name, provider, COUNT(*) as total_requests
    FROM model_predictions
    WHERE created_at > NOW() - INTERVAL '1 hour'
    GROUP BY model_name, provider
) p ON e.model_name = p.model_name AND e.provider = p.provider
WHERE e.created_at > NOW() - INTERVAL '1 hour'
GROUP BY e.model_name, e.provider, p.total_requests;

-- Vue: Alertes actives
CREATE OR REPLACE VIEW v_active_alerts AS
SELECT *
FROM alerts
WHERE status = 'active'
ORDER BY 
    CASE severity 
        WHEN 'critical' THEN 1 
        WHEN 'warning' THEN 2 
        ELSE 3 
    END,
    created_at DESC;

-- ============================================================================
-- FONCTIONS pour le calcul des métriques
-- ============================================================================

-- Fonction: Calculer et stocker les percentiles pour une période
CREATE OR REPLACE FUNCTION calculate_latency_percentiles(
    p_period_start TIMESTAMP WITH TIME ZONE,
    p_period_end TIMESTAMP WITH TIME ZONE
) RETURNS void AS $$
BEGIN
    INSERT INTO latency_percentiles (
        period_start, period_end, model_name, provider,
        p50_ms, p95_ms, p99_ms, avg_ms, min_ms, max_ms,
        total_requests, error_count, fallback_count
    )
    SELECT 
        p_period_start,
        p_period_end,
        p.model_name,
        p.provider,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.latency_ms),
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY p.latency_ms),
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY p.latency_ms),
        AVG(p.latency_ms),
        MIN(p.latency_ms),
        MAX(p.latency_ms),
        COUNT(*),
        COALESCE(e.error_count, 0),
        SUM(CASE WHEN p.fallback_used THEN 1 ELSE 0 END)
    FROM model_predictions p
    LEFT JOIN (
        SELECT model_name, provider, COUNT(*) as error_count
        FROM model_errors
        WHERE created_at BETWEEN p_period_start AND p_period_end
        GROUP BY model_name, provider
    ) e ON p.model_name = e.model_name AND p.provider = e.provider
    WHERE p.created_at BETWEEN p_period_start AND p_period_end
    GROUP BY p.model_name, p.provider, e.error_count
    ON CONFLICT (period_start, period_end, model_name) 
    DO UPDATE SET
        p50_ms = EXCLUDED.p50_ms,
        p95_ms = EXCLUDED.p95_ms,
        p99_ms = EXCLUDED.p99_ms,
        avg_ms = EXCLUDED.avg_ms,
        min_ms = EXCLUDED.min_ms,
        max_ms = EXCLUDED.max_ms,
        total_requests = EXCLUDED.total_requests,
        error_count = EXCLUDED.error_count,
        fallback_count = EXCLUDED.fallback_count,
        calculated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DONNÉES INITIALES
-- ============================================================================

-- Insérer un health check initial pour chaque modèle attendu
INSERT INTO model_health_checks (model_name, provider, status, details)
VALUES 
    ('camembert-depression', 'huggingface', 'unknown', '{"message": "Awaiting first health check"}'),
    ('qwen-depression', 'ollama', 'unknown', '{"message": "Awaiting first health check"}'),
    ('llama-generation', 'ollama', 'unknown', '{"message": "Awaiting first health check"}')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- COMMENTAIRES
-- ============================================================================
COMMENT ON TABLE model_predictions IS 'Stocke toutes les prédictions effectuées par les modèles ML';
COMMENT ON TABLE model_errors IS 'Stocke les erreurs rencontrées lors des prédictions';
COMMENT ON TABLE model_health_checks IS 'Historique des health checks des modèles';
COMMENT ON TABLE latency_percentiles IS 'Percentiles de latence agrégés par période';
COMMENT ON TABLE throughput_metrics IS 'Métriques de débit (requêtes/seconde)';
COMMENT ON TABLE alerts IS 'Alertes générées par le système de monitoring';
