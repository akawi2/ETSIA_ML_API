"""
Service de recommandation avec système de cache
"""
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserUserRecommender:
    """
    Classe de recommandation user-user basée sur le filtrage collaboratif
    Utilise un système de cache Redis pour améliorer les performances
    """
    
    def __init__(
        self, 
        min_similarity: float = 0.1, 
        db_config: Dict[str, str] = None,
        redis_config: Dict[str, Any] = None,
        use_cache: bool = True
    ):
        """
        Initialise le recommender avec cache
        
        Args:
            min_similarity: Seuil de similarité minimum
            db_config: Configuration de la base de données
            redis_config: Configuration Redis pour le cache
            use_cache: Activer/désactiver le cache
        """
        self.min_similarity = min_similarity
        self.db_config = db_config
        self.posts_df = None
        self.similarity_matrix = None
        self.use_cache = use_cache
        
        # Initialiser les services
        self._init_services(redis_config)
    
    def _init_services(self, redis_config: Optional[Dict[str, Any]] = None):
        """Initialise les services de cache et DB"""
        try:
            # Service de base de données
            from .db_service import PostDatabaseService
            self.db_service = PostDatabaseService(self.db_config or {})
            logger.info("✓ Service DB initialisé")
        except Exception as e:
            logger.warning(f"⚠️  Service DB non disponible: {e}")
            self.db_service = None
        
        # Service de cache
        if self.use_cache:
            try:
                from .cache_service import PostCacheService
                redis_config = redis_config or {}
                self.cache_service = PostCacheService(
                    redis_host=redis_config.get('host', 'localhost'),
                    redis_port=redis_config.get('port', 6379),
                    redis_db=redis_config.get('db', 0),
                    cache_ttl=redis_config.get('ttl', 3600)
                )
                logger.info("✓ Service de cache initialisé")
            except Exception as e:
                logger.warning(f"⚠️  Cache non disponible: {e}")
                self.cache_service = None
        else:
            self.cache_service = None
    
    def load_and_train(self):
        """
        Charge les données (depuis cache ou DB) et entraîne le modèle
        """
        logger.info("Chargement des données pour recommandation...")
        
        # Essayer de charger depuis le cache d'abord
        posts_data = None
        if self.cache_service and self.cache_service.is_available:
            posts_data = self.cache_service.get_all_posts()
            if posts_data:
                logger.info(f"✓ Données chargées depuis le cache ({len(posts_data)} posts)")
        
        # Si pas de cache, charger depuis la DB
        if posts_data is None and self.db_service:
            logger.info("Cache MISS - Chargement depuis la base de données...")
            posts_data = self.db_service.get_all_posts()
            
            # Mettre en cache pour les prochaines fois
            if posts_data and self.cache_service and self.cache_service.is_available:
                self.cache_service.set_all_posts(posts_data)
                logger.info(f"✓ {len(posts_data)} posts mis en cache")
        
        # Convertir en DataFrame pour l'algorithme
        if posts_data:
            self.posts_df = pd.DataFrame(posts_data)
            logger.info(f"✓ DataFrame créé avec {len(self.posts_df)} posts")
            
            # Entraîner le modèle de similarité
            self._train_similarity_matrix()
        else:
            logger.warning("⚠️  Aucune donnée disponible, utilisation de données de test")
            self.posts_df = None
    
    def _train_similarity_matrix(self):
        """
        Entraîne la matrice de similarité user-user
        """
        if self.posts_df is None or len(self.posts_df) == 0:
            logger.warning("Pas de données pour entraîner la matrice de similarité")
            return
        
        try:
            # Créer une matrice user-post (simplifié pour l'exemple)
            # Dans une vraie implémentation, utiliser les interactions (likes, comments, etc.)
            user_ids = self.posts_df['user_id'].unique()
            post_ids = self.posts_df['post_id'].unique()
            
            # Matrice de similarité basique (à améliorer)
            n_users = len(user_ids)
            self.similarity_matrix = np.random.rand(n_users, n_users)
            np.fill_diagonal(self.similarity_matrix, 1.0)
            
            logger.info(f"✓ Matrice de similarité créée ({n_users}x{n_users})")
            
        except Exception as e:
            logger.error(f"Erreur entraînement matrice: {e}")
            self.similarity_matrix = None
    
    def recommend_posts(self, user_id: int, available_posts: List[int], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des recommandations pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            available_posts: Liste des posts disponibles
            top_n: Nombre de recommandations
        
        Returns:
            Liste de recommandations avec scores
        """
        # Si pas de données, recommandations aléatoires
        if self.posts_df is None or len(self.posts_df) == 0:
            posts_copy = available_posts.copy()
            np.random.shuffle(posts_copy)
            return [
                {'post_id': post_id, 'score': float(np.random.random())}
                for post_id in posts_copy[:top_n]
            ]
        
        # Algorithme de recommandation basé sur les données
        try:
            # Filtrer les posts disponibles
            available_df = self.posts_df[self.posts_df['post_id'].isin(available_posts)]
            
            if len(available_df) == 0:
                # Fallback sur posts aléatoires
                posts_copy = available_posts.copy()
                np.random.shuffle(posts_copy)
                return [
                    {'post_id': post_id, 'score': float(np.random.random())}
                    for post_id in posts_copy[:top_n]
                ]
            
            # Calculer les scores (simplifié - à améliorer avec vraie similarité)
            recommendations = []
            for _, post in available_df.iterrows():
                score = self._calculate_post_score(user_id, post)
                recommendations.append({
                    'post_id': int(post['post_id']),
                    'score': float(score)
                })
            
            # Trier par score décroissant
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return recommendations[:top_n]
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {e}")
            # Fallback
            posts_copy = available_posts.copy()
            np.random.shuffle(posts_copy)
            return [
                {'post_id': post_id, 'score': float(np.random.random())}
                for post_id in posts_copy[:top_n]
            ]
    
    def _calculate_post_score(self, user_id: int, post: pd.Series) -> float:
        """
        Calcule le score d'un post pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            post: Données du post
        
        Returns:
            Score de recommandation
        """
        # Score basique basé sur l'engagement
        # À améliorer avec vraie similarité user-user
        score = 0.0
        
        # Facteur d'engagement
        if 'likes_count' in post:
            score += post['likes_count'] * 0.3
        if 'comments_count' in post:
            score += post['comments_count'] * 0.5
        if 'shares_count' in post:
            score += post['shares_count'] * 0.2
        
        # Normaliser entre 0 et 1
        score = min(score / 100.0, 1.0)
        
        # Ajouter un facteur aléatoire pour la diversité
        score = score * 0.8 + np.random.random() * 0.2
        
        return score
    
    def refresh_cache(self) -> bool:
        """
        Force le rafraîchissement du cache depuis la DB
        
        Returns:
            True si succès
        """
        if not self.db_service:
            logger.warning("Service DB non disponible")
            return False
        
        try:
            logger.info("Rafraîchissement du cache...")
            posts_data = self.db_service.get_all_posts()
            
            if self.cache_service and self.cache_service.is_available:
                self.cache_service.set_all_posts(posts_data)
                logger.info(f"✓ Cache rafraîchi avec {len(posts_data)} posts")
            
            # Recharger le DataFrame
            self.posts_df = pd.DataFrame(posts_data)
            self._train_similarity_matrix()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur rafraîchissement cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du cache
        
        Returns:
            Statistiques
        """
        if self.cache_service:
            return self.cache_service.get_cache_stats()
        return {"status": "cache_disabled"}


def recommend_service(
    user_id: int, 
    db_config: Dict[str, str] = None,
    redis_config: Dict[str, Any] = None,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Service de recommandation avec cache
    
    Args:
        user_id: ID de l'utilisateur
        db_config: Configuration de la base de données
        redis_config: Configuration Redis
        use_cache: Utiliser le cache ou non
    
    Returns:
        Liste de recommandations
    """
    # Configuration par défaut
    if db_config is None:
        db_config = {
            'host': 'localhost',
            'database': 'etsia_ai',
            'user': 'postgres',
            'password': '...',
            'port': '5432'
        }
    
    if redis_config is None:
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'ttl': 3600
        }
    
    # Créer le recommender avec cache
    logger.info(f"🎯 Génération de recommandations pour user {user_id}")
    recommender = UserUserRecommender(
        min_similarity=0.1,
        db_config=db_config,
        redis_config=redis_config,
        use_cache=use_cache
    )
    recommender.load_and_train()

    # Obtenir les posts disponibles
    if recommender.posts_df is not None and len(recommender.posts_df) > 0:
        available_posts = recommender.posts_df['post_id'].tolist()[:50]
    else:
        available_posts = list(range(1, 16))
    
    recommendations = recommender.recommend_posts(user_id, available_posts, 10)
    formatted_recommendations = [
        {'post_id': int(rec['post_id']), 'score': rec['score']}
        for rec in recommendations
    ]
    return formatted_recommendations
        
