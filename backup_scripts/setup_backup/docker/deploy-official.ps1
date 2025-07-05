# PowerShell script to deploy PostGIS using official image (no build required)
# Run this script from the project root directory

param(
    [string]$RemoteHost = "192.168.1.79",
    [string]$RemoteUser = "kmirza",
    [string]$RemoteDir = "/server/postgis"
)

Write-Host "🚀 Deploying PostGIS using official image..." -ForegroundColor Green

# Check if required files exist
$requiredFiles = @(
    "docker-compose.official.yml"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Error: Required file '$file' not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required files found" -ForegroundColor Green

# Create remote directory
Write-Host "📁 Creating remote directory..." -ForegroundColor Yellow
ssh "${RemoteUser}@${RemoteHost}" "mkdir -p ${RemoteDir}"

# Transfer files
Write-Host "📤 Transferring files to remote server..." -ForegroundColor Yellow

# Transfer docker-compose file
Write-Host "  Transferring docker-compose.official.yml..." -ForegroundColor Cyan
scp docker-compose.official.yml "${RemoteUser}@${RemoteHost}:${RemoteDir}/"

Write-Host "✅ File transfer completed" -ForegroundColor Green

# Pull and start the database
Write-Host "🚀 Pulling official PostGIS image and starting database..." -ForegroundColor Yellow

# Pull the official image
ssh "${RemoteUser}@${RemoteHost}" "cd ${RemoteDir} && docker pull postgis/postgis:16-3.4"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostGIS image pulled successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to pull PostGIS image" -ForegroundColor Red
    exit 1
}

# Start the database
Write-Host "🚀 Starting database..." -ForegroundColor Yellow
ssh "${RemoteUser}@${RemoteHost}" "cd ${RemoteDir} && docker-compose -f docker-compose.official.yml up -d"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start database" -ForegroundColor Red
    exit 1
}

# Verify the setup
Write-Host "🔍 Verifying setup..." -ForegroundColor Yellow

# Check if containers are running
$containers = ssh "${RemoteUser}@${RemoteHost}" "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"
Write-Host "📊 Container status:" -ForegroundColor Cyan
Write-Host $containers

# Test database connection
Write-Host "🔗 Testing database connection..." -ForegroundColor Yellow
$dbTest = ssh "${RemoteUser}@${RemoteHost}" "docker exec -it `$(docker ps -q --filter 'name=db') psql -U nndr -d nndr_db -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet'"
Write-Host $dbTest

Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   - Remote Host: ${RemoteHost}" -ForegroundColor White
Write-Host "   - Database Port: 5432" -ForegroundColor White
Write-Host "   - pgAdmin Port: 8080" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To connect to the database:" -ForegroundColor Yellow
Write-Host "   Host: ${RemoteHost}" -ForegroundColor White
Write-Host "   Port: 5432" -ForegroundColor White
Write-Host "   User: nndr" -ForegroundColor White
Write-Host "   Password: nndrpass" -ForegroundColor White
Write-Host "   Database: nndr_db" -ForegroundColor White
Write-Host ""
Write-Host "🌐 pgAdmin access:" -ForegroundColor Yellow
Write-Host "   URL: http://${RemoteHost}:8080" -ForegroundColor White
Write-Host "   Email: admin@nndr.local" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White 