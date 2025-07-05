@echo off
echo FroidPredict Fake Data Generator
echo ================================

set PYTHON_PATH="C:\Users\Home\Desktop\New folder (8)\.venv\Scripts\python.exe"

echo.
echo Select data generation mode:
echo 1. Generate batch data (10 batches)
echo 2. Generate continuous data (every 10 seconds)
echo 3. Generate batch data with high anomaly rate
echo 4. Custom parameters
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto batch
if "%choice%"=="2" goto continuous
if "%choice%"=="3" goto batch_anomaly
if "%choice%"=="4" goto custom
goto invalid

:batch
echo.
echo Generating batch data...
%PYTHON_PATH% generate_fake_data.py --mode batch --equipment 5 --batches 10
goto end

:continuous
echo.
echo Starting continuous data generation...
echo Press Ctrl+C to stop
%PYTHON_PATH% generate_fake_data.py --mode continuous --equipment 5 --interval 10
goto end

:batch_anomaly
echo.
echo Generating batch data with high anomaly rate...
%PYTHON_PATH% generate_fake_data.py --mode batch --equipment 5 --batches 10 --anomaly-chance 0.3
goto end

:custom
echo.
set /p equipment=Number of equipment (default 5): 
set /p mode=Mode (batch/continuous, default batch): 
set /p anomaly=Anomaly chance 0.0-1.0 (default 0.1): 

if "%equipment%"=="" set equipment=5
if "%mode%"=="" set mode=batch
if "%anomaly%"=="" set anomaly=0.1

if "%mode%"=="batch" (
    set /p batches=Number of batches (default 10): 
    if "%batches%"=="" set batches=10
    %PYTHON_PATH% generate_fake_data.py --mode batch --equipment %equipment% --batches %batches% --anomaly-chance %anomaly%
) else (
    set /p interval=Interval in seconds (default 10): 
    if "%interval%"=="" set interval=10
    %PYTHON_PATH% generate_fake_data.py --mode continuous --equipment %equipment% --interval %interval% --anomaly-chance %anomaly%
)
goto end

:invalid
echo Invalid choice. Please select 1-4.
pause
goto :eof

:end
echo.
echo Data generation completed!
pause
