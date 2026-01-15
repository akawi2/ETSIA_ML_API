"""
Modèle de recommandation de posts basé sur le filtrage collaboratif user-user
"""
from typing import Dict, Any, List
import time
import numpy as np
from app.core.base_model import BaseMLModel
from app.core.monitoring import emit_metric
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RecommendationModel(BaseMLModel):
    """
    Modèle de recommandation de posts utilisant le filtrage collaboratif user-user
    """
    
    @property
    def model_name(self) -> str:
        return "recommendation-system"
    
    @property
    def model_version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "Équipe ETSIA"
    
    @property
    def description(self) -> str:
        return "Système de recommandation de posts basé sur le filtrage collaboratif user-user"
    
    @property
    def tags(self) -> List[str]:
        return ["recommendation", "collaborative-filtering", "user-user", "posts"]
    
    def __init__(
        self, 
        db_config: Dict[str, str] = None,
        redis_config: Dict[str, Any] = None,
        use_cache: bool = True
    ):
        """
        Initialise le modèle de recommandation avec cache
        
        Args:
            db_config: Configuration de la base de données PostgreSQL
            redis_config: Configuration Redis pour le cache
            use_cache: Activer/désactiver le cache
        """
        try:
            logger.info("Initialisation du système de recommandation avec cache...")
            
            # Importer les settings
            from app.config import settings
            
            self.db_config = db_config or {
                'host': settings.POSTGRES_HOST,
                'database': settings.POSTGRES_DB,
                'user': settings.POSTGRES_USER,
                'password': settings.POSTGRES_PASSWORD,
                'port': settings.POSTGRES_PORT
            }
            
            self.redis_config = redis_config or {
                'host': settings.REDIS_HOST,
                'port': settings.REDIS_PORT,
                'db': settings.REDIS_DB,
                'ttl': settings.REDIS_CACHE_TTL
            }
            
            self.use_cache = use_cache
            
            # Importer le recommender
            try:
                from .recommendation_service import UserUserRecommender
                self.recommender = UserUserRecommender(
                    min_similarity=0.1,
                    db_config=self.db_config,
                    redis_config=self.redis_config,
                    use_cache=self.use_cache
                )
                logger.info("  → UserUserRecommender avec cache chargé")
            except ImportError as e:
                logger.warning(f"  → UserUserRecommender non disponible: {e}")
                self.recommender = None
            
            self._initialized = True
            logger.info(f"✓ {self.model_name} initialisé avec succès")
            
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'initialisation de {self.model_name}: {e}")
            self._initialized = False
            raise
    
    async def predict(self, text: str = "", user_id: int = None, **kwargs) -> Dict[str, Any]:
        """
        Génère des recommandations de posts pour un utilisateur
        
        Args:
            text: Non utilisé (compatibilité avec l'interface)
            user_id: ID de l'utilisateur
            **kwargs: Paramètres additionnels (top_n, available_posts)
        
        Returns:
            Dict avec les recommandations
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé correctement")
        
        if user_id is None:
            raise ValueError("user_id est requis pour les recommandations")
        
        start_time = time.time()
        
        try:
            top_n = kwargs.get('top_n', 10)
            available_posts = kwargs.get('available_posts', None)
            
            # Charger et entraîner le modèle si nécessaire
            if self.recommender and not hasattr(self.recommender, 'similarity_matrix'):
                logger.info("Entraînement du modèle de recommandation...")
                self.recommender.load_and_train()
            
            # Générer les recommandations
            if self.recommender:
                if available_posts is None:
                    # Vérifier si posts_df existe et n'est pas None
                    if hasattr(self.recommender, 'posts_df') and self.recommender.posts_df is not None and hasattr(self.recommender.posts_df, 'empty') and not self.recommender.posts_df.empty:
                        available_posts = self.recommender.posts_df['post_id'].tolist()[:15]
                    else:
                        available_posts = list(range(1, 16))
                
                recommendations = self.recommender.recommend_posts(user_id, available_posts, top_n)
                
                formatted_recommendations = [
                    {
                        'post_id': int(rec['post_id']),
                        'score': float(rec['score'])
                    }
                    for rec in recommendations
                ]
            else:
                # Fallback: recommandations aléatoires
                logger.warning("Recommender non disponible, génération de recommandations aléatoires")
                available_posts = available_posts or list(range(1, 16))
                np.random.shuffle(available_posts)
                formatted_recommendations = [
                    {'post_id': int(post_id), 'score': float(np.random.random())}
                    for post_id in available_posts[:top_n]
                ]
            
            # Calculer la latence
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Calculer le score moyen
            avg_score = np.mean([rec['score'] for rec in formatted_recommendations]) if formatted_recommendations else 0.0
            
            # Émettre les métriques de monitoring (GA4)
            emit_metric(
                service="recommendation",
                event_name="generate_recommendations",
                model_name="collaborative-filtering",
                params={
                    "latency": latency_ms,
                    "recommendations_count": len(formatted_recommendations),
                    "avg_score": float(avg_score),
                    "user_id": user_id
                }
            )
            
            # Enregistrer dans la base de données (Métriques internes)
            try:
                from app.core.metrics.metrics_decorator import record_prediction_async
                await record_prediction_async(
                    model_name=self.model_name,
                    provider="local",
                    endpoint="/api/v1/recommend",
                    prediction="RECOMMANDATIONS",
                    confidence=avg_score,
                    severity="Aucune",
                    latency_ms=latency_ms,
                    fallback_used=False,
                    input_length=0
                )
            except Exception as e:
                logger.debug(f"Erreur enregistrement métrique BDD: {e}")
            
            return {
                "prediction": "RECOMMANDATIONS",
                "confidence": 1.0,
                "severity": "Aucune",
                "reasoning": f"Recommandations générées pour l'utilisateur {user_id}",
                "user_id": user_id,
                "recommendations": formatted_recommendations,
                "total_recommendations": len(formatted_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de recommandations: {e}")
            
            # Émettre métrique d'erreur
            latency_ms = int((time.time() - start_time) * 1000)
            emit_metric(
                service="recommendation",
                event_name="generate_recommendations_error",
                model_name="collaborative-filtering",
                params={
                    "latency": latency_ms,
                    "error": str(e)[:100],
                    "user_id": user_id
                }
            )
            raise
    
    def batch_predict(self, texts: List[str] = None, user_ids: List[int] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Génère des recommandations pour plusieurs utilisateurs
        
        Args:
            texts: Non utilisé (compatibilité)
            user_ids: Liste d'IDs utilisateurs
            **kwargs: Paramètres additionnels
        
        Returns:
            Liste de résultats de recommandations
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé correctement")
        
        if not user_ids:
            raise ValueError("user_ids est requis pour les recommandations batch")
        
        results = []
        for user_id in user_ids:
            try:
                result = self.predict(user_id=user_id, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur pour user_id {user_id}: {e}")
                results.append({
                    "prediction": "ERREUR",
                    "confidence": 0.0,
                    "severity": "Aucune",
                    "reasoning": f"Erreur: {str(e)}",
                    "user_id": user_id,
                    "recommendations": []
                })
        
        return results
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé du système de recommandation
        
        Returns:
            Dict avec les informations de santé
        """
        try:
            # Test basique
            test_result = await self.predict(user_id=1, top_n=5)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version,
                "recommender_available": self.recommender is not None,
                "test_recommendations": len(test_result.get("recommendations", []))
            }
            
        except Exception as e:
            logger.error(f"Health check failed for {self.model_name}: {e}")
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "version": self.model_version,
                "recommender_available": self.recommender is not None,
                "error": str(e)
            }


class UserUserRecommender:
    """
    Classe de recommandation user-user (placeholder pour compatibilité)
    """
    
    def __init__(self, min_similarity: float = 0.1, db_config: Dict[str, str] = None):
        self.min_similarity = min_similarity
        self.db_config = db_config
        self.posts_df = None
        self.similarity_matrix = None
    
    def load_and_train(self):
        """Charge les données et entraîne le modèle"""
        logger.info("Chargement et entraînement du modèle...")
        # TODO: Implémenter le chargement depuis la DB
        pass
    
    def recommend_posts(self, user_id: int, available_posts: List[int], top_n: int = 10) -> List[Dict[str, Any]]:
        """Génère des recommandations pour un utilisateur"""
        # Recommandations aléatoires pour le moment
        posts_copy = available_posts.copy()
        np.random.shuffle(posts_copy)
        return [
            {'post_id': post_id, 'score': float(np.random.random())}
            for post_id in posts_copy[:top_n]
        ]
