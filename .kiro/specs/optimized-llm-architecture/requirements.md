# Requirements Document

## Introduction

Ce document définit les exigences pour l'optimisation de l'architecture LLM du projet ETSIA ML API. L'objectif est de remplacer l'architecture actuelle basée uniquement sur Llama 3.2 8B par une architecture hybride optimisée pour un serveur sans GPU (32GB RAM, 2TB SSD), offrant des performances optimales pour la détection de dépression (workflow utilisateur) et la génération de contenu (démos/tests).

## Glossary

- **System**: L'API ETSIA ML qui fournit des services de détection de dépression et de génération de contenu
- **CamemBERT**: Modèle BERT pré-entraîné spécialisé pour la langue française (110M paramètres)
- **XLM-RoBERTa**: Modèle RoBERTa multilingue supportant 100 langues (125M paramètres)
- **Qwen 2.5**: Famille de modèles de langage d'Alibaba Cloud (1.5B, 3B, 7B paramètres)
- **Llama 3.2**: Famille de modèles de langage de Meta (1B, 3B, 8B paramètres)
- **Ollama**: Runtime local pour exécuter des LLM
- **Workflow utilisateur**: Flux d'interaction où l'utilisateur attend une réponse immédiate
- **Latence**: Temps entre la requête et la réponse
- **Inférence**: Processus de génération de prédictions par un modèle
- **Quantification**: Technique de compression de modèle réduisant la précision numérique
- **Hybrid Provider**: Mode permettant d'utiliser différents modèles selon le cas d'usage

## Requirements

### Requirement 1

**User Story:** En tant qu'utilisateur de YANSNET, je veux que la détection de dépression soit quasi-instantanée, afin que mon expérience ne soit pas interrompue par des temps d'attente.

#### Acceptance Criteria

1. WHEN a user submits text for depression detection THEN the System SHALL return a prediction within 500 milliseconds
2. WHEN the System processes French text THEN the System SHALL maintain detection accuracy above 80 percent
3. WHEN the System processes multilingual text THEN the System SHALL support French and English with equivalent accuracy
4. WHEN the System runs on CPU-only hardware THEN the System SHALL complete inference without requiring GPU acceleration
5. WHEN the System loads the depression detection model THEN the System SHALL consume less than 1 gigabyte of RAM

### Requirement 2

**User Story:** En tant qu'administrateur système, je veux utiliser des modèles gratuits et open-source, afin d'éviter les coûts récurrents d'API externes.

#### Acceptance Criteria

1. WHEN the System initializes depression detection THEN the System SHALL use locally hosted models without external API calls
2. WHEN the System initializes content generation THEN the System SHALL use locally hosted models without external API calls
3. WHEN the System downloads models THEN the System SHALL use models available on HuggingFace or Ollama repositories
4. WHEN the System operates THEN the System SHALL incur zero per-request costs
5. WHEN the System stores models THEN the System SHALL require less than 20 gigabytes of disk space total

### Requirement 3

**User Story:** En tant que développeur, je veux une architecture hybride qui utilise le meilleur modèle pour chaque tâche, afin d'optimiser performance et qualité.

#### Acceptance Criteria

1. WHEN the System receives a depression detection request THEN the System SHALL route the request to CamemBERT, XLM-RoBERTa, or Qwen 2.5 1.5B
2. WHEN the System receives a content generation request THEN the System SHALL route the request to Llama 3.2 3B via Ollama
3. WHEN the System switches between models THEN the System SHALL maintain consistent API interfaces
4. WHEN the System configuration changes THEN the System SHALL allow model selection via environment variables
5. WHERE the primary detection model fails THEN the System SHALL fallback to Llama 3.2 1B with extended timeout

### Requirement 4

**User Story:** En tant qu'utilisateur créant du contenu de démonstration, je veux générer des posts et commentaires réalistes en français, même si cela prend quelques secondes.

#### Acceptance Criteria

1. WHEN a demo user requests content generation THEN the System SHALL return generated content within 30 seconds
2. WHEN the System generates French content THEN the System SHALL produce natural and contextually appropriate text
3. WHEN the System generates posts THEN the System SHALL support multiple post types including confession, demande d'aide, and blague
4. WHEN the System generates comments THEN the System SHALL maintain coherence with the original post content
5. WHEN the System generates content THEN the System SHALL not block depression detection requests

