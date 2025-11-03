"""
Routes API spécifiques pour le modèle HateComment BERT
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.model_registry import registry
from app.utils.logger import setup_logger
import time

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/hatecomment", tags=["HateComment BERT"])


# ============================================================================
# SCHÉMAS SPÉCIFIQUES HATECOMMENT
# ============================================================================

class HateCommentRequest(BaseModel):
    """Requête pour analyse de hate speech"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texte à analyser pour détecter le hate speech",
        example="Je déteste ces gens"
    )
    include_reasoning: bool = Field(
        True,
        description="Inclure l'explication détaillée"
    )

class HateCommentResponse(BaseModel):
    """Réponse d'analyse de hate speech"""
    prediction: str = Field(
        ..., 
        description="HAINEUX ou NON-HAINEUX",
        example="HAINEUX"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Niveau de confiance (0.0 à 1.0)",
        example=0.92
    )
    severity: str = Field(
        ...,
        description="Niveau de sévérité du hate speech",
        example="Critique"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Explication détaillée de la classification",
        example="Commentaire classifié comme haineux avec une confiance de 92.00%"
    )
    hate_classification: str = Field(
        ...,
        description="Classification hate speech (haineux/non-haineux)",
        example="haineux"
    )
    original_label: str = Field(
        ...,
        description="Label original du modèle BERT",
        example="LABEL_1"
    )
    enhanced: bool = Field(
        ...,
        description="Modèle Enhanced v1.1.0 utilisé",
        example=True
    )
    boost_applied: Optional[bool] = Field(
        None,
        description="Post-processing boost appliqué",
        example=True
    )
    processing_time: Optional[float] = Field(
        None,
        description="Temps de traitement en secondes",
        example=0.045
    )

class BatchHateCommentRequest(BaseModel):
    """Requête batch pour analyse de hate speech"""
    texts: List[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Liste de textes à analyser (max 100)",
        example=["Hello world", "Je déteste tout le monde"]
    )
    include_reasoning: bool = Field(
        False,
        description="Inclure les explications (défaut: false pour performance)"
    )

class BatchHateCommentResult(BaseModel):
    """Résultat individuel d'analyse batch"""
    text: str = Field(..., description="Texte analysé (tronqué si > 100 chars)")
    prediction: str = Field(..., description="HAINEUX ou NON-HAINEUX")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance")
    severity: str = Field(..., description="Sévérité")
    reasoning: Optional[str] = Field(None, description="Explication")
    hate_classification: str = Field(..., description="Classification")

class BatchHateCommentResponse(BaseModel):
    """Réponse batch d'analyse de hate speech"""
    results: List[BatchHateCommentResult] = Field(..., description="Résultats d'analyse")
    total_processed: int = Field(..., description="Nombre de textes traités")
    processing_time: float = Field(..., description="Temps total de traitement")
    model_used: str = Field(..., description="Modèle utilisé")
    enhanced_version: str = Field(..., description="Version du modèle Enhanced")

class HateCommentHealthResponse(BaseModel):
    """Réponse health check HateComment"""
    status: str = Field(..., description="healthy ou unhealthy")
    model: str = Field(..., description="Nom du modèle")
    version: str = Field(..., description="Version du modèle")
    device: str = Field(..., description="Device utilisé (cuda/cpu)")
    fine_tuned: bool = Field(..., description="Modèle fine-tuné utilisé")
    enhanced: bool = Field(..., description="Version Enhanced")
    gpu_name: Optional[str] = Field(None, description="Nom du GPU si disponible")
    gpu_memory_allocated: Optional[str] = Field(None, description="Mémoire GPU allouée")


# ============================================================================
# ROUTES HATECOMMENT BERT
# ============================================================================

@router.get(
    "/health",
    response_model=HateCommentHealthResponse,
    summary="Health check HateComment BERT",
    description="Vérifie l'état de santé du modèle HateComment BERT Enhanced"
)
async def hatecomment_health():
    """Health check spécifique pour HateComment BERT"""
    model = registry.get("hatecomment-bert")
    if not model:
        raise HTTPException(
            status_code=404,
            detail="Modèle HateComment BERT non trouvé"
        )
    
    health_data = model.health_check()
    return HateCommentHealthResponse(**health_data)


@router.post(
    "/detect",
    response_model=HateCommentResponse,
    summary="Détecter hate speech",
    description="Analyse un texte pour détecter le hate speech avec le modèle BERT Enhanced v1.1.0"
)
async def detect_hate_speech(request: HateCommentRequest) -> HateCommentResponse:
    """
    Détecte le hate speech dans un texte.
    
    - **text**: Texte à analyser (1-5000 caractères)
    - **include_reasoning**: Inclure l'explication détaillée
    
    Retourne:
    - **prediction**: HAINEUX ou NON-HAINEUX
    - **confidence**: Niveau de confiance (0-1)
    - **severity**: Sévérité (Aucune, Faible, Moyenne, Élevée, Critique)
    - **reasoning**: Explication détaillée
    - **hate_classification**: Classification simplifiée
    - **enhanced**: Utilise le modèle Enhanced v1.1.0
    """
    try:
        logger.info(f"Détection hate speech (texte: {len(request.text)} chars)")
        
        # Récupérer le modèle HateComment BERT
        model = registry.get("hatecomment-bert")
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Modèle HateComment BERT non disponible"
            )
        
        # Mesurer le temps de traitement
        start_time = time.time()
        
        # Prédiction
        result = model.predict(
            text=request.text,
            include_reasoning=request.include_reasoning
        )
        
        processing_time = time.time() - start_time
        result["processing_time"] = round(processing_time, 3)
        result["enhanced"] = True  # Version Enhanced v1.1.0
        
        logger.info(f"  → Prédiction: {result['prediction']} (confiance: {result['confidence']:.3f})")
        
        return HateCommentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur détection hate speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de détection: {str(e)}"
        )


