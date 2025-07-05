# Docker Setup for NNDR Insight

This directory contains all Docker-related files for the NNDR Insight project, including Dockerfiles, docker-compose configurations, and deployment scripts.

## Directory Structure

```
setup/docker/
├── Dockerfiles/
│   ├── Dockerfile.postgis-arm64-simple      # Simple Ubuntu-based PostGIS for ARM64
│   ├── Dockerfile.postgis-arm64-working     # Working Ubuntu-based PostGIS for ARM64
│   ├── Dockerfile.postgis-arm64-stable      # Stable Debian-based PostGIS for ARM64
│   └── Dockerfile.postgis-arm64             # Custom Alpine-based PostGIS for ARM64
├── docker-compose files/
│   ├── docker-compose.simple.yml            # Simple setup with custom Dockerfile
│   ├── docker-compose.working.yml           # Working setup with custom Dockerfile
│   ├── docker-compose.stable.yml            # Stable setup with custom Dockerfile
│   ├── docker-compose.custom.yml            # Custom setup with performance tuning
│   ├── docker-compose.official.yml          # Official PostGIS image setup
│   └── docker-compose.yml                   # Main docker-compose configuration
├── deployment scripts/
│   ├── deploy-postgis-simple.bat            # Deploy simple setup to remote server
│   ├── deploy-postgis-working.bat           # Deploy working setup to remote server
│   ├── deploy-postgis-fixed.bat             # Deploy fixed setup to remote server
│   ├── deploy-to-remote.bat                 # Main deployment script
│   ├── deploy-to-remote.ps1                 # PowerShell deployment script
│   └── [other deployment scripts...]
├── build scripts/
│   ├── build-postgis-simple.bat             # Build simple PostGIS image
│   ├── build-postgis-simple.sh              # Linux build script for simple setup
│   ├── build-postgis-working.sh             # Linux build script for working setup
│   └── [other build scripts...]
├── data ingestion scripts/
│   ├── run-data-ingestion.bat               # Run data ingestion on Windows
│   ├── run-data-ingestion.ps1               # PowerShell data ingestion script
│   ├── run-data-ingestion-simple.bat        # Simple data ingestion setup
│   └── [other ingestion scripts...]
└── documentation/
    ├── DOCKER_SETUP.md                      # Detailed Docker setup guide
    └── POSTGIS_SIMPLE_README.md             # Simple PostGIS setup guide
```

## Quick Start

### For Local Development

1. **Enhanced Custom PostGIS ARM64** (Recommended):
   ```bash
   cd setup/docker
   docker compose -f docker-compose.custom.yml up -d --build
   ```

2. **Official Kartoza PostGIS** (Alternative Production):
   ```bash
   cd setup/docker
   docker compose -f docker-compose.official-kartoza.yml up -d
   ```

3. **Simple Setup** (Good for Development):
   ```bash
   cd setup/docker
   docker compose -f docker-compose.simple.yml up -d
   ```

4. **Official PostGIS Image**:
   ```bash
   cd setup/docker
   docker compose -f docker-compose.official.yml up -d
   ```

### For Remote Deployment

1. **Deploy Enhanced Custom PostGIS** (Recommended):
   ```bash
   # From project root directory
   setup\docker\deploy-enhanced-custom.bat
   ```

2. **Deploy Official Kartoza PostGIS** (Alternative):
   ```bash
   # From project root directory
   setup\docker\deploy-kartoza-official.bat
   ```

3. **Deploy Simple Setup**:
   ```bash
   # From project root directory
   setup\docker\deploy-postgis-simple.bat
   ```

4. **Or use PowerShell**:
   ```powershell
   # From project root directory
   .\setup\docker\deploy-simple.ps1
   ```

## Configuration Files

All docker-compose files have been updated to use relative paths from the `setup/docker/` directory:

- **Build Context**: `context: ../..` (points to project root)
- **Dockerfile Path**: `dockerfile: setup/docker/Dockerfile.postgis-arm64-simple`
- **Volume Paths**: `../../setup/database/...` (points to database setup files)

## Database Connection Details

After successful deployment:

### Enhanced Custom PostGIS ARM64
- **Host**: `localhost` (local) or your remote server IP
- **Port**: `5432`
- **Database**: `nndr_db`
- **User**: `nndr`
- **Password**: `nndrpass`
- **PostGIS Version**: 3.5.1 (latest)
- **Additional Services**:
  - **pgAdmin**: http://localhost:8080 (admin@nndr.local/admin123)
  - **Grafana**: http://localhost:3000 (admin/admin123)
  - **Prometheus**: http://localhost:9090
  - **Redis**: localhost:6379

### Official Kartoza PostGIS
- **Host**: `localhost` (local) or your remote server IP
- **Port**: `5432`
- **Database**: `nndr_db`
- **User**: `nndr`
- **Password**: `nndrpass`
- **PostGIS Version**: 3.5.x (latest)

### Simple Setup
- **Host**: `localhost` (local) or your remote server IP
- **Port**: `5432`
- **Database**: `nndr_insight`
- **User**: `nndr_user`
- **Password**: `nndr_password`
- **PostGIS Version**: Package version (3.4.x)

## Troubleshooting

### Common Issues

1. **pg_ctl: command not found**: Fixed in latest Dockerfiles by using full paths
2. **Build context errors**: Ensure you're running from the project root directory
3. **Volume mount errors**: Check that database setup files exist in `setup/database/`

### Logs and Debugging

```bash
# Check container logs
docker logs nndr-postgis-simple

# Check container status
docker ps

# Connect to database
docker exec -it nndr-postgis-simple psql -U nndr_user -d nndr_insight
```

## Migration from Root Directory

If you have existing containers or volumes from when Docker files were in the root directory:

1. **Stop existing containers**:
   ```bash
   docker compose down
   ```

2. **Remove old volumes** (if needed):
   ```bash
   docker volume rm postgis_simple_data
   ```

3. **Rebuild with new paths**:
   ```bash
   cd setup/docker
   docker compose -f docker-compose.simple.yml up -d --build
   ```

## Next Steps

After the database is running:

1. **Run database migrations**: Use scripts in `setup/database/`
2. **Ingest data**: Use scripts in `setup/docker/` or `backend/ingest/`
3. **Start the application**: Use the main `docker-compose.yml` for full stack

For detailed setup instructions, see:
- `ENHANCED_SETUP_README.md` - Enhanced PostGIS setup with monitoring
- `DOCKER_SETUP.md` - Complete Docker setup guide
- `POSTGIS_SIMPLE_README.md` - Simple PostGIS setup guide 