### Requirement 5

**User Story:** En tant qu'administrateur système, je veux monitorer les performances des modèles en production, afin de détecter les dégradations de service.

#### Acceptance Criteria

1. WHEN the System processes requests THEN the System SHALL log latency metrics for each model
2. WHEN the System completes predictions THEN the System SHALL track accuracy metrics when ground truth is available
3. WHEN the System encounters errors THEN the System SHALL log error rates per model
4. WHEN the System serves requests THEN the System SHALL expose health check endpoints for each model
5. WHEN the System operates under load THEN the System SHALL track throughput in requests per second

### Requirement 6

**User Story:** En tant que développeur, je veux que le système gère gracieusement les erreurs et les cas limites, afin d'assurer la fiabilité du service.

#### Acceptance Criteria

1. WHEN a model fails to load THEN the System SHALL return a clear error message indicating which model failed
2. WHEN inference times out THEN the System SHALL return a timeout error within the configured timeout period
3. WHEN input text exceeds maximum length THEN the System SHALL truncate or reject the input with an appropriate error
4. WHEN the System runs out of memory THEN the System SHALL log the error and attempt graceful degradation
5. WHEN concurrent requests exceed capacity THEN the System SHALL queue requests or return a rate limit error

### Requirement 7

**User Story:** En tant que développeur, je veux une migration progressive depuis l'architecture actuelle, afin de minimiser les risques et permettre des tests comparatifs.

#### Acceptance Criteria

1. WHEN the System deploys the new architecture THEN the System SHALL maintain backward compatibility with existing API endpoints
2. WHEN the System switches providers THEN the System SHALL allow A/B testing between old and new models
3. WHEN the System migrates THEN the System SHALL preserve existing response formats
4. WHEN the System runs in migration mode THEN the System SHALL log comparative metrics between old and new models
5. WHEN the System completes migration THEN the System SHALL allow rollback to previous architecture via configuration

### Requirement 8

**User Story:** En tant qu'administrateur système, je veux optimiser l'utilisation des ressources serveur, afin de maximiser le nombre de requêtes traitées simultanément.

#### Acceptance Criteria

1. WHEN the System loads models THEN the System SHALL use memory-efficient model loading techniques
2. WHEN the System processes batch requests THEN the System SHALL optimize throughput via batching when possible
3. WHEN the System is idle THEN the System SHALL release unused memory resources
4. WHEN the System serves multiple requests THEN the System SHALL handle at least 10 concurrent depression detection requests
5. WHEN the System serves multiple requests THEN the System SHALL handle at least 2 concurrent content generation requests

### Requirement 9

**User Story:** En tant que data scientist, je veux évaluer la qualité des prédictions, afin de valider que les nouveaux modèles maintiennent ou améliorent la performance.

#### Acceptance Criteria

1. WHEN the System provides predictions THEN the System SHALL include confidence scores between 0 and 1
2. WHEN the System detects depression THEN the System SHALL classify severity as Aucune, Faible, Moyenne, Élevée, or Critique
3. WHEN the System provides predictions THEN the System SHALL optionally include reasoning or explanation
4. WHEN the System processes test datasets THEN the System SHALL compute precision, recall, and F1 scores
5. WHEN the System compares models THEN the System SHALL provide side-by-side performance metrics

### Requirement 10

**User Story:** En tant que développeur, je veux une documentation claire sur le choix et la configuration des modèles, afin de faciliter la maintenance et les futures optimisations.

#### Acceptance Criteria

1. WHEN the System documentation is accessed THEN the System SHALL provide model selection rationale
2. WHEN the System documentation is accessed THEN the System SHALL include performance benchmarks for each model
3. WHEN the System documentation is accessed THEN the System SHALL document environment variable configuration
4. WHEN the System documentation is accessed THEN the System SHALL provide troubleshooting guides for common issues
5. WHEN the System documentation is accessed THEN the System SHALL include examples of model switching and fallback scenarios
