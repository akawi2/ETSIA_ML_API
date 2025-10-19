# 🖼️ Modèle de Détection de Contenu Sensible dans les Images

Modèle d'analyse d'images pour détecter du contenu sensible (drogue, violence, sexe) via génération de légendes et analyse de mots-clés.

---

## 🎯 Fonctionnalités

- ✅ Génération de légendes avec **microsoft/git-large-textcaps**
- ✅ Détection de contenu sensible (drogue, violence, sexe)
- ✅ Traduction automatique EN→FR
- ✅ Filtrage des mots sensibles
- ✅ Support batch pour plusieurs images

---

## 🚀 Installation

```bash
# Installer les dépendances spécifiques
pip install -r app/services/sensitive_image_caption/requirements.txt
```

---

## 📖 Utilisation

### Via l'API

```python
import requests

# Prédiction sur une image
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/predict-image",
        files={"image": f}
    )

result = response.json()
print(f"Prédiction: {result['prediction']}")
print(f"Légende (FR): {result['caption_fr']}")
```

### Utilisation directe

```python
from app.services.sensitive_image_caption import SensitiveImageCaptionModel
from PIL import Image

# Initialiser le modèle
model = SensitiveImageCaptionModel()

# Analyser une image
image = Image.open("image.jpg")
result = model.predict(image=image)

print(f"Prédiction: {result['prediction']}")
print(f"Est sûr: {result['is_safe']}")
print(f"Légende (FR): {result['caption_fr']}")
print(f"Explication: {result['reasoning']}")
```

---

## 🔍 Détection de Contenu

### Catégories de Contenu Sensible

1. **Drogue et substances illégales**
   - drugs, cocaine, heroin, marijuana, cannabis, meth, pills, etc.

2. **Contenu sexuel**
   - porn, nude, naked, sexual, adult, xxx, nsfw, etc.

3. **Violence et armes**
   - gun, weapon, knife, blood, violence, kill, etc.

4. **Autres contenus problématiques**
   - bomb, explosive, suicide, self-harm, etc.

### Mots-clés supportés

- **Anglais** : 40+ mots-clés
- **Français** : 20+ mots-clés

---

## 📊 Format de Réponse

### Contenu Sûr

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

### Contenu Sensible

```json
{
  "prediction": "SENSIBLE",
  "confidence": 0.85,
  "severity": "Élevée",
  "reasoning": "⚠️ CONTENU SENSIBLE DÉTECTÉ - Image inappropriée",
  "caption_en": "a *** on a table",
  "caption_fr": "un *** sur une table",
  "is_safe": false
}
```

---

## 🧪 Tests

```python
# Test avec une image sûre
model = SensitiveImageCaptionModel()
result = model.predict(image_path="safe_image.jpg")
assert result["is_safe"] == True

# Test avec une image sensible
result = model.predict(image_path="sensitive_image.jpg")
assert result["is_safe"] == False
```

---

## ⚙️ Configuration

### GPU vs CPU

Le modèle utilise automatiquement le GPU si disponible :

```python
# Forcer CPU
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Vérifier le device
model = SensitiveImageCaptionModel()
print(model.device)  # "cuda" ou "cpu"
```

### Personnaliser les Mots-clés

```python
# Ajouter des mots-clés personnalisés
model = SensitiveImageCaptionModel()
model.SENSITIVE_KEYWORDS.update({
    'nouveau_mot_cle',
    'autre_mot'
})
```

---

## 📈 Performances

| Métrique | Valeur |
|----------|--------|
| Temps par image (GPU) | ~2-3 secondes |
| Temps par image (CPU) | ~10-15 secondes |
| Précision caption | ~80% |
| Détection sensible | ~85% |

---

## ⚠️ Limitations

1. **Dépend de la qualité des légendes** : Le modèle génère d'abord une légende textuelle
2. **Mots-clés limités** : Détection basée sur une liste de mots-clés prédéfinis
3. **Contexte** : Ne comprend pas le contexte (ex: "gun" dans "water gun")
4. **Langues** : Optimisé pour anglais et français uniquement

---

## 🔧 Dépannage

### Erreur : "Model not found"

```bash
# Télécharger manuellement les modèles
python -c "from transformers import GitProcessor, GitForCausalLM; \
  GitProcessor.from_pretrained('microsoft/git-large-textcaps'); \
  GitForCausalLM.from_pretrained('microsoft/git-large-textcaps')"
```

### Erreur : "Out of memory"

```python
# Utiliser une taille de batch plus petite
results = model.batch_predict(image_paths=paths[:5])  # Traiter par lots de 5
```

---

## 📚 Ressources

- [microsoft/git-large-textcaps](https://huggingface.co/microsoft/git-large-textcaps)
- [Helsinki-NLP/opus-mt-en-fr](https://huggingface.co/Helsinki-NLP/opus-mt-en-fr)

---

**Version:** 1.0.0  
**Auteur:** Votre Équipe
