"""
Core - Infrastructure pour le système multi-modèles YANSNET
"""
from .base_model import BaseMLModel
from .model_registry import ModelRegistry, registry

__all__ = ['BaseMLModel', 'ModelRegistry', 'registry']
