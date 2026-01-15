#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de préparation du dataset HateSpeechDataset.csv
Nettoie, split et sauvegarde les données pour le fine-tuning
"""

import sys
import pandas as pd
import numpy as np
import re
from pathlib import Path
from sklearn.model_selection import train_test_split

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text):
    """Nettoie le texte"""
    if pd.isna(text):
        return ""
    
    # Convertir en string
    text = str(text)
    
    # Lowercase
    text = text.lower()
    
    # Supprimer URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Supprimer mentions
    text = re.sub(r'@\w+', '', text)
    
    # Supprimer hashtags (garder le texte)
    text = re.sub(r'#', '', text)
    
    # Supprimer caractères spéciaux excessifs
    text = re.sub(r'[^\w\s\.,!?;:\'-]', '', text)
    
    # Supprimer espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def main():
    print("=" * 60)
    print("PRÉPARATION DU DATASET HATE SPEECH")
    print("=" * 60)
    
    # Chemins
    dataset_path = Path("app/services/hatecomment_bert/HateSpeechDataset.csv/HateSpeechDataset.csv")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Charger le dataset
    print(f"\n1. Chargement du dataset: {dataset_path}")
    if not dataset_path.exists():
        print(f"❌ ERREUR: Dataset non trouvé à {dataset_path}")
        return
    
    df = pd.read_csv(dataset_path)
    print(f"   ✓ Dataset chargé: {len(df)} exemples")
    
    # Vérifier les colonnes
    print(f"\n2. Colonnes disponibles: {df.columns.tolist()}")
    
    # Vérifier la distribution des labels
    print(f"\n3. Distribution des labels:")
    print(df['Label'].value_counts())
    
    # Nettoyer le texte
    print(f"\n4. Nettoyage du texte...")
    df['text'] = df['Content'].apply(clean_text)
    
    # Supprimer les lignes vides
    df = df[df['text'].str.len() > 0]
    print(f"   ✓ Texte nettoyé: {len(df)} exemples restants")
    
    # Renommer la colonne Label en label
    df = df.rename(columns={'Label': 'label'})
    
    # Convertir label en int
    df['label'] = pd.to_numeric(df['label'], errors='coerce')
    
    # Garder seulement text et label
    df = df[['text', 'label']]
    
    # Supprimer les lignes avec des labels invalides (NaN ou pas 0/1)
    df = df.dropna(subset=['label'])
    df = df[df['label'].isin([0, 1])]
    df['label'] = df['label'].astype(int)
    print(f"   ✓ Après filtrage des labels: {len(df)} exemples")
    
    # Équilibrer le dataset si nécessaire
    label_counts = df['label'].value_counts()
    min_count = label_counts.min()
    
    print(f"\n5. Équilibrage du dataset...")
    print(f"   Avant: {label_counts.to_dict()}")
    
    # Prendre le même nombre d'exemples pour chaque classe
    df_balanced = pd.concat([
        df[df['label'] == 0].sample(min(min_count, 10000), random_state=42),
        df[df['label'] == 1].sample(min(min_count, 10000), random_state=42)
    ]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"   Après: {df_balanced['label'].value_counts().to_dict()}")
    print(f"   ✓ Dataset équilibré: {len(df_balanced)} exemples")
    
    # Split: 70% train, 15% val, 15% test
    print(f"\n6. Split du dataset...")
    train_df, temp_df = train_test_split(
        df_balanced, 
        test_size=0.3, 
        stratify=df_balanced['label'],
        random_state=42
    )
    
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,
        stratify=temp_df['label'],
        random_state=42
    )
    
    print(f"   Train: {len(train_df)} exemples")
    print(f"   Val:   {len(val_df)} exemples")
    print(f"   Test:  {len(test_df)} exemples")
    
    # Sauvegarder
    print(f"\n7. Sauvegarde des fichiers...")
    train_path = output_dir / "train.csv"
    val_path = output_dir / "val.csv"
    test_path = output_dir / "test.csv"
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"   ✓ {train_path}")
    print(f"   ✓ {val_path}")
    print(f"   ✓ {test_path}")
    
    # Afficher quelques exemples
    print(f"\n8. Exemples du dataset:")
    print("\n   Exemples HAINEUX (label=1):")
    for i, row in train_df[train_df['label'] == 1].head(3).iterrows():
        print(f"   - {row['text'][:80]}...")
    
    print("\n   Exemples NON-HAINEUX (label=0):")
    for i, row in train_df[train_df['label'] == 0].head(3).iterrows():
        print(f"   - {row['text'][:80]}...")
    
    print("\n" + "=" * 60)
    print("✅ PRÉPARATION TERMINÉE AVEC SUCCÈS")
    print("=" * 60)
    print(f"\nFichiers créés dans: {output_dir.absolute()}")
    print(f"Prochaine étape: python scripts/finetune_hate_speech.py")

if __name__ == "__main__":
    main()
