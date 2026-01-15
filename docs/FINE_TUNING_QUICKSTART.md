# 🚀 Guide de Démarrage Rapide - Fine-Tuning Hate Speech

Ce guide vous permet de fine-tuner le modèle BERT en **moins de 30 minutes** (avec GPU).

---

## ⚡ Démarrage Rapide (3 étapes)

### 1️⃣ Préparer les Données (5 min)

```bash
# Installer les dépendances
pip install torch transformers datasets scikit-learn pandas

# Préparer le dataset
python scripts/prepare_dataset.py
```

**Résultat attendu:**
```
✓ Sauvegardé: data/hate_speech/train.json (XX exemples)
✓ Sauvegardé: data/hate_speech/val.json (XX exemples)
✓ Sauvegardé: data/hate_speech/test.json (XX exemples)
```

### 2️⃣ Fine-Tuner le Modèle (2-3h GPU / 8-12h CPU)

```bash
python scripts/fine_tune_hate_speech.py
```

**Progression:**
- Epoch 1/3: Loss diminue, Accuracy augmente
- Epoch 2/3: Amélioration continue
- Epoch 3/3: Convergence

**Résultat attendu:**
```
✓ Modèle sauvegardé dans: models/bert-hate-speech-fr
```

### 3️⃣ Tester le Modèle (1 min)

```bash
python scripts/quick_test_finetuned.py
```

**Résultat attendu:**
```
Tests réussis: 8/8
Accuracy: 100%
🎉 EXCELLENT! Le modèle atteint l'objectif (>90%)
```

---

## 🔧 Intégration dans l'API

### Copier le Modèle

```bash
# Windows
xcopy /E /I models\bert-hate-speech-fr app\services\hatecomment_bert\model

# Linux/Mac
cp -r models/bert-hate-speech-fr app/services/hatecomment_bert/model
```

### Redémarrer Docker

```bash
docker-compose restart api
```

### Tester l'API

```bash
curl -X POST http://localhost:8000/api/v1/hate-speech/detect \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Tu es stupide\"}"
```

**Résultat attendu:**
```json
{
  "prediction": "HAINEUX",
  "confidence": 0.92,
  "model_fine_tuned": true
}
```

---

## 📊 Vérification

✅ Le modèle est prêt si:
- Accuracy > 90%
- Confiance > 80%
- `model_fine_tuned: true` dans l'API

---

Pour plus de détails, voir `FINE_TUNING_PLAN.md`
