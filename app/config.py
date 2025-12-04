"""
Configuration de l'application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # ============================================================================
    # HYBRID ARCHITECTURE CONFIGURATION
    # ============================================================================
    
    # Provider selection for different tasks
    DETECTION_PROVIDER: str = "camembert"  # camembert, xlm-roberta, llama
    GENERATION_PROVIDER: str = "ollama"    # ollama, gpt, claude
    
    # ============================================================================
    # CAMEMBERT SETTINGS (Depression Detection)
    # ============================================================================
    CAMEMBERT_MODEL: str = "camembert-base"
    CAMEMBERT_DEVICE: str = "cpu"
    CAMEMBERT_MAX_LENGTH: int = 512
    
    # ============================================================================
    # XLM-ROBERTA SETTINGS (Alternative Detection)
    # ============================================================================
    XLM_ROBERTA_MODEL: str = "xlm-roberta-base"
    XLM_ROBERTA_DEVICE: str = "cpu"
    XLM_ROBERTA_MAX_LENGTH: int = 512
    
    # ============================================================================
    # OLLAMA SETTINGS (Updated for 3B model)
    # ============================================================================
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DETECTION_MODEL: str = "llama3.2:1b"  # Fallback only
    OLLAMA_GENERATION_MODEL: str = "llama3.2:3b"  # Primary for generation
    OLLAMA_MODEL: str = "llama3.2"  # Legacy compatibility
    
    # ============================================================================
    # OPENAI SETTINGS (Optional external provider)
    # ============================================================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # ============================================================================
    # ANTHROPIC SETTINGS (Optional external provider)
    # ============================================================================
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # ============================================================================
    # LEGACY LLM PROVIDER (Backward compatibility)
    # ============================================================================
    LLM_PROVIDER: str = "gpt"  # gpt, claude, local
    
    # ============================================================================
    # PERFORMANCE SETTINGS
    # ============================================================================
    MAX_DETECTION_LATENCY_MS: int = 500
    MAX_GENERATION_LATENCY_S: int = 30
    ENABLE_FALLBACK: bool = True
    
    # ============================================================================
    # MONITORING SETTINGS
    # ============================================================================
    ENABLE_METRICS: bool = True
    LOG_LATENCY: bool = True
    
    # ============================================================================
    # API SETTINGS
    # ============================================================================
    API_TITLE: str = "ETSIA ML API"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "API ML avec architecture hybride optimisée"
    LOG_LEVEL: str = "INFO"
    
    # ============================================================================
    # SECURITY SETTINGS
    # ============================================================================
    API_KEY: Optional[str] = None
    CORS_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale
settings = Settings()
