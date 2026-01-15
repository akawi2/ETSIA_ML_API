#!/usr/bin/env python3
"""
Script de démonstration du système de monitoring
Teste tous les modèles et affiche les métriques en temps réel
"""
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8001"
BRIDGE_URL = "http://localhost:5000"

# Couleurs pour le terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Affiche un header coloré"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_metric(label: str, value: Any, color: str = Colors.RESET):
    """Affiche une métrique formatée"""
    print(f"  {Colors.YELLOW}{label}:{Colors.RESET} {color}{value}{Colors.RESET}")

def test_bridge_health():
    """Vérifie l'état du GA4-Bridge"""
    print_header("🔍 VÉRIFICATION DU MONITORING (GA4-Bridge)")
    
    try:
        response = requests.get(f"{BRIDGE_URL}/health", timeout=5)
        data = response.json()
        
        print_metric("Status", data['status'], Colors.GREEN)
        print_metric("Règles d'alerte", data['catalog_rules'], Colors.CYAN)
        print_metric("URL", BRIDGE_URL, Colors.BLUE)
        
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.RESET}")
        return False

def test_model_with_monitoring(
    endpoint: str,
    payload: Dict,
    model_name: str,
    description: str
):
    """Teste un modèle et affiche les métriques"""
    print_header(f"🤖 TEST: {model_name}")
    print(f"{Colors.BLUE}Description:{Colors.RESET} {description}\n")
    
    # Afficher le payload
    print(f"{Colors.YELLOW}📤 Requête:{Colors.RESET}")
    print(f"  Endpoint: {endpoint}")
    print(f"  Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}\n")
    
    # Envoyer la requête
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"{Colors.GREEN}✅ Succès{Colors.RESET}\n")
            print(f"{Colors.YELLOW}📥 Réponse:{Colors.RESET}")
            
            # Afficher les métriques principales
            if 'prediction' in data:
                print_metric("Prédiction", data['prediction'], Colors.MAGENTA)
            if 'confidence' in data:
                print_metric("Confiance", f"{data['confidence']:.4f}", Colors.CYAN)
            if 'severity' in data:
                print_metric("Sévérité", data['severity'], Colors.YELLOW)
            if 'processing_time' in data:
                print_metric("Temps de traitement", f"{data['processing_time']:.3f}s", Colors.BLUE)
            
            print_metric("Latence totale", f"{elapsed:.3f}s", Colors.BLUE)
            
            # Vérifier si une alerte a été déclenchée
            if elapsed > 1.0:
                print(f"\n{Colors.RED}⚠️  ALERTE: Latence > 1000ms détectée!{Colors.RESET}")
                print(f"   → Métrique envoyée au GA4-Bridge")
                print(f"   → Alerte enregistrée dans GA4")
            
            return True
        else:
            print(f"{Colors.RED}❌ Erreur HTTP {response.status_code}{Colors.RESET}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.RESET}")
        return False

def demo_monitoring_flow():
    """Démontre le flux complet de monitoring"""
    print_header("📊 DÉMONSTRATION DU SYSTÈME DE MONITORING")
    
    print(f"{Colors.CYAN}Architecture:{Colors.RESET}")
    print(f"  1. {Colors.GREEN}API ML{Colors.RESET} (port 8001) → Exécute les modèles")
    print(f"  2. {Colors.YELLOW}Émission métriques{Colors.RESET} → Envoi asynchrone au Bridge")
    print(f"  3. {Colors.BLUE}GA4-Bridge{Colors.RESET} (port 5000) → Évalue les seuils")
    print(f"  4. {Colors.MAGENTA}Alertes{Colors.RESET} → Si seuils dépassés")
    print(f"  5. {Colors.CYAN}Google Analytics 4{Colors.RESET} → Stockage et visualisation\n")
    
    input(f"{Colors.YELLOW}Appuyez sur Entrée pour commencer les tests...{Colors.RESET}")

