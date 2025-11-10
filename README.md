# 🧠 API de Détection de Dépression avec LLM + 🖼️ Analyse d'Images

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

API REST professionnelle multi-modèles pour :
- 📝 **Détection de dépression** dans les textes (LLM)
- 🖼️ **Analyse de contenu sensible** dans les images (Vision + NLP)
- ✍️ **Génération de contenu** pour le réseau social YANSNET (LLM)

**Projet académique - X5 Semestre 9 ETSIA**

> ⚠️ **Avertissement** : Ce système est à usage de RECHERCHE uniquement. Il ne remplace PAS un diagnostic médical professionnel.

---

## 🎯 Résultats

### Modèles de Détection de Dépression (Texte)

| Modèle | Précision | Vitesse | Avantages |
|--------|-----------|---------|-----------|
| **LLM (GPT-4o-mini)** | **75%** | 0.3/s | Explications détaillées, cas ambigus |
| **LLM (Llama 3.2 local)** | **75%** | 0.3/s | Gratuit, privé, offline |
| **LLM (Claude)** | **75%** | 0.3/s | Haute qualité, nuancé |

### 🆕 Modèle d'Analyse d'Images

| Modèle | Type | Vitesse | Avantages |
|--------|------|---------|-----------|
| **Image Caption (GIT)** | Vision + NLP | 2-15s | Détection contenu sensible, multilingue |

### 🆕 Générateur de Contenu YANSNET

| Modèle | Type | Vitesse | Usage |
|--------|------|---------|-------|
| **Content Generator** | LLM | 2-3s/post | Génération posts/commentaires pour démos |

### Performance par Catégorie

| Catégorie | Précision |
|-----------|-----------|
| Dépression claire | 80% |
| Normal clair | 100% |
| Textes courts | 40% |
| Cas ambigus | **80%** ⭐ |

---

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le projet
git clone <votre-repo>
cd ETSIA_ML_API

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

### Lancer l'API

```bash
# Mode développement
uvicorn app.main:app --reload --port 8000

# Mode production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Tester l'API

```bash
# Health check
curl http://localhost:8000/health

# Analyse de texte
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel so sad and hopeless"}'

# 🆕 Analyse d'image
curl -X POST http://localhost:8000/api/v1/predict-image \
  -F "image=@path/to/image.jpg"

# Documentation interactive
# Ouvrir http://localhost:8000/docs
```

---

## 📁 Structure du Projet

```
ETSIA_ML_API/
├── app/
│   ├── main.py                      # Point d'entrée FastAPI
│   ├── config.py                    # Configuration
│   │
│   ├── core/                        # ⭐ Infrastructure multi-modèles
│   │   ├── base_model.py           # Interface de base
│   │   └── model_registry.py       # Registre des modèles
│   │
│   ├── models/
│   │   └── schemas.py              # Schémas Pydantic
│   │
│   ├── services/                    # ⭐ Modèles de détection
│   │   ├── yansnet_llm/            # Modèle LLM (YANSNET)
│   │   │   ├── yansnet_llm_model.py
│   │   │   ├── llm_predictor.py
│   │   │   └── requirements.txt
│   │   │
│   │   ├── sensitive_image_caption/ # 🆕 Modèle analyse d'images
│   │   │   ├── sensitive_image_caption_model.py
│   │   │   ├── requirements.txt
│   │   │   └── README.md
│   │   │
│   │   ├── yansnet_content_generator/ # 🆕 Générateur de contenu
│   │   │   ├── yansnet_content_generator_model.py
│   │   │   ├── requirements.txt
│   │   │   └── README.md
│   │   │
│   │   └── [autres_modeles]/       # Modèles des autres étudiants
│   │
│   ├── routes/
│   │   └── api.py                  # Routes API (multi-modèles)
│   │
│   └── utils/
│       └── logger.py               # Logging
│
├── docs/
│   ├── API_CONTRACT.md             # Contrat d'API détaillé
│   ├── DATA_SOURCES.md             # Sources de données
│   ├── DEPLOYMENT.md               # Guide de déploiement
│   ├── CONTENT_GENERATION_GUIDE.md # 🆕 Guide génération de contenu
│   └── ADD_YOUR_MODEL.md           # ⭐ Guide pour ajouter un modèle
│
├── tests/
│   └── test_api.py                 # Tests unitaires
│
├── .env.example                    # Template variables d'environnement
├── requirements.txt                # Dépendances Python
└── README.md                       # Ce fichier
```

---

## 🔧 Configuration

### Variables d'Environnement

Créer un fichier `.env` :

```env
# LLM Provider (gpt, claude, local)
LLM_PROVIDER=gpt

