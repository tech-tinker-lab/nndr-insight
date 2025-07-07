@echo off
echo ========================================
echo FAST CODEPOINT DATA INGESTION
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
if not exist "ingest_codepoint_fast.py" (
    echo ERROR: ingest_codepoint_fast.py not found
    echo Please ensure the script is in the current directory
    pause
    exit /b 1
)

echo Starting fast CodePoint data ingestion...
echo.

REM Run the ingestion script
REM You can pass a specific file or directory as an argument
REM Example: run_codepoint_fast.bat "backend\data\codepo_gb\Data\CSV\codepo_gb.csv"
REM Example: run_codepoint_fast.bat "backend\data\codepo_gb\Data\CSV"

if "%~1"=="" (
    echo No specific path provided, using default CodePoint directory...
    python ingest_codepoint_fast.py
) else (
    echo Using provided path: %~1
    python ingest_codepoint_fast.py "%~1"
)

if errorlevel 1 (
    echo.
    echo ERROR: CodePoint ingestion failed!
    echo Please check the error messages above
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: CodePoint ingestion completed!
    echo.
)

pause 