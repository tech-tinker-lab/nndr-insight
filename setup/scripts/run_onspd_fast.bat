@echo off
echo ========================================
echo FAST ONSPD DATA INGESTION
echo ========================================
echo.

REM Change to the scripts directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if the ingestion script exists
if not exist "ingest_onspd_fast.py" (
    echo ERROR: ingest_onspd_fast.py not found
    echo Please ensure the script is in the current directory
    pause
    exit /b 1
)

echo Starting fast ONSPD data ingestion...
echo.

REM Run the ingestion script
REM You can pass a specific file as an argument
REM Example: run_onspd_fast.bat "backend\data\ONSPD_Online_Latest_Centroids.csv"

if "%~1"=="" (
    echo No specific path provided, using default ONSPD file...
    python ingest_onspd_fast.py
) else (
    echo Using provided path: %~1
    python ingest_onspd_fast.py "%~1"
)

if errorlevel 1 (
    echo.
    echo ERROR: ONSPD ingestion failed!
    echo Please check the error messages above
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: ONSPD ingestion completed!
    echo.
)

pause 