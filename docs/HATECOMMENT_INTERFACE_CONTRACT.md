# 📋 Contrat d'Interface - Modèle HateComment BERT

## 📖 Vue d'Ensemble

Ce document définit le contrat d'interface pour le modèle `hatecomment-bert`, un modèle de détection de hate speech intégré dans l'API ETSIA_ML_API. Le modèle respecte l'interface `BaseDepressionModel` tout en fournissant des fonctionnalités spécialisées pour la détection de discours haineux.

---

## 🏗️ Architecture du Modèle

### **Classe Principale**
```python
class HateCommentBertModel(BaseDepressionModel)
```

### **Modèle de Base**
- **Architecture** : BERT multilingue (`bert-base-multilingual-cased`)
- **Type** : Classification binaire de séquences
- **Langues supportées** : Français, Anglais (extensible)
- **Framework** : PyTorch + Transformers

---

## 📝 Propriétés Obligatoires

### **Métadonnées du Modèle**

| Propriété | Type | Valeur | Description |
|-----------|------|--------|-------------|
| `model_name` | `str` | `"hatecomment-bert"` | Identifiant unique du modèle |
| `model_version` | `str` | `"1.0.0"` | Version sémantique |
| `author` | `str` | `"Équipe ETSIA"` | Auteur/Organisation |
| `description` | `str` | `"BERT multilingue fine-tuné pour détection de hate speech"` | Description courte |
| `tags` | `List[str]` | `["bert", "multilingual", "hate-speech", "french", "english", "transformers"]` | Tags de classification |

### **Exemple d'Implémentation**
```python
@property
def model_name(self) -> str:
    return "hatecomment-bert"

@property
def model_version(self) -> str:
    return "1.0.0"

@property
def author(self) -> str:
    return "Équipe ETSIA"
```

---

## 🔧 Méthodes Obligatoires

### **1. Méthode `predict()`**

#### **Signature**
```python
def predict(self, text: str, **kwargs) -> Dict[str, Any]
```

#### **Paramètres d'Entrée**
| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `text` | `str` | ✅ | Texte à analyser (1-5000 caractères) |
| `**kwargs` | `Any` | ❌ | Paramètres additionnels (ignorés) |

#### **Format de Sortie**
```python
{
    "prediction": str,           # "HAINEUX" ou "NON-HAINEUX"
    "confidence": float,         # 0.0 à 1.0
    "severity": str,            # "Aucune", "Faible", "Moyenne", "Élevée", "Critique"
    "reasoning": str,           # Explication détaillée
    "hate_classification": str, # "haineux" ou "non-haineux"
    "original_label": str,      # "LABEL_1" ou "LABEL_0"
    "model_fine_tuned": bool    # True si modèle fine-tuné utilisé
}
```

#### **Exemple de Réponse**
```json
{
    "prediction": "HAINEUX",
    "confidence": 0.92,
    "severity": "Critique",
    "reasoning": "Commentaire classifié comme haineux avec une confiance de 92.00%. Le contenu contient des éléments de discours haineux.",
    "hate_classification": "haineux",
    "original_label": "LABEL_1",
    "model_fine_tuned": false
}
```

### **2. Méthode `batch_predict()`**

#### **Signature**
```python
def batch_predict(self, texts: List[str], **kwargs) -> List[Dict[str, Any]]
```

#### **Paramètres d'Entrée**
| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `texts` | `List[str]` | ✅ | Liste de textes (max 100) |
| `**kwargs` | `Any` | ❌ | Paramètres additionnels |

#### **Format de Sortie**
```python
[
    {
        "prediction": "HAINEUX",
        "confidence": 0.85,
        "severity": "Élevée",
        "reasoning": "...",
        # ... autres champs
    },
    # ... autres résultats
]
```

### **3. Méthode `health_check()`**

#### **Signature**
```python
def health_check(self) -> Dict[str, Any]
```

