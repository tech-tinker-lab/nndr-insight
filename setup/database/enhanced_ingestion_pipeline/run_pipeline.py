#!/usr/bin/env python3
"""
Runner script for the Comprehensive Data Ingestion Pipeline
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_ingestion_pipeline import ComprehensiveIngestionPipeline
from pipeline_config import get_enabled_sources, get_sources_by_type

def setup_logging(log_level: str = 'INFO'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'pipeline_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )

def print_pipeline_info():
    """Print information about the pipeline and available data sources"""
    print("=" * 80)
    print("COMPREHENSIVE DATA INGESTION PIPELINE")
    print("=" * 80)
    
    enabled_sources = get_enabled_sources()
    print(f"\nEnabled Data Sources ({len(enabled_sources)}):")
    print("-" * 60)
    
    for source_name, config in enabled_sources.items():
        print(f"✓ {source_name}")
        print(f"  Description: {config['description']}")
        print(f"  Priority: {config['priority']} | Quality: {config['quality_score']}")
        print(f"  Type: {config['source_type']} | Format: {config['format']}")
        print(f"  File Pattern: {config['file_pattern']}")
        print()
    
    # Group by source type
    print("Data Sources by Type:")
    print("-" * 30)
    for source_type in ['nndr', 'reference', 'property_sales', 'market_analysis', 'economic_indicators']:
        sources = get_sources_by_type(source_type)
        if sources:
            print(f"{source_type.upper()}: {len(sources)} sources")
            for source_name in sources.keys():
                print(f"  - {source_name}")

def validate_environment():
    """Validate that the environment is ready for ingestion"""
    print("\nValidating Environment...")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    if 'enhanced_ingestion_pipeline' not in str(current_dir):
        print("⚠️  Warning: Not running from enhanced_ingestion_pipeline directory")
    
    # Check for required files
    required_files = [
        'comprehensive_ingestion_pipeline.py',
        'pipeline_config.py',
        'run_pipeline.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ Environment validation passed")
    return True

def run_pipeline(data_directory: Optional[str] = None, source_type: Optional[str] = None, dry_run: bool = False):
    """Run the comprehensive ingestion pipeline"""
    
    print(f"\n{'='*20} PIPELINE EXECUTION {'='*20}")
    print(f"Start Time: {datetime.now()}")
    print(f"Data Directory: {data_directory or 'Default'}")
    print(f"Source Type Filter: {source_type or 'All'}")
    print(f"Dry Run: {dry_run}")
    print("=" * 60)
    
    try:
        # Initialize pipeline
        pipeline = ComprehensiveIngestionPipeline(data_directory if data_directory else None)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No data will be inserted")
            # Just validate and show what would be processed
            enabled_sources = get_enabled_sources()
            if source_type:
                enabled_sources = get_sources_by_type(source_type)
            
            print(f"\nWould process {len(enabled_sources)} data sources:")
            for source_name, config in enabled_sources.items():
                print(f"  - {source_name}: {config['file_pattern']}")
            
            print("\n✅ Dry run completed successfully")
            return True
        
        # Run actual ingestion
        success = pipeline.run_complete_ingestion()
        
        if success:
            print("\n✅ Pipeline execution completed successfully!")
            print(f"End Time: {datetime.now()}")
            return True
        else:
            print("\n❌ Pipeline execution failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Pipeline execution failed with error: {e}")
        logging.error(f"Pipeline execution failed: {e}", exc_info=True)
        return False

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Comprehensive Data Ingestion Pipeline')
    parser.add_argument('--data-dir', type=str, help='Data directory path')
    parser.add_argument('--source-type', type=str, choices=['nndr', 'reference', 'property_sales', 'market_analysis', 'economic_indicators'], 
                       help='Filter by source type')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no data insertion)')
    parser.add_argument('--log-level', type=str, default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Logging level')
    parser.add_argument('--info', action='store_true', help='Show pipeline information and exit')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Show pipeline information if requested
    if args.info:
        print_pipeline_info()
        return
    
    # Validate environment
    if not validate_environment():
        print("❌ Environment validation failed. Please check the setup.")
        sys.exit(1)
    
    # Run pipeline
    success = run_pipeline(
        data_directory=args.data_dir,
        source_type=args.source_type,
        dry_run=args.dry_run
    )
    
    if success:
        print("\n🎉 Pipeline completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 