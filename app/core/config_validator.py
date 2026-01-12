"""
Configuration validator for hybrid architecture
"""
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_configuration() -> bool:
    """
    Valide la configuration au démarrage.
    
    Returns:
        True si la configuration est valide, False sinon
    """
    errors = []
    warnings = []
    
    # Validate detection provider
    valid_detection_providers = ["camembert", "xlm-roberta", "llama"]
    if settings.DETECTION_PROVIDER not in valid_detection_providers:
        errors.append(
            f"DETECTION_PROVIDER invalide: {settings.DETECTION_PROVIDER}. "
            f"Valeurs acceptées: {valid_detection_providers}"
        )
    
    # Validate generation provider
    valid_generation_providers = ["ollama", "gpt", "claude"]
    if settings.GENERATION_PROVIDER not in valid_generation_providers:
        errors.append(
            f"GENERATION_PROVIDER invalide: {settings.GENERATION_PROVIDER}. "
            f"Valeurs acceptées: {valid_generation_providers}"
        )
    
    # Check API keys for external providers
    if settings.GENERATION_PROVIDER == "gpt" and not settings.OPENAI_API_KEY:
        warnings.append("GENERATION_PROVIDER=gpt mais OPENAI_API_KEY non définie")
    
    if settings.GENERATION_PROVIDER == "claude" and not settings.ANTHROPIC_API_KEY:
        warnings.append("GENERATION_PROVIDER=claude mais ANTHROPIC_API_KEY non définie")
    
    # Validate latency settings
    if settings.MAX_DETECTION_LATENCY_MS <= 0:
        errors.append("MAX_DETECTION_LATENCY_MS doit être > 0")
    
    if settings.MAX_GENERATION_LATENCY_S <= 0:
        errors.append("MAX_GENERATION_LATENCY_S doit être > 0")
    
    # Log results
    if errors:
        logger.error("❌ Erreurs de configuration:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    if warnings:
        logger.warning("⚠️  Avertissements de configuration:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    logger.info("✓ Configuration validée avec succès")
    logger.info(f"  - Detection: {settings.DETECTION_PROVIDER}")
    logger.info(f"  - Generation: {settings.GENERATION_PROVIDER}")
    logger.info(f"  - Fallback: {'activé' if settings.ENABLE_FALLBACK else 'désactivé'}")
    logger.info(f"  - Metrics: {'activés' if settings.ENABLE_METRICS else 'désactivés'}")
    
    return True


def get_configuration_summary() -> dict:
    """
    Retourne un résumé de la configuration actuelle.
    
    Returns:
        Dict avec les paramètres de configuration
    """
    return {
        "architecture": "hybrid",
        "detection": {
            "provider": settings.DETECTION_PROVIDER,
            "max_latency_ms": settings.MAX_DETECTION_LATENCY_MS,
            "fallback_enabled": settings.ENABLE_FALLBACK
        },
        "generation": {
            "provider": settings.GENERATION_PROVIDER,
            "max_latency_s": settings.MAX_GENERATION_LATENCY_S
        },
        "monitoring": {
            "metrics_enabled": settings.ENABLE_METRICS,
            "latency_logging": settings.LOG_LATENCY
        },
        "models": {
            "camembert": settings.CAMEMBERT_MODEL,
            "xlm_roberta": settings.XLM_ROBERTA_MODEL,
            "ollama_detection": settings.OLLAMA_DETECTION_MODEL,
            "ollama_generation": settings.OLLAMA_GENERATION_MODEL
        }
    }
