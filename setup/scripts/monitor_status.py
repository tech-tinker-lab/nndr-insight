#!/usr/bin/env python3
"""
File Monitor Status Checker
Provides status information about the file processing system
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

# Database configuration
USER = os.getenv("PGUSER")
PASSWORD = os.getenv("PGPASSWORD")
HOST = os.getenv("PGHOST")
PORT = os.getenv("PGPORT")
DBNAME = os.getenv("PGDATABASE")

def get_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def load_config():
    """Load file monitor configuration"""
    config_path = Path(__file__).parent / "file_monitor_config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

def check_directory_status():
    """Check status of processing directories"""
    project_root = Path(__file__).parent.parent.parent
    config = load_config()
    
    if not config:
        print("❌ Configuration file not found")
        return
    
    print("=" * 60)
    print("DIRECTORY STATUS")
    print("=" * 60)
    
    for dir_name, dir_path in config['directories'].items():
        full_path = project_root / dir_path
        if full_path.exists():
            # Count files
            file_count = len(list(full_path.glob('*')))
            # Get directory size
            total_size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            print(f"📁 {dir_name.upper()}: {file_count} files, {size_mb:.2f} MB")
            print(f"   Path: {full_path}")
            
            # Show recent files
            recent_files = []
            for file_path in full_path.iterdir():
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime > datetime.now() - timedelta(days=1):
                        recent_files.append((file_path.name, mtime))
            
            if recent_files:
                print("   Recent files:")
                for name, mtime in sorted(recent_files, key=lambda x: x[1], reverse=True)[:3]:
                    print(f"     - {name} ({mtime.strftime('%H:%M:%S')})")
        else:
            print(f"❌ {dir_name.upper()}: Directory not found")
            print(f"   Expected: {full_path}")

def check_database_status():
    """Check database table status"""
    print("\n" + "=" * 60)
    print("DATABASE STATUS")
    print("=" * 60)
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Get table counts
                tables = [
                    'os_open_uprn', 'code_point_open', 'onspd', 
                    'os_open_names', 'lad_boundaries', 'os_open_map_local',
                    'os_open_usrn'
                ]
                
                for table in tables:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cur.fetchone()[0]
                        print(f"📊 {table}: {count:,} records")
                    except Exception as e:
                        print(f"❌ {table}: Error - {e}")
                
                # Check for recent activity
                print("\nRecent database activity:")
                try:
                    cur.execute("""
                        SELECT schemaname, tablename, last_vacuum, last_autovacuum
                        FROM pg_stat_user_tables 
                        WHERE schemaname = 'public'
                        ORDER BY last_vacuum DESC NULLS LAST
                        LIMIT 5
                    """)
                    activity = cur.fetchall()
                    
                    for schema, table, vacuum, autovacuum in activity:
                        if vacuum or autovacuum:
                            print(f"   {table}: Last vacuum {vacuum or autovacuum}")
                except Exception as e:
                    print(f"   Error checking activity: {e}")
                    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def check_file_monitor_log():
    """Check file monitor log for recent activity"""
    log_path = Path("file_monitor.log")
    
    print("\n" + "=" * 60)
    print("FILE MONITOR LOG")
    print("=" * 60)
    
    if log_path.exists():
        # Read last 10 lines of log
        with open(log_path, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            
            print("Recent log entries:")
            for line in recent_lines:
                line = line.strip()
                if line:
                    # Extract timestamp and message
                    if ' - ' in line:
                        timestamp, message = line.split(' - ', 1)
                        print(f"   {timestamp}: {message}")
                    else:
                        print(f"   {line}")
    else:
        print("❌ File monitor log not found")

def check_processing_queue():
    """Check if there are files waiting to be processed"""
    project_root = Path(__file__).parent.parent.parent
    incoming_dir = project_root / "setup" / "data" / "incoming"
    
    print("\n" + "=" * 60)
    print("PROCESSING QUEUE")
    print("=" * 60)
    
    if incoming_dir.exists():
        files = list(incoming_dir.glob('*'))
        if files:
            print(f"📋 {len(files)} files waiting for processing:")
            for file_path in files:
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    print(f"   - {file_path.name} ({size_mb:.2f} MB, added {mtime.strftime('%H:%M:%S')})")
        else:
            print("✅ No files waiting for processing")
    else:
        print("❌ Incoming directory not found")

def check_system_health():
    """Overall system health check"""
    print("\n" + "=" * 60)
    print("SYSTEM HEALTH")
    print("=" * 60)
    
    # Check if file monitor is running
    try:
        import psutil
        monitor_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'file_monitor.py' in ' '.join(proc.info['cmdline'] or []):
                    monitor_running = True
                    print(f"✅ File monitor is running (PID: {proc.info['pid']})")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not monitor_running:
            print("❌ File monitor is not running")
            
    except ImportError:
        print("⚠️  psutil not available - cannot check if monitor is running")
    
    # Check disk space
    try:
        project_root = Path(__file__).parent.parent.parent
        disk_usage = project_root.stat()
        print(f"📊 Project directory accessible: ✅")
    except Exception as e:
        print(f"❌ Project directory error: {e}")

def main():
    """Main status check function"""
    print("=" * 60)
    print("FILE PROCESSING SYSTEM STATUS")
    print("=" * 60)
    print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all status checks
    check_directory_status()
    check_database_status()
    check_file_monitor_log()
    check_processing_queue()
    check_system_health()
    
    print("\n" + "=" * 60)
    print("STATUS CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 