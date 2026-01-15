#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de fine-tuning du modèle BERT pour la détection de hate speech
Utilise l'API Trainer de Hugging Face
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
import evaluate

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def load_data():
    """Charge les datasets préparés"""
    data_dir = Path("data/processed")
    
    train_df = pd.read_csv(data_dir / "train.csv")
    val_df = pd.read_csv(data_dir / "val.csv")
    
    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)
    
    return train_dataset, val_dataset

def tokenize_function(examples, tokenizer):
    """Tokenize les textes"""
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=128
    )

def compute_metrics(eval_pred):
    """Calcule les métriques"""
    metric_acc = evaluate.load("accuracy")
    metric_prec = evaluate.load("precision")
    metric_recall = evaluate.load("recall")
    metric_f1 = evaluate.load("f1")
    
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    acc = metric_acc.compute(predictions=predictions, references=labels)["accuracy"]
    prec = metric_prec.compute(predictions=predictions, references=labels)["precision"]
    rec = metric_recall.compute(predictions=predictions, references=labels)["recall"]
    f1 = metric_f1.compute(predictions=predictions, references=labels)["f1"]
    
    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1
    }

def main():
    print("=" * 70)
    print("FINE-TUNING DU MODÈLE BERT POUR HATE SPEECH DETECTION")
    print("=" * 70)
    
    # Vérifier CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n1. Device: {device}")
    if device == "cuda":
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("   ⚠️  Pas de GPU détecté. L'entraînement sera plus lent (8-12h)")
    
    # Charger les données
    print(f"\n2. Chargement des données...")
    train_dataset, val_dataset = load_data()
    print(f"   ✓ Train: {len(train_dataset)} exemples")
    print(f"   ✓ Val:   {len(val_dataset)} exemples")
    
    # Charger le tokenizer
    print(f"\n3. Chargement du tokenizer...")
    model_name = "bert-base-multilingual-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print(f"   ✓ Tokenizer chargé: {model_name}")
    
    # Tokenizer les datasets
    print(f"\n4. Tokenization des données...")
    train_dataset = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True
    )
    val_dataset = val_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True
    )
    print(f"   ✓ Tokenization terminée")
    
    # Charger le modèle
    print(f"\n5. Chargement du modèle...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2
    )
    print(f"   ✓ Modèle chargé")
    
    # Configuration de l'entraînement
    output_dir = Path("models/bert-hate-speech-fr")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n6. Configuration de l'entraînement...")
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=3,
        per_device_train_batch_size=16 if device == "cuda" else 8,
        per_device_eval_batch_size=32 if device == "cuda" else 16,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_steps=500,
        logging_dir=str(output_dir / "logs"),
        logging_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        save_total_limit=2,
        report_to="none",
        fp16=device == "cuda",  # Mixed precision si GPU
    )
    
    print(f"   Epochs: {training_args.num_train_epochs}")
    print(f"   Batch size (train): {training_args.per_device_train_batch_size}")
    print(f"   Learning rate: {training_args.learning_rate}")
    print(f"   Output dir: {output_dir}")
    
    # Data collator
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    # Créer le Trainer
    print(f"\n7. Création du Trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    print(f"   ✓ Trainer créé")
    
    # Entraînement
    print(f"\n8. Début de l'entraînement...")
    print(f"   ⏱️  Durée estimée: {'2-3 heures' if device == 'cuda' else '8-12 heures'}")
    print("=" * 70)
    
    trainer.train()
    
    print("\n" + "=" * 70)
    print("✅ ENTRAÎNEMENT TERMINÉ")
    print("=" * 70)
    
    # Évaluation finale
    print(f"\n9. Évaluation finale sur validation set...")
    metrics = trainer.evaluate()
    
    print(f"\n📊 MÉTRIQUES FINALES:")
    print(f"   Accuracy:  {metrics['eval_accuracy']:.4f} (objectif: >0.90)")
    print(f"   Precision: {metrics['eval_precision']:.4f} (objectif: >0.85)")
    print(f"   Recall:    {metrics['eval_recall']:.4f} (objectif: >0.90)")
    print(f"   F1-Score:  {metrics['eval_f1']:.4f} (objectif: >0.88)")
    
    # Vérifier si les objectifs sont atteints
    success = (
        metrics['eval_accuracy'] >= 0.90 and
        metrics['eval_f1'] >= 0.88
    )
    
    if success:
        print(f"\n✅ OBJECTIFS ATTEINTS!")
    else:
        print(f"\n⚠️  Objectifs non atteints. Considérer:")
        print(f"   - Augmenter le nombre d'epochs")
        print(f"   - Ajuster le learning rate")
        print(f"   - Ajouter plus de données")
    
    # Sauvegarder le modèle
    print(f"\n10. Sauvegarde du modèle...")
    trainer.save_model(str(output_dir / "final"))
    tokenizer.save_pretrained(str(output_dir / "final"))
    print(f"   ✓ Modèle sauvegardé dans: {output_dir / 'final'}")
    
    print("\n" + "=" * 70)
    print("Prochaine étape: python scripts/validate_model.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
