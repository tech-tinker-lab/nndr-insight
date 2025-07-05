# Script to run NNDR data ingestion on remote server
# Run this script from the project root directory

$REMOTE_HOST = "192.168.1.79"
$REMOTE_USER = "kmirza"
$REMOTE_DIR = "/server/postgis"

Write-Host "🚀 Running NNDR data ingestion on remote server..." -ForegroundColor Green

# Check if required files exist
if (-not (Test-Path "setup\database\ingest_all_data.py")) {
    Write-Host "❌ Error: ingest_all_data.py not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "backend\data")) {
    Write-Host "❌ Error: backend\data directory not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Required files found" -ForegroundColor Green

# Prompt for password once
$PASSWORD = Read-Host "Enter password for ${REMOTE_USER}@${REMOTE_HOST}" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($PASSWORD)
$PLAINTEXT_PASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Transfer the ingestion script
Write-Host "📤 Transferring ingestion script..." -ForegroundColor Yellow
$scpCommand = "echo '$PLAINTEXT_PASSWORD' | sshpass -p '$PLAINTEXT_PASSWORD' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null setup\database\ingest_all_data.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"
Invoke-Expression $scpCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to transfer ingestion script" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Transfer the data directory (this will take a while)
Write-Host "📤 Transferring data directory..." -ForegroundColor Yellow
Write-Host "   This may take 10-30 minutes depending on data size..." -ForegroundColor Yellow
$scpDataCommand = "echo '$PLAINTEXT_PASSWORD' | sshpass -p '$PLAINTEXT_PASSWORD' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r backend\data\ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"
Invoke-Expression $scpDataCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to transfer data directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install required Python packages on remote server
Write-Host "🔧 Installing required Python packages..." -ForegroundColor Yellow
$installCommand = "echo '$PLAINTEXT_PASSWORD' | sshpass -p '$PLAINTEXT_PASSWORD' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_HOST} 'cd ${REMOTE_DIR} && pip install pandas geopandas sqlalchemy psycopg2-binary'"
Invoke-Expression $installCommand

# Run the data ingestion
Write-Host "🚀 Starting data ingestion..." -ForegroundColor Yellow
Write-Host "   This will take 30-60 minutes depending on data size..." -ForegroundColor Yellow
$ingestCommand = "echo '$PLAINTEXT_PASSWORD' | sshpass -p '$PLAINTEXT_PASSWORD' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_HOST} 'cd ${REMOTE_DIR} && python3 ingest_all_data.py'"
Invoke-Expression $ingestCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Data ingestion failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Data ingestion completed successfully!" -ForegroundColor Green

# Show database statistics
Write-Host "📊 Database statistics:" -ForegroundColor Yellow
$statsCommand = "echo '$PLAINTEXT_PASSWORD' | sshpass -p '$PLAINTEXT_PASSWORD' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_HOST} 'docker exec -it `$(docker ps -q --filter \"name=postgis-simple\") psql -U nndr_user -d nndr_insight -c \"SELECT schemaname, tablename, n_tup_ins as rows FROM pg_stat_user_tables ORDER BY n_tup_ins DESC;\"'"
Invoke-Expression $statsCommand

Write-Host "🎉 NNDR data ingestion completed!" -ForegroundColor Green
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   - All database tables created" -ForegroundColor White
Write-Host "   - Geospatial data ingested" -ForegroundColor White
Write-Host "   - NNDR data ingested (2023, 2017, 2010)" -ForegroundColor White
Write-Host "   - Performance indexes created" -ForegroundColor White
Write-Host "   - Ready for business rate forecasting" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Run your forecasting models" -ForegroundColor White
Write-Host "   2. Generate business rate reports" -ForegroundColor White
Write-Host "   3. Analyze non-rated properties" -ForegroundColor White

Read-Host "Press Enter to exit" 