#### **Format de Sortie**
```python
{
    "status": str,              # "healthy" ou "unhealthy"
    "model": str,               # "hatecomment-bert"
    "version": str,             # "1.0.0"
    "device": str,              # "cuda:0" ou "cpu"
    "fine_tuned": bool,         # État du fine-tuning
    "test_prediction": str,     # Résultat d'un test simple
    # Si GPU disponible :
    "gpu_name": str,            # Nom du GPU
    "gpu_memory_allocated": str, # Mémoire allouée
    "gpu_memory_cached": str,   # Mémoire en cache
    "gpu_utilization": str      # État d'utilisation
}
```

---

## 🎯 Logique de Classification

### **Mapping des Labels**

#### **Labels Internes → API**
| Label Interne | Prédiction API | Description |
|---------------|----------------|-------------|
| `LABEL_1` | `"HAINEUX"` | Contenu haineux détecté |
| `LABEL_0` | `"NON-HAINEUX"` | Contenu non-haineux |

#### **Niveaux de Sévérité**
| Confiance | Sévérité | Description |
|-----------|----------|-------------|
| > 90% | `"Critique"` | Très haute confiance |
| 80-90% | `"Élevée"` | Haute confiance |
| 60-80% | `"Moyenne"` | Confiance modérée |
| < 60% | `"Faible"` | Faible confiance |
| Non-haineux | `"Aucune"` | Pas de hate speech |

### **Prétraitement du Texte**

#### **Étapes de Nettoyage**
1. **Suppression des espaces** en début/fin
2. **Limitation de longueur** à 500 caractères
3. **Réduction des caractères répétés** (ex: "haaaate" → "haate")
4. **Normalisation des espaces** multiples
5. **Suppression des caractères de contrôle**

#### **Gestion des Cas Limites**
| Cas | Comportement |
|-----|--------------|
| Texte vide | Retourne `"NON-HAINEUX"` avec confiance 0.5 |
| Texte trop long | Tronqué à 500 caractères |
| Erreur de traitement | Retourne `"ERREUR"` avec détails |

---

## 🔌 Intégration API

### **Routes Automatiques**

Le modèle est automatiquement exposé via les routes suivantes :

#### **1. Prédiction Simple**
```http
POST /api/v1/predict?model_name=hatecomment-bert
Content-Type: application/json

{
    "text": "Je déteste tout le monde",
    "include_reasoning": true
}
```

#### **2. Prédiction Batch**
```http
POST /api/v1/batch-predict?model_name=hatecomment-bert
Content-Type: application/json

{
    "texts": [
        "Hello world",
        "I hate everyone"
    ],
    "include_reasoning": false
}
```

#### **3. Health Check**
```http
GET /api/v1/models/hatecomment-bert/health
```

#### **4. Liste des Modèles**
```http
GET /api/v1/models
```

### **Schémas de Validation**

#### **Valeurs Acceptées**
```python
class PredictionEnum(str, Enum):
    DEPRESSION = "DÉPRESSION"      # Modèles de dépression
    NORMAL = "NORMAL"              # État normal
    ERROR = "ERREUR"               # Erreur de traitement
    HATEFUL = "HAINEUX"            # ✅ Hate speech détecté
    NON_HATEFUL = "NON-HAINEUX"    # ✅ Pas de hate speech
```

---

## ⚙️ Configuration et Optimisations

### **Device Management**
```python
# Détection automatique du device
self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Optimisations GPU
if self.device.type == "cuda":
    torch.cuda.empty_cache()
    torch.backends.cudnn.benchmark = True
```

### **Pipeline de Classification**
```python
self.classifier = pipeline(
    "text-classification",
    model=self.model,
    tokenizer=self.tokenizer,
    device=0 if self.device.type == "cuda" else -1,
    return_all_scores=True
)
```

### **Gestion des Modèles Fine-tunés**
```python
# Chargement conditionnel
if model_path and self._model_exists(model_path):
    # Modèle fine-tuné personnalisé
    self.model = AutoModelForSequenceClassification.from_pretrained(
        model_path, num_labels=2
    )
    self.is_fine_tuned = True
else:
    # Modèle de base
    self.model = AutoModelForSequenceClassification.from_pretrained(
        'bert-base-multilingual-cased', num_labels=2
    )
    self.is_fine_tuned = False
```

