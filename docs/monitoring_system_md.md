# SYSTÈME DE MONITORING: MÉTRIQUES ET CRITÈRES

Ce document recense en fonction du modèle, les métriques et les critères d'évaluation nécessaire pour le système de monitoring.

---

## HATECOMMENT DETECTION

### MÉTRIQUES À MONITORER

| Métriques | Description |
|-----------|-------------|
| **Précision** | Pourcentage de vrais positifs parmi les commentaires détectés comme haineux |
| **Recall** | Capacité à détecter les vrais cas de discours haineux |
| **Score F1** | Moyenne harmonique entre précision et rappel |
| **Accuracy** | Précision globale du modèle |
| **Taux de faux positifs et faux négatifs** | Évaluer la fréquence des erreurs de classification du modèle |
| **Temps de réponse du modèle** | Mesure le temps nécessaire pour qu'une prédiction soit effectuée |

### CRITÈRES D'ÉVALUATIONS

| Critères | Seuil |
|----------|-------|
| Alerte de baisse de précision | < 80% |
| Alerte de diminution F1 score | < 88% |
| Alerte de baisse de Recall | < 85% |
| Alertes faux positifs élevés | > 10% |
| Alerte de faux négatifs élevés | > 15% |
| Alerte temps de réponse lent | > 500 ms |

