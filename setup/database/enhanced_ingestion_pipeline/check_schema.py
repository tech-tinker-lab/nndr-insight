#!/usr/bin/env python3
"""
Simple script to check database schema and identify issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from db_config import get_connection_string
import psycopg2

def check_schema():
    """Check the master_gazetteer table schema"""
    try:
        conn = psycopg2.connect(get_connection_string())
        cur = conn.cursor()
        
        print("=== Master Gazetteer Schema ===")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'master_gazetteer' 
            ORDER BY ordinal_position
        """)
        
        for row in cur.fetchall():
            print(f"{row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        print("\n=== Table Constraints ===")
        cur.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'master_gazetteer'
        """)
        
        for row in cur.fetchall():
            print(f"{row[0]}: {row[1]}")
        
        print("\n=== Foreign Key References ===")
        cur.execute("""
            SELECT 
                tc.constraint_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name='master_gazetteer';
        """)
        
        for row in cur.fetchall():
            print(f"{row[0]}: {row[1]} -> {row[2]}.{row[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking schema: {e}")

if __name__ == "__main__":
    check_schema() 