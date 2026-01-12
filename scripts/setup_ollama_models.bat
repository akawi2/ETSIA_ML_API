@echo off
REM Script pour télécharger les modèles Ollama nécessaires (Windows)
REM Usage: scripts\setup_ollama_models.bat

echo 🚀 Configuration des modèles Ollama...

REM Vérifier si Ollama est accessible
set OLLAMA_URL=http://localhost:11434
echo 📡 Vérification de la connexion à Ollama (%OLLAMA_URL%)...

:wait_ollama
curl -s %OLLAMA_URL%/api/tags >nul 2>&1
if errorlevel 1 (
    echo ⏳ En attente d'Ollama...
    timeout /t 2 /nobreak >nul
    goto wait_ollama
)

echo ✅ Ollama est accessible

REM Télécharger Qwen 2.5 1.5B pour la détection de dépression
echo.
echo 📥 Téléchargement de Qwen 2.5 1.5B (modèle de détection)...
docker exec ollama-server ollama pull qwen2.5:1.5b

REM Télécharger Llama 3.2 3B pour la génération de contenu
echo.
echo 📥 Téléchargement de Llama 3.2 3B (génération de contenu)...
docker exec ollama-server ollama pull llama3.2:3b

REM Télécharger Llama 3.2 1B pour le fallback
echo.
echo 📥 Téléchargement de Llama 3.2 1B (fallback)...
docker exec ollama-server ollama pull llama3.2:1b

REM Vérifier les modèles installés
echo.
echo 📋 Modèles Ollama installés:
docker exec ollama-server ollama list

echo.
echo ✅ Configuration terminée!
echo.
echo Modèles disponibles:
echo   - qwen2.5:1.5b    → Détection de dépression (200-500ms)
echo   - llama3.2:3b     → Génération de contenu (5-15s)
echo   - llama3.2:1b     → Fallback (2-5s)

pause
