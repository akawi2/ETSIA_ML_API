# ✍️ Guide de Génération de Contenu YANSNET

Guide complet pour utiliser le générateur de contenu du réseau social YANSNET.

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Démarrage rapide](#démarrage-rapide)
3. [Endpoints API](#endpoints-api)
4. [Exemples d'utilisation](#exemples-dutilisation)
5. [Intégration Frontend](#intégration-frontend)
6. [Bonnes pratiques](#bonnes-pratiques)

---

## Vue d'ensemble

Le générateur de contenu YANSNET permet de créer du contenu réaliste pour peupler l'interface du réseau social :

- **Posts** : Confessions, demandes d'aide, blagues, etc.
- **Commentaires** : Réponses naturelles aux posts
- **Posts complets** : Post + commentaires en une seule requête

### Cas d'usage

✅ **Démos** : Montrer l'interface avec du contenu crédible  
✅ **Tests** : Tester les fonctionnalités sans vrais utilisateurs  
✅ **Prototypage** : Développer l'UI rapidement  
❌ **Entraînement ML** : Ne PAS utiliser pour entraîner des modèles

---

## Démarrage rapide

### 1. Vérifier que l'API est lancée

```bash
# Lancer l'API
uvicorn app.main:app --reload

# Vérifier le health check
curl http://localhost:8000/health
```

### 2. Tester le générateur

```bash
# Générer un post aléatoire
curl -X POST http://localhost:8000/api/v1/content/generate-post \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 3. Voir la documentation interactive

Ouvrir http://localhost:8000/docs et chercher la section "Génération de Contenu"

---

## Endpoints API

### 1. POST `/api/v1/content/generate-post`

Génère un post pour le forum étudiant.

**Paramètres (tous optionnels) :**

```json
{
  "post_type": "demande d'aide",  // Type de post
  "topic": "les partiels stressants",  // Sujet
  "sentiment": "négatif"  // Sentiment
}
```

**Types de posts disponibles :**
- `confession`
- `coup de gueule`
- `demande d'aide`
- `message de soutien`
- `blague`
- `information utile`

**Sentiments disponibles :**
- `positif`
- `neutre`
- `négatif`

**Réponse :**

```json
{
  "content": "Bonjour à tous, je suis vraiment stressé...",
  "post_type": "demande d'aide",
  "topic": "les partiels stressants",
  "sentiment": "négatif",
  "timestamp": "2025-01-16T10:30:00Z"
}
```

---

### 2. POST `/api/v1/content/generate-comments`

Génère des commentaires pour un post donné.

**Paramètres :**

```json
{
  "post_content": "Je suis vraiment stressé...",  // Requis
  "sentiment": "positif",  // Optionnel
  "num_comments": 5  // 1-20, défaut: 5
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
    }
  ],
  "total_comments": 5,
  "timestamp": "2025-01-16T10:30:00Z"
}
```

---

### 3. POST `/api/v1/content/generate-post-with-comments`

Génère un post complet avec ses commentaires.

**Paramètres (tous optionnels) :**

```json
{
  "post_type": "blague",
  "topic": "les fêtes étudiantes",
  "num_comments": 10  // 1-20, défaut: 8-12 aléatoire
}
```

**Réponse :**

```json
{
  "post": {
    "content": "Vous savez ce qui est drôle ?...",
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

## Exemples d'utilisation

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Générer un post aléatoire
response = requests.post(f"{BASE_URL}/api/v1/content/generate-post")
post = response.json()
print(f"Post: {post['content']}")

# 2. Générer un post spécifique
response = requests.post(
    f"{BASE_URL}/api/v1/content/generate-post",
    json={
        "post_type": "demande d'aide",
        "topic": "les partiels stressants"
    }
)
post = response.json()

# 3. Générer des commentaires
response = requests.post(
    f"{BASE_URL}/api/v1/content/generate-comments",
    json={
        "post_content": post["content"],
        "num_comments": 5
    }
)
comments = response.json()

# 4. Générer un post complet
response = requests.post(
    f"{BASE_URL}/api/v1/content/generate-post-with-comments",
    json={
        "post_type": "blague",
        "num_comments": 10
    }
)
full_post = response.json()
```

### JavaScript / TypeScript

```typescript
const BASE_URL = "http://localhost:8000";

// Générer un post
async function generatePost() {
  const response = await fetch(`${BASE_URL}/api/v1/content/generate-post`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      post_type: "demande d'aide",
      topic: "les partiels stressants"
    })
  });
  
  const post = await response.json();
  console.log(post.content);
  return post;
}

// Générer des commentaires
async function generateComments(postContent: string) {
  const response = await fetch(`${BASE_URL}/api/v1/content/generate-comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      post_content: postContent,
      num_comments: 5
    })
  });
  
  const data = await response.json();
  return data.comments;
}

