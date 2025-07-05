@echo off
REM Comprehensive Data Ingestion Pipeline Runner for Windows
REM Usage: run_pipeline.bat [options]

setlocal enabledelayedexpansion

REM Set default values
set DATA_DIR=
set SOURCE_TYPE=
set LOG_LEVEL=INFO
set DRY_RUN=
set SHOW_INFO=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse
if /i "%~1"=="--data-dir" (
    set DATA_DIR=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--source-type" (
    set SOURCE_TYPE=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--log-level" (
    set LOG_LEVEL=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--dry-run" (
    set DRY_RUN=--dry-run
    shift
    goto :parse_args
)
if /i "%~1"=="--info" (
    set SHOW_INFO=--info
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:end_parse

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "comprehensive_ingestion_pipeline.py" (
    echo ERROR: comprehensive_ingestion_pipeline.py not found
    echo Please run this script from the enhanced_ingestion_pipeline directory
    pause
    exit /b 1
)

REM Check if db_config.py exists
if not exist "db_config.py" (
    echo WARNING: db_config.py not found
    echo Copying from parent directory...
    copy "..\db_config.py" . >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Could not copy db_config.py
        echo Please ensure db_config.py exists in the parent directory
        pause
        exit /b 1
    )
)

echo ========================================
echo Comprehensive Data Ingestion Pipeline
echo ========================================
echo.

REM Build command
set CMD=python run_pipeline.py

if not "%DATA_DIR%"=="" (
    set CMD=!CMD! --data-dir "%DATA_DIR%"
)

if not "%SOURCE_TYPE%"=="" (
    set CMD=!CMD! --source-type %SOURCE_TYPE%
)

if not "%LOG_LEVEL%"=="" (
    set CMD=!CMD! --log-level %LOG_LEVEL%
)

if not "%DRY_RUN%"=="" (
    set CMD=!CMD! %DRY_RUN%
)

if not "%SHOW_INFO%"=="" (
    set CMD=!CMD! %SHOW_INFO%
)

REM Show what will be executed
echo Command: %CMD%
echo.

REM Execute the pipeline
echo Starting pipeline execution...
echo.
%CMD%

REM Check exit code
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline execution failed
    echo Check the logs for details
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: Pipeline execution completed
    pause
    exit /b 0
)

:show_help
echo.
echo Comprehensive Data Ingestion Pipeline - Windows Runner
echo =====================================================
echo.
echo Usage: run_pipeline.bat [options]
echo.
echo Options:
echo   --data-dir PATH      Specify custom data directory
echo   --source-type TYPE   Filter by source type (nndr, reference, property_sales, market_analysis, economic_indicators)
echo   --log-level LEVEL    Set logging level (DEBUG, INFO, WARNING, ERROR)
echo   --dry-run           Run in dry-run mode (no data insertion)
echo   --info              Show pipeline information and exit
echo   --help              Show this help message
echo.
echo Examples:
echo   run_pipeline.bat --info
echo   run_pipeline.bat --dry-run
echo   run_pipeline.bat --source-type nndr
echo   run_pipeline.bat --data-dir "C:\data" --log-level DEBUG
echo.
pause
exit /b 0 