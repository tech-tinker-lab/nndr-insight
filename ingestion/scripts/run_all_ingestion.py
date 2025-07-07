#!/usr/bin/env python3
"""
Master Ingestion Script for NNDR Insight Data Pipeline

This script runs all ingestion scripts in the correct order:
1. Reference datasets (OS Open UPRN, Code Point Open, ONSPD, etc.)
2. Address datasets (OS Open Names, etc.)
3. Street datasets (OS Open Map Local, OS Open USRN, etc.)
4. NNDR datasets (Properties, Ratepayers, Valuations, etc.)

Usage:
    python run_all_ingestion.py [--skip-reference] [--skip-address] [--skip-street] [--skip-nndr]
"""

import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

# Define ingestion scripts in order
INGESTION_SCRIPTS = {
    'reference': [
        'ingest_os_open_uprn.py',
        'ingest_code_point_open.py', 
        'ingest_onspd.py'
    ],
    'address': [
        'ingest_os_open_names.py'
    ],
    'street': [
        'ingest_os_open_map_local.py',
        'ingest_os_open_usrn.py'
    ],
    'nndr': [
        'ingest_nndr_properties.py',
        'ingest_nndr_ratepayers.py',
        'ingest_valuations.py'
    ]
}

def run_script(script_path):
    """Run a single ingestion script and return success status."""
    try:
        logging.info(f"Running: {script_path}")
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=os.path.dirname(script_path))
        
        if result.returncode == 0:
            logging.info(f"✓ Success: {script_path}")
            return True
        else:
            logging.error(f"✗ Failed: {script_path}")
            logging.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"✗ Exception running {script_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run all ingestion scripts')
    parser.add_argument('--skip-reference', action='store_true', help='Skip reference datasets')
    parser.add_argument('--skip-address', action='store_true', help='Skip address datasets')
    parser.add_argument('--skip-street', action='store_true', help='Skip street datasets')
    parser.add_argument('--skip-nndr', action='store_true', help='Skip NNDR datasets')
    
    args = parser.parse_args()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    logging.info("Starting NNDR Insight Data Ingestion Pipeline")
    logging.info(f"Script directory: {script_dir}")
    
    total_scripts = 0
    successful_scripts = 0
    
    # Run scripts by category
    for category, scripts in INGESTION_SCRIPTS.items():
        if getattr(args, f'skip_{category}', False):
            logging.info(f"Skipping {category} datasets")
            continue
            
        logging.info(f"\n=== Processing {category.upper()} datasets ===")
        
        for script in scripts:
            script_path = script_dir / script
            if script_path.exists():
                total_scripts += 1
                if run_script(str(script_path)):
                    successful_scripts += 1
            else:
                logging.warning(f"Script not found: {script_path}")
    
    # Summary
    logging.info(f"\n=== INGESTION SUMMARY ===")
    logging.info(f"Total scripts: {total_scripts}")
    logging.info(f"Successful: {successful_scripts}")
    logging.info(f"Failed: {total_scripts - successful_scripts}")
    
    if successful_scripts == total_scripts:
        logging.info("🎉 All ingestion scripts completed successfully!")
        return 0
    else:
        logging.error("❌ Some ingestion scripts failed. Check the log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 