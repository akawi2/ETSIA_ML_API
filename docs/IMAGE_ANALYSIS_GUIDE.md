# 🖼️ Guide d'Utilisation - Analyse d'Images

Guide complet pour utiliser le modèle de détection de contenu sensible dans les images.

---

## 🎯 Vue d'Ensemble

Le modèle **SensitiveImageCaptionModel** analyse les images pour détecter du contenu sensible :
- 🚫 **Drogue** et substances illégales
- 🔫 **Violence** et armes
- 🔞 **Contenu sexuel**
- 💣 **Autres contenus problématiques**

**Processus :**
1. Génère une légende de l'image (microsoft/git-large-textcaps)
2. Détecte les mots-clés sensibles
3. Traduit en français
4. Retourne une alerte si contenu détecté

---

## 📦 Installation

### 1. Installer les Dépendances

```bash
# Dépendances principales (déjà installées)
pip install -r requirements.txt

# Dépendances spécifiques au modèle d'images
pip install -r app/services/sensitive_image_caption/requirements.txt
```

**Packages requis :**
- `transformers>=4.30.0`
- `torch>=2.0.0`
- `Pillow>=9.5.0`
- `sentencepiece>=0.1.99`

### 2. Télécharger les Modèles (Optionnel)

Les modèles se téléchargent automatiquement au premier lancement. Pour pré-télécharger :

```python
from transformers import GitProcessor, GitForCausalLM, pipeline

# Modèle de génération de légendes
GitProcessor.from_pretrained("microsoft/git-large-textcaps")
GitForCausalLM.from_pretrained("microsoft/git-large-textcaps")

# Modèle de traduction
pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
```

---

## 🚀 Utilisation

### Via l'API REST

#### **1. Analyser une Image Unique**

```bash
# Avec curl
curl -X POST "http://localhost:8000/api/v1/predict-image" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/image.jpg"
```

**Réponse :**
```json
{
  "prediction": "SÛR",
  "confidence": 0.95,
  "severity": "Aucune",
  "reasoning": "✅ Contenu sûr - Aucun élément sensible détecté",
  "caption_en": "a cat sitting on a table",
  "caption_fr": "un chat assis sur une table",
  "is_safe": true,
  "model_used": "sensitive-image-caption"
}
```

#### **2. Avec Python requests**

```python
import requests

# Analyser une image
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/predict-image",
        files={"image": f}
    )

result = response.json()
print(f"Prédiction: {result['prediction']}")
print(f"Sûr: {result['is_safe']}")
print(f"Légende FR: {result['caption_fr']}")
```

#### **3. Analyser Plusieurs Images (Batch)**

```python
import requests

# Préparer les images
files = [
    ("images", open("image1.jpg", "rb")),
    ("images", open("image2.jpg", "rb")),
    ("images", open("image3.jpg", "rb"))
]

# Envoyer
response = requests.post(
    "http://localhost:8000/api/v1/batch-predict-images",
    files=files
)

result = response.json()
print(f"Traité: {result['total_processed']} images")

for i, res in enumerate(result['results']):
    print(f"\nImage {i+1}:")
    print(f"  Prédiction: {res['prediction']}")
    print(f"  Légende: {res['caption_fr']}")
```

### Utilisation Directe (Python)

#### **1. Import et Initialisation**

```python
from app.services.sensitive_image_caption import SensitiveImageCaptionModel
from PIL import Image

# Initialiser le modèle
model = SensitiveImageCaptionModel()
```

#### **2. Analyser une Image**

```python
# Charger l'image
image = Image.open("path/to/image.jpg")

# Prédire
result = model.predict(image=image)

# Afficher les résultats
print(f"Prédiction: {result['prediction']}")
print(f"Confiance: {result['confidence']:.2%}")
print(f"Sûr: {result['is_safe']}")
print(f"Légende EN: {result['caption_en']}")
print(f"Légende FR: {result['caption_fr']}")
print(f"Explication: {result['reasoning']}")
```

#### **3. Analyser Plusieurs Images**

```python
from PIL import Image

# Charger les images
images = [
    Image.open("image1.jpg"),
    Image.open("image2.jpg"),
    Image.open("image3.jpg")
]

# Prédire en batch
results = model.batch_predict(images=images)

# Afficher
for i, result in enumerate(results):
    print(f"\nImage {i+1}:")
    print(f"  Prédiction: {result['prediction']}")
    print(f"  Légende FR: {result['caption_fr']}")
    print(f"  Sûr: {result['is_safe']}")
```

---

## 📊 Exemples de Résultats

### Image Sûre (Chat)

**Input :** `cat.jpg`

**Output :**
```json
{
  "prediction": "SÛR",
  "confidence": 0.95,
  "severity": "Aucune",
  "reasoning": "✅ Contenu sûr - Aucun élément sensible détecté",
  "caption_en": "a cat sitting on a table",
  "caption_fr": "un chat assis sur une table",
  "is_safe": true
}
```

### Image Sensible (Détection de drogue)

**Input :** `sensitive.jpg`

