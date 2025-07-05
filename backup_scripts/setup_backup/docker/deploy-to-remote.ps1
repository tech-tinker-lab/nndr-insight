# PowerShell script to deploy PostGIS to remote server
# Run this script from the project root directory

param(
    [string]$RemoteHost = "192.168.1.79",
    [string]$RemoteUser = "kmirza",
    [string]$RemoteDir = "/server/postgis"
)

Write-Host "🚀 Deploying PostGIS to remote server..." -ForegroundColor Green

# Check if required files exist
$requiredFiles = @(
    "Dockerfile.postgis-arm64",
    "build-postgis.sh",
    "docker-compose.yml",
    "docker-compose.custom.yml",
    "DOCKER_SETUP.md"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Error: Required file/directory '$file' not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required files found" -ForegroundColor Green

# Create remote directory
Write-Host "📁 Creating remote directory..." -ForegroundColor Yellow
ssh "${RemoteUser}@${RemoteHost}" "mkdir -p ${RemoteDir}"

# Transfer files
Write-Host "📤 Transferring files to remote server..." -ForegroundColor Yellow

# Transfer individual files
$filesToTransfer = @(
    "Dockerfile.postgis-arm64",
    "Dockerfile.postgis-arm64-stable",
    "build-postgis.sh", 
    "docker-compose.yml",
    "docker-compose.custom.yml",
    "docker-compose.simple.yml",
    "docker-compose.stable.yml",
    "DOCKER_SETUP.md"
)

foreach ($file in $filesToTransfer) {
    Write-Host "  Transferring $file..." -ForegroundColor Cyan
    scp $file "${RemoteUser}@${RemoteHost}:${RemoteDir}/"
}

# Transfer config directory (for docker-compose configuration)
Write-Host "  Transferring setup/config/..." -ForegroundColor Cyan
scp -r setup/config/ "${RemoteUser}@${RemoteHost}:${RemoteDir}/"

Write-Host "✅ File transfer completed" -ForegroundColor Green

# Build the image on remote server
Write-Host "🔨 Building PostGIS image on remote server..." -ForegroundColor Yellow
Write-Host "   This will take 10-15 minutes..." -ForegroundColor Yellow

ssh "${RemoteUser}@${RemoteHost}" "cd ${RemoteDir} && chmod +x build-postgis.sh && ./build-postgis.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostGIS image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build PostGIS image" -ForegroundColor Red
    exit 1
}

# Install Docker Compose if not available
Write-Host "🔧 Checking Docker Compose installation..." -ForegroundColor Yellow
ssh "${RemoteUser}@${RemoteHost}" "if ! command -v docker-compose &> /dev/null; then
    echo 'Installing Docker Compose...'
    sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo 'Docker Compose installed successfully'
else
    echo 'Docker Compose already installed'
fi"

# Start the database
Write-Host "🚀 Starting database on remote server..." -ForegroundColor Yellow
Write-Host "   Using stable version for better compatibility..." -ForegroundColor Yellow
ssh "${RemoteUser}@${RemoteHost}" "cd ${RemoteDir} && (docker-compose -f docker-compose.stable.yml up -d || docker compose -f docker-compose.stable.yml up -d)"

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
Write-Host "   - pgAdmin Port: 8080 (if using custom setup)" -ForegroundColor White
Write-Host "   - Redis Port: 6379 (if using custom setup)" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To connect to the database:" -ForegroundColor Yellow
Write-Host "   Host: ${RemoteHost}" -ForegroundColor White
Write-Host "   Port: 5432" -ForegroundColor White
Write-Host "   User: nndr" -ForegroundColor White
Write-Host "   Password: nndrpass" -ForegroundColor White
Write-Host "   Database: nndr_db" -ForegroundColor White 