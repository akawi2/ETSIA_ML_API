"""
Wrapper pour le modèle NSFW avec monitoring intégré
"""
from typing import Dict, Any, List
import time
from PIL import Image
from app.core.base_model import BaseMLModel
from app.core.monitoring import emit_metric
from app.utils.logger import setup_logger
from .censure_model import predict_image

logger = setup_logger(__name__)


class CensureModel(BaseMLModel):
    """
    Modèle de détection NSFW avec monitoring
    """
    
    @property
    def model_name(self) -> str:
        return "nsfw-detection"
    
    @property
    def model_version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "Équipe ETSIA"
    
    @property
    def description(self) -> str:
        return "Détection de contenu NSFW dans les images"
    
    @property
    def tags(self) -> List[str]:
        return ["nsfw", "content-moderation", "shield-gemma", "safety"]
    
    def __init__(self):
        """Initialise le modèle NSFW"""
        try:
            logger.info("Initialisation du modèle NSFW...")
            # Le modèle est déjà chargé dans censure_model.py
            self._initialized = True
            logger.info(f"✓ {self.model_name} initialisé avec succès")
        except Exception as e:
            logger.error(f"✗ Erreur d'initialisation de {self.model_name}: {e}")
            self._initialized = False
            raise
    
    def predict(self, text: str = "", image_path: str = None, **kwargs) -> Dict[str, Any]:
        """
        Détecte le contenu NSFW dans une image
        
        Args:
            text: Non utilisé (compatibilité)
            image_path: Chemin vers l'image
            **kwargs: Peut contenir 'image' directement
        
        Returns:
            Dict avec prediction, confidence, severity, reasoning
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé correctement")
        
        start_time = time.time()
        
        try:
            # Récupérer l'image
            image = kwargs.get('image')
            
            if image is None and image_path:
                logger.info(f"Chargement de l'image depuis: {image_path}")
                image = Image.open(image_path)
            
            if image is None:
                raise ValueError("Aucune image fournie. Utilisez 'image_path' ou 'image'")
            
            # Prédiction
            results = predict_image(image)
            
            # Calculer la latence
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Analyser les résultats
            is_nsfw = False
            max_violation_score = 0.0
            violation_categories = []
            
            for category, scores in results.items():
                if scores["Prediction"] == "Violation":
                    is_nsfw = True
                    violation_categories.append(category)
                    max_violation_score = max(max_violation_score, scores["Violation"])
            
            # Déterminer la confiance et la sévérité
            if is_nsfw:
                confidence = max_violation_score / 100.0
                severity = "Critique" if confidence > 0.8 else "Élevée"
                prediction = "NSFW"
                reasoning = f"⚠️ Contenu NSFW détecté: {', '.join(violation_categories)}"
            else:
                confidence = 0.95
                severity = "Aucune"
                prediction = "SAFE"
                reasoning = "✅ Contenu sûr - Aucun élément NSFW détecté"
            
            # Émettre les métriques de monitoring
            emit_metric(
                service="nsfw_detection",
                event_name="detect_nsfw",
                model_name="shield-gemma",
                params={
                    "latency": latency_ms,
                    "is_nsfw": is_nsfw,
                    "confidence": float(confidence),
                    "violation_count": len(violation_categories)
                }
            )
            
            return {
                "prediction": prediction,
                "confidence": round(confidence, 4),
                "severity": severity,
                "reasoning": reasoning,
                "is_nsfw": is_nsfw,
                "categories": results
            }
            
        except Exception as e:
            logger.error(f"Erreur de prédiction {self.model_name}: {e}")
            
            # Émettre métrique d'erreur
            latency_ms = int((time.time() - start_time) * 1000)
            emit_metric(
                service="nsfw_detection",
                event_name="detect_nsfw_error",
                model_name="shield-gemma",
                params={
                    "latency": latency_ms,
                    "error": str(e)[:100]
                }
            )
            raise
    
    def batch_predict(self, texts: List[str] = None, image_paths: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Analyse plusieurs images en batch
        
        Args:
            texts: Non utilisé
            image_paths: Liste de chemins vers les images
            **kwargs: Peut contenir 'images'
        
        Returns:
            Liste de résultats
        """
        images = kwargs.get('images', [])
        
        if not images and image_paths:
            images = [Image.open(path) for path in image_paths]
        
        if not images:
            raise ValueError("Aucune image fournie pour le batch")
        
        logger.info(f"Analyse batch de {len(images)} images...")
        
        results = []
        for i, image in enumerate(images, 1):
            try:
                result = self.predict(image=image)
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur sur image {i}: {e}")
                results.append({
                    "prediction": "ERREUR",
                    "confidence": 0.0,
                    "severity": "Aucune",
                    "reasoning": f"Erreur: {str(e)}",
                    "is_nsfw": False
                })
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie que le modèle est opérationnel"""
        try:
            # Créer une image de test
            test_image = Image.new('RGB', (100, 100), color='white')
            
            # Tester la prédiction
            result = self.predict(image=test_image)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version,
                "test_prediction": result.get("prediction")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "error": str(e)
            }
