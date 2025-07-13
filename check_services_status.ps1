#!/usr/bin/env powershell
# Service Status Check Script

Write-Host "Verification du statut des services..." -ForegroundColor Cyan
Write-Host ""

# Check Docker containers
Write-Host "Docker Containers:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""

# Check Python processes
Write-Host "Python Processes:" -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Format-Table -Property Name, Id, CPU, WorkingSet

Write-Host ""

# Check web services
Write-Host "Web Services:" -ForegroundColor Yellow

$services = @(
    @{Name = "Flask Dashboard"; URL = "http://localhost:5002/api/system_status"},
    @{Name = "Kafka UI"; URL = "http://localhost:8080"},
    @{Name = "MongoDB UI"; URL = "http://localhost:8081"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "$($service.Name): OK" -ForegroundColor Green
        } else {
            Write-Host "$($service.Name): $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "$($service.Name): OFFLINE" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "URLs d'acces:" -ForegroundColor Cyan
Write-Host "- Dashboard: http://localhost:5002" -ForegroundColor White
Write-Host "- Kafka UI: http://localhost:8080" -ForegroundColor White
Write-Host "- MongoDB UI: http://localhost:8081" -ForegroundColor White
Write-Host ""
