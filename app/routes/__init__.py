"""
Routes
"""
from .api import router, content_router
from .image_api import router as image_router
from .hatecomment_api import router as hatecomment_router
from .recommendation_api import router as recommendation_router


__all__ = ['router', 'image_router', 'hatecomment_router', 'content_router', 'recommendation_router']
