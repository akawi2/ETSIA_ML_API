from app.models.recommendation_model import UserUserRecommender


def recommend_service(user_id):
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
        recommendations  = recommender.recommend_posts(user_id, available_posts, 10)
        formatted_recommendations = [ {'post_id': int(rec['post_id']), 'score': rec['score']} for rec in recommendations  ]
        return formatted_recommendations
        
