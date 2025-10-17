"""
Schémas Pydantic pour validation des données
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PredictionEnum(str, Enum):
    """Types de prédiction"""
    DEPRESSION = "DÉPRESSION"
    NORMAL = "NORMAL"
    ERROR = "ERREUR"


class SeverityEnum(str, Enum):
    """Niveaux de sévérité"""
    NONE = "Aucune"
    LOW = "Faible"
    MEDIUM = "Moyenne"
    HIGH = "Élevée"
    CRITICAL = "Critique"


class PredictRequest(BaseModel):
    """Requête de prédiction"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texte à analyser"
    )
    include_reasoning: bool = Field(
        default=True,
        description="Inclure le raisonnement dans la réponse"
    )
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Le texte ne peut pas être vide")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I feel so sad and hopeless, I don't want to live anymore",
                "include_reasoning": True
            }
        }


class PredictResponse(BaseModel):
    """Réponse de prédiction"""
    prediction: PredictionEnum = Field(
        ...,
        description="Prédiction: DÉPRESSION ou NORMAL"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Niveau de confiance (0-1)"
    )
    severity: SeverityEnum = Field(
        ...,
        description="Niveau de sévérité"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Explication du raisonnement"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la prédiction"
    )
    model_used: str = Field(
        ...,
        description="Modèle LLM utilisé"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "DÉPRESSION",
                "confidence": 0.85,
                "severity": "Élevée",
                "reasoning": "Le texte exprime un désespoir profond et une tristesse intense, avec des pensées suicidaires explicites.",
                "timestamp": "2025-01-16T10:30:00Z",
                "model_used": "gpt-4o-mini"
            }
        }


class BatchPredictRequest(BaseModel):
    """Requête de prédiction batch"""
    texts: List[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Liste de textes à analyser (max 100)"
    )
    include_reasoning: bool = Field(
        default=False,
        description="Inclure le raisonnement (ralentit le traitement)"
    )
    
    @validator('texts')
    def texts_not_empty(cls, v):
        if not v:
            raise ValueError("La liste ne peut pas être vide")
        # Filtrer les textes vides
        filtered = [t.strip() for t in v if t.strip()]
        if not filtered:
            raise ValueError("Tous les textes sont vides")
        return filtered
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "I'm so happy today",
                    "I feel worthless and empty"
                ],
                "include_reasoning": False
            }
        }


class BatchPredictResult(BaseModel):
    """Résultat individuel dans un batch"""
    text: str
    prediction: PredictionEnum
    confidence: float
    severity: SeverityEnum
    reasoning: Optional[str] = None


class BatchPredictResponse(BaseModel):
    """Réponse de prédiction batch"""
    results: List[BatchPredictResult]
    total_processed: int
    processing_time: float = Field(
        ...,
        description="Temps de traitement en secondes"
    )
    model_used: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "text": "I'm so happy today",
                        "prediction": "NORMAL",
                        "confidence": 0.95,
                        "severity": "Aucune"
                    },
                    {
                        "text": "I feel worthless and empty",
                        "prediction": "DÉPRESSION",
                        "confidence": 0.88,
                        "severity": "Élevée"
                    }
                ],
                "total_processed": 2,
                "processing_time": 1.2,
                "model_used": "gpt-4o-mini"
            }
        }


class HealthResponse(BaseModel):
    """Réponse du health check"""
    status: str = "healthy"
    version: str
    llm_provider: str
    llm_model: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "llm_provider": "gpt",
                "llm_model": "gpt-4o-mini",
                "timestamp": "2025-01-16T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Réponse d'erreur"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Erreur de prédiction",
                "detail": "Le service LLM est temporairement indisponible",
                "timestamp": "2025-01-16T10:30:00Z"
            }
        }
