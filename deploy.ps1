# ============================================
# Script de Deploiement Rapide - ETSIA ML API
# ============================================

param(
    [switch]$SkipBuild,
    [switch]$SkipModels,
    [switch]$SkipTests,
    [switch]$Clean
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ETSIA ML API - Deploiement Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# Verification Docker
# ============================================
Write-Host "[1/7] Verification Docker..." -ForegroundColor Green

try {
    docker --version | Out-Null
    docker ps | Out-Null
    Write-Host "  OK Docker OK" -ForegroundColor Green
} catch {
    Write-Host "  X Docker non disponible" -ForegroundColor Red
    Write-Host "  Lancez Docker Desktop et reessayez" -ForegroundColor Yellow
    exit 1
}

# ============================================
# Verification .env
# ============================================
Write-Host "[2/7] Verification configuration..." -ForegroundColor Green

if (-not (Test-Path ".env")) {
    Write-Host "  ! Fichier .env manquant" -ForegroundColor Yellow
    Write-Host "  Copie de .env.example vers .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  OK Fichier .env cree" -ForegroundColor Green
    Write-Host "  ! Configurez vos cles API dans .env avant de continuer" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continuer quand meme ? (o/N)"
    if ($continue -ne "o" -and $continue -ne "O") {
        exit 0
    }
} else {
    Write-Host "  OK Fichier .env trouve" -ForegroundColor Green
}

# ============================================
# Nettoyage (optionnel)
# ============================================
if ($Clean) {
    Write-Host "[3/7] Nettoyage des anciens containers..." -ForegroundColor Green
    docker-compose --profile ml down -v
    Write-Host "  OK Nettoyage termine" -ForegroundColor Green
} else {
    Write-Host "[3/7] Nettoyage ignore (utilisez -Clean pour nettoyer)" -ForegroundColor Yellow
}

# ============================================
# Build des images
# ============================================
if (-not $SkipBuild) {
    Write-Host "[4/7] Build des images Docker..." -ForegroundColor Green
    Write-Host "  Cela peut prendre 10-15 minutes..." -ForegroundColor Yellow
    
    $buildStart = Get-Date
    docker-compose --profile ml build
    $buildEnd = Get-Date
    $buildDuration = ($buildEnd - $buildStart).TotalMinutes
    
    Write-Host "  OK Build termine en $([math]::Round($buildDuration, 1)) min" -ForegroundColor Green
} else {
    Write-Host "[4/7] Build ignore (utilisez sans -SkipBuild pour rebuilder)" -ForegroundColor Yellow
}

# ============================================
# Demarrage des services
# ============================================
Write-Host "[5/7] Demarrage des services..." -ForegroundColor Green

docker-compose --profile ml up -d

Write-Host "  OK Services demarres" -ForegroundColor Green
Write-Host ""
Write-Host "  Attente du demarrage complet..." -ForegroundColor Yellow

# Attendre PostgreSQL
Write-Host "  - PostgreSQL..." -NoNewline
$retries = 0
while ($retries -lt 30) {
    $status = docker-compose ps postgres 2>$null | Select-String "Up"
    if ($status) {
        Write-Host " OK" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
    $retries++
}

# Attendre Redis
Write-Host "  - Redis..." -NoNewline
$retries = 0
while ($retries -lt 30) {
    $status = docker-compose ps redis 2>$null | Select-String "Up"
    if ($status) {
        Write-Host " OK" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
    $retries++
}

# Attendre Ollama
Write-Host "  - Ollama..." -NoNewline
$retries = 0
while ($retries -lt 30) {
    $status = docker-compose ps ollama 2>$null | Select-String "Up"
    if ($status) {
        Write-Host " OK" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 2
    $retries++
}

# Attendre GA4-Bridge
Write-Host "  - GA4-Bridge..." -NoNewline
$retries = 0
while ($retries -lt 30) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host " OK" -ForegroundColor Green
            break
        }
    } catch {
        # Ignorer
    }
    Start-Sleep -Seconds 2
    $retries++
}

# ============================================
# Telechargement des modeles Ollama
# ============================================
if (-not $SkipModels) {
    Write-Host "[6/7] Telechargement des modeles Ollama..." -ForegroundColor Green
    Write-Host "  Cela peut prendre 10-15 minutes..." -ForegroundColor Yellow
    Write-Host ""
    
    # Qwen 2.5 1.5B
    Write-Host "  - qwen2.5:1.5b (~1 GB)..." -NoNewline
    docker exec ollama-server ollama pull qwen2.5:1.5b 2>&1 | Out-Null
    Write-Host " OK" -ForegroundColor Green
    
    # Llama 3.2 1B
    Write-Host "  - llama3.2:1b (~700 MB)..." -NoNewline
    docker exec ollama-server ollama pull llama3.2:1b 2>&1 | Out-Null
    Write-Host " OK" -ForegroundColor Green
    
    # Llama 3.2 3B
    Write-Host "  - llama3.2:3b (~2 GB)..." -NoNewline
    docker exec ollama-server ollama pull llama3.2:3b 2>&1 | Out-Null
    Write-Host " OK" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "  Modeles installes:" -ForegroundColor Yellow
    docker exec ollama-server ollama list
} else {
    Write-Host "[6/7] Telechargement modeles ignore (utilisez sans -SkipModels)" -ForegroundColor Yellow
}

# ============================================
# Attente de l'API
# ============================================
Write-Host "[7/7] Attente de l'API ML..." -ForegroundColor Green
Write-Host "  L'API telecharge les modeles HuggingFace..." -ForegroundColor Yellow
Write-Host "  Cela peut prendre 5-10 minutes" -ForegroundColor Yellow
Write-Host ""

$retries = 0
$maxRetries = 60
while ($retries -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "  OK API prete !" -ForegroundColor Green
            break
        }
    } catch {
        # Ignorer
    }
    
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 10
    $retries++
}

