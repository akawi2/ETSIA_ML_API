# Système de Recommandation avec Cache Redis

## Vue d'ensemble

Ce module implémente un système de recommandation de posts avec un système de cache Redis pour améliorer les performances.

## Architecture

```
recommendation/
├── __init__.py
├── README.md                    # Ce fichier
├── recommendation_model.py      # Modèle principal (interface BaseMLModel)
├── recommendation_service.py    # Service de recommandation avec cache
├── cache_service.py            # Service de cache Redis
└── db_service.py               # Service de base de données PostgreSQL
```

## Composants

### 1. RecommendationModel
Classe principale qui implémente l'interface `BaseMLModel`. C'est le point d'entrée pour le système de recommandation.

**Utilisation :**
```python
from app.services.recommendation.recommendation_model import RecommendationModel

model = RecommendationModel(
    db_config={'host': 'localhost', 'database': 'etsia_ai', ...},
    redis_config={'host': 'localhost', 'port': 6379, ...},
    use_cache=True
)

# Générer des recommandations
result = model.predict(user_id=1, top_n=10)
```

### 2. UserUserRecommender
Implémente l'algorithme de filtrage collaboratif user-user avec support du cache.

**Fonctionnalités :**
- Chargement intelligent des données (cache → DB)
- Calcul de similarité entre utilisateurs
- Génération de recommandations personnalisées
- Rafraîchissement du cache

### 3. PostCacheService
Gère le cache Redis pour les posts.

**Fonctionnalités :**
- Stockage/récupération des posts
- Gestion du TTL (Time To Live)
- Invalidation du cache
- Mise à jour incrémentale
- Statistiques du cache

### 4. PostDatabaseService
Gère l'accès à la base de données PostgreSQL.

**Fonctionnalités :**
- Récupération de tous les posts
- Requêtes par IDs
- Détection des posts modifiés
- Détection des posts supprimés

## Installation

### Prérequis

1. **Redis** (pour le cache)
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Windows (Docker)
docker run -d -p 6379:6379 redis:latest
```

2. **PostgreSQL** (pour les données)
```bash
# Ubuntu/Debian
sudo apt install postgresql

# macOS
brew install postgresql
```

### Dépendances Python

```bash
pip install redis psycopg2-binary pandas numpy
```

## Configuration

### Variables d'environnement

Créer/modifier `.env` :

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_TTL=3600
ENABLE_CACHE=True

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=etsia
POSTGRES_PASSWORD=your_password
POSTGRES_DB=etsia_ai
```

### Configuration dans le code

```python
from app.config import settings

# Configuration Redis
redis_config = {
    'host': settings.REDIS_HOST,
    'port': settings.REDIS_PORT,
    'db': settings.REDIS_DB,
    'ttl': settings.REDIS_CACHE_TTL
}

# Configuration PostgreSQL
db_config = {
    'host': settings.POSTGRES_HOST,
    'port': settings.POSTGRES_PORT,
    'user': settings.POSTGRES_USER,
    'password': settings.POSTGRES_PASSWORD,
    'database': settings.POSTGRES_DB
}
```

## Utilisation

### Via l'API

#### 1. Obtenir des recommandations
```bash
curl -X POST http://localhost:8000/api/v1/recommendation/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "top_n": 10}'
```

#### 2. Statistiques du cache
```bash
curl http://localhost:8000/api/v1/recommendation/cache/stats
```

#### 3. Rafraîchir le cache
```bash
curl -X POST http://localhost:8000/api/v1/recommendation/cache/refresh
```

#### 4. Invalider le cache
```bash
curl -X DELETE http://localhost:8000/api/v1/recommendation/cache/invalidate
```

### Via le code Python

```python
from app.services.recommendation.recommendation_service import UserUserRecommender

# Créer le recommender
recommender = UserUserRecommender(
    min_similarity=0.1,
    db_config={...},
    redis_config={...},
    use_cache=True
)

# Charger les données (depuis cache ou DB)
recommender.load_and_train()

# Générer des recommandations
recommendations = recommender.recommend_posts(
    user_id=1,
    available_posts=[1, 2, 3, 4, 5],
    top_n=10
)

# Rafraîchir le cache
recommender.refresh_cache()

# Obtenir les stats
stats = recommender.get_cache_stats()
```

