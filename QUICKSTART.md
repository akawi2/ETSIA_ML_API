# ⚡ Démarrage Ultra-Rapide

## 🚀 En 3 Minutes

### 1. Installation (1 min)
```bash
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec votre clé API (OpenAI, Claude, ou Ollama)
```

### 2. Lancer l'API (30 sec)
```bash
uvicorn app.main:app --reload
```

### 3. Tester (1 min)
```bash
# Test automatique des 6 modèles
python test_all_models.py

# Ou test manuel
curl http://localhost:8000/health
```

---

## 📋 Les 6 Modèles en 1 Ligne

```bash
# 1. Détection dépression (NOUVELLE ROUTE)
curl -X POST http://localhost:8000/api/v1/depression/detect -H "Content-Type: application/json" -d '{"text":"Je suis triste","include_reasoning":true}'

# 2. Détection hate speech
curl -X POST http://localhost:8000/api/v1/hatecomment/detect -H "Content-Type: application/json" -d '{"text":"Je déteste"}'

# 3. Détection NSFW
curl -X POST http://localhost:8000/api/v1/censure/detect -F "file=@image.jpg"

# 4. Analyse image
curl -X POST http://localhost:8000/api/v1/predict-image -F "image=@image.jpg"

# 5. Recommandation
curl http://localhost:8000/recommend?userId=1

# 6. Génération contenu
curl -X POST http://localhost:8000/api/v1/content/generate-post -H "Content-Type: application/json" -d '{}'
```

---

## 🔧 Configuration Minimale

### Option 1: OpenAI (Recommandé)
```env
LLM_PROVIDER=gpt
OPENAI_API_KEY=sk-votre-cle
OPENAI_MODEL=gpt-4o-mini
```

### Option 2: Ollama (Gratuit)
```bash
# Installer Ollama
ollama pull llama3.2
ollama serve

# Dans .env
LLM_PROVIDER=local
OLLAMA_MODEL=llama3.2
```

---

## 📚 Documentation

- **Tests détaillés:** [TEST_ENDPOINTS.md](TEST_ENDPOINTS.md)
- **Résumé endpoints:** [ENDPOINTS_SUMMARY.md](ENDPOINTS_SUMMARY.md)
- **Documentation complète:** [README.md](README.md)
- **Swagger UI:** http://localhost:8000/docs

---

## ✅ Checklist

- [ ] `pip install -r requirements.txt`
- [ ] `.env` configuré avec clé API
- [ ] `uvicorn app.main:app --reload`
- [ ] `python test_all_models.py` → Tous les tests passent
- [ ] http://localhost:8000/docs accessible

---

## 🆘 Problèmes Courants

### "Modèle non enregistré"
```bash
# Vérifier .env
cat .env | grep LLM
```

### "Connection refused"
```bash
# Vérifier que l'API tourne
curl http://localhost:8000/health
```

### "Out of Memory" (images)
```bash
# Forcer CPU
export CUDA_VISIBLE_DEVICES=""
```

---

**Temps total:** ~3 minutes ⏱️
