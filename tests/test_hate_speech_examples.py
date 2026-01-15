"""
Tests pour le modèle de détection de hate speech
"""
import requests
import json
from typing import Dict, Any

API_URL = "http://localhost:8000/api/v1/hatecomment/detect"

# Exemples de tests
TEST_CASES = [
    # Messages positifs/neutres (devrait être NON-HAINEUX)
    {
        "text": "Bonjour, comment allez-vous aujourd'hui?",
        "expected": "NON-HAINEUX",
        "category": "Positif"
    },
    {
        "text": "Merci beaucoup pour votre aide, c'est très gentil",
        "expected": "NON-HAINEUX",
        "category": "Positif"
    },
    {
        "text": "J'adore ce restaurant, la nourriture est excellente",
        "expected": "NON-HAINEUX",
        "category": "Positif"
    },
    {
        "text": "Je vais au cinéma ce soir avec des amis",
        "expected": "NON-HAINEUX",
        "category": "Neutre"
    },
    {
        "text": "Il fait beau aujourd'hui, parfait pour une promenade",
        "expected": "NON-HAINEUX",
        "category": "Neutre"
    },
    
    # Critiques constructives (devrait être NON-HAINEUX)
    {
        "text": "Je ne suis pas d'accord avec cette décision, mais je respecte votre opinion",
        "expected": "NON-HAINEUX",
        "category": "Critique constructive"
    },
    {
        "text": "Ce film n'était pas terrible, j'ai été déçu",
        "expected": "NON-HAINEUX",
        "category": "Critique constructive"
    },
    {
        "text": "Je pense que cette solution pourrait être améliorée",
        "expected": "NON-HAINEUX",
        "category": "Critique constructive"
    },
    
    # Insultes légères (devrait être HAINEUX)
    {
        "text": "Tu es vraiment stupide",
        "expected": "HAINEUX",
        "category": "Insulte légère"
    },
    {
        "text": "Quel idiot, il ne comprend rien",
        "expected": "HAINEUX",
        "category": "Insulte légère"
    },
    {
        "text": "T'es trop bête pour comprendre",
        "expected": "HAINEUX",
        "category": "Insulte légère"
    },
    
    # Insultes graves (devrait être HAINEUX)
    {
        "text": "Tu es un déchet humain",
        "expected": "HAINEUX",
        "category": "Insulte grave"
    },
    {
        "text": "Va crever, personne ne t'aime",
        "expected": "HAINEUX",
        "category": "Insulte grave"
    },
    {
        "text": "Tu mérites de souffrir",
        "expected": "HAINEUX",
        "category": "Insulte grave"
    },
    
    # Menaces (devrait être HAINEUX)
    {
        "text": "Je vais te tuer",
        "expected": "HAINEUX",
        "category": "Menace directe"
    },
    {
        "text": "Tu vas le regretter",
        "expected": "HAINEUX",
        "category": "Menace implicite"
    },
    {
        "text": "Les gens comme toi devraient disparaître",
        "expected": "HAINEUX",
        "category": "Menace indirecte"
    },
    
    # Discrimination (devrait être HAINEUX)
    {
        "text": "Tous les [groupe] sont des voleurs",
        "expected": "HAINEUX",
        "category": "Discrimination"
    },
    {
        "text": "Retourne dans ton pays",
        "expected": "HAINEUX",
        "category": "Discrimination"
    },
    
    # Harcèlement (devrait être HAINEUX)
    {
        "text": "Tu es moche et personne ne t'aimera jamais",
        "expected": "HAINEUX",
        "category": "Harcèlement"
    },
    {
        "text": "Tu devrais avoir honte de toi",
        "expected": "HAINEUX",
        "category": "Harcèlement"
    },
]


def test_hate_speech(text: str) -> Dict[str, Any]:
    """Teste le modèle de détection de hate speech"""
    try:
        response = requests.post(
            API_URL,
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def run_all_tests():
    """Exécute tous les tests et génère un rapport"""
    print("\n" + "="*80)
    print("TESTS DU MODÈLE DE DÉTECTION DE HATE SPEECH")
    print("="*80)
    
    results = {
        "total": len(TEST_CASES),
        "correct": 0,
        "incorrect": 0,
        "errors": 0,
        "by_category": {}
    }
    
    for i, test_case in enumerate(TEST_CASES, 1):
        text = test_case["text"]
        expected = test_case["expected"]
        category = test_case["category"]
        
        print(f"\n[Test {i}/{len(TEST_CASES)}] {category}")
        print(f"Texte: {text}")
        print(f"Attendu: {expected}")
        
        result = test_hate_speech(text)
        
        if "error" in result:
            print(f"❌ ERREUR: {result['error']}")
            results["errors"] += 1
            continue
        
        prediction = result.get("prediction", "UNKNOWN")
        confidence = result.get("confidence", 0)
        
        print(f"Prédit: {prediction} (confiance: {confidence:.2%})")
        
        # Vérifier si la prédiction est correcte
        is_correct = prediction == expected
        
        if is_correct:
            print("✅ CORRECT")
            results["correct"] += 1
        else:
            print(f"❌ INCORRECT (attendu: {expected})")
            results["incorrect"] += 1
        
        # Statistiques par catégorie
        if category not in results["by_category"]:
            results["by_category"][category] = {
                "total": 0,
                "correct": 0,
                "incorrect": 0
            }
        
        results["by_category"][category]["total"] += 1
        if is_correct:
            results["by_category"][category]["correct"] += 1
        else:
            results["by_category"][category]["incorrect"] += 1
    
    # Rapport final
    print("\n" + "="*80)
    print("RAPPORT FINAL")
    print("="*80)
    
    accuracy = (results["correct"] / results["total"]) * 100 if results["total"] > 0 else 0
    
    print(f"\nRésultats globaux:")
    print(f"  Total de tests: {results['total']}")
    print(f"  Corrects: {results['correct']} ({results['correct']/results['total']*100:.1f}%)")
    print(f"  Incorrects: {results['incorrect']} ({results['incorrect']/results['total']*100:.1f}%)")
    print(f"  Erreurs: {results['errors']}")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    print(f"\nRésultats par catégorie:")
    for category, stats in sorted(results["by_category"].items()):
        cat_accuracy = (stats["correct"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"  {category}:")
        print(f"    Total: {stats['total']}")
        print(f"    Corrects: {stats['correct']}")
        print(f"    Incorrects: {stats['incorrect']}")
        print(f"    Accuracy: {cat_accuracy:.1f}%")
    
    # Recommandations
    print(f"\n{'='*80}")
    print("RECOMMANDATIONS")
    print("="*80)
    
    if accuracy < 70:
        print("\n⚠️  CRITIQUE: L'accuracy est très faible (<70%)")
        print("   → Le modèle doit être fine-tuné sur un dataset de hate speech français")
        print("   → Considérer l'utilisation d'un modèle pré-entraîné spécialisé")
    elif accuracy < 85:
        print("\n⚠️  ATTENTION: L'accuracy est moyenne (70-85%)")
        print("   → Le modèle nécessite des améliorations")
        print("   → Collecter plus de données d'entraînement")
    else:
        print("\n✅ BON: L'accuracy est acceptable (>85%)")
        print("   → Continuer le monitoring et l'amélioration continue")
    
    print("\n" + "="*80)
    
    return results


if __name__ == "__main__":
    run_all_tests()