**Output :**
```json
{
  "prediction": "SENSIBLE",
  "confidence": 0.85,
  "severity": "Élevée",
  "reasoning": "⚠️ CONTENU SENSIBLE DÉTECTÉ - Cette image contient un contenu inapproprié",
  "caption_en": "a *** on a table",
  "caption_fr": "une *** sur une table",
  "is_safe": false
}
```

---

## 🔍 Mots-clés Détectés

### Catégories

| Catégorie | Exemples EN | Exemples FR |
|-----------|-------------|-------------|
| **Drogue** | drugs, cocaine, heroin, marijuana, weed | drogue, cocaïne, héroïne |
| **Violence** | gun, weapon, knife, blood, kill | arme, couteau, sang, tuer |
| **Sexe** | porn, nude, naked, sexual | pornographie, nudité, sexuel |
| **Autres** | bomb, explosive, suicide | bombe, explosif, suicide |

### Liste Complète

Voir `SENSITIVE_KEYWORDS` dans le code source.

---

## 🧪 Tests

### Lancer les Tests

```bash
# Tous les tests du modèle
pytest tests/test_image_model.py -v

# Tests unitaires uniquement
pytest tests/test_image_model.py -k "test_model" -v

# Tests d'intégration API
pytest tests/test_image_model.py -k "test_predict" -v

# Tests de performance (plus lents)
pytest tests/test_image_model.py -k "test_performance" -v
```

### Créer vos Propres Tests

```python
import pytest
from app.services.sensitive_image_caption import SensitiveImageCaptionModel
from PIL import Image

def test_custom_image():
    """Test avec votre image"""
    model = SensitiveImageCaptionModel()
    
    # Votre image
    image = Image.open("my_image.jpg")
    
    # Prédire
    result = model.predict(image=image)
    
    # Vérifier
    assert result["prediction"] in ["SENSIBLE", "SÛR"]
    assert 0 <= result["confidence"] <= 1
    assert "caption_fr" in result
```

---

## ⚙️ Configuration Avancée

### Utiliser GPU

```python
import torch

# Vérifier si GPU disponible
print(f"CUDA disponible: {torch.cuda.is_available()}")

# Le modèle utilise automatiquement le GPU si disponible
model = SensitiveImageCaptionModel()
print(f"Device: {model.device}")  # "cuda" ou "cpu"
```

### Forcer CPU

```python
import os

# Désactiver CUDA
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Initialiser le modèle
model = SensitiveImageCaptionModel()
```

### Personnaliser les Mots-clés

```python
# Ajouter des mots-clés personnalisés
model = SensitiveImageCaptionModel()

# Ajouter
model.SENSITIVE_KEYWORDS.update({
    'nouveau_mot',
    'autre_mot'
})

# Retirer
model.SENSITIVE_KEYWORDS.discard('mot_existant')
```

---

## 📈 Performances

### Temps de Traitement

| Configuration | Temps/Image |
|---------------|-------------|
| GPU (CUDA) | 2-3 secondes |
| CPU | 10-15 secondes |

### Optimisation

```python
# Pour traiter beaucoup d'images
images = [Image.open(f"img{i}.jpg") for i in range(100)]

# Traiter par batch de 5
batch_size = 5
for i in range(0, len(images), batch_size):
    batch = images[i:i+batch_size]
    results = model.batch_predict(images=batch)
```

---

## ⚠️ Limitations

1. **Dépend de la qualité des légendes**
   - Le modèle génère d'abord une légende textuelle
   - Si la légende est imprécise, la détection peut échouer

2. **Mots-clés limités**
   - Détection basée sur une liste de mots-clés
   - Peut manquer certains contenus subtils

3. **Contexte**
   - Ne comprend pas le contexte
   - Ex: "water gun" sera détecté comme "gun"

4. **Langues**
   - Optimisé pour anglais et français
   - Autres langues non supportées

---

## 🔧 Dépannage

### Erreur : "Out of Memory"

**Solution :** Réduire la taille du batch ou utiliser CPU

```python
# Traiter une image à la fois
for image in images:
    result = model.predict(image=image)
```

### Erreur : "Model not found"

**Solution :** Télécharger manuellement les modèles

```bash
python -c "from transformers import GitProcessor, GitForCausalLM; \
  GitProcessor.from_pretrained('microsoft/git-large-textcaps'); \
  GitForCausalLM.from_pretrained('microsoft/git-large-textcaps')"
```

### Performance Lente

**Solutions :**
1. Utiliser un GPU
2. Réduire la taille des images
3. Utiliser un modèle plus petit

---

## 📚 Ressources

- [microsoft/git-large-textcaps](https://huggingface.co/microsoft/git-large-textcaps)
- [Helsinki-NLP/opus-mt-en-fr](https://huggingface.co/Helsinki-NLP/opus-mt-en-fr)
- [Documentation Transformers](https://huggingface.co/docs/transformers)

---

## 🤝 Contribution

Pour améliorer le modèle :

1. Ajouter des mots-clés dans `SENSITIVE_KEYWORDS`
2. Améliorer la détection (ML au lieu de règles)
3. Support de nouvelles langues
4. Optimiser les performances

---

**Version:** 1.0.0  
**Dernière mise à jour:** Octobre 2025
