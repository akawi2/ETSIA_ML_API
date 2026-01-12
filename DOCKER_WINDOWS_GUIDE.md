# 🐳 Guide Docker pour Windows - ETSIA ML API

## 🎯 **Système Unifié**

Le projet utilise maintenant **un seul Dockerfile** intelligent qui s'adapte automatiquement au CPU ou GPU selon vos besoins, avec **PostgreSQL** pour les métriques et **Ollama** pour les modèles LLM.

## 🏗️ **Architecture des Services**

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  PostgreSQL  │  │    Ollama    │  │   API (FastAPI)  │  │
│  │  (Métriques) │  │  (LLM/Qwen)  │  │   CPU ou GPU     │  │
│  │  Port: 5432  │  │  Port: 11434 │  │   Port: 8000     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Déploiement Rapide**

### **Option 1: Docker Compose (Recommandé)**
```powershell
# Démarrer tous les services (PostgreSQL + Ollama + API)
docker-compose up -d

# Télécharger les modèles Ollama
.\scripts\setup_ollama_models.bat
```

### **Option 2: Script PowerShell - CPU**
```powershell
.\docker-deploy.ps1 cpu
```
- **Port API**: 8000
- **Port PostgreSQL**: 5432
- **Port Ollama**: 11434
- **URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

### **Option 3: Script PowerShell - GPU**
```powershell
.\docker-deploy.ps1 gpu
```
- **Port API**: 8001  
- **URL**: http://localhost:8001
- **Prérequis**: NVIDIA GPU + Docker GPU support

## 🛠️ **Commandes Disponibles**

### **Déploiement**
```powershell
# CPU uniquement (défaut)
.\docker-deploy.ps1 cpu

# GPU avec CUDA
.\docker-deploy.ps1 gpu
```

### **Gestion**
```powershell
# Arrêter tous les services
.\docker-deploy.ps1 stop

# Voir les logs en temps réel
.\docker-deploy.ps1 logs

# Vérifier la santé de l'API
.\docker-deploy.ps1 health

# Nettoyage complet
.\docker-deploy.ps1 clean

# Aide
.\docker-deploy.ps1 help
```

## 🔧 **Architecture Technique**

### **Dockerfile Unifié**
```dockerfile
# Utilise une image de base variable
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

# S'adapte automatiquement à CPU ou GPU
```

### **Images Générées**
- **CPU**: `etsia-ml-api:cpu` (basée sur python:3.11-slim)
- **GPU**: `etsia-ml-api:gpu` (basée sur nvidia/cuda:12.1-runtime)

### **Conteneurs Créés**
- **CPU**: `etsia-ml-api-cpu` sur port 8000
- **GPU**: `etsia-ml-api-gpu` sur port 8001

## 🎯 **Avantages du Nouveau Système**

### ✅ **Simplicité**
- **1 seul Dockerfile** au lieu de 2
- **1 seul script** PowerShell optimisé pour Windows
- **Détection automatique** des capacités

### ✅ **Flexibilité**
- **Basculement facile** entre CPU et GPU
- **Coexistence possible** des deux modes
- **Configuration par variables d'environnement**

### ✅ **Maintenance**
- **Code unifié** plus facile à maintenir
- **Moins de duplication**
- **Évolution centralisée**

## 🔍 **Vérification du Déploiement**

### **Test Automatique**
Le script vérifie automatiquement la santé après déploiement :
```
✅ API CPU: Healthy
✅ API GPU: Healthy
```

### **Test Manuel**
```powershell
# Tester l'endpoint de santé
curl http://localhost:8000/health

# Tester une prédiction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Je me sens triste"}'
```

## 🚨 **Prérequis GPU**

Pour utiliser le mode GPU, assurez-vous d'avoir :

1. **GPU NVIDIA** compatible CUDA
2. **Pilotes NVIDIA** récents
3. **NVIDIA Docker Runtime** installé
4. **Docker Desktop** avec support GPU activé

### **Installation NVIDIA Docker (Windows)**
```powershell
# Installer NVIDIA Container Toolkit
# Suivre: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

## 📊 **Comparaison des Performances**

| Mode | Modèles Supportés | Performance | Mémoire |
|------|------------------|-------------|---------|
| CPU  | Tous | Standard | ~2GB |
| GPU  | Tous + Accélération | 3-10x plus rapide | ~4-8GB |

## 🔧 **Dépannage**

### **Erreur "Docker non installé"**
```powershell
# Installer Docker Desktop pour Windows
# https://docs.docker.com/desktop/windows/install/
```

### **Erreur GPU non disponible**
```powershell
# Vérifier le support GPU
docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi
```

### **Port déjà utilisé**
```powershell
# Arrêter les services existants
.\docker-deploy.ps1 stop

# Ou changer le port dans le script
```

## 🗄️ **Services Docker**

### **PostgreSQL (Métriques)**
```yaml
# Stockage des métriques de performance
Container: etsia-postgres
Port: 5432
Database: etsia_metrics
User: etsia
```

**Accès à la base de données:**
```powershell
# Via Docker
docker exec -it etsia-postgres psql -U etsia -d etsia_metrics

# Requêtes utiles
SELECT * FROM v_model_stats_24h;  # Stats 24h
SELECT * FROM v_active_alerts;     # Alertes actives
```

### **Ollama (LLM)**
```yaml
# Modèles LLM locaux
Container: ollama-server
Port: 11434
Modèles: qwen2.5:1.5b, llama3.2:3b, llama3.2:1b
```

**Gestion des modèles:**
```powershell
# Lister les modèles
docker exec ollama-server ollama list

# Télécharger un modèle
docker exec ollama-server ollama pull qwen2.5:1.5b

# Tester un modèle
docker exec ollama-server ollama run qwen2.5:1.5b "Bonjour"
```

## 📊 **Endpoints de Métriques**

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/metrics/health` | Health check PostgreSQL |
| `GET /api/v1/metrics/summary` | Résumé global des métriques |
| `GET /api/v1/metrics/models` | Statistiques par modèle |
| `GET /api/v1/metrics/errors` | Erreurs récentes |
| `GET /api/v1/metrics/alerts` | Alertes actives |
| `GET /api/v1/metrics/prometheus` | Format Prometheus |

## 📚 **Ressources**

- **Documentation API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Modèles disponibles**: http://localhost:8000/api/v1/models
- **Métriques**: http://localhost:8000/api/v1/metrics/summary
- **Détection dépression**: http://localhost:8000/api/v1/depression/detect
- **Logs**: `docker-compose logs -f`

## 🔧 **Variables d'Environnement**

Créez un fichier `.env` basé sur `.env.example`:

```bash
# Provider de détection (camembert, qwen, xlm-roberta)
DETECTION_PROVIDER=qwen

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=etsia
POSTGRES_PASSWORD=etsia_secure_password
POSTGRES_DB=etsia_metrics

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
QWEN_DETECTION_MODEL=qwen2.5:1.5b

# Monitoring
ENABLE_METRICS=true
LOG_LATENCY=true
```

---

**🎉 Votre API ETSIA ML est maintenant optimisée pour Windows avec PostgreSQL, Ollama et un système Docker unifié !**
