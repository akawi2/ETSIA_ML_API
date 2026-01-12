-- Ajouter tous les modèles ML au système de monitoring

INSERT INTO model_versions (model_name, version, provider, description, deployed_at, is_active) VALUES 
    -- Hate Comment Detection
    ('google-bert-multilingual', '1.0.0', 'huggingface', 'BERT multilingue pour détection de haine', NOW(), TRUE),
    
    -- Depression Detection
    ('camembert-depression', '1.0.0', 'huggingface', 'CamemBERT fine-tuned pour détection de dépression (FR)', NOW(), TRUE),
    ('qwen-depression', '1.0.0', 'ollama', 'Qwen 2.5 1.5B pour détection de dépression avec raisonnement', NOW(), TRUE),
    ('xlm-roberta-depression', '1.0.0', 'huggingface', 'XLM-RoBERTa pour détection multilingue', NOW(), TRUE),
    
    -- Content Generation
    ('llama-generation', '1.0.0', 'ollama', 'Llama 3.2 3B pour génération de contenu', NOW(), TRUE),
    ('llama-fallback', '1.0.0', 'ollama', 'Llama 3.2 1B fallback rapide', NOW(), TRUE),
    
    -- Image Captioning
    ('git-large-captioning', '1.0.0', 'huggingface', 'GIT Large pour captioning d''images', NOW(), TRUE),
    ('opus-mt-translation', '1.0.0', 'huggingface', 'Helsinki NLP traduction EN→FR', NOW(), TRUE)
ON CONFLICT (model_name, version) DO UPDATE SET 
    description = EXCLUDED.description,
    is_active = TRUE;

-- Health checks initiaux pour tous les modèles
INSERT INTO model_health_checks (model_name, provider, status, details) VALUES 
    ('google-bert-multilingual', 'huggingface', 'unknown', '{"message": "Awaiting first health check", "service": "hate_comment"}'),
    ('camembert-depression', 'huggingface', 'unknown', '{"message": "Awaiting first health check", "service": "depression_detection"}'),
    ('qwen-depression', 'ollama', 'unknown', '{"message": "Awaiting first health check", "service": "depression_detection"}'),
    ('xlm-roberta-depression', 'huggingface', 'unknown', '{"message": "Awaiting first health check", "service": "depression_detection"}'),
    ('llama-generation', 'ollama', 'unknown', '{"message": "Awaiting first health check", "service": "content_generation"}'),
    ('llama-fallback', 'ollama', 'unknown', '{"message": "Awaiting first health check", "service": "content_generation"}'),
    ('git-large-captioning', 'huggingface', 'unknown', '{"message": "Awaiting first health check", "service": "image_captioning"}'),
    ('opus-mt-translation', 'huggingface', 'unknown', '{"message": "Awaiting first health check", "service": "image_captioning"}');
