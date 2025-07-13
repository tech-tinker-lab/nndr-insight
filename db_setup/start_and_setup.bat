@echo off
echo ========================================
echo Starting NNDR Insight Database Setup
echo ========================================

echo.
echo 1. Starting PostgreSQL database...
docker-compose -f docker-compose.simple.yml up -d

echo.
echo 2. Waiting for database to be ready...
timeout /t 10 /nobreak > nul

echo.
echo 3. Running unified schema creation...
python create_unified_schema.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Database is running on localhost:5432
echo Username: nndr_user
echo Password: nndr_password
echo Database: nndr_insight
echo.
pause 