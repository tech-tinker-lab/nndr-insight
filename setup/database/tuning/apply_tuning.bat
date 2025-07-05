@echo off
setlocal enabledelayedexpansion

REM Performance Tuning Application Script for Windows
REM This script applies the performance tuning settings to the running PostgreSQL container

REM Configuration
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=nndr_db
set DB_USER=postgres
set TUNING_SCRIPT=performance_tuning.sql

echo 🔧 Applying PostgreSQL Performance Tuning...
echo ==============================================

REM Check if PostgreSQL is running
echo Checking PostgreSQL connection...
pg_isready -h %DB_HOST% -p %DB_PORT% -U %DB_USER% >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: PostgreSQL is not running or not accessible
    echo    Make sure the container is up: docker-compose up -d
    pause
    exit /b 1
)

echo ✅ PostgreSQL is running and accessible

REM Apply tuning settings
echo 📝 Applying performance tuning settings...
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f "%TUNING_SCRIPT%"

if errorlevel 1 (
    echo ❌ Error applying tuning settings
    pause
    exit /b 1
)

echo ✅ Performance tuning applied successfully!
echo.
echo 📊 Current settings summary:
echo ============================
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "SELECT name, setting, unit, context FROM pg_settings WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem', 'wal_buffers', 'max_wal_size', 'checkpoint_completion_target', 'max_connections', 'random_page_cost', 'effective_io_concurrency', 'autovacuum', 'default_statistics_target') ORDER BY name;"

echo.
echo 🎯 Tuning complete! The database is now optimized for large data handling.
echo.
echo 💡 Tips:
echo    - Monitor performance with: docker logs ^<container_name^>
echo    - Check slow queries in logs (queries ^> 1 second are logged)
echo    - Use pgAdmin (http://localhost:8080) for database management
echo    - Consider running ANALYZE on your tables after data import

pause 