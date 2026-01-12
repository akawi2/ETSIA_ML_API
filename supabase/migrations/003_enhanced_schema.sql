-- Migration: Schéma amélioré pour monitoring ML complet
-- Basé sur le document de métriques Yansnet

-- Table des modèles ML
CREATE TABLE IF NOT EXISTS models (
    model_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    version VARCHAR(20),
    type VARCHAR(50), -- 'classification', 'generation', 'captioning', 'translation'
    provider VARCHAR(50), -- 'huggingface', 'ollama', 'openai'
    description TEXT,
    config JSONB DEFAULT '{}', -- température, max_tokens, etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des exécutions de modèles
CREATE TABLE IF NOT EXISTS model_runs (
    run_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_id UUID REFERENCES models(model_id) ON DELETE CASCADE,
    service VARCHAR(100) NOT NULL, -- hate_comment, depression_detection, etc.
    run_timestamp TIMESTAMPTZ DEFAULT NOW(),
    input_data JSONB,
    output_data JSONB,
    latency_ms FLOAT,
    gpu_utilization FLOAT,
    cpu_utilization FLOAT,
    memory_usage_mb FLOAT,
    status VARCHAR(20) CHECK (status IN ('success', 'failed', 'warning', 'timeout')),
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Table des métriques de modèles (évaluations périodiques)
CREATE TABLE IF NOT EXISTS models_metrics (
    metric_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_id UUID REFERENCES models(model_id) ON DELETE CASCADE,
    service VARCHAR(100) NOT NULL,
    evaluation_timestamp TIMESTAMPTZ DEFAULT NOW(),
    -- Métriques de classification
    precision_score FLOAT,
    recall_score FLOAT,
    f1_score FLOAT,
    accuracy FLOAT,
    false_positive_rate FLOAT,
    false_negative_rate FLOAT,
    -- Métriques de performance
    latency_p50 FLOAT,
    latency_p95 FLOAT,
    latency_p99 FLOAT,
    throughput FLOAT, -- req/s
    -- Métriques de ressources
    ram_usage_mb FLOAT,
    gpu_memory_mb FLOAT,
    -- Métriques spécifiques génération
    ttr FLOAT, -- Type-Token Ratio (diversité lexicale)
    avg_length FLOAT,
    repetition_rate FLOAT,
    -- Métriques spécifiques captioning
    bleu_score FLOAT,
    cider_score FLOAT,
    keyword_coverage FLOAT,
    -- Métriques spécifiques dépression
    confidence_avg FLOAT,
    fallback_rate FLOAT,
    -- Contexte
    sample_size INT,
    evaluation_context TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Table des alertes de modèles
CREATE TABLE IF NOT EXISTS model_alerts (
    alert_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    model_id UUID REFERENCES models(model_id) ON DELETE SET NULL,
    metric_id UUID REFERENCES models_metrics(metric_id) ON DELETE SET NULL,
    run_id UUID REFERENCES model_runs(run_id) ON DELETE SET NULL,
    service VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- 'precision_low', 'latency_high', 'faux_negatifs', etc.
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')) NOT NULL,
    message TEXT,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    threshold FLOAT,
    operator VARCHAR(10),
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ
);

-- Table des seuils d'alertes par service/modèle
CREATE TABLE IF NOT EXISTS alert_thresholds (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    service VARCHAR(100) NOT NULL,
    model_name VARCHAR(150), -- NULL = tous les modèles du service
    metric VARCHAR(100) NOT NULL,
    threshold FLOAT NOT NULL,
    operator VARCHAR(10) CHECK (operator IN ('>', '<', '>=', '<=', '=')) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')) NOT NULL,
    description TEXT,
    action_recommended TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_model_runs_service ON model_runs(service);
CREATE INDEX IF NOT EXISTS idx_model_runs_timestamp ON model_runs(run_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_model_runs_status ON model_runs(status);
CREATE INDEX IF NOT EXISTS idx_models_metrics_service ON models_metrics(service);
CREATE INDEX IF NOT EXISTS idx_models_metrics_timestamp ON models_metrics(evaluation_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_model_alerts_severity ON model_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_model_alerts_resolved ON model_alerts(resolved);
CREATE INDEX IF NOT EXISTS idx_model_alerts_triggered ON model_alerts(triggered_at DESC);

-- Enable Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE model_alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE model_runs;
ALTER PUBLICATION supabase_realtime ADD TABLE models_metrics;
