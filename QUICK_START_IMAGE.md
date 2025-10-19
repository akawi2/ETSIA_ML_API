# 🚀 Démarrage Rapide - Modèle d'Analyse d'Images

Guide rapide pour tester le modèle de détection de contenu sensible dans les images.

---

## ⚡ Installation Express

```bash
# 1. Installer les dépendances
pip install -r app/services/sensitive_image_caption/requirements.txt

# 2. Lancer l'API
uvicorn app.main:app --reload
```

---

## 🧪 Test Rapide avec Curl

```bash
# 1. Créer une image de test (ou utilisez une vraie image)
# Utilisez n'importe quelle image JPG/PNG

# 2. Analyser l'image
curl -X POST "http://localhost:8000/api/v1/predict-image" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/your/image.jpg"
```

---

## 🐍 Test Rapide avec Python

```python
import requests

# Analyser une image
with open("votre_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/predict-image",
        files={"image": f}
    )

result = response.json()
print(f"Résultat: {result['prediction']}")
print(f"Sûr: {result['is_safe']}")
print(f"Légende: {result['caption_fr']}")
```

---

## 📊 Exemples de Tests

### Test 1 : Image Normale

**Image :** Chat, paysage, nourriture

**Résultat Attendu :**
```json
{
  "prediction": "SÛR",
  "is_safe": true,
  "caption_fr": "un chat assis..."
}
```

### Test 2 : Image avec Contenu Sensible

**Image :** Contenant drogue, armes, violence

**Résultat Attendu :**
```json
{
  "prediction": "SENSIBLE",
  "is_safe": false,
  "caption_fr": "une *** sur..."
}
```

---

## 🔍 Vérifier les Modèles Disponibles

```bash
# Lister tous les modèles
curl http://localhost:8000/api/v1/models
```

**Réponse :**
```json
{
  "models": {
    "yansnet-llm": {...},
    "sensitive-image-caption": {
      "name": "sensitive-image-caption",
      "version": "1.0.0",
      "author": "Votre Équipe",
      "is_default": false
    }
  },
  "total": 2
}
```

---

## 📦 Test Batch (Plusieurs Images)

```python
import requests

# Préparer 3 images
files = [
    ("images", open("image1.jpg", "rb")),
    ("images", open("image2.jpg", "rb")),
    ("images", open("image3.jpg", "rb"))
]

# Analyser en batch
response = requests.post(
    "http://localhost:8000/api/v1/batch-predict-images",
    files=files
)

result = response.json()
print(f"Images traitées: {result['total_processed']}")

for res in result['results']:
    print(f"Image {res['image_index']}: {res['prediction']}")
```

---

## 🧪 Test avec Postman

### 1. Créer une Requête

- **Method:** POST
- **URL:** `http://localhost:8000/api/v1/predict-image`
- **Body:** Form-data
  - Key: `image`
  - Type: File
  - Value: Sélectionner votre image

### 2. Envoyer

Cliquez sur **Send**

### 3. Vérifier la Réponse

```json
{
  "prediction": "SÛR",
  "confidence": 0.95,
  "caption_fr": "..."
}
```

---

## ⚙️ Vérifier le Health Check

```bash
# Health check global
curl http://localhost:8000/health

# Health check du modèle spécifique
curl http://localhost:8000/api/v1/models/sensitive-image-caption/health
```

---

## 🐛 Dépannage Rapide

### Erreur : "Modèle non disponible"

```bash
# Vérifier les logs au démarrage
# Cherchez :
# ✓ Modèle de détection de contenu sensible (images) enregistré
```

**Si erreur :**
```bash
# Réinstaller les dépendances
pip install transformers torch Pillow sentencepiece --upgrade
```

### Erreur : "Out of Memory"

**Solution :** Utiliser CPU au lieu de GPU

```bash
# Avant de lancer l'API
export CUDA_VISIBLE_DEVICES=""
uvicorn app.main:app --reload
```

### Lenteur Excessive

**Normal :** Première exécution = téléchargement des modèles (~2-3 GB)

**Vérifier :**
```python
# Vérifier si les modèles sont en cache
import os
cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
print(f"Cache: {cache_dir}")
```

---

## 📖 Documentation Complète

Pour plus de détails, consultez :

- **Guide complet :** `docs/IMAGE_ANALYSIS_GUIDE.md`
- **README du modèle :** `app/services/sensitive_image_caption/README.md`
- **Tests :** `tests/test_image_model.py`

---

## 🎯 Prochaines Étapes

1. ✅ Testez avec vos propres images
2. ✅ Personnalisez les mots-clés sensibles
3. ✅ Intégrez dans votre application
4. ✅ Déployez en production

---

**Temps estimé :** 5-10 minutes  
**Niveau :** Débutant

🎉 **Bon test !**
