# ============================================
# Script de Monitoring - ETSIA ML API
# ============================================

param(
    [switch]$Errors,
    [switch]$Performance,
    [switch]$Continuous
)

function Show-Status {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  ETSIA ML API - Status" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Status des services
    Write-Host "Services:" -ForegroundColor Yellow
    docker-compose ps
    
    Write-Host "`nSante de l'API:" -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -UseBasicParsing -TimeoutSec 5
        Write-Host "  [OK] API: $($health.status)" -ForegroundColor Green
        Write-Host "  [OK] Version: $($health.version)" -ForegroundColor Green
        Write-Host "  [OK] Modeles: $($health.models.total)" -ForegroundColor Green
    } catch {
        Write-Host "  [ERREUR] API non accessible" -ForegroundColor Red
    }
}

function Show-Errors {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Dernieres Erreurs (20)" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    docker-compose logs --tail=100 api | Select-String -Pattern "ERROR" | Select-Object -First 20
}

function Show-Warnings {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Dernieres Alertes (20)" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    docker-compose logs --tail=100 api | Select-String -Pattern "(WARNING|ALERTE)" | Select-Object -First 20
}

function Show-Performance {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Performance" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Utilisation des ressources
    Write-Host "Utilisation des ressources:" -ForegroundColor Yellow
    docker stats --no-stream etsia-ml-api-cpu etsia-postgres etsia-redis ollama-server
    
    # Test de latence
    Write-Host "`nTest de latence:" -ForegroundColor Yellow
    
    Write-Host "  - Health check..." -NoNewline
    $time = Measure-Command {
        Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -UseBasicParsing -TimeoutSec 10 | Out-Null
    }
    Write-Host " $([math]::Round($time.TotalMilliseconds, 0))ms" -ForegroundColor $(if ($time.TotalMilliseconds -lt 1000) { "Green" } else { "Yellow" })
    
    Write-Host "  - Prediction..." -NoNewline
    $time = Measure-Command {
        $body = @{text = "Test"} | ConvertTo-Json
        Invoke-RestMethod -Uri "http://localhost:8001/api/v1/predict?model_name=qwen-depression" `
            -Method Post -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 30 | Out-Null
    }
    Write-Host " $([math]::Round($time.TotalMilliseconds, 0))ms" -ForegroundColor $(if ($time.TotalMilliseconds -lt 3000) { "Green" } else { "Yellow" })
    
    Write-Host "  - Recommandations..." -NoNewline
    $time = Measure-Command {
        Invoke-RestMethod -Uri "http://localhost:8001/recommend?userId=1" -Method Get -UseBasicParsing -TimeoutSec 10 | Out-Null
    }
    Write-Host " $([math]::Round($time.TotalMilliseconds, 0))ms" -ForegroundColor $(if ($time.TotalMilliseconds -lt 500) { "Green" } else { "Yellow" })
}

function Show-Metrics {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  Metriques" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    try {
        $metrics = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/metrics/summary" -Method Get -UseBasicParsing
        Write-Host "Periode: Dernieres 24h" -ForegroundColor Yellow
        Write-Host "  - Total predictions: $($metrics.total_predictions)" -ForegroundColor White
        Write-Host "  - Total erreurs: $($metrics.total_errors)" -ForegroundColor White
        Write-Host "  - Alertes actives: $($metrics.active_alerts)" -ForegroundColor White
    } catch {
        Write-Host "  [ERREUR] Impossible de recuperer les metriques" -ForegroundColor Red
    }
}

function Show-Continuous {
    while ($true) {
        Clear-Host
        Show-Status
        Show-Errors
        Show-Performance
        Show-Metrics
        
        Write-Host "`n[Actualisation dans 30s... Ctrl+C pour arreter]" -ForegroundColor Gray
        Start-Sleep -Seconds 30
    }
}

# ============================================
# Execution
# ============================================

if ($Continuous) {
    Show-Continuous
} elseif ($Errors) {
    Show-Status
    Show-Errors
    Show-Warnings
} elseif ($Performance) {
    Show-Status
    Show-Performance
    Show-Metrics
} else {
    # Mode par defaut: tout afficher
    Show-Status
    Show-Errors
    Show-Performance
    Show-Metrics
}

Write-Host ""
