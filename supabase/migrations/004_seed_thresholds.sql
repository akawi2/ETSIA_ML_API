-- Seed: Seuils d'alertes basés sur le document de métriques Yansnet

-- ============================================
-- HATE COMMENT DETECTION
-- ============================================
INSERT INTO alert_thresholds (service, model_name, metric, threshold, operator, severity, description, action_recommended) VALUES
('hate_comment', 'google-bert-multilingual', 'precision', 0.80, '<', 'critical', 'Alerte de baisse de précision', 'Réévaluation du modèle et ajustement des seuils'),
('hate_comment', 'google-bert-multilingual', 'f1_score', 0.88, '<', 'medium', 'Alerte de diminution F1 score', 'Analyse des cas d''erreur et fine-tuning'),
('hate_comment', 'google-bert-multilingual', 'recall', 0.85, '<', 'high', 'Alerte de baisse de Recall', 'Priorité haute - risque de manquer des cas'),
('hate_comment', 'google-bert-multilingual', 'false_positive_rate', 0.10, '>', 'critical', 'Alertes faux positifs élevés', 'Ajustement du seuil de confiance'),
('hate_comment', 'google-bert-multilingual', 'false_negative_rate', 0.15, '>', 'critical', 'Alerte de faux négatifs élevés', 'Révision urgente du modèle'),
('hate_comment', 'google-bert-multilingual', 'latency_ms', 500, '>', 'medium', 'Alerte temps de réponse lent', 'Optimisation du modèle ou vérification ressources'),

-- ============================================
-- IMAGE CAPTIONING / SENSITIVE CONTENT
-- ============================================
('image_captioning', 'git-large-textcaps', 'precision', 0.85, '<', 'medium', 'Alerte de baisse de précision', 'Révision des mots-clés et mise à jour du dictionnaire'),
('image_captioning', 'git-large-textcaps', 'f1_score', 0.87, '<', 'medium', 'Alerte de diminution F1 score', 'Réévaluation du système de détection'),
('image_captioning', 'git-large-textcaps', 'recall', 0.90, '<', 'high', 'Alerte de baisse de Recall', 'Ajout de nouveaux mots-clés sensibles'),
('image_captioning', 'git-large-textcaps', 'false_positive_rate', 0.08, '>', 'medium', 'Alerte faux positifs élevés', 'Affinage des règles de détection'),
('image_captioning', 'git-large-textcaps', 'false_negative_rate', 0.05, '>', 'critical', 'Alerte faux négatifs élevés', 'Expansion du dictionnaire de mots-clés'),
('image_captioning', 'git-large-textcaps', 'latency_ms', 2000, '>', 'medium', 'Alerte temps de réponse lent', 'Optimisation du pipeline captioning + traduction'),
('image_captioning', 'git-large-textcaps', 'bleu_score', 0.25, '<', 'high', 'Alerte qualité de légende faible', 'Considérer un modèle de captioning plus performant'),
('image_captioning', 'git-large-textcaps', 'keyword_coverage', 0.75, '<', 'medium', 'Alerte couverture mots-clés', 'Enrichissement du dictionnaire multilingue'),

-- ============================================
-- DEPRESSION DETECTION - CamemBERT
-- ============================================
('depression_detection', 'camembert-base', 'precision', 0.80, '<', 'critical', 'Alerte de baisse de précision', 'Réévaluation du modèle et ajustement des seuils'),
('depression_detection', 'camembert-base', 'recall', 0.85, '<', 'critical', 'Alerte de baisse de Recall', 'Priorité haute - risque de manquer des cas critiques'),
('depression_detection', 'camembert-base', 'false_positive_rate', 0.15, '>', 'high', 'Alerte faux positifs élevés', 'Ajustement du seuil de confiance'),
('depression_detection', 'camembert-base', 'false_negative_rate', 0.10, '>', 'critical', 'Alerte faux négatifs élevés', 'Révision urgente - impact sur la sécurité'),
('depression_detection', 'camembert-base', 'latency_p50', 50, '>', 'low', 'Alerte latence p50', 'Vérification des ressources'),
('depression_detection', 'camembert-base', 'latency_p95', 100, '>', 'medium', 'Alerte latence p95', 'Optimisation du modèle'),
('depression_detection', 'camembert-base', 'latency_p99', 200, '>', 'high', 'Alerte latence p99', 'Vérification urgente des ressources'),
('depression_detection', 'camembert-base', 'latency_ms', 500, '>', 'medium', 'Alerte temps de réponse lent', 'Optimisation du modèle ou vérification ressources'),
('depression_detection', 'camembert-base', 'ram_usage_mb', 600, '>', 'high', 'Alerte mémoire élevée', 'Optimisation ou redémarrage'),
('depression_detection', 'camembert-base', 'confidence_avg', 0.60, '<', 'medium', 'Alerte confiance moyenne faible', 'Analyse des textes ambigus'),
('depression_detection', 'camembert-base', 'fallback_rate', 0.05, '>', 'medium', 'Alerte taux de fallback élevé', 'Vérification du modèle primaire'),

