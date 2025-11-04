"""
Modèle de Détection de Contenu NSFW dans les Images
Utilise genie10/ETSIA_CENSURE pour la classification Safe/NSFW
"""
from typing import Dict, Any, List, Optional
import torch
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor
from app.core.base_model import BaseDepressionModel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CensureModel(BaseDepressionModel):
    """
    Modèle de détection de contenu NSFW dans les images.
    
    Processus :
    1. Charge l'image
    2. Classifie comme Safe ou NSFW
    3. Retourne les probabilités pour chaque classe
    """
    
    @property
    def model_name(self) -> str:
        return "censure-nsfw"
    
    @property
    def model_version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "Équipe ETSIA"
    
    @property
    def description(self) -> str:
        return "Détection de contenu NSFW dans les images (Safe/Not Safe)"
    
    @property
    def tags(self) -> List[str]:
        return ["image-classification", "nsfw-detection", "content-moderation", "safety"]
    
    def __init__(self):
        """Initialise le modèle de détection NSFW"""
        try:
            logger.info("Initialisation du modèle de détection NSFW...")
            
            from .hf_config import HF_MODEL_REPO
            
            # Charger le modèle et le processeur
            logger.info(f"  → Chargement de {HF_MODEL_REPO}...")
            self.processor = ViTImageProcessor.from_pretrained(
                HF_MODEL_REPO,
                token=False
            )
            self.model = ViTForImageClassification.from_pretrained(
                HF_MODEL_REPO,
                token=False
            )
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.model.eval()
            
            # Mapping des labels
            self.label_mapping = {0: "Safe", 1: "NSFW"}
            
            logger.info(f"✓ {self.model_name} initialisé avec succès (device: {self.device})")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"✗ Erreur d'initialisation de {self.model_name}: {e}")
            self._initialized = False
            raise
    
    def _predict_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Prédit si une image est Safe ou NSFW.
        
        Args:
            image: Image PIL
        
        Returns:
            Dict avec les résultats de classification
        """
        inputs = self.processor(images=image.convert("RGB"), return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probabilities = torch.softmax(logits, dim=-1).squeeze().tolist()
        
        predicted_class = logits.argmax(-1).item()
        predicted_label = self.label_mapping[predicted_class]
        
        results = {
            "Safe": round(probabilities[0] * 100, 2),
            "NSFW": round(probabilities[1] * 100, 2)
        }
        
        return {
            "predicted_label": predicted_label,
            "probabilities": results,
            "is_safe": predicted_label == "Safe"
        }
    
    def predict(self, text: str = "", image_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Analyse une image et détecte le contenu NSFW.
        
        Args:
            text: Non utilisé (compatibilité avec l'interface)
            image_path: Chemin vers l'image à analyser
            **kwargs: Autres paramètres (peut contenir 'image' directement)
        
        Returns:
            Dict avec:
            - prediction: "SAFE" ou "NSFW"
            - confidence: Niveau de confiance (0.0 - 1.0)
            - severity: Niveau de sévérité
            - reasoning: Explication
            - probabilities: Probabilités pour chaque classe
        
        Raises:
            RuntimeError: Si le modèle n'est pas initialisé
            ValueError: Si aucune image n'est fournie
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé correctement")
        
        try:
            # Récupérer l'image
            image = kwargs.get('image')
            
            if image is None and image_path:
                logger.info(f"Chargement de l'image depuis: {image_path}")
                image = Image.open(image_path).convert("RGB")
            
            if image is None:
                raise ValueError("Aucune image fournie. Utilisez 'image_path' ou 'image'")
            
            # Prédiction
            logger.info("Classification de l'image...")
            result = self._predict_image(image)
            
            predicted_label = result["predicted_label"]
            probabilities = result["probabilities"]
            is_safe = result["is_safe"]
            
            # Déterminer la confiance et la sévérité
            confidence = probabilities[predicted_label] / 100.0
            
            if is_safe:
                severity = "Aucune"
                reasoning = f"✅ Contenu sûr - L'image est classifiée comme Safe avec {probabilities['Safe']}% de confiance"
            else:
                if probabilities['NSFW'] > 90:
                    severity = "Critique"
                elif probabilities['NSFW'] > 75:
                    severity = "Élevée"
                elif probabilities['NSFW'] > 60:
                    severity = "Moyenne"
                else:
                    severity = "Faible"
                
                reasoning = f"⚠️ CONTENU NSFW DÉTECTÉ - L'image contient du contenu inapproprié avec {probabilities['NSFW']}% de confiance"
            
            logger.info(f"  → Classification: {predicted_label} ({confidence:.2%})")
            
            return {
                "prediction": predicted_label.upper(),
                "confidence": confidence,
                "severity": severity,
                "reasoning": reasoning,
                "probabilities": probabilities,
                "is_safe": is_safe
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de l'image: {e}")
            raise
    
    def batch_predict(self, texts: List[str] = None, image_paths: List[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Analyse plusieurs images en batch.
        
        Args:
            texts: Non utilisé (compatibilité)
            image_paths: Liste de chemins vers les images
            **kwargs: Peut contenir 'images' (liste d'images PIL)
        
        Returns:
            Liste de résultats
        """
        images = kwargs.get('images', [])
        
        if not images and image_paths:
            images = [Image.open(path).convert("RGB") for path in image_paths]
        
        if not images:
            raise ValueError("Aucune image fournie pour le batch")
        
        logger.info(f"Analyse batch de {len(images)} images...")
        
        results = []
        for i, image in enumerate(images, 1):
            try:
                result = self.predict(image=image)
                results.append(result)
                
                if i % 5 == 0:
                    logger.info(f"  Traité {i}/{len(images)} images")
            
            except Exception as e:
                logger.error(f"Erreur sur image {i}: {e}")
                results.append({
                    "prediction": "ERREUR",
                    "confidence": 0.0,
                    "severity": "Aucune",
                    "reasoning": f"Erreur: {str(e)}",
                    "is_safe": False
                })
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie que le modèle est opérationnel.
        
        Returns:
            Dict avec status et détails
        """
        try:
            # Créer une image de test (carré blanc 224x224)
            test_image = Image.new('RGB', (224, 224), color='white')
            
            # Tester la classification
            result = self._predict_image(test_image)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version,
                "device": self.device,
                "test_prediction": result["predicted_label"]
            }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "error": str(e)
            }
