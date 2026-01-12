from transformers import AutoProcessor, ShieldGemma2ForImageClassification
from PIL import Image
import torch
from app.services.model_censure.hf_config import HF_MODEL_REPO
# Charger modèle et processeur
processor = AutoProcessor.from_pretrained(HF_MODEL_REPO)
model = ShieldGemma2ForImageClassification.from_pretrained(HF_MODEL_REPO)
model.eval()


def predict_image(image: Image.Image):
    inputs = processor(images=[image.convert("RGB")], return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    # Résultats : dictionnaire contenant les scores pour chaque type de contenu
    results = {}
    for key in outputs.probabilities:
        scores = outputs.probabilities[key][0]
        results[key] = {
            "Safe": round(scores[0].item() * 100, 2),
            "Violation": round(scores[1].item() * 100, 2),
            "Prediction": "Violation" if scores[1] > scores[0] else "Safe"
        }

    return results

