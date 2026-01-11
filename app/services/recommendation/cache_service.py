"""
Service de cache Redis pour les recommandations
Permet de cacher les posts et d'améliorer les performances
"""
import redis
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PostCacheService:
    """
    Service de cache pour les posts utilisé dans les recommandations.
    Utilise Redis pour stocker les données de posts et réduire les requêtes DB.
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        cache_ttl: int = 3600  # 1 heure par défaut
    ):
        """
        Initialise le service de cache Redis
        
        Args:
            redis_host: Hôte Redis
            redis_port: Port Redis
            redis_db: Numéro de base Redis
            cache_ttl: Durée de vie du cache en secondes
        """
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test de connexion
            self.redis_client.ping()
            self.cache_ttl = cache_ttl
            self._initialized = True
            logger.info(f"✓ Cache Redis initialisé ({redis_host}:{redis_port})")
        except Exception as e:
            logger.warning(f"⚠️  Redis non disponible: {e}. Mode sans cache activé.")
            self.redis_client = None
            self._initialized = False
    
    @property
    def is_available(self) -> bool:
        """Vérifie si Redis est disponible"""
        return self._initialized and self.redis_client is not None
    
    def _get_posts_cache_key(self) -> str:
        """Clé Redis pour tous les posts"""
        return "recommendation:posts:all"
    
    def _get_post_cache_key(self, post_id: int) -> str:
        """Clé Redis pour un post spécifique"""
        return f"recommendation:post:{post_id}"
    
    def _get_metadata_key(self) -> str:
        """Clé Redis pour les métadonnées du cache"""
        return "recommendation:cache:metadata"
    
    def get_all_posts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Récupère tous les posts depuis le cache
        
        Returns:
            Liste des posts ou None si non trouvé/erreur
        """
        if not self.is_available:
            return None
        
        try:
            cache_key = self._get_posts_cache_key()
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                posts = json.loads(cached_data)
                logger.info(f"✓ Cache HIT: {len(posts)} posts récupérés")
                return posts
            
            logger.info("Cache MISS: posts non trouvés")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lecture cache: {e}")
            return None
    
    def set_all_posts(self, posts: List[Dict[str, Any]]) -> bool:
        """
        Stocke tous les posts dans le cache
        
        Args:
            posts: Liste des posts à cacher
        
        Returns:
            True si succès, False sinon
        """
        if not self.is_available:
            return False
        
        try:
            cache_key = self._get_posts_cache_key()
            posts_json = json.dumps(posts)
            
            # Stocker avec TTL
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                posts_json
            )
            
            # Mettre à jour les métadonnées
            metadata = {
                "last_update": datetime.utcnow().isoformat(),
                "total_posts": len(posts),
                "ttl": self.cache_ttl
            }
            self.redis_client.setex(
                self._get_metadata_key(),
                self.cache_ttl,
                json.dumps(metadata)
            )
            
            logger.info(f"✓ Cache SET: {len(posts)} posts stockés (TTL: {self.cache_ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Erreur écriture cache: {e}")
            return False
    
    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un post spécifique depuis le cache
        
        Args:
            post_id: ID du post
        
        Returns:
            Données du post ou None
        """
        if not self.is_available:
            return None
        
        try:
            cache_key = self._get_post_cache_key(post_id)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
            
        except Exception as e:
            logger.error(f"Erreur lecture post {post_id}: {e}")
            return None
    
    def set_post(self, post_id: int, post_data: Dict[str, Any]) -> bool:
        """
        Stocke un post spécifique dans le cache
        
        Args:
            post_id: ID du post
            post_data: Données du post
        
        Returns:
            True si succès
        """
        if not self.is_available:
            return False
        
        try:
            cache_key = self._get_post_cache_key(post_id)
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(post_data)
            )
            return True
            
        except Exception as e:
            logger.error(f"Erreur écriture post {post_id}: {e}")
            return False
    
    def invalidate_post(self, post_id: int) -> bool:
        """
        Invalide le cache d'un post spécifique
        
        Args:
            post_id: ID du post à invalider
        
        Returns:
            True si succès
        """
        if not self.is_available:
            return False
        
        try:
            cache_key = self._get_post_cache_key(post_id)
            self.redis_client.delete(cache_key)
            logger.info(f"✓ Cache invalidé pour post {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur invalidation post {post_id}: {e}")
            return False
    
    def invalidate_all(self) -> bool:
        """
        Invalide tout le cache des posts
        
        Returns:
            True si succès
        """
        if not self.is_available:
            return False
        
        try:
            # Supprimer le cache global
            self.redis_client.delete(self._get_posts_cache_key())
            self.redis_client.delete(self._get_metadata_key())
            
            # Supprimer tous les posts individuels
            pattern = "recommendation:post:*"
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
            
            logger.info("✓ Cache complet invalidé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur invalidation cache: {e}")
            return False
    
    def get_cache_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Récupère les métadonnées du cache
        
        Returns:
            Métadonnées ou None
        """
        if not self.is_available:
            return None
        
        try:
            metadata_json = self.redis_client.get(self._get_metadata_key())
            if metadata_json:
                metadata = json.loads(metadata_json)
                # Ajouter le TTL restant
                ttl = self.redis_client.ttl(self._get_posts_cache_key())
                metadata["ttl_remaining"] = ttl if ttl > 0 else 0
                return metadata
            return None
            
        except Exception as e:
            logger.error(f"Erreur lecture métadonnées: {e}")
            return None
    
    def update_posts_incremental(self, new_posts: List[Dict[str, Any]], deleted_post_ids: List[int] = None) -> bool:
        """
        Mise à jour incrémentale du cache
        
        Args:
            new_posts: Nouveaux posts ou posts modifiés
            deleted_post_ids: IDs des posts supprimés
        
        Returns:
            True si succès
        """
        if not self.is_available:
            return False
        
        try:
            # Récupérer le cache actuel
            current_posts = self.get_all_posts()
            
            if current_posts is None:
                # Pas de cache, créer un nouveau
                return self.set_all_posts(new_posts)
            
            # Créer un dictionnaire pour accès rapide
            posts_dict = {post['post_id']: post for post in current_posts}
            
            # Ajouter/mettre à jour les nouveaux posts
            for post in new_posts:
                post_id = post['post_id']
                posts_dict[post_id] = post
                # Mettre à jour le cache individuel
                self.set_post(post_id, post)
            
            # Supprimer les posts supprimés
            if deleted_post_ids:
                for post_id in deleted_post_ids:
                    posts_dict.pop(post_id, None)
                    self.invalidate_post(post_id)
            
            # Mettre à jour le cache global
            updated_posts = list(posts_dict.values())
            return self.set_all_posts(updated_posts)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour incrémentale: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du cache
        
        Returns:
            Statistiques du cache
        """
        if not self.is_available:
            return {
                "status": "unavailable",
                "redis_connected": False
            }
        
        try:
            metadata = self.get_cache_metadata()
            
            # Compter les posts individuels en cache
            pattern = "recommendation:post:*"
            individual_posts = len(list(self.redis_client.scan_iter(match=pattern)))
            
            return {
                "status": "available",
                "redis_connected": True,
                "metadata": metadata,
                "individual_posts_cached": individual_posts,
                "cache_ttl": self.cache_ttl
            }
            
        except Exception as e:
            logger.error(f"Erreur stats cache: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
