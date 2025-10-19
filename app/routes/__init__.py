"""
Routes
"""
from .api import router
from .image_api import router as image_router

__all__ = ['router', 'image_router']