**Lien HF du modèle:** [google-bert/bert-base-multilingual-cased](https://huggingface.co/google-bert/bert-base-multilingual-cased)

---

## SENSITIVE CONTENT DETECTION (IMAGE CAPTIONING)

### MÉTRIQUES À MONITORER

| Métriques | Description |
|-----------|-------------|
| **Précision (Precision)** | Pourcentage de vrais positifs parmi les images détectées comme contenant du contenu sensible |
| **Rappel (Recall)** | Capacité à détecter tous les vrais cas de contenu sensible dans les images |
| **Score F1** | Moyenne harmonique entre précision et rappel pour évaluer l'équilibre du modèle |
| **Accuracy** | Précision globale du modèle sur l'ensemble des prédictions |
| **Taux de faux positifs** | Fréquence des images sûres incorrectement classées comme sensibles |
| **Taux de faux négatifs** | Fréquence des images sensibles non détectées par le système |
| **Temps de réponse** | Temps nécessaire pour générer la légende et détecter le contenu (captioning + détection) |
| **Couverture des mots-clés** | Pourcentage de mots-clés sensibles effectivement détectés dans les légendes |
| **Qualité de la légende** | Précision descriptive du modèle de captioning (BLEU, CIDEr scores) |
| **Taux de détection par catégorie** | Performance de détection par type de contenu (drogue, violence, contenu sexuel, etc.) |

### CRITÈRES D'ÉVALUATION

| Critères | Seuil | Action |
|----------|-------|--------|
| Alerte de baisse de précision | < 85% | Révision des mots-clés et mise à jour du dictionnaire |
| Alerte de diminution F1 score | < 87% | Réévaluation du système de détection et du modèle de captioning |
| Alerte de baisse de Recall | < 90% | Ajout de nouveaux mots-clés sensibles et amélioration du pattern matching |
| Alerte faux positifs élevés | > 8% | Affinage des règles de détection et révision des expressions régulières |
| Alerte faux négatifs élevés | > 5% | Expansion du dictionnaire de mots-clés et amélioration des synonymes |
| Alerte temps de réponse lent | > 2000 ms | Optimisation du pipeline (captioning + traduction + détection) |
| Alerte qualité de légende faible | BLEU < 0.25 | Considérer un modèle de captioning plus performant |
| Alerte couverture mots-clés | < 75% | Enrichissement du dictionnaire multilingue |

### MÉTRIQUES SPÉCIFIQUES AU MODÈLE

#### Modèle de Captioning (microsoft/git-large-textcaps)

| Métrique | Description | Seuil optimal |
|----------|-------------|---------------|
| Longueur moyenne des légendes | Nombre de mots générés par légende | 8-15 mots |
| Confiance du modèle | Score de probabilité des tokens générés | > 0.7 |
| Taux de légendes vides | Fréquence des échecs de génération | < 2% |

#### Modèle de Traduction (Helsinki-NLP/opus-mt-en-fr)

| Métrique | Description | Seuil optimal |
|----------|-------------|---------------|
| Précision de traduction | Exactitude de la traduction des termes sensibles | > 95% |
| Temps de traduction | Latence de la traduction EN→FR | < 200 ms |

### MODÈLES UTILISÉS

- **Captioning:** microsoft/git-large-textcaps
- **Traduction:** Helsinki-NLP/opus-mt-en-fr
- **Détection:** Pattern matching avec dictionnaire de mots-clés multilingues


---

## DEPRESSION DETECTION

### MÉTRIQUES À MONITORER

| Métriques | Description |
|-----------|-------------|
| **Précision (Precision)** | Pourcentage de vrais positifs parmi les textes détectés comme indicateurs de dépression |
| **Rappel (Recall)** | Capacité à détecter tous les vrais cas de dépression dans les textes |
| **Score F1** | Moyenne harmonique entre précision et rappel |
| **Accuracy** | Précision globale du modèle sur l'ensemble des prédictions |
| **Taux de faux positifs** | Fréquence des textes normaux incorrectement classés comme dépressifs |
| **Taux de faux négatifs** | Fréquence des textes dépressifs non détectés (critique pour la sécurité) |
| **Temps de réponse** | Latence de l'inférence (ms) |
| **Score de confiance moyen** | Moyenne des scores de confiance des prédictions |
| **Distribution des sévérités** | Répartition des prédictions par niveau de sévérité |
| **Taux d'utilisation du fallback** | Fréquence d'activation du modèle de secours |
| **Consommation mémoire** | RAM utilisée par le modèle |
| **Throughput** | Nombre de requêtes traitées par seconde |

### CRITÈRES D'ÉVALUATION

| Critères | Seuil | Action |
|----------|-------|--------|
| Alerte de baisse de précision | < 80% | Réévaluation du modèle et ajustement des seuils |
| Alerte de diminution F1 score | < 80% | Analyse des cas d'erreur et fine-tuning |
| Alerte de baisse de Recall | < 85% | Priorité haute - risque de manquer des cas critiques |
| Alerte faux positifs élevés | > 15% | Ajustement du seuil de confiance |
| Alerte faux négatifs élevés | > 10% | Révision urgente - impact sur la sécurité des utilisateurs |
| Alerte temps de réponse lent (CamemBERT) | > 500 ms | Optimisation du modèle ou vérification des ressources |
| Alerte temps de réponse lent (Qwen) | > 1000 ms | Vérification d'Ollama et des ressources |
| Alerte confiance moyenne faible | < 0.6 | Analyse des textes ambigus |
| Alerte taux de fallback élevé | > 5% | Vérification du modèle primaire |
| Alerte mémoire élevée | > 2GB (CamemBERT) / > 4GB (Qwen) | Optimisation ou redémarrage |

### MÉTRIQUES PAR NIVEAU DE SÉVÉRITÉ

| Sévérité | Seuil de confiance | Action recommandée |
|----------|-------------------|-------------------|
| **Critique** | ≥ 0.90 | Alerte immédiate, intervention prioritaire |
| **Élevée** | ≥ 0.75 | Notification aux modérateurs |
| **Moyenne** | ≥ 0.60 | Suivi et surveillance |
| **Faible** | < 0.60 | Enregistrement pour analyse |
| **Aucune** | Prédiction NORMAL | Pas d'action requise |

### MÉTRIQUES SPÉCIFIQUES PAR MODÈLE

#### CamemBERT (camembert-base)

| Métrique | Description | Seuil optimal |
|----------|-------------|---------------|
| Latence p50 | Temps de réponse médian | < 50 ms |
| Latence p95 | Temps de réponse 95e percentile | < 100 ms |
| Latence p99 | Temps de réponse 99e percentile | < 200 ms |
| RAM utilisée | Mémoire consommée | < 600 MB |
| Throughput | Requêtes par seconde | > 20 req/s |
| Temps de chargement | Temps d'initialisation | < 30 s |

#### Qwen 2.5 1.5B (via Ollama)

| Métrique | Description | Seuil optimal |
|----------|-------------|---------------|
| Latence p50 | Temps de réponse médian | < 400 ms |
| Latence p95 | Temps de réponse 95e percentile | < 700 ms |
| Latence p99 | Temps de réponse 99e percentile | < 1000 ms |
| RAM utilisée | Mémoire consommée | < 3 GB |
| Throughput | Requêtes par seconde | > 2 req/s |
| Qualité du raisonnement | Pertinence des explications | Évaluation manuelle |
| Taux de parsing JSON réussi | Réponses correctement formatées | > 95% |

### MODÈLES UTILISÉS

| Provider | Modèle | Paramètres | Usage |
|----------|--------|------------|-------|
| **CamemBERT** | camembert-base | 110M | Détection rapide (FR) |
| **Qwen** | qwen2.5:1.5b | 1.5B | Détection avec raisonnement |
| **XLM-RoBERTa** | xlm-roberta-base | 125M | Détection multilingue |
| **Llama (fallback)** | llama3.2:1b | 1B | Secours si modèle primaire échoue |

**Liens des modèles:**
- CamemBERT: [camembert-base](https://huggingface.co/camembert-base)
- Qwen 2.5: [qwen2.5:1.5b](https://ollama.com/library/qwen2.5)
- XLM-RoBERTa: [xlm-roberta-base](https://huggingface.co/xlm-roberta-base)

---

## CONTENT GENERATION (YANSNET)

### MÉTRIQUES À MONITORER

| Métriques | Description |
|-----------|-------------|
| **Temps de génération** | Latence pour générer un post ou commentaire complet |
| **Qualité du texte** | Cohérence, grammaire et naturalité du contenu généré |
| **Pertinence contextuelle** | Adéquation du contenu généré avec le contexte demandé |
| **Diversité lexicale** | Variété du vocabulaire utilisé (Type-Token Ratio) |
| **Longueur moyenne** | Nombre de mots/caractères générés |
| **Taux de génération réussie** | Pourcentage de requêtes aboutissant à un contenu valide |
| **Taux de contenu inapproprié** | Fréquence de génération de contenu problématique |
| **Throughput** | Nombre de générations par minute |
| **Consommation mémoire** | RAM utilisée pendant la génération |
| **Taux de timeout** | Fréquence des dépassements de délai |

### CRITÈRES D'ÉVALUATION

| Critères | Seuil | Action |
|----------|-------|--------|
| Alerte temps de génération lent | > 30 s | Vérification d'Ollama et optimisation |
| Alerte taux d'échec élevé | > 5% | Analyse des erreurs et ajustement des prompts |
| Alerte contenu inapproprié | > 1% | Révision des prompts et ajout de filtres |
| Alerte timeout | > 3% | Augmentation du timeout ou optimisation |
| Alerte mémoire élevée | > 8 GB | Vérification des ressources |
| Alerte longueur anormale | < 20 ou > 500 mots | Ajustement des paramètres de génération |
| Alerte diversité faible | TTR < 0.4 | Augmentation de la température |
| Alerte répétitions | > 10% de contenu répété | Ajustement des paramètres (repetition_penalty) |

### MÉTRIQUES PAR TYPE DE CONTENU

#### Génération de Posts

| Type de post | Longueur cible | Temps max | Critères spécifiques |
|--------------|----------------|-----------|---------------------|
| **Confession** | 50-200 mots | 20 s | Ton personnel, émotionnel |
| **Demande d'aide** | 30-150 mots | 15 s | Question claire, contexte |
| **Blague** | 20-100 mots | 10 s | Humour approprié |
| **Opinion** | 50-250 mots | 20 s | Argumentation cohérente |
| **Témoignage** | 100-300 mots | 25 s | Récit structuré |

#### Génération de Commentaires

| Métrique | Description | Seuil optimal |
|----------|-------------|---------------|
| Cohérence avec le post | Pertinence par rapport au contenu original | > 80% |
| Ton approprié | Adéquation du ton (supportif, humoristique, etc.) | > 85% |
| Longueur | Nombre de mots | 10-100 mots |
| Temps de génération | Latence | < 15 s |

### MÉTRIQUES SPÉCIFIQUES AU MODÈLE

#### Llama 3.2 3B (via Ollama)

| Métrique | Description | Seuil optimal |
|----------|-------------|---------------|
| Latence p50 | Temps de génération médian | < 10 s |
| Latence p95 | Temps de génération 95e percentile | < 20 s |
| Latence p99 | Temps de génération 99e percentile | < 30 s |
| RAM utilisée | Mémoire consommée | < 6 GB |
| Tokens générés/seconde | Vitesse de génération | > 10 tokens/s |
| Température | Paramètre de créativité | 0.7-0.9 |
| Max tokens | Limite de génération | 256-512 |

#### Llama 3.2 1B (fallback)

| Métrique | Description | Seuil optimal |
|----------|-------------|---------------|
| Latence p50 | Temps de génération médian | < 5 s |
| Latence p95 | Temps de génération 95e percentile | < 10 s |
| RAM utilisée | Mémoire consommée | < 3 GB |
| Qualité | Légèrement inférieure au 3B | Acceptable pour fallback |

### MODÈLES UTILISÉS

| Provider | Modèle | Paramètres | Usage |
|----------|--------|------------|-------|
| **Ollama** | llama3.2:3b | 3B | Génération principale |
| **Ollama** | llama3.2:1b | 1B | Fallback rapide |
| **OpenAI** | gpt-4o-mini | - | Alternative externe (optionnel) |
| **Anthropic** | claude-3-5-sonnet | - | Alternative externe (optionnel) |

**Liens des modèles:**
- Llama 3.2: [llama3.2](https://ollama.com/library/llama3.2)
- GPT-4o-mini: [OpenAI API](https://platform.openai.com/)
- Claude: [Anthropic API](https://www.anthropic.com/)

---

## TABLEAU RÉCAPITULATIF DES ALERTES

| Service | Métrique critique | Seuil d'alerte | Priorité |
|---------|------------------|----------------|----------|
| Depression Detection | Faux négatifs | > 10% | 🔴 Critique |
| Depression Detection | Latence (CamemBERT) | > 500 ms | 🟡 Moyenne |
| Depression Detection | Latence (Qwen) | > 1000 ms | 🟡 Moyenne |
| Depression Detection | Taux fallback | > 5% | 🟡 Moyenne |
| Content Generation | Timeout | > 3% | 🟠 Haute |
| Content Generation | Contenu inapproprié | > 1% | 🔴 Critique |
| Content Generation | Latence | > 30 s | 🟡 Moyenne |
| HateComment | Faux négatifs | > 15% | 🔴 Critique |
| HateComment | Latence | > 500 ms | 🟡 Moyenne |
| Image Caption | Faux négatifs | > 5% | 🔴 Critique |
| Image Caption | Latence | > 2000 ms | 🟡 Moyenne |

---

## ENDPOINTS DE MONITORING

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check global de l'API |
| `GET /api/v1/models` | Liste des modèles chargés |
| `GET /api/v1/depression/health` | Health check détection dépression |
| `GET /api/v1/depression/health/all` | Health check tous les modèles de détection |
| `GET /api/v1/metrics` | Métriques Prometheus (à implémenter) |
