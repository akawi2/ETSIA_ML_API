"""
Registre centralisé des modèles ML YANSNET - Enhanced Version
"""
from typing import Dict, Optional, List
from app.core.base_model import BaseMLModel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class EnhancedModelRegistry:
    """
    Registre singleton pour gérer tous les modèles ML disponibles.
    
    Enhanced version with support for:
    - Multiple model types (detection, generation, classification, etc.)
    - Priority-based model selection
    - Separate detection and generation model management
    - Fallback chains for reliability
    
    Supporte différents types de modèles :
    - Classification de texte (dépression, hate speech)
    - Classification d'images (NSFW, contenu sensible)
    - Systèmes de recommandation
    - Génération de contenu
    
    Permet d'enregistrer, récupérer et lister les modèles dynamiquement.
    """
    
    _instance: Optional['EnhancedModelRegistry'] = None
    _models: Dict[str, BaseMLModel] = {}
    _default_model: Optional[str] = None
    
    # Enhanced: Separate registries for different model types
    _detection_models: Dict[str, tuple[BaseMLModel, int]] = {}  # (model, priority)
    _generation_models: Dict[str, BaseMLModel] = {}
    _primary_detection_model: Optional[str] = None
    _primary_generation_model: Optional[str] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._models = {}
            cls._instance._default_model = None
            cls._instance._detection_models = {}
            cls._instance._generation_models = {}
            cls._instance._primary_detection_model = None
            cls._instance._primary_generation_model = None
        return cls._instance
    
    def register(self, model: BaseMLModel, set_as_default: bool = False):
        """
        Enregistre un nouveau modèle dans le registre.
        
        Args:
            model: Instance du modèle à enregistrer
            set_as_default: Si True, définit ce modèle comme défaut
        
        Raises:
            ValueError: Si le modèle est invalide
        """
        # Validation
        if not isinstance(model, BaseMLModel):
            raise ValueError(f"Le modèle doit hériter de BaseMLModel")
        
        model_name = model.model_name
        
        # Vérifier si déjà enregistré
        if model_name in self._models:
            logger.warning(f"⚠️  Modèle '{model_name}' déjà enregistré, écrasement")
        
        # Enregistrer
        self._models[model_name] = model
        logger.info(
            f"✓ Modèle enregistré: {model_name} "
            f"v{model.model_version} by {model.author}"
        )
        
        # Définir comme défaut si demandé ou si c'est le premier
        if set_as_default or self._default_model is None:
            self._default_model = model_name
            logger.info(f"  → Défini comme modèle par défaut")
    
    def get(self, model_name: str) -> Optional[BaseMLModel]:
        """
        Récupère un modèle par son nom.
        
        Args:
            model_name: Nom du modèle
        
        Returns:
            Instance du modèle ou None si non trouvé
        """
        return self._models.get(model_name)
    
    def get_default(self) -> Optional[BaseMLModel]:
        """
        Retourne le modèle par défaut.
        
        Returns:
            Instance du modèle par défaut ou None
        """
        if self._default_model:
            return self._models.get(self._default_model)
        return None
    
    def list_models(self) -> Dict[str, Dict]:
        """
        Liste tous les modèles disponibles avec leurs métadonnées.
        
        Returns:
            Dict {model_name: model_info}
        """
        return {
            name: {
                **model.get_info(),
                "is_default": name == self._default_model
            }
            for name, model in self._models.items()
        }
    
    def get_model_names(self) -> List[str]:
        """
        Retourne la liste des noms de modèles disponibles.
        
        Returns:
            Liste des noms
        """
        return list(self._models.keys())
    
    def unregister(self, model_name: str) -> bool:
        """
        Désenregistre un modèle.
        
        Args:
            model_name: Nom du modèle à retirer
        
        Returns:
            True si retiré, False si non trouvé
        """
        if model_name in self._models:
            del self._models[model_name]
            logger.info(f"✓ Modèle désenregistré: {model_name}")
            
            # Si c'était le défaut, choisir un autre
            if self._default_model == model_name:
                self._default_model = next(iter(self._models.keys()), None)
                if self._default_model:
                    logger.info(f"  → Nouveau défaut: {self._default_model}")
            
            return True
        return False
    
    def clear(self):
        """Vide le registre (utile pour les tests)"""
        self._models.clear()
        self._default_model = None
        logger.info("✓ Registre vidé")
    
    def health_check_all(self) -> Dict[str, Dict]:
        """
        Vérifie la santé de tous les modèles.
        
        Returns:
            Dict {model_name: health_status}
        """
        return {
            name: model.health_check()
            for name, model in self._models.items()
        }
    
    # ============================================================================
    # ENHANCED METHODS FOR HYBRID ARCHITECTURE
    # ============================================================================
    
    def register_detection_model(self, model: BaseMLModel, priority: int = 0):
        """
        Enregistre un modèle de détection avec priorité.
        
        Args:
            model: Instance du modèle de détection
            priority: Priorité (plus élevé = préféré). 0 = fallback
        
        Raises:
            ValueError: Si le modèle est invalide
        """
        if not isinstance(model, BaseMLModel):
            raise ValueError(f"Le modèle doit hériter de BaseMLModel")
        
        model_name = model.model_name
        self._detection_models[model_name] = (model, priority)
        
        # Aussi enregistrer dans le registre général
        self.register(model, set_as_default=False)
        
        # Définir comme primaire si priorité plus élevée
        if (self._primary_detection_model is None or 
            priority > self._detection_models.get(self._primary_detection_model, (None, -1))[1]):
            self._primary_detection_model = model_name
            logger.info(f"✓ Modèle de détection primaire: {model_name} (priorité: {priority})")
        else:
            logger.info(f"✓ Modèle de détection enregistré: {model_name} (priorité: {priority})")
    
    def register_generation_model(self, model: BaseMLModel, set_as_primary: bool = False):
        """
        Enregistre un modèle de génération.
        
        Args:
            model: Instance du modèle de génération
            set_as_primary: Si True, définit comme modèle primaire
        
        Raises:
            ValueError: Si le modèle est invalide
        """
        if not isinstance(model, BaseMLModel):
            raise ValueError(f"Le modèle doit hériter de BaseMLModel")
        
        model_name = model.model_name
        self._generation_models[model_name] = model
        
        # Aussi enregistrer dans le registre général
        self.register(model, set_as_default=False)
        
        # Définir comme primaire si demandé ou si c'est le premier
        if set_as_primary or self._primary_generation_model is None:
            self._primary_generation_model = model_name
            logger.info(f"✓ Modèle de génération primaire: {model_name}")
        else:
            logger.info(f"✓ Modèle de génération enregistré: {model_name}")
    
    def get_detection_model(self) -> Optional[BaseMLModel]:
        """
        Retourne le modèle de détection primaire.
        
        Returns:
            Instance du modèle de détection ou None
        """
        if self._primary_detection_model:
            model, _ = self._detection_models.get(self._primary_detection_model, (None, 0))
            return model
        return None
    
    def get_detection_fallback(self) -> Optional[BaseMLModel]:
        """
        Retourne le modèle de détection fallback (priorité 0).
        
        Returns:
            Instance du modèle fallback ou None
        """
        for model_name, (model, priority) in self._detection_models.items():
            if priority == 0:
                return model
        return None
    
    def get_generation_model(self) -> Optional[BaseMLModel]:
        """
        Retourne le modèle de génération primaire.
        
        Returns:
            Instance du modèle de génération ou None
        """
        if self._primary_generation_model:
            return self._generation_models.get(self._primary_generation_model)
        return None
    
    def get_detection_models_by_priority(self) -> List[tuple[str, BaseMLModel, int]]:
        """
        Retourne tous les modèles de détection triés par priorité (décroissant).
        
        Returns:
            Liste de (model_name, model, priority)
        """
        models = [
            (name, model, priority)
            for name, (model, priority) in self._detection_models.items()
        ]
        return sorted(models, key=lambda x: x[2], reverse=True)


# Instance globale (singleton)
registry = EnhancedModelRegistry()

# Backward compatibility alias
ModelRegistry = EnhancedModelRegistry
