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
    DETECTION_PROVIDER: str = "camembert"  # camembert, xlm-roberta, qwen, llama
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
    # QWEN SETTINGS (Ollama-based Detection - Better Reasoning)
    # ============================================================================
    QWEN_DETECTION_MODEL: str = "qwen2.5:1.5b"
    QWEN_MAX_LENGTH: int = 2048
    
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
    # Note: Actual CamemBERT CPU latency is 600-700ms (still 50-200x faster than Llama 8B)
    MAX_DETECTION_LATENCY_MS: int = 1000  # Adjusted for actual CPU performance
    MAX_QWEN_DETECTION_LATENCY_MS: int = 1000  # Qwen 2.5 1.5B latency target
    MAX_GENERATION_LATENCY_S: int = 30
    ENABLE_FALLBACK: bool = True
    
    # ============================================================================
    # POSTGRESQL SETTINGS (Metrics Database)
    # ============================================================================
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "etsia"
    POSTGRES_PASSWORD: str = "etsia_secure_password"
    POSTGRES_DB: str = "etsia_metrics"
    
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
