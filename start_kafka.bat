@echo off
echo Starting Kafka and related services...
echo.

echo Checking if Docker is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Starting services with Docker Compose...
docker-compose up -d zookeeper kafka kafka-ui postgres

echo.
echo Waiting for services to start...
timeout /t 30 /nobreak

echo.
echo Services started! You can access:
echo - Kafka UI: http://localhost:8080
echo - PostgreSQL: localhost:5432
echo - Kafka: localhost:9092
echo.

echo Creating Kafka topics...
docker exec kafka kafka-topics --create --topic sensor_data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
docker exec kafka kafka-topics --create --topic alerts --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1  
docker exec kafka kafka-topics --create --topic maintenance --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

echo.
echo Topics created! Listing all topics:
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

echo.
echo Kafka setup completed!
echo You can now start the FroidPredict application.
pause
