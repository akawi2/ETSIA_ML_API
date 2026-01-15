from transformers import pipeline
from PIL import Image
import torch
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Utiliser un modèle NSFW plus simple et stable
# Alternative à ShieldGemma2 qui a des problèmes d'inférence
try:
    # Modèle CLIP-based pour détection NSFW (plus léger et stable)
    nsfw_detector = pipeline(
        "image-classification",
        model="Falconsai/nsfw_image_detection",
        device=-1  # CPU
    )
    logger.info("✓ Modèle NSFW (Falconsai) chargé avec succès")
except Exception as e:
    logger.error(f"Erreur chargement modèle NSFW: {e}")
    nsfw_detector = None


def predict_image(image: Image.Image):
    """
    Détecte le contenu NSFW dans une image
    
    Args:
        image: Image PIL en RGB
        
    Returns:
        dict: Résultats avec scores Safe/NSFW
    """
    if nsfw_detector is None:
        raise RuntimeError("Modèle NSFW non disponible")
    
    # Convertir en RGB si nécessaire
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Prédiction
    results = nsfw_detector(image)
    
    # Formater les résultats
    # Le modèle retourne une liste de labels avec scores
    formatted_results = {}
    
    for result in results:
        label = result['label']
        score = result['score'] * 100
        
        if label.lower() in ['nsfw', 'porn', 'hentai', 'sexy']:
            formatted_results['NSFW Content'] = {
                "Safe": round(100 - score, 2),
                "Violation": round(score, 2),
                "Prediction": "Violation" if score > 50 else "Safe"
            }
        elif label.lower() in ['normal', 'safe', 'neutral']:
            formatted_results['General Content'] = {
                "Safe": round(score, 2),
                "Violation": round(100 - score, 2),
                "Prediction": "Safe" if score > 50 else "Violation"
            }
    
    # Si pas de résultats, considérer comme safe
    if not formatted_results:
        formatted_results['General Content'] = {
            "Safe": 95.0,
            "Violation": 5.0,
            "Prediction": "Safe"
        }
    
    return formatted_results


