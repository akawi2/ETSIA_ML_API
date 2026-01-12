-- Migration des règles depuis metrics_catalog.json

INSERT INTO alert_rules (service, model, metric, threshold, operator, priority, description) VALUES
-- Hate Comment
('hate_comment', NULL, 'precision', 0.80, '<', 'Critique', 'Alerte de baisse de précision'),
('hate_comment', NULL, 'f1_score', 0.88, '<', 'Moyenne', 'Alerte de diminution F1 score'),
('hate_comment', NULL, 'recall', 0.85, '<', 'Haute', 'Alerte de baisse de Recall'),
('hate_comment', NULL, 'false_positive_rate', 0.10, '>', 'Critique', 'Alertes faux positifs élevés'),
('hate_comment', NULL, 'false_negative_rate', 0.15, '>', 'Critique', 'Alerte de faux négatifs élevés'),
('hate_comment', NULL, 'latency', 500, '>', 'Moyenne', 'Alerte temps de réponse lent'),

-- Image Captioning
('image_captioning', NULL, 'precision', 0.85, '<', 'Moyenne', 'Alerte de baisse de précision'),
('image_captioning', NULL, 'recall', 0.90, '<', 'Moyenne', 'Alerte de baisse de Recall'),
('image_captioning', NULL, 'false_positive_rate', 0.08, '>', 'Moyenne', 'Alerte faux positifs élevés'),
('image_captioning', NULL, 'false_negative_rate', 0.05, '>', 'Critique', 'Alerte faux négatifs élevés'),
('image_captioning', NULL, 'latency', 2000, '>', 'Moyenne', 'Alerte temps de réponse lent'),
('image_captioning', NULL, 'bleu_score', 0.25, '<', 'Haute', 'Alerte qualité de légende faible'),
('image_captioning', NULL, 'keyword_coverage', 0.75, '<', 'Moyenne', 'Alerte couverture mots-clés'),

-- Depression Detection
('depression_detection', NULL, 'precision', 0.80, '<', 'Critique', 'Alerte de baisse de précision'),
('depression_detection', NULL, 'recall', 0.85, '<', 'Critique', 'Alerte de baisse de Recall'),
('depression_detection', NULL, 'false_positive_rate', 0.15, '>', 'Haute', 'Alerte faux positifs élevés'),
('depression_detection', NULL, 'false_negative_rate', 0.10, '>', 'Critique', 'Alerte faux négatifs élevés'),
('depression_detection', 'camembert-base', 'latency', 500, '>', 'Moyenne', 'Alerte latence CamemBERT'),
('depression_detection', 'qwen2.5:1.5b', 'latency', 1000, '>', 'Moyenne', 'Alerte latence Qwen'),
('depression_detection', NULL, 'confidence', 0.60, '<', 'Moyenne', 'Alerte confiance faible'),
('depression_detection', NULL, 'fallback_rate', 0.05, '>', 'Moyenne', 'Alerte taux de fallback élevé'),
('depression_detection', 'camembert-base', 'ram_usage', 2048, '>', 'Haute', 'Alerte mémoire CamemBERT'),
('depression_detection', 'qwen2.5:1.5b', 'ram_usage', 4096, '>', 'Haute', 'Alerte mémoire Qwen'),

-- Content Generation
('content_generation', NULL, 'latency', 30000, '>', 'Moyenne', 'Alerte génération lente'),
('content_generation', NULL, 'failure_rate', 0.05, '>', 'Haute', 'Alerte taux échec élevé'),
('content_generation', NULL, 'inappropriate_content_rate', 0.01, '>', 'Critique', 'Alerte contenu inapproprié'),
('content_generation', NULL, 'timeout_rate', 0.03, '>', 'Haute', 'Alerte timeout'),
('content_generation', NULL, 'ram_usage', 8192, '>', 'Haute', 'Alerte mémoire élevée'),
('content_generation', NULL, 'ttr', 0.40, '<', 'Faible', 'Alerte diversité lexicale faible'),
('content_generation', NULL, 'repetition_rate', 0.10, '>', 'Faible', 'Alerte répétitions excessives');
