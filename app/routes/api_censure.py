from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
import time
from typing import List

import torch
from transformers import ViTForImageClassification, ViTImageProcessor
from app.services.model_censure.hf_config import HF_MODEL_REPO

app = FastAPI()

# Chargement du modèle et du processor
processor = ViTImageProcessor.from_pretrained(HF_MODEL_REPO)
model = ViTForImageClassification.from_pretrained(HF_MODEL_REPO)
model.eval()

label_mapping = {0: "Safe", 1: "NSFW"}

@app.post("/predict/")
async def predict_images(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")

        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze().tolist()
            predicted_class = logits.argmax(-1).item()
            predicted_label = label_mapping[predicted_class]

        results.append({
            "filename": file.filename,
            "prediction": predicted_label,
            "confidence": {
                "Safe": round(probs[0] * 100, 2),
                "NSFW": round(probs[1] * 100, 2)
            }
        })

    # Encapsulation dans un dictionnaire pour que JSONResponse soit valide
    return JSONResponse(content={"results": results})
