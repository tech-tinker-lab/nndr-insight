@echo off
REM Simple PostGIS deployment script - works with command prompt
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🚀 Deploying PostGIS with simple approach...

REM Check if required files exist
if not exist "setup\docker\docker-compose.simple.yml" (
    echo ❌ Error: setup\docker\docker-compose.simple.yml not found!
    pause
    exit /b 1
)

if not exist "setup\docker\Dockerfile.postgis-arm64-simple" (
    echo ❌ Error: setup\docker\Dockerfile.postgis-arm64-simple not found!
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

echo   Transferring docker-compose.simple.yml...
sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null setup\docker\docker-compose.simple.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring Dockerfile.postgis-arm64-simple...
sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null setup\docker\Dockerfile.postgis-arm64-simple %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo ✅ File transfer completed

REM Clean up and rebuild on remote server
echo 🔧 Cleaning up and rebuilding on remote server...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.simple.yml down -v && docker volume rm postgis_simple_data 2>/dev/null || true && docker rmi nndr-insight-postgis-simple 2>/dev/null || true && docker build -f Dockerfile.postgis-arm64-simple -t postgis-simple . && docker compose -f docker-compose.simple.yml up -d"

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
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "sleep 10 && docker exec -it $(docker ps -q --filter 'name=nndr-postgis-simple') psql -U nndr_user -d nndr_insight -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet, wait a few more seconds'"

echo 🎉 Deployment completed!
echo 📋 Summary:
echo    - Remote Host: %REMOTE_HOST%
echo    - Database Port: 5432
echo    - Database: nndr_insight
echo    - User: nndr_user
echo    - Password: nndr_password
echo.
echo 🔧 To connect to the database:
echo    Host: %REMOTE_HOST%
echo    Port: 5432
echo    User: nndr_user
echo    Password: nndr_password
echo    Database: nndr_insight
echo.
echo 📊 Next steps:
echo    1. Wait 30-60 seconds for database to fully start
echo    2. Run your data ingestion script
echo    3. Check logs if needed: docker logs nndr-postgis-simple

pause 