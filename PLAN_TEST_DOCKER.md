# 🧪 Plan de Test Complet - Docker

Plan détaillé pour tester l'ensemble du système Docker avec monitoring.

## 📋 Prérequis

- [ ] Docker Desktop installé et démarré
- [ ] Connexion Internet stable
- [ ] PowerShell ou Terminal ouvert
- [ ] Fichier `.env` configuré

## 🎯 Phase 1 : Préparation (5 min)

### 1.1 Vérifier Docker
```powershell
# Vérifier que Docker fonctionne
docker --version
docker ps

# Arrêter les anciens conteneurs
docker-compose down -v
```

**Résultat attendu** : Docker version affichée, aucun conteneur en cours

### 1.2 Vérifier la Configuration
```powershell
# Vérifier que .env existe
cat .env | Select-String "GA4"

# Vérifier docker-compose.yml
cat docker-compose.yml | Select-String "ga4-bridge"
```

**Résultat attendu** : Variables GA4 présentes, services configurés

### 1.3 Nettoyer l'Environnement
```powershell
# Supprimer les anciens volumes
docker volume prune -f

# Supprimer les anciennes images (optionnel)
docker image prune -a -f
```

## 🚀 Phase 2 : Démarrage Monitoring Seul (5 min)

### 2.1 Démarrer GA4-Bridge
```powershell
# Démarrer uniquement le monitoring
docker-compose up -d ga4-bridge
```

**Résultat attendu** : 
```
✔ Container ga4-bridge  Started
```

### 2.2 Vérifier les Logs
```powershell
# Voir les logs du bridge
docker-compose logs ga4-bridge

# Vérifier qu'il n'y a pas d'erreurs
docker-compose logs ga4-bridge | Select-String "ERROR"
```

**Résultat attendu** : 
```
INFO:     Uvicorn running on http://0.0.0.0:5000
INFO:     Application startup complete
```

### 2.3 Test Health Check
```powershell
# Test 1 : Health check
curl http://localhost:5000/health -UseBasicParsing
```

**Résultat attendu** :
```json
{"status":"ok","catalog_rules":40}
```

**✅ Checkpoint 1** : Si le health check fonctionne, le monitoring est OK !

## 🧪 Phase 3 : Tests du Monitoring (10 min)

### 3.1 Test Métrique Simple
```powershell
# Envoyer une métrique de test
$body = '{"service":"test","event_name":"test","model_name":"test","params":{"latency":100},"client_id":"test"}'
Invoke-WebRequest -Uri http://localhost:5000/log_metric -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Résultat attendu** :
```json
{"status":"queued","alerts":false}
```

### 3.2 Test Alerte (Latence Élevée)
```powershell
# Envoyer une métrique qui déclenche une alerte
$body = '{"service":"hate_comment","event_name":"detect_hate","model_name":"bert-multilingual","params":{"latency":600},"client_id":"test"}'
Invoke-WebRequest -Uri http://localhost:5000/log_metric -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Résultat attendu** :
```json
{"status":"queued","alerts":true}
```

### 3.3 Vérifier les Alertes dans les Logs
```powershell
# Voir les alertes déclenchées
docker-compose logs ga4-bridge | Select-String "ALERTE"
```

**Résultat attendu** :
```
⚠️ ALERTE: hate_comment - latency: 600 > 500
```

**✅ Checkpoint 2** : Si les alertes se déclenchent, le système d'évaluation fonctionne !

## 🐳 Phase 4 : Démarrage Services de Base (10 min)

### 4.1 Démarrer PostgreSQL et Redis
```powershell
# Démarrer les services de base
docker-compose up -d postgres redis
```

**Résultat attendu** :
```
✔ Container etsia-postgres  Started
✔ Container etsia-redis     Started
```

### 4.2 Attendre le Démarrage
```powershell
# Attendre que les services soient prêts (30 secondes)
Start-Sleep -Seconds 30

# Vérifier l'état
docker-compose ps
```

