"""
Qwen 2.5 1.5B Depression Detection Service

Uses Ollama to run Qwen 2.5 1.5B for depression detection with improved reasoning.
"""
from app.services.qwen_depression.qwen_depression_model import QwenDepressionModel

__all__ = ["QwenDepressionModel"]
