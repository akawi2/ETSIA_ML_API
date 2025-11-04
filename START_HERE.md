# 🚀 START HERE - Démarrage Complet du Projet

Guide de démarrage complet pour lancer l'API avec tous les modèles (texte + images).

---

## 📋 Checklist Avant de Commencer

- [ ] Python 3.8+ installé
- [ ] Git installé
- [ ] Clés API configurées (OpenAI/Anthropic) OU Ollama installé
- [ ] ~5 GB d'espace disque (pour les modèles d'images)

---

## ⚡ Installation Rapide

### 1. Cloner et Configurer

```bash
# Cloner le projet
git clone <votre-repo>
cd ETSIA_ML_API

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate
```

### 2. Installer les Dépendances

```bash
# Dépendances principales
pip install -r requirements.txt

# Dépendances pour l'analyse d'images
pip install -r app/services/sensitive_image_caption/requirements.txt
```

**Packages principaux installés :**
- FastAPI, Uvicorn (API)
- Transformers, Torch (ML)
- OpenAI, Anthropic (LLM)
- Pillow (Images)

### 3. Configurer les Variables d'Environnement

```bash
# Copier le fichier exemple
copy .env.example .env

# Éditer .env avec vos configurations
notepad .env
```

**Configuration minimale pour LLM local (gratuit) :**
```env
LLM_PROVIDER=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**OU avec GPT (payant mais rapide) :**
```env
LLM_PROVIDER=gpt
OPENAI_API_KEY=sk-votre-cle-ici
OPENAI_MODEL=gpt-4o-mini
```

---

## 🎬 Lancer l'API

### Méthode 1 : Développement (Recommandé)

```bash
# Activer l'environnement virtuel
.\venv\Scripts\activate

# Lancer l'API en mode développement
uvicorn app.main:app --reload --port 8000
```

**Vous devriez voir :**
```
======================================================================
Depression Detection API v1.0.0
Architecture Multi-Modèles
======================================================================

📦 Enregistrement des modèles...
----------------------------------------------------------------------
✓ yansnet-llm v1.0.0 by Équipe YANSNET [DÉFAUT]
✓ Modèle de détection de contenu sensible (images) enregistré
✓ sensitive-image-caption v1.0.0 by Votre Équipe
----------------------------------------------------------------------
✓ 2 modèle(s) enregistré(s)

======================================================================
✓ API démarrée avec succès!
📚 Documentation: http://localhost:8000/docs
📋 Modèles disponibles: http://localhost:8000/api/v1/models
======================================================================
```

### Méthode 2 : Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Méthode 3 : Docker

```bash
# Construire l'image
docker build -t etsia-ml-api .

# Lancer le conteneur
docker run -p 8000:8000 --env-file .env etsia-ml-api
```

---

## 🧪 Tester l'Installation

### Test 1 : Health Check

```bash
curl http://localhost:8000/health
```

**Résultat attendu :**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "total": 2,
    "available": ["yansnet-llm", "sensitive-image-caption"]
  }
}
```

### Test 2 : Lister les Modèles

```bash
curl http://localhost:8000/api/v1/models
```

**Résultat attendu :**
```json
{
  "models": {
    "yansnet-llm": {...},
    "sensitive-image-caption": {...}
  },
  "total": 2
}
```

### Test 3 : Analyse de Texte

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"I feel so sad and hopeless\", \"include_reasoning\": true}"
```

### Test 4 : Analyse d'Image

```bash
# Créer une image de test ou utiliser une vraie image
curl -X POST http://localhost:8000/api/v1/predict-image \
  -F "image=@path/to/your/image.jpg"
```

### Test 5 : Documentation Interactive

**Ouvrir dans votre navigateur :**
```
http://localhost:8000/docs
```

Vous pouvez tester tous les endpoints directement depuis Swagger UI !

---

## 📊 Tests Python

### Test avec le Script de Démo

```bash
# Test du modèle d'images
python demo_image_analysis.py

# Test avec vos propres images
python demo_image_analysis.py image1.jpg image2.jpg
```

### Tests Unitaires

```bash
# Tous les tests
pytest tests/ -v

# Tests du modèle texte uniquement
pytest tests/test_api.py -v

# Tests du modèle images uniquement
pytest tests/test_image_model.py -v

# Tests avec couverture
pytest tests/ --cov=app --cov-report=html
```

---

## 🐛 Dépannage

### Problème : "Modèle non enregistré"

**Symptôme :** L'API démarre mais un modèle manque

**Solution :**
```bash
# Vérifier les logs au démarrage
# Chercher : ✗ Erreur lors de l'enregistrement...

# Réinstaller les dépendances manquantes
pip install transformers torch Pillow sentencepiece --upgrade
```

### Problème : "Out of Memory"

**Symptôme :** Erreur lors du chargement du modèle d'images

**Solution 1 - Utiliser CPU :**
```bash
# Windows
set CUDA_VISIBLE_DEVICES=
uvicorn app.main:app --reload