---

## 🧪 Tests et Validation

### **Tests Unitaires Requis**

#### **1. Test d'Initialisation**
```python
def test_model_initialization():
    model = HateCommentBertModel()
    assert model.model_name == "hatecomment-bert"
    assert model.model_version == "1.0.0"
    assert "hate-speech" in model.tags
```

#### **2. Test de Prédiction**
```python
def test_predict_basic():
    model = HateCommentBertModel()
    result = model.predict("Test message")
    
    assert "prediction" in result
    assert result["prediction"] in ["HAINEUX", "NON-HAINEUX", "ERREUR"]
    assert 0 <= result["confidence"] <= 1
```

#### **3. Test Health Check**
```python
def test_health_check():
    model = HateCommentBertModel()
    health = model.health_check()
    
    assert health["status"] in ["healthy", "unhealthy"]
    assert health["model"] == "hatecomment-bert"
```

### **Critères de Performance**

| Métrique | Seuil Minimum | Objectif |
|----------|---------------|----------|
| Temps de réponse | < 2s par prédiction | < 1s |
| Mémoire GPU | < 2GB | < 1GB |
| Accuracy | > 75% | > 80% |
| F1-Score | > 70% | > 75% |

---

## 🚨 Gestion d'Erreurs

### **Types d'Erreurs**

#### **1. Erreurs d'Initialisation**
```python
# Modèle non initialisé
if not self._initialized:
    raise RuntimeError(f"{self.model_name} n'est pas initialisé correctement")
```

#### **2. Erreurs de Prédiction**
```python
# Retour gracieux en cas d'erreur
return {
    "prediction": "ERREUR",
    "confidence": 0.0,
    "severity": "Aucune",
    "reasoning": f"Erreur lors de l'analyse: {str(e)}"
}
```

### **Logging**
```python
# Utilisation du logger uniforme
from app.utils.logger import setup_logger
logger = setup_logger(__name__)

# Messages standardisés
logger.info(f"✓ {self.model_name} initialisé avec succès")
logger.error(f"✗ Erreur de prédiction {self.model_name}: {e}")
```

---

## 📊 Métriques et Monitoring

### **Métriques Exposées**
- **Temps de traitement** par prédiction
- **Utilisation mémoire** GPU/CPU
- **Taux de succès** des prédictions
- **Distribution des prédictions** (haineux vs non-haineux)

### **Health Check Détaillé**
```python
{
    "status": "healthy",
    "model": "hatecomment-bert",
    "version": "1.0.0",
    "device": "cuda:0",
    "fine_tuned": false,
    "test_prediction": "NON-HAINEUX",
    "gpu_name": "NVIDIA GeForce RTX 4050",
    "gpu_memory_allocated": "245.2 MB",
    "gpu_memory_cached": "512.0 MB",
    "gpu_utilization": "Available"
}
```

---

## 🔄 Évolutions Futures

### **Améliorations Prévues**
1. **Support multilingue étendu** (espagnol, allemand, italien)
2. **Fine-tuning personnalisé** sur données spécifiques
3. **Détection de nuances** (ironie, sarcasme)
4. **Analyse contextuelle** (conversations complètes)

### **Rétrocompatibilité**
- ✅ **Interface stable** : Pas de breaking changes
- ✅ **Versioning sémantique** : Incréments de version appropriés
- ✅ **Migration guidée** : Documentation des changements

---

## 📚 Références

- **Modèle de base** : [BERT Multilingual](https://huggingface.co/bert-base-multilingual-cased)
- **Framework** : [Transformers](https://huggingface.co/transformers/)
- **Interface** : `BaseDepressionModel` (voir `app/core/base_model.py`)
- **Tests** : `tests/test_hatecomment_bert.py`

---

**Version du document** : 1.0.0  
**Dernière mise à jour** : 20 octobre 2025  
**Auteur** : Équipe ETSIA
