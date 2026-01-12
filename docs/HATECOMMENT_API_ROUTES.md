# 🛣️ Routes API HateComment BERT - Guide Complet

## 📖 Vue d'Ensemble

Ce document détaille les routes API spécifiques créées pour le modèle **HateComment BERT Enhanced v1.1.0**. Ces routes permettent d'utiliser le modèle dans sa fonction native de détection de hate speech, en parallèle des routes génériques de l'API.

---

## 🏗️ Architecture des Routes

### **Préfixe des Routes**
```
/api/v1/hatecomment/
```

### **Tags OpenAPI**
```
["HateComment BERT"]
```

### **Modèle Ciblé**
- **Nom** : `hatecomment-bert`
- **Version** : `1.1.0 Enhanced`
- **Type** : Détection de hate speech
- **Langues** : Français, Anglais

---

## 🎯 Routes Disponibles

### **1. Détection de Hate Speech**

#### **POST `/api/v1/hatecomment/detect`**

**Description** : Analyse un texte pour détecter le hate speech

**Requête** :
```json
{
  "text": "Je déteste ces gens",
  "include_reasoning": true
}
```

**Réponse** :
```json
{
  "prediction": "HAINEUX",
  "confidence": 0.92,
  "severity": "Critique",
  "reasoning": "Commentaire classifié comme haineux avec une confiance de 92.00%. Détection améliorée par analyse de patterns.",
  "hate_classification": "haineux",
  "original_label": "LABEL_1",
  "enhanced": true,
  "boost_applied": true,
  "processing_time": 0.045
}
```

**Exemple cURL** :
```bash
curl -X POST "http://localhost:8000/api/v1/hatecomment/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je déteste ces gens", "include_reasoning": true}'
```

---

### **2. Détection Batch**

#### **POST `/api/v1/hatecomment/batch-detect`**

**Description** : Analyse plusieurs textes en batch (max 100)

**Requête** :
```json
{
  "texts": [
    "Hello world",
    "Je déteste tout le monde",
    "Nice weather today"
  ],
  "include_reasoning": false
}
```

**Réponse** :
```json
{
  "results": [
    {
      "text": "Hello world",
      "prediction": "NON-HAINEUX",
      "confidence": 0.95,
      "severity": "Aucune",
      "reasoning": null,
      "hate_classification": "non-haineux"
    },
    {
      "text": "Je déteste tout le monde",
      "prediction": "HAINEUX",
      "confidence": 0.88,
      "severity": "Élevée",
      "reasoning": null,
      "hate_classification": "haineux"
    }
  ],
  "total_processed": 3,
  "processing_time": 0.12,
  "model_used": "hatecomment-bert",
  "enhanced_version": "1.1.0"
}
```

---

### **3. Health Check Spécialisé**

#### **GET `/api/v1/hatecomment/health`**

**Description** : Vérifie l'état de santé du modèle HateComment BERT

**Réponse** :
```json
{
  "status": "healthy",
  "model": "hatecomment-bert",
  "version": "1.1.0",
  "device": "cuda:0",
  "fine_tuned": true,
  "enhanced": true,
  "gpu_name": "NVIDIA GeForce RTX 4050 Laptop GPU",
  "gpu_memory_allocated": "245.2 MB"
}
```

---

### **4. Informations Détaillées**

#### **GET `/api/v1/hatecomment/info`**

**Description** : Informations complètes sur le modèle

**Réponse** :
```json
{
  "name": "hatecomment-bert",
  "version": "1.1.0",
  "author": "Équipe ETSIA",
  "model_type": "hate_speech_detection",
  "languages": ["français", "anglais"],
  "architecture": "BERT multilingue fine-tuné",
  "enhanced_features": [
    "Post-processing intelligent",
    "Patterns regex français/anglais",
    "Seuil adaptatif",
    "Support GPU optimisé"
  ],
  "performance": {
    "accuracy": "88.94%",
    "f1_score": "90.56%",
    "precision": "89.20%",
    "recall": "91.97%"
  },
  "endpoints": {
    "detection": "/api/v1/hatecomment/detect",
    "batch": "/api/v1/hatecomment/batch-detect",
    "health": "/api/v1/hatecomment/health",
    "info": "/api/v1/hatecomment/info"
  }
}
```

