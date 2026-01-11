#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de monitoring en temps réel du fine-tuning
Affiche la progression, les métriques et le temps restant
"""

import sys
import time
from pathlib import Path
import json
from datetime import datetime, timedelta

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def parse_log_file(log_file):
    """Parse le fichier de log pour extraire les métriques"""
    if not log_file.exists():
        return None
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                # Prendre la dernière ligne avec des métriques
                for line in reversed(lines):
                    if 'loss' in line.lower():
                        return line.strip()
    except:
        pass
    return None

def get_checkpoint_info(output_dir):
    """Récupère les infos des checkpoints"""
    checkpoints = list(output_dir.glob("checkpoint-*"))
    if not checkpoints:
        return None
    
    latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
    
    # Lire trainer_state.json si disponible
    state_file = latest / "trainer_state.json"
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
                return {
                    'checkpoint': latest.name,
                    'epoch': state.get('epoch', 0),
                    'global_step': state.get('global_step', 0),
                    'best_metric': state.get('best_metric'),
                    'log_history': state.get('log_history', [])
                }
        except:
            pass
    
    return {'checkpoint': latest.name}

def format_time(seconds):
    """Formate le temps en heures:minutes:secondes"""
    return str(timedelta(seconds=int(seconds)))

def display_progress(info):
    """Affiche la progression de manière formatée"""
    print("\033[2J\033[H")  # Clear screen
    print("=" * 80)
    print("🚀 MONITORING DU FINE-TUNING - HATE SPEECH DETECTION")
    print("=" * 80)
    print(f"\n⏰ Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}")
    
    if info:
        print(f"\n📊 PROGRESSION:")
        print(f"   Checkpoint: {info.get('checkpoint', 'N/A')}")
        print(f"   Epoch: {info.get('epoch', 0):.2f} / 3")
        print(f"   Step global: {info.get('global_step', 0)}")
        
        if info.get('log_history'):
            history = info['log_history']
            
            # Dernières métriques d'entraînement
            train_logs = [h for h in history if 'loss' in h]
            if train_logs:
                last_train = train_logs[-1]
                print(f"\n📈 ENTRAÎNEMENT:")
                print(f"   Loss: {last_train.get('loss', 'N/A'):.4f}")
                print(f"   Learning rate: {last_train.get('learning_rate', 'N/A'):.2e}")
                
                # Estimer le temps restant
                if 'epoch' in last_train:
                    current_epoch = last_train['epoch']
                    epochs_left = 3 - current_epoch
                    # Estimer basé sur le temps écoulé
                    steps = last_train.get('step', 0)
                    if steps > 0:
                        time_per_step = 0.4  # ~2.5 it/s
                        total_steps = 2625 * 3  # 2625 steps par epoch, 3 epochs
                        remaining_steps = total_steps - info.get('global_step', 0)
                        time_left = remaining_steps * time_per_step
                        print(f"   ⏱️  Temps restant estimé: {format_time(time_left)}")
            
            # Dernières métriques de validation
            eval_logs = [h for h in history if 'eval_loss' in h]
            if eval_logs:
                last_eval = eval_logs[-1]
                print(f"\n✅ VALIDATION (Epoch {last_eval.get('epoch', 'N/A')}):")
                print(f"   Loss: {last_eval.get('eval_loss', 'N/A'):.4f}")
                print(f"   Accuracy: {last_eval.get('eval_accuracy', 'N/A'):.4f}")
                print(f"   Precision: {last_eval.get('eval_precision', 'N/A'):.4f}")
                print(f"   Recall: {last_eval.get('eval_recall', 'N/A'):.4f}")
                print(f"   F1-Score: {last_eval.get('eval_f1', 'N/A'):.4f}")
                
                # Vérifier si objectifs atteints
                if last_eval.get('eval_accuracy', 0) >= 0.90:
                    print(f"\n   🎯 Objectif Accuracy atteint! (>90%)")
                if last_eval.get('eval_f1', 0) >= 0.88:
                    print(f"   🎯 Objectif F1-Score atteint! (>88%)")
        
        if info.get('best_metric'):
            print(f"\n🏆 Meilleure métrique: {info['best_metric']:.4f}")
    else:
        print(f"\n⏳ En attente du démarrage de l'entraînement...")
        print(f"   Vérification du dossier: models/bert-hate-speech-fr/")
    
    print("\n" + "=" * 80)
    print("Appuyez sur Ctrl+C pour arrêter le monitoring")
    print("=" * 80)

def main():
    output_dir = Path("models/bert-hate-speech-fr")
    
    print("Démarrage du monitoring...")
    print(f"Surveillance du dossier: {output_dir}")
    print("\nAppuyez sur Ctrl+C pour arrêter\n")
    
    try:
        while True:
            info = get_checkpoint_info(output_dir)
            display_progress(info)
            time.sleep(10)  # Mise à jour toutes les 10 secondes
            
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring arrêté par l'utilisateur")
        print("L'entraînement continue en arrière-plan")

if __name__ == "__main__":
    main()