## Schéma de base de données

Le service s'attend à une table `posts` avec la structure suivante :

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0
);

-- Index pour les performances
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_posts_updated_at ON posts(updated_at);
CREATE INDEX idx_posts_deleted_at ON posts(deleted_at);
```

## Performance

### Benchmarks

**Sans cache (requête DB directe) :**
- Temps de réponse : 200-500ms
- Charge DB : Élevée

**Avec cache (Redis) :**
- Temps de réponse : 10-50ms
- Charge DB : Minimale
- **Amélioration : 10-50x plus rapide**

### Optimisations

1. **TTL adaptatif** : Ajuster selon la fréquence de mise à jour
2. **Compression** : Compresser les données JSON
3. **Partitionnement** : Cacher par catégories
4. **Pré-calcul** : Cacher aussi les recommandations

## Tests

### Script de test automatique

```bash
python examples/test_cache_system.py
```

Ce script teste :
- Statistiques du cache
- Performance avec/sans cache
- Rafraîchissement
- Invalidation
- Recommandations batch

### Tests unitaires

```bash
pytest tests/test_recommendation_cache.py -v
```

## Monitoring

### Logs

Le système log automatiquement :
- Cache HIT/MISS
- Nombre de posts chargés
- Erreurs de connexion
- Temps de traitement

**Exemple :**
```
INFO: ✓ Cache Redis initialisé (localhost:6379)
INFO: Cache MISS: posts non trouvés
INFO: ✓ 1500 posts récupérés depuis la DB
INFO: ✓ Cache SET: 1500 posts stockés (TTL: 3600s)
INFO: ✓ Cache HIT: 1500 posts récupérés
```

### Métriques

Vérifier les statistiques :
```bash
curl http://localhost:8000/api/v1/recommendation/cache/stats
```

## Troubleshooting

### Redis non disponible
**Symptôme :** `⚠️ Redis non disponible: ... Mode sans cache activé.`

**Solution :**
1. Vérifier que Redis est démarré : `redis-cli ping`
2. Vérifier la configuration dans `.env`
3. Le système fonctionne en mode dégradé (sans cache)

### Cache corrompu
**Symptôme :** Données incorrectes ou erreurs de désérialisation

**Solution :**
```bash
curl -X DELETE http://localhost:8000/api/v1/recommendation/cache/invalidate
```

### Données obsolètes
**Symptôme :** Recommandations basées sur d'anciennes données

**Solution :**
```bash
curl -X POST http://localhost:8000/api/v1/recommendation/cache/refresh
```

### Connexion DB échouée
**Symptôme :** `Erreur connexion DB: ...`

**Solution :**
1. Vérifier PostgreSQL : `psql -U etsia -d etsia_ai`
2. Vérifier les credentials dans `.env`
3. Le système utilise des données de test en fallback

## Sécurité

### Recommandations

1. **Authentification Redis**
```bash
# redis.conf
requirepass your_strong_password
```

2. **Isolation réseau**
```bash
# redis.conf
bind 127.0.0.1
```

3. **Chiffrement TLS** en production

4. **DB séparées par environnement**
- Dev : DB 0
- Staging : DB 1
- Production : DB 2

## Évolutions futures

- [ ] Cache des recommandations par utilisateur
- [ ] Webhooks pour mise à jour en temps réel
- [ ] Clustering Redis pour haute disponibilité
- [ ] Métriques avancées (hit rate, latence)
- [ ] Cache warming au démarrage
- [ ] Algorithme de recommandation plus sophistiqué
- [ ] Support de filtres (catégories, tags, etc.)

## Support

Pour plus d'informations, consulter :
- [Documentation complète](../../../docs/CACHE_SYSTEM.md)
- [Script de test](../../../examples/test_cache_system.py)
- [API Documentation](http://localhost:8000/docs)
