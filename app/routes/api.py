"""
Routes API - Support multi-modèles
"""
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime
from app.models.schemas import (
    PredictRequest,
    PredictResponse,
    BatchPredictRequest,
    BatchPredictResponse,
    ErrorResponse
)
from app.core.model_registry import registry
from app.utils.logger import setup_logger
from PIL import Image
import io
import time

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Prédiction"])


@router.get(
    "/models",
    summary="Lister les modèles",
    description="Liste tous les modèles de détection disponibles"
)
async def list_models():
    """
    Liste tous les modèles disponibles avec leurs métadonnées.
    
    Retourne:
    - **models**: Dict des modèles avec leurs infos
    - **total**: Nombre total de modèles
    - **default**: Nom du modèle par défaut
    """
    models = registry.list_models()
    default_model = registry.get_default()
    
    return {
        "models": models,
        "total": len(models),
        "default": default_model.model_name if default_model else None
    }


@router.get(
    "/models/{model_name}/health",
    summary="Health check d'un modèle",
    description="Vérifie qu'un modèle spécifique est opérationnel"
)
async def model_health(model_name: str):
    """Vérifie la santé d'un modèle spécifique"""
    model = registry.get(model_name)
    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Modèle '{model_name}' non trouvé"
        )
    
    return model.health_check()


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Requête invalide"},
        404: {"model": ErrorResponse, "description": "Modèle non trouvé"},
        500: {"model": ErrorResponse, "description": "Erreur serveur"}
    },
    summary="Analyser un texte",
    description="Analyse un texte et détecte les signes de dépression avec le modèle spécifié"
)
async def predict(
    request: PredictRequest,
    model_name: Optional[str] = Query(
        None,
        description="Nom du modèle à utiliser (optionnel, utilise le défaut si non spécifié)"
    )
) -> PredictResponse:
    """
    Analyse un texte et détecte les signes de dépression.
    
    - **text**: Texte à analyser (1-5000 caractères)
    - **include_reasoning**: Inclure l'explication (défaut: true)
    - **model_name**: Modèle à utiliser (query param, optionnel)
    
    Retourne:
    - **prediction**: DÉPRESSION ou NORMAL
    - **confidence**: Niveau de confiance (0-1)
    - **severity**: Niveau de sévérité
    - **reasoning**: Explication (si demandé)
    - **model_used**: Nom du modèle utilisé
    """
    try:
        logger.info(f"Requête de prédiction (texte: {len(request.text)} chars, modèle: {model_name or 'default'})")
        
        # Récupérer le modèle
        if model_name:
            model = registry.get(model_name)
            if not model:
                available = registry.get_model_names()
                raise HTTPException(
                    status_code=404,
                    detail=f"Modèle '{model_name}' non trouvé. Disponibles: {available}"
                )
        else:
            model = registry.get_default()
            if not model:
                raise HTTPException(
                    status_code=500,
                    detail="Aucun modèle disponible. Vérifiez la configuration."
                )
        
        logger.info(f"  → Utilisation du modèle: {model.model_name}")
        
        # Prédire
        result = model.predict(
            text=request.text,
            include_reasoning=request.include_reasoning
        )
        
        # Construire la réponse
        return PredictResponse(
            prediction=result["prediction"],
            confidence=float(result["confidence"]),
            severity=result["severity"],
            reasoning=result.get("reasoning"),
            model_used=model.model_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de prédiction: {str(e)}"
        )


@router.post(
    "/predict-image",
    summary="Analyser une image",
    description="Analyse une image avec un modèle de vision"
)
async def predict_image(
    model_name: str = Form(..., description="Nom du modèle à utiliser"),
    image: UploadFile = File(..., description="Image à analyser")
):
    """
    Analyse une image avec un modèle de vision.
    
    - **model_name**: Nom du modèle (ex: sensitive-image-caption)
    - **image**: Fichier image (JPEG, PNG, etc.)
    """
    try:
        logger.info(f"Requête de prédiction image (modèle: {model_name})")
        
        # Récupérer le modèle
        model = registry.get(model_name)
        if not model:
            available = registry.get_model_names()
            raise HTTPException(
                status_code=404,
                detail=f"Modèle '{model_name}' non trouvé. Disponibles: {available}"
            )
        
        # Lire l'image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        logger.info(f"  → Image chargée: {pil_image.size}, mode: {pil_image.mode}")
        
        # Prédire
        result = model.predict(image=pil_image)
        
        return {
            **result,
            "model_used": model.model_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de l'image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'analyse: {str(e)}"
        )


