@echo off
REM Remote NNDR Data Ingestion Script
REM Runs from local machine, connects to remote database

echo 🚀 Starting Remote NNDR Data Ingestion...
echo    This will process data locally and send to remote database
echo.

REM Check if required files exist
if not exist "setup\database\remote_data_ingestion.py" (
    echo ❌ Error: remote_data_ingestion.py not found!
    pause
    exit /b 1
)

if not exist "backend\data" (
    echo ❌ Error: backend\data directory not found!
    pause
    exit /b 1
)

echo ✅ Required files found

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Error: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found

REM Install required packages if needed
echo 🔧 Checking Python packages...
python -c "import pandas, geopandas, sqlalchemy, psycopg2" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 📦 Installing required Python packages...
    pip install pandas geopandas sqlalchemy psycopg2-binary
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to install Python packages
        pause
        exit /b 1
    )
)

echo ✅ Python packages ready

REM Run the remote ingestion
echo 🚀 Starting data ingestion...
echo    This will take 30-60 minutes depending on data size...
echo    Progress will be shown in real-time...
echo.

python setup\database\remote_data_ingestion.py

if %ERRORLEVEL% neq 0 (
    echo ❌ Data ingestion failed
    echo Check remote_data_ingestion.log for details
    pause
    exit /b 1
)

echo.
echo 🎉 Remote NNDR data ingestion completed!
echo 📋 Summary:
echo    - All database tables created on remote server
echo    - Geospatial data ingested
echo    - NNDR data ingested (2023, 2017, 2010)
echo    - Performance indexes created
echo    - Ready for business rate forecasting
echo.
echo 🔧 Next steps:
echo    1. Run your forecasting models
echo    2. Generate business rate reports
echo    3. Analyze non-rated properties
echo.
echo 📊 Check remote_data_ingestion.log for detailed statistics

pause 