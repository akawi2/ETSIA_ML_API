"""
Routes
"""
from .api import router
from .censure_api import router as censure_router

__all__ = ['router', 'censure_router']
