# 🧪 Guide de Test via Interface Swagger

## 🌐 Accès à l'Interface

Ouvrez votre navigateur : **http://localhost:8001/docs**

---

## 📋 Tests des 7 Modèles

### 1️⃣ Health Check Global

**Endpoint**: `GET /health`

1. Cliquez sur `GET /health`
2. Cliquez sur "Try it out"
3. Cliquez sur "Execute"

**Résultat attendu**:
```json
{
  "status": "healthy",
  "models": {
    "total": 7,
    "available": [
      "yansnet-llm",
      "qwen-depression",
      "sensitive-image-caption",
      "yansnet-content-generator",
      "hatecomment-bert",
      "recommendation-system",
      "nsfw-detection"
    ]
  }
}
```

---

### 2️⃣ Détection de Dépression (Qwen 2.5)

**Endpoint**: `POST /api/v1/depression/detect`

1. Cliquez sur `POST /api/v1/depression/detect`
2. Cliquez sur "Try it out"
3. Entrez le JSON suivant :

```json
{
  "text": "Je me sens vraiment triste et sans espoir depuis plusieurs semaines"
}
```

4. Cliquez sur "Execute"

**Résultat attendu**:
```json
{
  "prediction": "DÉPRESSION",
  "confidence": 0.85,
  "severity": "Élevée",
  "processing_time": 3.5,
  "model_used": "qwen2.5:1.5b"
}
```

**Test alternatif** (texte normal):
```json
{
  "text": "Je suis très heureux aujourd'hui, tout va bien dans ma vie!"
}
```

---

### 3️⃣ Détection Hate Speech (BERT)

**Endpoint**: `POST /api/v1/hatecomment/detect`

1. Cliquez sur `POST /api/v1/hatecomment/detect`
2. Cliquez sur "Try it out"
3. Entrez le JSON suivant :

```json
{
  "text": "Tu es vraiment stupide et inutile, personne ne t'aime"
}
```

4. Cliquez sur "Execute"

**Résultat attendu**:
```json
{
  "prediction": "HAINEUX",
  "confidence": 0.92,
  "severity": "Critique",
  "processing_time": 0.05,
  "enhanced": true
}
```

**Test alternatif** (texte positif):
```json
{
  "text": "Merci beaucoup pour ton aide, c'est vraiment gentil de ta part!"
}
```

---

### 4️⃣ Génération de Contenu

**Endpoint**: `POST /api/v1/predict`

1. Cliquez sur `POST /api/v1/predict`
2. Cliquez sur "Try it out"
3. Entrez le JSON suivant :

```json
{
  "text": "Écris un court message motivant pour quelqu'un qui se sent triste",
  "model_name": "yansnet-content-generator"
}
```

4. Cliquez sur "Execute"

**Résultat attendu**:
```json
{
  "prediction": "Je comprends que tu traverses une période difficile...",
  "confidence": 0.95,
  "processing_time": 2.5
}
```

---

### 5️⃣ Caption d'Images Sensibles

**Endpoint**: `POST /api/v1/predict-image`

1. Cliquez sur `POST /api/v1/predict-image`
2. Cliquez sur "Try it out"
3. Pour tester, vous avez besoin d'une image en base64

