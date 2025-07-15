# Refrigeration Maintenance Dashboard - Vue.js Version

echo "Starting Refrigeration Maintenance Dashboard..."

echo ""
echo "1. Starting Backend API Server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting Flask Backend...' -ForegroundColor Green; python app.py"

echo ""
echo "2. Waiting for backend to start..."
Start-Sleep -Seconds 5

echo ""
echo "3. Installing Frontend Dependencies..."
Set-Location frontend
npm install

echo ""
echo "4. Starting Vue.js Frontend Development Server..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host 'Starting Vue.js Frontend...' -ForegroundColor Green; npm run dev"

echo ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dashboard is starting up!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:5002" -ForegroundColor Yellow
Write-Host "Frontend UI: http://localhost:3000" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
echo ""
Write-Host "Both servers are running in separate windows." -ForegroundColor Green
Write-Host "Close those windows to stop the servers." -ForegroundColor Green
echo ""
Read-Host "Press Enter to continue..."
