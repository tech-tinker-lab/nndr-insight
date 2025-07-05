# PostgreSQL Performance Tuning for NNDR Database

This directory contains scripts and configurations to optimize PostgreSQL performance for handling large NNDR (National Non-Domestic Rates) datasets.

## Overview

The Kartoza PostGIS Docker image provides excellent defaults, but for large datasets, additional tuning is recommended. Since the Kartoza image doesn't support custom `postgresql.conf` files, we apply tuning via SQL commands after the container is running.

## Files

- `performance_tuning.sql` - Comprehensive SQL script with all tuning parameters
- `apply_tuning.sh` - Linux/macOS script to apply tuning
- `apply_tuning.bat` - Windows script to apply tuning
- `README.md` - This documentation

## Quick Start

### 1. Start the Database

```bash
cd setup/docker
docker-compose -f docker-compose.official-kartoza.yml up -d
```

### 2. Apply Performance Tuning

**Linux/macOS:**
```bash
cd setup/database/tuning
chmod +x apply_tuning.sh
./apply_tuning.sh
```

**Windows:**
```cmd
cd setup\database\tuning
apply_tuning.bat
```

## Tuning Parameters Explained

### Memory Settings

- **shared_buffers**: 2GB - Cache for frequently accessed data
- **effective_cache_size**: 6GB - Estimated OS cache size for query planning
- **work_mem**: 64MB - Memory for sorting and hash operations
- **maintenance_work_mem**: 512MB - Memory for maintenance operations

### WAL (Write-Ahead Logging) Settings

- **wal_buffers**: 16MB - Buffer for WAL data
- **max_wal_size**: 2GB - Maximum WAL file size
- **checkpoint_completion_target**: 0.9 - Spreads checkpoint writes over time

### Connection Settings

- **max_connections**: 200 - Maximum concurrent connections
- **statement_timeout**: 5 minutes - Prevents runaway queries
- **idle_in_transaction_session_timeout**: 10 minutes - Closes idle transactions

### Query Planner Settings

- **random_page_cost**: 1.1 - Optimized for SSDs
- **effective_io_concurrency**: 200 - Parallel I/O operations
- **cpu_tuple_cost**: 0.01 - CPU cost for processing tuples

### Autovacuum Settings

- **autovacuum**: on - Automatic cleanup of dead tuples
- **autovacuum_max_workers**: 3 - Number of autovacuum processes
- **autovacuum_vacuum_scale_factor**: 0.2 - When to trigger vacuum

## Monitoring Performance

### 1. Check Current Settings

```sql
SELECT name, setting, unit, context 
FROM pg_settings 
WHERE name IN (
    'shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem',
    'wal_buffers', 'max_wal_size', 'checkpoint_completion_target',
    'max_connections', 'random_page_cost', 'effective_io_concurrency',
    'autovacuum', 'default_statistics_target'
)
ORDER BY name;
```

### 2. Monitor Slow Queries

Queries taking longer than 1 second are automatically logged. Check logs:

```bash
docker logs <container_name>
```

### 3. Check Database Statistics

```sql
-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

## Customization

### Adjusting Memory Settings

For different server configurations, adjust these settings in `performance_tuning.sql`:

```sql
-- For 8GB RAM server
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';

-- For 16GB RAM server  
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';

-- For 32GB RAM server
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
```

### SSD vs HDD Optimization

For HDD storage, adjust these settings:

```sql
ALTER SYSTEM SET random_page_cost = '4.0';
ALTER SYSTEM SET effective_io_concurrency = '2';
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure you're connecting as the `postgres` superuser
2. **Connection Refused**: Ensure the container is running and healthy
3. **Settings Not Applied**: Some settings require a restart; check the `context` column in `pg_settings`

### Reset to Defaults

To reset all settings to defaults:

```sql
ALTER SYSTEM RESET ALL;
SELECT pg_reload_conf();
```

### Verify Tuning Applied

```sql
-- Check if tuning was applied
SELECT name, setting, unit 
FROM pg_settings 
WHERE name = 'shared_buffers' AND setting != '128MB';
```

## Best Practices

1. **Apply tuning after container startup** - Don't modify the docker-compose file
2. **Monitor performance** - Use the provided monitoring queries
3. **Adjust for your data** - Modify settings based on your specific dataset size
4. **Test thoroughly** - Verify performance improvements with your actual queries
5. **Backup before changes** - Always backup your data before applying tuning

## Additional Resources

- [PostgreSQL Tuning Guide](https://www.postgresql.org/docs/current/runtime-config.html)
- [Kartoza PostGIS Documentation](https://github.com/kartoza/docker-postgis)
- [PostGIS Performance Tuning](https://postgis.net/workshops/postgis-intro/tuning.html) 