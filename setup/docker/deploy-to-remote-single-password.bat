@echo off
REM Batch script to deploy PostGIS to remote server with single password prompt
REM Run this script from the project root directory

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🚀 Deploying PostGIS to remote server with single password prompt...

REM Check if required files exist
if not exist "Dockerfile.postgis-arm64" (
    echo ❌ Error: Dockerfile.postgis-arm64 not found!
    pause
    exit /b 1
)

if not exist "Dockerfile.postgis-arm64-simple" (
    echo ❌ Error: Dockerfile.postgis-arm64-simple not found!
    pause
    exit /b 1
)

if not exist "build-postgis.sh" (
    echo ❌ Error: build-postgis.sh not found!
    pause
    exit /b 1
)

if not exist "docker-compose.simple.yml" (
    echo ❌ Error: docker-compose.simple.yml not found!
    pause
    exit /b 1
)

echo ✅ All required files found

REM Prompt for password once
set /p PASSWORD="Enter password for %REMOTE_USER%@%REMOTE_HOST%: "

REM Create a temporary SSH config file
echo Host %REMOTE_HOST% > "%TEMP%\ssh_config"
echo   User %REMOTE_USER% >> "%TEMP%\ssh_config"
echo   StrictHostKeyChecking no >> "%TEMP%\ssh_config"
echo   UserKnownHostsFile /dev/null >> "%TEMP%\ssh_config"

REM Create remote directory
echo 📁 Creating remote directory...
ssh -F "%TEMP%\ssh_config" %REMOTE_HOST% "mkdir -p %REMOTE_DIR%"

REM Transfer files using scp with password
echo 📤 Transferring files to remote server...

echo   Transferring Dockerfile.postgis-arm64...
echo %PASSWORD% | sshpass -p %PASSWORD% scp -F "%TEMP%\ssh_config" Dockerfile.postgis-arm64 %REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring Dockerfile.postgis-arm64-simple...
echo %PASSWORD% | sshpass -p %PASSWORD% scp -F "%TEMP%\ssh_config" Dockerfile.postgis-arm64-simple %REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring build-postgis.sh...
echo %PASSWORD% | sshpass -p %PASSWORD% scp -F "%TEMP%\ssh_config" build-postgis.sh %REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring docker-compose.simple.yml...
echo %PASSWORD% | sshpass -p %PASSWORD% scp -F "%TEMP%\ssh_config" docker-compose.simple.yml %REMOTE_HOST%:%REMOTE_DIR%/

echo   Transferring DOCKER_SETUP.md...
echo %PASSWORD% | sshpass -p %PASSWORD% scp -F "%TEMP%\ssh_config" DOCKER_SETUP.md %REMOTE_HOST%:%REMOTE_DIR%/

REM Transfer config directory if it exists
if exist "setup\config" (
    echo   Transferring setup/config/...
    echo %PASSWORD% | sshpass -p %PASSWORD% scp -F "%TEMP%\ssh_config" -r setup\config\ %REMOTE_HOST%:%REMOTE_DIR%/
) else (
    echo   Note: setup/config directory not found, skipping...
)

echo ✅ File transfer completed

REM Build the image on remote server
echo 🔨 Building PostGIS image on remote server...
echo    This will take 10-15 minutes...
echo %PASSWORD% | sshpass -p %PASSWORD% ssh -F "%TEMP%\ssh_config" %REMOTE_HOST% "cd %REMOTE_DIR% && chmod +x build-postgis.sh && ./build-postgis.sh"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build PostGIS image
    goto cleanup
)

echo ✅ PostGIS image built successfully

REM Start the database
echo 🚀 Starting database on remote server...
echo %PASSWORD% | sshpass -p %PASSWORD% ssh -F "%TEMP%\ssh_config" %REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.simple.yml up -d"

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start database
    goto cleanup
)

echo ✅ Database started successfully

REM Verify the setup
echo 🔍 Verifying setup...

echo 📊 Container status:
echo %PASSWORD% | sshpass -p %PASSWORD% ssh -F "%TEMP%\ssh_config" %REMOTE_HOST% "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"

echo 🔗 Testing database connection...
echo %PASSWORD% | sshpass -p %PASSWORD% ssh -F "%TEMP%\ssh_config" %REMOTE_HOST% "docker exec -it $(docker ps -q --filter 'name=postgis-simple') psql -U nndr_user -d nndr_insight -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet'"

echo 🎉 Deployment completed!
echo 📋 Summary:
echo    - Remote Host: %REMOTE_HOST%
echo    - Database Port: 5432
echo    - Database: nndr_insight
echo    - Username: nndr_user
echo    - Password: nndr_password
echo.
echo 🔧 To connect to the database:
echo    Host: %REMOTE_HOST%
echo    Port: 5432
echo    User: nndr_user
echo    Password: nndr_password
echo    Database: nndr_insight

:cleanup
REM Clean up temporary files
del "%TEMP%\ssh_config" 2>nul

pause 