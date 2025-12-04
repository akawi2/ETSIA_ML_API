"""
Routes API spécialisées pour le modèle de détection de dépression YANSNET LLM
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel, Field
from app.core.model_registry import registry
from app.utils.logger import setup_logger
import time

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/depression", tags=["Depression Detection"])


# ============================================================================
# SCHÉMAS SPÉCIFIQUES DÉTECTION DE DÉPRESSION
# ============================================================================

class DepressionDetectRequest(BaseModel):
    """Requête de détection de dépression"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texte à analyser",
        example="I feel so sad and hopeless, I don't want to live anymore"
    )
    include_reasoning: bool = Field(
        True,
        description="Inclure l'explication détaillée"
    )


class DepressionDetectResponse(BaseModel):
    """Réponse de détection de dépression"""
    prediction: str = Field(..., description="DÉPRESSION ou NORMAL")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance")
    severity: str = Field(..., description="Sévérité")
    reasoning: Optional[str] = Field(None, description="Explication")
    processing_time: Optional[float] = Field(None, description="Temps de traitement")


class DepressionBatchRequest(BaseModel):
    """Requête batch de détection de dépression"""
    texts: List[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Liste de textes à analyser (max 100)",
        example=["I'm so happy today", "I feel worthless and empty"]
    )
    include_reasoning: bool = Field(
        False,
        description="Inclure les explications"
    )


class DepressionBatchResult(BaseModel):
    """Résultat individuel batch"""
    text: str = Field(..., description="Texte analysé")
    prediction: str = Field(..., description="DÉPRESSION ou NORMAL")
    confidence: float = Field(..., description="Confiance")
    severity: str = Field(..., description="Sévérité")
    reasoning: Optional[str] = Field(None, description="Explication")


class DepressionBatchResponse(BaseModel):
    """Réponse batch de détection de dépression"""
    results: List[DepressionBatchResult] = Field(..., description="Résultats")
    total_processed: int = Field(..., description="Nombre de textes traités")
    processing_time: float = Field(..., description="Temps total de traitement")


class DepressionHealthResponse(BaseModel):
    """Réponse health check Depression"""
    status: str = Field(..., description="healthy ou unhealthy")
    model: str = Field(..., description="Nom du modèle")
    version: str = Field(..., description="Version du modèle")
    llm_provider: str = Field(..., description="Provider LLM utilisé")
    llm_model: str = Field(..., description="Modèle LLM utilisé")


# ============================================================================
# ROUTES DÉTECTION DE DÉPRESSION
# ============================================================================

@router.get(
    "/health",
    response_model=DepressionHealthResponse,
    summary="Health check Depression Detection",
    description="Vérifie l'état de santé du modèle de détection de dépression"
)
async def depression_health():
    """Health check spécifique pour le modèle de détection de dépression"""
    try:
        model = registry.get("yansnet-llm")
        if not model:
            # Essayer avec le modèle par défaut
            model = registry.get_default()
            if not model or model.model_name != "yansnet-llm":
                raise HTTPException(
                    status_code=404,
                    detail="Modèle de détection de dépression non trouvé. Vérifiez que le modèle 'yansnet-llm' est enregistré."
                )
        
        health_data = model.health_check()
        return DepressionHealthResponse(**health_data)
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du health check: {str(e)}"
        )


@router.post(
    "/detect",
    response_model=DepressionDetectResponse,
    summary="Détecter la dépression",
    description="Analyse un texte pour détecter les signes de dépression"
)
async def detect_depression(request: DepressionDetectRequest) -> DepressionDetectResponse:
    """
    Détecte les signes de dépression dans un texte.
    
    - **text**: Texte à analyser (1-5000 caractères)
    - **include_reasoning**: Inclure l'explication (défaut: true)
    
    Retourne:
    - **prediction**: DÉPRESSION ou NORMAL
    - **confidence**: Niveau de confiance (0-1)
    - **severity**: Sévérité (Aucune, Faible, Moyenne, Élevée, Critique)
    - **reasoning**: Explication détaillée (si demandé)
    """
    try:
        logger.info(f"Détection de dépression (texte: {len(request.text)} chars)")
        
        # Récupérer le modèle
        model = registry.get("yansnet-llm")
        if not model:
            # Essayer avec le modèle par défaut
            model = registry.get_default()
            if not model or model.model_name != "yansnet-llm":
                available = registry.get_model_names()
                raise HTTPException(
                    status_code=404,
                    detail=f"Modèle 'yansnet-llm' non disponible. Modèles disponibles: {available}"
                )
        
        # Mesurer le temps de traitement
        start_time = time.time()
        
        # Prédiction
        result = model.predict(
            text=request.text,
            include_reasoning=request.include_reasoning
        )
        
        processing_time = time.time() - start_time
        
        logger.info(f"  → Prédiction: {result['prediction']} (confiance: {result['confidence']:.3f})")
        
        return DepressionDetectResponse(
            prediction=result["prediction"],
            confidence=float(result["confidence"]),
            severity=result["severity"],
            reasoning=result.get("reasoning"),
            processing_time=round(processing_time, 3)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur détection dépression: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de détection: {str(e)}"
        )


