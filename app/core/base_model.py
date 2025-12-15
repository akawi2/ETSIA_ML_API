"""
Interface de base pour tous les modèles ML de YANSNET
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseMLModel(ABC):
    """
    Interface générique que tous les modèles ML doivent implémenter.
    
    Supporte différents types de modèles :
    - Classification de texte (dépression, hate speech, etc.)
    - Classification d'images (NSFW, contenu sensible, etc.)
    - Systèmes de recommandation
    - Génération de contenu
    
    Chaque étudiant doit créer une classe qui hérite de celle-ci
    et implémente toutes les méthodes abstraites.
    """
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Nom unique du modèle (ex: 'yansnet-llm', 'etudiant2-gcn')
        
        Format recommandé: 'nom_equipe-type_modele'
        """
        pass
    
    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version du modèle (ex: '1.0.0')"""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """Auteur ou équipe (ex: 'Équipe YANSNET')"""
        pass
    
    @property
    def description(self) -> str:
        """Description du modèle (optionnel)"""
        return "Modèle ML YANSNET"
    
    @property
    def tags(self) -> List[str]:
        """Tags pour catégoriser le modèle (optionnel)"""
        return []
    
    @abstractmethod
    def predict(self, **kwargs) -> Dict[str, Any]:
        """
        Effectue une prédiction avec le modèle.
        
        Args:
            **kwargs: Paramètres spécifiques au modèle
                - text: str (pour modèles de texte)
                - image: PIL.Image (pour modèles d'images)
                - user_id: int (pour systèmes de recommandation)
                - etc.
        
        Returns:
            Dict avec AU MINIMUM:
            {
                "prediction": str,  # Résultat de la prédiction
                "confidence": float,  # 0.0 à 1.0
                "severity": str,  # "Aucune", "Faible", "Moyenne", "Élevée", "Critique"
                "reasoning": str (optionnel)  # Explication
            }
            
            Le format exact dépend du type de modèle.
        
        Raises:
            Exception: Si la prédiction échoue
        """
        pass
    
    def batch_predict(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Prédiction batch (implémentation par défaut).
        
        Les modèles peuvent override cette méthode pour optimiser
        le traitement batch.
        
        Args:
            **kwargs: Paramètres spécifiques au modèle
                - texts: List[str] (pour modèles de texte)
                - images: List[PIL.Image] (pour modèles d'images)
                - user_ids: List[int] (pour systèmes de recommandation)
                - etc.
        
        Returns:
            Liste de résultats (même format que predict)
        """
        # Implémentation par défaut : traitement séquentiel
        # Les modèles peuvent override pour optimiser
        if 'texts' in kwargs:
            return [self.predict(text=text) for text in kwargs['texts']]
        elif 'images' in kwargs:
            return [self.predict(image=img) for img in kwargs['images']]
        else:
            raise NotImplementedError("batch_predict doit être implémenté pour ce type de modèle")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle.
        
        Returns:
            Dict avec métadonnées du modèle
        """
        return {
            "name": self.model_name,
            "version": self.model_version,
            "author": self.author,
            "description": self.description,
            "tags": self.tags
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Vérifie que le modèle est opérationnel.
        
        Returns:
            Dict avec status et détails
        """
        try:
            # Test simple avec un texte court
            result = self.predict("test")
            return {
                "status": "healthy",
                "model": self.model_name,
                "version": self.model_version
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "error": str(e)
            }
