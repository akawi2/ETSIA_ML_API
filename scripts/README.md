# 📜 Scripts de Fine-Tuning - Hate Speech Detection

Ce dossier contient tous les scripts nécessaires pour fine-tuner le modèle BERT de détection de hate speech.

---

## 📋 Liste des Scripts

### 🔧 Scripts Principaux

| Script | Description | Durée |
|--------|-------------|-------|
| `run_full_pipeline.py` | **Pipeline complet** (tout-en-un) | 2-12h |
| `prepare_dataset.py` | Prépare les données d'entraînement | 5 min |
| `fine_tune_hate_speech.py` | Fine-tune le modèle BERT | 2-12h |
| `evaluate_model.py` | Évalue le modèle sur test set | 5 min |
| `quick_test_finetuned.py` | Tests rapides (8 exemples) | 1 min |
| `deploy_finetuned_model.py` | Déploie le modèle dans l'API | 1 min |

---

## 🚀 Utilisation

### Option 1: Pipeline Complet (Recommandé)

Exécute toutes les étapes automatiquement:

```bash
python scripts/run_full_pipeline.py
```

### Option 2: Étape par Étape

#### 1. Préparer les Données

```bash
python scripts/prepare_dataset.py
```

**Sortie:**
- `data/hate_speech/train.json`
- `data/hate_speech/val.json`
- `data/hate_speech/test.json`

#### 2. Fine-Tuner le Modèle

```bash
python scripts/fine_tune_hate_speech.py
```

**Sortie:**
- `models/bert-hate-speech-fr/` (modèle complet)
- `models/bert-hate-speech-fr/logs/` (logs d'entraînement)

#### 3. Évaluer le Modèle

```bash
python scripts/evaluate_model.py
```

**Sortie:**
- Métriques dans le terminal
- `models/bert-hate-speech-fr/evaluation_report.json`

#### 4. Tests Rapides

```bash
python scripts/quick_test_finetuned.py
```

**Sortie:**
- Résultats des 8 tests critiques
- Accuracy globale

#### 5. Déployer dans l'API

```bash
python scripts/deploy_finetuned_model.py
```

**Sortie:**
- Copie le modèle vers `app/services/hatecomment_bert/model/`
- Sauvegarde l'ancien modèle dans `model_backup/`

---

## ⚙️ Configuration

### Prérequis

```bash
pip install -r requirements-finetuning.txt
```

### Hyperparamètres (fine_tune_hate_speech.py)

Modifiez ces valeurs selon vos besoins:

```python
num_epochs = 3          # Nombre d'epochs (3-5 recommandé)
batch_size = 16         # Taille du batch (16 GPU, 8 CPU)
learning_rate = 2e-5    # Taux d'apprentissage
warmup_steps = 500      # Steps de warmup
```

---

## 📊 Résultats Attendus

### Avant Fine-Tuning
- Accuracy: 42.9%
- Confiance: 54-59%
- Détection menaces: 0%

### Après Fine-Tuning
- Accuracy: >90% ✅
- Confiance: >80% ✅
- Détection menaces: >95% ✅

---

## 🐛 Dépannage

### Erreur: "CUDA out of memory"

Réduire le batch size:
```python
batch_size = 8  # ou 4
```

### Erreur: "Dataset not found"

Exécuter d'abord:
```bash
python scripts/prepare_dataset.py
```

### Erreur: "Model not found"

Exécuter d'abord:
```bash
python scripts/fine_tune_hate_speech.py
```

---

## 📚 Documentation

- Plan complet: `FINE_TUNING_PLAN.md`
- Guide rapide: `docs/FINE_TUNING_QUICKSTART.md`
- Rapport de tests: `HATE_SPEECH_TEST_REPORT.md`

---

**Dernière mise à jour**: 8 janvier 2026
