# Système de Cache pour les Recommandations

## Vue d'ensemble

Le système de cache Redis a été implémenté pour améliorer significativement les performances du système de recommandation. Au lieu de requêter la base de données PostgreSQL à chaque demande de recommandation, les posts sont maintenant mis en cache dans Redis.

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Recommendation API Endpoint    │
│  /api/v1/recommendation/recommend│
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│  RecommendationModel    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  UserUserRecommender    │
└──────┬──────────────────┘
       │
       ├─────────────────┐
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Cache Service│  │  DB Service  │
│   (Redis)    │  │ (PostgreSQL) │
└──────────────┘  └──────────────┘
```

## Composants

### 1. PostCacheService (`cache_service.py`)

Service de gestion du cache Redis qui gère :
- **Stockage des posts** : Cache tous les posts avec TTL configurable
- **Récupération rapide** : Lecture depuis Redis (beaucoup plus rapide que PostgreSQL)
- **Invalidation** : Possibilité d'invalider le cache complet ou par post
- **Mise à jour incrémentale** : Mise à jour uniquement des posts modifiés
- **Métadonnées** : Suivi de la dernière mise à jour et statistiques

**Méthodes principales :**
- `get_all_posts()` : Récupère tous les posts depuis le cache
- `set_all_posts(posts)` : Stocke tous les posts dans le cache
- `invalidate_all()` : Invalide tout le cache
- `update_posts_incremental(new_posts, deleted_ids)` : Mise à jour incrémentale
- `get_cache_stats()` : Statistiques du cache

### 2. PostDatabaseService (`db_service.py`)

Service de gestion de la base de données PostgreSQL :
- **Récupération des posts** : Charge tous les posts depuis PostgreSQL
- **Requêtes optimisées** : Récupération par IDs, posts récents, etc.
- **Détection des changements** : Récupère les posts modifiés depuis une date
- **Fallback** : Données de test si la DB n'est pas disponible

**Méthodes principales :**
- `get_all_posts()` : Récupère tous les posts
- `get_posts_updated_since(datetime)` : Posts modifiés depuis une date
- `get_deleted_post_ids_since(datetime)` : IDs des posts supprimés
- `test_connection()` : Test de connexion DB

### 3. UserUserRecommender (mis à jour)

Le recommender a été amélioré pour utiliser le cache :
- **Chargement intelligent** : Essaie d'abord le cache, puis la DB
- **Mise en cache automatique** : Cache les données après chargement depuis la DB
- **Rafraîchissement** : Méthode pour forcer le rechargement depuis la DB

## Flux de données

### Premier appel (Cache MISS)
```
1. Client → API /recommend
2. API → RecommendationModel
3. RecommendationModel → UserUserRecommender
4. UserUserRecommender → Cache Service (get_all_posts)
5. Cache Service → MISS (pas de données)
6. UserUserRecommender → DB Service (get_all_posts)
7. DB Service → PostgreSQL
8. PostgreSQL → Retourne les posts
9. UserUserRecommender → Cache Service (set_all_posts)
10. Cache Service → Stocke dans Redis
11. UserUserRecommender → Génère recommandations
12. API → Retourne résultats au client
```

### Appels suivants (Cache HIT)
```
1. Client → API /recommend
2. API → RecommendationModel
3. RecommendationModel → UserUserRecommender
4. UserUserRecommender → Cache Service (get_all_posts)
5. Cache Service → HIT (données trouvées dans Redis)
6. UserUserRecommender → Génère recommandations
7. API → Retourne résultats au client
```

**Gain de performance** : Pas de requête PostgreSQL, lecture directe depuis Redis (10-100x plus rapide)

## Configuration

### Variables d'environnement (.env)

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_TTL=3600  # 1 heure en secondes
ENABLE_CACHE=True

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=etsia
POSTGRES_PASSWORD=your_password
POSTGRES_DB=etsia_ai
```

### Configuration dans le code

```python
from app.config import settings

redis_config = {
    'host': settings.REDIS_HOST,
    'port': settings.REDIS_PORT,
    'db': settings.REDIS_DB,
    'ttl': settings.REDIS_CACHE_TTL
}
```

## API Endpoints

### 1. Obtenir des recommandations
```bash
POST /api/v1/recommendation/recommend
Content-Type: application/json

{
  "user_id": 1,
  "top_n": 10
}
```

### 2. Statistiques du cache
```bash
GET /api/v1/recommendation/cache/stats
```

**Réponse :**
```json
{
  "status": "available",
  "redis_connected": true,
  "metadata": {
    "last_update": "2025-01-09T10:30:00",
    "total_posts": 1500,
    "ttl": 3600,
    "ttl_remaining": 2400
  },
  "individual_posts_cached": 1500,
  "cache_ttl": 3600
}
```

### 3. Rafraîchir le cache
```bash
POST /api/v1/recommendation/cache/refresh
```

Force le rechargement des posts depuis la base de données et met à jour le cache.

**Réponse :**
```json
{
  "success": true,
  "message": "Cache rafraîchi avec succès",
  "posts_cached": 1500
}
```

