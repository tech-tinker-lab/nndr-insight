@echo off
echo ========================================
echo FILE MONITOR AND AUTO-PROCESSING SYSTEM
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

REM Check if required packages are installed
python -c "import watchdog" >nul 2>&1
if errorlevel 1 (
    echo Installing required package: watchdog
    pip install watchdog
    if errorlevel 1 (
        echo ERROR: Failed to install watchdog package
        pause
        exit /b 1
    )
)

REM Check if the script exists
if not exist "setup\scripts\file_monitor.py" (
    echo ERROR: file_monitor.py not found
    echo Please ensure the script exists in setup\scripts\
    pause
    exit /b 1
)

echo Starting file monitor and auto-processing system...
echo.
echo Directory Structure:
echo - Incoming: setup\data\incoming
echo - Processing: setup\data\processing  
echo - Processed: setup\data\processed
echo - Failed: setup\data\failed
echo.
echo Place files in the 'incoming' directory to trigger automatic processing.
echo Press Ctrl+C to stop the monitor.
echo.

REM Run the file monitor
python setup\scripts\file_monitor.py

echo.
echo File monitor stopped.
pause 