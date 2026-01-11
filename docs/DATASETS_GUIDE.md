# 📊 Guide des Datasets - Hate Speech Detection

Ce guide liste les datasets recommandés pour le fine-tuning du modèle BERT.

---

## 🇫🇷 Datasets Français (Priorité)

### 1. HateCheck-FR ⭐⭐⭐

**Description**: Dataset de test pour la détection de hate speech en français

**Caractéristiques:**
- Taille: ~3,000 exemples annotés
- Langue: Français
- Catégories: Insultes, menaces, discrimination, stéréotypes
- Format: JSONL
- Licence: MIT

**Téléchargement:**
```bash
git clone https://github.com/paul-rottger/hatecheck-data.git
cd hatecheck-data
# Fichier: test_suite_cases_fr.jsonl
```

**Structure:**
```json
{
  "case_id": "1",
  "text": "Tu es stupide",
  "label": "hateful",
  "target_ident": "individual",
  "ref_case_id": null,
  "ref_templ_id": "1"
}
```

### 2. OLID-FR (Offensive Language Identification Dataset)

**Description**: Tweets annotés pour la détection de langage offensant

**Caractéristiques:**
- Taille: ~14,000 tweets
- Langue: Français (version adaptée)
- Catégories: Offensive (OFF) vs Non-Offensive (NOT)
- Format: CSV

**Téléchargement:**
```bash
# Disponible sur demande ou via SemEval-2019 Task 6
# https://sites.google.com/site/offensevalsharedtask/
```

**Structure:**
```csv
id,text,label
1,"Bonjour",NOT
2,"Tu es un idiot",OFF
```

### 3. French Toxic Comments (Kaggle)

**Description**: Commentaires toxiques en français

**Caractéristiques:**
- Taille: Variable selon la source
- Langue: Français
- Catégories: Toxic, Severe Toxic, Obscene, Threat, Insult, Identity Hate

**Téléchargement:**
```bash
# Via Kaggle API
kaggle datasets download -d julian3833/jigsaw-toxic-comment-classification-challenge-french
```

---

## 🇬🇧 Datasets Anglais (Complémentaires)

### 1. Toxic Comment Classification Challenge ⭐⭐⭐

**Description**: Large dataset de commentaires Wikipedia

**Caractéristiques:**
- Taille: ~160,000 commentaires
- Langue: Anglais
- Catégories: 6 types de toxicité
- Format: CSV

**Téléchargement:**
```bash
kaggle competitions download -c jigsaw-toxic-comment-classification-challenge
```

### 2. HateXplain

**Description**: Dataset avec explications pour hate speech

**Caractéristiques:**
- Taille: ~20,000 posts
- Langue: Anglais
- Annotations: Hate, Offensive, Normal + explications

**Téléchargement:**
```bash
git clone https://github.com/hate-alert/HateXplain.git
```

---

## 🎯 Dataset Personnalisé YANSNET

### Création Manuelle

**Objectif**: Collecter 1,000-2,000 exemples du contexte étudiant français

**Catégories à couvrir:**
1. Insultes personnelles
2. Menaces de violence
3. Discrimination (race, genre, religion)
4. Harcèlement
5. Cyberbullying étudiant

**Format:**
```json
{
  "text": "Exemple de texte",
  "label": 1,
  "severity": "Moyenne",
  "category": "Insulte",
  "context": "Commentaire sur post"
}
```

**Sources:**
- Commentaires signalés sur la plateforme
- Exemples synthétiques basés sur cas réels
- Crowdsourcing avec modération

---

## 📥 Téléchargement Automatique

### Script de Téléchargement

Créer `scripts/download_datasets.py`:

```python
import requests
import json
from pathlib import Path

def download_hatecheck_fr():
    """Télécharge HateCheck-FR"""
    url = "https://raw.githubusercontent.com/paul-rottger/hatecheck-data/main/test_suite_cases_fr.jsonl"
    output = Path("data/raw/hatecheck_fr.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    response = requests.get(url)
    with open(output, 'wb') as f:
        f.write(response.content)
    
    print(f"✓ HateCheck-FR téléchargé: {output}")

if __name__ == "__main__":
    download_hatecheck_fr()
```

---

## 🔄 Fusion des Datasets

### Stratégie Recommandée

1. **Base**: HateCheck-FR (3,000 exemples)
2. **Complément**: OLID-FR (14,000 exemples)
3. **Spécifique**: YANSNET (1,000-2,000 exemples)
4. **Total**: ~18,000 exemples

### Équilibrage

- 50% HAINEUX
- 50% NON-HAINEUX
- Après équilibrage: ~9,000 exemples par classe

### Split Final

- Train: 80% (~14,400 exemples)
- Validation: 10% (~1,800 exemples)
- Test: 10% (~1,800 exemples)

---

## ✅ Checklist de Qualité

Avant d'utiliser un dataset, vérifier:

- [ ] Langue correcte (français prioritaire)
- [ ] Annotations de qualité
- [ ] Classes équilibrées
- [ ] Pas de doublons
- [ ] Textes nettoyés (URLs, mentions supprimées)
- [ ] Contexte pertinent (réseaux sociaux, commentaires)
- [ ] Licence compatible (MIT, CC-BY, etc.)

---

## 📚 Ressources Supplémentaires

### Papers

- [HateCheck: Functional Tests for Hate Speech Detection Models](https://arxiv.org/abs/2012.15606)
- [Multilingual Hate Speech Detection](https://arxiv.org/abs/2004.06465)

### Outils

- [Label Studio](https://labelstud.io/) - Annotation manuelle
- [Prodigy](https://prodi.gy/) - Annotation assistée par ML
- [Doccano](https://github.com/doccano/doccano) - Annotation open-source

---

**Dernière mise à jour**: 8 janvier 2026
