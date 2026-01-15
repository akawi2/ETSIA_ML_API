# Système de Monitoring Yansnet

Documentation complète du système de monitoring intégré pour l'API ML ETSIA.

## Vue d'Ensemble

Le système de monitoring Yansnet permet de suivre en temps réel les performances et la qualité de tous les modèles ML déployés. Il utilise une architecture à 3 niveaux :

```
┌──────────────────────────────────────────────────────────────┐
│                     NIVEAU 1: COLLECTE                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ HateComment│  │ Depression │  │   Content  │  ... autres │
│  │   Model    │  │   Model    │  │  Generator │             │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │
│        │                │                │                     │
│        └────────────────┴────────────────┘                     │
│                         │                                      │
│                  emit_metric()                                 │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  NIVEAU 2: ÉVALUATION                         │
│                                                                │
│                    ┌──────────────┐                           │
│                    │  GA4-Bridge  │                           │
│                    │  (Port 5000) │                           │
│                    │              │                           │
│                    │ • Évalue les │                           │
│                    │   seuils     │                           │
│                    │ • Enrichit   │                           │
│                    │   alertes    │                           │
│                    │ • Forwarde   │                           │
│                    └──────┬───────┘                           │
└───────────────────────────┼───────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                NIVEAU 3: VISUALISATION                        │
│                                                                │
│                  ┌──────────────┐                             │
│                  │   Google     │                             │
│                  │ Analytics 4  │                             │
│                  │              │                             │
│                  │ • Dashboard  │                             │
│                  │ • Alertes    │                             │
│                  │ • Historique │                             │
│                  └──────────────┘                             │
└──────────────────────────────────────────────────────────────┘
```

## Composants

### 1. Client de Monitoring (`app/core/monitoring/`)

Module Python intégré dans l'API ML pour émettre des métriques.

**Fichiers**:
- `client.py` : Client de monitoring et décorateurs
- `__init__.py` : Exports publics

**Usage**:
```python
from app.core.monitoring import emit_metric

emit_metric(
    service="hate_comment",
    event_name="detect_hate",
    model_name="bert-multilingual",
    params={"latency": 250, "confidence": 0.85}
)
```

### 2. GA4-Bridge (`ga4_bridge/`)

Service FastAPI qui évalue les métriques contre des seuils configurables.

**Fichiers**:
- `main.py` : Application FastAPI
- `schemas.py` : Modèles Pydantic
- `Dockerfile` : Image Docker
- `requirements.txt` : Dépendances

**Endpoints**:
- `POST /log_metric` : Recevoir une métrique
- `GET /health` : Health check

### 3. Catalogue de Métriques (`metrics_catalog.json`)

Configuration JSON définissant les règles d'alerte pour chaque service.

**Structure**:
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

## Services Monitorés

### 1. Hate Comment Detection

**Service**: `hate_comment`  
**Modèle**: `bert-multilingual`

**Métriques**:
| Métrique | Type | Seuil | Description |
|----------|------|-------|-------------|
| `latency` | int (ms) | > 500 | Temps de réponse |
| `confidence` | float (0-1) | < 0.70 | Confiance de prédiction |
| `precision` | float (0-1) | < 0.80 | Précision du modèle |
| `recall` | float (0-1) | < 0.85 | Rappel du modèle |
| `f1_score` | float (0-1) | < 0.88 | Score F1 |
| `false_positive_rate` | float (0-1) | > 0.10 | Taux de faux positifs |

**Alertes**:
- 🔴 **Critique**: Precision < 0.80, FPR > 0.10
- 🟠 **Haute**: Recall < 0.85
- 🟡 **Moyenne**: Latency > 500ms, F1 < 0.88

### 2. Depression Detection

**Service**: `depression_detection` / `llm_detection`  
**Modèles**: `camembert-base`, `qwen2.5:1.5b`, `yansnet-llm` (✅ Tous avec monitoring intégré)

**Métriques**:
| Métrique | Type | Seuil | Description |
|----------|------|-------|-------------|
| `latency` | int (ms) | > 500 (CamemBERT)<br>> 3500 (Qwen) | Temps de réponse |
| `confidence` | float (0-1) | < 0.60 | Confiance de prédiction |
| `severity` | string | - | Niveau de sévérité |
| `is_depression` | bool | - | Résultat de détection |
| `ram_usage` | int (MB) | > 2048 (CamemBERT)<br>> 4096 (Qwen) | Utilisation mémoire |
| `precision` | float (0-1) | < 0.80 | Précision du modèle |
| `recall` | float (0-1) | < 0.85 | Rappel du modèle |

**Événements**:
- `detect_depression` : Prédiction réussie (CamemBERT, Qwen)
- `detect_depression_llm` : Prédiction réussie (YANSNET-LLM)
- `detect_depression_error` : Erreur lors de la prédiction (timeout, exception)
- `detect_depression_llm_error` : Erreur lors de la prédiction LLM

