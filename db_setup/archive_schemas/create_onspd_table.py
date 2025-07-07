#!/usr/bin/env python3
"""
Create the ONSPD table with proper schema.
"""
import sqlalchemy
from sqlalchemy import text
from db_config import get_connection_string

def create_onspd_table():
    """Create the ONSPD table if it doesn't exist."""
    print("🔧 Creating ONSPD table...")
    
    try:
        engine = sqlalchemy.create_engine(get_connection_string())
        
        with engine.connect() as conn:
            # Create ONSPD table
            onspd_schema = """
            CREATE TABLE IF NOT EXISTS onspd (
                pcds TEXT PRIMARY KEY,
                pcd TEXT,
                lat DOUBLE PRECISION,
                long DOUBLE PRECISION,
                ctry TEXT,
                oslaua TEXT,
                osward TEXT,
                parish TEXT,
                oa11 TEXT,
                lsoa11 TEXT,
                msoa11 TEXT,
                imd TEXT,
                rgn TEXT,
                pcon TEXT,
                ur01ind TEXT,
                oac11 TEXT,
                oseast1m TEXT,
                osnrth1m TEXT,
                dointr TEXT,
                doterm TEXT
            );
            """
            
            conn.execute(text(onspd_schema))
            conn.commit()
            
            print("✅ ONSPD table created successfully!")
            
            # Verify the table was created
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'onspd'
            """))
            
            count = result.scalar()
            if count and count > 0:
                print("✅ ONSPD table verification passed!")
            else:
                print("❌ ONSPD table verification failed!")
                return False
                
    except Exception as e:
        print(f"❌ Error creating ONSPD table: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_onspd_table() 