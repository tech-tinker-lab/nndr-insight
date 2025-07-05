@echo off
REM Clean and deploy script - fixes the database initialization issue

set REMOTE_HOST=192.168.1.79
set REMOTE_USER=kmirza
set REMOTE_DIR=/server/postgis

echo 🧹 Cleaning and deploying fresh database...

REM Prompt for password
set /p PASSWORD="Enter password for %REMOTE_USER%@%REMOTE_HOST%: "

REM Run cleanup and deployment commands
echo %PASSWORD% | sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "cd %REMOTE_DIR% && docker compose -f docker-compose.custom.yml down -v && docker volume rm nndr-insight_db_data 2>/dev/null || true && docker rmi postgis-custom 2>/dev/null || true && docker build -f Dockerfile.postgis-arm64-working -t postgis-custom . && docker compose -f docker-compose.custom.yml up -d"

if %ERRORLEVEL% neq 0 (
    echo ❌ Clean and deploy failed
    pause
    exit /b 1
)

echo ✅ Database cleaned and deployed successfully!
echo 📊 Checking status...
echo %PASSWORD% | sshpass -p "%PASSWORD%" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %REMOTE_HOST% "docker ps --filter 'name=postgis'"

echo.
echo 🎉 Database is ready for data ingestion!
echo 📋 Next steps:
echo    1. Wait 30-60 seconds for database to fully start
echo    2. Run your data ingestion script
echo    3. Check logs if needed: docker logs postgis-db-1

pause 