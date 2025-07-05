@echo off
echo FroidPredict API Server
echo =======================

cd /d "%~dp0"

echo.
echo Checking Python environment...
"C:\Users\Home\Desktop\New folder (8)\.venv\Scripts\python.exe" --version
if %errorlevel% neq 0 (
    echo ERROR: Python environment not found!
    echo Please run setup.bat first to install dependencies.
    pause
    exit /b 1
)

echo.
echo Starting FroidPredict API server...
echo Server will be available at: http://localhost:5000
echo.
echo Available endpoints:
echo - GET  /                           - API information
echo - GET  /health                     - Health check
echo - GET  /api/test                   - Test endpoint
echo - POST /api/kafka/generate/batch   - Generate fake data
echo - POST /api/kafka/generate/start   - Start continuous data generation
echo - POST /api/kafka/generate/stop    - Stop continuous data generation
echo - GET  /api/kafka/health           - Kafka health check
echo - GET  /api/kafka/config           - Kafka configuration
echo.
echo Press Ctrl+C to stop the server
echo.

"C:\Users\Home\Desktop\New folder (8)\.venv\Scripts\python.exe" app.py

echo.
echo Server stopped.
pause