**Résultat attendu** : Status "Up" pour postgres et redis

### 4.3 Test PostgreSQL
```powershell
# Tester la connexion PostgreSQL
docker exec etsia-postgres pg_isready -U etsia -d etsia_metrics
```

**Résultat attendu** :
```
etsia_metrics:5432 - accepting connections
```

### 4.4 Test Redis
```powershell
# Tester Redis
docker exec etsia-redis redis-cli ping
```

**Résultat attendu** :
```
PONG
```

**✅ Checkpoint 3** : Si PostgreSQL et Redis répondent, les services de base sont OK !

## 🤖 Phase 5 : Démarrage Ollama (15-30 min)

### 5.1 Télécharger l'Image Ollama
```powershell
# Télécharger Ollama (peut prendre 5-10 min)
docker pull ollama/ollama:latest
```

**Résultat attendu** : Image téléchargée avec succès

### 5.2 Démarrer Ollama
```powershell
# Démarrer Ollama
docker-compose up -d ollama
```

**Résultat attendu** :
```
✔ Container ollama-server  Started
```

### 5.3 Attendre le Démarrage
```powershell
# Attendre qu'Ollama soit prêt (30 secondes)
Start-Sleep -Seconds 30

# Vérifier les logs
docker-compose logs ollama
```

### 5.4 Télécharger les Modèles
```powershell
# Télécharger Qwen 2.5 1.5B (peut prendre 10-15 min)
docker exec ollama-server ollama pull qwen2.5:1.5b

# Télécharger Llama 3.2 3B (peut prendre 10-15 min)
docker exec ollama-server ollama pull llama3.2:3b

# Vérifier les modèles installés
docker exec ollama-server ollama list
```

**Résultat attendu** :
```
NAME                ID              SIZE
qwen2.5:1.5b       abc123          900 MB
llama3.2:3b        def456          2.0 GB
```

**✅ Checkpoint 4** : Si les modèles sont téléchargés, Ollama est prêt !

## 🚀 Phase 6 : Démarrage API ML (10 min)

### 6.1 Démarrer l'API ML
```powershell
# Démarrer l'API ML (CPU)
docker-compose up -d api
```

**Résultat attendu** :
```
✔ Container etsia-ml-api-cpu  Started
```

### 6.2 Attendre le Démarrage
```powershell
# Attendre que l'API soit prête (120 secondes - temps de démarrage augmenté)
Start-Sleep -Seconds 120

# Vérifier les logs
docker-compose logs api | Select-String "Application startup complete"
```

### 6.3 Test Health Check API
```powershell
# Test health check
curl http://localhost:8001/health -UseBasicParsing
```

**Résultat attendu** :
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "models": {
    "total": 6,
    "available": [
      "yansnet-llm",
      "camembert-depression",
      "sensitive-image-caption",
      "yansnet-content-generator",
      "hatecomment-bert",
      "recommendation-system"
    ]
  }
}
```

> **Note**: Le modèle `censure-nsfw` est désactivé par défaut pour accélérer les tests. Total: 6 modèles au lieu de 7.
```

**✅ Checkpoint 5** : Si l'API répond, tous les services sont démarrés !

## 🧪 Phase 7 : Tests des Modèles ML (20 min)

### 7.1 Test HateComment Detection
```powershell
# Test 1 : Texte normal
$body = '{"text":"Bonjour, comment allez-vous?"}'
Invoke-WebRequest -Uri http://localhost:8001/api/v1/hatecomment/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing

# Test 2 : Texte haineux
$body = '{"text":"Je déteste tous ces gens"}'
Invoke-WebRequest -Uri http://localhost:8001/api/v1/hatecomment/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Résultat attendu** :
```json
{
  "prediction": "HAINEUX",
  "confidence": 0.85,
  "severity": "Élevée"
}
```

### 7.2 Test Depression Detection (CamemBERT)
```powershell
# Test dépression
$body = '{"text":"Je me sens très triste et sans espoir depuis plusieurs semaines"}'
Invoke-WebRequest -Uri http://localhost:8001/api/v1/depression/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Résultat attendu** :
```json
{
  "prediction": "DÉPRESSION",
  "confidence": 0.78,
  "severity": "Moyenne"
}
```

