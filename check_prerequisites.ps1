#!/usr/bin/env powershell
# System Check Script

Write-Host "Verification des prerequis du systeme..." -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Verification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detecte: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python n'est pas installe ou non accessible" -ForegroundColor Red
    exit 1
}

# Check Docker
Write-Host "Verification de Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "Docker detecte: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker n'est pas installe ou non accessible" -ForegroundColor Red
    exit 1
}

# Check Docker running
Write-Host "Verification du statut Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "Docker est en cours d'execution" -ForegroundColor Green
} catch {
    Write-Host "Docker n'est pas en cours d'execution. Demarrez Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Python packages
Write-Host "Verification des packages Python..." -ForegroundColor Yellow
$requiredPackages = @('flask', 'flask-socketio', 'pandas', 'scikit-learn', 'pymongo', 'kafka-python')
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        pip show $package | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Package $package installe" -ForegroundColor Green
        } else {
            $missingPackages += $package
            Write-Host "Package $package manquant" -ForegroundColor Red
        }
    } catch {
        $missingPackages += $package
        Write-Host "Package $package manquant" -ForegroundColor Red
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "Packages manquants detectes. Installation..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur lors de l'installation des packages" -ForegroundColor Red
        exit 1
    }
    Write-Host "Packages installes avec succes" -ForegroundColor Green
}

Write-Host ""
Write-Host "Tous les prerequis sont satisfaits!" -ForegroundColor Green
Write-Host "Vous pouvez maintenant executer .\run_all_services.ps1" -ForegroundColor Cyan
Write-Host ""
Read-Host "Appuyez sur Entree pour continuer..."
