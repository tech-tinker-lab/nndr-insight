Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting NNDR Insight Database Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Starting PostgreSQL database..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d

Write-Host ""
Write-Host "2. Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "3. Running unified schema creation..." -ForegroundColor Yellow
python create_unified_schema.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Database is running on localhost:5432" -ForegroundColor Cyan
Write-Host "Username: nndr_user" -ForegroundColor Cyan
Write-Host "Password: nndr_password" -ForegroundColor Cyan
Write-Host "Database: nndr_insight" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue" 