# ============================================
# Script de Test - API ETSIA ML
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tests API ETSIA ML" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Fonction pour afficher les resultats
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Uri,
        [object]$Body = $null
    )
    
    Write-Host "Test: $Name" -ForegroundColor Yellow
    Write-Host "  URI: $Method $Uri" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $Uri
            Method = $Method
            TimeoutSec = 30
            UseBasicParsing = $true
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
            $params.ContentType = "application/json"
        }
        
        $startTime = Get-Date
        $response = Invoke-RestMethod @params
        $endTime = Get-Date
        $duration = [math]::Round(($endTime - $startTime).TotalMilliseconds, 0)
        
        Write-Host "  [OK] Succes (${duration}ms)" -ForegroundColor Green
        Write-Host "  Reponse:" -ForegroundColor Gray
        Write-Host ($response | ConvertTo-Json -Depth 5) -ForegroundColor White
        Write-Host ""
        return $true
    } catch {
        Write-Host "  [ERREUR] Echec: $_" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# ============================================
# Tests de base
# ============================================
Write-Host "=== Tests de Base ===" -ForegroundColor Cyan
Write-Host ""

$results = @{}

# Health check
$results."Health Check" = Test-Endpoint `
    -Name "Health Check" `
    -Method "GET" `
    -Uri "http://localhost:8001/health"

# Liste des modeles
$results."Models List" = Test-Endpoint `
    -Name "Liste des Modeles" `
    -Method "GET" `
    -Uri "http://localhost:8001/api/v1/models"

# ============================================
# Tests de detection de depression
# ============================================
Write-Host "=== Tests Detection de Depression ===" -ForegroundColor Cyan
Write-Host ""

# Test avec texte negatif
$results."Depression Detection Negative" = Test-Endpoint `
    -Name "Detection Depression (Texte Negatif)" `
    -Method "POST" `
    -Uri "http://localhost:8001/api/v1/predict" `
    -Body @{
        text = "Je me sens triste et sans espoir, je n'ai plus envie de rien faire"
    }

# Test avec texte positif
$results."Depression Detection Positive" = Test-Endpoint `
    -Name "Detection Depression (Texte Positif)" `
    -Method "POST" `
    -Uri "http://localhost:8001/api/v1/predict" `
    -Body @{
        text = "Je suis tres heureux aujourd'hui, la vie est belle"
    }

# ============================================
# Tests de generation de contenu
# ============================================
Write-Host "=== Tests Generation de Contenu ===" -ForegroundColor Cyan
Write-Host ""

# Generation de blague
$results."Generate Joke" = Test-Endpoint `
    -Name "Generation de Blague" `
    -Method "POST" `
    -Uri "http://localhost:8001/api/v1/content/generate-post" `
    -Body @{
        post_type = "blague"
        topic = "les examens"
        sentiment = "positif"
    }

# Generation d'information utile
$results."Generate Info" = Test-Endpoint `
    -Name "Generation d'Information Utile" `
    -Method "POST" `
    -Uri "http://localhost:8001/api/v1/content/generate-post" `
    -Body @{
        post_type = "information utile"
        topic = "gestion du stress"
        sentiment = "positif"
    }

# ============================================
# Tests de detection hate speech
# ============================================
Write-Host "=== Tests Detection Hate Speech ===" -ForegroundColor Cyan
Write-Host ""

$results."Hate Speech Detection" = Test-Endpoint `
    -Name "Detection Hate Speech" `
    -Method "POST" `
    -Uri "http://localhost:8001/api/v1/predict?model_name=hatecomment-bert" `
    -Body @{
        text = "Ce commentaire est offensant et haineux"
    }

# ============================================
# Tests de recommandations
# ============================================
Write-Host "=== Tests Recommandations ===" -ForegroundColor Cyan
Write-Host ""

$results."Recommendations" = Test-Endpoint `
    -Name "Recommandations pour utilisateur" `
    -Method "GET" `
    -Uri "http://localhost:8001/recommend?userId=1"

# ============================================
# Tests de metriques
# ============================================
Write-Host "=== Tests Metriques ===" -ForegroundColor Cyan
Write-Host ""

$results."Metrics Summary" = Test-Endpoint `
    -Name "Resume des metriques" `
    -Method "GET" `
    -Uri "http://localhost:8001/api/v1/metrics/summary"

$results."Model Stats" = Test-Endpoint `
    -Name "Statistiques des modeles" `
    -Method "GET" `
    -Uri "http://localhost:8001/api/v1/metrics/models"

# ============================================
# Resume des tests
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Resume des Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$successCount = ($results.Values | Where-Object { $_ -eq $true }).Count
$totalCount = $results.Count
$failureCount = $totalCount - $successCount

Write-Host "Total: $totalCount tests" -ForegroundColor White
Write-Host "Succes: $successCount" -ForegroundColor Green
Write-Host "Echecs: $failureCount" -ForegroundColor Red
Write-Host ""

if ($failureCount -eq 0) {
    Write-Host "[OK] Tous les tests ont reussi !" -ForegroundColor Green
} else {
    Write-Host "[!] Certains tests ont echoue" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Tests echoues:" -ForegroundColor Yellow
    foreach ($test in $results.GetEnumerator()) {
        if (-not $test.Value) {
            Write-Host "  - $($test.Key)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Pour plus de details, consultez:" -ForegroundColor Yellow
Write-Host "  - Logs API: docker-compose logs -f api" -ForegroundColor White
Write-Host "  - Documentation: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
