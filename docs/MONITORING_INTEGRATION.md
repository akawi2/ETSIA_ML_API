# Guide d'Intégration du Monitoring

Ce guide explique comment intégrer le système de monitoring GA4-Bridge dans vos modèles ML.

## Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│   ML API        │─────▶│  GA4-Bridge  │─────▶│  Google     │
│   (Port 8001)   │      │  (Port 5000) │      │  Analytics  │
│                 │      │              │      │     4       │
│  • HateComment  │      │  • Évalue    │      │             │
│  • Depression   │      │    alertes   │      │  Dashboard  │
│  • Content Gen  │      │  • Enrichit  │      │  & Alertes  │
│  • Image Cap    │      │    métriques │      │             │
│  • Recommend    │      │              │      │             │
└─────────────────┘      └──────────────┘      └─────────────┘
```

## Configuration Docker

### 1. Variables d'environnement

Ajoutez dans votre `.env` :

```bash
# Monitoring GA4-Bridge
BRIDGE_URL=http://ga4-bridge:5000/log_metric
ENABLE_METRICS=true
CLIENT_ID=etsia_ml_api_v2
METRICS_TIMEOUT=0.5

# Google Analytics 4
GA4_MEASUREMENT_ID=G-XXXXXXXXXX
GA4_API_SECRET=your_api_secret_here
```

### 2. Docker Compose

Le service `api` doit dépendre de `ga4-bridge` :

```yaml
api:
  depends_on:
    ga4-bridge:
      condition: service_started
  environment:
    - BRIDGE_URL=http://ga4-bridge:5000/log_metric
    - ENABLE_METRICS=true
```

## Intégration dans un Modèle

### Méthode 1 : Import Direct (Recommandé)

```python
from app.core.monitoring import emit_metric
import time

