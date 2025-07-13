@echo off
echo 🧊 Démarrage du Système de Maintenance Prédictive
echo.

echo ▶️ Démarrage des services Docker...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Erreur lors du démarrage des services Docker
    pause
    exit /b 1
)

echo ⏳ Attente du démarrage des services Docker...
ping -n 15 127.0.0.1 >nul

echo ▶️ Démarrage de l'application Flask...
start "Flask App" python app.py

ping -n 8 127.0.0.1 >nul

echo ▶️ Démarrage du producteur Kafka...
start "Kafka Producer" python kafka_producer.py

ping -n 5 127.0.0.1 >nul

echo ▶️ Démarrage du service de prédiction...
start "Prediction Service" python streamingpredict.py

ping -n 5 127.0.0.1 >nul

echo.
echo ✅ Services démarrés!
echo 🌐 Dashboard: http://localhost:5002
echo 📊 Kafka UI: http://localhost:8080
echo 📈 MongoDB UI: http://localhost:8081
echo.
pause