### 4. Invalider le cache
```bash
DELETE /api/v1/recommendation/cache/invalidate
```

Supprime toutes les données du cache. Le cache sera rechargé au prochain appel.

**Réponse :**
```json
{
  "success": true,
  "message": "Cache invalidé avec succès"
}
```

## Installation et démarrage

### 1. Installer Redis

**Ubuntu/Debian :**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS :**
```bash
brew install redis
brew services start redis
```

**Windows :**
Télécharger depuis https://redis.io/download ou utiliser Docker :
```bash
docker run -d -p 6379:6379 redis:latest
```

### 2. Vérifier Redis
```bash
redis-cli ping
# Devrait retourner: PONG
```

### 3. Installer les dépendances Python
```bash
pip install redis psycopg2-binary pandas
```

### 4. Configurer les variables d'environnement
Créer/modifier `.env` avec les configurations Redis et PostgreSQL.

### 5. Démarrer l'application
```bash
python -m uvicorn app.main:app --reload
```

## Stratégies de mise à jour du cache

### 1. TTL (Time To Live)
Le cache expire automatiquement après `REDIS_CACHE_TTL` secondes (par défaut 1 heure). Après expiration, les données seront rechargées depuis la DB au prochain appel.

**Avantages :**
- Simple, automatique
- Garantit des données relativement fraîches

**Inconvénients :**
- Peut servir des données légèrement obsolètes
- Pic de latence lors du rechargement

### 2. Rafraîchissement manuel
Appeler `/cache/refresh` pour forcer la mise à jour.

**Cas d'usage :**
- Après des modifications importantes dans la DB
- Déploiement de nouvelles données
- Maintenance planifiée

### 3. Mise à jour incrémentale (recommandé)
Utiliser `update_posts_incremental()` pour mettre à jour uniquement les posts modifiés.

**Implémentation avec webhook/trigger :**
```python
# Après création/modification d'un post
new_post = {...}
recommender.cache_service.update_posts_incremental([new_post], [])

# Après suppression d'un post
deleted_id = 123
recommender.cache_service.update_posts_incremental([], [deleted_id])
```

### 4. Cache-aside pattern (actuel)
L'application vérifie d'abord le cache, puis la DB si nécessaire.

## Monitoring et métriques

### Vérifier l'état du cache
```bash
curl http://localhost:8000/api/v1/recommendation/cache/stats
```

### Logs
Le système log automatiquement :
- Cache HIT/MISS
- Nombre de posts chargés
- Erreurs de connexion Redis
- Temps de chargement

**Exemple de logs :**
```
INFO: ✓ Cache Redis initialisé (localhost:6379)
INFO: Cache MISS: posts non trouvés
INFO: ✓ 1500 posts récupérés depuis la DB
INFO: ✓ Cache SET: 1500 posts stockés (TTL: 3600s)
INFO: ✓ Cache HIT: 1500 posts récupérés
```

## Performance

### Benchmarks attendus

**Sans cache (requête DB directe) :**
- Temps de réponse : 200-500ms
- Charge DB : Élevée

**Avec cache (Redis) :**
- Temps de réponse : 10-50ms (10-50x plus rapide)
- Charge DB : Minimale (uniquement lors du rechargement)

### Optimisations supplémentaires

1. **Compression** : Compresser les données JSON avant stockage
2. **Partitionnement** : Cacher par catégories de posts
3. **Cache multi-niveaux** : Redis + cache mémoire local
4. **Pré-calcul** : Cacher aussi les recommandations par utilisateur

## Troubleshooting

### Redis non disponible
Si Redis n'est pas disponible, le système fonctionne en mode dégradé :
- Les données sont chargées directement depuis PostgreSQL
- Logs : `⚠️ Redis non disponible: ... Mode sans cache activé.`

### Cache corrompu
Invalider le cache :
```bash
curl -X DELETE http://localhost:8000/api/v1/recommendation/cache/invalidate
```

### Données obsolètes
Rafraîchir manuellement :
```bash
curl -X POST http://localhost:8000/api/v1/recommendation/cache/refresh
```

### Vider Redis manuellement
```bash
redis-cli FLUSHDB
```

## Sécurité

### Recommandations
1. **Authentification Redis** : Configurer un mot de passe
   ```bash
   # redis.conf
   requirepass your_strong_password
   ```

2. **Réseau** : Ne pas exposer Redis sur Internet
   ```bash
   # redis.conf
   bind 127.0.0.1
   ```

3. **Chiffrement** : Utiliser Redis avec TLS en production

4. **Isolation** : Utiliser des DB Redis séparées par environnement
   - Dev : DB 0
   - Staging : DB 1
   - Production : DB 2

## Évolutions futures

1. **Cache des recommandations** : Cacher aussi les résultats de recommandations par utilisateur
2. **Invalidation intelligente** : Webhooks pour mise à jour en temps réel
3. **Clustering Redis** : Pour haute disponibilité
4. **Métriques avancées** : Taux de hit/miss, latence, etc.
5. **Cache warming** : Pré-charger le cache au démarrage
