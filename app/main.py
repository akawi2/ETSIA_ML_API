"""
Point d'entrée de l'application FastAPI - Architecture Multi-Modèles
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes import router, hatecomment_router, image_router, content_router, recommendation_router, censure_router
from app.routes.depression_api import router as depression_router
from app.routes.metrics_api import router as metrics_router
from app.models.schemas import HealthResponse
from app.core.model_registry import registry
from app.services.recommendation.recommendation_service import recommend_service
from app.utils.logger import setup_logger
from datetime import datetime

logger = setup_logger(__name__)

# Créer l'application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION + " - Architecture Multi-Modèles",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(router)
app.include_router(hatecomment_router)
app.include_router(image_router)
app.include_router(content_router)
app.include_router(recommendation_router)
app.include_router(censure_router)
app.include_router(depression_router)
app.include_router(metrics_router)



@app.on_event("startup")
async def startup_event():
    """Événement au démarrage - Enregistrement des modèles"""
    logger.info("="*70)
    logger.info(f"{settings.API_TITLE} v{settings.API_VERSION}")
    logger.info("Architecture Multi-Modèles")
    logger.info("="*70)
    
    # Connexion à la base de données PostgreSQL pour les métriques
    if settings.ENABLE_METRICS:
        try:
            from app.core.metrics.database import db
            await db.connect()
            logger.info("✓ Connexion PostgreSQL établie (métriques)")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de se connecter à PostgreSQL: {e}")
            logger.warning("  Les métriques seront désactivées")
    
    # Enregistrer les modèles disponibles
    logger.info("\n📦 Enregistrement des modèles...")
    logger.info("-"*70)
    
    # 1. Modèle YANSNET LLM
    try:
        from app.services.yansnet_llm import YansnetLLMModel
        registry.register(YansnetLLMModel(), set_as_default=True)
    except Exception as e:
        logger.error(f"✗ Erreur lors de l'enregistrement du modèle YANSNET LLM: {e}")
        logger.error(f"  Vérifiez que .env est configuré avec les clés API")
    
    # 2. Modèle de détection de dépression selon la configuration
    detection_provider = settings.DETECTION_PROVIDER.lower()
    logger.info(f"📊 Provider de détection configuré: {detection_provider}")
    
    if detection_provider == "qwen":
        # Utiliser Qwen 2.5 1.5B via Ollama
        try:
            from app.services.qwen_depression import QwenDepressionModel
            qwen_model = QwenDepressionModel()
            registry.register_detection_model(qwen_model, priority=10)
            logger.info("✓ Modèle Qwen 2.5 1.5B de détection de dépression enregistré (primaire)")
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'enregistrement du modèle Qwen: {e}")
            logger.error(f"  Vérifiez que Ollama est démarré et que qwen2.5:1.5b est téléchargé")
            # Fallback to CamemBERT
            logger.info("  Tentative de fallback vers CamemBERT...")
            try:
                from app.services.camembert_depression import CamemBERTDepressionModel
                camembert_model = CamemBERTDepressionModel()
                registry.register_detection_model(camembert_model, priority=10)
                logger.info("✓ Fallback: Modèle CamemBERT enregistré comme primaire")
            except Exception as e2:
                logger.error(f"✗ Fallback CamemBERT également échoué: {e2}")
    
    elif detection_provider == "camembert":
        # Utiliser CamemBERT (défaut)
        try:
            from app.services.camembert_depression import CamemBERTDepressionModel
            camembert_model = CamemBERTDepressionModel()
            registry.register_detection_model(camembert_model, priority=10)
            logger.info("✓ Modèle CamemBERT de détection de dépression enregistré (primaire)")
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'enregistrement du modèle CamemBERT: {e}")
            logger.error(f"  Vérifiez que les dépendances sont installées (transformers, torch)")
    
    elif detection_provider == "xlm-roberta":
        # Utiliser XLM-RoBERTa (multilingue)
        logger.warning("⚠️ XLM-RoBERTa non encore implémenté, utilisation de CamemBERT")
        try:
            from app.services.camembert_depression import CamemBERTDepressionModel
            camembert_model = CamemBERTDepressionModel()
            registry.register_detection_model(camembert_model, priority=10)
            logger.info("✓ Modèle CamemBERT de détection de dépression enregistré (primaire)")
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'enregistrement du modèle CamemBERT: {e}")
    
    else:
        logger.warning(f"⚠️ Provider de détection inconnu: {detection_provider}")
        logger.info("  Tentative d'enregistrement de CamemBERT par défaut...")
        try:
            from app.services.camembert_depression import CamemBERTDepressionModel
            camembert_model = CamemBERTDepressionModel()
            registry.register_detection_model(camembert_model, priority=10)
            logger.info("✓ Modèle CamemBERT de détection de dépression enregistré (primaire)")
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'enregistrement du modèle CamemBERT: {e}")
    
    # 3. Modèle de Détection de Contenu Sensible dans les Images
    try:
        from app.services.sensitive_image_caption import SensitiveImageCaptionModel
        registry.register(SensitiveImageCaptionModel())
        logger.info("✓ Modèle de détection de contenu sensible (images) enregistré")
    except Exception as e:
        logger.error(f"✗ Erreur lors de l'enregistrement du modèle d'images: {e}")
        logger.error(f"  Vérifiez que les dépendances sont installées (transformers, torch, PIL)")

    # 4. Générateur de Contenu YANSNET
    try:
        from app.services.yansnet_content_generator import YansnetContentGeneratorModel
        registry.register(YansnetContentGeneratorModel())
        logger.info("✓ Générateur de contenu YANSNET enregistré")
    except Exception as e:
        logger.error(f"✗ Erreur lors de l'enregistrement du générateur: {e}")
        logger.error(f"  Vérifiez que le LLM est configuré dans .env")

    # 5. Modèle HateComment BERT
    try:
        from app.services.hatecomment_bert import HateCommentBertModel
        registry.register(HateCommentBertModel())
        logger.info("✓ Modèle HateComment BERT enregistré")
    except Exception as e:
        logger.error(f"✗ Erreur lors de l'enregistrement du modèle HateComment BERT: {e}")
    
    # 6. Système de Recommandation
    try:
        from app.services.recommendation import RecommendationModel
        registry.register(RecommendationModel())
        logger.info("✓ Système de recommandation enregistré")
    except Exception as e:
        logger.error(f"✗ Erreur lors de l'enregistrement du système de recommandation: {e}")
    
    # 7. Modèle de Détection NSFW
    try:
        from app.services.model_censure import CensureModel
        registry.register(CensureModel())
        logger.info("✓ Modèle de détection NSFW enregistré")
    except Exception as e:
        logger.error(f"✗ Erreur lors de l'enregistrement du modèle NSFW: {e}")
    
    # 8. Autres modèles à ajouter ici
    # Exemple pour un futur étudiant:
    # try:
    #     from app.services.etudiant2_gcn import Etudiant2GCNModel
    #     registry.register(Etudiant2GCNModel())
    # except Exception as e:
    #     logger.error(f"✗ Erreur: {e}")
    
    # Résumé
    logger.info("-"*70)
    models = registry.list_models()
    if models:
        logger.info(f"✓ {len(models)} modèle(s) enregistré(s):")
        for name, info in models.items():
            default_marker = " [DÉFAUT]" if info.get('is_default') else ""
            logger.info(f"  • {name} v{info['version']} by {info['author']}{default_marker}")
    else:
        logger.warning("⚠️  Aucun modèle enregistré!")
    
    logger.info("="*70)
    logger.info("✓ API démarrée avec succès!")
    logger.info("📚 Documentation: http://localhost:8000/docs")
    logger.info("📋 Modèles disponibles: http://localhost:8000/api/v1/models")
    logger.info("="*70)



@app.on_event("shutdown")
async def shutdown_event():
    """Événement à l'arrêt"""
    logger.info("Arrêt de l'API...")
    
    # Fermer la connexion PostgreSQL
    if settings.ENABLE_METRICS:
        try:
            from app.core.metrics.database import db
            await db.disconnect()
            logger.info("✓ Connexion PostgreSQL fermée")
        except Exception as e:
            logger.error(f"Erreur fermeture PostgreSQL: {e}")


@app.get(
    "/",
    response_model=dict,
    summary="Page d'accueil",
    description="Informations sur l'API"
)
async def root():
    """Page d'accueil"""
    return {
        "message": "ETSIA ML API - Architecture Multi-Modèles",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=dict,
    summary="Health check",
    description="Vérifie l'état de l'API et des modèles"
)
async def health():
    """Health check global"""
    models_health = await registry.health_check_all()
    models_list = registry.list_models()
    
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "models": {
            "total": len(models_list),
            "available": list(models_list.keys()),
            "health": models_health
        }
    }


@app.get(
    "/recommend",
    response_model=dict,
    summary="Recommendation",
    description="Propose une recommendation de posts"
)
async def recommend(userId: int = Query(...)):
    recommendations = recommend_service(userId)
    
    return {
        "user_id": userId,
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "recommendations": recommendations, 
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global pour les exceptions"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