### 7.3 Test Depression Detection (Qwen)
```powershell
# Test avec Qwen
$body = '{"text":"Je me sens très triste","model_type":"qwen"}'
Invoke-WebRequest -Uri http://localhost:8001/api/v1/depression/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

### 7.4 Test Recommendation System
```powershell
# Test recommandations
$body = '{"user_id":1,"top_n":10}'
Invoke-WebRequest -Uri http://localhost:8001/api/v1/recommendation/recommend -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Résultat attendu** :
```json
{
  "user_id": 1,
  "recommendations": [...],
  "total_recommendations": 10
}
```

### 7.5 Vérifier les Métriques dans le Bridge
```powershell
# Voir toutes les métriques reçues
docker-compose logs ga4-bridge | Select-String "hate_comment|depression_detection|recommendation"

# Voir les alertes déclenchées
docker-compose logs ga4-bridge | Select-String "ALERTE"
```

**✅ Checkpoint 6** : Si tous les modèles répondent et émettent des métriques, le système est complet !

## 📊 Phase 8 : Vérification Complète (5 min)

### 8.1 Vérifier Tous les Services
```powershell
# Lister tous les conteneurs
docker-compose ps

# Vérifier qu'ils sont tous "Up"
docker-compose ps | Select-String "Up"
```

**Résultat attendu** : 5 services "Up" (avec profil ml)
- ga4-bridge
- postgres
- redis
- ollama
- api

> **Note**: Le modèle NSFW est désactivé dans le code, donc 6 modèles ML sont chargés au lieu de 7.

### 8.2 Vérifier les Logs d'Erreurs
```powershell
# Chercher les erreurs dans tous les services
docker-compose logs | Select-String "ERROR|CRITICAL|FATAL"
```

**Résultat attendu** : Aucune erreur critique

### 8.3 Test de Charge Léger
```powershell
# Envoyer 10 requêtes rapides
for ($i=1; $i -le 10; $i++) {
    $body = '{"text":"Test ' + $i + '"}'
    Invoke-WebRequest -Uri http://localhost:8001/api/v1/hatecomment/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "Test $i/10 terminé"
}

# Vérifier que toutes les métriques ont été reçues
docker-compose logs ga4-bridge | Select-String "hate_comment" | Measure-Object
```

**Résultat attendu** : 10 métriques reçues

## 📈 Phase 9 : Monitoring en Temps Réel (5 min)

### 9.1 Ouvrir les Logs en Temps Réel
```powershell
# Terminal 1 : Logs du bridge
docker-compose logs -f ga4-bridge

# Terminal 2 : Logs de l'API
docker-compose logs -f api
```

### 9.2 Envoyer des Requêtes et Observer
```powershell
# Dans un 3ème terminal, envoyer des requêtes
$body = '{"text":"Test monitoring en temps réel"}'
Invoke-WebRequest -Uri http://localhost:8001/api/v1/hatecomment/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

**Observer** :
- Terminal 1 : Métrique reçue par le bridge
- Terminal 2 : Prédiction effectuée par l'API

## 🎯 Phase 10 : Tests Avancés (Optionnel)

### 10.1 Test Script Python - Monitoring
```powershell
# Exécuter le script de test du monitoring
python scripts/test_monitoring_integration.py
```

### 10.2 Test Script Python - Docker Complet
```powershell
# Exécuter le script de test complet de l'environnement Docker
python scripts/test_docker_complete.py
```

**Ce script teste automatiquement :**
- ✅ Health checks (API ML + GA4-Bridge)
- ✅ Modèles ML (Depression, Hate Speech, Recommendation)
- ✅ Système de monitoring (métriques + alertes)
- ✅ Cache Redis (stats)
- ✅ Requêtes concurrentes (10 requêtes simultanées)

**Résultat attendu :**
```
============================================================
  TESTS DOCKER COMPLETS - ETSIA ML API
