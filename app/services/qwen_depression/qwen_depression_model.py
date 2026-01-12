"""
Qwen 2.5 1.5B Depression Detection Model

Depression detection using Qwen 2.5 1.5B via Ollama.
Provides better reasoning capabilities than BERT models with acceptable latency.
"""
from typing import Dict, Any, List, Optional
import time
import json
import re
import httpx
from app.core.base_model import BaseMLModel
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class QwenDepressionModel(BaseMLModel):
    """
    Depression detection model using Qwen 2.5 1.5B via Ollama.
    
    Features:
    - Better reasoning and context understanding
    - Latency: 200-500ms on CPU
    - Memory: 2-3GB RAM
    - Supports French and multilingual text
    - Detailed reasoning for predictions
    """
    
    @property
    def model_name(self) -> str:
        return "qwen-depression"
    
    @property
    def model_version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "Equipe YANSNET"
    
    @property
    def description(self) -> str:
        return f"Detection de depression avec Qwen 2.5 ({settings.QWEN_DETECTION_MODEL})"
    
    @property
    def tags(self) -> List[str]:
        return ["qwen", "ollama", "french", "depression", "reasoning"]

    
    # Prompt template for depression detection
    DETECTION_PROMPT = """Tu es un assistant specialise dans l'analyse de texte pour detecter des signes de depression.

Analyse le texte suivant et determine s'il contient des indicateurs de depression.

Texte a analyser:
"{text}"

Reponds UNIQUEMENT avec un JSON valide dans ce format exact:
{{
    "prediction": "DEPRESSION" ou "NORMAL",
    "confidence": un nombre entre 0.0 et 1.0,
    "severity": "Aucune", "Faible", "Moyenne", "Elevee" ou "Critique",
    "reasoning": "explication courte de ton analyse"
}}

JSON:"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize Qwen model via Ollama.
        
        Args:
            model_name: Ollama model name (default: from settings)
            base_url: Ollama API URL (default: from settings)
            timeout: Request timeout in seconds
        """
        self._initialized = False
        self.ollama_model = model_name or settings.QWEN_DETECTION_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.timeout = timeout
        self.max_length = settings.QWEN_MAX_LENGTH
        
        # HTTP client for Ollama API
        self._client = httpx.Client(timeout=timeout)
        
        try:
            self._verify_model()
            self._initialized = True
            self._warmup_model()
            logger.info(f"Qwen {self.ollama_model} initialise via {self.base_url}")
        except Exception as e:
            logger.error(f"Erreur d'initialisation Qwen: {e}")
            self._initialized = False
            raise
    
    def _verify_model(self):
        """Verify that the Qwen model is available in Ollama."""
        try:
            response = self._client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check if our model is available
            if not any(self.ollama_model in name for name in model_names):
                logger.warning(
                    f"Modele {self.ollama_model} non trouve. "
                    f"Modeles disponibles: {model_names}"
                )
                # Try to pull the model
                self._pull_model()
            else:
                logger.info(f"Modele {self.ollama_model} disponible")
                
        except httpx.ConnectError:
            raise RuntimeError(
                f"Impossible de se connecter a Ollama ({self.base_url}). "
                f"Verifiez que Ollama est demarre."
            )
        except Exception as e:
            raise RuntimeError(f"Erreur de verification du modele: {e}")
    
    def _pull_model(self):
        """Pull the model from Ollama registry."""
        logger.info(f"Telechargement du modele {self.ollama_model}...")
        try:
            response = self._client.post(
                f"{self.base_url}/api/pull",
                json={"name": self.ollama_model},
                timeout=600.0  # 10 minutes for download
            )
            response.raise_for_status()
            logger.info(f"Modele {self.ollama_model} telecharge")
        except Exception as e:
            raise RuntimeError(f"Erreur de telechargement: {e}")
    
    def _warmup_model(self):
        """Warm up the model with a dummy inference."""
        try:
            logger.info("Rechauffement du modele Qwen...")
            self.predict("Ceci est un test.", include_reasoning=False)
            logger.info("Modele Qwen rechauffe")
        except Exception as e:
            logger.warning(f"Avertissement lors du rechauffement: {e}")

    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        text = text.strip()
        if len(text) > self.max_length:
            text = text[:self.max_length]
            logger.warning(f"Texte tronque a {self.max_length} caracteres")
        return text
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the JSON response from Qwen.
        
        Args:
            response_text: Raw response from Qwen
            
        Returns:
            Parsed prediction dict
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Validate and normalize
                prediction = result.get("prediction", "NORMAL").upper()
                if "DEPR" in prediction:
                    prediction = "DEPRESSION"
                else:
                    prediction = "NORMAL"
                
                confidence = float(result.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))
                
                severity = result.get("severity", "Aucune")
                valid_severities = ["Aucune", "Faible", "Moyenne", "Elevee", "Critique"]
                if severity not in valid_severities:
                    severity = self._classify_severity(confidence, prediction)
                
                reasoning = result.get("reasoning", "")
                
                return {
                    "prediction": prediction,
                    "confidence": round(confidence, 4),
                    "severity": severity,
                    "reasoning": reasoning
                }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Erreur de parsing JSON: {e}")
        
        # Fallback: try to extract prediction from text
        return self._fallback_parse(response_text)
    
    def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails."""
        text_lower = response_text.lower()
        
        if "depression" in text_lower or "deprime" in text_lower:
            prediction = "DEPRESSION"
            confidence = 0.7
        else:
            prediction = "NORMAL"
            confidence = 0.6
        
        severity = self._classify_severity(confidence, prediction)
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "severity": severity,
            "reasoning": "Analyse basee sur le contenu du texte."
        }
    
    def _classify_severity(self, confidence: float, prediction: str) -> str:
        """Classify depression severity based on confidence."""
        if prediction != "DEPRESSION":
            return "Aucune"
        
        if confidence >= 0.9:
            return "Critique"
        elif confidence >= 0.75:
            return "Elevee"
        elif confidence >= 0.6:
            return "Moyenne"
        else:
            return "Faible"

    
    def predict(self, text: str, include_reasoning: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Predict depression from text using Qwen.
        
        Args:
            text: Text to analyze
            include_reasoning: Include explanation (default: True)
            **kwargs: Additional parameters
            
        Returns:
            Dict with prediction, confidence, severity, reasoning, processing_time
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialise")
        
        start_time = time.time()
        
        try:
            # Preprocess
            text = self._preprocess_text(text)
            
            # Build prompt
            prompt = self.DETECTION_PROMPT.format(text=text)
            
            # Call Ollama API
            response = self._client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 256
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            response_data = response.json()
            response_text = response_data.get("response", "")
            
            result = self._parse_response(response_text)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            result["processing_time"] = round(processing_time, 2)
            
            # Remove reasoning if not requested
            if not include_reasoning:
                result.pop("reasoning", None)
            
            return result
            
        except httpx.TimeoutException:
            logger.error(f"Timeout lors de l'inference Qwen")
            raise RuntimeError("Timeout de l'inference")
        except Exception as e:
            logger.error(f"Erreur de prediction Qwen: {e}")
            raise
    
    def batch_predict(
        self, texts: List[str], include_reasoning: bool = False, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Batch prediction (sequential for Ollama).
        
        Args:
            texts: List of texts to analyze
            include_reasoning: Include explanations
            **kwargs: Additional parameters
            
        Returns:
            List of prediction results
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialise")
        
        logger.info(f"Prediction batch de {len(texts)} textes avec Qwen")
        
        results = []
        start_time = time.time()
        
        for text in texts:
            try:
                result = self.predict(text, include_reasoning=include_reasoning)
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur sur un texte: {e}")
                results.append({
                    "prediction": "NORMAL",
                    "confidence": 0.0,
                    "severity": "Aucune",
                    "processing_time": 0.0,
                    "error": str(e)
                })
        
        total_time = (time.time() - start_time) * 1000
        logger.info(f"Batch traite: {len(texts)} textes en {total_time:.2f}ms")
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Check if model is operational."""
        try:
            result = self.predict("Je vais bien.", include_reasoning=False)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version,
                "llm_provider": "ollama",
                "llm_model": self.ollama_model,
                "base_url": self.base_url,
                "test_latency_ms": result.get("processing_time"),
                "test_prediction": result.get("prediction")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "llm_provider": "ollama",
                "llm_model": self.ollama_model,
                "error": str(e)
            }
