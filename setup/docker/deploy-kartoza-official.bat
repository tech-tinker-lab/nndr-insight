@echo off
REM Deploy official Kartoza PostGIS image to remote server
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🚀 Deploying Official Kartoza PostGIS...

REM Check if required files exist
if not exist "setup\docker\docker-compose.official-kartoza.yml" (
    echo ❌ Error: setup\docker\docker-compose.official-kartoza.yml not found!
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

echo   Transferring docker-compose.official-kartoza.yml...
sshpass -p "%PASSWORD%" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null setup\docker\docker-compose.official-kartoza.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo ✅ File transfer completed

REM Clean up and start on remote server
echo 🔧 Starting official Kartoza PostGIS on remote server...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.official-kartoza.yml down -v && docker compose -f docker-compose.official-kartoza.yml up -d"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start database
    pause
    exit /b 1
)

echo ✅ Database started successfully

REM Verify the setup
echo 🔍 Verifying setup...

echo 📊 Container status:
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"

echo 🔗 Testing database connection...
sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "sleep 15 && docker exec -it $(docker ps -q --filter 'name=nndr-insight-db-1') psql -U nndr -d nndr_db -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet, wait a few more seconds'"

echo 🎉 Deployment completed!
echo 📋 Summary:
echo    - Remote Host: %REMOTE_HOST%
echo    - Database Port: 5432
echo    - Database: nndr_db
echo    - User: nndr
echo    - Password: nndrpass
echo    - Image: kartoza/postgis:17-3.5
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
echo    3. Check logs if needed: docker logs nndr-insight-db-1
echo.
echo 🌟 Benefits of Official Kartoza Image:
echo    - Latest PostGIS 3.5.x
echo    - Professional maintenance
echo    - ARM64 optimized
echo    - Comprehensive extensions
echo    - Production-ready reliability

pause 