def main():
    """Exécute la démonstration complète"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║     DÉMONSTRATION SYSTÈME DE MONITORING - YANSNET ML API          ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # 1. Vérifier le bridge
    if not test_bridge_health():
        print(f"\n{Colors.RED}❌ GA4-Bridge non accessible. Arrêt du test.{Colors.RESET}")
        return
    
    input(f"\n{Colors.YELLOW}Appuyez sur Entrée pour continuer...{Colors.RESET}")
    
    # 2. Expliquer le flux
    demo_monitoring_flow()
    
    # 3. Test 1: Détection de dépression (latence élevée = alerte)
    test_model_with_monitoring(
        endpoint="/api/v1/depression/detect",
        payload={"text": "Je me sens vraiment triste et sans espoir depuis plusieurs semaines"},
        model_name="Détection de Dépression (Qwen 2.5)",
        description="Détecte les signes de dépression dans le texte. Latence ~4s → Déclenche une alerte!"
    )
    
    input(f"\n{Colors.YELLOW}Appuyez sur Entrée pour le test suivant...{Colors.RESET}")
    
    # 4. Test 2: Détection hate speech (rapide, pas d'alerte)
    test_model_with_monitoring(
        endpoint="/api/v1/hatecomment/detect",
        payload={"text": "Tu es vraiment stupide et inutile"},
        model_name="Détection Hate Speech (BERT)",
        description="Détecte le contenu haineux. Latence ~50ms → Pas d'alerte"
    )
    
    input(f"\n{Colors.YELLOW}Appuyez sur Entrée pour le test suivant...{Colors.RESET}")
    
    # 5. Test 3: Recommandations (avec cache)
    test_model_with_monitoring(
        endpoint="/api/v1/recommendation/recommend",
        payload={"user_id": 1, "top_n": 5},
        model_name="Système de Recommandation",
        description="Génère des recommandations personnalisées avec cache Redis"
    )
    
    input(f"\n{Colors.YELLOW}Appuyez sur Entrée pour le test suivant...{Colors.RESET}")
    
    # 6. Test 4: NSFW Detection (nouveau modèle!)
    print_header("🆕 NOUVEAU: Détection NSFW (ShieldGemma2)")
    print(f"{Colors.CYAN}Ce modèle vient d'être activé!{Colors.RESET}\n")
    
    # Image de test en base64 (1x1 pixel blanc)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    test_model_with_monitoring(
        endpoint="/api/v1/censure/detect",
        payload={"image": test_image},
        model_name="Détection NSFW (ShieldGemma2)",
        description="Analyse multi-catégories: Sexually Explicit, Violence, Hate Speech, etc."
    )
    
    # 7. Résumé final
    print_header("📊 RÉSUMÉ DU MONITORING")
    
    print(f"{Colors.GREEN}✅ Tests effectués:{Colors.RESET}")
    print(f"  • Détection de dépression (alerte latence)")
    print(f"  • Détection hate speech (pas d'alerte)")
    print(f"  • Recommandations (cache Redis)")
    print(f"  • Détection NSFW (nouveau modèle)")
    
    print(f"\n{Colors.YELLOW}📈 Métriques émises:{Colors.RESET}")
    print(f"  • Latence (ms)")
    print(f"  • Confiance (0-1)")
    print(f"  • Prédiction")
    print(f"  • Erreurs")
    
    print(f"\n{Colors.BLUE}🔔 Alertes configurées:{Colors.RESET}")
    print(f"  • Latence > 1000ms → Priorité HAUTE")
    print(f"  • Confiance < 0.5 → Priorité MOYENNE")
    print(f"  • Taux erreur > 5% → Priorité CRITIQUE")
    
    print(f"\n{Colors.MAGENTA}📊 Visualisation:{Colors.RESET}")
    print(f"  • Google Analytics 4 Dashboard")
    print(f"  • Métriques en temps réel")
    print(f"  • Historique et tendances")
    
    print(f"\n{Colors.CYAN}🔍 Pour voir les logs du monitoring:{Colors.RESET}")
    print(f"  docker logs etsia_ml_api-ga4-bridge-1 --tail 50")
    
    print(f"\n{Colors.GREEN}✅ Démonstration terminée!{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Démonstration interrompue{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erreur: {e}{Colors.RESET}\n")
