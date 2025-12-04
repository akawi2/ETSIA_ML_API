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