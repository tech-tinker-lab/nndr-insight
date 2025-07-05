@echo off
REM Script to rebuild and restart the database with fixed Dockerfile

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🔧 Rebuilding database with fixed Dockerfile...

REM Prompt for password
set /p PASSWORD="Enter password for %REMOTE_USER%@%REMOTE_HOST%: "

REM Transfer the fixed Dockerfile
echo 📤 Transferring fixed Dockerfile...
powershell -ExecutionPolicy Bypass -Command "& {
    $ErrorActionPreference = 'Stop'
    $REMOTE_HOST = '%REMOTE_HOST%'
    $REMOTE_USER = '%REMOTE_USER%'
    $REMOTE_DIR = '%REMOTE_DIR%'
    $PASSWORD = '%PASSWORD%'
    
    $securePassword = ConvertTo-SecureString $PASSWORD -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential $REMOTE_USER, $securePassword
    
    try {
        $session = New-PSSession -HostName $REMOTE_HOST -Credential $credential -ErrorAction Stop
        Copy-Item 'Dockerfile.postgis-arm64-working' -Destination '$REMOTE_DIR/Dockerfile.postgis-custom' -ToSession $session -Force
        Write-Host '✅ Fixed Dockerfile transferred' -ForegroundColor Green
    } catch {
        Write-Host '❌ Failed to transfer Dockerfile: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    
    Write-Host '🔧 Rebuilding database container...' -ForegroundColor Yellow
    try {
        Invoke-Command -Session $session -ScriptBlock {
            cd $using:REMOTE_DIR
            
            # Stop and remove existing containers
            docker compose -f docker-compose.custom.yml down
            
            # Remove the problematic volume
            docker volume rm nndr-insight_db_data 2>$null
            
            # Rebuild the image with fixed Dockerfile
            docker build -f Dockerfile.postgis-custom -t postgis-custom .
            
            # Start fresh
            docker compose -f docker-compose.custom.yml up -d
            
            Write-Host '✅ Database rebuilt and started successfully' -ForegroundColor Green
        }
    } catch {
        Write-Host '❌ Failed to rebuild database: ' $_.Exception.Message -ForegroundColor Red
        exit 1
    }
    
    Write-Host '📊 Checking database status...' -ForegroundColor Yellow
    try {
        Invoke-Command -Session $session -ScriptBlock {
            docker ps --filter 'name=postgis-db'
            Write-Host ''
            Write-Host 'Database logs:' -ForegroundColor Cyan
            docker logs postgis-db-1 --tail 10
        }
    } catch {
        Write-Host '⚠️ Could not check status: ' $_.Exception.Message -ForegroundColor Yellow
    }
    
    Remove-PSSession $session
}"

if %ERRORLEVEL% neq 0 (
    echo ❌ Database rebuild failed
    pause
    exit /b 1
)

echo.
echo 🎉 Database rebuilt successfully!
echo 📋 Next steps:
echo    1. Wait 30-60 seconds for database to fully start
echo    2. Run your data ingestion script
echo    3. Check database logs if needed: docker logs postgis-db-1

pause 