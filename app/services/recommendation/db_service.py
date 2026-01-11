"""
Service de base de données pour les recommandations
Gère la récupération des posts depuis PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PostDatabaseService:
    """
    Service pour récupérer les posts depuis la base de données PostgreSQL
    """
    
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialise le service de base de données
        
        Args:
            db_config: Configuration de connexion PostgreSQL
                {
                    'host': 'localhost',
                    'database': 'etsia_ai',
                    'user': 'postgres',
                    'password': '...',
                    'port': '5432'
                }
        """
        self.db_config = db_config
        self._connection = None
        logger.info("Service de base de données initialisé")
    
    def _get_connection(self):
        """
        Obtient une connexion à la base de données
        
        Returns:
            Connexion psycopg2
        """
        try:
            if self._connection is None or self._connection.closed:
                self._connection = psycopg2.connect(
                    host=self.db_config.get('host', 'localhost'),
                    database=self.db_config.get('database', 'etsia_ai'),
                    user=self.db_config.get('user', 'postgres'),
                    password=self.db_config.get('password', ''),
                    port=self.db_config.get('port', '5432')
                )
            return self._connection
        except Exception as e:
            logger.error(f"Erreur connexion DB: {e}")
            raise
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("Connexion DB fermée")
    
    def get_all_posts(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les posts depuis la base de données
        
        Returns:
            Liste des posts avec leurs métadonnées
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Requête pour récupérer tous les posts
            # Adapter selon votre schéma de base de données
            query = """
                SELECT 
                    id as post_id,
                    user_id,
                    content,
                    created_at,
                    updated_at,
                    likes_count,
                    comments_count,
                    shares_count
                FROM posts
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC
            """
            
            cursor.execute(query)
            posts = cursor.fetchall()
            
            # Convertir en liste de dictionnaires
            posts_list = [dict(post) for post in posts]
            
            # Convertir les dates en ISO format
            for post in posts_list:
                if 'created_at' in post and post['created_at']:
                    post['created_at'] = post['created_at'].isoformat()
                if 'updated_at' in post and post['updated_at']:
                    post['updated_at'] = post['updated_at'].isoformat()
            
            cursor.close()
            logger.info(f"✓ {len(posts_list)} posts récupérés depuis la DB")
            return posts_list
            
        except Exception as e:
            logger.error(f"Erreur récupération posts: {e}")
            # Retourner des données de test en cas d'erreur
            return self._get_mock_posts()
    
    def get_posts_by_ids(self, post_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Récupère des posts spécifiques par leurs IDs
        
        Args:
            post_ids: Liste des IDs de posts
        
        Returns:
            Liste des posts trouvés
        """
        if not post_ids:
            return []
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    id as post_id,
                    user_id,
                    content,
                    created_at,
                    updated_at,
                    likes_count,
                    comments_count,
                    shares_count
                FROM posts
                WHERE id = ANY(%s) AND deleted_at IS NULL
            """
            
            cursor.execute(query, (post_ids,))
            posts = cursor.fetchall()
            
            posts_list = [dict(post) for post in posts]
            
            # Convertir les dates
            for post in posts_list:
                if 'created_at' in post and post['created_at']:
                    post['created_at'] = post['created_at'].isoformat()
                if 'updated_at' in post and post['updated_at']:
                    post['updated_at'] = post['updated_at'].isoformat()
            
            cursor.close()
            return posts_list
            
        except Exception as e:
            logger.error(f"Erreur récupération posts par IDs: {e}")
            return []
    
    def get_recent_posts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les posts les plus récents
        
        Args:
            limit: Nombre maximum de posts à récupérer
        
        Returns:
            Liste des posts récents
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    id as post_id,
                    user_id,
                    content,
                    created_at,
                    updated_at,
                    likes_count,
                    comments_count,
                    shares_count
                FROM posts
                WHERE deleted_at IS NULL
                ORDER BY created_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            posts = cursor.fetchall()
            
            posts_list = [dict(post) for post in posts]
            
            for post in posts_list:
                if 'created_at' in post and post['created_at']:
                    post['created_at'] = post['created_at'].isoformat()
                if 'updated_at' in post and post['updated_at']:
                    post['updated_at'] = post['updated_at'].isoformat()
            
            cursor.close()
            return posts_list
            
        except Exception as e:
            logger.error(f"Erreur récupération posts récents: {e}")
            return []
    
    def get_posts_updated_since(self, since_datetime: datetime) -> List[Dict[str, Any]]:
        """
        Récupère les posts modifiés depuis une date donnée
        
        Args:
            since_datetime: Date de référence
        
        Returns:
            Liste des posts modifiés
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    id as post_id,
                    user_id,
                    content,
                    created_at,
                    updated_at,
                    likes_count,
                    comments_count,
                    shares_count
                FROM posts
                WHERE updated_at > %s AND deleted_at IS NULL
                ORDER BY updated_at DESC
            """
            
            cursor.execute(query, (since_datetime,))
            posts = cursor.fetchall()
            
            posts_list = [dict(post) for post in posts]
            
            for post in posts_list:
                if 'created_at' in post and post['created_at']:
                    post['created_at'] = post['created_at'].isoformat()
                if 'updated_at' in post and post['updated_at']:
                    post['updated_at'] = post['updated_at'].isoformat()
            
            cursor.close()
            logger.info(f"✓ {len(posts_list)} posts modifiés depuis {since_datetime}")
            return posts_list
            
        except Exception as e:
            logger.error(f"Erreur récupération posts modifiés: {e}")
            return []
    
    def get_deleted_post_ids_since(self, since_datetime: datetime) -> List[int]:
        """
        Récupère les IDs des posts supprimés depuis une date donnée
        
        Args:
            since_datetime: Date de référence
        
        Returns:
            Liste des IDs de posts supprimés
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id
                FROM posts
                WHERE deleted_at > %s AND deleted_at IS NOT NULL
            """
            
            cursor.execute(query, (since_datetime,))
            deleted_ids = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            logger.info(f"✓ {len(deleted_ids)} posts supprimés depuis {since_datetime}")
            return deleted_ids
            
        except Exception as e:
            logger.error(f"Erreur récupération posts supprimés: {e}")
            return []
    
    def _get_mock_posts(self) -> List[Dict[str, Any]]:
        """
        Retourne des données de test si la DB n'est pas disponible
        
        Returns:
            Liste de posts de test
        """
        logger.warning("⚠️  Utilisation de données de test (DB non disponible)")
        
        mock_posts = []
        for i in range(1, 21):
            mock_posts.append({
                'post_id': i,
                'user_id': (i % 5) + 1,
                'content': f'Ceci est un post de test numéro {i}',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'likes_count': i * 10,
                'comments_count': i * 2,
                'shares_count': i
            })
        
        return mock_posts
    
    def test_connection(self) -> bool:
        """
        Test la connexion à la base de données
        
        Returns:
            True si la connexion fonctionne
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            logger.info("✓ Connexion DB testée avec succès")
            return True
        except Exception as e:
            logger.error(f"✗ Test connexion DB échoué: {e}")
            return False
