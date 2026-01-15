# 🚀 Guide de Déploiement Local - API ETSIA ML avec Docker

## 📋 Vue d'ensemble

Ce guide vous accompagne pas à pas pour déployer l'API ETSIA ML en local sur Windows avec Docker.

### Architecture du Projet

```
Services Docker:
├── ga4-bridge (port 5000)      → Monitoring et métriques
├── fastapi-app (port 8000)     → API de monitoring legacy
├── postgres (port 5432)        → Base de données métriques
├── redis (port 6379)           → Cache pour recommandations
├── ollama (port 11434)         → Serveur LLM local
└── api (port 8001)             → API ML principale (CPU) ⭐
```

### Modèles ML Disponibles

1. **CamemBERT** - Détection de dépression (français, rapide)
2. **Qwen 2.5 1.5B** - Détection de dépression (via Ollama)
3. **Llama 3.2 3B** - Génération de contenu (via Ollama)
4. **BLIP** - Analyse d'images sensibles (auto-téléchargé)
5. **Falconsai NSFW** - Détection contenu NSFW (auto-téléchargé)
6. **BERT HateComment** - Détection hate speech

---

## ✅ Étape 1 : Vérification des Prérequis

### 1.1 Docker Desktop

```powershell
# Vérifier que Docker est installé et lancé
docker --version
docker ps
```

**Résultat attendu :**
```
Docker version 29.1.3, build f52814d
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

✅ **Si Docker fonctionne, passez à l'étape suivante**

❌ **Si erreur :**
- Téléchargez Docker Desktop : https://www.docker.com/products/docker-desktop
- Lancez Docker Desktop
- Attendez que l'icône Docker soit verte dans la barre des tâches

### 1.2 Ressources Système Recommandées

- **RAM** : 12 GB minimum (16 GB recommandé)
- **Disque** : 20 GB d'espace libre
- **CPU** : 4 cœurs minimum

**Note :** Cette configuration utilise uniquement le CPU (pas de GPU requis).

---

## ⚙️ Étape 2 : Configuration du Fichier .env

Votre fichier `.env` existe déjà. Vérifions et ajustons la configuration :

### 2.1 Configuration Actuelle

```env
# Providers configurés
DETECTION_PROVIDER=qwen          # ✅ Qwen 2.5 1.5B via Ollama
GENERATION_PROVIDER=ollama       # ✅ Llama 3.2 3B

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
QWEN_DETECTION_MODEL=qwen2.5:1.5b
OLLAMA_GENERATION_MODEL=llama3.2:3b

# Monitoring (GA4-Bridge)
GA4_MEASUREMENT_ID=G-XXXXXXXXXX   # ⚠️ À configurer si monitoring souhaité
GA4_API_SECRET=your_api_secret_here
ENABLE_METRICS=true
```

### 2.2 Configuration Monitoring (Optionnel)

Si vous voulez activer le monitoring GA4 :

1. Créez une propriété Google Analytics 4
2. Récupérez votre `MEASUREMENT_ID` et `API_SECRET`
3. Mettez à jour le `.env`

**OU** désactivez le monitoring :

```env
ENABLE_METRICS=false
```

---

## 🐳 Étape 3 : Lancement des Services Docker

### 3.1 Build et Démarrage

```powershell
# Lancer tous les services (monitoring + ML)
docker-compose --profile ml up --build -d
```

**Explication des options :**
- `--profile ml` : Active les services ML (api, ollama, postgres, redis)
- `--build` : Reconstruit les images si nécessaire
- `-d` : Mode détaché (arrière-plan)

### 3.2 Surveillance des Logs

```powershell
# Voir les logs de tous les services
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f api
docker-compose logs -f ollama
docker-compose logs -f ga4-bridge
```

**Appuyez sur `Ctrl+C` pour arrêter la surveillance des logs**

### 3.3 Temps de Démarrage Attendus

| Service | Temps | Raison |
|---------|-------|--------|
| postgres | 10-20s | Base de données |
| redis | 5-10s | Cache |
| ga4-bridge | 20-30s | API monitoring |
| ollama | 30-60s | Serveur LLM |
| **api** | **5-10 min** | ⏳ Téléchargement modèles HuggingFace |

**⚠️ IMPORTANT :** Le premier démarrage de l'API prend 5-10 minutes car les modèles HuggingFace sont téléchargés automatiquement :
- CamemBERT (~500 MB)
- BLIP Image Captioning (~1 GB)
- Falconsai NSFW (~500 MB)
- Helsinki Translator (~300 MB)

---

## 📥 Étape 4 : Téléchargement des Modèles Ollama

Les modèles Ollama doivent être téléchargés **manuellement** après le démarrage.

### 4.1 Vérifier qu'Ollama est Prêt

```powershell
# Attendre que le container ollama soit "healthy"
docker ps | findstr ollama
```

**Résultat attendu :**
```
ollama-server   Up 2 minutes (healthy)
```

### 4.2 Télécharger les Modèles

```powershell
# Modèle 1 : Qwen 2.5 1.5B (détection de dépression)
docker exec ollama-server ollama pull qwen2.5:1.5b

