# Yansnet - Monitoring ML avec Supabase

Système de monitoring temps réel pour modèles ML (détection de haine, dépression, génération de contenu, captioning). L'architecture découplée permet d'évaluer des seuils d'alerte via Supabase Edge Functions.

## Architecture

```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────┐
│ FastAPI App │────▶│  Supabase Edge Fn   │────▶│  Supabase   │
│  (8000)     │     │  (evaluate-alerts)  │     │  Database   │
└─────────────┘     └─────────────────────┘     └─────────────┘
                              │
                       alert_rules table
                     (règles d'alertes)
```

## Démarrage rapide

```bash
# 1. Configurer les credentials Supabase
echo "SUPABASE_URL=https://your-project.supabase.co" > .env
echo "SUPABASE_ANON_KEY=your-anon-key" >> .env

# 2. Lancer les services
docker-compose --env-file .env up --build -d

# 3. Vérifier
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
    event_name="mon_event",       # Nom de l'événement
    model="nom-du-modele",        # Optionnel (défaut: "default")
    params={
        "latency": 150,           # Métriques numériques
        "ma_nouvelle_metrique": 0.85,
        "status": "success"       # Ou textuelles
    }
)
```

### Étape 2 : Configurer l'alerte (Supabase)

Ajouter une règle dans la table `alert_rules` via migration SQL :

```sql
INSERT INTO alert_rules (service, model, metric, threshold, operator, priority, description) 
VALUES ('mon_service', 'nom-du-modele', 'ma_nouvelle_metrique', 0.80, '<', 'Haute', 'Alerte si métrique < 80%');
```

Ou via le dashboard Supabase dans la table `alert_rules`.

## Structure des règles d'alertes

La table `alert_rules` dans Supabase définit les règles d'évaluation :

| Colonne | Type | Description |
|---------|------|-------------|
| `service` | string | Requis: nom du service |
| `model` | string | Optionnel: filtre par modèle spécifique |
| `metric` | string | Requis: clé de la métrique dans params |
| `threshold` | number | Requis: valeur seuil |
| `operator` | string | Requis: `>`, `<`, `>=`, `<=` |
| `priority` | string | Critique, Haute, Moyenne, Faible |
| `description` | string | Documentation |

Quand une alerte est déclenchée, elle est enregistrée dans la table `alerts` avec :
- `metric_value`: valeur mesurée
- `threshold`: seuil franchi
- `reason`: `{metric}_fail`
- `priority`: niveau de priorité

## Schéma d'un événement métrique

```python
# Payload envoyé à Supabase Edge Function
{
    "service": "depression_detection",  # Requis
    "event_name": "detect_depression",  # Requis
    "model_name": "camembert-base",     # Optionnel (défaut: "default")
    "client_id": "yansnet_prod_v1",     # Identifiant client
    "params": {...}                     # Dict de métriques
}
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
docker-compose logs -f fastapi-app

# Test rapide
curl -X POST http://localhost:8000/predict_hatecomment
curl -X POST "http://localhost:8000/predict_depression?model_type=qwen"

# Envoyer des données de test vers Supabase
python scripts/send_test_data.py              # 50 événements par défaut
python scripts/send_test_data.py -n 100       # 100 événements
python scripts/send_test_data.py --single     # Un seul événement
python scripts/send_test_data.py --single --model qwen-depression  # Tester un modèle spécifique
```

## Structure du projet

```
├── fastapi_app/           # API métier (port 8000)
│   └── app/main.py        # Endpoints + emit_metric()
├── supabase/
│   ├── functions/
│   │   └── evaluate-alerts/  # Edge Function d'évaluation
│   └── migrations/           # Schéma DB + règles d'alertes
├── scripts/
│   ├── send_sample_events.py # Test GA4-Bridge
│   └── send_test_data.py     # Test Supabase Edge Function
├── docker-compose.yml
└── .env                   # SUPABASE_URL, SUPABASE_ANON_KEY
```
