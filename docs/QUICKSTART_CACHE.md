# Guide de Démarrage Rapide - Système de Cache

## Installation en 5 minutes

### 1. Installer Redis

**Ubuntu/Debian :**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

**macOS :**
```bash
brew install redis
brew services start redis
```

**Windows (Docker) :**
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
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

Copier `.env.example` vers `.env` et ajuster :
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_TTL=3600
ENABLE_CACHE=true
```

### 5. Démarrer l'application
```bash
python -m uvicorn app.main:app --reload
```

## Test rapide

### 1. Vérifier le système
```bash
curl http://localhost:8000/api/v1/recommendation/health
```

### 2. Obtenir des recommandations
```bash
curl -X POST http://localhost:8000/api/v1/recommendation/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "top_n": 10}'
```

### 3. Vérifier les stats du cache
```bash
curl http://localhost:8000/api/v1/recommendation/cache/stats
```

## Utilisation avec Docker

### Démarrer tous les services
```bash
docker-compose up -d
```

Cela démarre :
- PostgreSQL (port 5432)
- Redis (port 6379)
- Ollama (port 11434)
- API (port 8000)

### Vérifier les services
```bash
docker-compose ps
```

### Voir les logs
```bash
docker-compose logs -f api
```

### Arrêter les services
```bash
docker-compose down
```

## Test de performance

Exécuter le script de test :
```bash
python examples/test_cache_system.py
```

Ce script va :
1. Tester le cache froid (premier appel)
2. Tester le cache chaud (appels suivants)
3. Comparer les performances
4. Afficher l'amélioration de vitesse

**Résultat attendu :**
```
RÉSULTATS DE PERFORMANCE:
  Temps sans cache: 0.450s
  Temps avec cache: 0.025s
  Accélération: 18.0x plus rapide
  Amélioration: 94.4%
```

## Commandes utiles

### Rafraîchir le cache
```bash
curl -X POST http://localhost:8000/api/v1/recommendation/cache/refresh
```

### Invalider le cache
```bash
curl -X DELETE http://localhost:8000/api/v1/recommendation/cache/invalidate
```

### Vider Redis manuellement
```bash
redis-cli FLUSHDB
```

### Voir les clés Redis
```bash
redis-cli KEYS "recommendation:*"
```

### Voir une clé spécifique
```bash
redis-cli GET "recommendation:posts:all"
```

## Troubleshooting rapide

### Redis ne démarre pas
```bash
# Vérifier le statut
sudo systemctl status redis-server

# Redémarrer
sudo systemctl restart redis-server
```

### Port déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :6379

# Tuer le processus
sudo kill -9 <PID>
```

### Cache ne fonctionne pas
1. Vérifier Redis : `redis-cli ping`
2. Vérifier les logs : `docker-compose logs redis`
3. Vérifier la config : `.env` → `ENABLE_CACHE=true`

## Prochaines étapes

- Lire la [documentation complète](CACHE_SYSTEM.md)
- Consulter le [README du module](../app/services/recommendation/README.md)
- Explorer l'[API documentation](http://localhost:8000/docs)

## Support

En cas de problème :
1. Vérifier les logs : `docker-compose logs -f`
2. Tester Redis : `redis-cli ping`
3. Tester PostgreSQL : `psql -U etsia -d etsia_ai`
4. Consulter la documentation complète
