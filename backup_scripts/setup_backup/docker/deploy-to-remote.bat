@echo off
REM Batch script to deploy PostGIS to remote server
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

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

echo 🚀 Deploying PostGIS to remote server...

REM Check if required files exist
if not exist "Dockerfile.postgis-arm64" (
    echo ❌ Error: Dockerfile.postgis-arm64 not found!
    pause
    exit /b 1
)

if not exist "build-postgis.sh" (
    echo ❌ Error: build-postgis.sh not found!
    pause
    exit /b 1
)

if not exist "docker-compose.yml" (
    echo ❌ Error: docker-compose.yml not found!
    pause
    exit /b 1
)

if not exist "docker-compose.custom.yml" (
    echo ❌ Error: docker-compose.custom.yml not found!
    pause
    exit /b 1
)

REM Note: setup\config is optional for docker-compose configuration

echo ✅ All required files found

REM Create remote directory
echo 📁 Creating remote directory...
ssh %REMOTE_USER%@%REMOTE_HOST% "mkdir -p %REMOTE_DIR%"

REM Transfer files
echo 📤 Transferring files to remote server...

echo   Transferring Dockerfile.postgis-arm64...
scp Dockerfile.postgis-arm64 %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring Dockerfile.postgis-arm64-simple...
scp Dockerfile.postgis-arm64-simple %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring build-postgis.sh...
scp build-postgis.sh %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring docker-compose.yml...
scp docker-compose.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring docker-compose.custom.yml...
scp docker-compose.custom.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring docker-compose.simple.yml...
scp docker-compose.simple.yml %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring DOCKER_SETUP.md...
scp DOCKER_SETUP.md %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/

REM Transfer config directory (for docker-compose configuration)
if exist "setup\config" (
    echo   Transferring setup/config/...
    scp -r setup\config\ %REMOTE_USER%@%REMOTE_HOST%:%REMOTE_DIR%/
) else (
    echo   Note: setup/config directory not found, skipping...
)

echo ✅ File transfer completed

REM Build the image on remote server
echo 🔨 Building PostGIS image on remote server...
echo    This will take 10-15 minutes...
ssh %REMOTE_USER%@%REMOTE_HOST% "cd %REMOTE_DIR% && chmod +x build-postgis.sh && ./build-postgis.sh"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build PostGIS image
    pause
    exit /b 1
)

echo ✅ PostGIS image built successfully

REM Start the database
echo 🚀 Starting database on remote server...
ssh %REMOTE_USER%@%REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.simple.yml up -d"

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
ssh %REMOTE_USER%@%REMOTE_HOST% "docker exec -it $(docker ps -q --filter 'name=db') psql -U nndr -d nndr_db -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet'"

echo 🎉 Deployment completed!
echo 📋 Summary:
echo    - Remote Host: %REMOTE_HOST%
echo    - Database Port: 5432
echo    - pgAdmin Port: 8080 (if using custom setup)
echo    - Redis Port: 6379 (if using custom setup)
echo.
echo 🔧 To connect to the database:
echo    Host: %REMOTE_HOST%
echo    Port: 5432
echo    User: nndr
echo    Password: nndrpass
echo    Database: nndr_db

pause 