@router.post(
    "/batch-predict",
    response_model=BatchPredictResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Requête invalide"},
        404: {"model": ErrorResponse, "description": "Modèle non trouvé"},
        500: {"model": ErrorResponse, "description": "Erreur serveur"}
    },
    summary="Analyser plusieurs textes",
    description="Analyse plusieurs textes en batch (max 100)"
)
async def batch_predict(
    request: BatchPredictRequest,
    model_name: Optional[str] = Query(
        None,
        description="Nom du modèle à utiliser (optionnel)"
    )
) -> BatchPredictResponse:
    """
    Analyse plusieurs textes en batch.
    
    - **texts**: Liste de textes (1-100 textes)
    - **include_reasoning**: Inclure les explications (défaut: false)
    - **model_name**: Modèle à utiliser (query param, optionnel)
    
    Retourne:
    - **results**: Liste des prédictions
    - **total_processed**: Nombre de textes traités
    - **processing_time**: Temps de traitement (secondes)
    - **model_used**: Nom du modèle utilisé
    """
    try:
        logger.info(f"Requête batch ({len(request.texts)} textes, modèle: {model_name or 'default'})")
        
        # Récupérer le modèle
        if model_name:
            model = registry.get(model_name)
            if not model:
                available = registry.get_model_names()
                raise HTTPException(
                    status_code=404,
                    detail=f"Modèle '{model_name}' non trouvé. Disponibles: {available}"
                )
        else:
            model = registry.get_default()
            if not model:
                raise HTTPException(
                    status_code=500,
                    detail="Aucun modèle disponible"
                )
        
        logger.info(f"  → Utilisation du modèle: {model.model_name}")
        
        # Prédire
        start_time = time.time()
        results = model.batch_predict(
            texts=request.texts,
            include_reasoning=request.include_reasoning
        )
        processing_time = time.time() - start_time
        
        # Construire la réponse
        from app.models.schemas import BatchPredictResult
        
        formatted_results = []
        for i, (text, result) in enumerate(zip(request.texts, results)):
            formatted_results.append(BatchPredictResult(
                text=text[:100] + "..." if len(text) > 100 else text,
                prediction=result["prediction"],
                confidence=float(result["confidence"]),
                severity=result["severity"],
                reasoning=result.get("reasoning") if request.include_reasoning else None
            ))
        
        return BatchPredictResponse(
            results=formatted_results,
            total_processed=len(formatted_results),
            processing_time=round(processing_time, 2),
            model_used=model.model_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de prédiction batch: {str(e)}"
        )


@router.post(
    "/batch-predict-image",
    summary="Analyser plusieurs images",
    description="Analyse plusieurs images en batch"
)
async def batch_predict_image(
    model_name: str = Form(..., description="Nom du modèle à utiliser"),
    images: List[UploadFile] = File(..., description="Images à analyser")
):
    """
    Analyse plusieurs images en batch.
    
    - **model_name**: Nom du modèle (ex: sensitive-image-caption)
    - **images**: Liste de fichiers images
    """
    try:
        logger.info(f"Requête batch image ({len(images)} images, modèle: {model_name})")
        
        # Récupérer le modèle
        model = registry.get(model_name)
        if not model:
            available = registry.get_model_names()
            raise HTTPException(
                status_code=404,
                detail=f"Modèle '{model_name}' non trouvé. Disponibles: {available}"
            )
        
        # Charger toutes les images
        pil_images = []
        for img_file in images:
            image_bytes = await img_file.read()
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_images.append(pil_image)
        
        logger.info(f"  → {len(pil_images)} images chargées")
        
        # Prédire en batch
        start_time = time.time()
        results = model.batch_predict(images=pil_images)
        processing_time = time.time() - start_time
        
        return {
            "results": results,
            "total_processed": len(results),
            "processing_time": round(processing_time, 2),
            "model_used": model.model_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse batch des images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'analyse batch: {str(e)}"
        )