# Modèle 2 : Llama 3.2 1B (fallback détection)
docker exec ollama-server ollama pull llama3.2:1b

# Modèle 3 : Llama 3.2 3B (génération de contenu)
docker exec ollama-server ollama pull llama3.2:3b
```

**Temps de téléchargement :**
- Qwen 2.5 1.5B : ~1 GB → 2-5 minutes
- Llama 3.2 1B : ~700 MB → 1-3 minutes
- Llama 3.2 3B : ~2 GB → 5-10 minutes

### 4.3 Vérifier les Modèles Installés

```powershell
docker exec ollama-server ollama list
```

**Résultat attendu :**
```
NAME                ID              SIZE      MODIFIED
qwen2.5:1.5b        xxx             1.0 GB    2 minutes ago
llama3.2:1b         xxx             700 MB    5 minutes ago
llama3.2:3b         xxx             2.0 GB    8 minutes ago
```

---

## 🧪 Étape 5 : Tests de l'API

### 5.1 Health Check Global

```powershell
curl http://localhost:8001/health
```

**Résultat attendu :**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "models": {
    "total": 7,
    "available": [
      "camembert-depression",
      "qwen-depression",
      "sensitive-image-caption",
      "yansnet-content-generator",
      "hatecomment-bert",
      "recommendation",
      "censure-nsfw"
    ]
  }
}
```

### 5.2 Test Détection de Dépression (CamemBERT)

```powershell
curl -X POST http://localhost:8001/api/v1/predict `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"Je me sens triste et sans espoir\"}'
```

### 5.3 Test Détection de Dépression (Qwen)

```powershell
curl -X POST "http://localhost:8001/api/v1/predict?model_name=qwen-depression" `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"Je me sens triste et sans espoir\"}'
```

### 5.4 Test Génération de Contenu

```powershell
curl -X POST http://localhost:8001/api/v1/content/generate-post `
  -H "Content-Type: application/json" `
  -d '{\"post_type\": \"blague\", \"topic\": \"les examens\", \"sentiment\": \"positif\"}'
```

### 5.5 Test Analyse d'Image

```powershell
# Remplacez "path/to/image.jpg" par le chemin de votre image
curl -X POST http://localhost:8001/api/v1/predict-image `
  -F "model_name=sensitive-image-caption" `
  -F "image=@path/to/image.jpg"
```

### 5.6 Test Détection NSFW

```powershell
curl -X POST http://localhost:8001/api/v1/censure/detect `
  -F "file=@path/to/image.jpg"
```

---

## 📊 Étape 6 : Accès aux Interfaces

### 6.1 Documentation Interactive (Swagger)

Ouvrez dans votre navigateur :
```
http://localhost:8001/docs
```

**Fonctionnalités :**
- Tester tous les endpoints
- Voir les schémas de requêtes/réponses
- Télécharger la spécification OpenAPI

### 6.2 Monitoring GA4-Bridge

```
http://localhost:5000/health
```

### 6.3 Base de Données PostgreSQL

```powershell
# Se connecter à PostgreSQL
docker exec -it etsia-postgres psql -U etsia -d etsia_metrics

# Voir les métriques
SELECT * FROM model_predictions ORDER BY created_at DESC LIMIT 10;

# Quitter
\q
```

### 6.4 Redis Cache

```powershell
# Se connecter à Redis
docker exec -it etsia-redis redis-cli

# Voir les clés
KEYS *

# Quitter
exit
```

---

## 🔧 Étape 7 : Résolution des Problèmes Courants

### 7.1 L'API ne démarre pas

**Symptôme :** Container `api` redémarre en boucle

```powershell
# Voir les logs d'erreur
docker-compose logs api | Select-String -Pattern "error" -Context 2
```

**Solutions courantes :**

1. **Manque de RAM**
   ```powershell
   # Augmenter la RAM allouée à Docker Desktop
   # Settings → Resources → Memory → 12 GB minimum
   ```

2. **Modèles HuggingFace non téléchargés**
   ```powershell
   # Attendre 5-10 minutes pour le premier démarrage
   docker-compose logs -f api
   ```

3. **Ollama non accessible**
   ```powershell
   # Vérifier qu'Ollama est healthy
   docker ps | findstr ollama
   
   # Redémarrer Ollama si nécessaire
   docker-compose restart ollama
   ```

### 7.2 Modèles Ollama non trouvés

**Symptôme :** Erreur "model not found" dans les logs

```powershell
# Vérifier les modèles installés
docker exec ollama-server ollama list

