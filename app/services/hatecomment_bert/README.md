# 🤖 Modèle HateComment BERT

Modèle de détection de hate speech (commentaires haineux) avec BERT multilingue.

## 📋 Description

Ce modèle utilise un BERT multilingue fine-tuné pour détecter les commentaires haineux en français et anglais. Il est intégré dans l'API de détection de dépression mais conserve sa fonction originale de classification de hate speech.

## 🏗️ Architecture

- **Modèle de base** : `bert-base-multilingual-cased`
- **Tâche** : Classification binaire (haineux/non-haineux)
- **Langues supportées** : Français, Anglais (extensible)
- **Format de sortie** : Adapté au format de l'API de dépression

## 📊 Données d'Entraînement

### Datasets Utilisés
1. **Français** : Paul/hatecheck-french (~3,700 exemples)
2. **Anglais** : tweet_eval hate speech (~3,000 exemples)

### Performance
- **Accuracy** : ~82%
- **F1-Score** : ~77%
- **Précision** : ~73%
- **Recall** : ~82%

## 🔄 Format de Sortie

### Adaptation au Format API

| Prédiction Hate | Confiance | → | Format API | Sévérité |
|----------------|-----------|---|------------|----------|
| Haineux | > 90% | → | HAINEUX | Critique |
| Haineux | 80-90% | → | HAINEUX | Élevée |
| Haineux | 60-80% | → | HAINEUX | Moyenne |
| Haineux | < 60% | → | HAINEUX | Faible |
| Non-haineux | Toute | → | NON-HAINEUX | Aucune |

**Note** : Le modèle utilise maintenant les vraies étiquettes de hate speech.

## 🚀 Utilisation

### Installation des Dépendances

```bash
pip install -r app/services/hatecomment_bert/requirements.txt
```

### Utilisation via API

```bash
# Prédiction simple
curl -X POST "http://localhost:8000/api/v1/predict?model_name=hatecomment-bert" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je déteste tout le monde"}'

# Prédiction batch
curl -X POST "http://localhost:8000/api/v1/batch-predict?model_name=hatecomment-bert" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["I hate everyone", "I love this day"]}'
```

### Utilisation Directe

```python
from app.services.hatecomment_bert import HateCommentBertModel

# Initialiser le modèle
model = HateCommentBertModel()

# Prédiction simple
result = model.predict("Je déteste tout le monde")
print(result)
# {
#   "prediction": "HAINEUX",
#   "confidence": 0.85,
#   "severity": "Élevée",
#   "reasoning": "Commentaire classifié comme haineux avec une confiance de 85.00%. Le contenu contient des éléments de discours haineux.",
#   "hate_classification": "haineux",
#   "original_label": "LABEL_1"
# }
```

## 🔧 Configuration

### Modèle Fine-tuné (Optionnel)

Si vous avez un modèle fine-tuné :

```python
model = HateCommentBertModel(model_path="./path/to/fine_tuned_model")
```

### Device

Le modèle détecte automatiquement CUDA/CPU :
- GPU disponible → Utilise CUDA
- Pas de GPU → Utilise CPU

## 📈 Métriques Retournées

### Prédiction Standard
```json
{
  "prediction": "HAINEUX|NON-HAINEUX",
  "confidence": 0.75,
  "severity": "Aucune|Faible|Moyenne|Élevée|Critique",
  "reasoning": "Explication détaillée"
}
```

### Métriques Additionnelles
```json
{
  "hate_classification": "haineux|non-haineux",
  "original_label": "LABEL_1|LABEL_0",
  "model_fine_tuned": true
}
```

## ⚠️ Limitations

1. **Fonction spécialisée** : Détecte uniquement le hate speech, pas la dépression directement
2. **Langues** : Optimisé pour français/anglais
3. **Contexte** : Ne prend pas en compte le contexte conversationnel
4. **Biais** : Peut avoir des biais selon les données d'entraînement

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/test_hatecomment_bert.py -v

# Test rapide
python app/services/hatecomment_bert/hatecomment_bert_model.py
```

## 📝 Améliorations Futures

1. **Fine-tuning** : Utiliser un modèle fine-tuné spécifique au domaine
2. **Multilingue** : Étendre à d'autres langues
3. **Contexte** : Analyser des conversations complètes
4. **Précision** : Améliorer la détection de nuances dans le hate speech

## 👥 Auteurs

Équipe ETSIA - Projet académique X5 Semestre 9

---

**Note** : Ce modèle détecte le hate speech et est à usage de recherche uniquement.
