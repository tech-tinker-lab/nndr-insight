# Enhanced PostGIS ARM64 Setup with Kartoza Features

## Overview

This enhanced setup combines the best features of your custom ARM64 PostGIS build with the advantages of the official Kartoza PostGIS image. It provides a production-ready, feature-rich spatial database with comprehensive monitoring and management tools.

## 🚀 Key Features

### Database Features
- **PostGIS 3.5.1** (latest version like Kartoza)
- **ARM64 optimized** source build for maximum performance
- **Comprehensive extensions**: h3, pg_repack, pg_stat_statements, and more
- **Enhanced spatial functions** for data integrity and performance monitoring
- **Production-ready configuration** with optimized WAL settings

### Monitoring & Management
- **Prometheus** for metrics collection
- **Grafana** for visualization dashboards
- **Enhanced pgAdmin** with pre-configured connections
- **Redis** for spatial query caching
- **Automated backups** with retention policies

### Performance Optimizations
- **Multi-stage build** for smaller image size
- **ARM64-specific optimizations**
- **Enhanced logging** with rotation
- **Resource limits** and reservations
- **Connection pooling** and caching

## 📁 File Structure

```
setup/docker/
├── Dockerfile.postgis-arm64          # Enhanced ARM64 Dockerfile
├── docker-compose.custom.yml         # Enhanced docker-compose
├── deploy-enhanced-custom.bat        # Deployment script
└── ENHANCED_SETUP_README.md          # This file

setup/config/
├── pgadmin-servers.json              # pgAdmin server configuration
├── prometheus.yml                    # Prometheus monitoring config
└── postgresql.conf                   # PostgreSQL configuration

setup/scripts/
└── backup.sh                         # Automated backup script
```

## 🛠️ Quick Start

### Local Development

1. **Build and start the enhanced setup:**
   ```bash
   cd setup/docker
   docker compose -f docker-compose.custom.yml up -d --build
   ```

2. **Wait for services to start** (60-90 seconds)

3. **Access the services:**
   - **Database**: `localhost:5432` (nndr/nndrpass)
   - **pgAdmin**: http://localhost:8080 (admin@nndr.local/admin123)
   - **Grafana**: http://localhost:3000 (admin/admin123)
   - **Prometheus**: http://localhost:9090
   - **Redis**: localhost:6379

### Remote Deployment

1. **Run the deployment script:**
   ```bash
   setup/docker/deploy-enhanced-custom.bat
   ```

2. **Follow the prompts** and wait for deployment

3. **Access services** using your remote server IP

## 🔧 Configuration

### Database Configuration

The enhanced setup includes optimized PostgreSQL settings:

```yaml
# Performance settings
shared_buffers: 512MB
effective_cache_size: 2GB
maintenance_work_mem: 128MB
work_mem: 8MB

# WAL settings (your favorite feature)
min_wal_size: 2GB
max_wal_size: 8GB
checkpoint_completion_target: 0.9

# PostGIS settings
postgis.enable_outdb_rasters: true
postgis.gdal_enabled_drivers: ENABLE_ALL
```

### Extensions Included

- **Core PostGIS**: postgis, postgis_topology, postgis_raster
- **Address Standardization**: address_standardizer, address_standardizer_data_us
- **Performance**: pg_stat_statements, pg_repack
- **Spatial**: h3 (hexagonal grid system)
- **Utilities**: uuid-ossp, pg_trgm, btree_gin, btree_gist

## 📊 Monitoring & Management

### Grafana Dashboards

Access Grafana at `http://your-server:3000` to view:
- Database performance metrics
- Spatial query statistics
- Connection monitoring
- Backup status

### Prometheus Metrics

Prometheus collects metrics from:
- PostgreSQL/PostGIS database
- Redis cache
- pgAdmin
- Grafana

### Enhanced Functions

The database includes custom functions for monitoring:

```sql
-- Get comprehensive PostGIS information
SELECT * FROM get_postgis_info();

-- Check spatial data integrity
SELECT * FROM check_spatial_integrity();

-- Monitor database performance
SELECT * FROM get_database_stats();

-- Analyze spatial indexes
SELECT * FROM analyze_spatial_indexes();
```

## 🔄 Backup & Recovery

### Automated Backups

The setup includes automated daily backups:
- **Format**: Custom PostgreSQL format (compressed)
- **Retention**: 7 days
- **Location**: `/backup` volume
- **Exclusions**: Log tables, temp tables, cache tables

### Manual Backup

