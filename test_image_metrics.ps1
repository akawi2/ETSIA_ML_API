# ============================================
# Test des Métriques des Modèles d'Images
# ============================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Métriques - Modèles d'Images" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Fonction pour tester et afficher les métriques
function Test-ImageModel {
    param(
        [string]$Name,
        [string]$Endpoint,
        [hashtable]$FormData
    )
    
    Write-Host "Test: $Name" -ForegroundColor Yellow
    Write-Host "  Endpoint: POST $Endpoint" -ForegroundColor Gray
    
    try {
        # Construire la commande curl
        $curlArgs = @("-X", "POST", $Endpoint)
        foreach ($key in $FormData.Keys) {
            $curlArgs += "-F"
            $curlArgs += "$key=$($FormData[$key])"
        }
        $curlArgs += "-H"
        $curlArgs += "accept: application/json"
        
        $startTime = Get-Date
        $response = & curl.exe @curlArgs 2>$null | ConvertFrom-Json
        $endTime = Get-Date
        $duration = [math]::Round(($endTime - $startTime).TotalMilliseconds, 0)
        
        Write-Host "  [OK] Succès (${duration}ms)" -ForegroundColor Green
        Write-Host "  Résultat:" -ForegroundColor Gray
        Write-Host "    - Prédiction: $($response.prediction)" -ForegroundColor White
        Write-Host "    - Confiance: $($response.confidence)" -ForegroundColor White
        
        if ($response.processing_time) {
            Write-Host "    - Temps traitement: $($response.processing_time)s" -ForegroundColor White
        }
        
        if ($response.caption_en) {
            Write-Host "    - Légende: $($response.caption_en)" -ForegroundColor White
        }
        
        Write-Host ""
        
        # Attendre un peu pour voir les logs
        Start-Sleep -Seconds 1
        
        return $true
    } catch {
        Write-Host "  [ERREUR] Échec: $_" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# ============================================
# Test 1: NSFW Detection
# ============================================
Write-Host "=== Test 1: NSFW Detection ===" -ForegroundColor Cyan
Write-Host ""

$result1 = Test-ImageModel `
    -Name "NSFW Detection" `
    -Endpoint "http://localhost:8001/api/v1/censure/detect" `
    -FormData @{
        "file" = "@test_image.jpg"
    }

# ============================================
# Test 2: Sensitive Image Caption
# ============================================
Write-Host "=== Test 2: Sensitive Image Caption ===" -ForegroundColor Cyan
Write-Host ""

$result2 = Test-ImageModel `
    -Name "Sensitive Image Caption" `
    -Endpoint "http://localhost:8001/api/v1/predict-image" `
    -FormData @{
        "model_name" = "sensitive-image-caption"
        "image" = "@test_image.jpg"
    }

# ============================================
# Vérification des métriques dans GA4-Bridge
# ============================================
Write-Host "=== Métriques envoyées au GA4-Bridge ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Logs récents du GA4-Bridge (dernières 30 secondes):" -ForegroundColor Yellow
Write-Host ""

# Attendre que les métriques soient envoyées
Start-Sleep -Seconds 2

# Afficher les logs du bridge
$logs = docker-compose logs --since=30s ga4-bridge 2>&1

# Filtrer les logs pertinents
$metricLogs = $logs | Select-String -Pattern "POST /log_metric|ALERTE|image_captioning|nsfw"

if ($metricLogs) {
    $metricLogs | ForEach-Object {
        Write-Host $_ -ForegroundColor White
    }
} else {
    Write-Host "  Aucune métrique d'images détectée dans les logs" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Vérification des logs de l'API
# ============================================
Write-Host "=== Logs de l'API (émission des métriques) ===" -ForegroundColor Cyan
Write-Host ""

$apiLogs = docker-compose logs --since=30s api 2>&1 | Select-String -Pattern "emit_metric|monitoring|image_captioning|nsfw_detection"

if ($apiLogs) {
    Write-Host "Métriques émises par l'API:" -ForegroundColor Yellow
    $apiLogs | Select-Object -Last 10 | ForEach-Object {
        Write-Host $_ -ForegroundColor White
    }
} else {
    Write-Host "  Aucune trace d'émission de métriques dans les logs de l'API" -ForegroundColor Yellow
    Write-Host "  Note: Les métriques sont envoyées de manière asynchrone avec timeout court" -ForegroundColor Gray
}

Write-Host ""

# ============================================
# Résumé
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Résumé" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
if ($result1) { $successCount++ }
if ($result2) { $successCount++ }

Write-Host "Tests réussis: $successCount/2" -ForegroundColor $(if ($successCount -eq 2) { "Green" } else { "Yellow" })
Write-Host ""

Write-Host "Pour voir les métriques en temps réel:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f ga4-bridge | Select-String 'image'" -ForegroundColor White
Write-Host ""

Write-Host "Pour voir toutes les métriques envoyées:" -ForegroundColor Yellow
Write-Host "  docker-compose logs ga4-bridge | Select-String 'POST /log_metric'" -ForegroundColor White
Write-Host ""
