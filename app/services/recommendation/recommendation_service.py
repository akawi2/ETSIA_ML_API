from app.models.recommendation_model import UserUserRecommender


# def recommend_service(user_id):
#         # Configure your database connection
#         db_config = {
#             'host': 'localhost',
#             'database': 'etsia_ai',
#             'user': 'postgres',
#             'password': 'JaAk',
#             'port': '5432'
#         }
        
#         # Train user-user collaborative filtering
#         print("\n🎯 Training User-User Collaborative Filtering...")
#         recommender = UserUserRecommender(min_similarity=0.1, db_config=db_config)
#         recommender.load_and_train()
   
        
#         # Get available posts for demo
#         available_posts = recommender.posts_df['post_id'].tolist()[:15] if hasattr(recommender, 'posts_df') and not recommender.posts_df.empty else list(range(1, 16))
#         recommendations  = recommender.recommend_posts(user_id, available_posts, 10)
#         formatted_recommendations = [ {'post_id': int(rec['post_id']), 'score': rec['score']} for rec in recommendations  ]
#         return formatted_recommendations

def recommend_service(user_id):
    # Configure your database connection
    
    db_config = {
        'host': 'localhost',
        'database': 'etsia_ai',
        'user': 'postgres',
        'password': 'JaAk',
        'port': '5432'
    }
    
    # Train user-user collaborative filtering
    print("\n🎯 Training User-User Collaborative Filtering...")
    recommender = UserUserRecommender(min_similarity=0.1, db_config=db_config)
    recommender.load_and_train()
    
    # Get available posts for demo
    available_posts = recommender.posts_df['post_id'].tolist()[:15] if hasattr(recommender, 'posts_df') and not recommender.posts_df.empty else list(range(1, 16))
    recommendations = recommender.recommend_posts(user_id, available_posts, 10)
    
    # Extract post IDs from recommendations
    recommended_post_ids = [int(rec['post_id']) for rec in recommendations]
    
    # Get full post data with media using the existing method
    posts_with_media = recommender.get_posts_with_media(recommended_post_ids)
    
    # Combine recommendation scores with post data
    formatted_recommendations = []
    for rec in recommendations:
        post_id = int(rec['post_id'])
        # Find the corresponding post in the posts_with_media list
        post_data = next((post for post in posts_with_media if post['post_id'] == post_id), None)
        
        if post_data:
            formatted_rec = {
                'post_id': post_id,
                'score': rec['score'],
                'title': post_data.get('title'),
                'content': post_data.get('content'),
                'created_at': post_data.get('created_at'),
                'user_id': post_data.get('user_id'),
                'media': post_data.get('media', [])
            }
            formatted_recommendations.append(formatted_rec)
        else:
            # Fallback if post data couldn't be fetched
            formatted_rec = {
                'post_id': post_id,
                'score': rec['score'],
                'title': f"Post {post_id}",
                'content': "Content not available",
                'created_at': None,
                'user_id': None,
                'media': []
            }
            formatted_recommendations.append(formatted_rec)
    
    return formatted_recommendations
        
