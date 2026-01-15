# 🧪 Guide de Test Complet - ETSIA ML API

## 📋 Table des Matières

1. [Accès à la Documentation Interactive](#documentation-interactive)
2. [Tests par Endpoint](#tests-par-endpoint)
3. [Monitoring des Performances](#monitoring-performances)
4. [Analyse des Logs](#analyse-logs)
5. [Résolution des Erreurs](#resolution-erreurs)

---

## 🌐 Documentation Interactive

### Accès Swagger UI

Ouvrez dans votre navigateur : **http://localhost:8001/docs**

Cette interface vous permet de :
- ✅ Voir tous les endpoints disponibles
- ✅ Tester chaque endpoint directement
- ✅ Voir les schémas de requête/réponse
- ✅ Obtenir des exemples de code

---

## 🎯 Tests par Endpoint

### 1. Health Check & Status

#### GET /health
**Description**: Vérifie l'état de l'API et de tous les modèles

**Test dans Swagger**:
1. Cliquez sur `GET /health`
2. Cliquez sur "Try it out"
3. Cliquez sur "Execute"

**Test PowerShell**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get | ConvertTo-Json -Depth 5
```

**Résultat attendu**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "models": {
    "total": 7,
    "available": ["yansnet-llm", "qwen-depression", ...]
  }
}
```

---

#### GET /api/v1/models
**Description**: Liste tous les modèles disponibles

**Test dans Swagger**:
1. Cliquez sur `GET /api/v1/models`
2. "Try it out" → "Execute"

**Test PowerShell**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/models" -Method Get | ConvertTo-Json -Depth 3
```

---

### 2. Détection de Dépression

#### POST /api/v1/predict
**Description**: Détecte les signes de dépression dans un texte

**Test dans Swagger**:
1. Cliquez sur `POST /api/v1/predict`
2. "Try it out"
3. Modifiez le JSON:

**Exemple 1 - Texte négatif**:
```json
{
  "text": "Je me sens triste et sans espoir, je n'ai plus envie de rien faire"
}
```

**Exemple 2 - Texte positif**:
```json
{
  "text": "Je suis heureux et plein d'énergie aujourd'hui"
}
```

**Exemple 3 - Texte neutre**:
```json
{
  "text": "Je vais à l'université pour suivre mes cours"
}
```

**Test PowerShell**:
```powershell
# Test négatif
$body = @{text = "Je me sens triste et sans espoir"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict" `
    -Method Post -Body $body -ContentType "application/json"

# Test positif
$body = @{text = "Je suis heureux et plein d'énergie"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict" `
    -Method Post -Body $body -ContentType "application/json"
```

**Résultat attendu**:
```json
{
  "prediction": "DÉPRESSION" ou "NORMAL",
  "confidence": 0.85,
  "severity": "Modérée",
  "reasoning": "...",
  "model_used": "yansnet-llm"
}
```

---

#### POST /api/v1/predict?model_name=qwen-depression
**Description**: Utilise spécifiquement le modèle Qwen pour la détection

**Test dans Swagger**:
1. `POST /api/v1/predict`
2. "Try it out"
3. Dans "Parameters", ajoutez `model_name`: `qwen-depression`
4. Body:
```json
{
  "text": "Je n'arrive plus à dormir, je me sens épuisé"
}
```

**Test PowerShell**:
```powershell
$body = @{text = "Je n'arrive plus à dormir, je me sens épuisé"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict?model_name=qwen-depression" `
    -Method Post -Body $body -ContentType "application/json"
```

---

### 3. Détection de Hate Speech

#### POST /api/v1/predict?model_name=hatecomment-bert
**Description**: Détecte les discours haineux dans les commentaires

**Test dans Swagger**:
1. `POST /api/v1/predict`
2. "Try it out"
3. Parameter `model_name`: `hatecomment-bert`

**Exemples de tests**:

**Exemple 1 - Commentaire haineux**:
```json
{
  "text": "Je déteste ces gens, ils sont tous stupides"
}
```

**Exemple 2 - Commentaire neutre**:
```json
{
  "text": "Je ne suis pas d'accord avec cette opinion"
}
```

**Exemple 3 - Commentaire positif**:
```json
{
  "text": "Merci pour ce partage, c'est très intéressant"
}
```

**Test PowerShell**:
```powershell
# Test haineux
$body = @{text = "Je déteste ces gens, ils sont tous stupides"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict?model_name=hatecomment-bert" `
    -Method Post -Body $body -ContentType "application/json"

# Test neutre
$body = @{text = "Je ne suis pas d'accord avec cette opinion"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict?model_name=hatecomment-bert" `
    -Method Post -Body $body -ContentType "application/json"
```

**Résultat attendu**:
```json
{
  "prediction": "HAINEUX" ou "NON-HAINEUX",
  "confidence": 0.75,
  "severity": "Modérée",
  "reasoning": "...",
  "model_used": "hatecomment-bert"
}
```

---

### 4. Génération de Contenu

#### POST /api/v1/content/generate-post
**Description**: Génère du contenu pour les réseaux sociaux

**Types de posts disponibles**:
- `confession`
- `coup de gueule`
- `demande d'aide`
- `message de soutien`
- `blague`
- `information utile`

**Test dans Swagger**:
1. `POST /api/v1/content/generate-post`
2. "Try it out"

**Exemple 1 - Blague**:
```json
{
  "post_type": "blague",
  "topic": "les examens",
  "sentiment": "positif"
}
```

**Exemple 2 - Conseil**:
```json
{
  "post_type": "information utile",
  "topic": "gestion du stress",
  "sentiment": "positif"
}
```

**Exemple 3 - Message de soutien**:
```json
{
  "post_type": "message de soutien",
  "topic": "difficultés scolaires",
  "sentiment": "positif"
}
```

**Exemple 4 - Confession**:
```json
{
  "post_type": "confession",
  "topic": "anxiété",
  "sentiment": "neutre"
}
```

**Test PowerShell**:
```powershell
# Blague
$body = @{
    post_type = "blague"
    topic = "les examens"
    sentiment = "positif"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/content/generate-post" `
    -Method Post -Body $body -ContentType "application/json"

# Information utile
$body = @{
    post_type = "information utile"
    topic = "gestion du temps"
    sentiment = "positif"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/content/generate-post" `
    -Method Post -Body $body -ContentType "application/json"

# Message de soutien
$body = @{
    post_type = "message de soutien"
    topic = "difficultés scolaires"
    sentiment = "positif"
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/content/generate-post" `
    -Method Post -Body $body -ContentType "application/json"
```

**Résultat attendu**:
```json
{
  "content": "Texte généré...",
  "post_type": "blague",
  "topic": "les examens",
  "sentiment": "positif",
  "timestamp": "2026-01-15T00:00:00"
}
```

---

### 5. Recommandations

#### GET /recommend?userId={userId}
**Description**: Obtient des recommandations de posts pour un utilisateur

**Test dans Swagger**:
1. `GET /recommend`
2. "Try it out"
3. Parameter `userId`: `1` (ou n'importe quel nombre)

**Test PowerShell**:
```powershell
# Recommandations pour utilisateur 1
Invoke-RestMethod -Uri "http://localhost:8001/recommend?userId=1" -Method Get

# Recommandations pour utilisateur 5
Invoke-RestMethod -Uri "http://localhost:8001/recommend?userId=5" -Method Get

# Recommandations pour utilisateur 10
Invoke-RestMethod -Uri "http://localhost:8001/recommend?userId=10" -Method Get
```

**Résultat attendu**:
```json
{
  "user_id": 1,
  "version": "2.0.0",
  "recommendations": [
    {"post_id": 20, "score": 0.85},
    {"post_id": 17, "score": 0.78},
    ...
  ]
}
```

---

### 6. Détection NSFW dans les Images

#### POST /api/v1/censure/detect
**Description**: Détecte le contenu NSFW dans les images

**Test dans Swagger**:
1. `POST /api/v1/censure/detect`
2. "Try it out"
3. Fournir une image encodée en base64

**Note**: Pour encoder une image en base64:
```powershell
$imageBytes = [System.IO.File]::ReadAllBytes("C:\chemin\vers\image.jpg")
$base64 = [System.Convert]::ToBase64String($imageBytes)
```

**Exemple de test**:
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

---

### 7. Analyse d'Images Sensibles

#### POST /api/v1/image/analyze
**Description**: Analyse le contenu sensible dans les images (drogue, violence, sexe)

**Test dans Swagger**:
1. `POST /api/v1/image/analyze`
2. "Try it out"
3. Fournir une image encodée en base64

**Exemple**:
```json
{
  "image_base64": "..."
}
```

---

### 8. Métriques et Monitoring

#### GET /api/v1/metrics/summary
**Description**: Résumé global des métriques

**Test dans Swagger**:
1. `GET /api/v1/metrics/summary`
2. "Try it out" → "Execute"

**Test PowerShell**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/metrics/summary" -Method Get | ConvertTo-Json -Depth 3
```

---

#### GET /api/v1/metrics/models
**Description**: Statistiques détaillées par modèle

**Test dans Swagger**:
1. `GET /api/v1/metrics/models`
2. "Try it out"
3. Optionnel: Parameter `hours`: `24` (dernières 24h)

**Test PowerShell**:
```powershell
# Dernières 24h
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/metrics/models?hours=24" -Method Get

# Dernière heure
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/metrics/models?hours=1" -Method Get
```

---

#### GET /api/v1/metrics/models/{model_name}
**Description**: Statistiques pour un modèle spécifique

**Test PowerShell**:
```powershell
# Stats pour yansnet-llm
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/metrics/models/yansnet-llm" -Method Get

# Stats pour hatecomment-bert
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/metrics/models/hatecomment-bert" -Method Get
```

---

## 📊 Monitoring des Performances

### 1. Commandes de Monitoring en Temps Réel

```powershell
# Voir les logs en temps réel
docker-compose logs -f api

# Voir uniquement les erreurs
docker-compose logs -f api | Select-String "ERROR"

# Voir les alertes de monitoring
docker-compose logs -f api | Select-String "ALERTE"

# Voir les métriques de latence
docker-compose logs -f api | Select-String "latency"

# Status des containers
docker-compose ps

# Utilisation des ressources
docker stats etsia-ml-api-cpu
```

### 2. Vérifier les Performances

```powershell
# Test de latence pour chaque endpoint
Measure-Command {
    Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
}

# Test de latence pour prédiction
Measure-Command {
    $body = @{text = "Test"} | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict" `
        -Method Post -Body $body -ContentType "application/json"
}

# Test de latence pour génération
Measure-Command {
    $body = @{
        post_type = "blague"
        topic = "test"
        sentiment = "positif"
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8001/api/v1/content/generate-post" `
        -Method Post -Body $body -ContentType "application/json"
}
```

### 3. Métriques Attendues

| Endpoint | Latence Attendue (CPU) | Latence Attendue (GPU) |
|----------|------------------------|------------------------|
| Health Check | < 100ms | < 50ms |
| Détection (CamemBERT) | 600-700ms | 50-100ms |
| Détection (Qwen) | 2-3s | 100-200ms |
| Génération (Llama 3.2 3B) | 2-10s | 300-500ms |
| Hate Speech | 400-600ms | 40-80ms |
| Recommandations | < 100ms | < 50ms |
| NSFW Detection | 500-800ms | 60-120ms |

---

## 🔍 Analyse des Logs

### 1. Commandes d'Analyse

```powershell
# Voir les 100 dernières lignes
docker-compose logs --tail=100 api

# Chercher les erreurs
docker-compose logs api | Select-String "ERROR"

# Chercher les warnings
docker-compose logs api | Select-String "WARNING"

# Chercher les alertes de monitoring
docker-compose logs api | Select-String "ALERTE"

# Voir les logs d'un modèle spécifique
docker-compose logs api | Select-String "qwen-depression"

# Voir les logs de démarrage
docker-compose logs api | Select-String "startup"

# Exporter les logs dans un fichier
docker-compose logs api > logs_api.txt
```

### 2. Logs des Autres Services

```powershell
# Logs GA4-Bridge
docker-compose logs -f ga4-bridge

# Logs PostgreSQL
docker-compose logs -f postgres

# Logs Redis
docker-compose logs -f redis

# Logs Ollama
docker-compose logs -f ollama

# Tous les logs
docker-compose logs -f
```

---

## 🔧 Résolution des Erreurs

### Erreur 1: "404 Client Error: Not Found for url: http://ollama:11434/api/generate"

**Cause**: Le modèle Ollama n'est pas téléchargé ou Ollama n'est pas démarré

**Solution**:
```powershell
# Vérifier qu'Ollama est lancé
docker-compose ps ollama

# Vérifier les modèles installés
docker exec ollama-server ollama list

# Télécharger les modèles manquants
docker exec ollama-server ollama pull qwen2.5:1.5b
docker exec ollama-server ollama pull llama3.2:3b

# Redémarrer l'API
docker-compose restart api
```

---

### Erreur 2: "connection to server at localhost, port 5432 failed"

**Cause**: PostgreSQL n'est pas accessible

**Solution**:
```powershell
# Vérifier que PostgreSQL est lancé
docker-compose ps postgres

# Voir les logs PostgreSQL
docker-compose logs postgres

# Redémarrer PostgreSQL
docker-compose restart postgres

# Attendre que PostgreSQL soit prêt
Start-Sleep -Seconds 10

# Redémarrer l'API
docker-compose restart api
```

---

### Erreur 3: "Memory Error" ou "Out of Memory"

**Cause**: Pas assez de mémoire allouée à Docker

**Solution**:
1. Ouvrir Docker Desktop
2. Settings → Resources → Memory
3. Augmenter à 12 GB minimum
4. Apply & Restart
5. Relancer les services:
```powershell
docker-compose --profile ml restart
```

---

### Erreur 4: Latence trop élevée

**Cause**: CPU surchargé ou modèles trop lourds

**Solutions**:
```powershell
# 1. Utiliser des modèles plus légers
# Dans .env, changer:
OLLAMA_GENERATION_MODEL=llama3.2:1b  # Au lieu de 3b

# 2. Réduire le nombre de workers
# Dans docker-compose.yml, modifier la commande:
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

# 3. Redémarrer
docker-compose restart api
```

---

### Erreur 5: "Model not found"

**Cause**: Le modèle demandé n'existe pas

**Solution**:
```powershell
# Lister les modèles disponibles
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/models" -Method Get

# Utiliser un nom de modèle valide:
# - yansnet-llm
# - qwen-depression
# - hatecomment-bert
# - yansnet-content-generator
# - recommendation-system
# - nsfw-detection
# - sensitive-image-caption
```

---

## 📈 Dashboard de Monitoring

### Accès au GA4-Bridge

```powershell
# Health check GA4-Bridge
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get

# Voir les logs du bridge
docker-compose logs -f ga4-bridge
```

### Métriques PostgreSQL

```powershell
# Se connecter à PostgreSQL
docker exec -it etsia-postgres psql -U etsia -d etsia_metrics

# Voir les prédictions récentes
SELECT model_name, COUNT(*), AVG(latency_ms) 
FROM model_predictions 
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY model_name;

# Voir les erreurs récentes
SELECT model_name, error_type, COUNT(*) 
FROM model_errors 
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY model_name, error_type;

# Quitter
\q
```

---

## 🎯 Checklist de Test Complet

### Tests Fonctionnels
- [ ] Health check retourne "healthy"
- [ ] Liste des modèles retourne 7 modèles
- [ ] Détection dépression (texte négatif)
- [ ] Détection dépression (texte positif)
- [ ] Détection hate speech (commentaire haineux)
- [ ] Détection hate speech (commentaire neutre)
- [ ] Génération de blague
- [ ] Génération d'information utile
- [ ] Génération de message de soutien
- [ ] Recommandations pour utilisateur 1
- [ ] Recommandations pour utilisateur 5
- [ ] Métriques summary
- [ ] Métriques par modèle

### Tests de Performance
- [ ] Health check < 100ms
- [ ] Détection < 1s
- [ ] Génération < 10s
- [ ] Recommandations < 100ms
- [ ] Pas d'erreur 500
- [ ] Pas de timeout

### Tests de Monitoring
- [ ] Logs accessibles
- [ ] Pas d'erreur critique
- [ ] Métriques enregistrées
- [ ] GA4-Bridge fonctionne
- [ ] PostgreSQL accessible
- [ ] Redis accessible

---

## 🚀 Script de Test Automatique

Utilisez le script fourni:
```powershell
.\test_api.ps1
```

Ce script teste automatiquement tous les endpoints principaux.

---

## 📞 Support

En cas de problème:
1. Vérifiez les logs: `docker-compose logs -f api`
2. Consultez ce guide
3. Redémarrez les services: `docker-compose restart api`
4. Consultez `DEPLOIEMENT_REUSSI.md`

**Bon testing ! 🎉**
