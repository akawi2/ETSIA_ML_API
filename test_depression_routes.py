"""
Script de test automatique pour les routes Depression Detection
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Affiche un titre de section"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_result(test_name, success, details=""):
    """Affiche le résultat d'un test"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"     {details}")

def test_health():
    """Test health check"""
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/depression/health")
        result = response.json()
        
        print(json.dumps(result, indent=2))
        
        success = (
            response.status_code == 200 and
            result.get("status") == "healthy" and
            result.get("model") == "yansnet-llm"
        )
        
        print_result(
            "Health Check",
            success,
            f"Status: {result.get('status')}, Model: {result.get('model')}"
        )
        return success
        
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False

def test_detect_depression():
    """Test détection de dépression"""
    print_section("Test 2: Détection Dépression")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/depression/detect",
            json={
                "text": "I feel so sad and hopeless, I don't want to live anymore",
                "include_reasoning": True
            }
        )
        result = response.json()
        
        print(f"Texte: 'I feel so sad and hopeless...'")
        print(f"Prédiction: {result.get('prediction')}")
        print(f"Confiance: {result.get('confidence'):.3f}")
        print(f"Sévérité: {result.get('severity')}")
        print(f"Temps: {result.get('processing_time'):.3f}s")
        if result.get('reasoning'):
            print(f"Raisonnement: {result.get('reasoning')[:100]}...")
        
        success = (
            response.status_code == 200 and
            result.get("prediction") in ["DÉPRESSION", "NORMAL"] and
            0 <= result.get("confidence", 0) <= 1
        )
        
        print_result(
            "Détection Dépression",
            success,
            f"Prédiction: {result.get('prediction')}"
        )
        return success
        
    except Exception as e:
        print_result("Détection Dépression", False, str(e))
        return False

def test_detect_normal():
    """Test détection normal"""
    print_section("Test 3: Détection Normal")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/depression/detect",
            json={
                "text": "I am so happy today, life is beautiful and I love everything",
                "include_reasoning": True
            }
        )
        result = response.json()
        
        print(f"Texte: 'I am so happy today...'")
        print(f"Prédiction: {result.get('prediction')}")
        print(f"Confiance: {result.get('confidence'):.3f}")
        print(f"Sévérité: {result.get('severity')}")
        print(f"Temps: {result.get('processing_time'):.3f}s")
        
        success = (
            response.status_code == 200 and
            result.get("prediction") in ["DÉPRESSION", "NORMAL"]
        )
        
        print_result(
            "Détection Normal",
            success,
            f"Prédiction: {result.get('prediction')}"
        )
        return success
        
    except Exception as e:
        print_result("Détection Normal", False, str(e))
        return False

def test_batch_detect():
    """Test détection batch"""
    print_section("Test 4: Détection Batch")
    try:
        texts = [
            "I am so happy today",
            "I feel worthless and empty",
            "Just finished a great workout"
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/v1/depression/batch-detect",
            json={
                "texts": texts,
                "include_reasoning": False
            }
        )
        result = response.json()
        
        print(f"Nombre de textes: {len(texts)}")
        print(f"Total traité: {result.get('total_processed')}")
        print(f"Temps total: {result.get('processing_time'):.2f}s")
        print(f"\nRésultats:")
        
        for r in result.get('results', []):
            print(f"  • {r['text'][:40]:40} → {r['prediction']:12} ({r['confidence']:.2f})")
        
        success = (
            response.status_code == 200 and
            result.get('total_processed') == len(texts) and
            len(result.get('results', [])) == len(texts)
        )
        
        print_result(
            "Détection Batch",
            success,
            f"Traité {result.get('total_processed')}/{len(texts)} textes"
        )
        return success
        
    except Exception as e:
        print_result("Détection Batch", False, str(e))
        return False

