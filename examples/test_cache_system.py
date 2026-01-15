"""
Script de test pour le système de cache des recommandations
"""
import requests
import time
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000/api/v1/recommendation"


def print_section(title: str):
    """Affiche un titre de section"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(result: Dict[str, Any]):
    """Affiche un résultat formaté"""
    print(json.dumps(result, indent=2, ensure_ascii=False))


def test_cache_stats():
    """Test des statistiques du cache"""
    print_section("1. Statistiques du cache")
    
    response = requests.get(f"{BASE_URL}/cache/stats")
    if response.status_code == 200:
        print("✓ Statistiques récupérées")
        print_result(response.json())
    else:
        print(f"✗ Erreur: {response.status_code}")
        print(response.text)


def test_recommendation_cold_start():
    """Test de recommandation (cache froid)"""
    print_section("2. Première recommandation (Cache MISS attendu)")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/recommend",
        json={"user_id": 1, "top_n": 10}
    )
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Recommandations générées en {elapsed:.3f}s")
        print(f"  User ID: {result['user_id']}")
        print(f"  Nombre de recommandations: {result['total_recommendations']}")
        print(f"  Temps de traitement: {result.get('processing_time', 'N/A')}s")
        print("\nPremières recommandations:")
        for rec in result['recommendations'][:3]:
            print(f"  - Post {rec['post_id']}: score {rec['score']:.3f}")
    else:
        print(f"✗ Erreur: {response.status_code}")
        print(response.text)
    
    return elapsed


def test_recommendation_warm_cache():
    """Test de recommandation (cache chaud)"""
    print_section("3. Deuxième recommandation (Cache HIT attendu)")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/recommend",
        json={"user_id": 2, "top_n": 10}
    )
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Recommandations générées en {elapsed:.3f}s")
        print(f"  User ID: {result['user_id']}")
        print(f"  Nombre de recommandations: {result['total_recommendations']}")
        print(f"  Temps de traitement: {result.get('processing_time', 'N/A')}s")
    else:
        print(f"✗ Erreur: {response.status_code}")
        print(response.text)
    
    return elapsed


def test_cache_refresh():
    """Test du rafraîchissement du cache"""
    print_section("4. Rafraîchissement du cache")
    
    response = requests.post(f"{BASE_URL}/cache/refresh")
    if response.status_code == 200:
        result = response.json()
        print("✓ Cache rafraîchi")
        print_result(result)
    else:
        print(f"✗ Erreur: {response.status_code}")
        print(response.text)


def test_cache_invalidate():
    """Test de l'invalidation du cache"""
    print_section("5. Invalidation du cache")
    
    response = requests.delete(f"{BASE_URL}/cache/invalidate")
    if response.status_code == 200:
        result = response.json()
        print("✓ Cache invalidé")
        print_result(result)
    else:
        print(f"✗ Erreur: {response.status_code}")
        print(response.text)


def test_batch_recommendations():
    """Test des recommandations batch"""
    print_section("6. Recommandations batch")
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/batch-recommend",
        json={"user_ids": [1, 2, 3, 4, 5], "top_n": 5}
    )
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Recommandations batch générées en {elapsed:.3f}s")
        print(f"  Utilisateurs traités: {result['total_users']}")
        print(f"  Temps de traitement: {result['processing_time']}s")
        print(f"  Temps moyen par utilisateur: {result['processing_time'] / result['total_users']:.3f}s")
    else:
        print(f"✗ Erreur: {response.status_code}")
        print(response.text)


def test_performance_comparison():
    """Compare les performances avec et sans cache"""
    print_section("7. Comparaison de performance")
    
    # Invalider le cache
    print("\nInvalidation du cache...")
    requests.delete(f"{BASE_URL}/cache/invalidate")
    time.sleep(1)
    
    # Test sans cache (premier appel)
    print("\nTest SANS cache (cache froid):")
    cold_time = test_recommendation_cold_start()
    
    # Test avec cache (deuxième appel)
    print("\nTest AVEC cache (cache chaud):")
    warm_time = test_recommendation_warm_cache()
    
    # Comparaison
    print("\n" + "-" * 60)
    print("RÉSULTATS DE PERFORMANCE:")
    print(f"  Temps sans cache: {cold_time:.3f}s")
    print(f"  Temps avec cache: {warm_time:.3f}s")
    if cold_time > 0:
        speedup = cold_time / warm_time if warm_time > 0 else float('inf')
        print(f"  Accélération: {speedup:.1f}x plus rapide")
        improvement = ((cold_time - warm_time) / cold_time) * 100
        print(f"  Amélioration: {improvement:.1f}%")
    print("-" * 60)


def main():
    """Fonction principale de test"""
    print("\n" + "=" * 60)
    print("  TEST DU SYSTÈME DE CACHE - RECOMMANDATIONS")
    print("=" * 60)
    print(f"\nURL de base: {BASE_URL}")
    print("Assurez-vous que l'API et Redis sont démarrés!\n")
    
    try:
        # 1. Vérifier les stats initiales
        test_cache_stats()
        
        # 2. Test de performance
        test_performance_comparison()
        
        # 3. Test du rafraîchissement
        test_cache_refresh()
        
        # 4. Test des stats après rafraîchissement
        test_cache_stats()
        
        # 5. Test batch
        test_batch_recommendations()
        
        # 6. Test d'invalidation
        test_cache_invalidate()
        
        # 7. Vérifier les stats après invalidation
        test_cache_stats()
        
        print_section("TESTS TERMINÉS")
        print("✓ Tous les tests ont été exécutés")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERREUR: Impossible de se connecter à l'API")
        print("Assurez-vous que l'API est démarrée sur http://localhost:8000")
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")


if __name__ == "__main__":
    main()
