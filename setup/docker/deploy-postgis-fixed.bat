@echo off
REM Fixed PostGIS deployment script - uses official approach
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🚀 Deploying PostGIS with fixed initialization...

REM Check if required files exist
if not exist "Dockerfile.postgis-arm64-stable" (
    echo ❌ Error: Dockerfile.postgis-arm64-stable not found!
    pause
    exit /b 1
)

if not exist "docker-compose.stable.yml" (
    echo ❌ Error: docker-compose.stable.yml not found!
    pause
    exit /b 1
)

echo ✅ Required files found

REM Prompt for password
set /p PASSWORD="Enter password for %REMOTE_USER%@%REMOTE_HOST%: "

REM Create remote directory
echo 📁 Creating remote directory...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%"

REM Transfer files
echo 📤 Transferring files to remote server...

echo   Transferring Dockerfile.postgis-arm64-stable...
sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null Dockerfile.postgis-arm64-stable %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring docker-compose.stable.yml...
sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null docker-compose.stable.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring setup/config/...
if exist "setup\config" (
    sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r setup\config\ %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/
) else (
    echo   Note: setup/config directory not found, skipping...
)

echo ✅ File transfer completed

REM Clean up and rebuild on remote server
echo 🔧 Cleaning up and rebuilding on remote server...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.stable.yml down -v && docker volume rm nndr-insight_db_data 2>/dev/null || true && docker rmi postgis-stable 2>/dev/null || true && docker build -f Dockerfile.postgis-arm64-stable -t postgis-stable . && docker compose -f docker-compose.stable.yml up -d"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build and start database
    pause
    exit /b 1
)

echo ✅ Database built and started successfully

REM Verify the setup
echo 🔍 Verifying setup...

echo 📊 Container status:
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"

echo 🔗 Testing database connection...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "sleep 10 && docker exec -it $(docker ps -q --filter 'name=db') psql -U nndr -d nndr_db -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet, wait a few more seconds'"

echo 🎉 Deployment completed!
echo 📋 Summary:
echo    - Remote Host: %REMOTE_HOST%
echo    - Database Port: 5432
echo    - Database: nndr_db
echo    - User: nndr
echo    - Password: nndrpass
echo.
echo 🔧 To connect to the database:
echo    Host: %REMOTE_HOST%
echo    Port: 5432
echo    User: nndr
echo    Password: nndrpass
echo    Database: nndr_db
echo.
echo 📊 Next steps:
echo    1. Wait 30-60 seconds for database to fully start
echo    2. Run your data ingestion script
echo    3. Check logs if needed: docker logs $(docker ps -q --filter 'name=db')

pause 