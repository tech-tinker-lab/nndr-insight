# Simple Kartoza PostGIS Deployment Script
# Deploys only the basic PostGIS setup without monitoring

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [Parameter(Mandatory=$false)]
    [string]$RemotePath = "/server/postgis"
)

Write-Host "🚀 Deploying Kartoza PostGIS to $ServerIP" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Create remote directory
Write-Host "📁 Creating remote directory..." -ForegroundColor Yellow
ssh $Username@$ServerIP "mkdir -p $RemotePath"

# Copy docker-compose file
Write-Host "📋 Copying docker-compose file..." -ForegroundColor Yellow
scp "setup/docker/docker-compose.official-kartoza.yml" "$Username@$ServerIP`:$RemotePath/docker-compose.yml"

# Deploy and start
Write-Host "🐳 Starting PostGIS container..." -ForegroundColor Yellow
ssh $Username@$ServerIP "cd $RemotePath && docker-compose down --remove-orphans && docker-compose up -d"

# Wait for container to be ready
Write-Host "⏳ Waiting for container to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
Write-Host "🔍 Checking container status..." -ForegroundColor Yellow
ssh $Username@$ServerIP "cd $RemotePath && docker-compose ps"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Database Details:" -ForegroundColor Cyan
Write-Host "   Host: $ServerIP" -ForegroundColor White
Write-Host "   Port: 5432" -ForegroundColor White
Write-Host "   Database: nndr_db" -ForegroundColor White
Write-Host "   User: nndr" -ForegroundColor White
Write-Host "   Password: nndrpass" -ForegroundColor White
Write-Host ""
Write-Host "🌐 pgAdmin (if enabled):" -ForegroundColor Cyan
Write-Host "   URL: http://$ServerIP`:8080" -ForegroundColor White
Write-Host "   Email: admin@nndr.local" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Useful commands:" -ForegroundColor Cyan
Write-Host "   View logs: ssh $Username@$ServerIP 'cd $RemotePath && docker-compose logs -f'" -ForegroundColor White
Write-Host "   Stop: ssh $Username@$ServerIP 'cd $RemotePath && docker-compose down'" -ForegroundColor White
Write-Host "   Restart: ssh $Username@$ServerIP 'cd $RemotePath && docker-compose restart'" -ForegroundColor White 