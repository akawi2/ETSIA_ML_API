# 🐳 Guide Docker pour Windows - ETSIA ML API

## 🎯 **Système Unifié**

Le projet utilise maintenant **un seul Dockerfile** intelligent qui s'adapte automatiquement au CPU ou GPU selon vos besoins.

## 🚀 **Déploiement Rapide**

### **Option 1: CPU (Recommandé pour débuter)**
```powershell
.\docker-deploy.ps1 cpu
```
- **Port**: 8000
- **URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs

### **Option 2: GPU (Performance maximale)**
```powershell
.\docker-deploy.ps1 gpu
```
- **Port**: 8001  
- **URL**: http://localhost:8001
- **Documentation**: http://localhost:8001/docs
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

## 📚 **Ressources**

- **Documentation API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Modèles disponibles**: http://localhost:8000/api/v1/models
- **Logs**: `.\docker-deploy.ps1 logs`

---

**🎉 Votre API ETSIA ML est maintenant optimisée pour Windows avec un système Docker unifié !**
