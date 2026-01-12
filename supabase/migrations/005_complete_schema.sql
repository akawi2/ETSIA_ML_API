-- ============================================================================
-- ETSIA ML API - Schema complet corrigé
-- Exécuter ce fichier dans Supabase SQL Editor
-- ============================================================================

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: model_predictions
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50),
    provider VARCHAR(50) NOT NULL,
    endpoint VARCHAR(200) NOT NULL,
    request_id VARCHAR(100),
    prediction VARCHAR(100) NOT NULL,
    confidence DECIMAL(5,4),
    severity VARCHAR(50),
    latency_ms DECIMAL(10,2) NOT NULL,
    fallback_used BOOLEAN DEFAULT FALSE,
    input_length INTEGER,
    batch_size INTEGER DEFAULT 1,
    CONSTRAINT chk_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

CREATE INDEX IF NOT EXISTS idx_predictions_model ON model_predictions(model_name);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON model_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_predictions_provider ON model_predictions(provider);

-- ============================================================================
-- TABLE: model_errors
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_errors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT,
    endpoint VARCHAR(200),
    request_id VARCHAR(100),
    input_length INTEGER,
    stack_trace TEXT
);

CREATE INDEX IF NOT EXISTS idx_errors_model ON model_errors(model_name);
CREATE INDEX IF NOT EXISTS idx_errors_created ON model_errors(created_at);
CREATE INDEX IF NOT EXISTS idx_errors_type ON model_errors(error_type);

-- ============================================================================
-- TABLE: model_health_checks
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    latency_ms DECIMAL(10,2),
    memory_mb DECIMAL(10,2),
    details JSONB
);

CREATE INDEX IF NOT EXISTS idx_health_model ON model_health_checks(model_name);
CREATE INDEX IF NOT EXISTS idx_health_checked ON model_health_checks(checked_at);
CREATE INDEX IF NOT EXISTS idx_health_status ON model_health_checks(status);

-- ============================================================================
-- TABLE: alerts
-- ============================================================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    model_name VARCHAR(100),
    provider VARCHAR(50),
    message TEXT NOT NULL,
    threshold_value DECIMAL(10,4),
    actual_value DECIMAL(10,4),
    status VARCHAR(20) DEFAULT 'active',
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_model ON alerts(model_name);

-- ============================================================================
-- TABLE: system_metrics
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cpu_percent DECIMAL(5,2),
    memory_percent DECIMAL(5,2),
    memory_used_mb DECIMAL(10,2),
    memory_available_mb DECIMAL(10,2),
    disk_usage_percent DECIMAL(5,2),
    disk_used_gb DECIMAL(10,2),
    disk_available_gb DECIMAL(10,2),
    network_sent_mb DECIMAL(10,2),
    network_recv_mb DECIMAL(10,2),
    hostname VARCHAR(100),
    process_name VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_system_metrics_recorded ON system_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_system_metrics_hostname ON system_metrics(hostname);

-- ============================================================================
-- TABLE: model_versions
-- ============================================================================
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    description TEXT,
    deployed_at TIMESTAMP WITH TIME ZONE,
    deprecated_at TIMESTAMP WITH TIME ZONE,
    config JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(model_name, version)
);

CREATE INDEX IF NOT EXISTS idx_model_versions_name ON model_versions(model_name);
CREATE INDEX IF NOT EXISTS idx_model_versions_active ON model_versions(is_active);

-- ============================================================================
-- TABLE: latency_percentiles
-- ============================================================================
CREATE TABLE IF NOT EXISTS latency_percentiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    p50_ms DECIMAL(10,2),
    p95_ms DECIMAL(10,2),
    p99_ms DECIMAL(10,2),
    avg_ms DECIMAL(10,2),
    min_ms DECIMAL(10,2),
    max_ms DECIMAL(10,2),
    total_requests INTEGER NOT NULL,
    error_count INTEGER DEFAULT 0,
    fallback_count INTEGER DEFAULT 0,
    UNIQUE(period_start, period_end, model_name)
);

CREATE INDEX IF NOT EXISTS idx_percentiles_model ON latency_percentiles(model_name);
CREATE INDEX IF NOT EXISTS idx_percentiles_period ON latency_percentiles(period_start, period_end);

-- ============================================================================
-- Enable Realtime
-- ============================================================================
ALTER PUBLICATION supabase_realtime ADD TABLE alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE model_predictions;
ALTER PUBLICATION supabase_realtime ADD TABLE model_health_checks;
ALTER PUBLICATION supabase_realtime ADD TABLE system_metrics;

-- ============================================================================
-- SEED: Modèles initiaux
-- ============================================================================
INSERT INTO model_versions (model_name, version, provider, description, deployed_at, is_active) VALUES 
    ('camembert-depression', '1.0.0', 'huggingface', 'CamemBERT fine-tuned pour la détection de dépression', NOW(), TRUE),
    ('qwen-depression', '1.0.0', 'ollama', 'Qwen 2.5 1.5B pour la détection de dépression', NOW(), TRUE),
    ('llama-generation', '1.0.0', 'ollama', 'Llama 3.2 3B pour la génération de contenu', NOW(), TRUE)
ON CONFLICT (model_name, version) DO NOTHING;

-- Health checks initiaux
INSERT INTO model_health_checks (model_name, provider, status, details) VALUES 
    ('camembert-depression', 'huggingface', 'unknown', '{"message": "Awaiting first health check"}'),
    ('qwen-depression', 'ollama', 'unknown', '{"message": "Awaiting first health check"}'),
    ('llama-generation', 'ollama', 'unknown', '{"message": "Awaiting first health check"}');
