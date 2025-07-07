#!/usr/bin/env python3
"""
File Monitor and Auto-Processing System
Watches a directory for new files and automatically runs appropriate ingestion scripts
"""

import os
import sys
import time
import logging
import subprocess
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
from datetime import datetime
import json
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileProcessor:
    """Handles file processing based on file patterns"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.processed_dir = self.project_root / "setup" / "data" / "processed"
        self.failed_dir = self.project_root / "setup" / "data" / "failed"
        self.processing_dir = self.project_root / "setup" / "data" / "processing"
        
        # Create directories if they don't exist
        for dir_path in [self.processed_dir, self.failed_dir, self.processing_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # File pattern to script mapping
        self.file_patterns = {
            # OS UPRN data
            'osopenuprn_*.csv': {
                'script': 'ingest_os_uprn_fast.py',
                'description': 'OS Open UPRN Data',
                'priority': 1
            },
            # CodePoint Open data
            'codepo_*.csv': {
                'script': 'ingest_codepoint.py',
                'description': 'CodePoint Open Postcodes',
                'priority': 2
            },
            # ONSPD data
            'ONSPD_*.csv': {
                'script': 'ingest_onspd.py',
                'description': 'ONS Postcode Directory',
                'priority': 2
            },
            # OS Open Names data
            'opname_*.csv': {
                'script': 'ingest_os_open_names.py',
                'description': 'OS Open Names',
                'priority': 2
            },
            # LAD Boundaries data
            'LAD_*.shp': {
                'script': 'ingest_lad_boundaries.py',
                'description': 'LAD Boundaries',
                'priority': 1
            },
            # OS Open Map Local data
            '*.gml': {
                'script': 'ingest_os_open_map_local.py',
                'description': 'OS Open Map Local',
                'priority': 3
            },
            # Generic CSV files (fallback)
            '*.csv': {
                'script': 'ingest_generic_csv.py',
                'description': 'Generic CSV Data',
                'priority': 5
            }
        }
    
    def get_script_for_file(self, filename):
        """Determine which script to use for a given file"""
        for pattern, config in self.file_patterns.items():
            if self._matches_pattern(filename, pattern):
                return config
        return None
    
    def _matches_pattern(self, filename, pattern):
        """Check if filename matches pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def move_to_processing(self, file_path):
        """Move file to processing directory"""
        try:
            processing_path = self.processing_dir / file_path.name
            shutil.move(str(file_path), str(processing_path))
            logger.info(f"Moved {file_path.name} to processing directory")
            return processing_path
        except Exception as e:
            logger.error(f"Error moving file to processing: {e}")
            return None
    
    def move_to_processed(self, file_path, success=True):
        """Move file to processed or failed directory"""
        try:
            if success:
                target_dir = self.processed_dir
                target_path = target_dir / file_path.name
                shutil.move(str(file_path), str(target_path))
                logger.info(f"Moved {file_path.name} to processed directory")
            else:
                target_dir = self.failed_dir
                target_path = target_dir / file_path.name
                shutil.move(str(file_path), str(target_path))
                logger.error(f"Moved {file_path.name} to failed directory")
            
            return target_path
        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return None
    
    def run_ingestion_script(self, script_name, file_path):
        """Run the appropriate ingestion script"""
        try:
            script_path = self.project_root / "setup" / "scripts" / script_name
            
            if not script_path.exists():
                logger.error(f"Ingestion script not found: {script_path}")
                return False
            
            logger.info(f"Running {script_name} for {file_path.name}")
            
            # Run the script with the file path as argument
            result = subprocess.run([
                sys.executable, str(script_path), str(file_path)
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info(f"Successfully processed {file_path.name}")
                return True
            else:
                logger.error(f"Script failed for {file_path.name}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running ingestion script: {e}")
            return False
    
    def process_file(self, file_path):
        """Process a single file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"File no longer exists: {file_path}")
            return
        
        logger.info(f"Processing file: {file_path.name}")
        
        # Get script configuration
        script_config = self.get_script_for_file(file_path.name)
        
        if not script_config:
            logger.warning(f"No script found for file: {file_path.name}")
            self.move_to_processed(file_path, success=False)
            return
        
        logger.info(f"Using script: {script_config['script']} for {script_config['description']}")
        
        # Move file to processing directory
        processing_path = self.move_to_processing(file_path)
        if not processing_path:
            return
        
        try:
            # Run the ingestion script
            success = self.run_ingestion_script(script_config['script'], processing_path)
            
            # Move file to appropriate final directory
            self.move_to_processed(processing_path, success=success)
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            self.move_to_processed(processing_path, success=False)

class FileHandler(FileSystemEventHandler):
    """Handles file system events"""
    
    def __init__(self, processor):
        self.processor = processor
        self.processing_files = set()
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Skip files that are being moved by our system
        if any(dir_name in str(file_path) for dir_name in ['processed', 'failed', 'processing']):
            return
        
        # Skip temporary files
        if file_path.name.startswith('.') or file_path.name.endswith('.tmp'):
            return
        
        # Add to processing set to avoid duplicate processing
        if file_path.name in self.processing_files:
            return
        
        self.processing_files.add(file_path.name)
        
        # Process the file
        try:
            self.processor.process_file(file_path)
        finally:
            self.processing_files.discard(file_path.name)

def create_ingestion_scripts():
    """Create missing ingestion scripts based on patterns"""
    scripts_dir = Path(__file__).parent.parent.parent / "setup" / "scripts"
    
    # Template for generic CSV ingestion
    generic_csv_template = '''#!/usr/bin/env python3
"""
Generic CSV Ingestion Script
"""

import sys
import os
sys.path.append('setup/database')

from db_config import get_connection_string
import pandas as pd
import psycopg2

def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_generic_csv.py <csv_file_path>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    print(f"Processing generic CSV file: {csv_file}")
    
    # Add your generic CSV processing logic here
    print("Generic CSV processing not yet implemented")
    sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # Create generic CSV script if it doesn't exist
    generic_script = scripts_dir / "ingest_generic_csv.py"
    if not generic_script.exists():
        with open(generic_script, 'w') as f:
            f.write(generic_csv_template)
        os.chmod(generic_script, 0o755)
        logger.info("Created generic CSV ingestion script")

def main():
    """Main function to run the file monitor"""
    # Create missing scripts
    create_ingestion_scripts()
    
    # Set up directories
    project_root = Path(__file__).parent.parent.parent
    watch_dir = project_root / "setup" / "data" / "incoming"
    watch_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("FILE MONITOR AND AUTO-PROCESSING SYSTEM")
    logger.info("=" * 60)
    logger.info(f"Watching directory: {watch_dir}")
    logger.info(f"Processed files: {project_root / 'setup' / 'data' / 'processed'}")
    logger.info(f"Failed files: {project_root / 'setup' / 'data' / 'failed'}")
    logger.info("=" * 60)
    
    # Create processor and handler
    processor = FileProcessor()
    handler = FileHandler(processor)
    
    # Set up observer
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    
    try:
        logger.info("File monitor started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping file monitor...")
        observer.stop()
    
    observer.join()
    logger.info("File monitor stopped.")

if __name__ == "__main__":
    main() 