============================================================

=== TEST 1: Health Checks ===
✓ API ML Health Check
  → 6 modèles chargés (NSFW désactivé par défaut)
✓ GA4-Bridge Health Check
  → 40 règles d'alerte

[... autres tests ...]

============================================================
  RÉSUMÉ
============================================================

Tests réussis: 10/10
Taux de réussite: 100.0%
Status: EXCELLENT
```

### 10.2 Test de Performance
```powershell
# Mesurer la latence moyenne
Measure-Command {
    $body = '{"text":"Test performance"}'
    Invoke-WebRequest -Uri http://localhost:8001/api/v1/hatecomment/predict -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
}
```

**Résultat attendu** : < 1 seconde

### 10.3 Test de Résilience
```powershell
# Redémarrer le bridge pendant que l'API tourne
docker-compose restart ga4-bridge

# Attendre 10 secondes
Start-Sleep -Seconds 10

# Vérifier que l'API continue de fonctionner
curl http://localhost:8001/health -UseBasicParsing
```

## ✅ Checklist Finale

### Services
- [ ] GA4-Bridge démarré et répond (port 5000)
- [ ] PostgreSQL démarré et accepte les connexions
- [ ] Redis démarré et répond au ping
- [ ] Ollama démarré avec modèles téléchargés
- [ ] API ML démarrée et répond (port 8001)

### Monitoring
- [ ] Health check du bridge fonctionne
- [ ] Métriques reçues et mises en file
- [ ] Alertes détectées et loggées
- [ ] Catalogue de règles chargé (40+ règles)

### Modèles ML
- [ ] HateComment BERT fonctionne
- [ ] Depression CamemBERT fonctionne
- [ ] Depression Qwen fonctionne
- [ ] Recommendation System fonctionne
- [ ] Métriques émises vers le bridge

### Intégration
- [ ] API → Bridge : Communication OK
- [ ] Bridge → GA4 : Configuration OK (si credentials fournis)
- [ ] Logs sans erreurs critiques
- [ ] Performance acceptable (< 1s par requête)

## 🛑 Arrêt Propre

```powershell
# Arrêter tous les services
docker-compose down

# Garder les volumes (données)
docker-compose down

# Supprimer aussi les volumes (reset complet)
docker-compose down -v
```

## 📊 Résultats Attendus

### Temps Total
- **Monitoring seul** : 5-10 minutes
- **Services de base** : +10 minutes
- **Ollama + Modèles** : +30-45 minutes
- **API ML + Tests** : +20 minutes (démarrage API: 2 min)
- **Total** : 1h-1h30 (première fois)

### Ressources
- **RAM** : 6-8 GB utilisés
- **Disk** : 10-15 GB (images + modèles)
- **CPU** : 20-40% en idle, 60-80% pendant inférence

## 🔧 Dépannage Rapide

### Problème : Service ne démarre pas
```powershell
# Voir les logs détaillés
docker-compose logs [service-name]

# Redémarrer le service
docker-compose restart [service-name]
```

### Problème : Port déjà utilisé
```powershell
# Trouver le processus qui utilise le port
netstat -ano | findstr :5000

# Tuer le processus (remplacer PID)
taskkill /PID [PID] /F
```

### Problème : Mémoire insuffisante
```powershell
# Augmenter la mémoire Docker Desktop
# Settings → Resources → Memory → 8 GB minimum
```

## 🎉 Succès !

Si tous les checkpoints sont validés, votre système Docker est **100% opérationnel** ! 🚀

Vous pouvez maintenant :
- Utiliser l'API ML en production
- Monitorer les métriques en temps réel
- Consulter les alertes dans les logs
- Intégrer avec Google Analytics 4
