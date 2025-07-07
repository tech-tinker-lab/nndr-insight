@echo off
echo ========================================
echo OS Open Map Local GML File Analyzer
echo ========================================
echo.

REM Change to the scripts directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Analyzing OS Open Map Local GML files...
echo This will show detailed information about the first file
echo.

python analyze_osopenmaplocal.py

echo.
echo Analysis completed!
pause 