# OpenAI (si provider=gpt)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic (si provider=claude)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Ollama (si provider=local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# API Configuration
API_TITLE=Depression Detection API
API_VERSION=1.0.0
LOG_LEVEL=INFO
```

### Configuration LLM Local (Ollama)

```bash
# Installer Ollama
# https://ollama.ai

# Télécharger le modèle
ollama pull llama3.2

# Lancer le serveur
ollama serve

# Tester
curl http://localhost:11434/api/tags
```

---

## 📖 Documentation API

### Endpoints Principaux

#### `GET /api/v1/models`
Liste tous les modèles disponibles.

**Response:**
```json
{
  "models": {
    "yansnet-llm": {
      "name": "yansnet-llm",
      "version": "1.0.0",
      "author": "Équipe YANSNET",
      "is_default": true
    }
  },
  "total": 1,
  "default": "yansnet-llm"
}
```

#### `POST /api/v1/predict`
Analyse un texte et détecte les signes de dépression.

**Request:**
```json
{
  "text": "I feel so sad and hopeless",
  "include_reasoning": true
}
```

**Query Parameters:**
- `model_name` (optionnel) : Nom du modèle à utiliser

**Response:**
```json
{
  "prediction": "DÉPRESSION",
  "confidence": 0.85,
  "severity": "Élevée",
  "reasoning": "Le texte exprime un désespoir profond et une tristesse intense...",
  "timestamp": "2025-01-16T10:30:00Z",
  "model_used": "yansnet-llm"
}
```

#### `POST /api/v1/batch-predict`
Analyse plusieurs textes en batch.

**Request:**
```json
{
  "texts": [
    "I'm so happy today",
    "I feel worthless and empty"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "I'm so happy today",
      "prediction": "NORMAL",
      "confidence": 0.95
    },
    {
      "text": "I feel worthless and empty",
      "prediction": "DÉPRESSION",
      "confidence": 0.88
    }
  ],
  "total_processed": 2,
  "processing_time": 1.2
}
```

#### 🆕 `POST /api/v1/predict-image`
Analyse une image et détecte le contenu sensible.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/predict-image \
  -F "image=@path/to/image.jpg"
```

**Response:**
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

**Détecte :**
- 🚫 Drogue et substances illégales
- 🔫 Violence et armes
- 🔞 Contenu sexuel
- 💣 Contenus problématiques

Voir [IMAGE_ANALYSIS_GUIDE.md](docs/IMAGE_ANALYSIS_GUIDE.md) pour la documentation complète.

#### 🆕 `POST /api/v1/content/generate-post`
Génère un post pour le forum étudiant YANSNET.

**Request:**
```json
{
  "post_type": "demande d'aide",
  "topic": "les partiels stressants",
  "sentiment": "négatif"
}
```

**Response:**
```json
{
  "content": "Bonjour à tous, je suis vraiment stressé par les partiels qui arrivent...",
  "post_type": "demande d'aide",
  "topic": "les partiels stressants",
  "sentiment": "négatif",
  "timestamp": "2025-01-16T10:30:00Z"
}
```

#### 🆕 `POST /api/v1/content/generate-post-with-comments`
Génère un post complet avec ses commentaires.

**Request:**
```json
{
  "post_type": "blague",
  "topic": "les fêtes étudiantes",
  "num_comments": 10
}
```

**Response:**
```json
{
  "post": {
    "content": "Vous savez ce qui est drôle ? Les fêtes étudiantes...",
    "post_type": "blague",
    "topic": "les fêtes étudiantes",
    "sentiment": "positif"
  },
  "comments": [
    {
      "content": "Haha trop vrai !",
      "sentiment": "positif",
      "comment_number": 1
    }
  ],
  "total_comments": 10
}
```

**Usage :**
- Peupler l'interface YANSNET pour les démos
- Tester les fonctionnalités du réseau social
- Prototyper l'UI sans vrais utilisateurs

