#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validation du modèle fine-tuné
Teste sur des exemples critiques en français
"""

import sys
import pandas as pd
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Tests critiques en français
TEST_CASES = [
    ("Je déteste ces gens", 1, "HAINEUX - Menace implicite"),
    ("Tu es stupide et incompétent", 1, "HAINEUX - Insulte directe"),
    ("Je vais te tuer", 1, "HAINEUX - Menace de mort"),
    ("Les gens comme toi devraient disparaître", 1, "HAINEUX - Menace implicite"),
    ("Bonjour comment allez-vous", 0, "NON-HAINEUX - Salutation"),
    ("Merci beaucoup pour votre aide", 0, "NON-HAINEUX - Remerciement"),
    ("Je déteste ce film", 0, "NON-HAINEUX - Critique d'objet"),
    ("Excellent travail, félicitations", 0, "NON-HAINEUX - Compliment"),
]

def predict(text, model, tokenizer, device):
    """Fait une prédiction"""
    inputs = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=128,
        return_tensors="pt"
    ).to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        pred = torch.argmax(probs, dim=-1).item()
        conf = probs[0][pred].item()
    
    return pred, conf

def main():
    print("=" * 70)
    print("VALIDATION DU MODÈLE FINE-TUNÉ")
    print("=" * 70)
    
    # Charger le modèle
    model_path = Path("models/bert-hate-speech-fr/final")
    
    if not model_path.exists():
        print(f"\n❌ ERREUR: Modèle non trouvé à {model_path}")
        print(f"   Assurez-vous d'avoir exécuté: python scripts/finetune_hate_speech.py")
        return
    
    print(f"\n1. Chargement du modèle depuis: {model_path}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.to(device)
    model.eval()
    
    print(f"   ✓ Modèle chargé sur {device}")
    
    # Tests
    print(f"\n2. Tests sur exemples critiques français:")
    print("=" * 70)
    
    correct = 0
    total = len(TEST_CASES)
    high_conf = 0
    
    for i, (text, expected, description) in enumerate(TEST_CASES, 1):
        pred, conf = predict(text, model, tokenizer, device)
        
        is_correct = pred == expected
        correct += is_correct
        if conf >= 0.80:
            high_conf += 1
        
        status = "✓" if is_correct else "✗"
        label = "HAINEUX" if pred == 1 else "NON-HAINEUX"
        
        print(f"\nTest {i}/{total}: {status}")
        print(f"  Texte: \"{text}\"")
        print(f"  Attendu: {description}")
        print(f"  Prédit:  {label} (confiance: {conf:.2%})")
        
        if not is_correct:
            print(f"  ⚠️  ERREUR DE PRÉDICTION!")
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    accuracy = correct / total
    high_conf_rate = high_conf / total
    
    print(f"\nPrécision: {correct}/{total} ({accuracy:.1%})")
    print(f"Confiance élevée (>80%): {high_conf}/{total} ({high_conf_rate:.1%})")
    
    # Évaluation
    if accuracy >= 0.90 and high_conf_rate >= 0.80:
        print(f"\n✅ VALIDATION RÉUSSIE!")
        print(f"   Le modèle est prêt pour le déploiement.")
    elif accuracy >= 0.80:
        print(f"\n⚠️  VALIDATION PARTIELLE")
        print(f"   Le modèle fonctionne mais pourrait être amélioré.")
    else:
        print(f"\n❌ VALIDATION ÉCHOUÉE")
        print(f"   Le modèle nécessite plus d'entraînement.")
    
    print("\n" + "=" * 70)
    print("Prochaine étape: python scripts/deploy_model.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
