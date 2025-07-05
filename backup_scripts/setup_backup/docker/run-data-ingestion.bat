@echo off
REM Script to run NNDR data ingestion on remote server
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🚀 Running NNDR data ingestion on remote server...

REM Check if required files exist
if not exist "setup\database\ingest_all_data.py" (
    echo ❌ Error: ingest_all_data.py not found!
    pause
    exit /b 1
)

if not exist "backend\data" (
    echo ❌ Error: backend\data directory not found!
    pause
    exit /b 1
)

echo ✅ Required files found

REM Prompt for password once
set /p PASSWORD="Enter password for %REMOTE_USER%@%REMOTE_HOST%: "

REM Transfer the ingestion script
echo 📤 Transferring ingestion script...
sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null setup\database\ingest_all_data.py %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

REM Transfer the data directory (this will take a while)
echo 📤 Transferring data directory...
echo    This may take 10-30 minutes depending on data size...
sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r backend\data\ %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

REM Install required Python packages on remote server
echo 🔧 Installing required Python packages...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "cd %REMOTE_DIR% && pip install pandas geopandas sqlalchemy psycopg2-binary"

REM Run the data ingestion
echo 🚀 Starting data ingestion...
echo    This will take 30-60 minutes depending on data size...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "cd %REMOTE_DIR% && python3 ingest_all_data.py"

if %ERRORLEVEL% neq 0 (
    echo ❌ Data ingestion failed
    pause
    exit /b 1
)

echo ✅ Data ingestion completed successfully!

REM Show database statistics
echo 📊 Database statistics:
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "docker exec -it $(docker ps -q --filter 'name=postgis-simple') psql -U nndr_user -d nndr_insight -c \"SELECT schemaname, tablename, n_tup_ins as rows FROM pg_stat_user_tables ORDER BY n_tup_ins DESC;\""

echo 🎉 NNDR data ingestion completed!
echo 📋 Summary:
echo    - All database tables created
echo    - Geospatial data ingested
echo    - NNDR data ingested (2023, 2017, 2010)
echo    - Performance indexes created
echo    - Ready for business rate forecasting
echo.
echo 🔧 Next steps:
echo    1. Run your forecasting models
echo    2. Generate business rate reports
echo    3. Analyze non-rated properties

pause 