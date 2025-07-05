#!/usr/bin/env python3
"""
Startup script for the NNDR Insight API
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the FastAPI server"""
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set default environment variables if not already set
    os.environ.setdefault('PGUSER', 'nndr')
    os.environ.setdefault('PGPASSWORD', 'nndrpass')
    os.environ.setdefault('PGHOST', 'localhost')
    os.environ.setdefault('PGPORT', '5432')
    os.environ.setdefault('PGDATABASE', 'nndr_db')
    
    print("🚀 Starting NNDR Insight API Server")
    print("=" * 50)
    print(f"📁 Working directory: {current_dir}")
    print(f"🗄️  Database: {os.environ.get('PGDATABASE')} on {os.environ.get('PGHOST')}:{os.environ.get('PGPORT')}")
    print(f"👤 Database user: {os.environ.get('PGUSER')}")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 