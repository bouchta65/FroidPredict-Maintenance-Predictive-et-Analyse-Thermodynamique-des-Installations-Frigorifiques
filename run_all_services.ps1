#!/usr/bin/env powershell
# PowerShell script to start all services

Write-Host "Demarrage du Systeme de Maintenance Predictive" -ForegroundColor Cyan
Write-Host ""

Write-Host "Demarrage des services Docker..." -ForegroundColor Green
try {
    docker-compose up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur lors du demarrage des services Docker" -ForegroundColor Red
        Read-Host "Appuyez sur Entree pour continuer..."
        exit 1
    }
} catch {
    Write-Host "Docker n'est pas disponible. Assurez-vous que Docker Desktop est demarre." -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour continuer..."
    exit 1
}

Write-Host "Attente du demarrage des services Docker..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Demarrage de l'application Flask..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "app.py" -WindowStyle Normal

Start-Sleep -Seconds 8

Write-Host "Demarrage du producteur Kafka..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "kafka_producer.py" -WindowStyle Normal

Start-Sleep -Seconds 5

Write-Host "Demarrage du service de prediction..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "streamingpredict.py" -WindowStyle Normal

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Services demarres!" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:5002" -ForegroundColor Cyan
Write-Host "Kafka UI: http://localhost:8080" -ForegroundColor Cyan
Write-Host "MongoDB UI: http://localhost:8081" -ForegroundColor Cyan
Write-Host ""
Read-Host "Appuyez sur Entree pour continuer..."
