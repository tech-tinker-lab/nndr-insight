@echo off
echo ========================================
echo Fast OS Open Names Ingestion Script
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
    echo ERROR: .env file not found in backend directory
    echo Please ensure the .env file is configured
    pause
    exit /b 1
)

echo Starting fast OS Open Names ingestion...
echo Data source: backend\data\opname_csv_gb\Data
echo.

REM Run the ingestion script
python setup\scripts\ingest_osopennames_fast.py

if errorlevel 1 (
    echo.
    echo ERROR: Ingestion failed with exit code %errorlevel%
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo Fast OS Open Names Ingestion Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Verify data quality in the database
echo 2. Check the os_open_names table structure
echo 3. Run spatial queries to test geometry
echo.
pause 