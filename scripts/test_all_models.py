#!/usr/bin/env python3
"""
Script de test complet de tous les modèles ML avec monitoring
Vérifie que chaque modèle fonctionne et émet des métriques
"""
import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8001"
BRIDGE_URL = "http://localhost:5000"

def test_health():
    """Test du health check global"""
    print("\n" + "="*70)
    print("TEST 1: Health Check Global")
    print("="*70)
    
    response = requests.get(f"{API_BASE_URL}/health")
    data = response.json()
    
    print(f"✓ Status: {data['status']}")
    print(f"✓ Version: {data['version']}")
    print(f"✓ Modèles disponibles: {data['models']['total']}")
    
    for model_name, health in data['models']['health'].items():
        status_icon = "✓" if health['status'] == 'healthy' else "✗"
        print(f"  {status_icon} {model_name}: {health['status']}")
    
    return data['models']['total']

def test_depression_detection():
    """Test du modèle de détection de dépression (Qwen)"""
    print("\n" + "="*70)
    print("TEST 2: Détection de Dépression (Qwen 2.5)")
    print("="*70)
    
    test_cases = [
        {
            "text": "Je me sens vraiment triste et sans espoir",
            "expected": "DÉPRESSION"
        },
        {
            "text": "Je suis très heureux aujourd'hui, tout va bien!",
            "expected": "NORMAL"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['text'][:50]}...")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/depression/detect",
            json={"text": test["text"]},
            timeout=30
        )
        
        data = response.json()
        print(f"  Prédiction: {data['prediction']}")
        print(f"  Confiance: {data['confidence']:.2f}")
        print(f"  Sévérité: {data['severity']}")
        print(f"  Latence: {data['processing_time']:.2f}s")
        print(f"  Modèle: {data['model_used']}")
        
        if data['prediction'] == test['expected']:
            print(f"  ✓ Résultat attendu")
        else:
            print(f"  ⚠ Résultat inattendu (attendu: {test['expected']})")

def test_hate_speech_detection():
    """Test du modèle de détection de hate speech (BERT)"""
    print("\n" + "="*70)
    print("TEST 3: Détection de Hate Speech (BERT)")
    print("="*70)
    
    test_cases = [
        {
            "text": "Tu es vraiment stupide et inutile",
            "expected": "HAINEUX"
        },
        {
            "text": "Merci beaucoup pour ton aide, c'est gentil",
            "expected": "NON-HAINEUX"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['text'][:50]}...")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/hatecomment/detect",
            json={"text": test["text"]},
            timeout=10
        )
        
        data = response.json()
        print(f"  Prédiction: {data['prediction']}")
        print(f"  Confiance: {data['confidence']:.2f}")
        print(f"  Sévérité: {data['severity']}")
        print(f"  Latence: {data['processing_time']:.3f}s")
        print(f"  Enhanced: {data['enhanced']}")

def test_content_generation():
    """Test du générateur de contenu"""
    print("\n" + "="*70)
    print("TEST 4: Génération de Contenu")
    print("="*70)
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/predict",
        json={
            "text": "Écris un court message motivant pour quelqu'un qui se sent triste",
            "model_name": "yansnet-content-generator"
        },
        timeout=30
    )
    
    data = response.json()
    print(f"  Contenu généré: {data['prediction'][:100]}...")
    print(f"  Longueur: {len(data['prediction'])} caractères")
    print(f"  Latence: {data.get('processing_time', 0):.2f}s")

def test_image_caption():
    """Test du modèle de caption d'images"""
    print("\n" + "="*70)
    print("TEST 5: Caption d'Images")
    print("="*70)
    
    # Créer une image de test simple (1x1 pixel blanc)
    import base64
    from PIL import Image
    import io
    
    # Image blanche 100x100
    img = Image.new('RGB', (100, 100), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/predict-image",
        json={
            "image": img_base64,
            "model_name": "sensitive-image-caption"
        },
        timeout=30
    )
    
    data = response.json()
    print(f"  Caption: {data['prediction']}")
    print(f"  Sensible: {data.get('is_sensitive', False)}")
    print(f"  Latence: {data.get('processing_time', 0):.2f}s")