# Linux/Mac
export CUDA_VISIBLE_DEVICES=""
uvicorn app.main:app --reload
```

**Solution 2 - Augmenter la mémoire :**
- Fermer les autres applications
- Redémarrer le système

### Problème : "Ollama not found"

**Symptôme :** Erreur avec `LLM_PROVIDER=local`

**Solution :**
```bash
# 1. Installer Ollama
# Windows: https://ollama.ai/download
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. Télécharger un modèle
ollama pull llama3.2

# 3. Lancer le serveur
ollama serve

# 4. Vérifier
curl http://localhost:11434/api/tags
```

### Problème : "Connection refused"

**Symptôme :** Impossible de se connecter à l'API

**Solutions :**
- Vérifier que l'API est bien lancée
- Vérifier le port (défaut: 8000)
- Vérifier le firewall
- Essayer : `http://127.0.0.1:8000` au lieu de `localhost`

### Problème : Lenteur Excessive (Première Fois)

**Explication :** Les modèles se téléchargent automatiquement (~2-3 GB)

**Progression :**
```
Downloading microsoft/git-large-textcaps...
Downloading Helsinki-NLP/opus-mt-en-fr...
```

**Solution :** Patienter ou pré-télécharger :
```bash
python -c "from transformers import GitProcessor, GitForCausalLM; \
  GitProcessor.from_pretrained('microsoft/git-large-textcaps'); \
  GitForCausalLM.from_pretrained('microsoft/git-large-textcaps')"
```

---

## 📚 Documentation

### Guides Principaux

| Document | Description |
|----------|-------------|
| **README.md** | Vue d'ensemble du projet |
| **QUICK_START_IMAGE.md** | Démarrage rapide analyse d'images |
| **docs/IMAGE_ANALYSIS_GUIDE.md** | Guide complet analyse d'images |
| **docs/ADD_YOUR_MODEL.md** | Ajouter votre propre modèle |
| **docs/API_CONTRACT.md** | Contrat API détaillé |
| **CHANGELOG.md** | Historique des modifications |

### Accès Rapide

```bash
# Documentation interactive
http://localhost:8000/docs

# Alternative (ReDoc)
http://localhost:8000/redoc

# Health check
http://localhost:8000/health

# Liste des modèles
http://localhost:8000/api/v1/models
```

---

## 🎯 Prochaines Étapes

### 1. Tester avec Vos Données

```python
import requests

# Analyser un texte
response = requests.post(
    "http://localhost:8000/api/v1/predict",
    json={"text": "Votre texte ici"}
)
print(response.json())

# Analyser une image
with open("votre_image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/predict-image",
        files={"image": f}
    )
print(response.json())
```

### 2. Personnaliser le Modèle d'Images

```python
# Éditer app/services/sensitive_image_caption/sensitive_image_caption_model.py

# Ajouter vos propres mots-clés sensibles
SENSITIVE_KEYWORDS.update({
    'votre_mot_cle',
    'autre_mot'
})
```

### 3. Ajouter Votre Propre Modèle

Suivre le guide : **docs/ADD_YOUR_MODEL.md**

### 4. Déployer en Production

Voir : **docs/DEPLOYMENT.md**

---

## 💡 Conseils Pro

### Optimisation Performance

```bash
# Utiliser GPU si disponible
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Vérifier
python -c "import torch; print(torch.cuda.is_available())"
```

### Monitoring

```bash
# Logs en temps réel
tail -f app.log

# Métriques
curl http://localhost:8000/health
```

### Sécurité

1. **Ne jamais commit .env** : Contient vos clés API
2. **Utiliser HTTPS** en production
3. **Activer l'authentification** si besoin
4. **Rate limiting** pour éviter les abus

---

## ✅ Checklist de Démarrage Réussi

Vérifiez que tout fonctionne :

- [ ] L'API démarre sans erreur
- [ ] 2 modèles sont enregistrés (yansnet-llm, sensitive-image-caption)
- [ ] `/health` retourne "healthy"
- [ ] `/api/v1/models` liste les 2 modèles
- [ ] `/api/v1/predict` fonctionne avec un texte
- [ ] `/api/v1/predict-image` fonctionne avec une image
- [ ] `/docs` affiche la documentation Swagger
- [ ] Les tests passent : `pytest tests/`

---

## 🆘 Support

### Ressources

- **Documentation** : Dossier `docs/`
- **Exemples** : Dossier `tests/`
- **Démo** : `demo_image_analysis.py`

### Commandes Utiles

```bash
# Réinstaller tout
pip install -r requirements.txt --force-reinstall

# Nettoyer le cache
pip cache purge

# Vérifier les versions
pip list | grep -E "fastapi|transformers|torch"

# Logs détaillés
uvicorn app.main:app --log-level debug
```

---

## 🎉 Félicitations !

Votre API multi-modèles est maintenant opérationnelle avec :
- ✅ Détection de dépression dans les textes (LLM)
- ✅ Détection de contenu sensible dans les images (Vision)
- ✅ Architecture extensible pour ajouter d'autres modèles
- ✅ Documentation complète et tests

**Temps estimé :** 10-20 minutes  
**Niveau :** Débutant à Intermédiaire

---

**Bon développement ! 🚀**

*Si vous rencontrez des problèmes, consultez la section Dépannage ou les guides dans `docs/`*