# Télécharger les modèles manquants
docker exec ollama-server ollama pull qwen2.5:1.5b
docker exec ollama-server ollama pull llama3.2:3b
```

### 7.3 Erreur de connexion PostgreSQL

**Symptôme :** "Connection refused" ou "database not ready"

```powershell
# Vérifier que PostgreSQL est healthy
docker ps | findstr postgres

# Redémarrer PostgreSQL
docker-compose restart postgres

# Attendre 10-20 secondes
timeout /t 20

# Redémarrer l'API
docker-compose restart api
```

### 7.4 Timeout lors des prédictions

**Symptôme :** Requêtes qui prennent trop de temps

**Solutions :**

1. **Utiliser CamemBERT au lieu de Qwen** (plus rapide)
   ```env
   # Dans .env
   DETECTION_PROVIDER=camembert
   ```

2. **Augmenter les timeouts**
   ```env
   MAX_DETECTION_LATENCY_MS=5000
   MAX_GENERATION_LATENCY_S=60
   ```

3. **Redémarrer l'API**
   ```powershell
   docker-compose restart api
   ```

### 7.5 Erreur "Out of Memory"

**Symptôme :** Container killed ou OOMKilled

```powershell
# Augmenter la limite mémoire dans docker-compose.yml
# Ou fermer d'autres applications
# Ou utiliser uniquement CamemBERT (plus léger)
```

---

## 🛑 Étape 8 : Arrêt et Nettoyage

### 8.1 Arrêter les Services

```powershell
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
docker-compose down -v
```

### 8.2 Redémarrer les Services

```powershell
# Redémarrer sans rebuild
docker-compose --profile ml up -d

# Redémarrer avec rebuild
docker-compose --profile ml up --build -d
```

### 8.3 Nettoyer Docker

```powershell
# Supprimer les images inutilisées
docker image prune -a

# Supprimer les volumes inutilisés
docker volume prune

# Nettoyer tout (⚠️ attention)
docker system prune -a --volumes
```

---

## 📈 Étape 9 : Monitoring et Métriques

### 9.1 Voir les Métriques en Temps Réel

```powershell
# Métriques de l'API
curl http://localhost:8001/api/v1/metrics/summary

# Métriques par modèle
curl http://localhost:8001/api/v1/metrics/models

# Alertes actives
curl http://localhost:8001/api/v1/metrics/alerts
```

### 9.2 Requêtes PostgreSQL Utiles

```sql
-- Statistiques des dernières 24h
SELECT * FROM v_model_stats_24h;

-- Taux d'erreur par modèle
SELECT * FROM v_error_rates_1h;

-- Alertes actives
SELECT * FROM v_active_alerts;

-- Latence moyenne par modèle
SELECT 
    model_name,
    AVG(latency_ms) as avg_latency,
    COUNT(*) as total_requests
FROM model_predictions
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY model_name;
```

---

## 🎯 Résumé des Commandes Essentielles

```powershell
# 1. Démarrer tout
docker-compose --profile ml up --build -d

# 2. Télécharger les modèles Ollama
docker exec ollama-server ollama pull qwen2.5:1.5b
docker exec ollama-server ollama pull llama3.2:3b

# 3. Vérifier le statut
docker ps
curl http://localhost:8001/health

# 4. Voir les logs
docker-compose logs -f api

# 5. Tester l'API
curl -X POST http://localhost:8001/api/v1/predict `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"Je me sens triste\"}'

# 6. Arrêter tout
docker-compose down
```

---

## 📚 Ressources Supplémentaires

- **Documentation API** : http://localhost:8001/docs
- **Guide développeur** : `docs/GUIDE_DEVELOPPEUR.md`
- **Contrat API** : `docs/API_CONTRACT.md`
- **Ajout de modèles** : `docs/ADD_YOUR_MODEL.md`

---

## ✅ Checklist de Déploiement

- [ ] Docker Desktop installé et lancé
- [ ] Fichier `.env` configuré
- [ ] Services Docker démarrés (`docker-compose up`)
- [ ] Modèles Ollama téléchargés (qwen2.5:1.5b, llama3.2:3b)
- [ ] Health check réussi (`/health`)
- [ ] Tests des endpoints principaux
- [ ] Documentation accessible (`/docs`)

---

**🎉 Félicitations ! Votre API ETSIA ML est déployée et opérationnelle !**
