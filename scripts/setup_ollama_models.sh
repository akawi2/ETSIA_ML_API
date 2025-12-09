#!/bin/bash
# Script pour télécharger les modèles Ollama nécessaires
# Usage: ./scripts/setup_ollama_models.sh

set -e

echo "🚀 Configuration des modèles Ollama..."

# Vérifier si Ollama est accessible
OLLAMA_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
echo "📡 Vérification de la connexion à Ollama ($OLLAMA_URL)..."

max_retries=30
retry_count=0
while ! curl -s "$OLLAMA_URL/api/tags" > /dev/null; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        echo "❌ Impossible de se connecter à Ollama après $max_retries tentatives"
        exit 1
    fi
    echo "⏳ En attente d'Ollama... ($retry_count/$max_retries)"
    sleep 2
done

echo "✅ Ollama est accessible"

# Télécharger Qwen 2.5 1.5B pour la détection de dépression
echo ""
echo "📥 Téléchargement de Qwen 2.5 1.5B (modèle de détection)..."
docker exec ollama-server ollama pull qwen2.5:1.5b

# Télécharger Llama 3.2 3B pour la génération de contenu
echo ""
echo "📥 Téléchargement de Llama 3.2 3B (génération de contenu)..."
docker exec ollama-server ollama pull llama3.2:3b

# Télécharger Llama 3.2 1B pour le fallback
echo ""
echo "📥 Téléchargement de Llama 3.2 1B (fallback)..."
docker exec ollama-server ollama pull llama3.2:1b

# Vérifier les modèles installés
echo ""
echo "📋 Modèles Ollama installés:"
docker exec ollama-server ollama list

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "Modèles disponibles:"
echo "  - qwen2.5:1.5b    → Détection de dépression (200-500ms)"
echo "  - llama3.2:3b     → Génération de contenu (5-15s)"
echo "  - llama3.2:1b     → Fallback (2-5s)"
