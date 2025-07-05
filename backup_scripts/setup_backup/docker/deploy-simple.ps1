# PowerShell deployment script for Simple ARM64 PostGIS
# This version uses pre-built Ubuntu packages instead of building from source

param(
    [string]$RemoteServer = "",
    [string]$RemoteUser = "",
    [string]$RemotePath = "/opt/nndr-insight",
    [switch]$BuildOnly,
    [switch]$DeployOnly,
    [switch]$StartOnly
)

# Configuration
$ImageName = "nndr-postgis-simple"
$Tag = "arm64-v1.0"
$FullImageName = "$ImageName`:$Tag"
$ComposeFile = "docker-compose.simple.yml"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Simple ARM64 PostGIS Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Image: $FullImageName" -ForegroundColor Yellow
Write-Host "Platform: linux/arm64" -ForegroundColor Yellow
Write-Host "Strategy: Pre-built Ubuntu packages" -ForegroundColor Yellow
Write-Host ""

# Function to check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to build the image
function Build-Image {
    Write-Host "Building PostGIS image..." -ForegroundColor Green
    Write-Host "This may take a few minutes..." -ForegroundColor Yellow
    
    docker build `
        --platform linux/arm64 `
        --file Dockerfile.postgis-arm64-simple `
        --tag $FullImageName `
        --progress=plain `
        .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build completed successfully!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        return $false
    }
}

# Function to deploy to remote server
function Deploy-ToRemote {
    param([string]$Server, [string]$User, [string]$Path)
    
    Write-Host "Deploying to remote server: $Server" -ForegroundColor Green
    
    # Create remote directory
    $CreateDirCmd = "ssh $User@$Server 'mkdir -p $Path'"
    Write-Host "Creating remote directory..." -ForegroundColor Yellow
    Invoke-Expression $CreateDirCmd
    
    # Copy files to remote server
    $FilesToCopy = @(
        "Dockerfile.postgis-arm64-simple",
        "docker-compose.simple.yml",
        "build-postgis-simple.sh"
    )
    
    foreach ($File in $FilesToCopy) {
        if (Test-Path $File) {
            Write-Host "Copying $File to remote server..." -ForegroundColor Yellow
            $CopyCmd = "scp $File $User@$Server`:$Path/"
            Invoke-Expression $CopyCmd
        } else {
            Write-Host "Warning: $File not found" -ForegroundColor Yellow
        }
    }
    
    # Copy setup directory if it exists
    if (Test-Path "setup") {
        Write-Host "Copying setup directory to remote server..." -ForegroundColor Yellow
        $CopySetupCmd = "scp -r setup $User@$Server`:$Path/"
        Invoke-Expression $CopySetupCmd
    }
    
    Write-Host "✅ Deployment completed!" -ForegroundColor Green
}

# Function to start services on remote server
function Start-RemoteServices {
    param([string]$Server, [string]$User, [string]$Path)
    
    Write-Host "Starting services on remote server..." -ForegroundColor Green
    
    $StartCmd = "ssh $User@$Server 'cd $Path && docker-compose -f $ComposeFile up -d'"
    Invoke-Expression $StartCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Connection details:" -ForegroundColor Cyan
        Write-Host "  Host: $Server" -ForegroundColor White
        Write-Host "  Port: 5432" -ForegroundColor White
        Write-Host "  Database: nndr_insight" -ForegroundColor White
        Write-Host "  Username: nndr_user" -ForegroundColor White
        Write-Host "  Password: nndr_password" -ForegroundColor White
        Write-Host ""
        Write-Host "To test the connection:" -ForegroundColor Cyan
        Write-Host "  ssh $User@$Server 'docker exec -it nndr-postgis-simple su - postgres -c \"psql -d nndr_insight -c \\\"SELECT PostGIS_Version();\\\"\"'" -ForegroundColor White
    } else {
        Write-Host "❌ Failed to start services!" -ForegroundColor Red
    }
}

# Main execution
if (-not (Test-Docker)) {
    Write-Host "ERROR: Docker is not running or not accessible" -ForegroundColor Red
    exit 1
}

# Check if we're on ARM64 platform
$Arch = $env:PROCESSOR_ARCHITECTURE
if ($Arch -ne "ARM64") {
    Write-Host "WARNING: Building on non-ARM64 platform ($Arch)" -ForegroundColor Yellow
    Write-Host "This image is designed for ARM64 but can be built on other platforms" -ForegroundColor Yellow
    Write-Host ""
}

# Build phase
if (-not $DeployOnly -and -not $StartOnly) {
    if (-not (Build-Image)) {
        exit 1
    }
}

# Deploy phase
if (-not $BuildOnly -and -not $StartOnly -and $RemoteServer) {
    if (-not $RemoteUser) {
        Write-Host "ERROR: Remote user is required for deployment" -ForegroundColor Red
        exit 1
    }
    
    Deploy-ToRemote -Server $RemoteServer -User $RemoteUser -Path $RemotePath
}

# Start phase
if (-not $BuildOnly -and -not $DeployOnly -and $RemoteServer) {
    if (-not $RemoteUser) {
        Write-Host "ERROR: Remote user is required for starting services" -ForegroundColor Red
        exit 1
    }
    
    Start-RemoteServices -Server $RemoteServer -User $RemoteUser -Path $RemotePath
}

# Local start if no remote server specified
if (-not $BuildOnly -and -not $DeployOnly -and -not $StartOnly -and -not $RemoteServer) {
    Write-Host "Starting services locally..." -ForegroundColor Green
    docker-compose -f $ComposeFile up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Connection details:" -ForegroundColor Cyan
        Write-Host "  Host: localhost" -ForegroundColor White
        Write-Host "  Port: 5432" -ForegroundColor White
        Write-Host "  Database: nndr_insight" -ForegroundColor White
        Write-Host "  Username: nndr_user" -ForegroundColor White
        Write-Host "  Password: nndr_password" -ForegroundColor White
        Write-Host ""
        Write-Host "To test the connection:" -ForegroundColor Cyan
        Write-Host "  docker exec -it nndr-postgis-simple su - postgres -c 'psql -d nndr_insight -c \"SELECT PostGIS_Version();\"'" -ForegroundColor White
    } else {
        Write-Host "❌ Failed to start services!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Deployment completed!" -ForegroundColor Green 