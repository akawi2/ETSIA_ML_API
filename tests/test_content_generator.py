#!/usr/bin/env python3
"""
Script de test rapide pour le générateur de contenu YANSNET
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_health():
    """Test du health check"""
    print("🔍 Test du health check...")
    response = requests.get(f"{BASE_URL}/api/v1/models/yansnet-content-generator/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_generate_post():
    """Test de génération de post"""
    print("📝 Test de génération de post...")
    response = requests.post(
        f"{BASE_URL}/api/v1/content/generate-post",
        json={
            "post_type": "demande d'aide",
            "topic": "les partiels stressants"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Type: {data['post_type']}")
    print(f"Topic: {data['topic']}")
    print(f"Sentiment: {data['sentiment']}")
    print(f"Contenu:\n{data['content']}")
    print()
    return data['content']

def test_generate_comments(post_content):
    """Test de génération de commentaires"""
    print("💬 Test de génération de commentaires...")
    response = requests.post(
        f"{BASE_URL}/api/v1/content/generate-comments",
        json={
            "post_content": post_content,
            "num_comments": 3,
            "sentiment": "positif"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total: {data['total_comments']} commentaires")
    for comment in data['comments']:
        print(f"  {comment['comment_number']}. [{comment['sentiment']}] {comment['content']}")
    print()

def test_generate_post_with_comments():
    """Test de génération de post complet"""
    print("🎯 Test de génération de post complet avec commentaires...")
    response = requests.post(
        f"{BASE_URL}/api/v1/content/generate-post-with-comments",
        json={
            "post_type": "blague",
            "topic": "les fêtes étudiantes",
            "num_comments": 5
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    
    print(f"\n📄 POST:")
    print(f"Type: {data['post']['post_type']}")
    print(f"Topic: {data['post']['topic']}")
    print(f"Contenu:\n{data['post']['content']}")
    
    print(f"\n💬 COMMENTAIRES ({data['total_comments']}):")
    for comment in data['comments']:
        print(f"  {comment['comment_number']}. [{comment['sentiment']}] {comment['content']}")
    print()

def test_list_models():
    """Test de la liste des modèles"""
    print("📋 Liste des modèles disponibles...")
    response = requests.get(f"{BASE_URL}/api/v1/models")
    data = response.json()
    print(f"Total: {data['total']} modèles")
    print(f"Défaut: {data['default']}")
    for name, info in data['models'].items():
        marker = " [DÉFAUT]" if info['is_default'] else ""
        print(f"  • {name} v{info['version']} by {info['author']}{marker}")
    print()

if __name__ == "__main__":
    print("="*70)
    print("🧪 TEST DU GÉNÉRATEUR DE CONTENU YANSNET")
    print("="*70)
    print()
    
    try:
        # 1. Vérifier que l'API est accessible
        print("🔌 Vérification de l'API...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ L'API n'est pas accessible. Lancez-la avec: uvicorn app.main:app --reload")
            exit(1)
        print("✅ API accessible\n")
        
        # 2. Lister les modèles
        test_list_models()
        
        # 3. Health check du générateur
        test_health()
        
        # 4. Générer un post
        post_content = test_generate_post()
        sleep(1)
        
        # 5. Générer des commentaires
        test_generate_comments(post_content)
        sleep(1)
        
        # 6. Générer un post complet
        test_generate_post_with_comments()
        
        print("="*70)
        print("✅ TOUS LES TESTS SONT PASSÉS !")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API.")
        print("   Lancez l'API avec: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
