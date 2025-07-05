# PowerShell script to deploy PostGIS to remote server with secure authentication
# Run this script from the project root directory

param(
    [string]$RemoteHost = "192.168.1.79",
    [string]$RemoteUser = "kmirza",
    [string]$RemoteDir = "/server/postgis",
    [switch]$UsePassword
)

Write-Host "🚀 Deploying PostGIS to remote server..." -ForegroundColor Green

# Function to test SSH connection
function Test-SSHConnection {
    param([string]$ServerHost, [string]$User)
    
    try {
        $result = ssh -o ConnectTimeout=10 -o BatchMode=yes "${User}@${ServerHost}" "echo 'SSH connection successful'" 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Function to setup SSH connection
function Setup-SSHConnection {
    param([string]$ServerHost, [string]$User)
    
    Write-Host "🔑 Setting up SSH connection..." -ForegroundColor Yellow
    
    # Check if SSH key exists
    $sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
    if (-not (Test-Path $sshKeyPath)) {
        Write-Host "⚠️  SSH key not found." -ForegroundColor Yellow
        Write-Host "   To avoid password prompts, generate an SSH key:" -ForegroundColor White
        Write-Host "   ssh-keygen -t rsa -b 4096" -ForegroundColor Cyan
        Write-Host "   Then copy it to the server:" -ForegroundColor White
        Write-Host "   ssh-copy-id ${User}@${Host}" -ForegroundColor Cyan
        Write-Host ""
        return $false
    }
    
    # Test SSH key authentication
    if (Test-SSHConnection -ServerHost $ServerHost -User $User) {
        Write-Host "✅ SSH key authentication working!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⚠️  SSH key authentication failed." -ForegroundColor Yellow
        Write-Host "   To fix this, run: ssh-copy-id ${User}@${ServerHost}" -ForegroundColor Cyan
        Write-Host ""
        return $false
    }
}

# Setup SSH connection
$sshKeyWorking = Setup-SSHConnection -Host $RemoteHost -User $RemoteUser

# If SSH key doesn't work and user wants to use password, setup sshpass
if (-not $sshKeyWorking -and $UsePassword) {
    Write-Host "🔐 Setting up password authentication..." -ForegroundColor Yellow
    
    # Prompt for password once
    $securePassword = Read-Host "Enter password for ${RemoteUser}@${RemoteHost}" -AsSecureString
    $password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
    
    # Create a temporary script with the password
    $tempScript = @"
#!/bin/bash
sshpass -p '$password' ssh -o StrictHostKeyChecking=no ${RemoteUser}@${RemoteHost} "\$@"
"@
    
    $tempScriptPath = "$env:TEMP\ssh_with_pass.sh"
    $tempScript | Out-File -FilePath $tempScriptPath -Encoding ASCII
    chmod +x $tempScriptPath
    
    # Function to run SSH with password
    function Invoke-SSHWithPassword {
        param([string]$Command)
        & $tempScriptPath $Command
    }
    
    $sshCommand = "Invoke-SSHWithPassword"
} else {
    $sshCommand = "ssh"
}

# Check if required files exist
$requiredFiles = @(
    "Dockerfile.postgis-arm64",
    "Dockerfile.postgis-arm64-simple",
    "build-postgis.sh",
    "docker-compose.yml",
    "docker-compose.custom.yml",
    "docker-compose.simple.yml"
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
if ($sshKeyWorking) {
    ssh "${RemoteUser}@${RemoteHost}" "mkdir -p ${RemoteDir}"
} else {
    Invoke-SSHWithPassword "mkdir -p ${RemoteDir}"
}

# Transfer files
Write-Host "📤 Transferring files to remote server..." -ForegroundColor Yellow

$filesToTransfer = @(
    "Dockerfile.postgis-arm64",
    "Dockerfile.postgis-arm64-simple",
    "build-postgis.sh",
    "docker-compose.yml",
    "docker-compose.custom.yml",
    "docker-compose.simple.yml",
    "DOCKER_SETUP.md"
)

foreach ($file in $filesToTransfer) {
    Write-Host "  Transferring $file..." -ForegroundColor Cyan
    if ($sshKeyWorking) {
        scp $file "${RemoteUser}@${RemoteHost}:${RemoteDir}/"
    } else {
        # Use scp with password
        $scpCommand = "sshpass -p '$password' scp $file ${RemoteUser}@${RemoteHost}:${RemoteDir}/"
        Invoke-Expression $scpCommand
    }
}

# Transfer config directory if it exists
if (Test-Path "setup\config") {
    Write-Host "  Transferring setup/config/..." -ForegroundColor Cyan
    if ($sshKeyWorking) {
        scp -r setup\config\ "${RemoteUser}@${RemoteHost}:${RemoteDir}/"
    } else {
        $scpCommand = "sshpass -p '$password' scp -r setup\config\ ${RemoteUser}@${RemoteHost}:${RemoteDir}/"
        Invoke-Expression $scpCommand
    }
}

Write-Host "✅ File transfer completed" -ForegroundColor Green

# Build the image on remote server
Write-Host "🔨 Building PostGIS image on remote server..." -ForegroundColor Yellow
Write-Host "   This will take 10-15 minutes..." -ForegroundColor Yellow

if ($sshKeyWorking) {
    ssh "${RemoteUser}@${RemoteHost}" "cd ${RemoteDir} && chmod +x build-postgis.sh && ./build-postgis.sh"
} else {
    Invoke-SSHWithPassword "cd ${RemoteDir} && chmod +x build-postgis.sh && ./build-postgis.sh"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostGIS image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build PostGIS image" -ForegroundColor Red
    exit 1
}

# Start the database
Write-Host "🚀 Starting database on remote server..." -ForegroundColor Yellow
if ($sshKeyWorking) {
    ssh "${RemoteUser}@${RemoteHost}" "cd ${RemoteDir} && docker compose -f docker-compose.simple.yml up -d"
} else {
    Invoke-SSHWithPassword "cd ${RemoteDir} && docker compose -f docker-compose.simple.yml up -d"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database started successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start database" -ForegroundColor Red
    exit 1
}

# Verify the setup
Write-Host "🔍 Verifying setup..." -ForegroundColor Yellow

# Check if containers are running
if ($sshKeyWorking) {
    $containers = ssh "${RemoteUser}@${RemoteHost}" "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"
} else {
    $containers = Invoke-SSHWithPassword "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep postgis"
}

Write-Host "📊 Container status:" -ForegroundColor Cyan
Write-Host $containers

# Test database connection
Write-Host "🔗 Testing database connection..." -ForegroundColor Yellow
if ($sshKeyWorking) {
    $dbTest = ssh "${RemoteUser}@${RemoteHost}" "docker exec -it `$(docker ps -q --filter 'name=postgis-simple') psql -U nndr_user -d nndr_insight -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet'"
} else {
    $dbTest = Invoke-SSHWithPassword "docker exec -it `$(docker ps -q --filter 'name=postgis-simple') psql -U nndr_user -d nndr_insight -c 'SELECT PostGIS_Version();' 2>/dev/null || echo 'Database not ready yet'"
}

Write-Host $dbTest

# Cleanup temporary script if created
if (-not $sshKeyWorking -and $UsePassword) {
    Remove-Item $tempScriptPath -Force -ErrorAction SilentlyContinue
}

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