"""
Routes
"""
from .api import router, content_router
from .image_api import router as image_router

__all__ = ['router', 'image_router', 'content_router']
