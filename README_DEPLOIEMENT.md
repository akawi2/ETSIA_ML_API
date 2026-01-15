# 🚀 ETSIA ML API - Déploiement Local Réussi

## ✅ Statut: OPÉRATIONNEL

Tous les services sont démarrés et fonctionnels !

## 🎯 Accès Rapide

| Service | URL | Description |
|---------|-----|-------------|
| **API ML** | http://localhost:8001 | API principale |
| **Documentation** | http://localhost:8001/docs | Swagger UI interactive |
| **Health Check** | http://localhost:8001/health | Statut des modèles |
| **GA4-Bridge** | http://localhost:5000 | Monitoring |

## 🤖 Modèles Disponibles (7)

1. **yansnet-llm** - LLM principal
2. **qwen-depression** - Détection dépression (Qwen 2.5 1.5B)
3. **sensitive-image-caption** - Analyse d'images
4. **yansnet-content-generator** - Génération de contenu
5. **hatecomment-bert** - Détection hate speech
6. **recommendation-system** - Recommandations
7. **nsfw-detection** - Détection contenu NSFW

## 🧪 Test Rapide

```powershell
# Test de génération de contenu
$body = @{
    post_type = "blague"
    topic = "les examens"
    sentiment = "positif"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/content/generate-post" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## 📝 Commandes Essentielles

```powershell
# Voir les logs
docker-compose logs -f api

# Redémarrer
docker-compose restart api

# Arrêter
docker-compose --profile ml down

# Tests complets
.\test_api.ps1

# Status
docker-compose ps
```

## 📚 Documentation

- **Guide complet**: `DEPLOIEMENT_REUSSI.md`
- **Quickstart**: `QUICKSTART_WINDOWS.md`
- **Guide développeur**: `docs/GUIDE_DEVELOPPEUR.md`

## 🎉 Prochaines Étapes

1. Testez l'API: http://localhost:8001/docs
2. Lancez les tests: `.\test_api.ps1`
3. Intégrez dans votre application
4. Configurez les clés API externes (optionnel)

**Bon développement ! 🚀**
