<<<<<<< HEAD
# Dockerfile pour l'API de détection de dépression
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Équipe YANSNET"
LABEL description="API de détection de dépression avec LLM"
LABEL version="1.0.0"
=======
# Dockerfile unifié pour l'API ETSIA ML - Support CPU/GPU automatique
# Utilise une image de base avec support CUDA optionnel
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

# Métadonnées
LABEL maintainer="Équipe ETSIA"
LABEL description="API de détection de dépression avec modèles YANSNET LLM et HateComment BERT"
LABEL version="1.1.0"
>>>>>>> cda1f63ffa39c1344ee5c876a2dfb835c641bbf5

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
<<<<<<< HEAD
    PIP_DISABLE_PIP_VERSION_CHECK=1
=======
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TRANSFORMERS_CACHE=/app/.cache/transformers \
    HF_HOME=/app/.cache/huggingface

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Installation conditionnelle de Python pour les images CUDA
RUN if [ -f /usr/bin/python3.11 ]; then \
        ln -sf /usr/bin/python3.11 /usr/bin/python || true; \
    fi
>>>>>>> cda1f63ffa39c1344ee5c876a2dfb835c641bbf5

# Répertoire de travail
WORKDIR /app

<<<<<<< HEAD
# Copier requirements et installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

=======
# Créer les dossiers de cache
RUN mkdir -p /app/.cache/transformers /app/.cache/huggingface

# Copier requirements et installer dépendances
COPY requirements.txt .
COPY app/services/hatecomment_bert/requirements.txt ./hatecomment_requirements.txt

# Installer les dépendances de base
RUN pip install --no-cache-dir -r requirements.txt

# Installer PyTorch avec support CPU (pour production légère)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Installer les dépendances spécifiques HateComment BERT
RUN pip install --no-cache-dir -r hatecomment_requirements.txt

>>>>>>> cda1f63ffa39c1344ee5c876a2dfb835c641bbf5
# Copier le code de l'application
COPY app/ ./app/

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exposer le port
EXPOSE 8000

<<<<<<< HEAD
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
=======
# Health check amélioré
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage avec optimisations
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
>>>>>>> cda1f63ffa39c1344ee5c876a2dfb835c641bbf5
