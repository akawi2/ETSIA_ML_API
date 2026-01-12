-- Yansnet Monitoring Schema for Supabase

-- Table des métriques (événements bruts)
CREATE TABLE metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    service VARCHAR(100) NOT NULL,
    model_name VARCHAR(100) DEFAULT 'default',
    event_name VARCHAR(100) NOT NULL,
    params JSONB NOT NULL DEFAULT '{}',
    client_id VARCHAR(100) DEFAULT 'system_mon',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des règles d'alertes (remplace metrics_catalog.json)
CREATE TABLE alert_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    service VARCHAR(100) NOT NULL,
    model VARCHAR(100),  -- NULL = toutes les modèles
    metric VARCHAR(100) NOT NULL,
    threshold DECIMAL NOT NULL,
    operator VARCHAR(10) NOT NULL CHECK (operator IN ('>', '<', '>=', '<=')),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('Critique', 'Haute', 'Moyenne', 'Faible')),
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des alertes déclenchées
CREATE TABLE alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    metric_id UUID REFERENCES metrics(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES alert_rules(id) ON DELETE SET NULL,
    service VARCHAR(100) NOT NULL,
    model_name VARCHAR(100),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL NOT NULL,
    threshold DECIMAL NOT NULL,
    operator VARCHAR(10) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    reason VARCHAR(200),
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour les requêtes fréquentes
CREATE INDEX idx_metrics_service ON metrics(service);
CREATE INDEX idx_metrics_created_at ON metrics(created_at DESC);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_alerts_priority ON alerts(priority);
CREATE INDEX idx_alerts_acknowledged ON alerts(acknowledged);
CREATE INDEX idx_alert_rules_service ON alert_rules(service);

-- Enable Realtime pour les alertes (notifications live)
ALTER PUBLICATION supabase_realtime ADD TABLE alerts;
ALTER PUBLICATION supabase_realtime ADD TABLE metrics;
