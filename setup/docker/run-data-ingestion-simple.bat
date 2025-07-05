@echo off
REM Simple NNDR data ingestion script for Windows
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

REM Run PowerShell with execution policy bypass
echo 📤 Transferring files and running ingestion...
powershell -ExecutionPolicy Bypass -Command "& {
    $ErrorActionPreference = 'Stop'
    $REMOTE_HOST = '%REMOTE_HOST%'
    $REMOTE_USER = '%REMOTE_USER%'
    $REMOTE_DIR = '%REMOTE_DIR%'
    $PASSWORD = '%PASSWORD%'
    
    # Convert password to secure string
    $securePassword = ConvertTo-SecureString $PASSWORD -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential $REMOTE_USER, $securePassword
    
    Write-Host '📤 Transferring ingestion script...' -ForegroundColor Yellow
    try {
        $session = New-PSSession -HostName $REMOTE_HOST -Credential $credential -ErrorAction Stop
        Copy-Item 'setup\database\ingest_all_data.py' -Destination '$REMOTE_DIR/' -ToSession $session -Force
        Write-Host '✅ Ingestion script transferred' -ForegroundColor Green
    } catch {
        Write-Host '❌ Failed to transfer ingestion script: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    
    Write-Host '📤 Transferring data directory...' -ForegroundColor Yellow
    Write-Host '   This may take 10-30 minutes depending on data size...' -ForegroundColor Yellow
    try {
        Copy-Item 'backend\data' -Destination '$REMOTE_DIR/' -ToSession $session -Recurse -Force
        Write-Host '✅ Data directory transferred' -ForegroundColor Green
    } catch {
        Write-Host '❌ Failed to transfer data directory: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    
    Write-Host '🔧 Installing required Python packages...' -ForegroundColor Yellow
    try {
        Invoke-Command -Session $session -ScriptBlock {
            cd $using:REMOTE_DIR
            pip install pandas geopandas sqlalchemy psycopg2-binary
        }
        Write-Host '✅ Python packages installed' -ForegroundColor Green
    } catch {
        Write-Host '❌ Failed to install Python packages: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    
    Write-Host '🚀 Starting data ingestion...' -ForegroundColor Yellow
    Write-Host '   This will take 30-60 minutes depending on data size...' -ForegroundColor Yellow
    try {
        Invoke-Command -Session $session -ScriptBlock {
            cd $using:REMOTE_DIR
            python3 ingest_all_data.py
        }
        Write-Host '✅ Data ingestion completed' -ForegroundColor Green
    } catch {
        Write-Host '❌ Data ingestion failed: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    
    Write-Host '📊 Database statistics:' -ForegroundColor Yellow
    try {
        Invoke-Command -Session $session -ScriptBlock {
            docker exec -it $(docker ps -q --filter 'name=postgis-simple') psql -U nndr_user -d nndr_insight -c 'SELECT schemaname, tablename, n_tup_ins as rows FROM pg_stat_user_tables ORDER BY n_tup_ins DESC;'
        }
    } catch {
        Write-Host '⚠️ Could not get database statistics: ' $_.Exception.Message -ForegroundColor Yellow
    }
    
    # Clean up session
    Remove-PSSession $session
}"

if %ERRORLEVEL% neq 0 (
    echo ❌ Data ingestion failed
    pause
    exit /b 1
)

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