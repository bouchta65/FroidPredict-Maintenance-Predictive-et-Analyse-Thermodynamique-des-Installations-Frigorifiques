@echo off
echo Starting Refrigeration Maintenance Dashboard...

echo.
echo 1. Starting Backend API Server...
start cmd /k "cd /d %~dp0 && echo Starting Flask Backend... && python app.py"

echo.
echo 2. Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 3. Installing Frontend Dependencies...
cd frontend
call npm install

echo.
echo 4. Starting Vue.js Frontend Development Server...
start cmd /k "cd /d %~dp0frontend && echo Starting Vue.js Frontend... && npm run dev"

echo.
echo ========================================
echo Dashboard is starting up!
echo ========================================
echo Backend API: http://localhost:5002
echo Frontend UI: http://localhost:3000
echo ========================================
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