**Alertes**:
- 🔴 **Critique**: Precision < 0.80, Recall < 0.85, FNR > 0.10
- 🟠 **Haute**: FPR > 0.15, RAM > seuils
- 🟡 **Moyenne**: Latency > seuils, Confidence < 0.60

### 3. Content Generation

**Service**: `content_generation`  
**Modèles**: `llama3.2:3b`, `gpt-4o-mini`

**Métriques**:
| Métrique | Type | Seuil | Description |
|----------|------|-------|-------------|
| `latency` | int (ms) | > 30000 | Temps de génération |
| `tokens_generated` | int | - | Nombre de tokens |
| `inappropriate_content_rate` | float (0-1) | > 0.01 | Taux de contenu inapproprié |
| `ttr` | float (0-1) | < 0.40 | Type-Token Ratio (diversité) |
| `repetition_rate` | float (0-1) | > 0.10 | Taux de répétition |
| `ram_usage` | int (MB) | > 8192 | Utilisation mémoire |

**Alertes**:
- 🔴 **Critique**: Inappropriate content > 0.01
- 🟠 **Haute**: Failure rate > 0.05, Timeout > 0.03, RAM > 8GB
- 🟡 **Moyenne**: Latency > 30s

### 4. Image Captioning

**Service**: `image_captioning`  
**Modèle**: `blip-base` (✅ Monitoring intégré)

**Métriques**:
| Métrique | Type | Seuil | Description |
|----------|------|-------|-------------|
| `latency` | int (ms) | > 2000 | Temps de traitement |
| `is_sensitive` | bool | - | Contenu sensible détecté |
| `caption_length` | int | - | Nombre de mots dans la légende |
| `bleu_score` | float (0-1) | < 0.25 | Qualité de la légende |
| `keyword_coverage` | float (0-1) | < 0.75 | Couverture des mots-clés |
| `precision` | float (0-1) | < 0.85 | Précision |
| `recall` | float (0-1) | < 0.90 | Rappel |

**Événements**:
- `caption_image` : Analyse réussie (sensible ou sûr)
- `caption_image_error` : Erreur lors de l'analyse

**Alertes**:
- 🔴 **Critique**: FNR > 0.05
- 🟠 **Haute**: BLEU < 0.25
- 🟡 **Moyenne**: Latency > 2s, Precision/Recall

### 5. Recommendation System

**Service**: `recommendation`  
**Modèle**: `collaborative-filtering`

**Métriques**:
| Métrique | Type | Seuil | Description |
|----------|------|-------|-------------|
| `latency` | int (ms) | > 200 | Temps de réponse |
| `recommendations_count` | int | - | Nombre de recommandations |
| `cache_hit` | bool | - | Cache hit/miss |
| `cache_miss_rate` | float (0-1) | > 0.30 | Taux de cache miss |
| `avg_score` | float (0-1) | < 0.50 | Score moyen |
| `diversity` | float (0-1) | < 0.40 | Diversité |

**Alertes**:
- 🟡 **Moyenne**: Latency > 200ms, Avg score < 0.50
- 🟢 **Faible**: Cache miss > 0.30, Diversity < 0.40

### 6. NSFW Detection

**Service**: `nsfw_detection`  
**Modèle**: `nsfw-classifier`

**Métriques**:
| Métrique | Type | Seuil | Description |
|----------|------|-------|-------------|
| `latency` | int (ms) | > 500 | Temps de réponse |
| `confidence` | float (0-1) | < 0.70 | Confiance |
| `is_nsfw` | bool | - | Résultat de détection |
| `category` | string | - | Catégorie (safe/suggestive/explicit) |
| `false_negative_rate` | float (0-1) | > 0.05 | Taux de faux négatifs |

**Alertes**:
- 🔴 **Critique**: FNR > 0.05 (contenu NSFW non détecté)
- 🟠 **Haute**: Confidence < 0.70
- 🟡 **Moyenne**: Latency > 500ms

### 7. API Gateway

**Service**: `api_gateway`

**Métriques**:
| Métrique | Type | Seuil | Description |
|----------|------|-------|-------------|
| `latency` | int (ms) | > 5000 | Latence globale |
| `status_code` | int | - | Code HTTP |
| `path` | string | - | Endpoint appelé |
| `method` | string | - | Méthode HTTP |
| `error_rate` | float (0-1) | > 0.05 | Taux d'erreur |

**Alertes**:
- 🔴 **Critique**: Error rate > 0.05
- 🟠 **Haute**: Latency > 5s

## Configuration

### Variables d'Environnement

```bash
# Monitoring
BRIDGE_URL=http://ga4-bridge:5000/log_metric
ENABLE_METRICS=true
CLIENT_ID=etsia_ml_api_v2
METRICS_TIMEOUT=0.5

# Google Analytics 4
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=your_api_secret_here
```

### Docker Compose

