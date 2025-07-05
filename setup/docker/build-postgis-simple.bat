@echo off
setlocal enabledelayedexpansion

REM Build script for Simple ARM64 PostGIS image (Windows)
REM This version uses pre-built Ubuntu packages instead of building from source

echo ==========================================
echo Building Simple ARM64 PostGIS Image
echo ==========================================

REM Configuration
set IMAGE_NAME=nndr-postgis-simple
set TAG=arm64-v1.0
set FULL_IMAGE_NAME=%IMAGE_NAME%:%TAG%

echo Image: %FULL_IMAGE_NAME%
echo Platform: linux/arm64
echo Strategy: Pre-built Ubuntu packages
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running or not accessible
    exit /b 1
)

REM Check if we're on ARM64 platform
for /f "tokens=*" %%i in ('echo %PROCESSOR_ARCHITECTURE%') do set ARCH=%%i
if not "%ARCH%"=="ARM64" (
    echo WARNING: Building on non-ARM64 platform (%ARCH%)
    echo This image is designed for ARM64 but can be built on other platforms
    echo.
)

REM Build the image
echo Building PostGIS image...
echo This may take a few minutes...

docker build ^
    --platform linux/arm64 ^
    --file Dockerfile.postgis-arm64-simple ^
    --tag "%FULL_IMAGE_NAME%" ^
    --progress=plain ^
    .

if errorlevel 1 (
    echo.
    echo Build failed!
    echo.
    echo Troubleshooting:
    echo 1. Check Docker logs: docker logs nndr-postgis-simple
    echo 2. Ensure you have sufficient disk space
    echo 3. Try building with more memory: docker build --memory=4g ...
    echo 4. Check internet connection for package downloads
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    echo.
    echo Image details:
    for /f "tokens=*" %%i in ('docker images %FULL_IMAGE_NAME% --format "table {{.Repository}}	{{.Tag}}	{{.Size}}"') do echo   %%i
    echo.
    echo To run the container:
    echo   docker run -d --name nndr-postgis-simple ^
    echo     -p 5432:5432 ^
    echo     -e POSTGRES_DB=nndr_insight ^
    echo     -e POSTGRES_USER=nndr_user ^
    echo     -e POSTGRES_PASSWORD=nndr_password ^
    echo     %FULL_IMAGE_NAME%
    echo.
    echo Or use docker-compose:
    echo   docker-compose -f docker-compose.simple.yml up -d
    echo.
    echo Connection details:
    echo   Host: localhost
    echo   Port: 5432
    echo   Database: nndr_insight
    echo   Username: nndr_user
    echo   Password: nndr_password
    echo.
    echo To test the connection:
    echo   docker exec -it nndr-postgis-simple su - postgres -c "psql -d nndr_insight -c \"SELECT PostGIS_Version();\""
)

pause 