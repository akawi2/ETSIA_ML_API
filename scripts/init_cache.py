"""
Script d'initialisation du cache Redis pour les recommandations
Peut être exécuté au démarrage de l'application ou manuellement
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.recommendation.cache_service import PostCacheService
from app.services.recommendation.db_service import PostDatabaseService
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def init_cache():
    """
    Initialise le cache Redis avec les données de la base de données
    """
    print("\n" + "=" * 60)
    print("  INITIALISATION DU CACHE REDIS")
    print("=" * 60)
    
    # Configuration Redis
    redis_config = {
        'host': settings.REDIS_HOST,
        'port': settings.REDIS_PORT,
        'db': settings.REDIS_DB,
        'ttl': settings.REDIS_CACHE_TTL
    }
    
    # Configuration DB
    db_config = {
        'host': settings.POSTGRES_HOST,
        'port': settings.POSTGRES_PORT,
        'user': settings.POSTGRES_USER,
        'password': settings.POSTGRES_PASSWORD,
        'database': settings.POSTGRES_DB
    }
    
    print(f"\nConfiguration Redis:")
    print(f"  Host: {redis_config['host']}")
    print(f"  Port: {redis_config['port']}")
    print(f"  DB: {redis_config['db']}")
    print(f"  TTL: {redis_config['ttl']}s")
    
    print(f"\nConfiguration PostgreSQL:")
    print(f"  Host: {db_config['host']}")
    print(f"  Port: {db_config['port']}")
    print(f"  Database: {db_config['database']}")
    
    # Initialiser les services
    print("\n" + "-" * 60)
    print("Initialisation des services...")
    print("-" * 60)
    
    try:
        # Service de cache
        cache_service = PostCacheService(
            redis_host=redis_config['host'],
            redis_port=redis_config['port'],
            redis_db=redis_config['db'],
            cache_ttl=redis_config['ttl']
        )
        
        if not cache_service.is_available:
            print("\n❌ ERREUR: Redis n'est pas disponible")
            print("Assurez-vous que Redis est démarré:")
            print("  - Ubuntu/Debian: sudo systemctl start redis-server")
            print("  - macOS: brew services start redis")
            print("  - Docker: docker run -d -p 6379:6379 redis:7-alpine")
            return False
        
        print("✓ Service de cache initialisé")
        
        # Service de base de données
        db_service = PostDatabaseService(db_config)
        
        # Tester la connexion DB
        if not db_service.test_connection():
            print("\n⚠️  AVERTISSEMENT: PostgreSQL n'est pas disponible")
            print("Le cache sera initialisé avec des données de test")
        else:
            print("✓ Service de base de données initialisé")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'initialisation: {e}")
        return False
    
    # Charger les données
    print("\n" + "-" * 60)
    print("Chargement des données...")
    print("-" * 60)
    
    try:
        # Récupérer les posts depuis la DB
        posts = db_service.get_all_posts()
        print(f"✓ {len(posts)} posts récupérés depuis la base de données")
        
        # Mettre en cache
        if cache_service.set_all_posts(posts):
            print(f"✓ {len(posts)} posts mis en cache avec succès")
        else:
            print("❌ Échec de la mise en cache")
            return False
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du chargement: {e}")
        return False
    
    # Vérifier le cache
    print("\n" + "-" * 60)
    print("Vérification du cache...")
    print("-" * 60)
    
    try:
        # Récupérer les stats
        stats = cache_service.get_cache_stats()
        
        print("\nStatistiques du cache:")
        print(f"  Status: {stats.get('status', 'unknown')}")
        print(f"  Redis connecté: {stats.get('redis_connected', False)}")
        
        if 'metadata' in stats and stats['metadata']:
            metadata = stats['metadata']
            print(f"  Dernière mise à jour: {metadata.get('last_update', 'N/A')}")
            print(f"  Total posts: {metadata.get('total_posts', 0)}")
            print(f"  TTL: {metadata.get('ttl', 0)}s")
            print(f"  TTL restant: {metadata.get('ttl_remaining', 0)}s")
        
        print(f"  Posts individuels en cache: {stats.get('individual_posts_cached', 0)}")
        
    except Exception as e:
        print(f"\n⚠️  Impossible de récupérer les stats: {e}")
    
    # Fermer la connexion DB
    db_service.close()
    
    print("\n" + "=" * 60)
    print("  ✅ INITIALISATION TERMINÉE AVEC SUCCÈS")
    print("=" * 60)
    print("\nLe cache est maintenant prêt à être utilisé!")
    print("Les recommandations seront beaucoup plus rapides.\n")
    
    return True


def clear_cache():
    """
    Vide complètement le cache Redis
    """
    print("\n" + "=" * 60)
    print("  VIDAGE DU CACHE REDIS")
    print("=" * 60)
    
    redis_config = {
        'host': settings.REDIS_HOST,
        'port': settings.REDIS_PORT,
        'db': settings.REDIS_DB,
        'ttl': settings.REDIS_CACHE_TTL
    }
    
    try:
        cache_service = PostCacheService(
            redis_host=redis_config['host'],
            redis_port=redis_config['port'],
            redis_db=redis_config['db'],
            cache_ttl=redis_config['ttl']
        )
        
        if not cache_service.is_available:
            print("\n❌ ERREUR: Redis n'est pas disponible")
            return False
        
        if cache_service.invalidate_all():
            print("\n✓ Cache vidé avec succès")
            return True
        else:
            print("\n❌ Échec du vidage du cache")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False


def show_cache_stats():
    """
    Affiche les statistiques du cache
    """
    print("\n" + "=" * 60)
    print("  STATISTIQUES DU CACHE REDIS")
    print("=" * 60)
    
    redis_config = {
        'host': settings.REDIS_HOST,
        'port': settings.REDIS_PORT,
        'db': settings.REDIS_DB,
        'ttl': settings.REDIS_CACHE_TTL
    }
    
    try:
        cache_service = PostCacheService(
            redis_host=redis_config['host'],
            redis_port=redis_config['port'],
            redis_db=redis_config['db'],
            cache_ttl=redis_config['ttl']
        )
        
        if not cache_service.is_available:
            print("\n❌ ERREUR: Redis n'est pas disponible")
            return False
        
        stats = cache_service.get_cache_stats()
        
        print(f"\nStatus: {stats.get('status', 'unknown')}")
        print(f"Redis connecté: {stats.get('redis_connected', False)}")
        
        if 'metadata' in stats and stats['metadata']:
            metadata = stats['metadata']
            print(f"\nMétadonnées:")
            print(f"  Dernière mise à jour: {metadata.get('last_update', 'N/A')}")
            print(f"  Total posts: {metadata.get('total_posts', 0)}")
            print(f"  TTL: {metadata.get('ttl', 0)}s")
            print(f"  TTL restant: {metadata.get('ttl_remaining', 0)}s")
        
        print(f"\nPosts individuels en cache: {stats.get('individual_posts_cached', 0)}")
        print(f"TTL du cache: {stats.get('cache_ttl', 0)}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False


def main():
    """
    Fonction principale
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gestion du cache Redis pour les recommandations"
    )
    parser.add_argument(
        'action',
        choices=['init', 'clear', 'stats'],
        help='Action à effectuer: init (initialiser), clear (vider), stats (statistiques)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'init':
        success = init_cache()
    elif args.action == 'clear':
        success = clear_cache()
    elif args.action == 'stats':
        success = show_cache_stats()
    else:
        print(f"Action inconnue: {args.action}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
