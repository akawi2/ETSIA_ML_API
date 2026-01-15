"""
Helpers pour gérer les appels synchrones et asynchrones de manière transparente
"""
import asyncio


async def call_model_predict(model, **kwargs):
    """
    Appelle model.predict() de manière adaptative (sync ou async).
    
    Args:
        model: Instance du modèle
        **kwargs: Arguments à passer à predict()
    
    Returns:
        Résultat de la prédiction
    """
    predict_method = model.predict
    
    # Vérifier si la méthode est asynchrone
    if asyncio.iscoroutinefunction(predict_method):
        return await predict_method(**kwargs)
    else:
        # Méthode synchrone, l'appeler directement
        return predict_method(**kwargs)


async def call_model_health_check(model):
    """
    Appelle model.health_check() de manière adaptative (sync ou async).
    
    Args:
        model: Instance du modèle
    
    Returns:
        Résultat du health check
    """
    health_check_method = model.health_check
    
    # Vérifier si la méthode est asynchrone
    if asyncio.iscoroutinefunction(health_check_method):
        return await health_check_method()
    else:
        # Méthode synchrone, l'appeler directement
        return health_check_method()


async def call_model_method(model, method_name: str, **kwargs):
    """
    Appelle une méthode du modèle de manière adaptative (sync ou async).
    
    Args:
        model: Instance du modèle
        method_name: Nom de la méthode à appeler
        **kwargs: Arguments à passer à la méthode
    
    Returns:
        Résultat de l'appel
    """
    method = getattr(model, method_name)
    
    # Vérifier si la méthode est asynchrone
    if asyncio.iscoroutinefunction(method):
        return await method(**kwargs)
    else:
        # Méthode synchrone, l'appeler directement
        return method(**kwargs)
