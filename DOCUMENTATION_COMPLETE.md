# Documentation Complète - ETSIA ML API

## 📋 Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture](#architecture)
3. [Déploiement](#déploiement)
4. [Modèles ML](#modèles-ml)
5. [Système de Monitoring](#système-de-monitoring)
6. [Tests](#tests)
7. [Résolution de Problèmes](#résolution-de-problèmes)

---

## 🎯 Vue d'ensemble

ETSIA ML API est une plateforme complète de Machine Learning avec 7 modèles intégrés et un système de monitoring à deux niveaux (temps réel + historique).

### Modèles Disponibles
1. **qwen-depression** - Détection de dépression (Qwen LLM)
2. **yansnet-llm** - Détection de dépression (LLM configurable)
3. **hatecomment-bert** - Détection de discours haineux (BERT multilingue)
4. **recommendation-system** - Recommandations de posts (filtrage collaboratif)
5. **nsfw-detection** - Détection de contenu NSFW (Falconsai CLIP)
6. **sensitive-image-caption** - Détection de contenu sensible dans images (BLIP)
7. **yansnet-content-generator** - Génération de contenu pour forum étudiant

### Services
- **API ML** (port 8001) - 7 modèles ML + endpoints REST
- **PostgreSQL** (port 5432) - Base de données pour métriques
- **Redis** (port 6379) - Cache pour recommandations
- **Ollama** (port 11434) - Serveur LLM local
- **GA4-Bridge** (port 5000) - Monitoring temps réel + alertes

---

## 🏗️ Architecture

### Stack Technique
- **Python 3.11** - Langage principal
- **FastAPI** - Framework web
- **Docker & Docker Compose** - Containerisation
- **PostgreSQL** - Métriques historiques
- **Redis** - Cache
- **Ollama** - LLM local (llama3.2:3b, qwen2.5:1.5b)

### Double Système de Monitoring

#### 1. GA4-Bridge (Temps Réel)
- Évaluation des seuils d'alerte
- Alertes instantanées
- Envoi vers Google Analytics 4
- Configuration: `metrics_catalog.json`

#### 2. PostgreSQL (Historique)
- Métriques détaillées par modèle
- Statistiques agrégées (P50, P95, P99)
- Analyse de performance
- Endpoints: `/api/v1/metrics/models`

---

## 🚀 Déploiement

### Prérequis
- Docker Desktop installé
- 16 GB RAM minimum
- 20 GB espace disque

### Déploiement Rapide

```powershell
# 1. Cloner le projet
git clone <repo-url>
cd ETSIA_ML_API

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés API

# 3. Déployer avec le script automatique
.\deploy.ps1
```

### Déploiement Manuel

```powershell
# Build et démarrage
docker-compose --profile ml up --build -d

# Vérifier les logs
docker logs etsia-ml-api-cpu -f

# Attendre 30-60s pour le chargement des modèles
```

### Vérification du Déploiement

```powershell
# Health check global
curl http://localhost:8001/health

# Test d'un modèle
curl -X POST "http://localhost:8001/api/v1/depression/detect" `
  -H "Content-Type: application/json" `
  -d '{"text":"Je me sens triste"}'
```

---

## 🤖 Modèles ML

### 1. Détection de Dépression

**qwen-depression** (Recommandé)
```bash
POST /api/v1/depression/detect
{
  "text": "Je me sens désespéré",
  "include_reasoning": true
}
```

**yansnet-llm** (Legacy)
```bash
POST /api/v1/predict_depression
{
  "text": "Je suis fatigué",
  "include_reasoning": true
}
```

### 2. Détection de Discours Haineux

```bash
POST /api/v1/hatecomment/detect
{
  "text": "Je déteste ce commentaire",
  "include_reasoning": true
}
```

### 3. Système de Recommandation

```bash
POST /api/v1/recommend
{
  "user_id": 1,
  "top_n": 10,
  "available_posts": [1, 2, 3, 4, 5]
}
```

### 4. Détection NSFW

```bash
POST /api/v1/censure/detect
Content-Type: multipart/form-data
file: <image.jpg>
```

### 5. Détection de Contenu Sensible

```bash
POST /api/v1/predict-image
Content-Type: multipart/form-data
model_name: sensitive-image-caption
image: <image.jpg>
```

### 6. Génération de Contenu

```bash
POST /api/v1/content/generate-post
{
  "post_type": "confession",
  "topic": "les partiels stressants",
  "sentiment": "négatif"
}
```

---

## 📊 Système de Monitoring

### Métriques Disponibles

#### Par Modèle
```bash
GET /api/v1/metrics/models?model_name=qwen-depression
```

**Réponse:**
```json
{
  "model_name": "qwen-depression",
  "total_requests": 127,
  "avg_latency_ms": 4176.56,
  "p50_latency_ms": 3613.66,
  "p95_latency_ms": 5667.64,
  "p99_latency_ms": 5770.99,
  "avg_confidence": 0.9,
  "error_rate": 0.0,
  "depression_count": 100,
  "normal_count": 27
}
```

#### Globales
```bash
GET /api/v1/metrics/summary
```

### Alertes (GA4-Bridge)

Configuration dans `metrics_catalog.json`:

```json
{
  "service": "depression_detection",
  "metric": "latency",
  "threshold": 3500,
  "operator": ">",
  "priority": "high",
  "description": "Latence élevée détection dépression"
}
```

### Scripts de Monitoring

```powershell
# Monitoring continu
.\monitor.ps1

# Vérification des métriques
.\test_final_metrics.ps1
```

---

## 🧪 Tests

### Tests Automatiques

```powershell
# Test complet de tous les modèles
.\test_api.ps1

# Test des modèles d'images
.\test_image_metrics.ps1

# Vérification des métriques BDD
.\test_final_metrics.ps1
```

### Tests Manuels

```powershell
# 1. Créer un fichier de test
echo '{"text":"Je me sens triste"}' > test.json

# 2. Tester un endpoint
curl -X POST "http://localhost:8001/api/v1/depression/detect" `
  -H "Content-Type: application/json" `
  -d "@test.json"

# 3. Vérifier les métriques
curl "http://localhost:8001/api/v1/metrics/models?model_name=qwen-depression"
```

### Tests d'Images

```powershell
# Test NSFW
curl -X POST "http://localhost:8001/api/v1/censure/detect" `
  -F "file=@test_image.jpg"

# Test Caption
curl -X POST "http://localhost:8001/api/v1/predict-image" `
  -F "model_name=sensitive-image-caption" `
  -F "image=@test_image.jpg"
```

---

## 🔧 Résolution de Problèmes

### Problème: Modèles ne se chargent pas

**Symptômes:**
- Health check retourne "unhealthy"
- Erreurs dans les logs

**Solutions:**
```powershell
# 1. Vérifier les logs
docker logs etsia-ml-api-cpu --tail 100

# 2. Vérifier la mémoire
docker stats etsia-ml-api-cpu

# 3. Redémarrer le container
docker-compose --profile ml restart api

# 4. Rebuild si nécessaire
docker-compose --profile ml build api
docker-compose --profile ml up -d --force-recreate api
```

### Problème: Ollama 404

**Symptômes:**
- Erreur "Model not found" pour yansnet-llm

**Solution:**
```powershell
# Vérifier la variable OLLAMA_MODEL dans .env
# Doit inclure le tag de version
OLLAMA_MODEL=llama3.2:3b  # ✅ Correct
OLLAMA_MODEL=llama3.2     # ❌ Incorrect

# Recréer le container
docker-compose --profile ml up -d --force-recreate api
```

### Problème: Métriques non enregistrées

**Symptômes:**
- Endpoint `/api/v1/metrics/models` retourne vide

**Vérification:**
```powershell
# 1. Tester un modèle
curl -X POST "http://localhost:8001/api/v1/depression/detect" `
  -H "Content-Type: application/json" `
  -d '{"text":"test"}'

# 2. Attendre 2-3 secondes

# 3. Vérifier les métriques
curl "http://localhost:8001/api/v1/metrics/models?model_name=qwen-depression"
```

**Solution:**
- Tous les modèles utilisent maintenant `record_prediction_async()`
- Si le problème persiste, vérifier les logs PostgreSQL

### Problème: Latence élevée

**Symptômes:**
- Temps de réponse > 5 secondes

**Solutions:**
1. **Vérifier les seuils d'alerte** dans `metrics_catalog.json`
2. **Optimiser les modèles:**
   - Utiliser qwen-depression au lieu de yansnet-llm (plus rapide)
   - Activer le cache Redis pour les recommandations
3. **Augmenter les ressources Docker:**
   ```yaml
   # docker-compose.yml
   services:
     api:
       deploy:
         resources:
           limits:
             memory: 8G
   ```

### Problème: Erreurs GPU

**Symptômes:**
- Erreurs CUDA dans les logs

**Solution:**
```powershell
# Supprimer la configuration GPU (non nécessaire sur Windows)
# Dans docker-compose.yml, commenter:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
```

---

## 📚 Documentation Additionnelle

- **QUICKSTART.md** - Guide de démarrage rapide
- **QUICKSTART_WINDOWS.md** - Guide spécifique Windows
- **GUIDE_DEPLOIEMENT_LOCAL.md** - Déploiement détaillé
- **GUIDE_TEST_COMPLET.md** - Guide de tests complets
- **ANALYSE_MONITORING.md** - Analyse du système de monitoring
- **ANALYSE_ENREGISTREMENT_METRIQUES_BDD.md** - Détails techniques métriques

---

## 🎯 Commandes Rapides

```powershell
# Déploiement
.\deploy.ps1

# Monitoring
.\monitor.ps1

# Tests
.\test_api.ps1
.\test_final_metrics.ps1

# Logs
docker logs etsia-ml-api-cpu -f

# Redémarrage
docker-compose --profile ml restart api

# Rebuild complet
docker-compose --profile ml down
docker-compose --profile ml up --build -d

# Nettoyage
docker-compose --profile ml down -v
docker system prune -a
```

---

## 📞 Support

Pour toute question ou problème:
1. Consulter cette documentation
2. Vérifier les logs: `docker logs etsia-ml-api-cpu`
3. Consulter les guides spécifiques dans `/docs`

---

**Version:** 1.0.0  
**Dernière mise à jour:** 15 janvier 2026  
**Statut:** ✅ Production Ready