def test_info():
    """Test informations"""
    print_section("Test 5: Informations du Modèle")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/depression/info")
        result = response.json()
        
        print(f"Nom: {result.get('name')}")
        print(f"Version: {result.get('version')}")
        print(f"Auteur: {result.get('author')}")
        print(f"Architecture: {result.get('architecture')}")
        print(f"Type: {result.get('model_type')}")
        
        if 'performance' in result:
            print(f"\nPerformances:")
            for key, value in result['performance'].items():
                print(f"  • {key}: {value}")
        
        if 'endpoints' in result:
            print(f"\nEndpoints disponibles:")
            for key, value in result['endpoints'].items():
                print(f"  • {key}: {value}")
        
        success = (
            response.status_code == 200 and
            result.get('name') == 'yansnet-llm'
        )
        
        print_result(
            "Informations",
            success,
            f"Modèle: {result.get('name')} v{result.get('version')}"
        )
        return success
        
    except Exception as e:
        print_result("Informations", False, str(e))
        return False

def test_examples():
    """Test exemples"""
    print_section("Test 6: Exemples d'Utilisation")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/depression/examples")
        result = response.json()
        
        if 'examples' in result:
            print(f"Exemples disponibles:")
            for key in result['examples'].keys():
                print(f"  • {key}")
        
        if 'curl_examples' in result:
            print(f"\nExemples cURL disponibles:")
            for key in result['curl_examples'].keys():
                print(f"  • {key}")
        
        success = (
            response.status_code == 200 and
            'examples' in result
        )
        
        print_result(
            "Exemples",
            success,
            f"{len(result.get('examples', {}))} exemples disponibles"
        )
        return success
        
    except Exception as e:
        print_result("Exemples", False, str(e))
        return False

def test_generic_routes_still_work():
    """Test que les routes génériques fonctionnent toujours"""
    print_section("Test 7: Compatibilité Routes Génériques")
    try:
        # Test avec route générique
        response = requests.post(
            f"{BASE_URL}/api/v1/predict?model_name=yansnet-llm",
            json={
                "text": "I feel sad",
                "include_reasoning": False
            }
        )
        result = response.json()
        
        print(f"Route générique: /api/v1/predict?model_name=yansnet-llm")
        print(f"Prédiction: {result.get('prediction')}")
        print(f"Confiance: {result.get('confidence'):.3f}")
        
        success = (
            response.status_code == 200 and
            result.get("prediction") in ["DÉPRESSION", "NORMAL"]
        )
        
        print_result(
            "Routes Génériques",
            success,
            "Les routes génériques fonctionnent toujours"
        )
        return success
        
    except Exception as e:
        print_result("Routes Génériques", False, str(e))
        return False

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("  🧪 Tests des Routes Depression Detection")
    print("  API: " + BASE_URL)
    print("="*60)
    
    # Vérifier que l'API est accessible
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n❌ L'API n'est pas accessible!")
            print("   Assurez-vous que l'API est lancée:")
            print("   uvicorn app.main:app --reload --port 8000")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ Impossible de se connecter à l'API!")
        print("   Assurez-vous que l'API est lancée:")
        print("   uvicorn app.main:app --reload --port 8000")
        sys.exit(1)
    
    # Lancer les tests
    results = []
    
    results.append(test_health())
    results.append(test_detect_depression())
    results.append(test_detect_normal())
    results.append(test_batch_detect())
    results.append(test_info())
    results.append(test_examples())
    results.append(test_generic_routes_still_work())
    
    # Résumé
    print_section("Résumé des Tests")
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\nTotal: {total} tests")
    print(f"✅ Réussis: {passed}")
    print(f"❌ Échoués: {failed}")
    print(f"\nTaux de réussite: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("\n✅ Les routes spécialisées Depression Detection sont opérationnelles!")
        print("\n📚 Documentation disponible:")
        print("   • Swagger UI: http://localhost:8000/docs")
        print("   • Guide: docs/DEPRESSION_API_ROUTES.md")
        print("   • Résumé: ROUTES_SUMMARY.md")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) ont échoué.")
        print("\n🔍 Vérifiez:")
        print("   • L'API est bien lancée")
        print("   • Le modèle yansnet-llm est enregistré")
        print("   • La configuration LLM dans .env est correcte")
        return 1

if __name__ == "__main__":
    sys.exit(main())
