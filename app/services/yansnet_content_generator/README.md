# 📝 Générateur de Contenu YANSNET

Service de génération de posts et commentaires pour peupler l'interface utilisateur du réseau social YANSNET.

## 🎯 Objectif

Ce service génère du contenu réaliste pour :
- **Démos** : Montrer l'interface avec du contenu crédible
- **Tests** : Tester les fonctionnalités du réseau social
- **Prototypage** : Développer l'UI sans attendre de vrais utilisateurs

**Note importante** : Ce contenu est généré par IA et ne doit PAS être utilisé pour entraîner des modèles de détection de dépression (risque de biais circulaire).

---

## 🏗️ Architecture

Le générateur **réutilise le LLM existant** de l'API (configuré dans `.env`) :
- **GPT-4o-mini** (OpenAI)
- **Claude 3.5 Sonnet** (Anthropic)
- **Llama 3.2** (Ollama local)

Aucune dépendance supplémentaire requise !

---

## 📡 Endpoints API

### 1. Générer un post

```bash
POST /api/v1/content/generate-post
```

**Body (optionnel) :**
```json
{
  "post_type": "demande d'aide",
  "topic": "les partiels stressants",
  "sentiment": "négatif"
}
```

**Réponse :**
```json
{
  "content": "Bonjour à tous, je suis vraiment stressé par les partiels qui arrivent...",
  "post_type": "demande d'aide",
  "topic": "les partiels stressants",
  "sentiment": "négatif",
  "timestamp": "2025-01-16T10:30:00Z"
}
```

**Types de posts disponibles :**
- `confession`
- `coup de gueule`
- `demande d'aide`
- `message de soutien`
- `blague`
- `information utile`

---

### 2. Générer des commentaires

```bash
POST /api/v1/content/generate-comments
```

**Body :**
```json
{
  "post_content": "Je suis vraiment stressé par les partiels qui arrivent...",
  "sentiment": "positif",
  "num_comments": 3
}
```

**Réponse :**
```json
{
  "comments": [
    {
      "content": "Courage ! On est tous dans le même bateau.",
      "sentiment": "positif",
      "comment_number": 1
    },
    {
      "content": "Tu devrais essayer de réviser en groupe, ça aide beaucoup !",
      "sentiment": "positif",
      "comment_number": 2
    }
  ],
  "total_comments": 2,
  "timestamp": "2025-01-16T10:30:00Z"
}
```

---

### 3. Générer un post complet avec commentaires

```bash
POST /api/v1/content/generate-post-with-comments
```

**Body (optionnel) :**
```json
{
  "post_type": "blague",
  "topic": "les fêtes étudiantes",
  "num_comments": 10
}
```

**Réponse :**
```json
{
  "post": {
    "content": "Vous savez ce qui est drôle ? Les fêtes étudiantes...",
    "post_type": "blague",
    "topic": "les fêtes étudiantes",
    "sentiment": "positif",
    "timestamp": "2025-01-16T10:30:00Z"
  },
  "comments": [
    {
      "content": "Haha trop vrai !",
      "sentiment": "positif",
      "comment_number": 1
    }
  ],
  "total_comments": 10,
  "timestamp": "2025-01-16T10:30:00Z"
}
```

---

## 🚀 Utilisation

### Via l'API

```bash
# Générer un post aléatoire
curl -X POST http://localhost:8000/api/v1/content/generate-post \
  -H "Content-Type: application/json" \
  -d '{}'

# Générer un post spécifique
curl -X POST http://localhost:8000/api/v1/content/generate-post \
  -H "Content-Type: application/json" \
  -d '{
    "post_type": "demande d'\''aide",
    "topic": "les partiels stressants"
  }'

# Générer un post complet avec commentaires
curl -X POST http://localhost:8000/api/v1/content/generate-post-with-comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_type": "blague",
    "num_comments": 5
  }'
```

### Via Python

```python
import requests

# Générer un post
response = requests.post(
    "http://localhost:8000/api/v1/content/generate-post",
    json={
        "post_type": "confession",
        "topic": "la vie en résidence universitaire"
    }
)
post = response.json()
print(post["content"])

# Générer des commentaires
response = requests.post(
    "http://localhost:8000/api/v1/content/generate-comments",
    json={
        "post_content": post["content"],
        "num_comments": 5
    }
)
comments = response.json()
for comment in comments["comments"]:
    print(f"- {comment['content']}")
```

---

## 🎨 Sujets Disponibles

Le générateur peut créer du contenu sur 20+ sujets :
- Les partiels stressants
- La vie en résidence universitaire
- Le stage de fin d'études
- Les associations étudiantes
- Le planning des cours
- Les notes et résultats
- Les échanges internationaux
- Le covoiturage pour l'école
- La cantine de l'école
- Les problèmes de logement
- Le stress avant les examens
- Les fêtes étudiantes
- Les relations étudiants-professeurs
- La recherche de mentors
- Les concours de programmation
- Le hackathon de l'école
- Les voyages d'études
- Les bourses et financements
- Le nouveau bâtiment sportif
- Les salles d'étude bondées

---

## ⚙️ Configuration

Le générateur utilise le LLM configuré dans `.env` :

```env
# LLM Provider (gpt, claude, local)
LLM_PROVIDER=gpt

# OpenAI (si provider=gpt)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Anthropic (si provider=claude)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Ollama (si provider=local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

---

## 🔍 Différences avec `comm/posts.py`

| Aspect | `comm/posts.py` (ancien) | Ce service (nouveau) |
|--------|--------------------------|----------------------|
| **Intégration** | Script standalone | Service intégré à l'API |
| **LLM** | Ollama uniquement | Supporte GPT, Claude, Ollama |
| **Configuration** | Hardcodé | Utilise `.env` de l'app |
| **Génération** | Batch (30 posts) | À la demande (API) |
| **Gestion erreurs** | Retries basiques | Gestion robuste |
| **Sentiments** | Forcés aléatoirement | Naturels ou spécifiés |
| **Usage** | Génération offline | Génération en temps réel |

---

## 📊 Performance

| Provider | Vitesse | Coût | Qualité |
|----------|---------|------|---------|
| **GPT-4o-mini** | ~2s/post | ~$0.0001 | ⭐⭐⭐⭐⭐ |
| **Claude** | ~2s/post | ~$0.0003 | ⭐⭐⭐⭐⭐ |
| **Llama local** | ~3s/post | Gratuit | ⭐⭐⭐⭐ |

---

## ⚠️ Avertissements

1. **Ne PAS utiliser pour l'entraînement** : Le contenu généré par IA ne doit pas servir à entraîner des modèles de détection (biais circulaire)

2. **Usage démo uniquement** : Ce contenu est pour peupler l'interface, pas pour simuler de vraies interactions

3. **Vérifier la qualité** : Toujours vérifier que le contenu généré est approprié avant de l'afficher

---

## 🧪 Tests

```bash
# Health check du générateur
curl http://localhost:8000/api/v1/models/yansnet-content-generator/health

# Tester la génération
python -c "
import requests
r = requests.post('http://localhost:8000/api/v1/content/generate-post', json={})
print(r.json()['content'])
"
```

---

## 📝 Auteur

Équipe YANSNET - ETSIA X5 Semestre 9

---

## 🔗 Liens Utiles

- [Documentation API complète](http://localhost:8000/docs)
- [Guide d'ajout de modèles](../../../docs/ADD_YOUR_MODEL.md)
- [Configuration LLM](../../../docs/SETUP_LLM.md)
