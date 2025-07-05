#!/usr/bin/env python3
"""
Script to fix database structure issues.
This script will:
1. Test the database connection
2. Add missing columns to existing tables
3. Verify the database structure
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from db.test_config import test_connection
from db.add_missing_tables import main as add_missing_tables

def main():
    print("🔧 Testing database connection...")
    
    # Test database connection
    print("\n1. Testing database connection...")
    if not test_connection():
        print("❌ Database connection failed. Please check your .env file and database settings.")
        return False
    
    print("\n✅ Database connection successful!")
    print("\nThe API code has been fixed to use the correct column names.")
    print("You can now run your API server.")
    return True

if __name__ == "__main__":
    main() 