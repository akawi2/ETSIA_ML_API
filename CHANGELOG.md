# 📝 Changelog - ETSIA_ML_API

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

---

## [1.1.0] - 2025-10-19

### 🆕 Ajouté

#### Modèle d'Analyse d'Images
- **Nouveau modèle** : `SensitiveImageCaptionModel` pour la détection de contenu sensible dans les images
- Génération automatique de légendes avec **microsoft/git-large-textcaps**
- Traduction EN→FR des légendes avec **Helsinki-NLP/opus-mt-en-fr**
- Détection de contenu sensible : drogue, violence, sexe, contenus problématiques
- Support de **60+ mots-clés** en anglais et français

#### Nouvelles Routes API
- `POST /api/v1/predict-image` : Analyse d'une image unique
- `POST /api/v1/batch-predict-images` : Analyse batch de plusieurs images (max 10)
- `GET /api/v1/models/{model_name}/health` : Health check d'un modèle spécifique

#### Documentation
- **IMAGE_ANALYSIS_GUIDE.md** : Guide complet d'utilisation du modèle d'images
- **INTEGRATION_SUMMARY.md** : Résumé technique de l'intégration
- **QUICK_START_IMAGE.md** : Démarrage rapide pour tester le modèle
- **README.md du modèle** : Documentation spécifique dans `app/services/sensitive_image_caption/`

#### Tests
- **test_image_model.py** : Suite complète de tests unitaires et d'intégration
  - Tests d'initialisation
  - Tests de détection de mots-clés
  - Tests de filtrage
  - Tests des endpoints API
  - Tests de performance (optionnels)

#### Scripts de Démonstration
- **demo_image_analysis.py** : Script interactif pour tester le modèle

### ✏️ Modifié

#### API
- **app/main.py**
  - Ajout de l'import et l'inclusion du `image_router`
  - Enregistrement du `SensitiveImageCaptionModel` au démarrage
  - Messages de log améliorés

- **app/routes/__init__.py**
  - Export du nouveau `image_router`

#### Documentation
- **README.md**
  - Titre mis à jour : "API de Détection de Dépression + Analyse d'Images"
  - Nouvelle section "Modèle d'Analyse d'Images" dans les résultats
  - Exemple de test d'image ajouté
  - Documentation du nouveau endpoint `/predict-image`
  - Structure du projet mise à jour

### 🔧 Technique

#### Architecture
- Extension de `BaseDepressionModel` via `**kwargs` pour supporter les images
- Utilisation du `ModelRegistry` existant (pas de modification nécessaire)
- Routes séparées dans `app/routes/image_api.py` pour maintenir la séparation des préoccupations

#### Dépendances
- **transformers** >= 4.30.0 (GIT model)
- **torch** >= 2.0.0 (Deep learning)
- **Pillow** >= 9.5.0 (Traitement d'images)
- **sentencepiece** >= 0.1.99 (Tokenization)

### 📊 Métriques

- **Nouveaux fichiers** : 10+
- **Fichiers modifiés** : 3
- **Lignes de code ajoutées** : ~1500
- **Tests ajoutés** : 15+
- **Pages de documentation** : 4

---

## [1.0.0] - 2025-01-16

### ✨ Version Initiale

#### Fonctionnalités
- Architecture multi-modèles avec `BaseDepressionModel` et `ModelRegistry`
- Modèle YANSNET LLM pour la détection de dépression dans les textes
- Support de 3 providers LLM : GPT (OpenAI), Claude (Anthropic), Ollama (local)
- API REST avec FastAPI
- Endpoints : `/predict`, `/batch-predict`, `/models`
- Documentation interactive avec Swagger UI
- Tests unitaires avec pytest
- Déploiement Docker
- Configuration via variables d'environnement

#### Documentation
- README.md complet
- API_CONTRACT.md
- ADD_YOUR_MODEL.md
- DATA_SOURCES.md
- DEPLOYMENT.md

---

## Format

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/lang/fr/).

### Types de Changements

- **🆕 Ajouté** : Nouvelles fonctionnalités
- **✏️ Modifié** : Changements dans les fonctionnalités existantes
- **⚠️ Déprécié** : Fonctionnalités bientôt supprimées
- **🗑️ Supprimé** : Fonctionnalités supprimées
- **🐛 Corrigé** : Corrections de bugs
- **🔒 Sécurité** : Corrections de vulnérabilités

---

## Liens Utiles

- [Comparer les versions](https://github.com/votre-repo/ETSIA_ML_API/compare)
- [Issues](https://github.com/votre-repo/ETSIA_ML_API/issues)
- [Pull Requests](https://github.com/votre-repo/ETSIA_ML_API/pulls)

---

**Dernière mise à jour** : Octobre 2025
