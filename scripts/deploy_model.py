#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de déploiement du modèle fine-tuné
Copie le modèle dans le dossier de l'API et met à jour le code
"""

import sys
import shutil
from pathlib import Path

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 70)
    print("DÉPLOIEMENT DU MODÈLE FINE-TUNÉ")
    print("=" * 70)
    
    # Chemins
    source_path = Path("models/bert-hate-speech-fr/final")
    target_path = Path("app/services/hatecomment_bert/model_finetuned")
    
    # Vérifier que le modèle existe
    if not source_path.exists():
        print(f"\n❌ ERREUR: Modèle source non trouvé à {source_path}")
        print(f"   Exécutez d'abord: python scripts/finetune_hate_speech.py")
        return
    
    print(f"\n1. Vérification du modèle source...")
    required_files = ["config.json", "tokenizer.json", "vocab.txt"]
    model_file = None
    
    for f in ["pytorch_model.bin", "model.safetensors"]:
        if (source_path / f).exists():
            model_file = f
            break
    
    if not model_file:
        print(f"   ❌ Fichier de poids manquant (pytorch_model.bin ou model.safetensors)")
        return
    
    required_files.append(model_file)
    
    for f in required_files:
        if not (source_path / f).exists():
            print(f"   ❌ Fichier manquant: {f}")
            return
    
    print(f"   ✓ Tous les fichiers requis sont présents")
    print(f"   ✓ Fichier de poids: {model_file}")
    
    # Créer le dossier cible
    print(f"\n2. Préparation du dossier cible...")
    if target_path.exists():
        print(f"   ⚠️  Le dossier existe déjà, il sera remplacé")
        shutil.rmtree(target_path)
    
    target_path.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ Dossier créé: {target_path}")
    
    # Copier les fichiers
    print(f"\n3. Copie des fichiers du modèle...")
    for item in source_path.iterdir():
        if item.is_file():
            target_file = target_path / item.name
            shutil.copy2(item, target_file)
            size_mb = item.stat().st_size / (1024 * 1024)
            print(f"   ✓ {item.name} ({size_mb:.1f} MB)")
    
    # Vérifier la copie
    print(f"\n4. Vérification de la copie...")
    for f in required_files:
        if not (target_path / f).exists():
            print(f"   ❌ Échec de la copie: {f}")
            return
    
    print(f"   ✓ Tous les fichiers copiés avec succès")
    
    # Mettre à jour le code du modèle
    print(f"\n5. Mise à jour du code du modèle...")
    model_code_path = Path("app/services/hatecomment_bert/hatecomment_bert_model.py")
    
    if not model_code_path.exists():
        print(f"   ❌ Fichier non trouvé: {model_code_path}")
        return
    
    # Lire le code actuel
    with open(model_code_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Vérifier si déjà modifié
    if 'model_finetuned' in code:
        print(f"   ✓ Le code pointe déjà vers model_finetuned")
    else:
        print(f"   ⚠️  Le code doit être modifié manuellement")
        print(f"   Modifier la ligne ~35 pour pointer vers: ./app/services/hatecomment_bert/model_finetuned")
    
    # Résumé
    print("\n" + "=" * 70)
    print("✅ DÉPLOIEMENT TERMINÉ")
    print("=" * 70)
    
    print(f"\nModèle déployé dans: {target_path.absolute()}")
    print(f"\nPROCHAINES ÉTAPES:")
    print(f"1. Vérifier que le code pointe vers model_finetuned")
    print(f"2. Rebuild Docker: docker-compose build")
    print(f"3. Redémarrer: docker-compose up -d")
    print(f"4. Tester l'API")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
