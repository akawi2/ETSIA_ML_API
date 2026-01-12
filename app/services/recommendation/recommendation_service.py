"""
Service de recommandation (legacy - conservé pour compatibilité)
"""
from typing import Dict, List, Any
import numpy as np


class UserUserRecommender:
    """
    Classe de recommandation user-user basée sur le filtrage collaboratif
    """
    
    def __init__(self, min_similarity: float = 0.1, db_config: Dict[str, str] = None):
        self.min_similarity = min_similarity
        self.db_config = db_config
        self.posts_df = None
        self.similarity_matrix = None
    
    def load_and_train(self):
        """Charge les données et entraîne le modèle"""
        print("Chargement et entraînement du modèle...")
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


def recommend_service(user_id: int) -> List[Dict[str, Any]]:
    """
    Service de recommandation (fonction legacy)
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Liste de recommandations
    """
    # Configure your database connection
    db_config = {
        'host': 'localhost',
        'database': 'etsia_ai',
        'user': 'postgres',
        'password': '...',
        'port': '5432'
    }
    
    # Train user-user collaborative filtering
    print("\n🎯 Training User-User Collaborative Filtering...")
    recommender = UserUserRecommender(min_similarity=0.1, db_config=db_config)
    recommender.load_and_train()

    # Get available posts for demo
    available_posts = recommender.posts_df['post_id'].tolist()[:15] if hasattr(recommender, 'posts_df') and not recommender.posts_df.empty else list(range(1, 16))
    recommendations = recommender.recommend_posts(user_id, available_posts, 10)
    formatted_recommendations = [
        {'post_id': int(rec['post_id']), 'score': rec['score']}
        for rec in recommendations
    ]
    return formatted_recommendations
        
