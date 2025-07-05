#!/bin/bash

# Performance Tuning Application Script
# This script applies the performance tuning settings to the running PostgreSQL container

set -e

# Configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="nndr_db"
DB_USER="postgres"  # Use postgres superuser for system settings
TUNING_SCRIPT="performance_tuning.sql"

echo "🔧 Applying PostgreSQL Performance Tuning..."
echo "=============================================="

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; then
    echo "❌ Error: PostgreSQL is not running or not accessible"
    echo "   Make sure the container is up: docker-compose up -d"
    exit 1
fi

echo "✅ PostgreSQL is running and accessible"

# Apply tuning settings
echo "📝 Applying performance tuning settings..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$TUNING_SCRIPT"

echo "✅ Performance tuning applied successfully!"
echo ""
echo "📊 Current settings summary:"
echo "============================"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
SELECT 
    name, 
    setting, 
    unit, 
    context 
FROM pg_settings 
WHERE name IN (
    'shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem',
    'wal_buffers', 'max_wal_size', 'checkpoint_completion_target',
    'max_connections', 'random_page_cost', 'effective_io_concurrency',
    'autovacuum', 'default_statistics_target'
)
ORDER BY name;
"

echo ""
echo "🎯 Tuning complete! The database is now optimized for large data handling."
echo ""
echo "💡 Tips:"
echo "   - Monitor performance with: docker logs <container_name>"
echo "   - Check slow queries in logs (queries > 1 second are logged)"
echo "   - Use pgAdmin (http://localhost:8080) for database management"
echo "   - Consider running ANALYZE on your tables after data import" 