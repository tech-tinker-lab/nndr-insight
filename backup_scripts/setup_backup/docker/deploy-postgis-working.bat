@echo off
REM Working PostGIS deployment script - uses same approach as deploy-to-remote.bat
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🚀 Deploying PostGIS with working approach...

REM Check if required files exist
if not exist "docker-compose.simple.yml" (
    echo ❌ Error: docker-compose.simple.yml not found!
    pause
    exit /b 1
)

if not exist "Dockerfile.postgis-arm64-simple" (
    echo ❌ Error: Dockerfile.postgis-arm64-simple not found!
    pause
    exit /b 1
)

echo ✅ Required files found

REM Check if SSH key exists and set up SSH connection
echo 🔑 Setting up SSH connection...
if not exist "%USERPROFILE%\.ssh\id_rsa" (
    echo ⚠️  SSH key not found. You will be prompted for password multiple times.
    echo    To avoid this, generate an SSH key: ssh-keygen -t rsa -b 4096
    echo    Then copy it to the server: ssh-copy-id %REMOTE_USER%@%REMOTE_HOST%
    echo.
) else (
    echo ✅ SSH key found. Setting up connection...
    REM Test SSH connection once
    ssh -o ConnectTimeout=10 -o BatchMode=yes %REMOTE_USER%@%REMOTE_HOST% "echo 'SSH connection successful'" 2>nul
    if %ERRORLEVEL% neq 0 (
        echo ⚠️  SSH key authentication failed. You will be prompted for password.
        echo    To fix this, run: ssh-copy-id %REMOTE_USER%@%REMOTE_HOST%
        echo.
    ) else (
        echo ✅ SSH key authentication working!
    )
)

REM Create remote directory
echo 📁 Creating remote directory...
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%"

REM Transfer files
echo 📤 Transferring files to remote server...

echo   Transferring docker-compose.simple.yml...
scp docker-compose.simple.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring Dockerfile.postgis-arm64-simple...
scp Dockerfile.postgis-arm64-simple %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo ✅ File transfer completed

REM Clean up and rebuild on remote server
echo 🔧 Cleaning up and rebuilding on remote server...
ssh %REMOTE_USER%@%REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.simple.yml down -v && docker volume rm postgis_simple_data 2>/dev/null || true && docker rmi nndr-insight-postgis-simple 2>/dev/null || true && docker build -f Dockerfile.postgis-arm64-simple -t postgis-simple . && docker compose -f docker-compose.simple.yml up -d"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build and start database
    pause
    exit /b 1
)

echo ✅ Database built and started successfully

REM Verify the setup
echo 🔍 Verifying setup...

echo 📊 Container status:
ssh %REMOTE_USER%@%REMOTE_HOST% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"

echo 🔗 Testing database connection...
ssh %REMOTE_USER%@%REMOTE_HOST% "sleep 10 && docker exec -it $(docker ps -q --filter 'name=nndr-postgis-simple') psql -U nndr_user -d nndr_insight -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet, wait a few more seconds'"

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