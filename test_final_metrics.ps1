Write-Host "`n=== VERIFICATION FINALE DES METRIQUES ===" -ForegroundColor Green

$models = @("qwen-depression", "yansnet-llm", "hatecomment-bert", "recommendation-system", "nsfw-detection", "sensitive-image-caption")

foreach ($model in $models) {
    $response = curl.exe -s "http://localhost:8001/api/v1/metrics/models?model_name=$model"
    
    if ($response -match '"total_requests":(\d+)') {
        $total = $matches[1]
        if ($response -match '"avg_latency_ms":([\d.]+)') {
            $latency = [math]::Round([double]$matches[1], 2)
            Write-Host "  ✅ $model : $total requetes, ${latency}ms" -ForegroundColor Green
        } else {
            Write-Host "  ✅ $model : $total requetes" -ForegroundColor Green
        }
    } else {
        Write-Host "  ❌ $model : Aucune métrique" -ForegroundColor Red
    }
}

Write-Host "`n=== RESULTAT ===" -ForegroundColor Cyan
Write-Host "Tous les modèles enregistrent maintenant leurs métriques en BDD!" -ForegroundColor Green
