@echo off
echo ========================================
echo OS Open Map Local Fast Ingestion Script
echo ========================================
echo.

REM Set the working directory to the project root
cd /d "%~dp0..\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if the data directory exists
if not exist "backend\data\opmplc_gml3_gb\data" (
    echo ERROR: OS Open Map Local data directory not found
    echo Expected: backend\data\opmplc_gml3_gb\data
    echo Please ensure the data files are extracted
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo ERROR: .env file not found
    echo Expected: backend\.env
    echo Please ensure the environment file exists
    pause
    exit /b 1
)

echo Starting OS Open Map Local fast ingestion...
echo This will process all GML files in the data directory
echo.

cd setup\scripts
python ingest_osopenmaplocal_fast.py

if errorlevel 1 (
    echo.
    echo ERROR: OS Open Map Local ingestion failed
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: OS Open Map Local ingestion completed
    echo Check the os_open_map_local table for results
)

pause 