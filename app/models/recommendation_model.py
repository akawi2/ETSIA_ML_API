# user_user_recommender.py
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pickle
import psycopg2
from sqlalchemy import create_engine
from typing import List, Dict, Any

class UserUserRecommender:
    def __init__(self, min_similarity=0.1, db_config=None):
        self.min_similarity = min_similarity
        self.is_trained = False
        self.db_config = db_config or {
            'host': 'localhost',
            'database': 'etsia_ai',
            'user': 'postgres',
            'password': 'JaAk',
            'port': '5432'
        }
    
    def _get_db_connection(self):
        """Create database connection"""
        return psycopg2.connect(**self.db_config)
    
    def _get_db_engine(self):
        """Create SQLAlchemy engine for pandas"""
        connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        return create_engine(connection_string)
    
    
    def get_posts_with_media(self, post_ids: List[int]) -> List[Dict[str, Any]]:
        print("00000")
        print(post_ids)
        """
        Fetch posts with their associated media for given post IDs
        
        Args:
            post_ids: List of post IDs to fetch
            
        Returns:
            List of dictionaries containing post data with associated media
        """
        if not post_ids:
            return []
            
        # Convert list to tuple for SQL IN clause
        post_ids_tuple = tuple(post_ids)
        
        # SQL query to fetch posts with their media
        query = """
        SELECT 
            p.post_id as post_id,
            p.postcontent,
            p.createdat,
            p.totallike,
            p.totalcomment,
            p.deletedat,
            p.userid,
            COALESCE(
                jsonb_agg(
                    jsonb_build_object(
                        'id', m.id,
                        'media_id', m.id,
                        'type', m.type,
                        'url', m.url,
                        'uploadedAt', m.uploadedAt,
                        'caption', m.caption,
                        'is_deleted', m.is_deleted,
                        'post_id', m.post_id
                    ) 
                    ORDER BY m.uploadedAt
                ) FILTER (WHERE m.id IS NOT NULL),
                '[]'::jsonb
            ) as media
        FROM Posts p
        LEFT JOIN Media m ON p.post_id = m.post_id AND m.is_deleted = FALSE
        WHERE p.post_id IN %s
        GROUP BY p.post_id, p.postcontent, p.createdat, p.totallike, p.totalcomment, p.deletedat, p.userid
        ORDER BY p.post_id;
        """
        
        try:
            # Use the existing database connection method
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query, (post_ids_tuple,))
            
            # Fetch results
            results = cursor.fetchall()
            
            # Format results
            posts_with_media = []
            for row in results:
                
                post_data = {
                    'post_id': row[0],
                    'postcontent': row[1],
                    'createdat': row[2],
                    'totallike': row[3],
                    'totalcomment': row[4],
                    'deletedat': row[5],
                    'userid': row[6],
                    'media': row[7]  # This is already a JSONB array with all media attributes
                }
                posts_with_media.append(post_data)
            
            return posts_with_media
            
        except Exception as e:
            print(f"Error fetching posts with media: {e}")
            return []
        
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    # def get_posts_with_media(self, post_ids: List[int]) -> List[Dict[str, Any]]:
    #     print ("00000")
    #     print(post_ids)
    #     """
    #     Fetch posts with their associated media for given post IDs
        
    #     Args:
    #         post_ids: List of post IDs to fetch
            
    #     Returns:
    #         List of dictionaries containing post data with associated media
    #     """
    #     if not post_ids:
    #         return []
            
    #     # Convert list to tuple for SQL IN clause
    #     post_ids_tuple = tuple(post_ids)
        
    #     # SQL query to fetch posts with their media
    #     query = """
    #     SELECT 
    #         p.post_id as post_id,
    #         p.postcontent,
    #         p.createdat,
    #         p.totallike,
    #         p.totalcomment,
    #         p.deletedat,
    #         p.userid,
    #         COALESCE(
    #             jsonb_agg(
    #                 jsonb_build_object(
    #                     'media_id', m.id,
    #                     'type', m.type,
    #                     'url', m.url,
    #                     'uploadedAt', m.uploadedAt,
    #                     'caption', m.caption,
    #                     'is_deleted', m.is_deleted
    #                 ) 
    #                 ORDER BY m.uploadedAt
    #             ) FILTER (WHERE m.id IS NOT NULL),
    #             '[]'::jsonb
    #         ) as media
    #     FROM Posts p
    #     LEFT JOIN Media m ON p.post_id = m.post_id AND m.is_deleted = FALSE
    #     WHERE p.post_id IN %s
    #     GROUP BY p.post_id, p.postcontent, p.createdat, p.totallike, p.totalcomment, p.deletedat, p.userid
    #     ORDER BY p.post_id;
    #     """
        
    #     try:
    #         # Use the existing database connection method
    #         conn = self._get_db_connection()
    #         cursor = conn.cursor()
            
    #         # Execute query
    #         cursor.execute(query, (post_ids_tuple,))
            
    #         # Fetch results
    #         results = cursor.fetchall()
            
    #         # Format results
    #         posts_with_media = []
    #         for row in results:
    #             post_data = {
    #                 'post_id': row[0],
    #                 'title': row[1],
    #                 'content': row[2],
    #                 'created_at': row[3],
    #                 'updated_at': row[4],
    #                 'user_id': row[5],
    #                 'media': row[6]  # This is already a JSONB array
    #             }
    #             posts_with_media.append(post_data)
            
    #         return posts_with_media
            
    #     except Exception as e:
    #         print(f"Error fetching posts with media: {e}")
    #         return []
        
    #     finally:
    #         if 'cursor' in locals():
    #             cursor.close()
    #         if 'conn' in locals():
    #             conn.close()
    
    def get_recommended_posts_with_media(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recommended posts for a user with their media attached.
        This assumes you have a recommendation system that provides post IDs.
        
        Args:
            user_id: The user ID to get recommendations for
            limit: Number of recommendations to return
            
        Returns:
            List of recommended posts with their media
        """
        # First, get recommended post IDs (you'll need to implement this part)
        recommended_post_ids = self._get_recommended_post_ids(user_id, limit)
        
        # Then fetch the posts with their media
        return self.get_posts_with_media(recommended_post_ids)
    
    def load_data_from_db(self):
        """Load data from PostgreSQL database"""
        print("📊 Loading data from database...")
        
        try:
            # Load likes data
            likes_query = """
            SELECT 
                u.userId as user_id,
                p.post_id,
                COUNT(l.like_id) as like_score
            FROM "likes" l
            JOIN users u ON l.user_id = u.userId
            JOIN posts p ON l.post_id = p.post_id
            WHERE p.deletedAt IS NULL
            GROUP BY u.userId, p.post_id
            """
            self.likes_df = pd.read_sql(likes_query, self._get_db_engine())
            print(f"✅ Loaded {len(self.likes_df)} likes records")
            
            # Load followers data
            followers_query = """
            SELECT 
                f1.follower_id,
                f1.following_id,
                CASE 
                    WHEN f2.follower_id IS NOT NULL THEN 0.2  -- Mutual follow
                    ELSE 0.1  -- One-way follow
                END as connection_strength
            FROM followers f1
            LEFT JOIN followers f2 ON f1.follower_id = f2.following_id AND f1.following_id = f2.follower_id
            """
            try:
                self.followers_df = pd.read_sql(followers_query, self._get_db_engine())
                print(f"✅ Loaded {len(self.followers_df)} followers records")
            except Exception as e:
                print(f"⚠️ Followers table not found, using empty dataframe: {e}")
                self.followers_df = pd.DataFrame(columns=['follower_id', 'following_id', 'connection_strength'])
            
            # Load promotion data
            promo_query = """
            SELECT 
                u.userId as user_id,
                p.course,
                p.year
            FROM promotion p
            JOIN users u ON p.user_id = u.userId
            WHERE u.isActive = TRUE AND u.isBlocked = FALSE
            """
            self.promo_df = pd.read_sql(promo_query, self._get_db_engine())
            print(f"✅ Loaded {len(self.promo_df)} promotion records")
            
            # Load users for reference
            users_query = """
            SELECT userId, email, isActive, isBlocked
            FROM users
            WHERE isActive = TRUE AND isBlocked = FALSE
            """
            self.users_df = pd.read_sql(users_query, self._get_db_engine())
            print(f"✅ Loaded {len(self.users_df)} active users")
            
            # Load posts details for better recommendations display
            posts_query = """
            SELECT post_id, postContent, userId as author_id, totalLike, totalComment
            FROM posts
            WHERE deletedAt IS NULL
            """
            self.posts_df = pd.read_sql(posts_query, self._get_db_engine())
            print(f"✅ Loaded {len(self.posts_df)} posts details")
            
        except Exception as e:
            print(f"❌ Error loading data from database: {e}")
            raise
    
    def load_and_train(self):
        """Load data and train user-user collaborative filtering"""
        print("📊 Loading data from database...")
        
        # Load data from database
        self.load_data_from_db()
        
        # Create user-item matrix for likes
        print("🔧 Creating user-item matrix...")
        if not self.likes_df.empty:
            self.user_item_matrix = self.likes_df.pivot_table(
                index='user_id', 
                columns='post_id', 
                values='like_score', 
                fill_value=0
            )
        else:
            self.user_item_matrix = pd.DataFrame()
        
        # Get active user IDs
        self.user_ids = self.users_df['userid'].tolist() if not self.users_df.empty else []
        
        if not self.user_item_matrix.empty and len(self.user_ids) > 0:
            # Compute user-user similarity for likes
            print("🎯 Computing user similarities...")
            self.user_similarity_likes = cosine_similarity(self.user_item_matrix)
            
            # Compute follower similarity matrix
            print("🔗 Computing follower similarities...")
            self.user_similarity_followers = self._compute_follower_similarity()
            
            # Compute promotion similarity matrix
            print("🎓 Computing promotion similarities...")
            self.user_similarity_promo = self._compute_promo_similarity()
            
            # Compute combined similarity matrix
            print("⚖️ Computing combined similarities...")
            self.user_similarity_combined = self._compute_combined_similarity()
        else:
            print("⚠️ No user data available for similarity computation")
            n_users = len(self.user_ids)
            self.user_similarity_likes = np.identity(n_users) if n_users > 0 else np.array([])
            self.user_similarity_followers = np.identity(n_users) if n_users > 0 else np.array([])
            self.user_similarity_promo = np.identity(n_users) if n_users > 0 else np.array([])
            self.user_similarity_combined = np.identity(n_users) if n_users > 0 else np.array([])
        
        # Compute item popularity for fallback
        if not self.likes_df.empty:
            self.item_popularity = self.likes_df.groupby('post_id')['like_score'].sum().sort_values(ascending=False)
        else:
            self.item_popularity = pd.Series(dtype=float)

        self.is_trained = True
        print("✅ User-User collaborative filtering model trained!")
        print(f"📈 User matrix: {self.user_item_matrix.shape if not self.user_item_matrix.empty else 'Empty'}")
        print(f"👥 Users: {len(self.user_ids)}")
    
    def _compute_follower_similarity(self):
        """Compute follower-based similarity between users"""
        n_users = len(self.user_ids)
        follower_similarity = np.zeros((n_users, n_users))
        
        if self.followers_df.empty:
            print("⚠️ No followers data available")
            return follower_similarity
        
        follower_matrix = np.zeros((n_users, n_users))
        user_to_idx = {user_id: idx for idx, user_id in enumerate(self.user_ids)}
        
        for _, row in self.followers_df.iterrows():
            follower_idx = user_to_idx.get(row['follower_id'])
            following_idx = user_to_idx.get(row['following_id'])
            
            if follower_idx is not None and following_idx is not None:
                follower_matrix[follower_idx, following_idx] = row['connection_strength']
        
        for i in range(n_users):
            for j in range(n_users):
                if i == j:
                    follower_similarity[i, j] = 1.0
                else:
                    follows_ij = follower_matrix[i, j] > 0
                    follows_ji = follower_matrix[j, i] > 0
                    
                    if follows_ij and follows_ji:
                        follower_similarity[i, j] = 0.2
                    elif follows_ij or follows_ji:
                        follower_similarity[i, j] = 0.1
                    else:
                        follower_similarity[i, j] = 0.0
        
        return follower_similarity
    
    def _compute_promo_similarity(self):
        """Compute promotion-based similarity between users"""
        n_users = len(self.user_ids)
        promo_similarity = np.zeros((n_users, n_users))
        
        if self.promo_df.empty:
            print("⚠️ No promotion data available")
            return promo_similarity
        
        user_to_idx = {user_id: idx for idx, user_id in enumerate(self.user_ids)}
        
        user_promo = {}
        for _, row in self.promo_df.iterrows():
            if row['user_id'] in user_to_idx:
                user_promo[row['user_id']] = (row['course'], row['year'])
        
        for i, user_i in enumerate(self.user_ids):
            for j, user_j in enumerate(self.user_ids):
                if i == j:
                    promo_similarity[i, j] = 1.0
                else:
                    promo_i = user_promo.get(user_i)
                    promo_j = user_promo.get(user_j)
                    
                    if promo_i and promo_j and promo_i == promo_j:
                        promo_similarity[i, j] = 0.2
                    else:
                        promo_similarity[i, j] = 0.0
        
        return promo_similarity
    
    def _compute_combined_similarity(self):
        """Compute combined similarity using weights: 60% likes, 20% followers, 20% promo"""
        n_users = len(self.user_ids)
        combined_similarity = np.zeros((n_users, n_users))
        
        for i in range(n_users):
            for j in range(n_users):
                if i == j:
                    combined_similarity[i, j] = 1.0
                else:
                    likes_sim = self.user_similarity_likes[i, j]
                    followers_sim = self.user_similarity_followers[i, j]
                    promo_sim = self.user_similarity_promo[i, j]
                    
                    combined_score = (0.6 * likes_sim + 
                                    0.2 * followers_sim + 
                                    0.2 * promo_sim)
                    
                    combined_similarity[i, j] = combined_score
        
        return combined_similarity
    
    def find_similar_users(self, user_id, n_similar=5, similarity_type="combined"):
        """Find similar users based on specified similarity type"""
        if user_id not in self.user_ids:
            return []
        
        user_idx = self.user_ids.index(user_id)
        
        if similarity_type == "likes":
            user_similarities = self.user_similarity_likes[user_idx]
        elif similarity_type == "followers":
            user_similarities = self.user_similarity_followers[user_idx]
        elif similarity_type == "promo":
            user_similarities = self.user_similarity_promo[user_idx]
        else:
            user_similarities = self.user_similarity_combined[user_idx]
        
        similar_indices = np.argsort(-user_similarities)[1:n_similar+1]
        similar_users = []
        
        for idx in similar_indices:
            if user_similarities[idx] > self.min_similarity:
                similar_users.append({
                    'user_id': self.user_ids[idx],
                    'similarity': user_similarities[idx],
                    'likes_similarity': self.user_similarity_likes[user_idx, idx],
                    'followers_similarity': self.user_similarity_followers[user_idx, idx],
                    'promo_similarity': self.user_similarity_promo[user_idx, idx]
                })
        
        return similar_users
    
    def get_post_details(self, post_ids):
        """Get detailed information about posts"""
        if not hasattr(self, 'posts_df') or self.posts_df.empty:
            return {}
        
        post_details = {}
        for post_id in post_ids:
            post_info = self.posts_df[self.posts_df['post_id'] == post_id]
            if not post_info.empty:
                post_details[post_id] = {
                    'content': post_info.iloc[0]['postcontent'],
                    'author_id': post_info.iloc[0]['author_id'],
                    'likes': post_info.iloc[0]['totallike'],
                    'comments': post_info.iloc[0]['totalcomment']
                }
        return post_details
    
    def recommend_with_details(self, user_id, post_ids, num_recommendations=10):
        """Generate recommendations with detailed information"""
        recommendations = self.recommend(user_id, post_ids, num_recommendations)
        post_details = self.get_post_details(recommendations)
        
        detailed_recommendations = []
        for post_id in recommendations:
            details = post_details.get(post_id, {})
            detailed_recommendations.append({
                'post_id': post_id,
                'content': details.get('content', 'Content not available'),
                'author_id': details.get('author_id', 'Unknown'),
                'likes': details.get('likes', 0),
                'comments': details.get('comments', 0)
            })
        
        return detailed_recommendations
    
    def recommend(self, user_id, post_ids, num_recommendations=10):
        """Generate recommendations using combined user-user collaborative filtering"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        if user_id not in self.user_ids:
            print(f"❌ User {user_id} not found in training data. Using popular posts.")
            return self._get_popular_posts(post_ids, num_recommendations)
        
        print(f"\n🎯 Generating recommendations for User {user_id}")
        print(f"📝 Available posts: {len(post_ids)}")
        
        similar_users = self.find_similar_users(user_id, n_similar=5, similarity_type="combined")
        
        if not similar_users:
            print("⚠️ No similar users found. Using popular posts.")
            return self._get_popular_posts(post_ids, num_recommendations)
        
        print(f"👥 Found {len(similar_users)} similar users:")
        for similar in similar_users:
            print(f"   - User {similar['user_id']} (similarity: {similar['similarity']:.3f})")
        
        recommendation_scores = {}
        user_likes = set(self.likes_df[self.likes_df['user_id'] == user_id]['post_id'])
        
        print(f"\n📊 Scoring posts from similar users:")
        for similar_user in similar_users:
            sim_user_id = similar_user['user_id']
            similarity = similar_user['similarity']
            
            sim_user_likes = self.likes_df[
                (self.likes_df['user_id'] == sim_user_id) & 
                (self.likes_df['post_id'].isin(post_ids))
            ]
            
            for _, like in sim_user_likes.iterrows():
                post_id = like['post_id']
                if post_id not in user_likes:
                    score = like['like_score'] * similarity
                    recommendation_scores[post_id] = recommendation_scores.get(post_id, 0) + score
                    print(f"   - Post {post_id}: +{score:.3f} (from User {sim_user_id})")
        
        if recommendation_scores:
            sorted_recommendations = sorted(
                recommendation_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            final_recommendations = [post_id for post_id, score in sorted_recommendations[:num_recommendations]]
            
            print(f"\n🏆 TOP RECOMMENDATIONS for User {user_id}:")
            for i, (post_id, score) in enumerate(sorted_recommendations[:num_recommendations], 1):
                print(f"   {i}. Post {post_id} (score: {score:.3f})")
            
            return final_recommendations
        else:
            print("⚠️ No recommendations generated. Using popular posts.")
            return self._get_popular_posts(post_ids, num_recommendations)
        
    def recommend_posts(self, user_id, post_ids, num_recommendations=10):
        """Generate recommendations using combined user-user collaborative filtering"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        print("++++++++")
        print(self.user_ids)
        if user_id not in self.user_ids:
            print(f"❌ User {user_id} not found in training data. Using popular posts.")
            return self._get_popular_posts(post_ids, num_recommendations)
        
        print(f"\n🎯 Generating recommendations for User {user_id}")
        print(f"📝 Available posts: {len(post_ids)}")
        
        similar_users = self.find_similar_users(user_id, n_similar=5, similarity_type="combined")
        
        if not similar_users:
            print("⚠️ No similar users found. Using popular posts.")
            return self._get_popular_posts(post_ids, num_recommendations)
        
        print(f"👥 Found {len(similar_users)} similar users:")
        for similar in similar_users:
            print(f"   - User {similar['user_id']} (similarity: {similar['similarity']:.3f})")
        
        recommendation_scores = {}
        user_likes = set(self.likes_df[self.likes_df['user_id'] == user_id]['post_id'])
        
        print(f"\n📊 Scoring posts from similar users:")
        for similar_user in similar_users:
            sim_user_id = similar_user['user_id']
            similarity = similar_user['similarity']
            
            sim_user_likes = self.likes_df[
                (self.likes_df['user_id'] == sim_user_id) & 
                (self.likes_df['post_id'].isin(post_ids))
            ]
            
            for _, like in sim_user_likes.iterrows():
                post_id = like['post_id']
                if post_id not in user_likes:
                    score = like['like_score'] * similarity
                    recommendation_scores[post_id] = recommendation_scores.get(post_id, 0) + score
                    print(f"   - Post {post_id}: +{score:.3f} (from User {sim_user_id})")
        
        if recommendation_scores:
            sorted_recommendations = sorted(
                recommendation_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            final_recommendations = [post_id for post_id, score in sorted_recommendations[:num_recommendations]]
            
            print(f"\n🏆 TOP RECOMMENDATIONS for User {user_id}:")
            posts_recommendations = []
            for i, (post_id, score) in enumerate(sorted_recommendations[:num_recommendations], 1):
                print(f"   {i}. Post {post_id} (score: {score:.3f})")
                posts_recommendations.append({"post_id": post_id, "score": f"{score:.3f}"})
            
            return posts_recommendations
        else:
            print("⚠️ No recommendations generated. Using popular posts.")
            return self._get_popular_posts(post_ids, num_recommendations)
    
    def _get_popular_posts(self, post_ids, num_recommendations):
        """Get popular posts from available list"""
        if self.item_popularity.empty:
            return post_ids[:num_recommendations]
        
        available_popular = [post for post in self.item_popularity.index if post in post_ids]
        return available_popular[:num_recommendations]
    
    def get_similarity_breakdown(self, user_id1, user_id2):
        """Get detailed similarity breakdown between two users"""
        if user_id1 not in self.user_ids or user_id2 not in self.user_ids:
            return None
        
        idx1 = self.user_ids.index(user_id1)
        idx2 = self.user_ids.index(user_id2)
        
        likes_sim = self.user_similarity_likes[idx1, idx2]
        followers_sim = self.user_similarity_followers[idx1, idx2]
        promo_sim = self.user_similarity_promo[idx1, idx2]
        combined_sim = self.user_similarity_combined[idx1, idx2]
        
        return {
            'likes_similarity': likes_sim,
            'followers_similarity': followers_sim,
            'promo_similarity': promo_sim,
            'combined_similarity': combined_sim,
            'weighted_breakdown': {
                'likes_contribution': 0.6 * likes_sim,
                'followers_contribution': 0.2 * followers_sim,
                'promo_contribution': 0.2 * promo_sim
            }
        }
    
    def demo_recommendations(self, user_ids=None, num_posts=10):
        """Demonstrate recommendations for specific users"""
        if user_ids is None:
            user_ids = self.user_ids[:3]  # Demo for first 3 users
        
        # Get some available posts for recommendation
        available_posts = self.posts_df['post_id'].tolist()[:num_posts] if not self.posts_df.empty else list(range(1, num_posts+1))
        
        print("\n" + "="*80)
        print("🎭 DEMONSTRATION DES RECOMMANDATIONS")
        print("="*80)
        
        for user_id in user_ids:
            if user_id in self.user_ids:
                print(f"\n🧑 User {user_id} Recommendations:")
                print("-" * 50)
                
                # Get detailed recommendations
                detailed_recs = self.recommend_with_details(user_id, available_posts, 5)
                
                if detailed_recs:
                    for i, rec in enumerate(detailed_recs, 1):
                        print(f"{i}. Post {rec['post_id']} (Author: {rec['author_id']})")
                        print(f"   📝 {rec['content'][:100]}...")
                        printd(f"   ❤️  {rec['likes']} likes | 💬 {rec['comments']} comments")
                        print()
                else:
                    print("   Aucune recommandation disponible")
    
    # def batch_recommend(self, test_file, output_file):
    #     """Generate recommendations for test users"""
    #     test_df = pd.read_csv(test_file)
    #     results = []
        
    #     print(f"\n📦 Processing batch recommendations for {len(test_df)} users...")
        
    #     for _, row in test_df.iterrows():
    #         user_id = row['user_id']
    #         post_ids = row['post_ids'].split('|')
            
    #         recommendations = self.recommend(user_id, post_ids, 10)
            
    #         results.append({
    #             'user_id': user_id,
    #             'recommendations': '|'.join(map(str, recommendations)),
    #             'count': len(recommendations)
    #         })
        
    #     result_df = pd.DataFrame(results)
    #     result_df.to_csv(output_file, index=False)
    #     print(f"✅ Recommendations saved to {output_file}")
    #     return result_df

# Usage example
# if __name__ == "__main__":
#     # Configure your database connection
#     db_config = {
#         'host': 'localhost',
#         'database': 'etsia_ai',
#         'user': 'postgres',
#         'password': 'JaAk',
#         'port': '5432'
#     }
    
#     # Train user-user collaborative filtering
#     print("\n🎯 Training User-User Collaborative Filtering...")
#     recommender = UserUserRecommender(min_similarity=0.1, db_config=db_config)
#     recommender.load_and_train()
    
#     # Test similar users finding
#     test_user = 1  # Use actual user ID from your database
#     similar_users = recommender.find_similar_users(test_user)
    
#     print(f"\n👥 Similar users to {test_user} (Combined Similarity):")
#     for similar in similar_users[:3]:
#         print(f"  - User {similar['user_id']} (combined: {similar['similarity']:.3f})")
#         breakdown = recommender.get_similarity_breakdown(test_user, similar['user_id'])
#         if breakdown:
#             print(f"     Likes: {breakdown['likes_similarity']:.3f}, "
#                   f"Followers: {breakdown['followers_similarity']:.3f}, "
#                   f"Promo: {breakdown['promo_similarity']:.3f}")
    
#     # Test similarity breakdown
#     print(f"\n🔍 Similarity breakdown example:")
#     if len(recommender.user_ids) >= 2:
#         user1, user2 = recommender.user_ids[0], recommender.user_ids[1]
#         breakdown = recommender.get_similarity_breakdown(user1, user2)
#         if breakdown:
#             print(f"Between {user1} and {user2}:")
#             print(f"  Combined: {breakdown['combined_similarity']:.3f}")
#             print(f"  Likes: {breakdown['likes_similarity']:.3f} (contribution: {breakdown['weighted_breakdown']['likes_contribution']:.3f})")
#             print(f"  Followers: {breakdown['followers_similarity']:.3f} (contribution: {breakdown['weighted_breakdown']['followers_contribution']:.3f})")
#             print(f"  Promotion: {breakdown['promo_similarity']:.3f} (contribution: {breakdown['weighted_breakdown']['promo_contribution']:.3f})")
    
#     # Demo recommendations with detailed prints
#     print(f"\n🎪 DEMO RECOMMENDATIONS")
#     print("="*60)
    
#     # Get available posts for demo
#     available_posts = recommender.posts_df['post_id'].tolist()[:15] if hasattr(recommender, 'posts_df') and not recommender.posts_df.empty else list(range(1, 16))
    
#     # Test recommendations for first few users
#     demo_users = recommender.user_ids[:3] if recommender.user_ids else [1, 2, 3]
    
#     for user_id in demo_users:
#         print(f"\n🧑 RECOMMANDATIONS POUR USER {user_id}:")
#         print("-" * 50)
        
#         recommendations = recommender.recommend(user_id, available_posts, 5)
        
#         if recommendations:
#             post_details = recommender.get_post_details(recommendations)
#             for i, post_id in enumerate(recommendations, 1):
#                 details = post_details.get(post_id, {})
#                 print(f"{i}. 📍 Post ID: {post_id}")
#                 print(f"   📝 Content: {details.get('content', 'N/A')[:80]}...")
#                 print(f"   👤 Author: User {details.get('author_id', 'N/A')}")
#                 print(f"   📊 Stats: {details.get('likes', 0)} ❤️ | {details.get('comments', 0)} 💬")
#                 print()
#         else:
#             print("   Aucune recommandation disponible pour cet utilisateur")
#         print("-" * 50)
    
#     # Generate batch recommendations if test file exists
#     # try:
#     #     results = recommender.batch_recommend('test.csv', 'user_user_recommendations.csv')
        
#     #     # Show sample results
#     #     print("\n📋 Batch Recommendations Results:")
#     #     for i, row in results.head().iterrows():
#     #         print(f"User: {row['user_id']}")
#     #         recs = row['recommendations'].split('|')[:5]
#     #         print(f"Top 5: {recs}")
#     #         print("-" * 50)
#     # except Exception as e:
#     #     print(f"⚠️ Batch recommendation skipped: {e}")