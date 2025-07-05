#!/bin/bash

# Enhanced NNDR PostGIS Backup Script
# This script performs automated backups of the PostGIS database

set -e

# Configuration
BACKUP_DIR="/backup"
DB_HOST="${POSTGRES_HOST:-db}"
DB_USER="${POSTGRES_USER:-nndr}"
DB_NAME="${POSTGRES_DB:-nndr_db}"
DB_PASSWORD="${POSTGRES_PASSWORD:-nndrpass}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/nndr_backup_${DATE}.sql"
COMPRESSED_BACKUP="${BACKUP_FILE}.gz"

# Set password for pg_dump
export PGPASSWORD="$DB_PASSWORD"

echo "🚀 Starting NNDR PostGIS backup at $(date)"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform the backup
echo "📊 Creating database backup..."
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" \
    --verbose \
    --format=custom \
    --compress=9 \
    --exclude-table-data='*.log' \
    --exclude-table-data='*.temp' \
    --exclude-table-data='*.cache' \
    -f "$COMPRESSED_BACKUP"

if [ $? -eq 0 ]; then
    echo "✅ Backup completed successfully: $COMPRESSED_BACKUP"
    
    # Get backup size
    BACKUP_SIZE=$(du -h "$COMPRESSED_BACKUP" | cut -f1)
    echo "📏 Backup size: $BACKUP_SIZE"
    
    # Clean up old backups (keep last 7 days)
    echo "🧹 Cleaning up old backups..."
    find "$BACKUP_DIR" -name "nndr_backup_*.sql.gz" -mtime +7 -delete
    
    # List remaining backups
    echo "📋 Remaining backups:"
    ls -lh "$BACKUP_DIR"/nndr_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    
else
    echo "❌ Backup failed!"
    exit 1
fi

echo "🎉 Backup process completed at $(date)" 