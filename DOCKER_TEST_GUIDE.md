# Guide de Test Docker Complet - ETSIA ML API

## Prérequis

- Docker Desktop installé
- Git installé
- **15GB d'espace disque minimum** (modèles HuggingFace + Ollama)
- **16GB RAM recommandé** (8GB minimum)

## Modèles Disponibles

| Service | Modèle | Tâche | RAM |
|---------|--------|-------|-----|
| `camembert_depression` | CamemBERT | Détection dépression (FR) | 500MB |
| `qwen_depression` | Qwen 2.5 1.5B | Détection dépression (raisonnement) | 2.5GB |
| `hatecomment_bert` | BERT | Détection commentaires haineux | 500MB |
| `sensitive_image_caption` | BLIP | Analyse images sensibles | 1GB |
| `yansnet_llm` | GPT/Claude/Ollama | LLM généraliste | Variable |
| `yansnet_content_generator` | Llama 3.2 | Génération contenu | 5GB |

---

## Installation Rapide

### 1. Cloner le projet

```bash
git clone <votre-repo-url>
cd ETSIA_ML_API
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
```

**Éditer `.env` selon le provider souhaité :**

```env
# === DETECTION DE DEPRESSION ===
# Options: camembert, qwen, xlm-roberta
DETECTION_PROVIDER=qwen

# === QWEN (si DETECTION_PROVIDER=qwen) ===
QWEN_DETECTION_MODEL=qwen2.5:1.5b
OLLAMA_BASE_URL=http://ollama:11434

# === CAMEMBERT (si DETECTION_PROVIDER=camembert) ===
CAMEMBERT_MODEL=camembert-base
CAMEMBERT_DEVICE=cpu

# === GENERATION DE CONTENU ===
GENERATION_PROVIDER=ollama
OLLAMA_GENERATION_MODEL=llama3.2:3b

# === LLM EXTERNE (optionnel) ===
# OPENAI_API_KEY=sk-xxx
# ANTHROPIC_API_KEY=sk-ant-xxx
```

### 3. Démarrer Docker

```bash
docker-compose up -d
docker-compose ps
```

### 4. Télécharger les modèles Ollama

```bash
# Windows
scripts\setup_ollama_models.bat

# Linux/Mac
chmod +x scripts/setup_ollama_models.sh
./scripts/setup_ollama_models.sh
```

**Ou manuellement :**
```bash
docker exec ollama-server ollama pull qwen2.5:1.5b
docker exec ollama-server ollama pull llama3.2:3b
docker exec ollama-server ollama pull llama3.2:1b
```

### 5. Vérifier le démarrage

```bash
# Health check global
curl http://localhost:8000/health

# Liste des modèles chargés
curl http://localhost:8000/api/v1/models
```

---

## Tests par Service

### 1. Détection de Dépression (CamemBERT ou Qwen)

```bash
# Health check
curl http://localhost:8000/api/v1/depression/health

# Health check tous les modèles
curl http://localhost:8000/api/v1/depression/health/all

# Test détection simple
curl -X POST http://localhost:8000/api/v1/depression/detect \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Je me sens triste et sans énergie depuis plusieurs semaines.",
    "include_reasoning": true
  }'

# Test batch
curl -X POST http://localhost:8000/api/v1/depression/batch-detect \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Je suis heureux aujourd hui!",
      "Tout me semble vide et sans sens.",
      "J ai passé une bonne journée."
    ],
    "include_reasoning": false
  }'

# Infos du modèle
curl http://localhost:8000/api/v1/depression/info
```

### 2. Détection Commentaires Haineux

```bash
# Test détection hate speech
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "hatecomment-bert",
    "text": "Tu es vraiment nul et stupide!"
  }'
```

### 3. Analyse Images Sensibles

```bash
# Test avec URL d'image
curl -X POST http://localhost:8000/api/v1/image/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg"
  }'

# Test avec fichier local (multipart)
curl -X POST http://localhost:8000/api/v1/image/analyze \
  -F "file=@/chemin/vers/image.jpg"
```

### 4. Génération de Contenu (Llama)

```bash
# Générer un post
curl -X POST http://localhost:8000/api/v1/content/generate-post \
  -H "Content-Type: application/json" \
  -d '{
    "post_type": "confession",
    "topic": "relations amoureuses"
  }'

# Générer un commentaire
curl -X POST http://localhost:8000/api/v1/content/generate-comment \
  -H "Content-Type: application/json" \
  -d '{
    "post_content": "Je me sens seul ces derniers temps...",
    "tone": "supportive"
  }'
```

