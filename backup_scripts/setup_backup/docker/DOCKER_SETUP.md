# NNDR Insight - Docker Setup Guide

This guide covers the Docker setup options for the NNDR Insight project, including high-performance PostGIS configurations optimized for ARM64 architecture.

## Quick Start Options

### Option 1: Use Existing PostGIS Image (Recommended for most users)
```bash
# Start with optimized existing image
docker-compose up -d db
```

### Option 2: Build Custom High-Performance Image
```bash
# Build custom optimized image
./build-postgis.sh

# Use custom image
docker-compose -f docker-compose.custom.yml up -d
```

## Docker Compose Files

### 1. `docker-compose.yml` - Standard Setup
- Uses official PostGIS Alpine image
- Optimized for ARM64
- Includes performance tuning
- Suitable for development and production

### 2. `docker-compose.custom.yml` - High-Performance Setup
- Uses custom-built PostGIS image
- Maximum performance optimizations
- Includes pgAdmin and Redis
- Suitable for production workloads

## Performance Optimizations

### Database Configuration
The Docker setup includes several performance optimizations:

#### Memory Settings
- `shared_buffers`: 256MB (standard) / 512MB (custom)
- `effective_cache_size`: 1GB (standard) / 2GB (custom)
- `maintenance_work_mem`: 64MB (standard) / 128MB (custom)
- `work_mem`: 4MB (standard) / 8MB (custom)

#### Connection Settings
- `max_connections`: 200
- `checkpoint_completion_target`: 0.9
- `wal_buffers`: 16MB (standard) / 32MB (custom)

#### PostGIS Optimizations
- `postgis.enable_outdb_rasters`: true
- `postgis.gdal_enabled_drivers`: ENABLE_ALL
- `shared_preload_libraries`: pg_stat_statements

## Custom PostGIS Image

### Features
- **Multi-stage build** for smaller final image
- **ARM64 optimized** compilation
- **Latest PostGIS 3.4.4** with all extensions
- **Performance tuned** PostgreSQL settings
- **Built-in monitoring** with pg_stat_statements

### Building the Custom Image
```bash
# Make script executable (if needed)
chmod +x build-postgis.sh

# Build the image
./build-postgis.sh
```

### Build Process
1. **Base Stage**: Install build dependencies
2. **Builder Stage**: Compile PostGIS from source
3. **Final Stage**: Create optimized runtime image

### Build Time
- **First build**: 10-15 minutes
- **Subsequent builds**: 5-10 minutes (with Docker layer caching)

## Architecture Support

### ARM64 (Apple Silicon, ARM servers)
- ✅ Full support with optimized builds
- ✅ Native performance
- ✅ All extensions available

### x86_64 (Intel/AMD)
- ✅ Compatible via emulation
- ✅ Slightly reduced performance
- ✅ All functionality available

## Services Overview

### Database Service (`db`)
- **Image**: `postgis/postgis:16-3.4-alpine` or custom built
- **Port**: 5432
- **Health Check**: Automatic PostgreSQL readiness check
- **Restart Policy**: Unless stopped
- **Resource Limits**: Configurable memory and CPU

### Optional Services

#### pgAdmin (Database Management)
- **Port**: 8080
- **Credentials**: admin@nndr.local / admin123
- **Features**: Web-based PostgreSQL administration

#### Redis (Caching)
- **Port**: 6379
- **Memory**: 256MB limit
- **Features**: Spatial query result caching

## Environment Variables

### Database Configuration
```bash
POSTGRES_USER=nndr
POSTGRES_PASSWORD=nndrpass
POSTGRES_DB=nndr_db
POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C
POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
POSTGRES_MAX_CONNECTIONS=200
```

### PostGIS Configuration
```bash
POSTGIS_ENABLE_OUTDB_RASTERS=1
POSTGIS_GDAL_ENABLED_DRIVERS=ENABLE_ALL
```

## Volume Management

### Data Persistence
- `db_data`: PostgreSQL data directory
- `pgadmin_data`: pgAdmin configuration
- `redis_data`: Redis persistence

### Configuration Files
- `./setup/config/postgresql.conf`: PostgreSQL configuration
- Mounted to container for runtime configuration

## Health Checks

### Database Health Check
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U nndr -d nndr_db"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Redis Health Check
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Performance Monitoring

### Built-in Extensions
- `pg_stat_statements`: Query performance monitoring
- `pg_stat_statements`: Connection and activity monitoring

### Custom Functions
- `get_postgis_info()`: Version information
- `check_spatial_integrity()`: Spatial data validation

## Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check Docker is running
docker info

# Check available disk space
df -h

# Check Docker buildx support
docker buildx version
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Check database connections
docker exec -it <container> psql -U nndr -d nndr_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check PostGIS extensions
docker exec -it <container> psql -U nndr -d nndr_db -c "SELECT * FROM get_postgis_info();"
```

#### Connection Issues
```bash
# Check if database is ready
docker exec -it <container> pg_isready -U nndr -d nndr_db

# Check logs
docker logs <container>
```

### Logs and Debugging
```bash
# View database logs
docker logs <db-container>

# Connect to database
docker exec -it <db-container> psql -U nndr -d nndr_db

# Check PostGIS version
docker exec -it <db-container> psql -U nndr -d nndr_db -c "SELECT PostGIS_Version();"
```

## Production Considerations

### Security
- Change default passwords
- Use secrets management
- Restrict network access
- Enable SSL connections

### Backup Strategy
```bash
# Create backup
docker exec <container> pg_dump -U nndr nndr_db > backup.sql

# Restore backup
docker exec -i <container> psql -U nndr nndr_db < backup.sql
```

### Scaling
- Use connection pooling (PgBouncer)
- Implement read replicas
- Consider TimescaleDB for time-series data
- Use Redis for query result caching

## Migration from Existing Setup

### If you have existing data:
```bash
# Stop existing containers
docker-compose down

# Backup existing data
docker exec <old-container> pg_dump -U nndr nndr_db > migration_backup.sql

# Start new setup
docker-compose up -d db

# Restore data
docker exec -i <new-container> psql -U nndr nndr_db < migration_backup.sql
```

## Next Steps

1. **Choose your setup**: Standard or custom image
2. **Build and start**: Use the appropriate docker-compose file
3. **Verify setup**: Check health checks and connectivity
4. **Run migrations**: Use the setup scripts to initialize the database
5. **Ingest data**: Load your NNDR and spatial data

For more information, see the main project README and setup documentation. 