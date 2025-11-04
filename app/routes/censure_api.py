"""
Routes API pour le modèle de détection NSFW
"""
from fastapi import APIRouter, HTTPException, status, File, UploadFile
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.model_registry import registry
from app.utils.logger import setup_logger
from PIL import Image
import io
import time

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/censure", tags=["NSFW Detection"])


# ============================================================================
# SCHÉMAS SPÉCIFIQUES CENSURE
# ============================================================================

class CensureResponse(BaseModel):
    """Réponse de détection NSFW"""
    prediction: str = Field(..., description="SAFE ou NSFW")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance")
    severity: str = Field(..., description="Sévérité")
    reasoning: str = Field(..., description="Explication")
    probabilities: dict = Field(..., description="Probabilités Safe/NSFW")
    is_safe: bool = Field(..., description="Image sûre ou non")
    processing_time: Optional[float] = Field(None, description="Temps de traitement")


class CensureHealthResponse(BaseModel):
    """Réponse health check Censure"""
    status: str = Field(..., description="healthy ou unhealthy")
    model: str = Field(..., description="Nom du modèle")
    version: str = Field(..., description="Version du modèle")
    device: str = Field(..., description="Device utilisé")


# ============================================================================
# ROUTES CENSURE
# ============================================================================

@router.get(
    "/health",
    response_model=CensureHealthResponse,
    summary="Health check NSFW Detection",
    description="Vérifie l'état de santé du modèle de détection NSFW"
)
async def censure_health():
    """Health check spécifique pour le modèle de censure"""
    model = registry.get("censure-nsfw")
    if not model:
        raise HTTPException(
            status_code=404,
            detail="Modèle de détection NSFW non trouvé"
        )
    
    health_data = model.health_check()
    return CensureHealthResponse(**health_data)


@router.post(
    "/detect",
    response_model=CensureResponse,
    summary="Détecter contenu NSFW",
    description="Analyse une image pour détecter du contenu NSFW"
)
async def detect_nsfw(file: UploadFile = File(...)) -> CensureResponse:
    """
    Détecte le contenu NSFW dans une image.
    
    - **file**: Image à analyser (JPG, PNG)
    
    Retourne:
    - **prediction**: SAFE ou NSFW
    - **confidence**: Niveau de confiance (0-1)
    - **severity**: Sévérité (Aucune, Faible, Moyenne, Élevée, Critique)
    - **probabilities**: Probabilités pour chaque classe
    """
    try:
        logger.info(f"Détection NSFW sur image: {file.filename}")
        
        # Récupérer le modèle
        model = registry.get("censure-nsfw")
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Modèle de détection NSFW non disponible"
            )
        
        # Lire l'image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Mesurer le temps de traitement
        start_time = time.time()
        
        # Prédiction
        result = model.predict(image=image)
        
        processing_time = time.time() - start_time
        result["processing_time"] = round(processing_time, 3)
        
        logger.info(f"  → Prédiction: {result['prediction']} (confiance: {result['confidence']:.3f})")
        
        return CensureResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur détection NSFW: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de détection: {str(e)}"
        )


@router.post(
    "/batch-detect",
    summary="Détection batch NSFW",
    description="Analyse plusieurs images en batch pour détecter du contenu NSFW"
)
async def batch_detect_nsfw(files: List[UploadFile] = File(...)):
    """
    Détecte le contenu NSFW dans plusieurs images en batch.
    
    - **files**: Liste d'images à analyser
    
    Retourne:
    - **results**: Liste des analyses
    - **total_processed**: Nombre d'images traitées
    """
    try:
        logger.info(f"Détection batch NSFW ({len(files)} images)")
        
        # Récupérer le modèle
        model = registry.get("censure-nsfw")
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Modèle de détection NSFW non disponible"
            )
        
        # Charger toutes les images
        images = []
        filenames = []
        for file in files:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            images.append(image)
            filenames.append(file.filename)
        
        # Traitement batch
        start_time = time.time()
        results = model.batch_predict(images=images)
        processing_time = time.time() - start_time
        
        # Formater les résultats
        formatted_results = []
        for filename, result in zip(filenames, results):
            formatted_results.append({
                "filename": filename,
                **result
            })
        
        logger.info(f"  → Traité {len(formatted_results)} images en {processing_time:.2f}s")
        
        return {
            "results": formatted_results,
            "total_processed": len(formatted_results),
            "processing_time": round(processing_time, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch détection NSFW: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de détection batch: {str(e)}"
        )


@router.get(
    "/info",
    summary="Informations modèle NSFW",
    description="Retourne les informations détaillées sur le modèle de détection NSFW"
)
async def censure_info():
    """Informations détaillées sur le modèle de détection NSFW"""
    model = registry.get("censure-nsfw")
    if not model:
        raise HTTPException(
            status_code=404,
            detail="Modèle de détection NSFW non trouvé"
        )
    
    info = model.get_info()
    
    # Ajouter des informations spécifiques
    enhanced_info = {
        **info,
        "model_type": "nsfw_detection",
        "classes": ["Safe", "NSFW"],
        "architecture": "Vision Transformer (ViT)",
        "features": [
            "Classification binaire Safe/NSFW",
            "Probabilités pour chaque classe",
            "Support batch",
            "Optimisé pour la modération de contenu"
        ],
        "endpoints": {
            "detection": "/api/v1/censure/detect",
            "batch": "/api/v1/censure/batch-detect",
            "health": "/api/v1/censure/health",
            "info": "/api/v1/censure/info"
        }
    }
    
    return enhanced_info


@router.get(
    "/examples",
    summary="Exemples d'utilisation",
    description="Exemples de requêtes pour le modèle de détection NSFW"
)
async def censure_examples():
    """Exemples d'utilisation du modèle de détection NSFW"""
    return {
        "examples": {
            "single_image": {
                "method": "POST",
                "endpoint": "/api/v1/censure/detect",
                "content_type": "multipart/form-data",
                "body": "file: <image_file>",
                "expected_response": {
                    "prediction": "SAFE",
                    "confidence": 0.95,
                    "severity": "Aucune",
                    "probabilities": {
                        "Safe": 95.0,
                        "NSFW": 5.0
                    },
                    "is_safe": True
                }
            },
            "batch_images": {
                "method": "POST",
                "endpoint": "/api/v1/censure/batch-detect",
                "content_type": "multipart/form-data",
                "body": "files: [<image_file1>, <image_file2>, ...]",
                "note": "Retourne une liste de résultats"
            }
        },
        "curl_examples": {
            "detect": 'curl -X POST "http://localhost:8000/api/v1/censure/detect" -F "file=@image.jpg"',
            "health": 'curl http://localhost:8000/api/v1/censure/health',
            "info": 'curl http://localhost:8000/api/v1/censure/info'
        },
        "postman_instructions": {
            "detect": [
                "1. Sélectionnez POST",
                "2. URL: http://localhost:8000/api/v1/censure/detect",
                "3. Body → form-data",
                "4. Key: 'file' (type: File)",
                "5. Value: Sélectionnez une image",
                "6. Send"
            ]
        }
    }