### 5. LLM Généraliste (YANSNET)

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "yansnet-llm",
    "text": "Analyse ce texte pour détecter des signes de dépression: Je me sens vide."
  }'
```

---

## Script de Test Automatisé

Créer un fichier `test_all.sh` :

```bash
#!/bin/bash
echo "=== TEST COMPLET ETSIA ML API ==="

BASE_URL="http://localhost:8000"

echo ""
echo "1. Health Check Global..."
curl -s $BASE_URL/health | jq .

echo ""
echo "2. Liste des modèles..."
curl -s $BASE_URL/api/v1/models | jq .

echo ""
echo "3. Test Détection Dépression..."
curl -s -X POST $BASE_URL/api/v1/depression/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Je me sens triste", "include_reasoning": true}' | jq .

echo ""
echo "4. Test Batch Dépression..."
curl -s -X POST $BASE_URL/api/v1/depression/batch-detect \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Heureux!", "Triste..."], "include_reasoning": false}' | jq .

echo ""
echo "5. Health All Depression Models..."
curl -s $BASE_URL/api/v1/depression/health/all | jq .

echo ""
echo "=== TESTS TERMINÉS ==="
```

**Windows (PowerShell) :**
```powershell
# test_all.ps1
$BASE_URL = "http://localhost:8000"

Write-Host "=== TEST COMPLET ETSIA ML API ===" -ForegroundColor Green

Write-Host "`n1. Health Check Global..."
Invoke-RestMethod -Uri "$BASE_URL/health" | ConvertTo-Json

Write-Host "`n2. Liste des modèles..."
Invoke-RestMethod -Uri "$BASE_URL/api/v1/models" | ConvertTo-Json

Write-Host "`n3. Test Détection Dépression..."
$body = @{text="Je me sens triste"; include_reasoning=$true} | ConvertTo-Json
Invoke-RestMethod -Uri "$BASE_URL/api/v1/depression/detect" -Method Post -Body $body -ContentType "application/json" | ConvertTo-Json

Write-Host "`n=== TESTS TERMINÉS ===" -ForegroundColor Green
```

---

## Changer de Provider de Détection

### Passer de CamemBERT à Qwen

```bash
# 1. Modifier .env
# DETECTION_PROVIDER=qwen

# 2. Redémarrer l'API
docker-compose restart api

# 3. Vérifier
curl http://localhost:8000/api/v1/depression/health
```

### Passer de Qwen à CamemBERT

```bash
# 1. Modifier .env
# DETECTION_PROVIDER=camembert

# 2. Redémarrer l'API
docker-compose restart api
```

---

## Commandes Docker Utiles

```bash
# Logs en temps réel
docker-compose logs -f

# Logs API seulement
docker-compose logs -f api

# Logs Ollama seulement
docker-compose logs -f ollama

# Redémarrer un service
docker-compose restart api

# Reconstruire l'image API
docker-compose build api
docker-compose up -d api

# Stats ressources
docker stats

# Shell dans le container API
docker exec -it depression-api bash

# Shell dans Ollama
docker exec -it ollama-server sh

# Lister modèles Ollama
docker exec ollama-server ollama list

# Arrêter tout
docker-compose down

# Reset complet (supprime volumes)
docker-compose down -v
```

---

## Dépannage

### API ne démarre pas
```bash
docker-compose logs api
# Vérifier les erreurs d'import ou de configuration
```

### Ollama non accessible
```bash
# Vérifier que le container tourne
docker-compose ps

# Tester Ollama directement
curl http://localhost:11434/api/tags

# Dans le container API, utiliser http://ollama:11434
```

### Modèle HuggingFace non trouvé
```bash
# Les modèles se téléchargent au premier démarrage
# Vérifier les logs pour le téléchargement
docker-compose logs -f api | grep -i "download\|loading"
```

### Mémoire insuffisante
```bash
# Vérifier l'utilisation
docker stats

# Augmenter RAM Docker Desktop
# Settings > Resources > Memory: 12GB+
```

### Timeout Qwen
```bash
# Qwen peut être lent au premier appel (chargement)
# Attendre 30-60s après le démarrage
```

---

## URLs de Référence

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Documentation Swagger |
| http://localhost:8000/redoc | Documentation ReDoc |
| http://localhost:8000/health | Health check global |
| http://localhost:8000/api/v1/models | Liste des modèles |
| http://localhost:8000/api/v1/depression/detect | Détection dépression |
| http://localhost:8000/api/v1/depression/health/all | Health tous modèles |
| http://localhost:11434/api/tags | Modèles Ollama |
