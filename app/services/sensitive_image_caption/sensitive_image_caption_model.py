"""
Modèle de Détection de Contenu Sensible dans les Images
Utilise Salesforce/blip-image-captioning-base pour la génération de légendes
et détecte du contenu sensible (drogue, violence, sexe, etc.)
"""
from typing import Dict, Any, List, Optional
import re
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
from app.core.base_model import BaseMLModel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class SensitiveImageCaptionModel(BaseMLModel):
    """
    Modèle de détection de contenu sensible dans les images.
    
    Processus :
    1. Génère une légende de l'image en anglais (Salesforce/blip-image-captioning-base)
    2. Détecte les mots-clés sensibles
    3. Traduit en français
    4. Retourne une alerte si contenu sensible détecté
    """
    
    # Mots-clés sensibles (EN et FR)
    SENSITIVE_KEYWORDS = {
        # Drogue et substances illégales
        'drugs', 'drug', 'cocaine', 'heroin', 'marijuana', 'weed', 'cannabis', 'meth',
        'methamphetamine', 'lsd', 'ecstasy', 'mdma', 'opium', 'pills', 'powder',
        'drogue', 'cocaïne', 'héroïne', 'marijuana', 'cannabis', 'méthamphétamine',
        
        # Contenu sexuel
        'sex', 'porn', 'nude', 'naked', 'sexual', 'adult', 'xxx', 'nsfw',
        'sexe', 'pornographie', 'nudité', 'nu', 'sexuel', 'adulte',
        
        # Violence et armes
        'gun', 'weapon', 'knife', 'blood', 'violence', 'kill', 'dead',
        'arme', 'couteau', 'sang', 'violence', 'tuer', 'mort',
        
        # Autres contenus problématiques
        'bomb', 'explosive', 'suicide', 'self-harm',
        'bombe', 'explosif', 'suicide', 'automutilation'
    }
    
    @property
    def model_name(self) -> str:
        return "sensitive-image-caption"
    
    @property
    def model_version(self) -> str:
        return "1.0.0"
    
    @property
    def author(self) -> str:
        return "Votre Équipe"
    
    @property
    def description(self) -> str:
        return "Détection de contenu sensible dans les images (drogue, violence, sexe) via analyse de légendes"
    
    @property
    def tags(self) -> List[str]:
        return ["image-caption", "content-moderation", "git-model", "translation", "safety"]
    
    def __init__(self):
        """Initialise le modèle de génération de légendes et le traducteur"""
        try:
            logger.info("Initialisation du modèle de détection de contenu sensible...")
            
            # Charger le modèle de génération de légendes
            logger.info("  → Chargement de Salesforce/blip-image-captioning-base...")
            self.processor = BlipProcessor.from_pretrained(
                "Salesforce/blip-image-captioning-base",
                token=False
            )
            self.caption_model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base",
                token=False
            )
            
            # Charger le modèle de traduction
            logger.info("  → Chargement du traducteur EN→FR...")
            self.translator = pipeline(
                "translation",
                model="Helsinki-NLP/opus-mt-en-fr",
                device=0 if torch.cuda.is_available() else -1,
                token=False
            )
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.caption_model.to(self.device)
            
            logger.info(f"✓ {self.model_name} initialisé avec succès (device: {self.device})")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"✗ Erreur d'initialisation de {self.model_name}: {e}")
            self._initialized = False
            raise
    
    def _detect_sensitive_content(self, text: str) -> bool:
        """
        Détecte si le texte contient du contenu sensible.
        
        Args:
            text: Texte à analyser
        
        Returns:
            True si contenu sensible détecté, False sinon
        """
        text_lower = text.lower()
        
        for keyword in self.SENSITIVE_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', text_lower):
                logger.info(f"  ⚠️ Mot-clé sensible détecté: {keyword}")
                return True
        
        return False
    
    def _filter_caption(self, text: str) -> str:
        """
        Filtre ou masque le contenu sensible.
        
        Args:
            text: Texte à filtrer
        
        Returns:
            Texte filtré avec mots sensibles remplacés par ***
        """
        filtered_text = text
        
        for keyword in self.SENSITIVE_KEYWORDS:
            pattern = re.compile(r'\b' + keyword + r'\b', re.IGNORECASE)
            filtered_text = pattern.sub('***', filtered_text)
        
        return filtered_text
    
    def _generate_caption(self, image: Image.Image) -> str:
        """
        Génère une légende pour l'image.
        
        Args:
            image: Image PIL
        
        Returns:
            Légende en anglais
        """
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            generated_ids = self.caption_model.generate(**inputs, max_length=50)

        caption = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return caption
    
    def _translate_to_french(self, text: str) -> str:
        """
        Traduit le texte en français.
        
        Args:
            text: Texte en anglais
        
        Returns:
            Texte traduit en français
        """
        translation = self.translator(text)[0]['translation_text']
        return translation
    
    def predict(self, text: str = "", image_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Analyse une image et détecte le contenu sensible.
        
        Args:
            text: Non utilisé (compatibilité avec l'interface)
            image_path: Chemin vers l'image à analyser
            **kwargs: Autres paramètres (peut contenir 'image' directement)
        
        Returns:
            Dict avec:
            - prediction: "SENSIBLE" ou "SÛR"
            - confidence: Niveau de confiance (0.0 - 1.0)
            - severity: Niveau de sévérité
            - reasoning: Explication
            - caption_en: Légende en anglais (filtrée si sensible)
            - caption_fr: Légende en français (filtrée si sensible)
        
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
            
            # 1. Générer la légende en anglais
            logger.info("Génération de la légende...")
            caption_en = self._generate_caption(image)
            logger.info(f"  → Légende (EN): {caption_en}")
            
            # 2. Détecter le contenu sensible
            is_sensitive = self._detect_sensitive_content(caption_en)
            
            # 3. Préparer les résultats
            if is_sensitive:
                # Contenu sensible détecté
                filtered_en = self._filter_caption(caption_en)
                filtered_fr = self._translate_to_french(filtered_en)
                
                return {
                    "prediction": "SENSIBLE",
                    "confidence": 0.85,
                    "severity": "Élevée",
                    "reasoning": "⚠️ CONTENU SENSIBLE DÉTECTÉ - Cette image contient un contenu inapproprié (drogue, violence, ou sexe)",
                    "caption_en": filtered_en,
                    "caption_fr": filtered_fr,
                    "is_safe": False
                }
            else:
                # Contenu sûr
                caption_fr = self._translate_to_french(caption_en)
                
                return {
                    "prediction": "SÛR",
                    "confidence": 0.95,
                    "severity": "Aucune",
                    "reasoning": "✅ Contenu sûr - Aucun élément sensible détecté dans l'image",
                    "caption_en": caption_en,
                    "caption_fr": caption_fr,
                    "is_safe": True
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
            # Créer une image de test (carré blanc 100x100)
            test_image = Image.new('RGB', (100, 100), color='white')
            
            # Tester la génération de légende
            caption = self._generate_caption(test_image)
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version,
                "device": self.device,
                "test_caption": caption
            }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "error": str(e)
            }
