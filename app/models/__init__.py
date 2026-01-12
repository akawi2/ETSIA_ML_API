"""
Modèles Pydantic
"""
from .schemas import (
    PredictRequest,
    PredictResponse,
    BatchPredictRequest,
    BatchPredictResult,
    BatchPredictResponse,
    HealthResponse,
    ErrorResponse,
    PredictionEnum,
    SeverityEnum
)

__all__ = [
    'PredictRequest',
    'PredictResponse',
    'BatchPredictRequest',
    'BatchPredictResult',
    'BatchPredictResponse',
    'HealthResponse',
    'ErrorResponse',
    'PredictionEnum',
    'SeverityEnum'
]