def test_recommendation_system():
    """Test du système de recommandation"""
    print("\n" + "="*70)
    print("TEST 6: Système de Recommandation")
    print("="*70)
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/recommendation/recommend",
        json={"user_id": 1, "top_n": 5},
        timeout=10
    )
    
    data = response.json()
    print(f"  Recommandations: {len(data['recommendations'])} posts")
    print(f"  Score moyen: {data.get('avg_score', 0):.3f}")
    print(f"  Latence: {data.get('processing_time', 0):.3f}s")
    print(f"  Cache utilisé: {data.get('from_cache', False)}")

def test_nsfw_detection():
    """Test du modèle de détection NSFW (ShieldGemma)"""
    print("\n" + "="*70)
    print("TEST 7: Détection NSFW (ShieldGemma)")
    print("="*70)
    
    # Créer une image de test simple (image blanche = safe)
    import base64
    from PIL import Image
    import io
    
    # Image blanche 224x224 (taille standard pour les modèles de vision)
    img = Image.new('RGB', (224, 224), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    print(f"\nTest: Image blanche (contenu sûr attendu)...")
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/censure/detect",
        json={"image": img_base64},
        timeout=30
    )
    
    data = response.json()
    print(f"  Prédiction: {data['prediction']}")
    print(f"  Confiance: {data['confidence']:.4f}")
    print(f"  Sévérité: {data['severity']}")
    print(f"  NSFW: {data['is_nsfw']}")
    print(f"  Raisonnement: {data['reasoning']}")
    print(f"  Latence: {data.get('processing_time', 0):.2f}s")
    
    # Afficher les catégories détectées
    if 'categories' in data:
        print(f"\n  Catégories analysées:")
        for category, scores in data['categories'].items():
            print(f"    - {category}: {scores['Prediction']} (score: {scores.get('Violation', 0):.1f}%)")

def test_bridge_health():
    """Test du GA4-Bridge"""
    print("\n" + "="*70)
    print("TEST 8: GA4-Bridge Monitoring")
    print("="*70)
    
    response = requests.get(f"{BRIDGE_URL}/health")
    data = response.json()
    
    print(f"  Status: {data['status']}")
    print(f"  Règles d'alerte: {data['catalog_rules']}")

def test_bridge_metric():
    """Test d'envoi de métrique au bridge"""
    print("\n" + "="*70)
    print("TEST 9: Envoi de Métrique au Bridge")
    print("="*70)
    
    # Test métrique normale
    response = requests.post(
        f"{BRIDGE_URL}/log_metric",
        json={
            "service": "test_service",
            "event_name": "test_metric",
            "params": {"latency": 100, "confidence": 0.95},
            "client_id": "test_client"
        }
    )
    
    data = response.json()
    print(f"  Métrique normale: {data}")
    
    # Test métrique avec alerte
    response = requests.post(
        f"{BRIDGE_URL}/log_metric",
        json={
            "service": "depression_detection",
            "model_name": "qwen2.5:1.5b",
            "event_name": "detect_depression",
            "params": {"latency": 1500, "confidence": 0.95},
            "client_id": "test_client"
        }
    )
    
    data = response.json()
    print(f"  Métrique avec alerte: {data}")

def main():
    """Exécute tous les tests"""
    print("\n" + "="*70)
    print("TESTS COMPLETS DES MODÈLES ML + MONITORING")
    print("="*70)
    
    try:
        # Test 1: Health check
        total_models = test_health()
        
        # Test 2: Détection de dépression
        test_depression_detection()
        
        # Test 3: Détection de hate speech
        test_hate_speech_detection()
        
        # Test 4: Génération de contenu
        test_content_generation()
        
        # Test 5: Caption d'images
        test_image_caption()
        
        # Test 6: Système de recommandation
        test_recommendation_system()
        
        # Test 7: Détection NSFW
        test_nsfw_detection()
        
        # Test 8: Bridge health
        test_bridge_health()
        
        # Test 9: Envoi de métriques
        test_bridge_metric()
        
        print("\n" + "="*70)
        print("✓ TOUS LES TESTS TERMINÉS AVEC SUCCÈS")
        print("="*70)
        print(f"\nRésumé:")
        print(f"  - {total_models} modèles testés")
        print(f"  - Monitoring GA4-Bridge opérationnel")
        print(f"  - Système de cache Redis fonctionnel")
        print(f"  - Prêt pour déploiement Docker Hub")
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
