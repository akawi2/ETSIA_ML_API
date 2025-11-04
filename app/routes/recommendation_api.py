"""
Routes API pour le système de recommandation
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.model_registry import registry
from app.utils.logger import setup_logger
import time

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/recommendation", tags=["Recommendation System"])


# ============================================================================
# SCHÉMAS SPÉCIFIQUES RECOMMANDATION
# ============================================================================

class RecommendationRequest(BaseModel):
    """Requête pour obtenir des recommandations"""
    user_id: int = Field(
        ...,
        ge=1,
        description="ID de l'utilisateur",
        example=1
    )
    top_n: int = Field(
        10,
        ge=1,
        le=50,
        description="Nombre de recommandations à retourner (1-50)",
        example=10
    )
    available_posts: Optional[List[int]] = Field(
        None,
        description="Liste des posts disponibles (optionnel)",
        example=[1, 2, 3, 4, 5]
    )


class RecommendationItem(BaseModel):
    """Item de recommandation"""
    post_id: int = Field(..., description="ID du post recommandé")
    score: float = Field(..., ge=0.0, le=1.0, description="Score de recommandation")


class RecommendationResponse(BaseModel):
    """Réponse de recommandation"""
    user_id: int = Field(..., description="ID de l'utilisateur")
    recommendations: List[RecommendationItem] = Field(..., description="Liste des recommandations")
    total_recommendations: int = Field(..., description="Nombre total de recommandations")
    processing_time: Optional[float] = Field(None, description="Temps de traitement en secondes")


class BatchRecommendationRequest(BaseModel):
    """Requête batch pour recommandations"""
    user_ids: List[int] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="Liste d'IDs utilisateurs (max 50)",
        example=[1, 2, 3]
    )
    top_n: int = Field(
        10,
        ge=1,
        le=50,
        description="Nombre de recommandations par utilisateur",
        example=10
    )


class BatchRecommendationResult(BaseModel):
    """Résultat individuel de recommandation batch"""
    user_id: int = Field(..., description="ID de l'utilisateur")
    recommendations: List[RecommendationItem] = Field(..., description="Recommandations")
    total_recommendations: int = Field(..., description="Nombre de recommandations")


class BatchRecommendationResponse(BaseModel):
    """Réponse batch de recommandations"""
    results: List[BatchRecommendationResult] = Field(..., description="Résultats")
    total_users: int = Field(..., description="Nombre d'utilisateurs traités")
    processing_time: float = Field(..., description="Temps total de traitement")


class RecommendationHealthResponse(BaseModel):
    """Réponse health check Recommendation"""
    status: str = Field(..., description="healthy ou unhealthy")
    model: str = Field(..., description="Nom du modèle")
    version: str = Field(..., description="Version du modèle")
    recommender_available: bool = Field(..., description="Recommender disponible")


# ============================================================================
# ROUTES RECOMMANDATION
# ============================================================================

@router.get(
    "/health",
    response_model=RecommendationHealthResponse,
    summary="Health check Recommendation System",
    description="Vérifie l'état de santé du système de recommandation"
)
async def recommendation_health():
    """Health check spécifique pour le système de recommandation"""
    model = registry.get("recommendation-system")
    if not model:
        raise HTTPException(
            status_code=404,
            detail="Système de recommandation non trouvé"
        )
    
    health_data = model.health_check()
    return RecommendationHealthResponse(**health_data)


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Obtenir des recommandations",
    description="Génère des recommandations de posts pour un utilisateur"
)
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Génère des recommandations de posts pour un utilisateur.
    
    - **user_id**: ID de l'utilisateur
    - **top_n**: Nombre de recommandations (1-50)
    - **available_posts**: Liste optionnelle de posts disponibles
    
    Retourne:
    - **recommendations**: Liste des posts recommandés avec scores
    - **total_recommendations**: Nombre de recommandations
    """
    try:
        logger.info(f"Génération de recommandations pour user_id={request.user_id}")
        
        # Récupérer le modèle
        model = registry.get("recommendation-system")
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Système de recommandation non disponible"
            )
        
        # Mesurer le temps de traitement
        start_time = time.time()
        
        # Générer les recommandations
        result = model.predict(
            user_id=request.user_id,
            top_n=request.top_n,
            available_posts=request.available_posts
        )
        
        processing_time = time.time() - start_time
        
        logger.info(f"  → {result['total_recommendations']} recommandations générées")
        
        return RecommendationResponse(
            user_id=result['user_id'],
            recommendations=[
                RecommendationItem(**rec) for rec in result['recommendations']
            ],
            total_recommendations=result['total_recommendations'],
            processing_time=round(processing_time, 3)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération recommandations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de génération: {str(e)}"
        )


