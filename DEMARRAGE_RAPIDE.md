# 🚀 Démarrage Rapide - Système de Monitoring

Guide pour démarrer le système de monitoring en 5 minutes.

## ⚠️ Prérequis

1. **Docker Desktop** installé et démarré
2. **Connexion Internet** (pour télécharger les images)
3. **Credentials GA4** (optionnel pour les tests)

## 📝 Étape 1 : Configuration (1 minute)

### Option A : Avec Google Analytics 4 (Production)

Éditez `.env` et ajoutez vos credentials GA4 :

```bash
# Google Analytics 4
GA4_MEASUREMENT_ID=G-VOTRE-ID-ICI
GA4_API_SECRET=votre_secret_ici
```

### Option B : Sans GA4 (Tests locaux)

Le système fonctionnera sans GA4, mais les métriques ne seront pas envoyées à Google Analytics.

Laissez les valeurs par défaut dans `.env` :
```bash
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=your_api_secret_here
```

## 🐳 Étape 2 : Démarrage (2-5 minutes)

### Option 1 : Monitoring Seul (Rapide)

Démarrez uniquement le système de monitoring :

```bash
docker-compose up -d ga4-bridge fastapi-app
```

**Services démarrés** :
- GA4-Bridge (port 5000)
- FastAPI Demo App (port 8000)

### Option 2 : Système Complet avec ML (Plus long)

Démarrez tous les services incluant les modèles ML :

```bash
docker-compose --profile ml up -d
```

**Services démarrés** :
- GA4-Bridge (port 5000)
- FastAPI Demo App (port 8000)
- ML API (port 8001)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Ollama (port 11434)

⏱️ **Temps de démarrage** : 5-10 minutes la première fois (téléchargement des images)

## ✅ Étape 3 : Vérification (1 minute)

### Vérifier les services

```bash
# Voir l'état des services
docker-compose ps

# Vérifier les logs
docker-compose logs -f ga4-bridge
```

### Health Checks

```bash
# GA4-Bridge
curl http://localhost:5000/health

# FastAPI Demo App
curl http://localhost:8000/health

# ML API (si démarré avec --profile ml)
curl http://localhost:8001/health
```

**Réponse attendue** :
```json
{
  "status": "ok",
  "catalog_rules": 50
}
```

## 🧪 Étape 4 : Tests (1 minute)

### Test Manuel Rapide

Envoyez une métrique de test au bridge :

```bash
curl -X POST http://localhost:5000/log_metric \
  -H "Content-Type: application/json" \
  -d '{
    "service": "test_service",
    "event_name": "test_event",
    "model_name": "test-model",
    "params": {
      "latency": 250,
      "confidence": 0.85
    },
    "client_id": "test_client"
  }'
```

**Réponse attendue** :
```json
{
  "status": "queued",
  "alerts": false
}
```

### Test avec Alerte

Envoyez une métrique qui déclenche une alerte :

```bash
curl -X POST http://localhost:5000/log_metric \
  -H "Content-Type: application/json" \
  -d '{
    "service": "hate_comment",
    "event_name": "detect_hate",
    "model_name": "bert-multilingual",
    "params": {
      "latency": 600
    },
    "client_id": "test"
  }'
```

**Réponse attendue** :
```json
{
  "status": "queued",
  "alerts": true
}
```

Vérifiez les logs pour voir l'alerte :
```bash
docker-compose logs ga4-bridge | grep ALERTE
```

### Suite de Tests Complète

Si Python est installé :

```bash
python scripts/test_monitoring_integration.py
```

## 📊 Étape 5 : Utilisation

### Voir les Métriques en Temps Réel

```bash
# Logs du bridge (toutes les métriques)
docker-compose logs -f ga4-bridge

# Uniquement les alertes
docker-compose logs ga4-bridge | grep ALERTE

# Logs de l'API ML
docker-compose logs -f api
```

### Tester les Endpoints ML (si --profile ml)

**HateComment Detection** :
```bash
curl -X POST http://localhost:8001/api/v1/hatecomment/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Je déteste tous ces gens"}'
```

**Depression Detection** :
```bash
curl -X POST http://localhost:8001/api/v1/depression/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Je me sens très triste depuis plusieurs semaines"}'
```

**Recommendations** :
```bash
curl -X POST http://localhost:8001/api/v1/recommendation/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "top_n": 10}'
```

### Consulter Google Analytics 4

Si vous avez configuré GA4 :

1. Aller sur https://analytics.google.com
2. Sélectionner votre propriété
3. Rapports > Événements
4. Voir les événements en temps réel

## 🛑 Arrêt des Services

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

## 🔧 Dépannage

### Problème : Services ne démarrent pas

```bash
# Vérifier Docker Desktop
docker ps

# Voir les erreurs
docker-compose logs

# Redémarrer Docker Desktop
```

### Problème : Port déjà utilisé

Si un port est déjà utilisé (5000, 8000, 8001), modifiez `docker-compose.yml` :

```yaml
ports:
  - "5001:5000"  # Changez 5000 en 5001
```

### Problème : Variables GA4 manquantes

Vérifiez que `.env` contient :
```bash
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=your_api_secret_here
```

### Problème : Erreur réseau Docker

Si Docker ne peut pas télécharger les images :

1. Vérifiez votre connexion Internet
2. Redémarrez Docker Desktop
3. Essayez : `docker-compose pull`

### Problème : Le bridge ne reçoit pas de métriques

Vérifiez que l'API est configurée :

```bash
# Dans .env
BRIDGE_URL=http://ga4-bridge:5000/log_metric
ENABLE_METRICS=true
```

## 📚 Documentation Complète

- **Quick Start** : `docs/MONITORING_QUICKSTART.md`
- **Documentation Complète** : `docs/MONITORING_SYSTEM.md`
- **Guide d'Intégration** : `docs/MONITORING_INTEGRATION.md`
- **Résumé** : `MONITORING_COMPLETE.md`

## 🎯 Prochaines Étapes

1. ✅ Démarrer les services
2. ✅ Vérifier les health checks
3. ✅ Tester l'envoi de métriques
4. ✅ Consulter les logs
5. 📊 Configurer GA4 (optionnel)
6. 🔧 Ajuster les seuils dans `metrics_catalog.json`
7. 🚀 Déployer en production

## 💡 Conseils

- **Première fois** : Utilisez l'Option 1 (monitoring seul) pour tester rapidement
- **Production** : Configurez GA4 pour avoir les métriques dans le dashboard
- **Développement** : Utilisez `ENABLE_METRICS=false` pour désactiver temporairement
- **Performance** : Le monitoring ajoute < 1ms de latence (timeout 0.5s)

## ✨ Résumé

```bash
# 1. Configuration (optionnel)
# Éditez .env avec vos credentials GA4

# 2. Démarrage
docker-compose up -d ga4-bridge fastapi-app

# 3. Vérification
curl http://localhost:5000/health

# 4. Test
curl -X POST http://localhost:5000/log_metric \
  -H "Content-Type: application/json" \
  -d '{"service":"test","event_name":"test","model_name":"test","params":{"latency":100},"client_id":"test"}'

# 5. Logs
docker-compose logs -f ga4-bridge
```

**C'est tout ! Le système de monitoring est opérationnel.** 🎉
