"""
Routes
"""
from .api import router, content_router
from .image_api import router as image_router
from .hatecomment_api import router as hatecomment_router


__all__ = ['router', 'image_router', 'hatecomment_router', 'content_router']
