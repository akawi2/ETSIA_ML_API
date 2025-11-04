"""
Schémas Pydantic pour validation des données
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PredictionEnum(str, Enum):
    """Types de prédiction"""
    DEPRESSION = "DÉPRESSION"
    NORMAL = "NORMAL"
    ERROR = "ERREUR"
    # Support pour modèle hate speech
    HATEFUL = "HAINEUX"
    NON_HATEFUL = "NON-HAINEUX"


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
    
    @field_validator('text')
    @classmethod
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
        description="Prédiction: DÉPRESSION, NORMAL, HAINEUX ou NON-HAINEUX"
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
            "examples": [
                {
                    "prediction": "DÉPRESSION",
                    "confidence": 0.85,
                    "severity": "Élevée",
                    "reasoning": "Le texte exprime un désespoir profond et une tristesse intense, avec des pensées suicidaires explicites.",
                    "timestamp": "2025-01-16T10:30:00Z",
                    "model_used": "yansnet-llm"
                },
                {
                    "prediction": "HAINEUX",
                    "confidence": 0.92,
                    "severity": "Critique",
                    "reasoning": "Commentaire classifié comme haineux avec une confiance de 92.00%. Le contenu contient des éléments de discours haineux.",
                    "timestamp": "2025-01-16T10:30:00Z",
                    "model_used": "hatecomment-bert"
                }
            ]
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
    
    @field_validator('texts')
    @classmethod
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
                    },
                    {
                        "text": "Je déteste tout le monde",
                        "prediction": "HAINEUX",
                        "confidence": 0.91,
                        "severity": "Élevée"
                    }
                ],
                "total_processed": 3,
                "processing_time": 1.5,
                "model_used": "hatecomment-bert"
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


# ============================================================================
# SCHÉMAS POUR LA GÉNÉRATION DE CONTENU YANSNET
# ============================================================================

class PostTypeEnum(str, Enum):
    """Types de posts"""
    CONFESSION = "confession"
    RANT = "coup de gueule"
    HELP_REQUEST = "demande d'aide"
    SUPPORT = "message de soutien"
    JOKE = "blague"
    INFO = "information utile"


class SentimentEnum(str, Enum):
    """Sentiments"""
    POSITIVE = "positif"
    NEUTRAL = "neutre"
    NEGATIVE = "négatif"


class GeneratePostRequest(BaseModel):
    """Requête de génération de post"""
    post_type: Optional[PostTypeEnum] = Field(
        None,
        description="Type de post (aléatoire si non spécifié)"
    )
    topic: Optional[str] = Field(
        None,
        max_length=200,
        description="Sujet du post (aléatoire si non spécifié)"
    )
    sentiment: Optional[SentimentEnum] = Field(
        None,
        description="Sentiment souhaité (auto si non spécifié)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_type": "demande d'aide",
                "topic": "les partiels stressants",
                "sentiment": "négatif"
            }
        }


class GeneratePostResponse(BaseModel):
    """Réponse de génération de post"""
    content: str = Field(..., description="Contenu du post généré")
    post_type: str = Field(..., description="Type de post")
    topic: str = Field(..., description="Sujet du post")
    sentiment: str = Field(..., description="Sentiment du post")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Bonjour à tous, je suis vraiment stressé par les partiels qui arrivent...",
                "post_type": "demande d'aide",
                "topic": "les partiels stressants",
                "sentiment": "négatif",
                "timestamp": "2025-01-16T10:30:00Z"
            }
        }


class GenerateCommentsRequest(BaseModel):
    """Requête de génération de commentaires"""
    post_content: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Contenu du post original"
    )
    sentiment: Optional[SentimentEnum] = Field(
        None,
        description="Sentiment souhaité pour les commentaires (naturel si non spécifié)"
    )
    num_comments: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Nombre de commentaires à générer (1-20)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_content": "Je suis vraiment stressé par les partiels qui arrivent...",
                "sentiment": "positif",
                "num_comments": 3
            }
        }


class CommentData(BaseModel):
    """Données d'un commentaire"""
    content: str
    sentiment: str
    comment_number: int


class GenerateCommentsResponse(BaseModel):
    """Réponse de génération de commentaires"""
    comments: List[CommentData]
    total_comments: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "comments": [
                    {
                        "content": "Courage ! On est tous dans le même bateau.",
                        "sentiment": "positif",
                        "comment_number": 1
                    },
                    {
                        "content": "Tu devrais essayer de réviser en groupe, ça aide beaucoup !",
                        "sentiment": "positif",
                        "comment_number": 2
                    }
                ],
                "total_comments": 2,
                "timestamp": "2025-01-16T10:30:00Z"
            }
        }


class GeneratePostWithCommentsRequest(BaseModel):
    """Requête de génération de post avec commentaires"""
    post_type: Optional[PostTypeEnum] = Field(
        None,
        description="Type de post (aléatoire si non spécifié)"
    )
    topic: Optional[str] = Field(
        None,
        max_length=200,
        description="Sujet du post (aléatoire si non spécifié)"
    )
    num_comments: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        description="Nombre de commentaires (8-12 aléatoire si non spécifié)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "post_type": "blague",
                "topic": "les fêtes étudiantes",
                "num_comments": 10
            }
        }


class GeneratePostWithCommentsResponse(BaseModel):
    """Réponse de génération de post avec commentaires"""
    post: GeneratePostResponse
    comments: List[CommentData]
    total_comments: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "post": {
                    "content": "Vous savez ce qui est drôle ? Les fêtes étudiantes...",
                    "post_type": "blague",
                    "topic": "les fêtes étudiantes",
                    "sentiment": "positif",
                    "timestamp": "2025-01-16T10:30:00Z"
                },
                "comments": [
                    {
                        "content": "Haha trop vrai !",
                        "sentiment": "positif",
                        "comment_number": 1
                    }
                ],
                "total_comments": 1,
                "timestamp": "2025-01-16T10:30:00Z"
            }
        }
