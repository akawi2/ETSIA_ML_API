# Yansnet - Monitoring ML avec Google Analytics 4

Système de monitoring temps réel pour modèles ML (détection de haine, dépression, génération de contenu, captioning). L'architecture découplée permet d'évaluer des seuils d'alerte avant transmission vers GA4.

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│ FastAPI App │────▶│   GA4-Bridge    │────▶│     GA4     │
│  (8000)     │     │    (5000)       │     │  Dashboard  │
└─────────────┘     └─────────────────┘     └─────────────┘
                           │
                    metrics_catalog.json
                    (règles d'alertes)
```

## Démarrage rapide

```bash
# 1. Configurer les credentials GA4
echo "GA4_MEASUREMENT_ID=G-XXXXXXXXXX" > .env
echo "GA4_API_SECRET=VotreSecret" >> .env

# 2. Lancer les services
docker-compose --env-file .env up --build -d

# 3. Vérifier
curl http://localhost:5000/health  # Bridge
curl http://localhost:8000/health  # API
```

## Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/predict_hatecomment` | POST | Détection commentaires haineux |
| `/predict_depression` | POST | Détection dépression (param: `model_type=camembert\|qwen`) |
| `/generate_content` | POST | Génération de contenu |
| `/caption_image` | POST | Captioning d'image |
| `/api/v1/models` | GET | Liste des modèles |
| `/health` | GET | Health check |

## Ajouter une nouvelle métrique (Guide Data)

### Étape 1 : Émettre la métrique (FastAPI App)

Dans `fastapi_app/app/main.py`, utiliser `emit_metric()` :

```python
emit_metric(
    service="mon_service",        # Identifiant du service
    event_name="mon_event",       # Nom de l'événement GA4
    model="nom-du-modele",        # Optionnel
    params={
        "latency": 150,           # Métriques numériques
        "ma_nouvelle_metrique": 0.85,
        "status": "success"       # Ou textuelles
    }
)
```

### Étape 2 : Configurer l'alerte (metrics_catalog.json)

Ajouter une règle dans `metrics_catalog.json` :

```json
{
  "service": "mon_service",
  "model": "nom-du-modele",       // Optionnel: filtre par modèle
  "metric": "ma_nouvelle_metrique",
  "threshold": 0.80,
  "operator": "<",                // Opérateurs: >, <, >=, <=
  "priority": "Haute",            // Critique, Haute, Moyenne, Faible
  "description": "Alerte si métrique < 80%"
}
```

Puis redémarrer le bridge :
```bash
docker-compose restart ga4-bridge
```

### Étape 3 : Déclarer dans GA4

Dans GA4 Admin > Définitions personnalisées :

**Dimensions** (texte) :
| Nom | Paramètre |
|-----|-----------|
| Service Name | `service` |
| Model Name | `model_name` |
| Alert Triggered | `alert_triggered` |
| Alert Reason | `alert_reason` |
| Alert Priority | `alert_priority` |

**Métriques** (numériques) :
| Nom | Paramètre | Unité |
|-----|-----------|-------|
| Latency | `latency` | ms |
| Confidence | `confidence` | Standard |
| Ma Nouvelle Métrique | `ma_nouvelle_metrique` | Standard |

## Structure du catalogue d'alertes

Le fichier `metrics_catalog.json` définit les règles d'évaluation :

```json
{
  "service": "string",      // Requis: nom du service
  "model": "string",        // Optionnel: filtre par modèle spécifique
  "metric": "string",       // Requis: clé de la métrique dans params
  "threshold": number,      // Requis: valeur seuil
  "operator": ">" | "<" | ">=" | "<=",  // Requis
  "priority": "Critique" | "Haute" | "Moyenne" | "Faible",
  "description": "string"   // Documentation
}
```

Quand une alerte est déclenchée, l'événement est enrichi avec :
- `alert_triggered: "true"`
- `alert_reason: "{metric}_fail"`
- `alert_priority: "{priority}"`

## Schéma d'un événement métrique

```python
MetricEvent(
    service="depression_detection",  # Requis
    event_name="detect_depression",  # Requis: nom event GA4
    model_name="camembert-base",     # Optionnel (défaut: "default")
    client_id="yansnet_prod_v1",     # Identifiant GA4
    params={...}                     # Dict de métriques
)
```

## Services et métriques existants

| Service | Métriques surveillées |
|---------|----------------------|
| `hate_comment` | latency, precision, recall, f1_score, false_positive_rate |
| `depression_detection` | latency, confidence, ram_usage, precision, recall |
| `content_generation` | latency, inappropriate_content_rate, failure_rate, ttr |
| `image_captioning` | latency, bleu_score, precision, recall |
| `api_gateway` | latency, status_code (middleware global) |

## Commandes utiles

```bash
# Rebuild complet
docker-compose --env-file .env up --build -d

# Logs en temps réel
docker-compose logs -f ga4-bridge

# Redémarrer après modif du catalogue
docker-compose restart ga4-bridge

# Test rapide
curl -X POST http://localhost:8000/predict_hatecomment
curl -X POST "http://localhost:8000/predict_depression?model_type=qwen"
```

## Structure du projet

```
├── fastapi_app/           # API métier (port 8000)
│   └── app/main.py        # Endpoints + emit_metric()
├── ga4_bridge/            # Middleware monitoring (port 5000)
│   ├── main.py            # Évaluation alertes + envoi GA4
│   └── schemas.py         # Modèle MetricEvent
├── scripts/
│   └── send_sample_events.py
├── metrics_catalog.json   # Règles d'alertes (volume monté)
├── docker-compose.yml
└── .env                   # GA4_MEASUREMENT_ID, GA4_API_SECRET
```
