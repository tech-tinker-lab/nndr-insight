@echo off
echo ========================================
echo OS Open Names Sample Ingestion Script
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
if not exist "backend\data\opname_csv_gb\Data" (
    echo ERROR: OS Open Names data directory not found
    echo Expected: backend\data\opname_csv_gb\Data
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

echo Starting OS Open Names sample ingestion...
echo This will load only the first row from each CSV file
echo.

cd setup\scripts
python ingest_osopennames_sample.py

if errorlevel 1 (
    echo.
    echo ERROR: Sample ingestion failed
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: Sample ingestion completed
    echo Check the os_open_names_sample table for results
)

pause 