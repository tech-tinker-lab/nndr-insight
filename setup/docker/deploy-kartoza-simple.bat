@echo off
REM Simple Kartoza PostGIS deployment - no monitoring stack
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis-kartoza

echo 🚀 Deploying Simple Kartoza PostGIS...

REM Check if required file exists
if not exist "setup\docker\docker-compose.official-kartoza.yml" (
    echo ❌ Error: setup\docker\docker-compose.official-kartoza.yml not found!
    pause
    exit /b 1
)

echo ✅ Required file found

REM Prompt for password
echo 🔑 Enter password for %REMOTE_USER%@%REMOTE_HOST% when prompted...
echo.

REM Create remote directory
echo 📁 Creating remote directory...
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%"

REM Transfer docker-compose file
echo 📤 Transferring docker-compose file...
scp setup\docker\docker-compose.official-kartoza.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/docker-compose.yml

echo ✅ File transfer completed

REM Start PostGIS on remote server
echo 🔧 Starting Kartoza PostGIS on remote server...
ssh %REMOTE_USER%@%REMOTE_HOST% "cd %REMOTE_DIR% && docker compose down -v && docker compose up -d"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start database
    pause
    exit /b 1
)

echo ✅ Database started successfully

REM Verify the setup
echo 🔍 Verifying setup...

echo 📊 Container status:
ssh %REMOTE_USER%@%REMOTE_HOST% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"

echo 🔗 Testing database connection...
ssh %REMOTE_USER%@%REMOTE_HOST% "sleep 15 && docker exec -it $(docker ps -q --filter 'name=nndr-insight-db-1') psql -U nndr -d nndr_db -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet, wait a few more seconds'"

echo 🎉 Simple Kartoza deployment completed!
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
echo 🌟 Kartoza Features:
echo    - Latest PostGIS 3.5.x
echo    - Professional maintenance
echo    - ARM64 optimized
echo    - Comprehensive extensions
echo    - Production-ready reliability
echo.
echo 📊 Next steps:
echo    1. Wait 30-60 seconds for database to fully start
echo    2. Run your data ingestion script
echo    3. Check logs if needed: docker logs nndr-insight-db-1

pause 