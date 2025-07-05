@echo off
REM Deploy Enhanced Custom PostGIS ARM64 with SSH key authentication
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis-enhanced

echo 🚀 Deploying Enhanced Custom PostGIS ARM64 with SSH Key Authentication...

REM Check if required files exist
if not exist "setup\docker\docker-compose.custom.yml" (
    echo ❌ Error: setup\docker\docker-compose.custom.yml not found!
    pause
    exit /b 1
)

if not exist "setup\docker\Dockerfile.postgis-arm64" (
    echo ❌ Error: setup\docker\Dockerfile.postgis-arm64 not found!
    pause
    exit /b 1
)

echo ✅ Required files found

REM Prompt for password
echo 🔑 Enter password for %REMOTE_USER%@%REMOTE_HOST% when prompted...
echo.

REM Create remote directory
echo 📁 Creating remote directory...
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%"

REM Transfer files
echo 📤 Transferring files to remote server...

echo   Transferring docker-compose.custom.yml...
scp setup\docker\docker-compose.custom.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring Dockerfile.postgis-arm64...
scp setup\docker\Dockerfile.postgis-arm64 %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Creating configuration directory...
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%/config"

echo   Transferring configuration files...
if exist "setup\config\pgadmin-servers.json" (
    scp setup\config\pgadmin-servers.json %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/config/
)

if exist "setup\config\prometheus.yml" (
    scp setup\config\prometheus.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/config/
)

if exist "setup\config\postgresql.conf" (
    scp setup\config\postgresql.conf %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/config/
)

echo   Creating Grafana configuration directories...
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%/config/grafana/dashboards"
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%/config/grafana/datasources"

if exist "setup\config\grafana\dashboards\dashboard.yml" (
    scp setup\config\grafana\dashboards\dashboard.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/config/grafana/dashboards/
)

if exist "setup\config\grafana\datasources\datasource.yml" (
    scp setup\config\grafana\datasources\datasource.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/config/grafana/datasources/
)

echo   Creating scripts directory...
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%/scripts"

echo   Transferring backup script...
if exist "setup\scripts\backup.sh" (
    scp setup\scripts\backup.sh %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/scripts/
)

echo ✅ File transfer completed

REM Clean up and start on remote server
echo 🔧 Starting Enhanced Custom PostGIS on remote server...
ssh %REMOTE_USER%@%REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.custom.yml down -v && docker compose -f docker-compose.custom.yml up -d --build"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start enhanced database
    pause
    exit /b 1
)

echo ✅ Enhanced database started successfully

REM Verify the setup
echo 🔍 Verifying enhanced setup...

echo 📊 Container status:
ssh %REMOTE_USER%@%REMOTE_HOST% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep nndr"

echo 🔗 Testing database connection...
ssh %REMOTE_USER%@%REMOTE_HOST% "sleep 30 && docker exec -it nndr-postgis-enhanced psql -U nndr -d nndr_db -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet, wait a few more seconds'"

echo 🎉 Enhanced deployment completed!
echo 📋 Summary:
echo    - Remote Host: %REMOTE_HOST%
echo    - Database Port: 5432
echo    - Database: nndr_db
echo    - User: nndr
echo    - Password: nndrpass
echo    - Image: Custom Enhanced ARM64 with PostGIS 3.5.1
echo    - pgAdmin: http://%REMOTE_HOST%:8080 (admin@nndr.local / admin123)
echo    - Grafana: http://%REMOTE_HOST%:3000 (admin / admin123)
echo    - Prometheus: http://%REMOTE_HOST%:9090
echo    - Redis: %REMOTE_HOST%:6379
echo.
echo 🔧 To connect to the database:
echo    Host: %REMOTE_HOST%
echo    Port: 5432
echo    User: nndr
echo    Password: nndrpass
echo    Database: nndr_db
echo.
echo 🌟 Enhanced Features:
echo    - PostGIS 3.5.1 (latest)
echo    - ARM64 optimized build
echo    - Comprehensive extensions (h3, pg_repack, etc.)
echo    - Enhanced monitoring with Prometheus + Grafana
echo    - Automated backups
echo    - Redis caching
echo    - Enhanced pgAdmin configuration
echo    - Performance monitoring functions
echo    - Spatial analysis helpers
echo.
echo 📊 Next steps:
echo    1. Wait 60-90 seconds for all services to fully start
echo    2. Access Grafana at http://%REMOTE_HOST%:3000
echo    3. Access pgAdmin at http://%REMOTE_HOST%:8080
echo    4. Run your data ingestion script
echo    5. Check logs if needed: docker logs nndr-postgis-enhanced
echo.
echo 🔍 Monitoring URLs:
echo    - Grafana Dashboards: http://%REMOTE_HOST%:3000
echo    - Prometheus Metrics: http://%REMOTE_HOST%:9090
echo    - pgAdmin Management: http://%REMOTE_HOST%:8080

pause 