Write-Host ""

if ($retries -eq $maxRetries) {
    Write-Host "  ! L'API n'a pas demarre dans le temps imparti" -ForegroundColor Yellow
    Write-Host "  Verifiez les logs: docker-compose logs -f api" -ForegroundColor Yellow
} else {
    # ============================================
    # Tests de l'API
    # ============================================
    if (-not $SkipTests) {
        Write-Host ""
        Write-Host "Tests rapides..." -ForegroundColor Green
        
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
            Write-Host "  OK Health check OK" -ForegroundColor Green
            
            $prediction = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict" -Method Post -Body (@{text="Je me sens bien"} | ConvertTo-Json) -ContentType "application/json"
            Write-Host "  OK Prediction OK" -ForegroundColor Green
        } catch {
            Write-Host "  ! Certains tests ont echoue" -ForegroundColor Yellow
        }
    }
}

# ============================================
# Resume final
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deploiement Termine !" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Services disponibles:" -ForegroundColor Yellow
Write-Host "  - API ML          : http://localhost:8001" -ForegroundColor White
Write-Host "  - Documentation   : http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - GA4-Bridge      : http://localhost:5000" -ForegroundColor White
Write-Host "  - Ollama          : http://localhost:11434" -ForegroundColor White
Write-Host ""

Write-Host "Commandes utiles:" -ForegroundColor Yellow
Write-Host "  - Tests complets  : .\test_api.ps1" -ForegroundColor White
Write-Host "  - Voir les logs   : docker-compose logs -f api" -ForegroundColor White
Write-Host "  - Arreter         : docker-compose --profile ml down" -ForegroundColor White
Write-Host "  - Redemarrer      : docker-compose --profile ml restart api" -ForegroundColor White
Write-Host "  - Status          : docker-compose ps" -ForegroundColor White
Write-Host ""

Write-Host "Options de deploiement:" -ForegroundColor Yellow
Write-Host "  - -SkipBuild      : Ignorer le build des images" -ForegroundColor White
Write-Host "  - -SkipModels     : Ignorer le telechargement des modeles Ollama" -ForegroundColor White
Write-Host "  - -SkipTests      : Ignorer les tests rapides" -ForegroundColor White
Write-Host "  - -Clean          : Nettoyer les anciens containers avant" -ForegroundColor White
Write-Host ""

Write-Host "OK Bon developpement !" -ForegroundColor Green
