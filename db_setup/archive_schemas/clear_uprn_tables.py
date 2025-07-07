#!/usr/bin/env python3
"""
Script to clear UPRN-related tables from the database
Run this before fresh data ingestion to avoid constraint violations
"""

import psycopg2
import logging
from db_config import get_connection_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_uprn_tables():
    """Clear all UPRN-related tables"""
    
    # Tables to clear (in order to respect foreign key constraints)
    tables_to_clear = [
        'master_gazetteer',
        'os_open_uprn', 
        'onspd',
        'code_point_open',
        'os_open_names',
        'lad_boundaries',
        'os_open_map_local'
    ]
    
    try:
        # Connect to database
        conn_str = get_connection_string()
        logger.info("Connecting to database...")
        
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                
                # Disable foreign key checks temporarily
                logger.info("Disabling foreign key checks...")
                cursor.execute("SET session_replication_role = replica;")
                
                for table in tables_to_clear:
                    try:
                        # Check if table exists
                        cursor.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = %s
                            );
                        """, (table,))
                        
                        result = cursor.fetchone()
                        if result and result[0]:
                            # Get row count before deletion
                            cursor.execute(f"SELECT COUNT(*) FROM {table};")
                            count_result = cursor.fetchone()
                            row_count = count_result[0] if count_result else 0
                            
                            # Clear the table
                            logger.info(f"Clearing table {table} ({row_count} rows)...")
                            cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                            
                            logger.info(f"✅ Cleared {row_count} rows from {table}")
                        else:
                            logger.info(f"⚠️ Table {table} does not exist, skipping...")
                            
                    except Exception as e:
                        logger.error(f"❌ Error clearing table {table}: {e}")
                        continue
                
                # Re-enable foreign key checks
                logger.info("Re-enabling foreign key checks...")
                cursor.execute("SET session_replication_role = DEFAULT;")
                
                # Commit changes
                conn.commit()
                logger.info("✅ All UPRN-related tables cleared successfully!")
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
    
    return True

def verify_tables_empty():
    """Verify that the tables are empty"""
    
    tables_to_check = [
        'master_gazetteer',
        'os_open_uprn', 
        'onspd',
        'code_point_open',
        'os_open_names',
        'lad_boundaries',
        'os_open_map_local'
    ]
    
    try:
        conn_str = get_connection_string()
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                
                logger.info("\n📊 Verifying tables are empty:")
                logger.info("-" * 50)
                
                for table in tables_to_check:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table};")
                        count_result = cursor.fetchone()
                        count = count_result[0] if count_result else 0
                        status = "✅ EMPTY" if count == 0 else f"❌ {count} rows"
                        logger.info(f"{table:25} : {status}")
                    except Exception as e:
                        logger.info(f"{table:25} : ⚠️ Table not found")
                        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False
    
    return True

def main():
    """Main execution function"""
    logger.info("🧹 UPRN Tables Cleanup Script")
    logger.info("=" * 50)
    
    # Clear the tables
    if clear_uprn_tables():
        # Verify they're empty
        verify_tables_empty()
        logger.info("\n🎉 Ready for fresh data ingestion!")
    else:
        logger.error("❌ Failed to clear tables")

if __name__ == "__main__":
    main() 