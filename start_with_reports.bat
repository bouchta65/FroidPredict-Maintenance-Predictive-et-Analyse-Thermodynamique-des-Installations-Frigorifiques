@echo off
echo 🚀 Starting FroidPredict with Reports Module
echo.

echo ▶️ Starting Flask Backend Server...
start "Flask Backend" cmd /k "python app.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo ▶️ Starting Vue.js Frontend Server...
start "Vue Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both servers are starting!
echo.
echo 📱 Frontend (Vue.js): http://localhost:3000
echo 🔧 Backend (Flask): http://localhost:5002
echo 📊 Reports Page: http://localhost:3000/reports
echo.
echo 🧪 To test the Reports API:
echo    python test_reports.py
echo.
pause