Voir [CONTENT_GENERATION_GUIDE.md](docs/CONTENT_GENERATION_GUIDE.md) pour la documentation complète.

Voir [API_CONTRACT.md](docs/API_CONTRACT.md) pour la documentation complète.

---

## 📊 Sources de Données

### Datasets Utilisés pour Validation

1. **Combined Data** (53,043 textes)
   - 7 classes : Normal, Depression, Suicidal, Anxiety, Bipolar, Stress, Personality disorder
   - Source : Compilation de datasets publics Reddit/Twitter

2. **CLPsych Shared Task** (1,800 utilisateurs)
   - 3 conditions : Depression vs Control, PTSD vs Control, PTSD vs Depression
   - Source : CLPsych 2015 Shared Task

Voir [DATA_SOURCES.md](docs/DATA_SOURCES.md) pour plus de détails.

---

## 🎓 Ajouter Votre Propre Modèle

L'API utilise une **architecture multi-modèles** qui permet à chaque étudiant d'ajouter son propre modèle sans conflit.

### Étapes Rapides

1. **Créer votre dossier** : `app/services/votre_nom_modele/`
2. **Implémenter l'interface** : Hériter de `BaseDepressionModel`
3. **Enregistrer** : Ajouter dans `app/main.py`
4. **Tester** : `curl http://localhost:8000/api/v1/models`

Voir le guide complet : [docs/ADD_YOUR_MODEL.md](docs/ADD_YOUR_MODEL.md)

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=app --cov-report=html

# Test d'un endpoint spécifique
pytest tests/test_api.py::test_predict_endpoint -v
```

---

## 🔒 Workflow Git

La branche `main` est **protégée**. Workflow obligatoire :

1. Créer une branche : `git checkout -b feat/ma-feature`
2. Développer et commiter
3. Pousser : `git push origin feat/ma-feature`
4. Créer une Pull Request sur GitHub

**Voir [docs/GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) pour le guide complet.**

### Installation des hooks Git (optionnel)

```bash
# Activer la protection locale
git config core.hooksPath .githooks
```

---

## 🚢 Déploiement

### Docker

```bash
# Build
docker build -t depression-detection-api .

# Run
docker run -p 8000:8000 --env-file .env depression-detection-api
```

### Cloud (Render, Railway, etc.)

Voir [DEPLOYMENT.md](docs/DEPLOYMENT.md) pour les guides détaillés.

---

## ⚠️ Avertissement Important

**Ce système est à usage de RECHERCHE uniquement.**

- ❌ Ne remplace PAS un diagnostic médical professionnel
- ❌ Ne pas utiliser pour des décisions médicales
- ✅ Utiliser uniquement pour la recherche académique
- ✅ Toujours consulter un professionnel de santé

### Ressources d'Aide

Si vous ou quelqu'un que vous connaissez êtes en détresse :
- **France** : SOS Amitié (09 72 39 40 50), 3114 (prévention suicide)
- **International** : https://www.iasp.info/resources/Crisis_Centres/

---

## 📈 Performances et Coûts

### Latence
- GPT-4o-mini : ~300ms par requête
- Claude : ~300ms par requête
- Llama local : ~300ms par requête (dépend du hardware)

### Coûts (GPT-4o-mini)
- Input : $0.150 / 1M tokens (~$0.00001 par texte)
- Output : $0.600 / 1M tokens (~$0.00005 par texte)
- **Total : ~$0.00006 par prédiction** (négligeable)

### Recommandations
- **Production** : GPT-4o-mini (meilleur rapport qualité/prix)
- **Développement** : Llama local (gratuit, privé)
- **Haute qualité** : Claude (meilleure nuance)

---

## 🛠️ Technologies

- **Framework** : FastAPI 0.109.0
- **LLM** : OpenAI GPT-4o-mini / Anthropic Claude / Ollama Llama
- **Validation** : Pydantic 2.5.0
- **Logging** : Python logging + structlog
- **Tests** : Pytest 7.4.0

---

## 📝 Licence

Projet académique - X5 Semestre 9 ETSIA, 2025

---

## 👥 Auteurs

Équipe YANSNET - ETSIA

---

## 📧 Contact

Pour toute question sur ce projet académique, contactez l'équipe YANSNET.

---

**Dernière mise à jour** : Janvier 2025
