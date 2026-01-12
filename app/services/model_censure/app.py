#from transformers import ViTForImageClassification, ViTImageProcessor
from transformers.models.vit import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch
from app.services.model_censure.hf_config import HF_MODEL_REPO, HF_TOKEN
import sys
import streamlit as st
import transformers
import time

print("Python executable:", sys.executable)
print("Transformers version:", transformers.__version__)


@st.cache_resource
def load_model():
    st.text("Chargement du modèle...")
    processor = ViTImageProcessor.from_pretrained(HF_MODEL_REPO)
    model = ViTForImageClassification.from_pretrained(HF_MODEL_REPO)
    model.eval()
    st.text("Modèle chargé.")
    return processor, model


def predict_image(image: Image.Image):
    processor, model = load_model()
    inputs = processor(images=image.convert("RGB"), return_tensors="pt")

    with torch.no_grad():
        logits = model(**inputs).logits
        probabilities = torch.softmax(logits, dim=-1).squeeze().tolist()

    label_mapping = {0: "Safe", 1: "NSFW"}

    results = {
        "Safe": round(probabilities[0] * 100, 2),
        "NSFW": round(probabilities[1] * 100, 2)
    }

    predicted_class = logits.argmax(-1).item()
    predicted_label = label_mapping[predicted_class]

    return predicted_label, results


st.title("🔍 Détection Image Néfaste - ETSIA CENSURE")

uploaded_file = st.file_uploader("Upload une image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Image chargée", use_column_width=True)

    if st.button("Analyser"):
        with st.spinner("Analyse en cours..."):
            start_time = time.time()  # ⏱️ début
            predicted_label, results = predict_image(image)
            end_time = time.time()  # ⏱️ fin
            inference_time = round(end_time - start_time, 2)  # Durée en secondes

        st.success(f"Résultat principal : **{predicted_label}**")
        st.write(f"🟢 SAFE : {results['Safe']}%")
        st.write(f"🔴 Not SAFE : {results['NSFW']}%")
        st.info(f"⏱️ Temps de réponse du modèle : {inference_time} secondes")
