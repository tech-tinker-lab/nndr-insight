# Simple ARM64 PostGIS Setup

This directory contains a simplified approach to building and deploying PostGIS for ARM64 platforms using pre-built Ubuntu packages instead of building from source.

## Overview

The simplified approach:
- Uses Ubuntu 22.04 as the base image
- Installs PostgreSQL 16 and PostGIS 3 from Ubuntu repositories
- Avoids complex compilation issues
- Provides a reliable, production-ready setup
- Includes all necessary extensions and optimizations

## Files

### Core Files
- `Dockerfile.postgis-arm64-simple` - Main Dockerfile using Ubuntu packages
- `docker-compose.simple.yml` - Docker Compose configuration
- `build-postgis-simple.sh` - Linux/macOS build script
- `build-postgis-simple.bat` - Windows build script
- `deploy-simple.ps1` - PowerShell deployment script

## Quick Start

### 1. Build the Image

**Linux/macOS:**
```bash
chmod +x build-postgis-simple.sh
./build-postgis-simple.sh
```

**Windows:**
```cmd
build-postgis-simple.bat
```

### 2. Start the Container

**Using Docker Compose (Recommended):**
```bash
docker-compose -f docker-compose.simple.yml up -d
```

**Using Docker directly:**
```bash
docker run -d --name nndr-postgis-simple \
  -p 5432:5432 \
  -e POSTGRES_DB=nndr_insight \
  -e POSTGRES_USER=nndr_user \
  -e POSTGRES_PASSWORD=nndr_password \
  nndr-postgis-simple:arm64-v1.0
```

### 3. Test the Connection

```bash
docker exec -it nndr-postgis-simple su - postgres -c 'psql -d nndr_insight -c "SELECT PostGIS_Version();"'
```

## Connection Details

- **Host:** localhost (or your server IP)
- **Port:** 5432
- **Database:** nndr_insight
- **Username:** nndr_user
- **Password:** nndr_password

## Features

### Included Extensions
- PostGIS 3.x (Core, Topology, Raster)
- Address Standardizer
- pg_stat_statements
- uuid-ossp
- pg_trgm
- btree_gin
- btree_gist

### Pre-configured Functions
- `get_postgis_info()` - Returns version information for all PostGIS components
- `check_spatial_integrity()` - Checks spatial data integrity across all tables

### Performance Optimizations
- Optimized PostgreSQL configuration
- Pre-loaded extensions
- Health checks
- Proper user permissions

## Deployment Options

### Local Development
```bash
# Build and start locally
./build-postgis-simple.sh
docker-compose -f docker-compose.simple.yml up -d
```

### Remote ARM64 Server
```powershell
# Build, deploy, and start on remote server
.\deploy-simple.ps1 -RemoteServer "your-server.com" -RemoteUser "your-user"
```

### Step-by-step Remote Deployment
```powershell
# Build only
.\deploy-simple.ps1 -BuildOnly

# Deploy only
.\deploy-simple.ps1 -DeployOnly -RemoteServer "your-server.com" -RemoteUser "your-user"

# Start only
.\deploy-simple.ps1 -StartOnly -RemoteServer "your-server.com" -RemoteUser "your-user"
```

## Advantages of This Approach

### 1. Reliability
- Uses tested, stable Ubuntu packages
- No compilation issues
- Consistent behavior across environments

### 2. Speed
- Faster build times (no compilation)
- Smaller image size
- Quick deployment

### 3. Compatibility
- Works on all ARM64 platforms
- Compatible with various Docker environments
- Minimal dependencies

### 4. Maintenance
- Easy to update (just change package versions)
- Clear dependency management
- Simple troubleshooting

## Troubleshooting

### Build Issues
1. **Docker not running:**
   ```bash
   docker info
   ```

2. **Insufficient memory:**
   ```bash
   docker build --memory=4g --file Dockerfile.postgis-arm64-simple --tag nndr-postgis-simple:arm64-v1.0 .
   ```

3. **Network issues:**
   - Check internet connection
   - Verify DNS resolution
   - Try using a different network

### Runtime Issues
1. **Container won't start:**
   ```bash
   docker logs nndr-postgis-simple
   ```

2. **Connection refused:**
   ```bash
   docker exec -it nndr-postgis-simple su - postgres -c 'pg_isready'
   ```

3. **Permission issues:**
   ```bash
   docker exec -it nndr-postgis-simple ls -la /var/lib/postgresql/data
   ```

### Performance Issues
1. **Slow queries:**
   ```sql
   -- Check PostGIS version and configuration
   SELECT get_postgis_info();
   
   -- Check spatial data integrity
   SELECT * FROM check_spatial_integrity();
   ```

2. **Memory usage:**
   ```bash
   docker stats nndr-postgis-simple
   ```

## Configuration

### Environment Variables
- `POSTGRES_DB` - Database name (default: nndr_insight)
- `POSTGRES_USER` - Database user (default: nndr_user)
- `POSTGRES_PASSWORD` - Database password (default: nndr_password)
- `POSTGIS_ENABLE_OUTDB_RASTERS` - Enable out-of-database rasters (default: 1)
- `POSTGIS_GDAL_ENABLED_DRIVERS` - GDAL drivers (default: ENABLE_ALL)

### Volume Mounts
- `/var/lib/postgresql/data` - Database data directory
- `/docker-entrypoint-initdb.d` - Initialization scripts

### Ports
- `5432` - PostgreSQL port

## Security Considerations

1. **Change default passwords** in production
2. **Use environment variables** for sensitive data
3. **Restrict network access** to the database port
4. **Regular security updates** of the base image
5. **Backup strategies** for data persistence

## Monitoring

### Health Checks
The container includes built-in health checks:
```bash
docker inspect nndr-postgis-simple | grep -A 10 "Health"
```

### Logs
```bash
# View container logs
docker logs nndr-postgis-simple

# Follow logs in real-time
docker logs -f nndr-postgis-simple
```

### Performance Monitoring
```sql
-- Check query statistics
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- Check database size
SELECT pg_size_pretty(pg_database_size('nndr_insight'));

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Backup and Restore

### Backup
```bash
docker exec nndr-postgis-simple su - postgres -c 'pg_dump nndr_insight > /tmp/backup.sql'
docker cp nndr-postgis-simple:/tmp/backup.sql ./backup.sql
```

### Restore
```bash
docker cp ./backup.sql nndr-postgis-simple:/tmp/backup.sql
docker exec nndr-postgis-simple su - postgres -c 'psql nndr_insight < /tmp/backup.sql'
```

## Comparison with Other Approaches

| Feature | Simple (Ubuntu) | Custom Build | Official Image |
|---------|----------------|--------------|----------------|
| Build Time | Fast | Slow | N/A |
| Image Size | Medium | Large | Small |
| ARM64 Support | ✅ | ✅ | ❌ |
| Reliability | High | Medium | High |
| Customization | Medium | High | Low |
| Maintenance | Easy | Hard | Easy |

## Support

For issues with this setup:
1. Check the troubleshooting section above
2. Review Docker and PostgreSQL logs
3. Verify system requirements
4. Test with a fresh build

## Version History

- **v1.0** - Initial release with Ubuntu 22.04 and PostgreSQL 16
- Uses PostGIS 3.x from Ubuntu repositories
- Includes all necessary extensions and optimizations 