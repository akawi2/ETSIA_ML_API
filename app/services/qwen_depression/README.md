# Qwen 2.5 1.5B Depression Detection

Service de détection de dépression utilisant Qwen 2.5 1.5B via Ollama.

## Caractéristiques

- **Modèle**: Qwen 2.5 1.5B (Alibaba Cloud)
- **Runtime**: Ollama
- **Latence**: 200-500ms sur CPU
- **RAM**: 2-3GB
- **Langues**: Français, Anglais, Multilingue

## Avantages vs CamemBERT

| Aspect | CamemBERT | Qwen 2.5 1.5B |
|--------|-----------|---------------|
| Latence | 20-50ms | 200-500ms |
| RAM | 500MB | 2.5GB |
| Raisonnement | Basique | Avancé |
| Explications | Limitées | Détaillées |
| Contexte | 512 tokens | 2048 tokens |

## Installation

### Prérequis

- Ollama installé et démarré
- Modèle Qwen téléchargé

### Télécharger le modèle

```bash
ollama pull qwen2.5:1.5b
```

### Via Docker

```bash
docker exec ollama-server ollama pull qwen2.5:1.5b
```

## Configuration

Variables d'environnement:

```bash
DETECTION_PROVIDER=qwen
QWEN_DETECTION_MODEL=qwen2.5:1.5b
QWEN_MAX_LENGTH=2048
OLLAMA_BASE_URL=http://localhost:11434
```

## Utilisation

```python
from app.services.qwen_depression import QwenDepressionModel

# Initialiser
model = QwenDepressionModel()

# Prédiction simple
result = model.predict("Je me sens triste et sans énergie.")
print(result)
# {
#     "prediction": "DÉPRESSION",
#     "confidence": 0.85,
#     "severity": "Moyenne",
#     "reasoning": "Le texte exprime de la tristesse et un manque d'énergie...",
#     "processing_time": 350.5
# }

# Prédiction batch
results = model.batch_predict([
    "Je suis heureux aujourd'hui!",
    "Tout me semble vide et sans sens."
])
```

## API Response

```json
{
    "prediction": "DÉPRESSION" | "NORMAL",
    "confidence": 0.0 - 1.0,
    "severity": "Aucune" | "Faible" | "Moyenne" | "Élevée" | "Critique",
    "reasoning": "Explication de l'analyse",
    "processing_time": 350.5
}
```

## Niveaux de sévérité

| Sévérité | Confidence |
|----------|------------|
| Critique | >= 0.90 |
| Élevée | >= 0.75 |
| Moyenne | >= 0.60 |
| Faible | < 0.60 |
| Aucune | Prédiction NORMAL |

## Dépannage

### Ollama non accessible

```bash
# Vérifier que Ollama est démarré
curl http://localhost:11434/api/tags

# Démarrer Ollama
ollama serve
```

### Modèle non trouvé

```bash
# Lister les modèles
ollama list

# Télécharger Qwen
ollama pull qwen2.5:1.5b
```

### Timeout

Augmenter le timeout dans la configuration:

```python
model = QwenDepressionModel(timeout=60.0)
```
