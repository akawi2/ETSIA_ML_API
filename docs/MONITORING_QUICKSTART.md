# Quick Start - Système de Monitoring

Guide rapide pour démarrer avec le système de monitoring Yansnet.

## Installation (5 minutes)

### 1. Configuration

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer et ajouter vos credentials GA4
nano .env
```

Ajouter dans `.env`:
```bash
# Google Analytics 4
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=your_api_secret_here

# Monitoring
BRIDGE_URL=http://ga4-bridge:5000/log_metric
ENABLE_METRICS=true
```

### 2. Démarrage

```bash
# Démarrer tous les services (monitoring + ML)
docker-compose --profile ml up -d

# Vérifier que tout fonctionne
curl http://localhost:5000/health  # GA4-Bridge
curl http://localhost:8001/health  # ML API
```

### 3. Test

```bash
# Exécuter le script de test
python scripts/test_monitoring_integration.py
```

## Utilisation Basique

### Dans un Modèle ML

```python
from app.core.monitoring import emit_metric
import time

class MonModele(BaseMLModel):
    def predict(self, text: str):
        start_time = time.time()
        
        # Votre logique
        result = self._do_prediction(text)
        
        # Monitoring
        emit_metric(
            service="mon_service",
            event_name="predict",
            model_name="mon-modele",
            params={
                "latency": int((time.time() - start_time) * 1000),
                "confidence": result["confidence"]
            }
        )
        
        return result
```

### Ajouter une Alerte

Éditer `metrics_catalog.json`:

```json
{
  "service": "mon_service",
  "metric": "latency",
  "threshold": 500,
  "operator": ">",
  "priority": "Moyenne",
  "description": "Alerte latence élevée"
}
```

Redémarrer le bridge:
```bash
docker-compose restart ga4-bridge
```

## Vérification

### Logs du Bridge

```bash
# Voir les métriques reçues
docker-compose logs -f ga4-bridge

# Voir les alertes déclenchées
docker-compose logs ga4-bridge | grep ALERTE
```

### Google Analytics 4

1. Aller sur https://analytics.google.com
2. Sélectionner votre propriété
3. Rapports > Événements
4. Voir les événements en temps réel

## Services Disponibles

| Service | Endpoint | Port |
|---------|----------|------|
| GA4-Bridge | http://localhost:5000 | 5000 |
| ML API | http://localhost:8001 | 8001 |
| FastAPI Demo | http://localhost:8000 | 8000 |

## Commandes Utiles

```bash
# Démarrer
docker-compose --profile ml up -d

# Arrêter
docker-compose down

# Logs
docker-compose logs -f ga4-bridge
docker-compose logs -f api

# Redémarrer après changement de config
docker-compose restart ga4-bridge

# Health checks
curl http://localhost:5000/health
curl http://localhost:8001/health
```

## Dépannage Rapide

### Le monitoring ne fonctionne pas

```bash
# 1. Vérifier les services
docker-compose ps

# 2. Vérifier les logs
docker-compose logs ga4-bridge

# 3. Tester manuellement
curl -X POST http://localhost:5000/log_metric \
  -H "Content-Type: application/json" \
  -d '{"service":"test","event_name":"test","model_name":"test","params":{"latency":100},"client_id":"test"}'
```

### Désactiver temporairement

```bash
# Dans .env
ENABLE_METRICS=false

# Redémarrer
docker-compose restart api
```

## Documentation Complète

- [Système de Monitoring](./MONITORING_SYSTEM.md) - Documentation complète
- [Guide d'Intégration](./MONITORING_INTEGRATION.md) - Intégrer dans vos modèles
- [Metrics Catalog](../metrics_catalog.json) - Configuration des alertes

## Support

- Logs: `docker-compose logs -f`
- Tests: `python scripts/test_monitoring_integration.py`
- Health: `curl http://localhost:5000/health`