@router.post(
    "/batch-detect",
    response_model=DepressionBatchResponse,
    summary="Détection batch de dépression",
    description="Analyse plusieurs textes en batch pour détecter la dépression (max 100)"
)
async def batch_detect_depression(request: DepressionBatchRequest) -> DepressionBatchResponse:
    """
    Détecte les signes de dépression dans plusieurs textes en batch.
    
    - **texts**: Liste de textes (1-100)
    - **include_reasoning**: Inclure les explications (défaut: false)
    
    Retourne:
    - **results**: Liste des analyses
    - **total_processed**: Nombre de textes traités
    - **processing_time**: Temps total de traitement
    """
    try:
        logger.info(f"Détection batch de dépression ({len(request.texts)} textes)")
        
        # Récupérer le modèle
        model = registry.get("yansnet-llm")
        if not model:
            # Essayer avec le modèle par défaut
            model = registry.get_default()
            if not model or model.model_name != "yansnet-llm":
                available = registry.get_model_names()
                raise HTTPException(
                    status_code=404,
                    detail=f"Modèle 'yansnet-llm' non disponible. Modèles disponibles: {available}"
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
        for text, result in zip(request.texts, results):
            formatted_results.append(DepressionBatchResult(
                text=text[:100] + "..." if len(text) > 100 else text,
                prediction=result["prediction"],
                confidence=float(result["confidence"]),
                severity=result["severity"],
                reasoning=result.get("reasoning") if request.include_reasoning else None
            ))
        
        logger.info(f"  → Traité {len(formatted_results)} textes en {processing_time:.2f}s")
        
        return DepressionBatchResponse(
            results=formatted_results,
            total_processed=len(formatted_results),
            processing_time=round(processing_time, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch détection dépression: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de détection batch: {str(e)}"
        )


@router.get(
    "/info",
    summary="Informations modèle de dépression",
    description="Retourne les informations détaillées sur le modèle de détection de dépression"
)
async def depression_info():
    """Informations détaillées sur le modèle de détection de dépression"""
    model = registry.get("yansnet-llm")
    if not model:
        # Essayer avec le modèle par défaut
        model = registry.get_default()
        if not model or model.model_name != "yansnet-llm":
            available = registry.get_model_names()
            raise HTTPException(
                status_code=404,
                detail=f"Modèle 'yansnet-llm' non trouvé. Modèles disponibles: {available}"
            )
    
    info = model.get_info()
    
    # Ajouter des informations spécifiques
    enhanced_info = {
        **info,
        "model_type": "depression_detection",
        "classes": ["DÉPRESSION", "NORMAL"],
        "architecture": "LLM (GPT/Claude/Ollama)",
        "features": [
            "Détection de signes de dépression",
            "Analyse contextuelle approfondie",
            "Explications détaillées",
            "Support multilingue",
            "Gestion des cas ambigus"
        ],
        "performance": {
            "accuracy": "75%",
            "depression_clear": "80%",
            "normal_clear": "100%",
            "ambiguous_cases": "80%"
        },
        "endpoints": {
            "detection": "/api/v1/depression/detect",
            "batch": "/api/v1/depression/batch-detect",
            "health": "/api/v1/depression/health",
            "info": "/api/v1/depression/info",
            "examples": "/api/v1/depression/examples"
        }
    }
    
    return enhanced_info


@router.get(
    "/examples",
    summary="Exemples d'utilisation",
    description="Exemples de requêtes et réponses pour la détection de dépression"
)
async def depression_examples():
    """Exemples d'utilisation du modèle de détection de dépression"""
    return {
        "examples": {
            "depression_clear": {
                "request": {
                    "text": "I feel so sad and hopeless, I don't want to live anymore",
                    "include_reasoning": True
                },
                "expected_response": {
                    "prediction": "DÉPRESSION",
                    "confidence": 0.85,
                    "severity": "Élevée",
                    "reasoning": "Le texte exprime un désespoir profond..."
                }
            },
            "normal_clear": {
                "request": {
                    "text": "I'm so happy today, life is beautiful",
                    "include_reasoning": True
                },
                "expected_response": {
                    "prediction": "NORMAL",
                    "confidence": 0.95,
                    "severity": "Aucune",
                    "reasoning": "Le texte exprime des émotions positives..."
                }
            },
            "ambiguous": {
                "request": {
                    "text": "I'm tired today",
                    "include_reasoning": True
                },
                "note": "Cas ambigu nécessitant une analyse contextuelle"
            }
        },
        "batch_example": {
            "request": {
                "texts": [
                    "I'm so happy today",
                    "I feel worthless and empty",
                    "Just finished a great workout"
                ],
                "include_reasoning": False
            },
            "note": "Retourne une liste de résultats"
        },
        "curl_examples": {
            "detect": 'curl -X POST "http://localhost:8000/api/v1/depression/detect" -H "Content-Type: application/json" -d \'{"text": "I feel so sad", "include_reasoning": true}\'',
            "batch": 'curl -X POST "http://localhost:8000/api/v1/depression/batch-detect" -H "Content-Type: application/json" -d \'{"texts": ["Happy", "Sad"], "include_reasoning": false}\'',
            "health": 'curl http://localhost:8000/api/v1/depression/health',
            "info": 'curl http://localhost:8000/api/v1/depression/info'
        },
        "python_example": {
            "code": """
import requests

# Détection simple
response = requests.post(
    "http://localhost:8000/api/v1/depression/detect",
    json={
        "text": "I feel so sad and hopeless",
        "include_reasoning": True
    }
)
result = response.json()
print(f"Prédiction: {result['prediction']}")
print(f"Confiance: {result['confidence']}")
print(f"Raisonnement: {result['reasoning']}")

# Détection batch
response = requests.post(
    "http://localhost:8000/api/v1/depression/batch-detect",
    json={
        "texts": ["I'm happy", "I'm sad"],
        "include_reasoning": False
    }
)
results = response.json()
print(f"Traité {results['total_processed']} textes")
"""
        }
    }
