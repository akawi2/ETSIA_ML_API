from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class MetricEvent(BaseModel):
    service: str = Field(..., description="Nom du service (ex: depression_detection)")
    model_name: Optional[str] = Field("default", description="Nom du modèle spécifique")
    event_name: str = Field(..., description="Nom de l'event GA4 (ex: model_prediction)")
    params: Dict[str, Any] = Field(..., description="Dictionnaire des métriques (latency, confidence, etc.)")
    client_id: str = Field("system_mon", description="Identifiant unique du client GA4")