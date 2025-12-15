from faker import Faker
import random
import pandas as pd
fake = Faker()

# Générer des utilisateurs
users = [{'user_id': i+1, 'name': fake.name(), 'email': fake.email()} for i in range(10)]

# Générer des posts
posts = []
for i in range(20):
    post = {
        'post_id': i+1,
        'user_id': random.choice(range(1, 11)),  # Associer à un utilisateur existant
        'content': fake.paragraph(),
        'image_url': fake.image_url(),
        'created_at': fake.date_time_this_year(),
        'likes': random.randint(0, 100)
    }
    posts.append(post)

# Générer des commentaires pour chaque post
for post in posts:
    num_comments = random.randint(0, 10)
    post['comments'] = [{'comment_id': j+1, 'user_id': random.choice(range(1, 11)),
                         'content': fake.sentence(), 'created_at': fake.date_time_this_year()}
                        for j in range(num_comments)]

# Exporter en CSV pour chaque entité
pd.DataFrame(users).to_csv('users.csv', index=False)
pd.DataFrame(posts).to_csv('posts.csv', index=False)
# Pour les commentaires, vous devrez peut-être ajuster selon votre structure