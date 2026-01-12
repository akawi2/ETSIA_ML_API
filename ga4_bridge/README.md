# GA4-Bridge - Monitoring Middleware

Service FastAPI qui évalue les métriques ML contre des seuils configurables avant de les transmettre à Google Analytics 4.

## Rôle

Le GA4-Bridge agit comme un middleware intelligent entre l'API ML et Google Analytics 4 :

1. **Reçoit** les métriques des modèles ML
2. **Évalue** les seuils définis dans `metrics_catalog.json`
3. **Enrichit** les événements avec des tags d'alerte si nécessaire
4. **Forwarde** vers Google Analytics 4 via Measurement Protocol

## Architecture

```
ML API → GA4-Bridge → Google Analytics 4
         (Port 5000)
         
         ↓ Évalue
         metrics_catalog.json
```

## Fichiers

- `main.py` : Application FastAPI principale
- `schemas.py` : Modèles Pydantic pour validation
- `Dockerfile` : Image Docker
- `requirements.txt` : Dépendances Python

## Endpoints

### POST /log_metric

Reçoit une métrique et l'évalue contre le catalogue.

**Request**:
```json
{
  "service": "hate_comment",
  "event_name": "detect_hate",
  "model_name": "bert-multilingual",
  "params": {
    "latency": 600,
    "confidence": 0.85
  },
  "client_id": "etsia_ml_api_v2"
}
```

**Response**:
```json
{
  "status": "queued",
  "alerts": true
}
```

### GET /health

Health check du service.

**Response**:
```json
{
  "status": "ok",
  "catalog_rules": 50
}
```

## Configuration

### Variables d'Environnement

```bash
GA4_MEASUREMENT_ID=G-XXXXXXXXXX  # ID de mesure GA4
GA4_API_SECRET=your_secret       # Secret API GA4
```

### Catalogue de Métriques

Le fichier `metrics_catalog.json` (monté en volume) définit les règles d'alerte :

```json
{
  "service": "hate_comment",
  "metric": "latency",
  "threshold": 500,
  "operator": ">",
  "priority": "Moyenne",
  "description": "Alerte temps de réponse lent"
}
```

**Champs**:
- `service` : Nom du service (hate_comment, depression_detection, etc.)
- `metric` : Nom de la métrique à évaluer
- `threshold` : Valeur seuil
- `operator` : Opérateur de comparaison (>, <, >=, <=)
- `priority` : Priorité de l'alerte (Critique, Haute, Moyenne, Faible)
- `description` : Description de l'alerte
- `model` (optionnel) : Filtre par modèle spécifique

## Logique d'Évaluation

Pour chaque métrique reçue :

1. **Filtrage par service** : Sélectionne les règles du service
2. **Filtrage par modèle** : Si spécifié dans la règle
3. **Évaluation du seuil** : Compare la valeur avec le seuil
4. **Enrichissement** : Si alerte déclenchée, ajoute :
   - `alert_triggered`: "true"
   - `alert_reason`: "{metric}_fail"
   - `alert_priority`: "Critique|Haute|Moyenne|Faible"

## Exemple d'Enrichissement

**Métrique reçue**:
```json
{
  "service": "hate_comment",
  "params": {
    "latency": 600,
    "confidence": 0.85
  }
}
```

**Règle applicable**:
```json
{
  "service": "hate_comment",
  "metric": "latency",
  "threshold": 500,
  "operator": ">",
  "priority": "Moyenne"
}
```

**Métrique enrichie**:
```json
{
  "service": "hate_comment",
  "params": {
    "latency": 600,
    "confidence": 0.85,
    "alert_triggered": "true",
    "alert_reason": "latency_fail",
    "alert_priority": "Moyenne"
  }
}
```

## Démarrage

### Avec Docker Compose

```bash
# Démarrer le bridge
docker-compose up -d ga4-bridge

# Vérifier les logs
docker-compose logs -f ga4-bridge

# Health check
curl http://localhost:5000/health
```

