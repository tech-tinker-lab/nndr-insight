@echo off
echo ========================================
echo FAST OS UPRN DATA INGESTION
echo ========================================
echo.

REM Change to the project root directory
cd /d "%~dp0..\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in PATH
    echo Please ensure Python is installed and in your PATH
    pause
    exit /b 1
)

REM Check if the script exists
if not exist "setup\scripts\ingest_os_uprn_fast.py" (
    echo ERROR: ingest_os_uprn_fast.py not found
    echo Please ensure the script exists in setup\scripts\
    pause
    exit /b 1
)

echo Starting fast OS UPRN data ingestion...
echo.

REM Run the ingestion script
python setup\scripts\ingest_os_uprn_fast.py

if errorlevel 1 (
    echo.
    echo ERROR: Ingestion failed!
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: OS UPRN data ingestion completed!
)

echo.
pause 