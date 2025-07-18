#!/usr/bin/env powershell
# FroidPredict Reports Module Startup Script

Write-Host "🚀 Starting FroidPredict with Reports Module" -ForegroundColor Cyan
Write-Host ""

# Start Flask Backend
Write-Host "▶️ Starting Flask Backend Server..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "app.py" -WindowStyle Normal -WorkingDirectory (Get-Location)

# Wait for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if frontend directory exists
if (Test-Path "frontend") {
    Write-Host "▶️ Starting Vue.js Frontend Server..." -ForegroundColor Green
    Start-Process -FilePath "cmd" -ArgumentList "/c", "cd frontend && npm run dev" -WindowStyle Normal
} else {
    Write-Host "⚠️ Frontend directory not found. Starting backend only." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend (Vue.js): http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend (Flask): http://localhost:5002" -ForegroundColor Cyan
Write-Host "📊 Reports Page: http://localhost:3000/reports" -ForegroundColor Magenta
Write-Host ""
Write-Host "🧪 To test the Reports API:" -ForegroundColor Yellow
Write-Host "   python test_reports.py" -ForegroundColor White
Write-Host ""

# Optional: Test if servers are responding
Write-Host "🔍 Testing server connectivity..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:5002/api/system_status" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($backendResponse.StatusCode -eq 200) {
        Write-Host "✅ Backend server is responding" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend server response: $($backendResponse.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend server not responding yet (this is normal during startup)" -ForegroundColor Red
}

try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "✅ Frontend server is responding" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Frontend server response: $($frontendResponse.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Frontend server not responding yet (this is normal during startup)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Wait for both servers to fully start (30-60 seconds)" -ForegroundColor White
Write-Host "   2. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "   3. Navigate to Reports page to test functionality" -ForegroundColor White
Write-Host "   4. Use date range filters and generate reports" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue..."