```bash
# Connect to the backup container
docker exec -it nndr-backup sh

# Run backup manually
/backup.sh
```

### Restore from Backup

```bash
# Connect to database container
docker exec -it nndr-postgis-enhanced psql -U nndr -d nndr_db

# Restore from backup
pg_restore -h localhost -U nndr -d nndr_db /backup/nndr_backup_YYYYMMDD_HHMMSS.sql.gz
```

## 🚀 Performance Features

### ARM64 Optimizations

- **Native ARM64 build** for optimal performance
- **Multi-stage build** for smaller image size
- **Optimized compilation flags** for ARM64 architecture

### Caching Strategy

- **Redis cache** for spatial query results
- **PostgreSQL query cache** with pg_stat_statements
- **Connection pooling** for better resource utilization

### Spatial Optimizations

- **H3 extension** for hexagonal spatial indexing
- **Enhanced spatial functions** for data validation
- **Optimized spatial indexes** with btree_gist

## 🔍 Troubleshooting

### Common Issues

1. **Build failures on ARM64:**
   ```bash
   # Check Docker platform
   docker buildx ls
   
   # Use specific platform
   docker buildx build --platform linux/arm64 .
   ```

2. **Memory issues:**
   ```bash
   # Check container resources
   docker stats nndr-postgis-enhanced
   
   # Adjust memory limits in docker-compose.yml
   ```

3. **Extension loading errors:**
   ```bash
   # Check extension status
   docker exec -it nndr-postgis-enhanced psql -U nndr -d nndr_db -c "SELECT * FROM pg_extension;"
   ```

### Logs and Debugging

```bash
# Database logs
docker logs nndr-postgis-enhanced

# pgAdmin logs
docker logs nndr-pgadmin-enhanced

# Grafana logs
docker logs nndr-grafana

# Prometheus logs
docker logs nndr-monitoring
```

## 🔄 Migration from Previous Versions

### From Simple Setup

1. **Backup existing data:**
   ```bash
   docker exec -it nndr-postgis-simple pg_dump -U nndr_user -d nndr_insight > backup.sql
   ```

2. **Start enhanced setup:**
   ```bash
   docker compose -f docker-compose.custom.yml up -d
   ```

3. **Restore data:**
   ```bash
   docker exec -it nndr-postgis-enhanced psql -U nndr -d nndr_db < backup.sql
   ```

### From Official Kartoza

The enhanced setup is compatible with Kartoza data:
- Same extension set
- Compatible PostGIS version
- Similar configuration structure

## 📈 Scaling Considerations

### Horizontal Scaling

- **Read replicas**: Add additional database containers
- **Load balancing**: Use HAProxy or nginx
- **Sharding**: Implement spatial partitioning

### Vertical Scaling

- **Memory**: Increase `shared_buffers` and `effective_cache_size`
- **CPU**: Adjust `work_mem` and `maintenance_work_mem`
- **Storage**: Use SSD volumes for better I/O

## 🔒 Security Features

- **Network isolation** with custom bridge network
- **Resource limits** to prevent DoS
- **Secure passwords** (change defaults in production)
- **SSL/TLS** support for database connections

## 📞 Support

### Getting Help

1. **Check logs** for error messages
2. **Verify configuration** files
3. **Test connectivity** to all services
4. **Review resource usage** and limits

### Useful Commands

```bash
# Check all container status
docker ps --filter "name=nndr"

# Monitor resource usage
docker stats --no-stream

# Check network connectivity
docker network inspect nndr-network-enhanced

# View volume usage
docker system df -v
```

## 🎯 Next Steps

After successful deployment:

1. **Configure Grafana dashboards** for your specific needs
2. **Set up alerting** in Prometheus
3. **Customize backup schedules** if needed
4. **Implement monitoring** for your application
5. **Optimize spatial queries** using the enhanced functions

## 🌟 Benefits Over Previous Versions

### Compared to Simple Setup
- ✅ Latest PostGIS 3.5.1 (vs package version)
- ✅ Comprehensive monitoring suite
- ✅ Automated backups
- ✅ Enhanced spatial functions
- ✅ Better performance optimization

### Compared to Official Kartoza
- ✅ ARM64 source build optimization
- ✅ Custom spatial analysis functions
- ✅ Enhanced logging and debugging
- ✅ Integrated monitoring stack
- ✅ Automated deployment scripts

This enhanced setup provides the best of both worlds: the performance and customization of your ARM64 builds with the reliability and features of the official Kartoza image. 