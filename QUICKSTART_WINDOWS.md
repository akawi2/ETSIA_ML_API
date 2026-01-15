# 🚀 Guide de Démarrage Rapide - Windows

## Prérequis

- ✅ Docker Desktop installé et lancé
- ✅ PowerShell 5.1+ (inclus dans Windows 10/11)
- ✅ 12 GB RAM minimum
- ✅ 20 GB espace disque libre

## Démarrage en 3 Commandes

### 1. Configuration (première fois uniquement)

```powershell
# Copier le fichier de configuration
Copy-Item .env.example .env

# Éditer .env et configurer vos clés API (optionnel)
notepad .env
```

### 2. Déploiement Complet

```powershell
# Déploiement automatique (15-20 minutes)
.\deploy.ps1
```

### 3. Tests

```powershell
# Tester tous les endpoints
.\test_api.ps1
```

## Options de Déploiement

```powershell
# Déploiement rapide (sans rebuild)
.\deploy.ps1 -SkipBuild

# Déploiement sans télécharger les modèles Ollama
.\deploy.ps1 -SkipModels

# Déploiement sans tests
.\deploy.ps1 -SkipTests

# Nettoyage complet avant déploiement
.\deploy.ps1 -Clean

# Combinaison d'options
.\deploy.ps1 -SkipBuild -SkipTests
```

## Services Disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **API ML** | http://localhost:8001 | API principale avec tous les modèles |
| **Documentation** | http://localhost:8001/docs | Documentation interactive Swagger |
| **GA4-Bridge** | http://localhost:5000 | Service de monitoring |
| **Ollama** | http://localhost:11434 | Serveur LLM local |

## Commandes Utiles

### Gestion des Services

```powershell
# Voir le status
docker-compose ps

# Voir les logs
docker-compose logs -f api

# Redémarrer l'API
docker-compose restart api

# Arrêter tous les services
docker-compose --profile ml down

# Arrêter et supprimer les volumes
docker-compose --profile ml down -v
```

### Monitoring

```powershell
# Logs en temps réel
docker-compose logs -f api

# Logs des 100 dernières lignes
docker-compose logs --tail=100 api

# Logs de tous les services
docker-compose logs -f
```

### Modèles Ollama

```powershell
# Lister les modèles installés
docker exec ollama-server ollama list

# Télécharger un nouveau modèle
docker exec ollama-server ollama pull llama3.2:3b

# Supprimer un modèle
docker exec ollama-server ollama rm llama3.2:1b
```

## Tests Rapides

### Health Check

```powershell
curl http://localhost:8001/health
```

### Prédiction de Dépression

```powershell
$body = @{
    text = "Je me sens triste et sans espoir"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### Génération de Contenu

```powershell
$body = @{
    post_type = "blague"
    topic = "les examens"
    sentiment = "positif"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/content/generate-post" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## Résolution de Problèmes

### Docker Desktop n'est pas lancé

```powershell
# Vérifier si Docker est lancé
docker ps

# Si erreur, lancez Docker Desktop et attendez qu'il soit prêt
```

### L'API ne démarre pas

```powershell
# Voir les logs d'erreur
docker-compose logs api

# Vérifier la mémoire disponible
docker stats

# Redémarrer l'API
docker-compose restart api
```

### Les modèles ne se téléchargent pas

```powershell
# Vérifier qu'Ollama est lancé
docker-compose ps ollama

# Télécharger manuellement
docker exec ollama-server ollama pull qwen2.5:1.5b
docker exec ollama-server ollama pull llama3.2:3b
```

### Erreur de mémoire

```powershell
# Augmenter la mémoire allouée à Docker Desktop
# Settings > Resources > Memory > 12 GB minimum

# Ou utiliser uniquement les modèles légers
docker exec ollama-server ollama pull llama3.2:1b
```

### Port déjà utilisé

```powershell
# Trouver le processus utilisant le port 8001
netstat -ano | findstr :8001

# Arrêter le processus (remplacer PID)
taskkill /PID <PID> /F

# Ou modifier le port dans docker-compose.yml
# ports:
#   - "8080:8000"  # Utiliser un autre port
```

## Configuration Avancée

### Changer le Provider de Détection

Éditez `.env`:

```env
# Utiliser CamemBERT (rapide, CPU)
DETECTION_PROVIDER=camembert

# Utiliser Qwen (meilleur raisonnement, plus lent)
DETECTION_PROVIDER=qwen

# Utiliser XLM-RoBERTa (multilingue)
DETECTION_PROVIDER=xlm-roberta
```

### Changer le Provider de Génération

```env
# Utiliser Ollama (local, gratuit)
GENERATION_PROVIDER=ollama
OLLAMA_GENERATION_MODEL=llama3.2:3b

# Utiliser OpenAI (meilleur qualité, payant)
GENERATION_PROVIDER=gpt
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Utiliser Claude (excellent qualité, payant)
GENERATION_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Activer le Cache Redis

```env
ENABLE_CACHE=true
REDIS_CACHE_TTL=3600  # 1 heure
```

### Désactiver les Métriques

```env
ENABLE_METRICS=false
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ETSIA ML API                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  CamemBERT   │  │  HateBERT    │  │  NSFW Model  │    │
│  │  (Dépression)│  │  (Hate)      │  │  (Images)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Qwen 2.5    │  │  Llama 3.2   │  │  Recommender │    │
│  │  (Détection) │  │  (Génération)│  │  (GCN)       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure                           │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis  │  Ollama  │  GA4-Bridge            │
│  (Métriques) │ (Cache) │  (LLM)   │  (Monitoring)          │
└─────────────────────────────────────────────────────────────┘
```

## Performances Attendues (CPU)

| Modèle | Latence | Mémoire |
|--------|---------|---------|
| CamemBERT | 600-700ms | 1 GB |
| Qwen 2.5 1.5B | 2-3s | 2 GB |
| Llama 3.2 3B | 2-5s | 3 GB |
| HateBERT | 400-600ms | 800 MB |
| NSFW Model | 500-800ms | 1 GB |

**Note:** Cette configuration utilise uniquement le CPU. Pour des performances optimales avec GPU, consultez la documentation de déploiement avancé.

## Support

- 📚 Documentation complète: `GUIDE_DEPLOIEMENT_LOCAL.md`
- 🔧 Guide développeur: `docs/GUIDE_DEVELOPPEUR.md`
- 📋 Contrat API: `docs/API_CONTRACT.md`
- 🐛 Issues: Créez une issue sur le repo

## Prochaines Étapes

1. ✅ Déployer l'API avec `.\deploy.ps1`
2. ✅ Tester avec `.\test_api.ps1`
3. 📚 Lire la documentation: http://localhost:8001/docs
4. 🔧 Configurer vos providers dans `.env`
5. 🚀 Intégrer l'API dans votre application

Bon développement ! 🎉