-- ============================================
-- DEPRESSION DETECTION - Qwen
-- ============================================
('depression_detection', 'qwen2.5:1.5b', 'latency_p50', 400, '>', 'low', 'Alerte latence p50 Qwen', 'Vérification Ollama'),
('depression_detection', 'qwen2.5:1.5b', 'latency_p95', 700, '>', 'medium', 'Alerte latence p95 Qwen', 'Optimisation'),
('depression_detection', 'qwen2.5:1.5b', 'latency_p99', 1000, '>', 'high', 'Alerte latence p99 Qwen', 'Vérification urgente'),
('depression_detection', 'qwen2.5:1.5b', 'latency_ms', 1000, '>', 'medium', 'Alerte temps de réponse lent Qwen', 'Vérification d''Ollama et des ressources'),
('depression_detection', 'qwen2.5:1.5b', 'ram_usage_mb', 3072, '>', 'high', 'Alerte mémoire élevée Qwen', 'Vérification des ressources'),

-- ============================================
-- CONTENT GENERATION - Llama 3.2 3B
-- ============================================
('content_generation', 'llama3.2:3b', 'latency_ms', 30000, '>', 'medium', 'Alerte temps de génération lent', 'Vérification d''Ollama et optimisation'),
('content_generation', 'llama3.2:3b', 'latency_p50', 10000, '>', 'low', 'Alerte latence p50', 'Vérification des ressources'),
('content_generation', 'llama3.2:3b', 'latency_p95', 20000, '>', 'medium', 'Alerte latence p95', 'Optimisation'),
('content_generation', 'llama3.2:3b', 'latency_p99', 30000, '>', 'high', 'Alerte latence p99', 'Vérification urgente'),
('content_generation', 'llama3.2:3b', 'failure_rate', 0.05, '>', 'high', 'Alerte taux d''échec élevé', 'Analyse des erreurs et ajustement des prompts'),
('content_generation', 'llama3.2:3b', 'inappropriate_content_rate', 0.01, '>', 'critical', 'Alerte contenu inapproprié', 'Révision des prompts et ajout de filtres'),
('content_generation', 'llama3.2:3b', 'timeout_rate', 0.03, '>', 'high', 'Alerte timeout', 'Augmentation du timeout ou optimisation'),
('content_generation', 'llama3.2:3b', 'ram_usage_mb', 6144, '>', 'high', 'Alerte mémoire élevée', 'Vérification des ressources'),
('content_generation', 'llama3.2:3b', 'ttr', 0.40, '<', 'low', 'Alerte diversité lexicale faible', 'Augmentation de la température'),
('content_generation', 'llama3.2:3b', 'repetition_rate', 0.10, '>', 'low', 'Alerte répétitions excessives', 'Ajustement repetition_penalty'),

-- ============================================
-- CONTENT GENERATION - Llama 3.2 1B (fallback)
-- ============================================
('content_generation', 'llama3.2:1b', 'latency_p50', 5000, '>', 'low', 'Alerte latence p50 fallback', 'Vérification'),
('content_generation', 'llama3.2:1b', 'latency_p95', 10000, '>', 'medium', 'Alerte latence p95 fallback', 'Optimisation'),
('content_generation', 'llama3.2:1b', 'ram_usage_mb', 3072, '>', 'high', 'Alerte mémoire fallback', 'Vérification');

-- ============================================
-- SEED: Modèles ML
-- ============================================
INSERT INTO models (name, version, type, provider, description) VALUES
('google-bert-multilingual', 'base', 'classification', 'huggingface', 'BERT multilingue pour détection de haine'),
('camembert-base', '1.0', 'classification', 'huggingface', 'CamemBERT pour détection de dépression (FR)'),
('qwen2.5:1.5b', '1.5b', 'classification', 'ollama', 'Qwen 2.5 pour détection avec raisonnement'),
('xlm-roberta-base', '1.0', 'classification', 'huggingface', 'XLM-RoBERTa pour détection multilingue'),
('llama3.2:3b', '3b', 'generation', 'ollama', 'Llama 3.2 pour génération de contenu'),
('llama3.2:1b', '1b', 'generation', 'ollama', 'Llama 3.2 fallback rapide'),
('git-large-textcaps', 'large', 'captioning', 'huggingface', 'GIT pour captioning d''images'),
('opus-mt-en-fr', '1.0', 'translation', 'huggingface', 'Helsinki NLP traduction EN→FR');
