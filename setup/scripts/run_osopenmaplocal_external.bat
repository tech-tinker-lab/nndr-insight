@echo off
echo ========================================
echo OS Open Map Local External Terminal Run
echo ========================================
echo.

REM Change to the scripts directory
cd /d "%~dp0"

REM Check if Python is available
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Starting OS Open Map Local ingestion...
echo This will process all GML files
echo Press Ctrl+C to stop if needed
echo.

python ingest_osopenmaplocal_fast.py

echo.
echo Ingestion completed!
pause 