@router.post(
    "/batch-detect",
    response_model=BatchHateCommentResponse,
    summary="Détection batch hate speech",
    description="Analyse plusieurs textes en batch pour détecter le hate speech (max 100 textes)"
)
async def batch_detect_hate_speech(request: BatchHateCommentRequest) -> BatchHateCommentResponse:
    """
    Détecte le hate speech dans plusieurs textes en batch.
    
    - **texts**: Liste de textes (1-100 textes)
    - **include_reasoning**: Inclure les explications (défaut: false)
    
    Retourne:
    - **results**: Liste des analyses
    - **total_processed**: Nombre de textes traités
    - **processing_time**: Temps total de traitement
    - **enhanced_version**: Version du modèle Enhanced
    """
    try:
        logger.info(f"Détection batch hate speech ({len(request.texts)} textes)")
        
        # Récupérer le modèle
        model = registry.get("hatecomment-bert")
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Modèle HateComment BERT non disponible"
            )
        
        # Traitement batch
        start_time = time.time()
        results = model.batch_predict(
            texts=request.texts,
            include_reasoning=request.include_reasoning
        )
        processing_time = time.time() - start_time
        
        # Formater les résultats
        formatted_results = []
        for i, (text, result) in enumerate(zip(request.texts, results)):
            formatted_results.append(BatchHateCommentResult(
                text=text[:100] + "..." if len(text) > 100 else text,
                prediction=result["prediction"],
                confidence=float(result["confidence"]),
                severity=result["severity"],
                reasoning=result.get("reasoning") if request.include_reasoning else None,
                hate_classification=result["hate_classification"]
            ))
        
        logger.info(f"  → Traité {len(formatted_results)} textes en {processing_time:.2f}s")
        
        return BatchHateCommentResponse(
            results=formatted_results,
            total_processed=len(formatted_results),
            processing_time=round(processing_time, 2),
            model_used="hatecomment-bert",
            enhanced_version="1.1.0"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch détection hate speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de détection batch: {str(e)}"
        )


@router.get(
    "/info",
    summary="Informations modèle HateComment",
    description="Retourne les informations détaillées sur le modèle HateComment BERT"
)
async def hatecomment_info():
    """Informations détaillées sur le modèle HateComment BERT"""
    model = registry.get("hatecomment-bert")
    if not model:
        raise HTTPException(
            status_code=404,
            detail="Modèle HateComment BERT non trouvé"
        )
    
    info = model.get_info()
    
    # Ajouter des informations spécifiques
    enhanced_info = {
        **info,
        "model_type": "hate_speech_detection",
        "languages": ["français", "anglais"],
        "architecture": "BERT multilingue fine-tuné",
        "enhanced_features": [
            "Post-processing intelligent",
            "Patterns regex français/anglais",
            "Seuil adaptatif",
            "Support GPU optimisé"
        ],
        "performance": {
            "accuracy": "88.94%",
            "f1_score": "90.56%",
            "precision": "89.20%",
            "recall": "91.97%"
        },
        "endpoints": {
            "detection": "/api/v1/hatecomment/detect",
            "batch": "/api/v1/hatecomment/batch-detect",
            "health": "/api/v1/hatecomment/health",
            "info": "/api/v1/hatecomment/info"
        }
    }
    
    return enhanced_info


@router.get(
    "/examples",
    summary="Exemples d'utilisation",
    description="Exemples de requêtes et réponses pour le modèle HateComment BERT"
)
async def hatecomment_examples():
    """Exemples d'utilisation du modèle HateComment BERT"""
    return {
        "examples": {
            "hate_speech_french": {
                "request": {
                    "text": "Je déteste ces gens",
                    "include_reasoning": True
                },
                "expected_response": {
                    "prediction": "HAINEUX",
                    "confidence": 0.85,
                    "severity": "Élevée",
                    "hate_classification": "haineux"
                }
            },
            "hate_speech_english": {
                "request": {
                    "text": "I hate all those people",
                    "include_reasoning": True
                },
                "expected_response": {
                    "prediction": "HAINEUX",
                    "confidence": 0.78,
                    "severity": "Élevée",
                    "hate_classification": "haineux"
                }
            },
            "normal_text": {
                "request": {
                    "text": "J'aime cette belle journée",
                    "include_reasoning": False
                },
                "expected_response": {
                    "prediction": "NON-HAINEUX",
                    "confidence": 0.92,
                    "severity": "Aucune",
                    "hate_classification": "non-haineux"
                }
            }
        },
        "batch_example": {
            "request": {
                "texts": [
                    "Hello world",
                    "Je déteste tout le monde",
                    "Nice weather today"
                ],
                "include_reasoning": False
            },
            "note": "Retourne une liste de résultats avec processing_time"
        },
        "curl_examples": {
            "detect": 'curl -X POST "http://localhost:8000/api/v1/hatecomment/detect" -H "Content-Type: application/json" -d \'{"text": "Je déteste ces gens", "include_reasoning": true}\'',
            "health": 'curl http://localhost:8000/api/v1/hatecomment/health',
            "info": 'curl http://localhost:8000/api/v1/hatecomment/info'
        }
    }
