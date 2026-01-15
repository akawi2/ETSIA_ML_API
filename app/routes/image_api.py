"""
Routes API pour l'analyse d'images - Support multi-modèles
"""
from fastapi import APIRouter, HTTPException, status, Form, UploadFile, File
from typing import List
from PIL import Image
import io
from app.core.model_registry import registry
from app.utils.logger import setup_logger


logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Analyse d'Images"])


@router.post(
    "/predict-image",
    summary="Analyser une image",
    description="Analyse une image et détecte le contenu sensible",
    operation_id="predict_image_v1"
)
async def predict_image(
    model_name: str = Form(..., description="Nom du modèle à utiliser (ex: sensitive-image-caption, nsfw-detection)"),
    image: UploadFile = File(..., description="Image à analyser (JPEG, PNG)")
):
    """
    Analyse une image et détecte le contenu sensible.
    
    - **model_name**: Nom du modèle (ex: sensitive-image-caption, nsfw-detection)
    - **image**: Image à uploader (JPEG, PNG, etc.)
    
    Retourne:
    - **prediction**: SENSIBLE ou SÛR
    - **confidence**: Niveau de confiance (0-1)
    - **severity**: Niveau de sévérité
    - **caption_en**: Légende en anglais (si applicable)
    - **caption_fr**: Légende en français (si applicable)
    - **is_safe**: Boolean indiquant si l'image est sûre
    """
    try:
        logger.info(f"Requête d'analyse d'image (modèle: {model_name})")
        
        # Vérifier le type de fichier
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Type de fichier invalide: {image.content_type}. Attendu: image/*"
            )
        
        # Lire l'image
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
        logger.info(f"  → Image chargée: {pil_image.size}")
        
        # Récupérer le modèle
        model = registry.get(model_name)
        if not model:
            available = registry.get_model_names()
            raise HTTPException(
                status_code=404,
                detail=f"Modèle '{model_name}' non trouvé. Disponibles: {available}"
            )
        
        logger.info(f"  → Utilisation du modèle: {model.model_name}")
        
        # Prédire
        result = await model.predict(image=pil_image)
        
        logger.info(f"  → Prédiction: {result['prediction']}")
        
        return {
            "prediction": result["prediction"],
            "confidence": float(result["confidence"]),
            "severity": result["severity"],
            "reasoning": result.get("reasoning"),
            "caption_en": result.get("caption_en"),
            "caption_fr": result.get("caption_fr"),
            "is_safe": result.get("is_safe", True),
            "model_used": model.model_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de l'image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'analyse d'image: {str(e)}"
        )


@router.post(
    "/batch-predict-image",
    summary="Analyser plusieurs images",
    description="Analyse plusieurs images en batch (max 10)",
    operation_id="batch_predict_image_v1"
)
async def batch_predict_image(
    model_name: str = Form(..., description="Nom du modèle à utiliser (ex: sensitive-image-caption, nsfw-detection)"),
    images: List[UploadFile] = File(..., description="Images à analyser (max 10)")
):
    """
    Analyse plusieurs images en batch.
    
    - **model_name**: Nom du modèle (ex: sensitive-image-caption, nsfw-detection)
    - **images**: Liste d'images (max 10)
    
    Retourne:
    - **results**: Liste des prédictions
    - **total_processed**: Nombre d'images traitées
    """
    try:
        if len(images) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 images par requête batch"
            )
        
        logger.info(f"Requête batch ({len(images)} images, modèle: {model_name})")
        
        # Récupérer le modèle
        model = registry.get(model_name)
        if not model:
            available = registry.get_model_names()
            raise HTTPException(
                status_code=404,
                detail=f"Modèle '{model_name}' non trouvé. Disponibles: {available}"
            )
        
        logger.info(f"  → Utilisation du modèle: {model.model_name}")
        
        # Charger toutes les images
        pil_images = []
        for img in images:
            contents = await img.read()
            pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
            pil_images.append(pil_image)
        
        # Prédire en batch
        results = model.batch_predict(images=pil_images)
        
        # Formater les résultats
        formatted_results = []
        for i, result in enumerate(results):
            formatted_results.append({
                "image_index": i,
                "prediction": result["prediction"],
                "confidence": float(result["confidence"]),
                "severity": result["severity"],
                "caption_fr": result.get("caption_fr"),
                "is_safe": result.get("is_safe", True)
            })
        
        return {
            "results": formatted_results,
            "total_processed": len(formatted_results),
            "model_used": model.model_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'analyse batch: {str(e)}"
        )
