#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Génération de 30 posts et de 8 à 12 commentaires chacun,
avec barre de progression, estimation du temps restant et retries
en cas d’erreur de modèle. Exports : posts.json, comments.json,
data.json (posts + leurs commentaires), posts.csv, comments.csv.
"""

import random
import json
import csv
import time
from tqdm import tqdm

try:
    import ollama
except ImportError:
    raise ImportError("Installez la bibliothèque Ollama : pip install ollama")

MODEL = "llama3.1"
TEMPERATURE = 0.9

post_types = [
    "confession", "coup de gueule", "demande d'aide",
    "message de soutien", "blague", "information utile"
]
sentiments = ["positif", "neutre", "négatif"]
topics = [
    "les partiels stressants", "la vie en résidence universitaire",
    "le stage de fin d'études", "les associations étudiantes",
    "le planning des cours", "les notes et résultats",
    "les échanges internationaux", "le covoiturage pour l'école",
    "la cantine de l'école", "les problèmes de logement",
    "le stress avant les examens", "les fêtes étudiantes",
    "les relations étudiants-professeurs", "la recherche de mentors",
    "les concours de programmation", "le hackathon de l'école",
    "les voyages d'études", "les bourses et financements",
    "le nouveau bâtiment sportif", "les salles d'étude bondées"
]

system_prompt_post = (
    "Vous êtes un assistant chargé de générer des publications crédibles "
    "pour un forum d'école d'ingénieurs, sans marqueurs artificiels ni phrases incomplètes."
)
system_prompt_comment = (
    "Vous êtes un assistant chargé de générer des commentaires réalistes sur un forum étudiant, "
    "sans marqueurs artificiels ni phrases incomplètes."
)

def retry_chat(messages):
    """
    Appelle ollama.chat avec retries et back-off.
    """
    for attempt in range(1, 4):
        try:
            return ollama.chat(
                model=MODEL,
                messages=messages,
                options={"temperature": TEMPERATURE}
            )["message"]["content"].strip()
        except Exception as e:
            print(f"[retry_chat] tentative {attempt} échouée : {e}")
            time.sleep(2 * attempt)
    raise RuntimeError("Échec répété de l'appel au modèle après 3 tentatives")

def generate_post():
    post_type = random.choice(post_types)
    if post_type == "coup de gueule": sentiment = "négatif"
    elif post_type == "message de soutien": sentiment = "positif"
    elif post_type == "blague": sentiment = random.choice(["positif", "neutre"])
    elif post_type == "information utile": sentiment = "neutre"
    elif post_type == "confession": sentiment = random.choice(["positif", "négatif"])
    else: sentiment = random.choice(sentiments)

    topic = random.choice(topics)
    prompt = (
        f"Génère un post '{post_type}' sur '{topic}', avec un sentiment '{sentiment}'. "
        "Minimum 3 phrases, crédible, sans préfixes ni phrases incomplètes."
    )
    text = retry_chat([
        {"role": "system", "content": system_prompt_post},
        {"role": "user",   "content": prompt}
    ])
    if text and text[-1] not in ".?!":
        text += "."
    return text, post_type, sentiment

def generate_comments(post_text, count):
    out = []
    for _ in range(count):
        sent = random.choice(sentiments)
        prompt = (
            f"Post : \"{post_text}\". Génère un commentaire avec sentiment '{sent}', "
            "au moins 2 phrases, naturel, sans préfixes ni phrases incomplètes."
        )
        com = retry_chat([
            {"role": "system", "content": system_prompt_comment},
            {"role": "user",   "content": prompt}
        ])
        if com and com[-1] not in ".?!":
            com += "."
        out.append((com, sent))
    return out

def main():
    total_posts = 30
    posts = []
    comments = []
    aggregated = []

    post_id = 1
    comment_id = 1
    start_time = time.time()

    for _ in tqdm(range(total_posts), desc="Génération posts", unit="post"):
        p_text, p_type, p_sent = generate_post()
        posts.append({
            "post_id": post_id,
            "context": p_text,
            "post_type": p_type,
            "sentiment": p_sent
        })

        n_comments = random.randint(8, 12)
        linked = []
        for _ in range(n_comments):
            c_text, c_sent = generate_comments(p_text, 1)[0]
            comments.append({
                "comment_id": comment_id,
                "post_id": post_id,
                "content": c_text,
                "sentiment": c_sent
            })
            linked.append({
                "comment_id": comment_id,
                "content": c_text,
                "sentiment": c_sent
            })
            comment_id += 1

        aggregated.append({
            "post_id": post_id,
            "context": p_text,
            "post_type": p_type,
            "sentiment": p_sent,
            "comments": linked
        })

        post_id += 1
        elapsed = time.time() - start_time
        avg = elapsed / post_id
        remaining = avg * (total_posts - post_id + 1)
        tqdm.write(f"Écoulé: {elapsed:.1f}s • Restant ≈ {remaining:.1f}s")

    # Exports JSON
    with open("posts.json",    "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, indent=2, ensure_ascii=False)
    with open("data.json",     "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2, ensure_ascii=False)

    # Exports CSV
    with open("posts.csv",    "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["post_id","context","post_type","sentiment"])
        writer.writeheader()
        writer.writerows(posts)
    with open("comments.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["comment_id","post_id","content","sentiment"])
        writer.writeheader()
        writer.writerows(comments)

    print(f"\nTerminé : {len(posts)} posts, {len(comments)} commentaires générés.")
    print("Fichiers : posts.json, comments.json, data.json, posts.csv, comments.csv")

if __name__ == "__main__":
    main()