// Générer un post complet
async function generateFullPost() {
  const response = await fetch(
    `${BASE_URL}/api/v1/content/generate-post-with-comments`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        post_type: "blague",
        num_comments: 10
      })
    }
  );
  
  return await response.json();
}
```

### cURL

```bash
# Post aléatoire
curl -X POST http://localhost:8000/api/v1/content/generate-post \
  -H "Content-Type: application/json" \
  -d '{}'

# Post spécifique
curl -X POST http://localhost:8000/api/v1/content/generate-post \
  -H "Content-Type: application/json" \
  -d '{
    "post_type": "confession",
    "topic": "la vie en résidence universitaire"
  }'

# Commentaires
curl -X POST http://localhost:8000/api/v1/content/generate-comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_content": "Je suis stressé par les partiels...",
    "num_comments": 3
  }'

# Post complet
curl -X POST http://localhost:8000/api/v1/content/generate-post-with-comments \
  -H "Content-Type: application/json" \
  -d '{
    "post_type": "blague",
    "num_comments": 5
  }'
```

---

## Intégration Frontend

### React Example

```tsx
import { useState } from 'react';

interface Post {
  content: string;
  post_type: string;
  topic: string;
  sentiment: string;
}

interface Comment {
  content: string;
  sentiment: string;
  comment_number: number;
}

function PostGenerator() {
  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(false);

  const generateFullPost = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        'http://localhost:8000/api/v1/content/generate-post-with-comments',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            post_type: 'demande d\'aide',
            num_comments: 5
          })
        }
      );
      
      const data = await response.json();
      setPost(data.post);
      setComments(data.comments);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={generateFullPost} disabled={loading}>
        {loading ? 'Génération...' : 'Générer un post'}
      </button>
      
      {post && (
        <div className="post">
          <h3>{post.post_type} - {post.topic}</h3>
          <p>{post.content}</p>
          
          <div className="comments">
            <h4>{comments.length} commentaires</h4>
            {comments.map(comment => (
              <div key={comment.comment_number} className="comment">
                <span className={`sentiment-${comment.sentiment}`}>
                  {comment.sentiment}
                </span>
                <p>{comment.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Bonnes pratiques

### ✅ À faire

1. **Utiliser pour les démos** : Parfait pour montrer l'interface
2. **Tester l'UI** : Valider les fonctionnalités sans vrais utilisateurs
3. **Vérifier le contenu** : Toujours vérifier que le contenu est approprié
4. **Gérer les erreurs** : Le LLM peut échouer, prévoir un fallback
5. **Limiter les requêtes** : Ne pas spammer l'API (coûts LLM)

### ❌ À éviter

1. **Entraîner des modèles** : Biais circulaire (IA génère → IA détecte)
2. **Utiliser en production** : C'est pour les démos uniquement
3. **Ignorer les coûts** : GPT/Claude ont un coût par requête
4. **Générer en masse** : Préférer générer à la demande

### 💡 Astuces

1. **Cache les résultats** : Éviter de régénérer le même contenu
2. **Batch generation** : Générer plusieurs posts d'un coup si besoin
3. **Variété** : Laisser les paramètres aléatoires pour plus de diversité
4. **Local LLM** : Utiliser Ollama pour éviter les coûts

---

## Performance et Coûts

### Temps de génération

| Provider | Post seul | Post + 10 commentaires |
|----------|-----------|------------------------|
| GPT-4o-mini | ~2s | ~15s |
| Claude | ~2s | ~15s |
| Llama local | ~3s | ~25s |

### Coûts (GPT-4o-mini)

- **Post** : ~$0.0001 (~200 tokens)
- **Commentaire** : ~$0.00005 (~100 tokens)
- **Post + 10 commentaires** : ~$0.0006

**Estimation mensuelle** (100 posts/jour) :
- GPT-4o-mini : ~$1.80/mois
- Claude : ~$5.40/mois
- Llama local : Gratuit

---

## Dépannage

### Erreur : "Générateur de contenu non disponible"

**Cause** : Le générateur n'est pas enregistré dans l'API

**Solution** :
```bash
# Vérifier les modèles disponibles
curl http://localhost:8000/api/v1/models

# Relancer l'API
uvicorn app.main:app --reload
```

### Erreur : "LLM non accessible"

**Cause** : Configuration LLM incorrecte dans `.env`

**Solution** :
```bash
# Vérifier .env
cat .env | grep LLM

# Pour Ollama local
ollama serve
ollama pull llama3.2
```

### Contenu de mauvaise qualité

**Cause** : Modèle LLM pas adapté

**Solution** :
- Essayer un autre provider (GPT, Claude, Llama)
- Ajuster la température dans le code (actuellement 0.9)
- Fournir des paramètres plus précis (post_type, topic)

---

## Support

- **Documentation API** : http://localhost:8000/docs
- **README du service** : `app/services/yansnet_content_generator/README.md`
- **Tests** : `python test_content_generator.py`

---

**Dernière mise à jour** : Janvier 2025