class MonModele(BaseMLModel):
    def predict(self, text: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Votre logique de prédiction
            result = self._do_prediction(text)
            
            # Calculer la latence
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Émettre les métriques
            emit_metric(
                service="mon_service",           # Nom du service
                event_name="predict",            # Nom de l'événement
                model_name="mon-modele-v1",      # Nom du modèle
                params={
                    "latency": latency_ms,       # Latence en ms
                    "confidence": result["confidence"],
                    "custom_metric": result["score"]
                }
            )
            
            return result
            
        except Exception as e:
            # Émettre métrique d'erreur
            latency_ms = int((time.time() - start_time) * 1000)
            emit_metric(
                service="mon_service",
                event_name="predict_error",
                model_name="mon-modele-v1",
                params={
                    "latency": latency_ms,
                    "error": str(e)[:100]
                }
            )
            raise
```

### Méthode 2 : Décorateur (Pour fonctions simples)

```python
from app.core.monitoring import monitor_prediction

class MonModele(BaseMLModel):
    @monitor_prediction(
        service="mon_service",
        event_name="predict",
        model_name="mon-modele-v1",
        extract_metrics=lambda result: {
            "confidence": result.get("confidence", 0),
            "score": result.get("score", 0)
        }
    )
    def predict(self, text: str) -> Dict[str, Any]:
        # Votre logique de prédiction
        return {"confidence": 0.95, "score": 0.87}
```

## Services et Métriques par Modèle

### 0. API Gateway (Global)

**Service**: `api_gateway`  
**Event**: `api_request`  
**Model**: N/A

**Métriques**:
```python
{
    "latency": 450,              # ms (alerte si > 5000ms)
    "error_rate": 0.02,          # 0-1 (alerte si > 0.05, CRITIQUE)
    "path": "/api/v1/predict",   # endpoint path
    "method": "POST",            # HTTP method
    "status_code": 200           # HTTP status
}
```

### 1. Hate Comment Detection

**Service**: `hate_comment`  
**Event**: `detect_hate`  
**Model**: `bert-multilingual`

**Métriques**:
```python
{
    "latency": 250,              # ms (alerte si > 500ms)
    "confidence": 0.85,          # 0-1 (alerte si < 0.70)
    "is_hateful": True,          # bool
    "precision": 0.82,           # 0-1 (si disponible)
    "recall": 0.86,              # 0-1 (si disponible)
    "f1_score": 0.84,            # 0-1 (si disponible)
    "false_positive_rate": 0.12  # 0-1 (si disponible)
}
```

### 2. Depression Detection

**Service**: `depression_detection`  
**Event**: `detect_depression`  
**Models**: `camembert-base`, `qwen2.5:1.5b`

**Métriques**:
```python
{
    "latency": 450,              # ms
    "confidence": 0.78,          # 0-1
    "severity": "Moyenne",       # Critique/Élevée/Moyenne/Faible
    "ram_usage": 1800,           # MB
    "precision": 0.80,           # 0-1 (si disponible)
    "recall": 0.85               # 0-1 (si disponible)
}
```

### 3. Content Generation

**Service**: `content_generation`  
**Event**: `generate_content`  
**Models**: `llama3.2:3b`, `gpt-4o-mini`

**Métriques**:
```python
{
    "latency": 15000,                    # ms
    "tokens_generated": 250,             # count
    "inappropriate_content_rate": 0.005, # 0-1
    "ttr": 0.45,                         # Type-Token Ratio
    "repetition_rate": 0.08,             # 0-1
    "ram_usage": 6000                    # MB
}
```

### 4. Image Captioning

**Service**: `image_captioning`  
**Event**: `caption_image`, `caption_image_error`  
**Model**: `blip-base`

**Métriques**:
```python
{
    "latency": 1200,             # ms
    "is_sensitive": False,       # bool - contenu sensible détecté
    "caption_length": 8,         # int - nombre de mots dans la légende
    "bleu_score": 0.35,          # 0-1 (optionnel)
    "keyword_coverage": 0.80,    # 0-1 (optionnel)
    "precision": 0.85,           # 0-1 (si disponible)
    "recall": 0.90               # 0-1 (si disponible)
}
```

### 5. Recommendation System

**Service**: `recommendation`  
**Event**: `generate_recommendations`  
**Model**: `collaborative-filtering`

**Métriques**:
```python
{
    "latency": 80,               # ms (alerte si > 200ms)
    "recommendations_count": 10, # count
    "cache_hit": True,           # bool
    "cache_miss_rate": 0.15,     # 0-1 (alerte si > 0.30)
    "avg_score": 0.75,           # 0-1 (alerte si < 0.50)
    "diversity": 0.65            # 0-1 (alerte si < 0.40)
}
```

### 6. NSFW Detection

**Service**: `nsfw_detection`  
**Event**: `detect_nsfw`  
**Model**: `nsfw-classifier`

**Métriques**:
```python
{
    "latency": 300,              # ms (alerte si > 500ms)
    "is_nsfw": False,            # bool
    "confidence": 0.92,          # 0-1 (alerte si < 0.70)
    "category": "safe",          # safe/suggestive/explicit
    "false_negative_rate": 0.02  # 0-1 (alerte si > 0.05, CRITIQUE)
}
```

## Configuration des Alertes

Les seuils d'alerte sont définis dans `metrics_catalog.json` :

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

### Résumé des Alertes Configurées

#### Depression Detection
- **Latence > 1000ms** (Moyenne) - Temps de réponse lent
- **Confidence < 0.60** (Haute) - Confiance faible

#### Hate Comment Detection
- **Latence > 500ms** (Moyenne) - Temps de réponse lent
- **Confidence < 0.70** (Moyenne) - Confiance faible
- **False Positive Rate > 0.10** (Haute) - Taux de faux positifs élevé

#### Image Captioning
- **Precision < 0.85** (Moyenne) - Précision faible
- **Latence > 2000ms** (Moyenne) - Temps de réponse lent
- **BLEU Score < 0.25** (Faible) - Qualité des captions faible
- **Keyword Coverage < 0.70** (Faible) - Couverture des mots-clés faible

#### Content Generation
- **Latence > 30000ms** (Moyenne) - Temps de réponse lent
- **Inappropriate Content Rate > 0.01** (Critique) - Contenu inapproprié détecté
- **TTR < 0.40** (Faible) - Diversité lexicale faible
- **Repetition Rate > 0.15** (Faible) - Répétitions excessives

#### Recommendation System
- **Latence > 200ms** (Moyenne) - Temps de réponse lent
- **Cache Miss Rate > 0.30** (Faible) - Taux de cache miss élevé
- **Avg Score < 0.50** (Moyenne) - Qualité des recommandations faible
- **Diversity < 0.40** (Faible) - Diversité des recommandations faible

#### NSFW Detection
- **Latence > 500ms** (Moyenne) - Temps de réponse lent
- **Confidence < 0.70** (Haute) - Confiance faible (risque de faux négatifs)
- **False Negative Rate > 0.05** (Critique) - Faux négatifs élevés (contenu NSFW non détecté)

#### API Gateway (Global)
- **Latence > 5000ms** (Haute) - Latence API globale élevée
- **Error Rate > 0.05** (Critique) - Taux d'erreur API élevé

### Opérateurs disponibles

- `>` : Supérieur à
- `<` : Inférieur à
- `>=` : Supérieur ou égal à
- `<=` : Inférieur ou égal à

### Priorités

- `Critique` : Problème majeur nécessitant une action immédiate
- `Haute` : Problème important à traiter rapidement
- `Moyenne` : Problème à surveiller
- `Faible` : Information, pas d'action requise

## Exemples d'Intégration Complète

### Exemple 1 : CamemBERT Depression

```python
from app.core.monitoring import emit_metric
import time

class CamemBERTDepressionModel(BaseMLModel):
    def predict(self, text: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Prédiction
            result = self._run_inference(text)
            
            # Métriques
            latency_ms = int((time.time() - start_time) * 1000)
            
            emit_metric(
                service="depression_detection",
                event_name="detect_depression",
                model_name="camembert-base",
                params={
                    "latency": latency_ms,
                    "confidence": result["confidence"],
                    "severity": result["severity"],
                    "ram_usage": self._get_ram_usage()
                }
            )
            
            return result
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            emit_metric(
                service="depression_detection",
                event_name="detect_depression_error",
                model_name="camembert-base",
                params={"latency": latency_ms, "error": str(e)[:100]}
            )
            raise
```

### Exemple 2 : Image Captioning

```python
from app.core.monitoring import emit_metric
import time

class SensitiveImageCaptionModel(BaseMLModel):
    def predict(self, image=None, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Génération de la légende
            caption_en = self._generate_caption(image)
            
            # Détection de contenu sensible
            is_sensitive = self._detect_sensitive_content(caption_en)
            
            # Calculer la latence
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Émettre les métriques
            emit_metric(
                service="image_captioning",
                event_name="caption_image",
                model_name="blip-base",
                params={
                    "latency": latency_ms,
                    "is_sensitive": is_sensitive,
                    "caption_length": len(caption_en.split())
                }
            )
            
            return {
                "prediction": "SENSIBLE" if is_sensitive else "SÛR",
                "caption_en": caption_en,
                "is_safe": not is_sensitive
            }
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            emit_metric(
                service="image_captioning",
                event_name="caption_image_error",
                model_name="blip-base",
                params={
                    "latency": latency_ms,
                    "error": str(e)[:100]
                }
            )
            raise
```

### Exemple 3 : Content Generator

```python
from app.core.monitoring import emit_metric
import time

class YansnetContentGeneratorModel(BaseMLModel):
    def generate(self, prompt: str, max_tokens: int = 200) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Génération
            content = self._generate_content(prompt, max_tokens)
            
            # Analyse du contenu
            ttr = self._calculate_ttr(content)
            repetition_rate = self._calculate_repetition(content)
            
            # Métriques
            latency_ms = int((time.time() - start_time) * 1000)
            
            emit_metric(
                service="content_generation",
                event_name="generate_content",
                model_name=self.model_name,
                params={
                    "latency": latency_ms,
                    "tokens_generated": len(content.split()),
                    "ttr": ttr,
                    "repetition_rate": repetition_rate,
                    "ram_usage": self._get_ram_usage()
                }
            )
            
            return {"content": content, "ttr": ttr}
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            emit_metric(
                service="content_generation",
                event_name="generate_content_error",
                model_name=self.model_name,
                params={"latency": latency_ms, "error": str(e)[:100]}
            )
            raise
```

## Tests

### Test local (sans Docker)

```python
# Désactiver le monitoring pour les tests locaux
import os
os.environ["ENABLE_METRICS"] = "false"

# Ou pointer vers un bridge local
os.environ["BRIDGE_URL"] = "http://localhost:5000/log_metric"
```

### Test avec Docker

```bash
# Démarrer tous les services
docker-compose --profile ml up -d

# Vérifier le health du bridge
curl http://localhost:5000/health

# Tester un endpoint
curl -X POST http://localhost:8001/api/v1/hatecomment/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Test de monitoring"}'

# Voir les logs du bridge
docker-compose logs -f ga4-bridge
```

## Bonnes Pratiques

1. **Toujours mesurer la latence** : C'est la métrique la plus importante
2. **Timeout court** : Le monitoring ne doit pas ralentir l'API (0.5s max)
3. **Métriques pertinentes** : N'envoyez que les métriques utiles pour les alertes
4. **Gestion d'erreurs** : Toujours émettre une métrique en cas d'erreur
5. **Noms cohérents** : Utilisez les noms de services définis dans le catalog
6. **Valeurs numériques** : Les seuils fonctionnent mieux avec des nombres

## Dépannage

### Le monitoring ne fonctionne pas

1. Vérifier que `ENABLE_METRICS=true`
2. Vérifier que le GA4-Bridge est démarré : `docker-compose ps`
3. Vérifier les logs : `docker-compose logs ga4-bridge`
4. Tester la connexion : `curl http://localhost:5000/health`

### Les alertes ne se déclenchent pas

1. Vérifier `metrics_catalog.json`
2. Vérifier que les noms de service correspondent
3. Vérifier que les métriques sont bien envoyées (logs du bridge)
4. Vérifier les seuils et opérateurs

### Latence élevée de l'API

1. Augmenter le timeout : `METRICS_TIMEOUT=1.0`
2. Ou désactiver temporairement : `ENABLE_METRICS=false`
3. Vérifier que le bridge répond rapidement

## Ressources

- [Documentation GA4 Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [Metrics Catalog](../metrics_catalog.json)
- [GA4 Bridge Source](../ga4_bridge/main.py)
- [Monitoring Client](../app/core/monitoring/client.py)
