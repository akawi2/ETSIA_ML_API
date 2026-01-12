# Script de déploiement Docker pour ETSIA ML API (Windows PowerShell)

param(
    [Parameter(Position=0)]
    [ValidateSet("cpu", "gpu", "stop", "logs", "clean", "health", "help")]
    [string]$Action = "cpu"
)

# Fonction d'affichage coloré
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "🚀 Déploiement ETSIA ML API" "Blue"
Write-ColorOutput "==================================" "Blue"

# Vérifier si Docker est installé
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-ColorOutput "❌ Docker n'est pas installé" "Red"
    exit 1
}

# Vérifier si Docker Compose est installé
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-ColorOutput "❌ Docker Compose n'est pas installé" "Red"
    exit 1
}

# Fonction d'aide
function Show-Help {
    Write-ColorOutput "Usage: .\docker-deploy.ps1 [OPTION]" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Options:" "White"
    Write-ColorOutput "  cpu     Déployer avec support CPU uniquement (défaut)" "White"
    Write-ColorOutput "  gpu     Déployer avec support GPU (NVIDIA CUDA requis)" "White"
    Write-ColorOutput "  stop    Arrêter tous les services" "White"
    Write-ColorOutput "  logs    Afficher les logs" "White"
    Write-ColorOutput "  clean   Nettoyer les images et volumes" "White"
    Write-ColorOutput "  help    Afficher cette aide" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Exemples:" "White"
    Write-ColorOutput "  .\docker-deploy.ps1 cpu          # Déploiement CPU" "White"
    Write-ColorOutput "  .\docker-deploy.ps1 gpu          # Déploiement GPU" "White"
    Write-ColorOutput "  .\docker-deploy.ps1 stop         # Arrêter les services" "White"
}

# Fonction de déploiement CPU
function Deploy-CPU {
    Write-ColorOutput "📦 Déploiement avec support CPU..." "Yellow"
    
    try {
        # Utiliser le Dockerfile unifié avec image CPU
        docker build --build-arg BASE_IMAGE=python:3.11-slim -t etsia-ml-api:cpu .
        docker run -d --name etsia-ml-api-cpu -p 8000:8000 --env-file .env etsia-ml-api:cpu
        Write-ColorOutput "✅ Déploiement CPU terminé" "Green"
        Write-ColorOutput "🌐 API disponible sur: http://localhost:8000" "Blue"
        Write-ColorOutput "📚 Documentation: http://localhost:8000/docs" "Blue"
    }
    catch {
        Write-ColorOutput "❌ Erreur lors du déploiement CPU: $_" "Red"
        exit 1
    }
}

# Fonction de déploiement GPU
function Deploy-GPU {
    Write-ColorOutput "🚀 Déploiement avec support GPU..." "Yellow"
    
    # Vérifier si NVIDIA Docker est disponible
    try {
        $null = docker run --rm --gpus all nvidia/cuda:12.1-base-ubuntu22.04 nvidia-smi 2>$null
    }
    catch {
        Write-ColorOutput "❌ Support GPU non disponible. Vérifiez:" "Red"
        Write-ColorOutput "  - NVIDIA Docker runtime installé" "Red"
        Write-ColorOutput "  - GPU NVIDIA disponible" "Red"
        Write-ColorOutput "  - Pilotes NVIDIA installés" "Red"
        exit 1
    }
    
    try {
        # Utiliser le Dockerfile unifié avec image GPU
        docker build --build-arg BASE_IMAGE=nvidia/cuda:12.1-runtime-ubuntu22.04 -t etsia-ml-api:gpu .
        docker run -d --name etsia-ml-api-gpu --gpus all -p 8001:8000 --env-file .env etsia-ml-api:gpu
        Write-ColorOutput "✅ Déploiement GPU terminé" "Green"
        Write-ColorOutput "🌐 API disponible sur: http://localhost:8001" "Blue"
        Write-ColorOutput "📚 Documentation: http://localhost:8001/docs" "Blue"
    }
    catch {
        Write-ColorOutput "❌ Erreur lors du déploiement GPU: $_" "Red"
        exit 1
    }
}

# Fonction d'arrêt des services
function Stop-Services {
    Write-ColorOutput "🛑 Arrêt des services..." "Yellow"
    
    # Arrêter les conteneurs par nom
    $containers = @("etsia-ml-api-cpu", "etsia-ml-api-gpu")
    foreach ($container in $containers) {
        $exists = docker ps -a --filter "name=$container" --format "{{.Names}}"
        if ($exists) {
            docker stop $container
            docker rm $container
            Write-ColorOutput "✅ Conteneur $container arrêté et supprimé" "Green"
        }
    }
}

# Fonction d'affichage des logs
function Show-Logs {
    Write-ColorOutput "📋 Logs des services:" "Blue"
    
    # Vérifier quels conteneurs sont actifs
    $cpuRunning = docker ps --filter "name=etsia-ml-api-cpu" --format "{{.Names}}"
    $gpuRunning = docker ps --filter "name=etsia-ml-api-gpu" --format "{{.Names}}"
    
    if ($cpuRunning) {
        Write-ColorOutput "📋 Logs CPU:" "Blue"
        docker logs -f etsia-ml-api-cpu
    } elseif ($gpuRunning) {
        Write-ColorOutput "📋 Logs GPU:" "Blue"
        docker logs -f etsia-ml-api-gpu
    } else {
        Write-ColorOutput "⚠️  Aucun conteneur en cours d'exécution" "Yellow"
    }
}

# Fonction de nettoyage
function Clean-All {
    Write-ColorOutput "🧹 Nettoyage des images et volumes..." "Yellow"
    
    # Arrêter les services d'abord
    Stop-Services
    
    # Supprimer les images ETSIA ML API
    $images = docker images --filter "reference=etsia-ml-api*" -q
    if ($images) {
        docker rmi -f $images
        Write-ColorOutput "✅ Images ETSIA ML API supprimées" "Green"
    }
    
    # Nettoyer les volumes orphelins
    docker volume prune -f
    
    # Nettoyer les images non utilisées
    docker image prune -f
    
    Write-ColorOutput "✅ Nettoyage terminé" "Green"
}

# Fonction de test de santé
function Test-Health {
    Write-ColorOutput "🏥 Vérification de la santé de l'API..." "Blue"
    
    # Tester CPU API
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✅ API CPU: Healthy" "Green"
        }
    }
    catch {
        Write-ColorOutput "❌ API CPU: Non disponible" "Red"
    }
    
    # Tester GPU API
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✅ API GPU: Healthy" "Green"
        }
    }
    catch {
        Write-ColorOutput "⚠️  API GPU: Non disponible" "Yellow"
    }
}

# Traitement des actions
switch ($Action) {
    "cpu" {
        Deploy-CPU
        Start-Sleep -Seconds 10
        Test-Health
    }
    "gpu" {
        Deploy-GPU
        Start-Sleep -Seconds 15
        Test-Health
    }
    "stop" {
        Stop-Services
    }
    "logs" {
        Show-Logs
    }
    "clean" {
        Clean-All
    }
    "health" {
        Test-Health
    }
    "help" {
        Show-Help
    }
    default {
        Write-ColorOutput "❌ Option inconnue: $Action" "Red"
        Show-Help
        exit 1
    }
}
