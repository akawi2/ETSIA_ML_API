#!/usr/bin/env python3
"""
Script de test automatique pour les 6 modèles YANSNET
"""
import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test 0: Health check global"""
    print("\n" + "="*70)
    print("🏥 TEST 0: Health Check Global")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"✅ Version: {data['version']}")
            print(f"✅ Modèles disponibles: {data['models']['total']}")
            print(f"   {', '.join(data['models']['available'])}")
            return True
        else:
            print(f"❌ Health check échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print(f"   Vérifiez que l'API est lancée sur {BASE_URL}")
        return False


def test_yansnet_llm():
    """Test 1: YANSNET LLM - Détection de dépression"""
    print("\n" + "="*70)
    print("1️⃣  TEST 1: YANSNET LLM - Détection de Dépression")
    print("="*70)
    
    tests = [
        {
            "name": "Texte dépressif",
            "text": "Je me sens tellement triste et sans espoir",
            "expected": "DÉPRESSION"
        },
        {
            "name": "Texte normal",
            "text": "Je suis très heureux aujourd'hui",
            "expected": "NORMAL"
        }
    ]
    
    for test in tests:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/predict",
                json={"text": test["text"], "include_reasoning": False},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                prediction = data.get("prediction")
                confidence = data.get("confidence", 0)
                
                if prediction == test["expected"]:
                    print(f"✅ {test['name']}: {prediction} (confiance: {confidence:.2%})")
                else:
                    print(f"⚠️  {test['name']}: {prediction} (attendu: {test['expected']})")
            else:
                print(f"❌ {test['name']}: Erreur {response.status_code}")
        except Exception as e:
            print(f"❌ {test['name']}: {e}")


def test_hatecomment_bert():
    """Test 2: HateComment BERT - Détection hate speech"""
    print("\n" + "="*70)
    print("2️⃣  TEST 2: HateComment BERT - Détection Hate Speech")
    print("="*70)
    
    tests = [
        {
            "name": "Hate speech",
            "text": "Je déteste ces gens, ils sont tous nuls",
            "expected": "HAINEUX"
        },
        {
            "name": "Texte normal",
            "text": "Bonjour, comment allez-vous ?",
            "expected": "NON-HAINEUX"
        }
    ]
    
    for test in tests:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/hatecomment/detect",
                json={"text": test["text"], "include_reasoning": False},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                prediction = data.get("prediction")
                confidence = data.get("confidence", 0)
                
                if prediction == test["expected"]:
                    print(f"✅ {test['name']}: {prediction} (confiance: {confidence:.2%})")
                else:
                    print(f"⚠️  {test['name']}: {prediction} (attendu: {test['expected']})")
            else:
                print(f"❌ {test['name']}: Erreur {response.status_code}")
        except Exception as e:
            print(f"❌ {test['name']}: {e}")


def test_censure():
    """Test 3: Censure - Détection NSFW"""
    print("\n" + "="*70)
    print("3️⃣  TEST 3: Censure - Détection NSFW")
    print("="*70)
    
    # Vérifier si une image de test existe
    test_images = ["test_image.jpg", "cat.jpg", "image.jpg"]
    image_path = None
    
    for img in test_images:
        if Path(img).exists():
            image_path = img
            break
    
    if not image_path:
        print("⚠️  Aucune image de test trouvée")
        print("   Créez un fichier 'test_image.jpg' pour tester ce modèle")
        return
    
    try:
        with open(image_path, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/api/v1/censure/predict-image",
                files={"image": f},
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            prediction = data.get("prediction")
            confidence = data.get("confidence", 0)
            is_safe = data.get("is_safe", False)
            
            print(f"✅ Image analysée: {prediction} (confiance: {confidence:.2%})")
            print(f"   Sûr: {is_safe}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def test_sensitive_image_caption():
    """Test 4: Sensitive Image Caption - Analyse contenu sensible"""
    print("\n" + "="*70)
    print("4️⃣  TEST 4: Sensitive Image Caption - Analyse Contenu")
    print("="*70)
    
    # Vérifier si une image de test existe
    test_images = ["test_image.jpg", "cat.jpg", "image.jpg"]
    image_path = None
    
    for img in test_images:
        if Path(img).exists():
            image_path = img
            break
    
    if not image_path:
        print("⚠️  Aucune image de test trouvée")
        print("   Créez un fichier 'test_image.jpg' pour tester ce modèle")
        return
    
    try:
        with open(image_path, "rb") as f:
            response = requests.post(
                f"{BASE_URL}/api/v1/predict-image",
                files={"image": f},
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            prediction = data.get("prediction")
            caption_fr = data.get("caption_fr", "N/A")
            is_safe = data.get("is_safe", False)
            
            print(f"✅ Image analysée: {prediction}")
            print(f"   Légende: {caption_fr}")
            print(f"   Sûr: {is_safe}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def test_recommendation():
    """Test 5: Recommendation - Système de recommandation"""
    print("\n" + "="*70)
    print("5️⃣  TEST 5: Recommendation - Système de Recommandation")
    print("="*70)
    
    try:
        response = requests.get(
            f"{BASE_URL}/recommend",
            params={"userId": 1},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            
            print(f"✅ Recommandations pour user 1: {len(recommendations)} posts")
            if recommendations:
                print(f"   Premiers posts recommandés:")
                for i, rec in enumerate(recommendations[:3], 1):
                    if isinstance(rec, dict):
                        post_id = rec.get("post_id", "N/A")
                        score = rec.get("score", 0)
                        print(f"   {i}. Post {post_id} (score: {score:.2f})")
                    else:
                        print(f"   {i}. {rec}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def test_content_generator():
    """Test 6: Content Generator - Génération de contenu"""
    print("\n" + "="*70)
    print("6️⃣  TEST 6: Content Generator - Génération de Contenu")
    print("="*70)
    
    try:
        # Test 1: Post aléatoire
        response = requests.post(
            f"{BASE_URL}/api/v1/content/generate-post",
            json={},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            post_type = data.get("post_type", "N/A")
            
            print(f"✅ Post généré ({post_type}):")
            print(f"   {content[:100]}...")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            
        # Test 2: Post avec commentaires
        response = requests.post(
            f"{BASE_URL}/api/v1/content/generate-post-with-comments",
            json={"num_comments": 3},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            total_comments = data.get("total_comments", 0)
            print(f"✅ Post complet généré avec {total_comments} commentaires")
        else:
            print(f"⚠️  Génération avec commentaires: Erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    """Fonction principale"""
    print("\n" + "🧪 "*20)
    print("TEST AUTOMATIQUE DES 6 MODÈLES YANSNET")
    print("🧪 "*20)
    
    # Test 0: Health check
    if not test_api_health():
        print("\n❌ L'API n'est pas accessible. Arrêt des tests.")
        print(f"   Lancez l'API avec: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Tests des 6 modèles
    test_yansnet_llm()
    test_hatecomment_bert()
    test_censure()
    test_sensitive_image_caption()
    test_recommendation()
    test_content_generator()
    
    # Résumé
    print("\n" + "="*70)
    print("✅ TESTS TERMINÉS")
    print("="*70)
    print("\nPour plus de détails, consultez:")
    print("  - Documentation: http://localhost:8000/docs")
    print("  - Guide de test: TEST_ENDPOINTS.md")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
