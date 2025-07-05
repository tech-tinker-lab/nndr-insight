# PowerShell script to deploy PostGIS with single password prompt
# Run this script from the project root directory

param(
    [string]$RemoteHost = "192.168.1.79",
    [string]$RemoteUser = "kmirza",
    [string]$RemoteDir = "/server/postgis"
)

Write-Host "🚀 Deploying PostGIS to remote server with single password prompt..." -ForegroundColor Green

# Check if required files exist
$requiredFiles = @(
    "Dockerfile.postgis-arm64",
    "Dockerfile.postgis-arm64-simple", 
    "build-postgis.sh",
    "docker-compose.simple.yml"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Error: Required file '$file' not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required files found" -ForegroundColor Green

# Prompt for password once
$securePassword = Read-Host "Enter password for ${RemoteUser}@${RemoteHost}" -AsSecureString
$password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))

# Create a temporary script that uses the password
$tempScript = @"
#!/bin/bash
sshpass -p '$password' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${RemoteUser}@${RemoteHost} "\$@"
"@

$tempScriptPath = "$env:TEMP\ssh_with_pass.sh"
$tempScript | Out-File -FilePath $tempScriptPath -Encoding ASCII

# Function to run SSH with password
function Invoke-SSHWithPassword {
    param([string]$Command)
    $scpCommand = "sshpass -p '$password' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${RemoteUser}@${RemoteHost} '$Command'"
    Invoke-Expression $scpCommand
}

# Function to run SCP with password
function Invoke-SCPWithPassword {
    param([string]$Source, [string]$Destination)
    $scpCommand = "sshpass -p '$password' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '$Source' ${RemoteUser}@${RemoteHost}:$Destination"
    Invoke-Expression $scpCommand
}

# Create remote directory
Write-Host "📁 Creating remote directory..." -ForegroundColor Yellow
Invoke-SSHWithPassword "mkdir -p ${RemoteDir}"

# Transfer files
Write-Host "📤 Transferring files to remote server..." -ForegroundColor Yellow

$filesToTransfer = @(
    "Dockerfile.postgis-arm64",
    "Dockerfile.postgis-arm64-simple",
    "build-postgis.sh",
    "docker-compose.simple.yml",
    "DOCKER_SETUP.md"
)

foreach ($file in $filesToTransfer) {
    Write-Host "  Transferring $file..." -ForegroundColor Cyan
    Invoke-SCPWithPassword -Source $file -Destination "${RemoteDir}/"
}

# Transfer config directory if it exists
if (Test-Path "setup\config") {
    Write-Host "  Transferring setup/config/..." -ForegroundColor Cyan
    Invoke-SCPWithPassword -Source "setup\config\" -Destination "${RemoteDir}/"
}

Write-Host "✅ File transfer completed" -ForegroundColor Green

# Build the image on remote server
Write-Host "🔨 Building PostGIS image on remote server..." -ForegroundColor Yellow
Write-Host "   This will take 10-15 minutes..." -ForegroundColor Yellow

Invoke-SSHWithPassword "cd ${RemoteDir} && chmod +x build-postgis.sh && ./build-postgis.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostGIS image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build PostGIS image" -ForegroundColor Red
    Remove-Item $tempScriptPath -Force -ErrorAction SilentlyContinue
    exit 1
}

# Start the database
Write-Host "🚀 Starting database on remote server..." -ForegroundColor Yellow
Invoke-SSHWithPassword "cd ${RemoteDir} && docker compose -f docker-compose.simple.yml up -d"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start database" -ForegroundColor Red
    Remove-Item $tempScriptPath -Force -ErrorAction SilentlyContinue
    exit 1
}

# Verify the setup
Write-Host "🔍 Verifying setup..." -ForegroundColor Yellow

# Check if containers are running
$containers = Invoke-SSHWithPassword "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"
Write-Host "📊 Container status:" -ForegroundColor Cyan
Write-Host $containers

# Test database connection
$dbTest = Invoke-SSHWithPassword "docker exec -it `$(docker ps -q --filter 'name=postgis-simple') psql -U nndr_user -d nndr_insight -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet'"
Write-Host "🔗 Testing database connection..." -ForegroundColor Yellow
Write-Host $dbTest

# Cleanup
Remove-Item $tempScriptPath -Force -ErrorAction SilentlyContinue

Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   - Remote Host: ${RemoteHost}" -ForegroundColor White
Write-Host "   - Database Port: 5432" -ForegroundColor White
Write-Host "   - Database: nndr_insight" -ForegroundColor White
Write-Host "   - Username: nndr_user" -ForegroundColor White
Write-Host "   - Password: nndr_password" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To connect to the database:" -ForegroundColor Yellow
Write-Host "   Host: ${RemoteHost}" -ForegroundColor White
Write-Host "   Port: 5432" -ForegroundColor White
Write-Host "   User: nndr_user" -ForegroundColor White
Write-Host "   Password: nndr_password" -ForegroundColor White
Write-Host "   Database: nndr_insight" -ForegroundColor White 