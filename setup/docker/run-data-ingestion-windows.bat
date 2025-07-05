@echo off
REM Script to run NNDR data ingestion on remote server (Windows compatible)
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

REM Create a temporary PowerShell script for SSH operations
echo Creating temporary PowerShell script...
(
echo $ErrorActionPreference = 'Stop'
echo $REMOTE_HOST = '%REMOTE_HOST%'
echo $REMOTE_USER = '%REMOTE_USER%'
echo $REMOTE_DIR = '%REMOTE_DIR%'
echo $PASSWORD = '%PASSWORD%'
echo.
echo # Convert password to secure string
echo $securePassword = ConvertTo-SecureString $PASSWORD -AsPlainText -Force
echo $credential = New-Object System.Management.Automation.PSCredential $REMOTE_USER, $securePassword
echo.
echo Write-Host "📤 Transferring ingestion script..." -ForegroundColor Yellow
echo try {
echo     $session = New-PSSession -HostName $REMOTE_HOST -Credential $credential -ErrorAction Stop
echo     Copy-Item "setup\database\ingest_all_data.py" -Destination "$REMOTE_DIR/" -ToSession $session -Force
echo     Write-Host "✅ Ingestion script transferred" -ForegroundColor Green
echo } catch {
echo     Write-Host "❌ Failed to transfer ingestion script: $($_.Exception.Message)" -ForegroundColor Red
echo     exit 1
echo }
echo.
echo Write-Host "📤 Transferring data directory..." -ForegroundColor Yellow
echo Write-Host "   This may take 10-30 minutes depending on data size..." -ForegroundColor Yellow
echo try {
echo     Copy-Item "backend\data" -Destination "$REMOTE_DIR/" -ToSession $session -Recurse -Force
echo     Write-Host "✅ Data directory transferred" -ForegroundColor Green
echo } catch {
echo     Write-Host "❌ Failed to transfer data directory: $($_.Exception.Message)" -ForegroundColor Red
echo     exit 1
echo }
echo.
echo Write-Host "🔧 Installing required Python packages..." -ForegroundColor Yellow
echo try {
echo     Invoke-Command -Session $session -ScriptBlock {
echo         cd $using:REMOTE_DIR
echo         pip install pandas geopandas sqlalchemy psycopg2-binary
echo     }
echo     Write-Host "✅ Python packages installed" -ForegroundColor Green
echo } catch {
echo     Write-Host "❌ Failed to install Python packages: $($_.Exception.Message)" -ForegroundColor Red
echo     exit 1
echo }
echo.
echo Write-Host "🚀 Starting data ingestion..." -ForegroundColor Yellow
echo Write-Host "   This will take 30-60 minutes depending on data size..." -ForegroundColor Yellow
echo try {
echo     Invoke-Command -Session $session -ScriptBlock {
echo         cd $using:REMOTE_DIR
echo         python3 ingest_all_data.py
echo     }
echo     Write-Host "✅ Data ingestion completed" -ForegroundColor Green
echo } catch {
echo     Write-Host "❌ Data ingestion failed: $($_.Exception.Message)" -ForegroundColor Red
echo     exit 1
echo }
echo.
echo Write-Host "📊 Database statistics:" -ForegroundColor Yellow
echo try {
echo     Invoke-Command -Session $session -ScriptBlock {
echo         docker exec -it `$(docker ps -q --filter 'name=postgis-simple'^) psql -U nndr_user -d nndr_insight -c "SELECT schemaname, tablename, n_tup_ins as rows FROM pg_stat_user_tables ORDER BY n_tup_ins DESC;"
echo     }
echo } catch {
echo     Write-Host "⚠️ Could not get database statistics: $($_.Exception.Message)" -ForegroundColor Yellow
echo }
echo.
echo # Clean up session
echo Remove-PSSession $session
) > temp_ssh_script.ps1

REM Run the PowerShell script
echo Running PowerShell script...
powershell -ExecutionPolicy Bypass -File temp_ssh_script.ps1

REM Check if PowerShell script succeeded
if %ERRORLEVEL% neq 0 (
    echo ❌ Data ingestion failed
    del temp_ssh_script.ps1
    pause
    exit /b 1
)

REM Clean up temporary script
del temp_ssh_script.ps1

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