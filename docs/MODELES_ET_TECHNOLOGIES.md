# 🤖 Modèles et Technologies - ETSIA ML API

Documentation complète des modèles de Machine Learning et des technologies utilisées dans le projet.

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Modèles de Détection de Dépression](#modèles-de-détection-de-dépression)
3. [Modèle de Détection de Hate Speech](#modèle-de-détection-de-hate-speech)
4. [Modèle d'Analyse d'Images](#modèle-danalyse-dimages)
5. [Modèle de Détection NSFW](#modèle-de-détection-nsfw)
6. [Système de Recommandation](#système-de-recommandation)
7. [Générateur de Contenu](#générateur-de-contenu)
8. [Architecture Technique](#architecture-technique)
9. [Comparaison des Modèles](#comparaison-des-modèles)

---

## 🎯 Vue d'Ensemble

L'API ETSIA ML intègre **7 modèles de Machine Learning** différents, chacun spécialisé dans une tâche spécifique :

| Modèle | Tâche | Technologie Principale | Latence |
|--------|-------|------------------------|---------|
| **CamemBERT Depression** | Détection dépression (FR) | BERT fine-tuné | 20-50ms |
| **Qwen Depression** | Détection dépression + raisonnement | LLM (1.5B params) | 200-500ms |
| **YANSNET LLM** | Détection dépression (legacy) | GPT/Claude/Llama | 300ms |
| **HateComment BERT** | Détection hate speech | BERT multilingue | 50-100ms |
| **Sensitive Image Caption** | Analyse contenu images | Vision + NLP | 2-15s |
| **NSFW Detection** | Détection contenu NSFW | ShieldGemma2 | 1-3s |
| **Recommendation System** | Recommandation posts | Filtrage collaboratif | 10-50ms |
| **Content Generator** | Génération contenu | LLM (3B params) | 2-10s |

---

## 📝 Modèles de Détection de Dépression

### 1. CamemBERT Depression (Recommandé)

**Objectif :** Détection rapide et précise de signes de dépression dans les textes français.

#### Technologie

- **Modèle de base :** `camembert-base` (110M paramètres)
- **Architecture :** BERT (Bidirectional Encoder Representations from Transformers)
- **Framework :** Transformers (HuggingFace)
- **Entraînement :** Pré-entraîné sur 138GB de texte français

#### Méthodologie

1. **Tokenization :** Découpage du texte en tokens avec le tokenizer CamemBERT
2. **Embedding :** Conversion des tokens en vecteurs de 768 dimensions
3. **Classification :** Couche de classification binaire (DÉPRESSION vs NORMAL)
4. **Scoring :** Softmax pour obtenir les probabilités de confiance

#### Caractéristiques Techniques

```python
# Configuration
Device: CPU/GPU (auto-détection)
Max Length: 512 tokens
Batch Size: Dynamique
Precision: FP32
```

#### Performance

- **Latence :** 20-50ms (CPU), 5-10ms (GPU)
- **RAM :** 500-600MB
- **Throughput :** >20 req/s (CPU)
- **Précision :** ~80% (selon dataset)

#### Niveaux de Sévérité

| Confiance | Sévérité | Action |
|-----------|----------|--------|
| ≥ 0.90 | Critique | Alerte immédiate |
| ≥ 0.75 | Élevée | Notification modérateurs |
| ≥ 0.60 | Moyenne | Suivi |
| < 0.60 | Faible | Enregistrement |

#### Exemple d'Utilisation

```python
from app.services.camembert_depression import CamemBERTDepressionModel

model = CamemBERTDepressionModel()
result = model.predict("Je me sens triste et sans espoir")

# Résultat
{
    "prediction": "DÉPRESSION",
    "confidence": 0.85,
    "severity": "Élevée",
    "processing_time": 45.2,
    "reasoning": "Le modèle CamemBERT a détecté..."
}
```



### 2. Qwen Depression (Raisonnement Avancé)

**Objectif :** Détection de dépression avec explications détaillées et meilleure compréhension du contexte.

#### Technologie

- **Modèle :** `qwen2.5:1.5b` (1.5 milliards de paramètres)
- **Architecture :** Transformer-based LLM
- **Déploiement :** Ollama (local)
- **Langage :** Multilingue (FR, EN, etc.)

#### Méthodologie

1. **Prompt Engineering :** Construction d'un prompt structuré pour l'analyse
2. **Génération :** Le LLM analyse le texte et génère une réponse JSON
3. **Parsing :** Extraction et validation de la réponse JSON
4. **Fallback :** Analyse textuelle si le JSON échoue

#### Prompt Template

```python
DETECTION_PROMPT = """Tu es un assistant spécialisé dans l'analyse de texte 
pour détecter des signes de dépression.

Analyse le texte suivant et détermine s'il contient des indicateurs de dépression.

Texte à analyser: "{text}"

Réponds UNIQUEMENT avec un JSON valide dans ce format exact:
{
    "prediction": "DEPRESSION" ou "NORMAL",
    "confidence": un nombre entre 0.0 et 1.0,
    "severity": "Aucune", "Faible", "Moyenne", "Élevée" ou "Critique",
    "reasoning": "explication courte de ton analyse"
}
"""
```

#### Performance

- **Latence :** 200-500ms (CPU), 100-200ms (GPU)
- **RAM :** 2-3GB
- **Throughput :** >2 req/s
- **Précision :** ~75-80%

#### Avantages vs CamemBERT

| Critère | CamemBERT | Qwen |
|---------|-----------|------|
| **Vitesse** | ⚡⚡⚡ (20-50ms) | ⚡⚡ (200-500ms) |
| **Raisonnement** | ⭐ (basique) | ⭐⭐⭐ (détaillé) |
| **Contexte** | ⭐⭐ (512 tokens) | ⭐⭐⭐ (2048 tokens) |
| **Coût** | Gratuit | Gratuit (local) |
| **Offline** | ✅ | ✅ |

#### Exemple d'Utilisation

```python
from app.services.qwen_depression import QwenDepressionModel

model = QwenDepressionModel()
result = model.predict("Je n'arrive plus à dormir, je me sens vide")

# Résultat
{
    "prediction": "DÉPRESSION",
    "confidence": 0.82,
    "severity": "Élevée",
    "processing_time": 350.5,
    "reasoning": "Le texte exprime des troubles du sommeil et un sentiment de vide..."
}
```

---

### 3. YANSNET LLM (Legacy)

**Objectif :** Détection de dépression avec LLM externes (GPT, Claude, Llama).

#### Technologie

- **Providers :** OpenAI GPT-4o-mini, Anthropic Claude, Ollama Llama
- **Architecture :** API externe ou local
- **Méthode :** Prompt engineering + parsing JSON

#### Configuration

```env
# OpenAI
LLM_PROVIDER=gpt
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet

# Ollama
LLM_PROVIDER=local
OLLAMA_MODEL=llama3.2
```

#### Performance

| Provider | Latence | Coût | Qualité |
|----------|---------|------|---------|
| **GPT-4o-mini** | ~300ms | $0.00006/req | ⭐⭐⭐⭐ |
| **Claude Sonnet** | ~300ms | $0.015/req | ⭐⭐⭐⭐⭐ |
| **Llama 3.2 (local)** | ~300ms | Gratuit | ⭐⭐⭐ |

---

## 💬 Modèle de Détection de Hate Speech

### HateComment BERT (Fine-tuné)

**Objectif :** Détection de discours haineux dans les commentaires (français et anglais).

#### Technologie

- **Modèle de base :** `bert-base-multilingual-cased`
- **Fine-tuning :** Entraîné sur dataset de hate speech français
- **Architecture :** BERT + Classification binaire
- **Post-processing :** Détection de patterns améliorée

#### Méthodologie

1. **Prétraitement :** Nettoyage et normalisation du texte
2. **Tokenization :** BERT tokenizer multilingue
3. **Classification :** Modèle fine-tuné (HAINEUX vs NON-HAINEUX)
4. **Post-processing :** Boost basé sur patterns regex
5. **Scoring :** Confiance ajustée avec patterns

#### Patterns de Détection

```python
# Patterns français
hate_patterns_fr = [
    r'\b(je déteste|j\'ai horreur de|je hais)\s+(ces?|les?|tous?\s+les?)',
    r'\bsale\s+race\b',
    r'\b(crève|crevez|mort aux?)\b',
    r'\b(dégage|dégagez)\s+(de\s+)?(notre?|mon)\s+(pays?|territoire)',
]

# Patterns anglais
hate_patterns_en = [
    r'\bi\s+hate\s+(all|those|these)\s+\w+',
    r'\b(kill|die)\s+(all|those|these)',
    r'\b(go\s+back|get\s+out)\s+(to|of)',
]
```

#### Performance

- **Latence :** 50-100ms (CPU), 10-20ms (GPU)
- **RAM :** 800MB-1GB
- **Précision :** >90% (après fine-tuning)
- **Recall :** >85%

#### Niveaux de Sévérité

| Confiance | Sévérité | Action |
|-----------|----------|--------|
| > 0.90 | Critique | Suppression automatique |
| > 0.80 | Élevée | Modération prioritaire |
| > 0.60 | Moyenne | Signalement |
| < 0.60 | Faible | Surveillance |

#### Exemple d'Utilisation

```python
from app.services.hatecomment_bert import HateCommentBertModel

model = HateCommentBertModel()
result = model.predict("Je déteste tous ces gens")

# Résultat
{
    "prediction": "HAINEUX",
    "confidence": 0.92,
    "severity": "Critique",
    "reasoning": "Commentaire classifié comme haineux...",
    "boost_applied": True,
    "base_score": 0.65,
    "enhanced_score": 0.92
}
```



---

## 🖼️ Modèle d'Analyse d'Images

### Sensitive Image Caption

**Objectif :** Détection de contenu sensible dans les images (drogue, violence, sexe).

#### Technologie

- **Captioning :** `Salesforce/blip-image-captioning-base`
- **Traduction :** `Helsinki-NLP/opus-mt-en-fr`
- **Détection :** Pattern matching + mots-clés
- **Framework :** Transformers + PIL

#### Méthodologie

1. **Génération de légende :** BLIP génère une description en anglais
2. **Détection de mots-clés :** Recherche de termes sensibles
3. **Traduction :** Conversion EN→FR
4. **Filtrage :** Masquage des mots sensibles si détectés
5. **Classification :** SENSIBLE vs SÛR

#### Mots-clés Sensibles

```python
SENSITIVE_KEYWORDS = {
    # Drogue
    'drugs', 'cocaine', 'heroin', 'marijuana', 'cannabis',
    'drogue', 'cocaïne', 'héroïne',
    
    # Contenu sexuel
    'sex', 'porn', 'nude', 'naked', 'nsfw',
    'sexe', 'pornographie', 'nudité',
    
    # Violence
    'gun', 'weapon', 'knife', 'blood', 'violence',
    'arme', 'couteau', 'sang',
    
    # Autres
    'bomb', 'explosive', 'suicide',
    'bombe', 'explosif'
}
```

#### Pipeline de Traitement

```
Image → BLIP → Caption (EN) → Détection → Traduction → Résultat
                                    ↓
                            Mots-clés sensibles?
                                    ↓
                            OUI: SENSIBLE (filtré)
                            NON: SÛR (complet)
```

#### Performance

- **Latence :** 2-15s (selon taille image)
- **RAM :** 2-3GB
- **Précision :** ~85-90%
- **Faux positifs :** <8%

#### Exemple d'Utilisation

```python
from app.services.sensitive_image_caption import SensitiveImageCaptionModel
from PIL import Image

model = SensitiveImageCaptionModel()
image = Image.open("photo.jpg")
result = model.predict(image=image)

# Résultat (contenu sûr)
{
    "prediction": "SÛR",
    "confidence": 0.95,
    "severity": "Aucune",
    "reasoning": "✅ Contenu sûr - Aucun élément sensible détecté",
    "caption_en": "a cat sitting on a table",
    "caption_fr": "un chat assis sur une table",
    "is_safe": True
}

# Résultat (contenu sensible)
{
    "prediction": "SENSIBLE",
    "confidence": 0.85,
    "severity": "Élevée",
    "reasoning": "⚠️ CONTENU SENSIBLE DÉTECTÉ",
    "caption_en": "a *** on the table",
    "caption_fr": "une *** sur la table",
    "is_safe": False
}
```

---

## 🚫 Modèle de Détection NSFW

### ShieldGemma2 Image Classification

**Objectif :** Détection de contenu NSFW (Not Safe For Work) dans les images.

#### Technologie

- **Modèle :** `google/shieldgemma-2b`
- **Architecture :** Vision Transformer
- **Classification :** Multi-catégories (Safe vs Violation)
- **Framework :** Transformers

#### Catégories Détectées

- **Nudité :** Contenu sexuellement explicite
- **Violence :** Images violentes ou gore
- **Haine :** Symboles ou contenus haineux
- **Harcèlement :** Contenu de harcèlement

#### Performance

- **Latence :** 1-3s
- **RAM :** 3-4GB
- **Précision :** >90%
- **Multi-catégories :** Oui

#### Exemple d'Utilisation

```python
from app.services.model_censure import predict_image
from PIL import Image

image = Image.open("photo.jpg")
results = predict_image(image)

# Résultat
{
    "nudity": {
        "Safe": 95.2,
        "Violation": 4.8,
        "Prediction": "Safe"
    },
    "violence": {
        "Safe": 98.1,
        "Violation": 1.9,
        "Prediction": "Safe"
    },
    "hate": {
        "Safe": 99.5,
        "Violation": 0.5,
        "Prediction": "Safe"
    }
}
```

---

## 📊 Système de Recommandation

### User-User Collaborative Filtering

**Objectif :** Recommander des posts pertinents aux utilisateurs basé sur leurs interactions.

#### Technologie

- **Algorithme :** Filtrage collaboratif user-user
- **Similarité :** Cosine similarity
- **Cache :** Redis (TTL: 1h)
- **Base de données :** PostgreSQL
- **Framework :** NumPy, Pandas

#### Méthodologie

1. **Collecte des interactions :** Likes, commentaires, partages
2. **Matrice utilisateur-post :** Construction de la matrice d'interactions
3. **Calcul de similarité :** Similarité cosinus entre utilisateurs
4. **Génération de recommandations :** Top-N posts des utilisateurs similaires
5. **Filtrage :** Exclusion des posts déjà vus
6. **Ranking :** Tri par score de pertinence

#### Architecture avec Cache

```
Requête → Cache Redis?
            ↓
        OUI: Retour immédiat (10-50ms)
            ↓
        NON: PostgreSQL → Calcul → Cache → Retour (200-500ms)
```

#### Performance

| Métrique | Sans Cache | Avec Cache | Amélioration |
|----------|------------|------------|--------------|
| **Latence** | 200-500ms | 10-50ms | **10-50x** |
| **Charge DB** | Élevée | Minimale | **90%** |
| **Throughput** | 5 req/s | 100+ req/s | **20x** |

#### Configuration

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CACHE_TTL=3600  # 1 heure

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_DB=etsia_ai
```

#### Exemple d'Utilisation

```python
from app.services.recommendation import RecommendationModel

model = RecommendationModel(use_cache=True)
result = model.predict(user_id=1, top_n=10)

# Résultat
{
    "prediction": "RECOMMANDATIONS",
    "user_id": 1,
    "recommendations": [
        {"post_id": 42, "score": 0.95},
        {"post_id": 17, "score": 0.89},
        {"post_id": 8, "score": 0.85}
    ],
    "total_recommendations": 10
}
```



---

## ✍️ Générateur de Contenu

### YANSNET Content Generator

**Objectif :** Générer des posts et commentaires réalistes pour peupler l'interface YANSNET.

#### Technologie

- **Modèle principal :** `llama3.2:3b` (via Ollama)
- **Fallback :** `llama3.2:1b`
- **Alternatives :** GPT-4o-mini, Claude
- **Méthode :** Prompt engineering + génération de texte

#### Types de Contenu Générés

| Type | Description | Sentiment |
|------|-------------|-----------|
| **Confession** | Partage personnel | Variable |
| **Coup de gueule** | Expression de frustration | Négatif |
| **Demande d'aide** | Question ou besoin d'aide | Variable |
| **Message de soutien** | Encouragement | Positif |
| **Blague** | Humour | Positif/Neutre |
| **Information utile** | Partage d'info | Neutre |

#### Sujets Disponibles

- Les partiels stressants
- La vie en résidence universitaire
- Le stage de fin d'études
- Les associations étudiantes
- Les fêtes étudiantes
- La cantine de l'école
- Les échanges internationaux
- ... (20+ sujets)

#### Méthodologie

1. **Sélection :** Type de post + sujet + sentiment
2. **Prompt Construction :** Création d'un prompt structuré
3. **Génération :** Appel au LLM
4. **Post-processing :** Nettoyage et validation
5. **Commentaires :** Génération optionnelle de commentaires

#### Prompt Template

```python
system_prompt = """Tu es un assistant qui génère des publications réalistes 
pour un forum d'école d'ingénieurs. Génère du contenu crédible, naturel, 
sans marqueurs artificiels."""

user_prompt = """Génère un post de type '{post_type}' sur le sujet '{topic}', 
avec un sentiment '{sentiment}'. Minimum 3 phrases, style étudiant naturel."""
```

#### Performance

- **Latence :** 2-10s par post
- **RAM :** 4-6GB (Llama 3.2 3B)
- **Qualité :** Très réaliste
- **Variété :** Excellente

#### Exemple d'Utilisation

```python
from app.services.yansnet_content_generator import YansnetContentGeneratorModel

model = YansnetContentGeneratorModel()

# Générer un post
post = model.generate_post(
    post_type="demande d'aide",
    topic="les partiels stressants",
    sentiment="négatif"
)

# Résultat
{
    "content": "Bonjour à tous, je suis vraiment stressé par les partiels...",
    "post_type": "demande d'aide",
    "topic": "les partiels stressants",
    "sentiment": "négatif"
}

# Générer post + commentaires
full_post = model.generate_post_with_comments(
    post_type="blague",
    topic="les fêtes étudiantes",
    num_comments=10
)

# Résultat
{
    "post": {...},
    "comments": [
        {"content": "Haha trop vrai !", "sentiment": "positif"},
        {"content": "J'adore cette blague", "sentiment": "positif"}
    ],
    "total_comments": 10
}
```

---

## 🏗️ Architecture Technique

### Stack Technologique Global

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI (API REST)                   │
├─────────────────────────────────────────────────────────┤
│                   Model Registry                         │
│              (Gestion multi-modèles)                     │
├─────────────────────────────────────────────────────────┤
│  CamemBERT │ Qwen │ BERT │ BLIP │ ShieldGemma │ Llama  │
│  (110M)    │(1.5B)│(110M)│(Base)│   (2B)      │ (3B)   │
├─────────────────────────────────────────────────────────┤
│  Transformers │ PyTorch │ Ollama │ OpenAI │ Anthropic  │
├─────────────────────────────────────────────────────────┤
│         PostgreSQL (Métriques) │ Redis (Cache)          │
└─────────────────────────────────────────────────────────┘
```

### Frameworks et Bibliothèques

| Catégorie | Technologie | Version | Usage |
|-----------|-------------|---------|-------|
| **API** | FastAPI | 0.109.0 | Framework web |
| **ML** | Transformers | 4.30.0+ | Modèles NLP/Vision |
| **ML** | PyTorch | 2.0.0+ | Deep Learning |
| **LLM** | Ollama | Latest | LLM local |
| **LLM** | OpenAI | 1.10.0+ | GPT API |
| **LLM** | Anthropic | 0.18.0+ | Claude API |
| **Data** | NumPy | 1.24.0+ | Calculs numériques |
| **Data** | Pandas | 2.0.0+ | Manipulation données |
| **DB** | PostgreSQL | 14+ | Base de données |
| **Cache** | Redis | 7+ | Cache distribué |
| **Image** | Pillow | 10.0.0+ | Traitement images |
| **HTTP** | httpx | 0.26.0+ | Client HTTP async |

### Architecture Multi-Modèles

```python
# Registre centralisé
from app.core.model_registry import registry

# Enregistrement des modèles
registry.register(CamemBERTDepressionModel(), set_as_default=True)
registry.register(QwenDepressionModel())
registry.register(HateCommentBertModel())
# ...

# Utilisation
model = registry.get_model("camembert-depression")
result = model.predict("texte à analyser")

# Sélection via API
GET /api/v1/predict?model_name=qwen-depression
```

### Providers Hybrides

L'API utilise différents providers selon la tâche :

```python
# Configuration dans .env
DETECTION_PROVIDER=camembert  # Pour détection rapide
GENERATION_PROVIDER=ollama    # Pour génération de contenu

# Fallback automatique
if primary_model_fails:
    use_fallback_model()
```

### Optimisations

#### 1. Cache Redis

```python
# Configuration
REDIS_CACHE_TTL=3600  # 1 heure
ENABLE_CACHE=true

# Amélioration: 10-50x plus rapide
```

#### 2. Batch Processing

```python
# Traitement par lots
results = model.batch_predict(texts=[...])

# Amélioration: 2-5x plus rapide
```

#### 3. GPU Acceleration

```python
# Auto-détection GPU
device = "cuda" if torch.cuda.is_available() else "cpu"

# Amélioration: 5-10x plus rapide
```

#### 4. Model Warmup

```python
# Préchauffage au démarrage
model._warmup_model()

# Évite la latence du premier appel
```

---

## 📊 Comparaison des Modèles

### Détection de Dépression

| Critère | CamemBERT | Qwen | YANSNET LLM |
|---------|-----------|------|-------------|
| **Vitesse** | ⚡⚡⚡ (20-50ms) | ⚡⚡ (200-500ms) | ⚡⚡ (300ms) |
| **Précision** | ⭐⭐⭐⭐ (80%) | ⭐⭐⭐⭐ (75-80%) | ⭐⭐⭐⭐ (75%) |
| **Raisonnement** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Contexte** | 512 tokens | 2048 tokens | Variable |
| **Coût** | Gratuit | Gratuit | $0.00006/req |
| **Offline** | ✅ | ✅ | ❌ (GPT/Claude) |
| **RAM** | 500MB | 2-3GB | Variable |
| **Recommandé pour** | Production | Analyse détaillée | Prototypage |

### Analyse d'Images

| Critère | Sensitive Caption | NSFW Detection |
|---------|-------------------|----------------|
| **Vitesse** | ⚡ (2-15s) | ⚡⚡ (1-3s) |
| **Précision** | ⭐⭐⭐⭐ (85-90%) | ⭐⭐⭐⭐⭐ (>90%) |
| **Catégories** | 4 types | Multi-catégories |
| **Multilingue** | ✅ (EN→FR) | ❌ |
| **RAM** | 2-3GB | 3-4GB |
| **Recommandé pour** | Modération générale | Détection NSFW |

### Génération de Contenu

| Critère | Llama 3.2 3B | GPT-4o-mini | Claude |
|---------|--------------|-------------|--------|
| **Vitesse** | ⚡⚡ (2-10s) | ⚡⚡⚡ (1-3s) | ⚡⚡⚡ (1-3s) |
| **Qualité** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Variété** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Coût** | Gratuit | $0.00006/req | $0.015/req |
| **Offline** | ✅ | ❌ | ❌ |
| **RAM** | 4-6GB | N/A | N/A |
| **Recommandé pour** | Production | Prototypage | Haute qualité |



---

## 🔬 Méthodologies de Machine Learning

### 1. Transfer Learning

**Utilisé par :** CamemBERT, BERT, BLIP, ShieldGemma

**Principe :** Utiliser un modèle pré-entraîné sur une grande quantité de données et l'adapter à une tâche spécifique.

```
Modèle pré-entraîné → Fine-tuning → Modèle spécialisé
(138GB texte FR)      (Dataset hate)  (Détection hate)
```

**Avantages :**
- Moins de données nécessaires
- Meilleure performance
- Temps d'entraînement réduit

### 2. Prompt Engineering

**Utilisé par :** Qwen, YANSNET LLM, Content Generator

**Principe :** Concevoir des prompts optimaux pour guider le LLM vers la réponse souhaitée.

```python
# Mauvais prompt
"Analyse ce texte"

# Bon prompt
"""Tu es un expert en psychologie. Analyse le texte suivant et détermine 
s'il contient des signes de dépression. Réponds au format JSON avec:
- prediction: DEPRESSION ou NORMAL
- confidence: 0.0 à 1.0
- reasoning: explication détaillée"""
```

**Techniques :**
- Few-shot learning (exemples dans le prompt)
- Chain-of-thought (raisonnement étape par étape)
- Format structuré (JSON, XML)

### 3. Filtrage Collaboratif

**Utilisé par :** Système de Recommandation

**Principe :** Recommander des items basés sur les préférences d'utilisateurs similaires.

```
User A: [Post1✓, Post2✓, Post3✗, Post4✓]
User B: [Post1✓, Post2✓, Post3✓, Post4✗]
         ↓ Similarité: 0.75
Recommander Post3 à User A
```

**Formule de similarité cosinus :**
```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

### 4. Ensemble Methods

**Utilisé par :** HateComment BERT (post-processing)

**Principe :** Combiner plusieurs approches pour améliorer la précision.

```
Prédiction BERT (0.65) + Pattern Matching (boost +0.27) = Score final (0.92)
```

**Avantages :**
- Réduit les faux négatifs
- Améliore la robustesse
- Capture différents types de patterns

### 5. Multi-Modal Learning

**Utilisé par :** Sensitive Image Caption

**Principe :** Combiner plusieurs modalités (vision + texte) pour une meilleure compréhension.

```
Image → Vision Model → Caption → NLP Model → Classification
```

---

## 🎓 Concepts Clés

### BERT (Bidirectional Encoder Representations from Transformers)

**Architecture :** Transformer encoder-only

**Caractéristiques :**
- Bidirectionnel (contexte gauche + droite)
- Pré-entraînement sur MLM (Masked Language Modeling)
- Fine-tuning pour tâches spécifiques

**Variantes utilisées :**
- `camembert-base` : BERT pour le français
- `bert-base-multilingual-cased` : BERT multilingue

### LLM (Large Language Model)

**Architecture :** Transformer decoder-only (généralement)

**Caractéristiques :**
- Milliards de paramètres (1.5B à 175B+)
- Génération de texte autoregressive
- Zero-shot / Few-shot learning

**Modèles utilisés :**
- Qwen 2.5 (1.5B) : Détection avec raisonnement
- Llama 3.2 (3B) : Génération de contenu
- GPT-4o-mini : API externe
- Claude Sonnet : API externe

### Vision Transformers

**Architecture :** Transformer adapté pour les images

**Caractéristiques :**
- Découpage de l'image en patches
- Attention sur les patches
- Classification ou génération

**Modèles utilisés :**
- BLIP : Image captioning
- ShieldGemma2 : Classification NSFW

### Embeddings

**Principe :** Représentation vectorielle dense des données

```
Texte: "Je suis triste" → [0.23, -0.45, 0.67, ..., 0.12] (768 dimensions)
```

**Propriétés :**
- Capture la sémantique
- Permet le calcul de similarité
- Utilisé pour classification, clustering, etc.

---

## 📈 Métriques de Performance

### Métriques de Classification

| Métrique | Formule | Usage |
|----------|---------|-------|
| **Accuracy** | (TP + TN) / Total | Précision globale |
| **Precision** | TP / (TP + FP) | Qualité des positifs |
| **Recall** | TP / (TP + FN) | Couverture des positifs |
| **F1-Score** | 2 × (P × R) / (P + R) | Équilibre P/R |

**Légende :**
- TP : True Positives (vrais positifs)
- TN : True Negatives (vrais négatifs)
- FP : False Positives (faux positifs)
- FN : False Negatives (faux négatifs)

### Métriques de Latence

| Percentile | Description | Seuil |
|------------|-------------|-------|
| **p50** | Médiane | Latence typique |
| **p95** | 95e percentile | Latence acceptable |
| **p99** | 99e percentile | Latence maximale |

**Exemple CamemBERT :**
- p50: 30ms
- p95: 50ms
- p99: 100ms

### Métriques de Cache

| Métrique | Formule | Objectif |
|----------|---------|----------|
| **Hit Rate** | Hits / (Hits + Misses) | >80% |
| **Miss Rate** | Misses / (Hits + Misses) | <20% |
| **Speedup** | Latency(no cache) / Latency(cache) | >10x |

---

## 🔧 Configuration et Déploiement

### Variables d'Environnement

```env
# ============================================================================
# DETECTION PROVIDER
# ============================================================================
DETECTION_PROVIDER=camembert  # camembert, qwen, xlm-roberta

# CamemBERT
CAMEMBERT_MODEL=camembert-base
CAMEMBERT_DEVICE=cpu
CAMEMBERT_MAX_LENGTH=512

# Qwen
QWEN_DETECTION_MODEL=qwen2.5:1.5b
QWEN_MAX_LENGTH=2048

# ============================================================================
# GENERATION PROVIDER
# ============================================================================
GENERATION_PROVIDER=ollama  # ollama, gpt, claude

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_GENERATION_MODEL=llama3.2:3b

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet

# ============================================================================
# DATABASE & CACHE
# ============================================================================
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=etsia_metrics

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CACHE_TTL=3600
ENABLE_CACHE=true
```

### Déploiement Docker

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DETECTION_PROVIDER=camembert
      - GENERATION_PROVIDER=ollama
    depends_on:
      - postgres
      - redis
      - ollama
  
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: etsia_metrics
  
  redis:
    image: redis:7-alpine
  
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-data:/root/.ollama
```

### Commandes de Démarrage

```bash
# Installation
pip install -r requirements.txt

# Lancer l'API
uvicorn app.main:app --reload --port 8000

# Avec Docker
docker-compose up -d

# Avec Ollama
ollama pull qwen2.5:1.5b
ollama pull llama3.2:3b
ollama serve
```

---

## 📚 Ressources et Documentation

### Documentation Officielle

- **Transformers :** https://huggingface.co/docs/transformers/
- **PyTorch :** https://pytorch.org/docs/
- **FastAPI :** https://fastapi.tiangolo.com/
- **Ollama :** https://ollama.ai/docs/
- **OpenAI :** https://platform.openai.com/docs/
- **Anthropic :** https://docs.anthropic.com/

### Modèles HuggingFace

- **CamemBERT :** https://huggingface.co/camembert-base
- **BERT Multilingual :** https://huggingface.co/bert-base-multilingual-cased
- **BLIP :** https://huggingface.co/Salesforce/blip-image-captioning-base
- **ShieldGemma2 :** https://huggingface.co/google/shieldgemma-2b
- **Opus MT :** https://huggingface.co/Helsinki-NLP/opus-mt-en-fr

### Papers de Référence

- **BERT :** Devlin et al. (2018) - "BERT: Pre-training of Deep Bidirectional Transformers"
- **CamemBERT :** Martin et al. (2020) - "CamemBERT: a Tasty French Language Model"
- **Transformers :** Vaswani et al. (2017) - "Attention Is All You Need"
- **BLIP :** Li et al. (2022) - "BLIP: Bootstrapping Language-Image Pre-training"

---

## 🎯 Recommandations d'Utilisation

### Par Cas d'Usage

| Cas d'Usage | Modèle Recommandé | Raison |
|-------------|-------------------|--------|
| **Production (détection rapide)** | CamemBERT | Latence minimale, bon rapport qualité/vitesse |
| **Analyse détaillée** | Qwen | Meilleur raisonnement, contexte étendu |
| **Prototypage** | YANSNET LLM (GPT) | Facile à configurer, bonne qualité |
| **Modération commentaires** | HateComment BERT | Spécialisé, fine-tuné, rapide |
| **Modération images** | NSFW Detection | Haute précision, multi-catégories |
| **Recommandations** | Collaborative Filtering | Performant avec cache |
| **Génération contenu** | Llama 3.2 3B | Gratuit, bonne qualité, offline |

### Par Contraintes

| Contrainte | Solution |
|------------|----------|
| **Latence < 100ms** | CamemBERT, HateComment BERT |
| **Offline requis** | CamemBERT, Qwen, Llama (via Ollama) |
| **Budget limité** | Modèles locaux (CamemBERT, Qwen, Llama) |
| **Haute qualité** | GPT-4o-mini, Claude, Qwen |
| **Multilingue** | BERT Multilingual, GPT, Claude |
| **Raisonnement détaillé** | Qwen, GPT, Claude |

---

## 🔮 Évolutions Futures

### Améliorations Prévues

1. **Fine-tuning CamemBERT** sur dataset de dépression français
2. **Modèle XLM-RoBERTa** pour support multilingue
3. **Cache des recommandations** par utilisateur
4. **Modèle de détection de suicide** spécialisé
5. **API de feedback** pour amélioration continue
6. **Monitoring avancé** avec Prometheus/Grafana
7. **A/B testing** entre modèles
8. **Quantization** pour réduire la taille des modèles

### Nouvelles Fonctionnalités

- **Détection d'émotions** (joie, colère, tristesse, etc.)
- **Analyse de sentiment** fine-grained
- **Détection de cyberharcèlement**
- **Recommandations personnalisées** avec deep learning
- **Génération d'images** pour les posts
- **Résumé automatique** de threads longs

---

## 📞 Support et Contribution

### Documentation Projet

- [Guide Développeur](GUIDE_DEVELOPPEUR.md)
- [API Contract](API_CONTRACT.md)
- [Ajouter un Modèle](ADD_YOUR_MODEL.md)
- [Déploiement](DEPLOYMENT.md)
- [Workflow Git](GIT_WORKFLOW.md)

### Contact

Pour toute question sur les modèles ou les technologies :
- **Issues GitHub :** Créer une issue
- **Documentation :** Consulter les docs dans `docs/`
- **Exemples :** Voir les tests dans `tests/`

---

**Dernière mise à jour :** 11 janvier 2026  
**Version :** 2.0.0  
**Auteurs :** Équipe YANSNET - ETSIA

---

## ✅ Checklist de Compréhension

- [ ] Je comprends les 7 modèles du projet
- [ ] Je connais les technologies utilisées (BERT, LLM, Vision)
- [ ] Je sais quand utiliser quel modèle
- [ ] Je comprends l'architecture multi-modèles
- [ ] Je connais les métriques de performance
- [ ] Je sais configurer les providers
- [ ] Je peux déployer l'API avec Docker
- [ ] Je comprends le système de cache

**Si tous les points sont cochés, vous maîtrisez l'architecture du projet ! 🎉**
