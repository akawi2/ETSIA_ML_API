# 📋 Résumé Complet des Routes API - YANSNET Multi-Model ML

## 🎯 Vue d'Ensemble

L'API YANSNET dispose maintenant de **routes spécialisées** pour chaque modèle, en plus des routes génériques.

---

## 🏗️ Structure des Routes

### Routes Génériques (Multi-Modèles)
```
/api/v1/predict                    # Prédiction avec n'importe quel modèle
/api/v1/batch-predict              # Batch avec n'importe quel modèle
/api/v1/models                     # Liste tous les modèles
/api/v1/models/{model_name}/health # Health check d'un modèle
```

### Routes Spécialisées par Modèle

#### 1. Depression Detection (YANSNET LLM)
```
/api/v1/depression/detect          # Détection de dépression
/api/v1/depression/batch-detect    # Batch dépression
/api/v1/depression/health          # Health check
/api/v1/depression/info            # Informations
/api/v1/depression/examples        # Exemples
```

#### 2. Hate Speech Detection (HateComment BERT)
```
/api/v1/hatecomment/detect         # Détection hate speech
/api/v1/hatecomment/batch-detect   # Batch hate speech
/api/v1/hatecomment/health         # Health check
/api/v1/hatecomment/info           # Informations
/api/v1/hatecomment/examples       # Exemples
```

#### 3. NSFW Detection (Censure)
```
/api/v1/censure/detect             # Détection NSFW
/api/v1/censure/batch-detect       # Batch NSFW
/api/v1/censure/health             # Health check
/api/v1/censure/info               # Informations
/api/v1/censure/examples           # Exemples
```

#### 4. Recommendation System
```
/api/v1/recommendation/recommend         # Recommandations
/api/v1/recommendation/batch-recommend   # Batch recommandations
/api/v1/recommendation/health            # Health check
/api/v1/recommendation/info              # Informations
/api/v1/recommendation/examples          # Exemples
```

#### 5. Content Generation
```
/api/v1/content/generate-post              # Générer un post
/api/v1/content/generate-comments          # Générer des commentaires
/api/v1/content/generate-post-with-comments # Post complet
```

#### 6. Image Analysis (Sensitive Content)
```
/api/v1/image/analyze              # Analyser une image
/api/v1/image/batch-analyze        # Batch images
/api/v1/image/health               # Health check
/api/v1/image/info                 # Informations
```

---

## 📊 Comparaison Routes Génériques vs Spécialisées

| Aspect | Routes Génériques | Routes Spécialisées |
|--------|-------------------|---------------------|
| **URL** | `/api/v1/predict?model_name=xxx` | `/api/v1/[model]/detect` |
| **Format** | Uniforme pour tous | Adapté au modèle |
| **Documentation** | Générique | Spécialisée |
| **Exemples** | Généraux | Contextuels |
| **Métadonnées** | Basiques | Enrichies |

---

## 🚀 Exemples d'Utilisation

### Détection de Dépression

**Route Générique** :
```bash
curl -X POST "http://localhost:8000/api/v1/predict?model_name=yansnet-llm" \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel sad"}'
```

**Route Spécialisée** :
```bash
curl -X POST "http://localhost:8000/api/v1/depression/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel sad", "include_reasoning": true}'
```

### Détection Hate Speech

**Route Générique** :
```bash
curl -X POST "http://localhost:8000/api/v1/predict?model_name=hatecomment-bert" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je déteste tout le monde"}'
```

**Route Spécialisée** :
```bash
curl -X POST "http://localhost:8000/api/v1/hatecomment/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je déteste tout le monde"}'
```

### Détection NSFW

**Route Spécialisée** :
```bash
curl -X POST "http://localhost:8000/api/v1/censure/detect" \
  -F "file=@image.jpg"
```

### Recommandations

**Route Spécialisée** :
```bash
curl -X POST "http://localhost:8000/api/v1/recommendation/recommend" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "top_n": 10}'
```

---

## 📚 Documentation Complète

### Guides par Modèle

| Modèle | Documentation |
|--------|---------------|
| **Depression** | `docs/DEPRESSION_API_ROUTES.md` |
| **Hate Speech** | `docs/HATECOMMENT_API_ROUTES.md` |
| **NSFW** | `docs/CENSURE_API_ROUTES.md` (à créer) |
| **Recommendation** | `docs/RECOMMENDATION_API_ROUTES.md` (à créer) |
| **Image Analysis** | `docs/IMAGE_ANALYSIS_GUIDE.md` |
| **Content Generation** | `docs/CONTENT_GENERATION_GUIDE.md` |

### Documentation Interactive

**Swagger UI** : http://localhost:8000/docs

Toutes les routes sont automatiquement documentées avec :
- Schémas de requête/réponse
- Exemples interactifs
- Tests en direct
- Validation automatique

---

## ✅ Avantages de cette Architecture

### 1. Flexibilité
- Routes génériques pour usage simple
- Routes spécialisées pour fonctionnalités avancées

### 2. Clarté
- URLs explicites par modèle
- Documentation dédiée
- Exemples contextuels

### 3. Extensibilité
- Facile d'ajouter de nouveaux modèles
- Chaque modèle peut avoir ses propres routes
- Pas de conflit entre modèles

### 4. Performance
- Pas de conversion de format
- Optimisations spécifiques par modèle
- Cache possible par route

---

## 🎯 Recommandations d'Utilisation

### Quand utiliser les routes génériques ?
- ✅ Prototypage rapide
- ✅ Tests multi-modèles
- ✅ Intégration simple

### Quand utiliser les routes spécialisées ?
- ✅ Production
- ✅ Fonctionnalités avancées
- ✅ Métadonnées enrichies
- ✅ Documentation spécifique

---

## 🔄 Migration

Si vous utilisez actuellement les routes génériques, vous pouvez migrer progressivement :

**Avant** :
```python
response = requests.post(
    "http://localhost:8000/api/v1/predict?model_name=yansnet-llm",
    json={"text": "I feel sad"}
)
```

**Après** :
```python
response = requests.post(
    "http://localhost:8000/api/v1/depression/detect",
    json={"text": "I feel sad", "include_reasoning": True}
)
```

---

## 📞 Support

- **Documentation** : http://localhost:8000/docs
- **Health Check Global** : http://localhost:8000/health
- **Liste des Modèles** : http://localhost:8000/api/v1/models

---

**Version** : 1.0.0  
**Date** : Novembre 2024  
**Auteur** : Équipe YANSNET
