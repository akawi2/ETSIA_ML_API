"""
Script de test pour vérifier l'intégration du monitoring
"""
import requests
import time
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8001"
BRIDGE_URL = "http://localhost:5000"

def test_bridge_health():
    """Test 1: Vérifier que le GA4-Bridge est accessible"""
    print("\n" + "="*70)
    print("TEST 1: Health Check GA4-Bridge")
    print("="*70)
    
    try:
        response = requests.get(f"{BRIDGE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ GA4-Bridge est opérationnel")
            print(f"  Status: {data.get('status')}")
            print(f"  Règles chargées: {data.get('catalog_rules')}")
            return True
        else:
            print(f"✗ Erreur: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Impossible de contacter le GA4-Bridge: {e}")
        return False


def test_api_health():
    """Test 2: Vérifier que l'API ML est accessible"""
    print("\n" + "="*70)
    print("TEST 2: Health Check ML API")
    print("="*70)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ ML API est opérationnelle")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Modèles disponibles: {data.get('models', {}).get('total', 0)}")
            return True
        else:
            print(f"✗ Erreur: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Impossible de contacter l'API ML: {e}")
        return False


def test_hate_comment_monitoring():
    """Test 3: Tester le monitoring du modèle HateComment"""
    print("\n" + "="*70)
    print("TEST 3: Monitoring HateComment Detection")
    print("="*70)
    
    test_texts = [
        "Je déteste tous ces gens",  # Devrait déclencher une alerte
        "Bonjour, comment allez-vous?"  # Normal
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n  Test {i}: '{text[:50]}...'")
        try:
            start = time.time()
            response = requests.post(
                f"{API_BASE_URL}/api/v1/hatecomment/predict",
                json={"text": text},
                timeout=10
            )
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                print(f"    ✓ Prédiction: {data.get('prediction')}")
                print(f"    ✓ Confiance: {data.get('confidence', 0):.2%}")
                print(f"    ✓ Latence: {latency}ms")
                
                if latency > 500:
                    print(f"    ⚠️ Alerte: Latence élevée (>{500}ms)")
            else:
                print(f"    ✗ Erreur: Status {response.status_code}")
                
        except Exception as e:
            print(f"    ✗ Erreur: {e}")
    
    return True


def test_depression_monitoring():
    """Test 4: Tester le monitoring du modèle Depression"""
    print("\n" + "="*70)
    print("TEST 4: Monitoring Depression Detection")
    print("="*70)
    
    test_text = "Je me sens très triste et sans espoir depuis plusieurs semaines"
    
    print(f"\n  Test: '{test_text[:50]}...'")
    try:
        start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/v1/depression/predict",
            json={"text": test_text},
            timeout=10
        )
        latency = int((time.time() - start) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ Prédiction: {data.get('prediction')}")
            print(f"    ✓ Confiance: {data.get('confidence', 0):.2%}")
            print(f"    ✓ Sévérité: {data.get('severity')}")
            print(f"    ✓ Latence: {latency}ms")
            
            if latency > 500:
                print(f"    ⚠️ Alerte: Latence élevée (>500ms)")
            
            if data.get('confidence', 1.0) < 0.60:
                print(f"    ⚠️ Alerte: Confiance faible (<0.60)")
        else:
            print(f"    ✗ Erreur: Status {response.status_code}")
            
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
    
    return True


def test_recommendation_monitoring():
    """Test 5: Tester le monitoring du système de recommandation"""
    print("\n" + "="*70)
    print("TEST 5: Monitoring Recommendation System")
    print("="*70)
    
    user_id = 1
    
    print(f"\n  Test: Recommandations pour user_id={user_id}")
    try:
        start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/v1/recommendation/recommend",
            json={"user_id": user_id, "top_n": 10},
            timeout=10
        )
        latency = int((time.time() - start) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ Recommandations: {data.get('total_recommendations')}")
            print(f"    ✓ Latence: {latency}ms")
            
            if latency > 200:
                print(f"    ⚠️ Alerte: Latence élevée (>200ms)")
        else:
            print(f"    ✗ Erreur: Status {response.status_code}")
            
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
    
    return True


def test_direct_bridge_emission():
    """Test 6: Tester l'émission directe vers le bridge"""
    print("\n" + "="*70)
    print("TEST 6: Émission Directe vers GA4-Bridge")
    print("="*70)
    
    test_event = {
        "service": "test_service",
        "event_name": "test_event",
        "model_name": "test-model",
        "params": {
            "latency": 250,
            "confidence": 0.85,
            "test_metric": 42
        },
        "client_id": "test_client"
    }
    
    print(f"\n  Envoi d'un événement de test...")
    try:
        response = requests.post(
            f"{BRIDGE_URL}/log_metric",
            json=test_event,
            timeout=2
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ Événement envoyé avec succès")
            print(f"    ✓ Status: {data.get('status')}")
            print(f"    ✓ Alertes déclenchées: {data.get('alerts', False)}")
        else:
            print(f"    ✗ Erreur: Status {response.status_code}")
            
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
    
    return True


def test_alert_triggering():
    """Test 7: Tester le déclenchement d'alertes"""
    print("\n" + "="*70)
    print("TEST 7: Déclenchement d'Alertes")
    print("="*70)
    
    # Événement qui devrait déclencher une alerte (latence élevée)
    alert_event = {
        "service": "hate_comment",
        "event_name": "detect_hate",
        "model_name": "bert-multilingual",
        "params": {
            "latency": 600,  # > 500ms (seuil d'alerte)
            "confidence": 0.65,
            "is_hateful": False
        },
        "client_id": "test_client"
    }
    
    print(f"\n  Envoi d'un événement avec latence élevée (600ms > 500ms)...")
    try:
        response = requests.post(
            f"{BRIDGE_URL}/log_metric",
            json=alert_event,
            timeout=2
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ Événement envoyé")
            
            if data.get('alerts'):
                print(f"    ✓ ALERTE DÉCLENCHÉE (comme attendu)")
            else:
                print(f"    ⚠️ Aucune alerte déclenchée (vérifier metrics_catalog.json)")
        else:
            print(f"    ✗ Erreur: Status {response.status_code}")
            
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
    
    return True


def main():
    """Exécute tous les tests"""
    print("\n" + "="*70)
    print("TESTS D'INTÉGRATION DU MONITORING")
    print("="*70)
    print("\nPré-requis:")
    print("  - docker-compose up -d (tous les services démarrés)")
    print("  - GA4-Bridge sur port 5000")
    print("  - ML API sur port 8001")
    
    results = []
    
    # Exécuter les tests
    results.append(("Bridge Health", test_bridge_health()))
    results.append(("API Health", test_api_health()))
    results.append(("HateComment Monitoring", test_hate_comment_monitoring()))
    results.append(("Depression Monitoring", test_depression_monitoring()))
    results.append(("Recommendation Monitoring", test_recommendation_monitoring()))
    results.append(("Direct Bridge Emission", test_direct_bridge_emission()))
    results.append(("Alert Triggering", test_alert_triggering()))
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n✓ Tous les tests sont passés!")
        print("\nProchaines étapes:")
        print("  1. Vérifier les logs du bridge: docker-compose logs ga4-bridge")
        print("  2. Consulter Google Analytics 4 pour voir les événements")
        print("  3. Intégrer le monitoring dans les autres modèles")
    else:
        print("\n⚠️ Certains tests ont échoué")
        print("\nDépannage:")
        print("  1. Vérifier que tous les services sont démarrés")
        print("  2. Vérifier les logs: docker-compose logs")
        print("  3. Vérifier la configuration .env")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
