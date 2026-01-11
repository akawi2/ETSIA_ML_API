# Dockerfile unifié pour l'API ETSIA ML - Support CPU/GPU automatique
# Utilise une image de base avec support CUDA optionnel
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}

# Métadonnées
LABEL maintainer="Équipe ETSIA"
LABEL description="API de détection de dépression avec modèles ML hybrides"
LABEL version="2.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
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

# Répertoire de travail
WORKDIR /app

# Créer les dossiers de cache
RUN mkdir -p /app/.cache/transformers /app/.cache/huggingface

# Copier requirements et installer dépendances
COPY requirements.txt .

# Augmenter le timeout pip et installer les dépendances en plusieurs étapes
# Étape 1: Dépendances légères
RUN pip install --default-timeout=300 --no-cache-dir \
    fastapi>=0.109.0 \
    uvicorn[standard]>=0.27.0 \
    pydantic>=2.5.0 \
    pydantic-settings>=2.1.0 \
    python-dotenv>=1.0.0 \
    python-multipart>=0.0.6 \
    httpx>=0.26.0 \
    asyncpg>=0.29.0 \
    psycopg2-binary>=2.9.9 \
    redis>=5.0.0 \
    pytest>=7.4.0 \
    pytest-asyncio>=0.21.0 \
    pytest-cov>=4.1.0 \
    hypothesis>=6.92.0 \
    openai>=1.10.0 \
    anthropic>=0.18.0 \
    requests>=2.31.0

# Étape 2: Packages lourds (numpy, Pillow, pandas)
RUN pip install --default-timeout=300 --no-cache-dir \
    numpy>=1.24.0 \
    Pillow>=10.0.0 \
    pandas>=2.0.0

# Étape 3: PyTorch CPU
RUN pip install --default-timeout=300 --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu

# Étape 4: Transformers et dépendances NLP (dépend de torch)
RUN pip install --default-timeout=300 --no-cache-dir \
    transformers>=4.30.0 \
    sentencepiece>=0.1.99 \
    protobuf>=3.20.0

# Copier le code de l'application
COPY app/ ./app/

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exposer le port
EXPOSE 8000

# Health check amélioré
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande de démarrage avec optimisations
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