```yaml
services:
  ga4-bridge:
    build: ./ga4_bridge
    ports:
      - "5000:5000"
    volumes:
      - ./metrics_catalog.json:/app/metrics_catalog.json
    environment:
      - GA4_MEASUREMENT_ID=${GA4_MEASUREMENT_ID}
      - GA4_API_SECRET=${GA4_API_SECRET}
    networks:
      - api-network

  api:
    depends_on:
      ga4-bridge:
        condition: service_started
    environment:
      - BRIDGE_URL=http://ga4-bridge:5000/log_metric
      - ENABLE_METRICS=true
    networks:
      - api-network
```

## Démarrage

### 1. Configuration

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env et ajouter vos credentials GA4
nano .env
```

### 2. Démarrage des services

```bash
# Démarrer tous les services
docker-compose --profile ml up -d

# Vérifier les services
docker-compose ps

# Vérifier les logs
docker-compose logs -f ga4-bridge
docker-compose logs -f api
```

### 3. Tests

```bash
# Test du bridge
curl http://localhost:5000/health

# Test de l'API
curl http://localhost:8001/health

# Test complet
python scripts/test_monitoring_integration.py
```

## Utilisation

### Consulter les Métriques

1. **Google Analytics 4**:
   - Aller sur https://analytics.google.com
   - Sélectionner votre propriété
   - Rapports > Événements
   - Filtrer par `event_name`

2. **Logs du Bridge**:
   ```bash
   docker-compose logs -f ga4-bridge
   ```

3. **Logs de l'API**:
   ```bash
   docker-compose logs -f api
   ```

### Ajouter une Nouvelle Règle d'Alerte

1. Éditer `metrics_catalog.json`:
   ```json
   {
     "service": "mon_service",
     "metric": "ma_metrique",
     "threshold": 100,
     "operator": ">",
     "priority": "Haute",
     "description": "Description de l'alerte"
   }
   ```

2. Redémarrer le bridge:
   ```bash
   docker-compose restart ga4-bridge
   ```

### Intégrer un Nouveau Modèle

Voir [MONITORING_INTEGRATION.md](./MONITORING_INTEGRATION.md) pour le guide complet.

## Dépannage

### Le monitoring ne fonctionne pas

```bash
# 1. Vérifier que le bridge est démarré
docker-compose ps ga4-bridge

# 2. Vérifier les logs
docker-compose logs ga4-bridge

# 3. Tester la connexion
curl http://localhost:5000/health

# 4. Vérifier les variables d'environnement
docker-compose exec api env | grep BRIDGE
```

### Les alertes ne se déclenchent pas

```bash
# 1. Vérifier le catalogue
cat metrics_catalog.json | jq

# 2. Tester manuellement
curl -X POST http://localhost:5000/log_metric \
  -H "Content-Type: application/json" \
  -d '{
    "service": "hate_comment",
    "event_name": "detect_hate",
    "model_name": "bert-multilingual",
    "params": {"latency": 600},
    "client_id": "test"
  }'

# 3. Vérifier les logs du bridge
docker-compose logs ga4-bridge | grep ALERTE
```

### Latence élevée de l'API

```bash
# 1. Augmenter le timeout
export METRICS_TIMEOUT=1.0

# 2. Ou désactiver temporairement
export ENABLE_METRICS=false

# 3. Redémarrer l'API
docker-compose restart api
```

## Métriques Avancées

### Calcul de Métriques Personnalisées

```python
def calculate_custom_metrics(result):
    """Calcule des métriques personnalisées"""
    return {
        "custom_score": result.get("score", 0) * 100,
        "quality_index": (
            result.get("precision", 0) * 0.5 +
            result.get("recall", 0) * 0.5
        )
    }

emit_metric(
    service="mon_service",
    event_name="predict",
    model_name="mon-modele",
    params={
        "latency": latency_ms,
        **calculate_custom_metrics(result)
    }
)
```

### Monitoring Batch

```python
def batch_predict_with_monitoring(texts):
    start_time = time.time()
    results = []
    errors = 0
    
    for text in texts:
        try:
            result = predict(text)
            results.append(result)
        except Exception as e:
            errors += 1
    
    # Émettre métriques batch
    emit_metric(
        service="mon_service",
        event_name="batch_predict",
        model_name="mon-modele",
        params={
            "latency": int((time.time() - start_time) * 1000),
            "batch_size": len(texts),
            "success_count": len(results),
            "error_count": errors,
            "error_rate": errors / len(texts) if texts else 0
        }
    )
    
    return results
```

## Ressources

- [Guide d'Intégration](./MONITORING_INTEGRATION.md)
- [Documentation GA4](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [Code Source GA4-Bridge](../ga4_bridge/)
- [Client de Monitoring](../app/core/monitoring/)
- [Script de Test](../scripts/test_monitoring_integration.py)

## Support

Pour toute question ou problème :
1. Consulter la documentation
2. Vérifier les logs
3. Exécuter le script de test
4. Contacter l'équipe ETSIA
