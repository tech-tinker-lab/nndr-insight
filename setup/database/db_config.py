#!/usr/bin/env python3
"""
Database configuration module for NNDR Insight project.
Handles environment variable loading and database connection settings.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file in the backend folder
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Database connection settings from environment variables
DB_CONFIG = {
    'USER': os.getenv("PGUSER", "nndr"),
    'PASSWORD': os.getenv("PGPASSWORD", "nndrpass"),
    'HOST': os.getenv("PGHOST", "localhost"),
    'PORT': os.getenv("PGPORT", "5432"),
    'DBNAME': os.getenv("PGDATABASE", "nndr_db")
}

def get_connection_string(dbname=None):
    """Get database connection string."""
    if dbname is None:
        dbname = DB_CONFIG['DBNAME']
    
    return f"postgresql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{dbname}"

def print_config():
    """Print current database configuration."""
    print("Database Configuration:")
    print(f"  Host: {DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}")
    print(f"  User: {DB_CONFIG['USER']}")
    print(f"  Database: {DB_CONFIG['DBNAME']}")
    print(f"  Environment file: {env_path}")
    print(f"  Environment file exists: {os.path.exists(env_path)}")

def check_drop_recreate_arg():
    """Check if --drop-recreate argument is provided."""
    return '--drop-recreate' in sys.argv 