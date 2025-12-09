# Configuration Ollama avec Docker

Ce guide explique comment configurer et utiliser Ollama via Docker pour les modèles Qwen 2.5 1.5B et Llama 3.2.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────────┐ │
│  │   API Container  │────────▶│  Ollama Container    │ │
│  │   (FastAPI)      │         │  (qwen2.5:1.5b)      │ │
│  │                  │         │  (llama3.2:3b)       │ │
│  │  Port: 8000      │         │  (llama3.2:1b)       │ │
│  └──────────────────┘         │                      │ │
│                                │  Port: 11434         │ │
│                                └──────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Prérequis

- Docker Desktop installé
- Docker Compose installé
- Au moins 8GB de RAM disponible
- 10GB d'espace disque pour les modèles

## Installation

### 1. Démarrer les services

```bash
# Démarrer Ollama et l'API
docker-compose up -d

# Vérifier que les services sont démarrés
docker-compose ps
```

### 2. Télécharger les modèles

**Linux/Mac:**
```bash
chmod +x scripts/setup_ollama_models.sh
./scripts/setup_ollama_models.sh
```

**Windows:**
```cmd
scripts\setup_ollama_models.bat
```

**Ou manuellement:**
```bash
# Qwen 2.5 1.5B (détection de dépression)
docker exec ollama-server ollama pull qwen2.5:1.5b

# Llama 3.2 3B (génération de contenu)
docker exec ollama-server ollama pull llama3.2:3b

# Llama 3.2 1B (fallback)
docker exec ollama-server ollama pull llama3.2:1b
```

### 3. Vérifier l'installation

```bash
# Lister les modèles installés
docker exec ollama-server ollama list

# Tester Ollama directement
curl http://localhost:11434/api/tags
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` basé sur `.env.example`:

```bash
# Pour utiliser Qwen pour la détection
DETECTION_PROVIDER=qwen
QWEN_DETECTION_MODEL=qwen2.5:1.5b
OLLAMA_BASE_URL=http://ollama:11434

# Pour utiliser Llama pour la génération
GENERATION_PROVIDER=ollama
OLLAMA_GENERATION_MODEL=llama3.2:3b
```

### Choix du modèle de détection

Vous avez 3 options:

1. **CamemBERT** (Recommandé pour latence ultra-faible)
   ```bash
   DETECTION_PROVIDER=camembert
   ```
   - Latence: 20-50ms
   - RAM: 500MB
   - Meilleur pour: Production avec contraintes de latence strictes

2. **Qwen 2.5 1.5B** (Recommandé pour meilleur raisonnement)
   ```bash
   DETECTION_PROVIDER=qwen
   ```
   - Latence: 200-500ms
   - RAM: 2-3GB
   - Meilleur pour: Meilleure précision et explications détaillées

3. **XLM-RoBERTa** (Multilingue)
   ```bash
   DETECTION_PROVIDER=xlm-roberta
   ```
   - Latence: 30-60ms
   - RAM: 600MB
   - Meilleur pour: Support multilingue (100 langues)

## Utilisation

### Tester Qwen directement

```bash
# Test simple
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:1.5b",
  "prompt": "Analyse ce texte pour détecter des signes de dépression: Je me sens triste et sans énergie.",
  "stream": false
}'
```

### Via l'API FastAPI

```bash
# Détection de dépression
curl -X POST http://localhost:8000/api/v1/depression/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Je me sens triste et sans énergie depuis plusieurs semaines."}'
```

## Gestion des modèles

### Lister les modèles

```bash
docker exec ollama-server ollama list
```

### Supprimer un modèle

```bash
docker exec ollama-server ollama rm qwen2.5:1.5b
```

### Mettre à jour un modèle

```bash
docker exec ollama-server ollama pull qwen2.5:1.5b
```

## Performance

### Benchmarks attendus (CPU)

| Modèle | Tâche | Latence (p50) | RAM | Throughput |
|--------|-------|---------------|-----|------------|
| Qwen 2.5 1.5B | Détection | 300ms | 2.5GB | 3 req/s |
| Llama 3.2 3B | Génération | 8s | 5GB | 0.1 req/s |
| Llama 3.2 1B | Fallback | 2s | 2GB | 0.5 req/s |

### Optimisation

Pour améliorer les performances:

1. **Augmenter la RAM allouée à Docker**
   - Docker Desktop → Settings → Resources → Memory: 8GB+

2. **Utiliser un SSD**
   - Les modèles se chargent plus rapidement depuis un SSD

3. **GPU (optionnel)**
   - Décommenter la section GPU dans `docker-compose.yml`
   - Installer NVIDIA Container Toolkit
   - Latence divisée par 5-10x

## Dépannage

### Ollama ne démarre pas

```bash
# Vérifier les logs
docker logs ollama-server

# Redémarrer le service
docker-compose restart ollama
```

### Modèles non trouvés

```bash
# Vérifier que les modèles sont téléchargés
docker exec ollama-server ollama list

# Re-télécharger si nécessaire
docker exec ollama-server ollama pull qwen2.5:1.5b
```

### Erreur de connexion depuis l'API

Vérifiez que `OLLAMA_BASE_URL` pointe vers le bon service:
- **Depuis l'hôte**: `http://localhost:11434`
- **Depuis un container Docker**: `http://ollama:11434`

### Mémoire insuffisante

```bash
# Vérifier l'utilisation mémoire
docker stats

# Augmenter la limite dans docker-compose.yml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
```

## Arrêt et nettoyage

```bash
# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ supprime les modèles téléchargés)
docker-compose down -v

# Supprimer uniquement les containers
docker-compose rm -f
```

## Support GPU (Optionnel)

Pour utiliser un GPU NVIDIA:

1. Installer NVIDIA Container Toolkit
2. Décommenter la section GPU dans `docker-compose.yml`
3. Redémarrer les services

```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Ressources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Qwen 2.5 Model Card](https://ollama.com/library/qwen2.5)
- [Llama 3.2 Model Card](https://ollama.com/library/llama3.2)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