---

### **5. Exemples d'Utilisation**

#### **GET `/api/v1/hatecomment/examples`**

**Description** : Exemples de requêtes et réponses

**Réponse** : Documentation interactive avec exemples pour :
- Hate speech français
- Hate speech anglais  
- Texte normal
- Utilisation batch
- Commandes cURL

---

## 📊 Schémas de Données

### **Formats de Prédiction**

#### **Valeurs de `prediction`**
| Valeur | Description |
|--------|-------------|
| `"HAINEUX"` | Hate speech détecté |
| `"NON-HAINEUX"` | Pas de hate speech |

#### **Niveaux de `severity`**
| Niveau | Confiance | Description |
|--------|-----------|-------------|
| `"Critique"` | > 90% | Très haute confiance |
| `"Élevée"` | 80-90% | Haute confiance |
| `"Moyenne"` | 60-80% | Confiance modérée |
| `"Faible"` | < 60% | Faible confiance |
| `"Aucune"` | N/A | Pas de hate speech |

#### **Classification `hate_classification`**
| Valeur | Description |
|--------|-------------|
| `"haineux"` | Contenu haineux |
| `"non-haineux"` | Contenu normal |

---

## 🔧 Paramètres et Limites

### **Limites de Texte**
- **Minimum** : 1 caractère
- **Maximum** : 5,000 caractères
- **Batch** : 1-100 textes maximum

### **Paramètres Optionnels**
- **`include_reasoning`** : `true`/`false` (défaut: `true` pour detect, `false` pour batch)

### **Performance**
- **Latence** : ~10ms (GPU), ~50ms (CPU)
- **Throughput** : ~100 req/s (GPU), ~20 req/s (CPU)

---

## 🚀 Intégration avec l'API Principale

### **Coexistence des Routes**

#### **Routes Génériques** (Existantes)
```
POST /api/v1/predict?model_name=hatecomment-bert
POST /api/v1/batch-predict?model_name=hatecomment-bert
GET  /api/v1/models/hatecomment-bert/health
```

#### **Routes Spécialisées** (Nouvelles)
```
POST /api/v1/hatecomment/detect
POST /api/v1/hatecomment/batch-detect
GET  /api/v1/hatecomment/health
GET  /api/v1/hatecomment/info
GET  /api/v1/hatecomment/examples
```

### **Avantages des Routes Spécialisées**
- ✅ **Format natif** : Préserve le format original `HAINEUX`/`NON-HAINEUX`
- ✅ **Métadonnées enrichies** : Informations spécifiques au hate speech
- ✅ **Documentation dédiée** : Swagger spécialisé
- ✅ **Exemples contextuels** : Cas d'usage hate speech
- ✅ **Performance optimisée** : Pas de conversion de format

---

## 📚 Documentation Interactive

### **Swagger UI**
Les nouvelles routes sont automatiquement documentées dans Swagger :
```
http://localhost:8000/docs
```

**Section** : `HateComment BERT`

### **Tests Interactifs**
Chaque endpoint peut être testé directement depuis l'interface Swagger avec :
- Formulaires pré-remplis
- Exemples de requêtes
- Validation en temps réel
- Réponses formatées

---

## 🧪 Exemples de Test

### **Test Simple**
```bash
# Détection hate speech
curl -X POST "http://localhost:8000/api/v1/hatecomment/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "Je déteste ces gens", "include_reasoning": true}'

# Health check
curl http://localhost:8000/api/v1/hatecomment/health

# Informations modèle
curl http://localhost:8000/api/v1/hatecomment/info
```

### **Test Batch**
```bash
curl -X POST "http://localhost:8000/api/v1/hatecomment/batch-detect" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Hello world",
      "Je déteste tout le monde",
      "I love this day"
    ],
    "include_reasoning": false
  }'
```

