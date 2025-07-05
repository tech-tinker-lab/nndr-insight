#!/usr/bin/env python3
"""
Database Migration Runner
Command-line interface for running database migrations with tracking.
Similar to Liquibase functionality.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string, print_config, DB_CONFIG
from migration_tracker import MigrationTracker, run_migration_with_tracking, print_migration_status, create_migration_summary
import argparse
import sys
from datetime import datetime

def create_engine_for_db(dbname):
    return sqlalchemy.create_engine(get_connection_string(dbname))

def check_database_exists(engine, dbname):
    """Check if database exists"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :dbname"), {"dbname": dbname})
            return result.fetchone() is not None
    except Exception:
        return False

def create_database_if_not_exists(dbname):
    """Create database if it doesn't exist"""
    print(f"🔍 Checking if database '{dbname}' exists...")
    
    # Connect to default postgres database
    default_engine = sqlalchemy.create_engine(
        f"postgresql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/postgres"
    )
    
    if not check_database_exists(default_engine, dbname):
        print(f"📝 Creating database '{dbname}'...")
        with default_engine.connect() as conn:
            with conn.begin():
                conn.execute(text(f"CREATE DATABASE {dbname}"))
        print(f"✅ Database '{dbname}' created successfully")
    else:
        print(f"✅ Database '{dbname}' already exists")

def run_all_migrations(engine, tracker):
    """Run all available migrations"""
    from migration_tracker import get_available_migrations, MIGRATION_REGISTRY
    
    available_migrations = get_available_migrations()
    pending_migrations = tracker.get_pending_migrations(available_migrations)
    
    if not pending_migrations:
        print("✅ All migrations are up to date!")
        return
    
    print(f"🔄 Found {len(pending_migrations)} pending migrations")
    
    for migration_name in pending_migrations:
        if migration_name in MIGRATION_REGISTRY:
            migration_function = MIGRATION_REGISTRY[migration_name]
            # For now, use a simple content hash - in a real system, you'd store the actual migration content
            migration_content = f"migration_{migration_name}"
            
            try:
                run_migration_with_tracking(tracker, migration_name, migration_content, lambda: migration_function(engine))
            except Exception as e:
                print(f"❌ Migration {migration_name} failed: {e}")
                if input("Continue with remaining migrations? (y/n): ").lower() != 'y':
                    break
        else:
            print(f"⚠️  Migration function not found for: {migration_name}")

def run_specific_migration(engine, tracker, migration_name):
    """Run a specific migration"""
    from migration_tracker import MIGRATION_REGISTRY
    
    if migration_name not in MIGRATION_REGISTRY:
        print(f"❌ Migration '{migration_name}' not found in registry")
        return False
    
    migration_function = MIGRATION_REGISTRY[migration_name]
    migration_content = f"migration_{migration_name}"
    
    try:
        run_migration_with_tracking(tracker, migration_name, migration_content, lambda: migration_function(engine))
        return True
    except Exception as e:
        print(f"❌ Migration {migration_name} failed: {e}")
        return False

def show_status(engine, tracker):
    """Show migration status"""
    print_migration_status(tracker)
    create_migration_summary(tracker)

def show_pending(engine, tracker):
    """Show pending migrations"""
    from migration_tracker import get_available_migrations
    
    available_migrations = get_available_migrations()
    pending_migrations = tracker.get_pending_migrations(available_migrations)
    
    if not pending_migrations:
        print("✅ All migrations are up to date!")
        return
    
    print(f"📋 Pending migrations ({len(pending_migrations)}):")
    for i, migration in enumerate(pending_migrations, 1):
        print(f"  {i}. {migration}")

def reset_migrations(engine, tracker):
    """Reset migration tracking (dangerous!)"""
    print("⚠️  WARNING: This will reset all migration tracking!")
    print("This means all migrations will be re-run on the next execution.")
    print("This should only be used in development environments.")
    
    confirm = input("Are you sure you want to reset migration tracking? (yes/no): ")
    if confirm.lower() == 'yes':
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text("DELETE FROM db_migrations"))
        print("✅ Migration tracking reset")
    else:
        print("❌ Migration reset cancelled")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('command', choices=['run', 'status', 'pending', 'reset', 'create-db'], 
                       help='Migration command to execute')
    parser.add_argument('--migration', '-m', help='Specific migration to run')
    parser.add_argument('--force', '-f', action='store_true', help='Force run migrations')
    
    args = parser.parse_args()
    
    print("🚀 Database Migration Runner")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_config()
    
    try:
        # Create database if needed
        if args.command == 'create-db':
            create_database_if_not_exists(DB_CONFIG['DBNAME'])
            return
        
        # Connect to database
        engine = create_engine_for_db(DB_CONFIG['DBNAME'])
        
        # Initialize migration tracker
        tracker = MigrationTracker(engine)
        
        if args.command == 'run':
            if args.migration:
                print(f"🔄 Running specific migration: {args.migration}")
                run_specific_migration(engine, tracker, args.migration)
            else:
                print("🔄 Running all pending migrations")
                run_all_migrations(engine, tracker)
        
        elif args.command == 'status':
            show_status(engine, tracker)
        
        elif args.command == 'pending':
            show_pending(engine, tracker)
        
        elif args.command == 'reset':
            reset_migrations(engine, tracker)
        
        print(f"\n✅ Migration command '{args.command}' completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 