"""
Modèle HateComment BERT amélioré avec post-processing
"""
import torch
import re
from typing import Dict, Any, List
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from pathlib import Path
import os

from app.core.base_model import BaseMLModel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class HateCommentBertModel(BaseMLModel):
    """
    Modèle BERT multilingue fine-tuné pour la détection de hate speech
    avec post-processing amélioré
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialise le modèle HateComment BERT amélioré
        
        Args:
            model_path: Chemin vers le modèle fine-tuné (optionnel)
        """
        self._initialized = False
        
        # Configuration du device avec optimisations GPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Utilisation du device: {self.device}")
        
        # Optimisations GPU si disponible
        if self.device.type == "cuda":
            logger.info(f"GPU détecté: {torch.cuda.get_device_name(0)}")
            logger.info(f"Mémoire GPU disponible: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            # Optimiser la mémoire GPU
            torch.cuda.empty_cache()
            # Activer les optimisations CUDA
            torch.backends.cudnn.benchmark = True
        
        # Chemin du modèle
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "model")
        
        self.model_path = model_path
        
        # Charger le modèle et tokenizer
        try:
            if self._model_exists(model_path):
                logger.info(f"Chargement du modèle fine-tuné depuis {model_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(model_path, token=False)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path, token=False)
                self.is_fine_tuned = True
            else:
                logger.warning("Modèle fine-tuné non trouvé, utilisation du modèle de base")
                base_model = 'bert-base-multilingual-cased'
                logger.info(f"Chargement de {base_model}...")
                self.tokenizer = AutoTokenizer.from_pretrained(base_model, token=False)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    base_model, 
                    num_labels=2,
                    token=False
                )
                self.is_fine_tuned = False
            
            # Déplacer le modèle sur le device approprié
            self.model.to(self.device)
            
            # Créer le pipeline de classification
            self.classifier = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device.type == "cuda" else -1,
                return_all_scores=True
            )
            
            # Patterns de hate speech pour post-processing
            self._init_hate_patterns()
            
            self._initialized = True
            logger.info(f"✓ {self.model_name} initialisé avec succès")
            
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'initialisation de {self.model_name}: {e}")
            raise
    
    def _init_hate_patterns(self):
        """Initialise les patterns de hate speech pour le post-processing"""
        # Patterns de hate speech français
        self.hate_patterns_fr = [
            r'\b(je déteste|j\'ai horreur de|je hais)\s+(ces?|les?|tous?\s+les?)\s+(gens?|personnes?)',
            r'\bsale\s+race\b',
            r'\b(crève|crevez|mort aux?)\b',
            r'\b(dégage|dégagez|cassez?-vous)\s+(de\s+)?(notre?|mon)\s+(pays?|territoire)',
            r'\binférieurs?\b.*\b(race|origine|ethnie)',
            r'\b(tous?\s+les?|ces)\s+\w+\s+(sont|c\'est)\s+(des?\s+)?(merdes?|pourris?|nuls?)',
        ]
        
        # Patterns de hate speech anglais
        self.hate_patterns_en = [
            r'\bi\s+hate\s+(all|those|these)\s+\w+',
            r'\b(kill|die)\s+(all|those|these)',
            r'\b(go\s+back|get\s+out)\s+(to|of)',
            r'\binferior\s+(race|people|beings?)',
            r'\b(all|those|these)\s+\w+\s+(should|must)\s+(die|leave|go)',
        ]
        
        # Mots-clés de renforcement
        self.hate_keywords = [
            'déteste', 'hais', 'hate', 'kill', 'die', 'mort', 'crève',
            'sale', 'dirty', 'inférieur', 'inferior', 'race', 'ethnie'
        ]
    
    def _model_exists(self, path: str) -> bool:
        """Vérifie si le modèle existe au chemin spécifié"""
        model_path = Path(path)
        return (model_path.exists() and 
                (model_path / "config.json").exists() and
                ((model_path / "pytorch_model.bin").exists() or 
                 (model_path / "model.safetensors").exists()))
    
    @property
    def model_name(self) -> str:
        return "hatecomment-bert"
    
    @property
    def model_version(self) -> str:
        return "1.1.0"  # Version améliorée
    
    @property
    def author(self) -> str:
        return "Équipe ETSIA"
    
    @property
    def description(self) -> str:
        return "BERT multilingue fine-tuné pour détection de hate speech avec post-processing amélioré"
    
    @property
    def tags(self) -> List[str]:
        return ["bert", "multilingual", "hate-speech", "french", "english", "transformers", "enhanced"]
    
    def _apply_pattern_boost(self, text: str, base_score: float) -> float:
        """Applique un boost basé sur les patterns détectés"""
        text_lower = text.lower()
        
        # Vérifier les patterns français
        for pattern in self.hate_patterns_fr:
            if re.search(pattern, text_lower):
                return min(0.95, base_score + 0.3)  # Boost significatif
        
        # Vérifier les patterns anglais
        for pattern in self.hate_patterns_en:
            if re.search(pattern, text_lower):
                return min(0.95, base_score + 0.3)
        
        # Compter les mots-clés de hate
        keyword_count = sum(1 for keyword in self.hate_keywords if keyword in text_lower)
        if keyword_count >= 2:
            return min(0.90, base_score + 0.2)
        elif keyword_count >= 1:
            return min(0.85, base_score + 0.1)
        
        return base_score
    
    def predict(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Détecte si le texte contient du hate speech avec post-processing amélioré
        
        Args:
            text: Texte à analyser
            **kwargs: Paramètres additionnels (ignorés)
        
        Returns:
            Dict avec prediction, confidence, severity, reasoning
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé correctement")
        
        try:
            # Prétraitement
            processed_text = self._preprocess_text(text)
            
            if not processed_text:
                return {
                    "prediction": "NON-HAINEUX",
                    "confidence": 0.5,
                    "severity": "Aucune",
                    "reasoning": "Texte vide ou invalide"
                }
            
            # Prédiction du modèle de base
            results = self.classifier(processed_text)
            scores = results[0]
            
            label_0 = next(s for s in scores if s['label'] == 'LABEL_0')
            label_1 = next(s for s in scores if s['label'] == 'LABEL_1')
            
            base_hate_score = label_1['score']
            
            # Appliquer le post-processing
            enhanced_hate_score = self._apply_pattern_boost(processed_text, base_hate_score)
            
            # Seuil adaptatif basé sur le boost appliqué
            threshold = 0.3 if enhanced_hate_score > base_hate_score else 0.5
            
            # Déterminer la prédiction finale
            if enhanced_hate_score > threshold:
                prediction = "HAINEUX"
                confidence = enhanced_hate_score
            else:
                prediction = "NON-HAINEUX"
                confidence = 1 - enhanced_hate_score
            
            # Formater le résultat
            result = self._format_hate_result(prediction, confidence, enhanced_hate_score > base_hate_score)
            
            # Ajouter des métadonnées
            result["model_fine_tuned"] = self.is_fine_tuned
            result["base_score"] = float(base_hate_score)
            result["enhanced_score"] = float(enhanced_hate_score)
            result["boost_applied"] = enhanced_hate_score > base_hate_score
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur de prédiction {self.model_name}: {e}")
            return {
                "prediction": "ERREUR",
                "confidence": 0.0,
                "severity": "Aucune",
                "reasoning": f"Erreur lors de l'analyse: {str(e)}"
            }
    
    def _preprocess_text(self, text: str) -> str:
        """
        Prétraite le texte avant analyse
        
        Args:
            text: Texte brut
            
        Returns:
            Texte prétraité
        """
        if not text or not text.strip():
            return ""
        
        # Nettoyage basique
        text = text.strip()
        # Limiter la longueur pour éviter les problèmes de tokenisation
        if len(text) > 500:
            text = text[:500]
        
        return text
    
    def _format_hate_result(self, prediction: str, confidence: float, boost_applied: bool = False) -> Dict[str, Any]:
        """
        Formate le résultat de hate speech dans le format attendu par l'API
        
        Args:
            prediction: "HAINEUX" ou "NON-HAINEUX"
            confidence: Confiance de la prédiction
            boost_applied: Si un boost a été appliqué
            
        Returns:
            Dict avec le résultat formaté
        """
        # Déterminer si c'est haineux ou non
        is_hateful = prediction == "HAINEUX"
        
        # Déterminer la sévérité basée sur la confiance
        if is_hateful:
            if confidence > 0.9:
                severity = "Critique"
            elif confidence > 0.8:
                severity = "Élevée"
            elif confidence > 0.6:
                severity = "Moyenne"
            else:
                severity = "Faible"
        else:
            severity = "Aucune"
        
        # Créer le message de raisonnement
        hate_label = "haineux" if is_hateful else "non-haineux"
        reasoning = f"Commentaire classifié comme {hate_label} avec une confiance de {confidence:.2%}."
        
        if boost_applied:
            reasoning += " Détection améliorée par analyse de patterns."
        
        if is_hateful:
            reasoning += " Le contenu contient des éléments de discours haineux."
        else:
            reasoning += " Le contenu ne présente pas de signes de discours haineux."
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "severity": severity,
            "reasoning": reasoning,
            "hate_classification": hate_label,
            "original_label": "LABEL_1" if is_hateful else "LABEL_0"
        }
    
    def batch_predict(self, texts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Analyse plusieurs textes en batch
        
        Args:
            texts: Liste de textes à analyser
            **kwargs: Paramètres additionnels
            
        Returns:
            Liste des résultats de prédiction
        """
        if not self._initialized:
            raise RuntimeError(f"{self.model_name} n'est pas initialisé correctement")
        
        results = []
        for text in texts:
            try:
                result = self.predict(text, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur batch prediction pour '{text}': {e}")
                results.append({
                    "prediction": "ERREUR",
                    "confidence": 0.0,
                    "severity": "Aucune",
                    "reasoning": f"Erreur: {str(e)}"
                })
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie l'état de santé du modèle
        
        Returns:
            Dict avec les informations de santé
        """
        try:
            # Test de prédiction simple
            test_result = self.predict("Test de santé du modèle")
            
            # Informations GPU si disponible
            gpu_info = {}
            if self.device.type == "cuda":
                gpu_info = {
                    "gpu_name": torch.cuda.get_device_name(0),
                    "gpu_memory_allocated": f"{torch.cuda.memory_allocated(0) / 1e6:.1f} MB",
                    "gpu_memory_cached": f"{torch.cuda.memory_reserved(0) / 1e6:.1f} MB",
                    "gpu_utilization": "Available"
                }
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version,
                "device": str(self.device),
                "fine_tuned": self.is_fine_tuned,
                "enhanced": True,  # Nouvelle propriété
                "test_prediction": test_result.get("prediction"),
                **gpu_info
            }
            
        except Exception as e:
            logger.error(f"Health check failed for {self.model_name}: {e}")
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "version": self.model_version,
                "error": str(e)
            }