### **Test avec Python**
```python
import requests

# Détection simple
response = requests.post(
    "http://localhost:8000/api/v1/hatecomment/detect",
    json={
        "text": "Je déteste ces gens",
        "include_reasoning": True
    }
)
result = response.json()
print(f"Prédiction: {result['prediction']}")
print(f"Confiance: {result['confidence']}")
```

---

## ⚡ Performance et Monitoring

### **Métriques Exposées**
- **`processing_time`** : Temps de traitement individuel
- **`total_processed`** : Nombre d'éléments traités (batch)
- **`enhanced`** : Version Enhanced utilisée
- **`boost_applied`** : Post-processing appliqué

### **Logs Structurés**
```
INFO - Détection hate speech (texte: 18 chars)
INFO - → Prédiction: HAINEUX (confiance: 0.920)
INFO - Détection batch hate speech (3 textes)
INFO - → Traité 3 textes en 0.12s
```

---

## 🔒 Sécurité et Validation

### **Validation des Entrées**
- **Pydantic** : Validation automatique des schémas
- **Limites** : Taille de texte et nombre d'éléments
- **Sanitization** : Nettoyage des entrées

### **Gestion d'Erreurs**
- **404** : Modèle non trouvé
- **422** : Validation échouée
- **500** : Erreur interne

### **Rate Limiting** (Recommandé)
```python
# À ajouter si nécessaire
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/minute")
@router.post("/detect")
```

---

## 🎯 Cas d'Usage

### **1. Modération de Contenu**
```python
# Modération automatique
def moderate_comment(text):
    response = requests.post(
        "/api/v1/hatecomment/detect",
        json={"text": text, "include_reasoning": False}
    )
    result = response.json()
    
    if result["prediction"] == "HAINEUX" and result["confidence"] > 0.8:
        return "BLOCKED"
    return "APPROVED"
```

### **2. Analyse de Sentiment**
```python
# Analyse batch de commentaires
def analyze_comments(comments):
    response = requests.post(
        "/api/v1/hatecomment/batch-detect",
        json={"texts": comments, "include_reasoning": False}
    )
    results = response.json()["results"]
    
    hate_count = sum(1 for r in results if r["prediction"] == "HAINEUX")
    return f"{hate_count}/{len(comments)} commentaires haineux détectés"
```

### **3. Dashboard de Monitoring**
```python
# Statistiques en temps réel
def get_model_stats():
    health = requests.get("/api/v1/hatecomment/health").json()
    info = requests.get("/api/v1/hatecomment/info").json()
    
    return {
        "status": health["status"],
        "device": health["device"],
        "performance": info["performance"],
        "enhanced": health["enhanced"]
    }
```

---

## 📈 Roadmap

### **Améliorations Prévues**
1. **Rate limiting** intégré
2. **Métriques Prometheus** 
3. **Cache Redis** pour performance
4. **Webhooks** pour notifications
5. **API Keys** pour authentification

### **Nouvelles Fonctionnalités**
1. **Analyse de toxicité** graduée
2. **Détection de cyberharcèlement**
3. **Support multilingue étendu**
4. **Explainability** avancée

---

## ✅ Résumé

**Les routes spécialisées HateComment BERT sont maintenant disponibles !**

### **🎯 Endpoints Principaux**
- `POST /api/v1/hatecomment/detect` - Détection simple
- `POST /api/v1/hatecomment/batch-detect` - Détection batch
- `GET /api/v1/hatecomment/health` - Health check
- `GET /api/v1/hatecomment/info` - Informations détaillées

### **✅ Avantages**
- Format natif préservé (`HAINEUX`/`NON-HAINEUX`)
- Documentation spécialisée
- Performance optimisée
- Coexistence avec routes génériques

**Votre modèle HateComment BERT dispose maintenant de routes dédiées tout en restant compatible avec l'architecture multi-modèles !** 🚀
