# 🚀 Guide Développeur - ETSIA ML API

Guide complet pour cloner, configurer, lancer et tester le projet.

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Lancement](#lancement)
6. [Tests](#tests)
7. [Architecture](#architecture)
8. [Développement](#développement)
9. [Déploiement](#déploiement)
10. [Dépannage](#dépannage)

---

## 🎯 Vue d'Ensemble

**ETSIA ML API** est une API REST multi-modèles pour :
- 📝 **Détection de dépression** dans les textes (CamemBERT, Qwen, LLM)
- 💬 **Détection de hate speech** (BERT fine-tuné)
- 🖼️ **Analyse de contenu sensible** dans les images (Vision + NLP)
- 📊 **Système de recommandation** de posts
- ✍️ **Génération de contenu** pour le réseau social YANSNET



**Technologies :**
- FastAPI 0.109.0
- PyTorch + Transformers
- PostgreSQL (métriques)
- Redis (cache)
- GA4-Bridge (monitoring centralisé)
- Google Analytics 4 (dashboard)
- Docker + Docker Compose

---

## 🔧 Prérequis

### Logiciels Requis

| Logiciel | Version | Installation |
|----------|---------|--------------|
| **Python** | 3.8+ | [python.org](https://www.python.org/) |
| **Git** | 2.0+ | [git-scm.com](https://git-scm.com/) |
| **Docker** (optionnel) | 20.0+ | [docker.com](https://www.docker.com/) |
| **PostgreSQL** (recommandé) | 14+ | [postgresql.org](https://www.postgresql.org/) |
| **Redis** (recommandé) | 7+ | [redis.io](https://redis.io/) |

### Clés API (au moins une)

- **OpenAI** : [platform.openai.com](https://platform.openai.com/)
- **Anthropic** : [console.anthropic.com](https://console.anthropic.com/)
- **Ollama** (gratuit) : [ollama.ai](https://ollama.ai/)

---

## 📥 Installation

### 1. Cloner le Projet

```bash
# Cloner le dépôt
git clone https://github.com/votre-organisation/ETSIA_ML_API.git
cd ETSIA_ML_API
```

### 2. Créer un Environnement Virtuel

#### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les Dépendances

```bash
# Dépendances principales
pip install -r requirements.txt

# Dépendances pour le modèle HateComment (optionnel)
pip install -r app/services/hatecomment_bert/requirements.txt
```

**Temps d'installation :** 5-10 minutes

---

## ⚙️ Configuration

### 1. Créer le Fichier `.env`

```bash
# Copier le template
cp .env.example .env
```

### 2. Configurer les Providers

Éditez `.env` avec vos clés API :

#### Option A : OpenAI (Recommandé)

```env
# Provider de détection
DETECTION_PROVIDER=camembert

# Provider de génération
GENERATION_PROVIDER=gpt

# OpenAI
OPENAI_API_KEY=sk-votre-cle-openai
OPENAI_MODEL=gpt-4o-mini
```

#### Option B : Ollama (Gratuit, Local)

```bash
# 1. Installer Ollama
# Windows: Télécharger depuis https://ollama.ai
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. Télécharger les modèles
ollama pull llama3.2:1b
ollama pull llama3.2:3b
ollama pull qwen2.5:1.5b

# 3. Lancer le serveur
ollama serve
```

```env
# Provider de détection
DETECTION_PROVIDER=qwen

# Provider de génération
GENERATION_PROVIDER=ollama

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DETECTION_MODEL=qwen2.5:1.5b
OLLAMA_GENERATION_MODEL=llama3.2:3b
```

#### Option C : Anthropic Claude

```env
# Provider de génération
GENERATION_PROVIDER=claude

# Anthropic
ANTHROPIC_API_KEY=sk-ant-votre-cle-anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### 3. Configuration PostgreSQL (Requis)

PostgreSQL est requis pour :
- **Métriques et monitoring** : API de métriques (`/api/v1/metrics/*`)
- **Système de recommandation** : Stockage des posts et interactions utilisateurs

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=etsia
POSTGRES_PASSWORD=etsia_secure_password
POSTGRES_DB=etsia_metrics
ENABLE_METRICS=true
```

**Note :** Sans PostgreSQL, l'API de métriques et le système de recommandation ne fonctionneront pas. Seul le monitoring via GA4-Bridge reste disponible.

### 4. Configuration Redis (Requis pour les recommandations)

Redis est requis pour le système de recommandation (cache des posts) :

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_TTL=3600
ENABLE_CACHE=true
```

**Note :** Sans Redis, le système de recommandation fonctionnera en mode dégradé (sans cache, performances réduites).

### 5. Configuration Monitoring (Optionnel)

Pour activer le monitoring centralisé avec GA4-Bridge :

```env
# Monitoring
ENABLE_METRICS=true
BRIDGE_URL=http://ga4-bridge:5000/log_metric
CLIENT_ID=yansnet_ml_api_v1

# Google Analytics 4 (requis pour GA4-Bridge)
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=your_api_secret
```

**Fonctionnalités :**
- ✅ Envoi automatique des métriques (latence, confidence, etc.)
- ✅ Évaluation des alertes en temps réel
- ✅ Dashboard Google Analytics 4
- ✅ Non-bloquant (timeout 0.5s)

**Note :** Avec Docker Compose, le `BRIDGE_URL` est automatiquement configuré pour pointer vers le service `ga4-bridge`. L'API attend que GA4-Bridge soit démarré avant de lancer.

---

## 🚀 Lancement

### Méthode 1 : Script de Démarrage Rapide (Recommandé)

#### Windows
```cmd
start.bat
```

#### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

Le script :
- ✅ Vérifie Python
- ✅ Crée l'environnement virtuel
- ✅ Installe les dépendances
- ✅ Vérifie le fichier `.env`
- ✅ Lance l'API

### Méthode 2 : Lancement Manuel

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Lancer l'API
uvicorn app.main:app --reload --port 8000
```

### Méthode 3 : Docker Compose (Production)

```bash
# Lancer tous les services (API + PostgreSQL + Redis + Ollama + GA4-Bridge)
docker-compose up -d

# Attendre le démarrage complet (environ 2 minutes pour l'API)
docker-compose logs -f api

# Voir les logs du monitoring
docker-compose logs -f ga4-bridge

# Arrêter
docker-compose down
```

### Vérification

L'API est prête quand vous voyez :

```
✓ API démarrée avec succès!
📚 Documentation: http://localhost:8000/docs
📋 Modèles disponibles: http://localhost:8000/api/v1/models
```

**URLs importantes :**
- API : http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs
- Documentation ReDoc : http://localhost:8000/redoc
- Health Check : http://localhost:8000/health

---

## 🧪 Tests

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-01-11T...",
  "models": {
    "total": 7,
    "available": [
      "yansnet-llm",
      "camembert-depression",
      "sensitive-image-caption",
      "yansnet-content-generator",
      "hatecomment-bert",
      "recommendation-system",
      "censure-nsfw"
    ]
  }
}
```

### 2. Lister les Modèles

```bash
curl http://localhost:8000/api/v1/models
```

### 3. Test de Détection de Dépression

```bash
curl -X POST http://localhost:8000/api/v1/depression/detect \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Je me sens triste et sans espoir\", \"include_reasoning\": true}"
```

**Réponse attendue :**
```json
{
  "prediction": "DÉPRESSION",
  "confidence": 0.85,
  "severity": "Élevée",
  "reasoning": "Le texte exprime un désespoir profond...",
  "timestamp": "2026-01-11T...",
  "model_used": "camembert-depression"
}
```

### 4. Test de Détection de Hate Speech

```bash
curl -X POST http://localhost:8000/api/v1/hatecomment/detect \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Je déteste ce groupe de personnes\"}"
```

### 5. Test d'Analyse d'Image

```bash
curl -X POST http://localhost:8000/api/v1/predict-image \
  -F "model_name=sensitive-image-caption" \
  -F "image=@chemin/vers/image.jpg"
```

### 6. Test de Génération de Contenu

```bash
curl -X POST http://localhost:8000/api/v1/content/generate-post \
  -H "Content-Type: application/json" \
  -d "{\"post_type\": \"demande d'aide\", \"topic\": \"les partiels stressants\", \"sentiment\": \"négatif\"}"
```

### 7. Test de Recommandation

```bash
curl "http://localhost:8000/recommend?userId=1"
```

### 8. Test de l'API de Métriques

```bash
# Health check du système de métriques
curl http://localhost:8000/api/v1/metrics/health

# Résumé des métriques (dernières 24h)
curl http://localhost:8000/api/v1/metrics/summary

# Statistiques par modèle
curl http://localhost:8000/api/v1/metrics/models

# Latence d'un modèle spécifique
curl http://localhost:8000/api/v1/metrics/models/camembert-depression/latency

# Erreurs récentes
curl http://localhost:8000/api/v1/metrics/errors

# Alertes actives
curl http://localhost:8000/api/v1/metrics/alerts

# Métriques au format Prometheus
curl http://localhost:8000/api/v1/metrics/prometheus
```

**Note :** Ces endpoints nécessitent PostgreSQL configuré.

### 9. Test de Détection NSFW

```bash
# Test avec une image (upload de fichier)
curl -X POST http://localhost:8000/api/v1/censure/detect \
  -F "file=@chemin/vers/image.jpg"

# Health check du modèle NSFW
curl http://localhost:8000/api/v1/censure/health

# Informations sur le modèle
curl http://localhost:8000/api/v1/censure/info

# Exemples d'utilisation
curl http://localhost:8000/api/v1/censure/examples
```

**Réponse attendue :**
```json
{
  "prediction": "SAFE",
  "confidence": 0.95,
  "severity": "Aucune",
  "is_nsfw": false,
  "reasoning": "✅ Contenu sûr - Aucun élément NSFW détecté",
  "categories": {
    "General Content": {
      "Safe": 95.0,
      "Violation": 5.0,
      "Prediction": "Safe"
    }
  },
  "processing_time": 0.45
}
```

**Note :** Cet endpoint utilise `multipart/form-data` avec le paramètre `file` (pas `image`).

### 10. Test du Système de Monitoring

#### Démonstration Interactive

```bash
# Démonstration interactive du monitoring (recommandé pour découvrir le système)
python scripts/demo_monitoring.py
```

**Ce script offre :**
- 🎨 Interface colorée et interactive
- 📊 Visualisation en temps réel des métriques
- 🔔 Démonstration des alertes
- 🤖 Test de tous les modèles ML (Depression, Hate Speech, Recommendation, NSFW)
- 📈 Explication du flux de monitoring complet

#### Tests Automatisés

```bash
# Test complet de l'intégration monitoring
python scripts/test_monitoring_integration.py
```

**Ce script teste :**
- ✅ Health check du GA4-Bridge (port 5000)
- ✅ Health check de l'API principale (port 8001)
- ✅ Émission directe de métriques au Bridge
- ✅ Détection de dépression avec monitoring automatique (CamemBERT et Qwen)
- ✅ Détection de hate speech avec monitoring automatique
- ✅ Déclenchement d'alertes (métriques hors seuil)

**Exemple de sortie :**
```
======================================================================
TEST 1: Health Check du GA4-Bridge
======================================================================
✓ Bridge Status: 200
  Response: {'status': 'healthy', 'service': 'ga4-bridge'}

======================================================================
TEST 4: Détection de dépression (avec monitoring)
======================================================================
✓ Prediction Status: 200
  Latency: 450.23ms
  Prediction: DÉPRESSION
  Confidence: 0.85
  Severity: Élevée
  Model: camembert-depression

  Note: Les métriques ont été envoyées automatiquement au Bridge

======================================================================
RÉSUMÉ DES TESTS
======================================================================
✓ PASS: Bridge Health
✓ PASS: API Health
✓ PASS: Direct Metric
✓ PASS: Depression Detection
✓ PASS: Hate Comment Detection
✓ PASS: Alert Triggering

Résultat: 6/6 tests réussis

🎉 Tous les tests sont passés! Le monitoring est opérationnel.
```

**Prérequis :**
- API principale lancée sur le port 8001
- GA4-Bridge lancé sur le port 5000
- Variables d'environnement configurées

### 9. Tests Automatisés

```bash
# Lancer tous les tests
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=app --cov-report=html

# Test d'un fichier spécifique
pytest tests/test_api.py -v

# Test d'une fonction spécifique
pytest tests/test_api.py::test_predict_endpoint -v

# Tests unitaires du client de monitoring
pytest tests/test_monitoring_client.py -v
```

**Temps d'exécution :** 30 secondes - 2 minutes

### 11. Test de Tous les Modèles ML

```bash
# Test automatique des 7 modèles avec monitoring
python scripts/test_all_models.py
```

**Ce script teste :**
- ✅ Health check global de l'API
- ✅ Détection de dépression (Qwen 2.5)
- ✅ Détection de hate speech (BERT)
- ✅ Génération de contenu
- ✅ Caption d'images
- ✅ Système de recommandation
- ✅ Détection NSFW (ShieldGemma)
- ✅ Health check du GA4-Bridge
- ✅ Envoi de métriques au Bridge

**Exemple de sortie :**
```
======================================================================
TEST 7: Détection NSFW (ShieldGemma)
======================================================================

Test: Image blanche (contenu sûr attendu)...
  Prédiction: SÛR
  Confiance: 0.9500
  Sévérité: Aucune
  NSFW: False
  Raisonnement: ✅ Contenu sûr - Aucun élément sensible détecté
  Latence: 0.45s

  Catégories analysées:
    - Dangerous Content: Safe (score: 0.0%)
    - Harassment: Safe (score: 0.0%)
    - Hate Speech: Safe (score: 0.0%)
    - Sexually Explicit: Safe (score: 0.0%)

======================================================================
✓ TOUS LES TESTS TERMINÉS AVEC SUCCÈS
======================================================================

Résumé:
  - 7 modèles testés
  - Monitoring GA4-Bridge opérationnel
  - Système de cache Redis fonctionnel
  - Prêt pour déploiement Docker Hub
```

**Temps d'exécution :** 1-2 minutes

### 12. Test Docker Complet

```bash
# Test complet de l'environnement Docker
python scripts/test_docker_complete.py
```

**Ce script teste :**
- ✅ Health checks (API ML + GA4-Bridge)
- ✅ Modèles ML (Depression, Hate Speech, Recommendation)
- ✅ Système de monitoring (métriques + alertes)
- ✅ Cache Redis (stats)
- ✅ Requêtes concurrentes (10 requêtes simultanées)

**Exemple de sortie :**
```
============================================================
  TESTS DOCKER COMPLETS - ETSIA ML API
============================================================

=== TEST 1: Health Checks ===
✓ API ML Health Check
  → 7 modèles chargés
✓ GA4-Bridge Health Check
  → 40 règles d'alerte

=== TEST 2: Modèles ML ===
✓ Depression Detection
  → DÉPRESSION (0.45s)
✓ Hate Speech Detection
  → HAINEUX (0.123s)
✓ Recommendation System
  → 5 recommandations

=== TEST 3: Monitoring ===
✓ Métrique normale
  → Alerts: False
✓ Alerte déclenchée
  → Latency > 1000ms détectée

=== TEST 4: Cache Redis ===
✓ Cache Stats
  → Enabled: True

=== TEST 5: Requêtes Concurrentes ===
✓ Requêtes Concurrentes
  → 10/10 réussies

============================================================
  RÉSUMÉ
============================================================

Tests réussis: 10/10
Taux de réussite: 100.0%
Status: EXCELLENT
```

**Prérequis :**
- Tous les services Docker lancés (`docker-compose up -d`)
- API accessible sur le port 8001
- GA4-Bridge accessible sur le port 5000

**Temps d'exécution :** 30-60 secondes

---

## 🏗️ Architecture

### Structure du Projet

```
ETSIA_ML_API/
├── app/                          # Code source de l'API
│   ├── main.py                   # Point d'entrée FastAPI
│   ├── config.py                 # Configuration globale
│   │
│   ├── core/                     # Infrastructure
│   │   ├── base_model.py         # Interface de base pour modèles
│   │   ├── model_registry.py     # Registre des modèles
│   │   └── metrics/              # Système de métriques
│   │       ├── monitoring_client.py # Client GA4-Bridge
│   │       ├── metrics_service.py   # Service de métriques
│   │       └── metrics_models.py    # Modèles de données
│   │
│   ├── models/                   # Schémas Pydantic
│   │   └── schemas.py
│   │
│   ├── routes/                   # Routes API
│   │   ├── api.py                # Routes génériques
│   │   ├── depression_api.py     # Routes dépression
│   │   ├── hatecomment_api.py    # Routes hate speech
│   │   ├── image_api.py          # Routes images
│   │   ├── recommendation_api.py # Routes recommandations
│   │   ├── censure_api.py        # Routes NSFW
│   │   └── metrics_api.py        # Routes métriques
│   │
│   ├── services/                 # Modèles ML
│   │   ├── yansnet_llm/          # Modèle LLM (génération)
│   │   ├── camembert_depression/ # Détection dépression (BERT)
│   │   ├── qwen_depression/      # Détection dépression (Qwen)
│   │   ├── hatecomment_bert/     # Détection hate speech
│   │   ├── sensitive_image_caption/ # Analyse images
│   │   ├── yansnet_content_generator/ # Génération contenu
│   │   ├── recommendation/       # Système recommandation
│   │   └── model_censure/        # Détection NSFW
│   │
│   └── utils/                    # Utilitaires
│       └── logger.py             # Logging
│
├── docs/                         # Documentation
│   ├── GUIDE_DEVELOPPEUR.md      # Ce fichier
│   ├── API_CONTRACT.md           # Contrat d'API
│   ├── ADD_YOUR_MODEL.md         # Guide ajout modèle
│   ├── DEPLOYMENT.md             # Guide déploiement
│   └── ...
│
├── tests/                        # Tests unitaires
│   ├── test_api.py
│   ├── test_hatecomment_bert.py
│   ├── test_monitoring_client.py  # Tests du client de monitoring
│   └── ...
│
├── scripts/                      # Scripts utilitaires
│   ├── setup_ollama_models.sh    # Setup Ollama
│   ├── init_db.sql               # Init PostgreSQL
│   ├── demo_monitoring.py        # Démo interactive du monitoring
│   ├── test_monitoring_integration.py  # Test monitoring complet
│   └── ...
│
├── .env.example                  # Template configuration
├── requirements.txt              # Dépendances Python
├── docker-compose.yml            # Configuration Docker
├── Dockerfile                    # Image Docker
├── pytest.ini                    # Configuration tests
├── start.sh / start.bat          # Scripts de démarrage
└── README.md                     # Documentation principale
```

### Architecture Multi-Modèles

L'API utilise un **registre de modèles** qui permet :
- ✅ Ajouter des modèles sans conflit
- ✅ Sélectionner le modèle via query parameter
- ✅ Fallback automatique si un modèle échoue
- ✅ Health check de tous les modèles

**Exemple :**
```python
# Enregistrer un modèle
from app.core.model_registry import registry
registry.register(MonModele())

# Utiliser un modèle spécifique
GET /api/v1/predict?model_name=mon-modele
```

### Architecture de Monitoring

L'API intègre un **système de monitoring centralisé** via GA4-Bridge :

**Flux de données :**
```
ML API → MonitoringService → GA4-Bridge → Google Analytics 4
         (async, 0.5s timeout)   (évaluation alertes)   (dashboard)
```

**Fonctionnalités :**
- ✅ Émission automatique des métriques (latence, confidence, etc.)
- ✅ Évaluation des alertes en temps réel
- ✅ Non-bloquant (ne ralentit pas l'API)
- ✅ Helper functions pour chaque service

**Exemple d'utilisation :**
```python
from app.core.monitoring import emit_depression_metric

# Dans votre endpoint
await emit_depression_metric(
    model_name="camembert-depression",
    latency_ms=450,
    confidence=0.85,
    severity="Élevée",
    prediction="DÉPRESSION"
)
```

**Services supportés :**
- `depression_detection` - Détection de dépression
- `hate_comment` - Détection de hate speech
- `image_captioning` - Analyse d'images
- `content_generation` - Génération de contenu
- `api_gateway` - Métriques API globales

### Providers Hybrides

L'API utilise différents providers selon la tâche :

| Tâche | Provider Recommandé | Alternatives |
|-------|---------------------|--------------|
| **Détection dépression** | CamemBERT (600ms) | Qwen 2.5 1.5B, XLM-RoBERTa |
| **Génération contenu** | Ollama Llama 3.2 3B | GPT-4o-mini, Claude |
| **Hate speech** | BERT fine-tuné | - |
| **Analyse images** | GIT (Vision) | - |
| **NSFW** | Modèle spécialisé | - |

---

## 💻 Développement

### Workflow Git

La branche `main` est **protégée**. Workflow obligatoire :

```bash
# 1. Créer une branche de feature
git checkout -b feat/ma-feature

# 2. Développer et commiter
git add .
git commit -m "feat: description de la feature"

# 3. Pousser
git push origin feat/ma-feature

# 4. Créer une Pull Request sur GitHub
# feat/ma-feature → develop → main
```

**Voir [GIT_WORKFLOW.md](GIT_WORKFLOW.md) pour le guide complet.**

### Ajouter un Nouveau Modèle

```bash
# 1. Créer le dossier
mkdir app/services/mon_modele

# 2. Créer les fichiers
touch app/services/mon_modele/__init__.py
touch app/services/mon_modele/mon_modele_model.py
touch app/services/mon_modele/requirements.txt

# 3. Implémenter l'interface BaseMLModel
# Voir app/core/base_model.py

# 4. Enregistrer dans app/main.py
# registry.register(MonModele())

# 5. Tester
pytest tests/test_mon_modele.py
```

**Voir [ADD_YOUR_MODEL.md](ADD_YOUR_MODEL.md) pour le guide complet.**

---

## 🚢 Déploiement

### Déploiement Local (Production)

```bash
# Avec Gunicorn + Uvicorn
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Déploiement Docker

```bash
# Build
docker build -t etsia-ml-api:latest .

# Run
docker run -d \
  --name etsia-ml-api \
  -p 8000:8000 \
  --env-file .env \
  etsia-ml-api:latest
```

### Déploiement Docker Compose

```bash
# Lancer tous les services (monitoring + ML)
docker-compose --profile ml up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

**Services déployés :**
- API ML (CPU-based, port 8001)
- PostgreSQL (métriques)
- Redis (cache)
- Ollama (LLM local)
- GA4-Bridge (monitoring)

**Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour les guides détaillés.**

---

## 🐛 Dépannage

### Problème : L'API ne démarre pas

**Solution :**
```bash
# Vérifier l'environnement virtuel
which python  # Doit pointer vers venv/

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Problème : Erreur LLM "Invalid API key"

**Solution :**
```bash
# Vérifier le fichier .env
cat .env | grep OPENAI_API_KEY

# Tester la clé directement
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Problème : Ollama "Connection refused"

**Solution :**
```bash
# Vérifier qu'Ollama est lancé
curl http://localhost:11434/api/tags

# Si non, lancer Ollama
ollama serve

# Vérifier les modèles téléchargés
ollama list
```

### Problème : Monitoring ne fonctionne pas

**Solution :**
```bash
# Vérifier que GA4-Bridge est lancé
curl http://localhost:5000/health

# Vérifier les variables d'environnement
cat .env | grep ENABLE_METRICS
cat .env | grep BRIDGE_URL

# Vérifier les logs de l'API
docker-compose logs -f api

# Tester l'intégration complète
python scripts/test_monitoring_integration.py

# Désactiver temporairement le monitoring
ENABLE_METRICS=false
```

### Problème : Tests de monitoring échouent

**Solution :**
```bash
# Vérifier que les services sont lancés sur les bons ports
curl http://localhost:8001/health  # API principale
curl http://localhost:5000/health  # GA4-Bridge

# Vérifier les logs pour les erreurs
docker-compose logs -f api
docker-compose logs -f ga4-bridge

# Relancer les services
docker-compose restart api ga4-bridge

# Attendre quelques secondes puis relancer les tests
python scripts/test_monitoring_integration.py
```

---

## 📚 Ressources Supplémentaires

### Documentation

- [README.md](../README.md) - Documentation principale
- [API_CONTRACT.md](API_CONTRACT.md) - Contrat d'API détaillé
- [ADD_YOUR_MODEL.md](ADD_YOUR_MODEL.md) - Guide ajout de modèle
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guide de déploiement
- [GIT_WORKFLOW.md](GIT_WORKFLOW.md) - Workflow Git
- [METRICS_SYSTEM.md](METRICS_SYSTEM.md) - Système de monitoring
- [QUICKSTART.md](../QUICKSTART.md) - Démarrage rapide

### APIs Externes

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Anthropic API](https://docs.anthropic.com/)
- [Ollama Documentation](https://ollama.ai/docs/)

---

## 📞 Support

### Problèmes et Questions

- **Issues GitHub** : Créer une issue sur le dépôt
- **Documentation** : Consulter les docs dans `docs/`
- **Exemples** : Voir les tests dans `tests/`

---

## 📝 Licence

Projet académique - X5 Semestre 9 ETSIA, 2026

---

## 👥 Auteurs

Équipe YANSNET - ETSIA

---

**Dernière mise à jour** : 11 janvier 2026
**Version** : 2.0.0

---

## ✅ Checklist de Démarrage

- [ ] Python 3.8+ installé
- [ ] Git installé
- [ ] Projet cloné
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées
- [ ] Fichier `.env` créé et configuré
- [ ] Au moins un provider LLM configuré
- [ ] API lancée
- [ ] Health check réussi
- [ ] Documentation accessible
- [ ] Tests passent
- [ ] Test de monitoring réussi (si activé)

**Si tous les points sont cochés, vous êtes prêt à développer ! 🎉**