@router.post(
    "/batch-recommend",
    response_model=BatchRecommendationResponse,
    summary="Recommandations batch",
    description="Génère des recommandations pour plusieurs utilisateurs (max 50)"
)
async def batch_get_recommendations(request: BatchRecommendationRequest) -> BatchRecommendationResponse:
    """
    Génère des recommandations pour plusieurs utilisateurs en batch.
    
    - **user_ids**: Liste d'IDs utilisateurs (1-50)
    - **top_n**: Nombre de recommandations par utilisateur
    
    Retourne:
    - **results**: Liste des recommandations par utilisateur
    - **total_users**: Nombre d'utilisateurs traités
    """
    try:
        logger.info(f"Génération batch de recommandations ({len(request.user_ids)} utilisateurs)")
        
        # Récupérer le modèle
        model = registry.get("recommendation-system")
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Système de recommandation non disponible"
            )
        
        # Traitement batch
        start_time = time.time()
        results = model.batch_predict(
            user_ids=request.user_ids,
            top_n=request.top_n
        )
        processing_time = time.time() - start_time
        
        # Formater les résultats
        formatted_results = []
        for result in results:
            formatted_results.append(BatchRecommendationResult(
                user_id=result['user_id'],
                recommendations=[
                    RecommendationItem(**rec) for rec in result['recommendations']
                ],
                total_recommendations=result['total_recommendations']
            ))
        
        logger.info(f"  → Traité {len(formatted_results)} utilisateurs en {processing_time:.2f}s")
        
        return BatchRecommendationResponse(
            results=formatted_results,
            total_users=len(formatted_results),
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch recommandations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de génération batch: {str(e)}"
        )


@router.get(
    "/info",
    summary="Informations système de recommandation",
    description="Retourne les informations détaillées sur le système de recommandation"
)
async def recommendation_info():
    """Informations détaillées sur le système de recommandation"""
    model = registry.get("recommendation-system")
    if not model:
        raise HTTPException(
            status_code=404,
            detail="Système de recommandation non trouvé"
        )
    
    info = model.get_info()
    
    # Ajouter des informations spécifiques
    enhanced_info = {
        **info,
        "model_type": "collaborative_filtering",
        "algorithm": "user-user",
        "features": [
            "Filtrage collaboratif user-user",
            "Calcul de similarité entre utilisateurs",
            "Recommandations personnalisées",
            "Support batch"
        ],
        "endpoints": {
            "recommend": "/api/v1/recommendation/recommend",
            "batch": "/api/v1/recommendation/batch-recommend",
            "health": "/api/v1/recommendation/health",
            "info": "/api/v1/recommendation/info"
        }
    }
    
    return enhanced_info


@router.get(
    "/examples",
    summary="Exemples d'utilisation",
    description="Exemples de requêtes et réponses pour le système de recommandation"
)
async def recommendation_examples():
    """Exemples d'utilisation du système de recommandation"""
    return {
        "examples": {
            "single_user": {
                "request": {
                    "user_id": 1,
                    "top_n": 10
                },
                "expected_response": {
                    "user_id": 1,
                    "recommendations": [
                        {"post_id": 5, "score": 0.95},
                        {"post_id": 12, "score": 0.87}
                    ],
                    "total_recommendations": 10
                }
            },
            "with_available_posts": {
                "request": {
                    "user_id": 2,
                    "top_n": 5,
                    "available_posts": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                },
                "note": "Limite les recommandations aux posts spécifiés"
            }
        },
        "batch_example": {
            "request": {
                "user_ids": [1, 2, 3],
                "top_n": 10
            },
            "note": "Retourne des recommandations pour chaque utilisateur"
        },
        "curl_examples": {
            "recommend": 'curl -X POST "http://localhost:8000/api/v1/recommendation/recommend" -H "Content-Type: application/json" -d \'{"user_id": 1, "top_n": 10}\'',
            "health": 'curl http://localhost:8000/api/v1/recommendation/health',
            "info": 'curl http://localhost:8000/api/v1/recommendation/info'
        }
    }