**Option simple** : Utilisez cette image de test (1x1 pixel blanc) :
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
  "model_name": "sensitive-image-caption"
}
```

4. Cliquez sur "Execute"

**Résultat attendu**:
```json
{
  "prediction": "une image simple avec un fond blanc",
  "is_sensitive": false,
  "processing_time": 1.2
}
```

---

### 6️⃣ Système de Recommandation

**Endpoint**: `POST /api/v1/recommendation/recommend`

1. Cliquez sur `POST /api/v1/recommendation/recommend`
2. Cliquez sur "Try it out"
3. Entrez le JSON suivant :

```json
{
  "user_id": 1,
  "top_n": 5
}
```

4. Cliquez sur "Execute"

**Résultat attendu**:
```json
{
  "recommendations": [
    {"post_id": 123, "score": 0.95},
    {"post_id": 456, "score": 0.87},
    {"post_id": 789, "score": 0.82},
    {"post_id": 234, "score": 0.78},
    {"post_id": 567, "score": 0.75}
  ],
  "from_cache": false,
  "processing_time": 0.15
}
```

---

### 7️⃣ Détection NSFW (ShieldGemma2)

**Endpoint**: `POST /api/v1/censure/detect`

1. Cliquez sur `POST /api/v1/censure/detect`
2. Cliquez sur "Try it out"
3. Utilisez la même image de test en base64 :

```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
}
```

4. Cliquez sur "Execute"

**Résultat attendu**:
```json
{
  "prediction": "SAFE",
  "confidence": 0.95,
  "severity": "Aucune",
  "is_nsfw": false,
  "reasoning": "✅ Contenu sûr - Aucun élément NSFW détecté",
  "categories": {
    "Sexually Explicit": {
      "Safe": 98.5,
      "Violation": 1.5,
      "Prediction": "Safe"
    },
    "Violence & Gore": {
      "Safe": 99.2,
      "Violation": 0.8,
      "Prediction": "Safe"
    }
  }
}
```

---

## 🔍 Vérification du Monitoring

### Test GA4-Bridge

**URL**: http://localhost:5000/health

```bash
curl http://localhost:5000/health
```

**Résultat attendu**:
```json
{
  "status": "healthy",
  "catalog_rules": 40
}
```

### Vérifier les Métriques Émises

Après avoir testé un modèle, vérifiez les logs du bridge :

```bash
docker logs etsia_ml_api-ga4-bridge-1 --tail 20
```

Vous devriez voir :
```
✓ Métrique reçue: depression_detection/detect_depression
⚠️ ALERTE: Latence > 1000ms (si applicable)
→ Forwarded to GA4
```

---

## 📊 Tests de Performance

### Test de Latence

Testez plusieurs fois le même endpoint et comparez les temps :

1. **Premier appel** : ~3-5s (chargement du modèle)
2. **Appels suivants** : ~0.5-2s (modèle en cache)

### Test de Cache (Recommandations)

1. Appelez `/api/v1/recommendation/recommend` avec `user_id: 1`
2. Notez `"from_cache": false`
3. Appelez à nouveau immédiatement
4. Notez `"from_cache": true` et temps réduit

---

## ⚠️ Résolution de Problèmes

### Erreur 503 Service Unavailable
- Le conteneur est en train de démarrer
- Attendez 2-3 minutes (chargement des modèles)
- Vérifiez : `docker logs etsia-ml-api-cpu`

### Erreur 500 Internal Server Error
- Vérifiez les logs : `docker logs etsia-ml-api-cpu --tail 50`
- Vérifiez que tous les services sont up : `docker ps`

### Modèle "unhealthy"
- Vérifiez le health check : `curl http://localhost:8001/health`
- Redémarrez le conteneur : `docker-compose --profile ml restart api`

---

## 🎯 Checklist de Test Complet

- [ ] Health check global (7 modèles disponibles)
- [ ] Détection de dépression (texte triste + texte joyeux)
- [ ] Détection hate speech (texte haineux + texte positif)
- [ ] Génération de contenu (prompt créatif)
- [ ] Caption d'images (image de test)
- [ ] Recommandations (user_id 1, vérifier cache)
- [ ] Détection NSFW (image safe)
- [ ] Vérifier monitoring GA4-Bridge
- [ ] Vérifier logs pour alertes
- [ ] Tester performance (latence)

---

## 🚀 Prêt pour Production

Une fois tous les tests passés :

✅ Tous les modèles répondent correctement  
✅ Les temps de réponse sont acceptables  
✅ Le monitoring émet des métriques  
✅ Le cache fonctionne  
✅ Les alertes se déclenchent correctement  

**Le système est prêt pour le déploiement ! 🎉**