### En Local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Définir les variables
export GA4_MEASUREMENT_ID=G-XXXXXXXXXX
export GA4_API_SECRET=your_secret

# Démarrer
uvicorn main:app --host 0.0.0.0 --port 5000
```

## Tests

### Test Manuel

```bash
# Envoyer une métrique de test
curl -X POST http://localhost:5000/log_metric \
  -H "Content-Type: application/json" \
  -d '{
    "service": "hate_comment",
    "event_name": "detect_hate",
    "model_name": "bert-multilingual",
    "params": {
      "latency": 600,
      "confidence": 0.85
    },
    "client_id": "test"
  }'
```

### Test avec Alerte

```bash
# Métrique qui déclenche une alerte (latency > 500)
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

# Vérifier les logs
docker-compose logs ga4-bridge | grep ALERTE
```

## Logs

Les logs affichent :
- Métriques reçues
- Alertes déclenchées (⚠️ ALERTE)
- Erreurs d'envoi vers GA4

```bash
# Voir tous les logs
docker-compose logs -f ga4-bridge

# Voir uniquement les alertes
docker-compose logs ga4-bridge | grep ALERTE

# Voir les erreurs
docker-compose logs ga4-bridge | grep ERROR
```

## Rechargement du Catalogue

Pour recharger le catalogue après modification :

```bash
# Redémarrer le service
docker-compose restart ga4-bridge

# Vérifier le nombre de règles chargées
curl http://localhost:5000/health
```

## Dépannage

### Le bridge ne démarre pas

```bash
# Vérifier les logs
docker-compose logs ga4-bridge

# Vérifier les variables d'environnement
docker-compose exec ga4-bridge env | grep GA4
```

### Les métriques ne sont pas envoyées à GA4

```bash
# Vérifier les credentials GA4
echo $GA4_MEASUREMENT_ID
echo $GA4_API_SECRET

# Tester manuellement
curl -X POST "https://www.google-analytics.com/mp/collect?measurement_id=$GA4_MEASUREMENT_ID&api_secret=$GA4_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "test",
    "events": [{
      "name": "test_event",
      "params": {"test": "value"}
    }]
  }'
```

### Les alertes ne se déclenchent pas

```bash
# Vérifier le catalogue
cat ../metrics_catalog.json | jq

# Vérifier les logs d'évaluation
docker-compose logs ga4-bridge | grep "Évalue"

# Tester avec une métrique qui devrait déclencher
curl -X POST http://localhost:5000/log_metric \
  -H "Content-Type: application/json" \
  -d '{
    "service": "hate_comment",
    "event_name": "test",
    "model_name": "test",
    "params": {"latency": 1000},
    "client_id": "test"
  }'
```

## Métriques de Performance

Le bridge est conçu pour être rapide :
- Évaluation des seuils : < 1ms
- Envoi vers GA4 : asynchrone (non bloquant)
- Timeout : configurable (défaut: aucun)

## Sécurité

- Les credentials GA4 sont en variables d'environnement
- Pas d'authentification sur le bridge (réseau interne Docker)
- Validation des données avec Pydantic

## Évolutions Futures

- [ ] Support de règles complexes (AND/OR)
- [ ] Agrégations (moyennes, percentiles)
- [ ] Cache des règles en mémoire
- [ ] Métriques du bridge lui-même
- [ ] Support de multiples destinations (GA4, Supabase, etc.)

## Documentation

- [Système de Monitoring](../docs/MONITORING_SYSTEM.md)
- [Guide d'Intégration](../docs/MONITORING_INTEGRATION.md)
- [Quick Start](../docs/MONITORING_QUICKSTART.md)

## Support

- Logs : `docker-compose logs -f ga4-bridge`
- Health : `curl http://localhost:5000/health`
- Tests : `python ../scripts/test_monitoring_integration.py`
