import sys, os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

print("=== USRN Ingestion Diagnostic ===")

# 1. Check imports
try:
    import fiona
    import geopandas as gpd
    from shapely.geometry import shape
    from backend.services.db_service import get_engine
    from sqlalchemy import text
    print("✅ All required Python modules imported successfully.")
except Exception as e:
    print("❌ Import error:", e)
    sys.exit(1)

# 2. Check database connection
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
try:
    engine = get_engine(
        os.getenv("PGUSER"),
        os.getenv("PGPASSWORD"),
        os.getenv("PGHOST"),
        os.getenv("PGPORT"),
        os.getenv("PGDATABASE")
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Database connection successful.")
except Exception as e:
    print("❌ Database connection error:", e)
    sys.exit(2)

# 3. Check GPKG file and layer
gpkg_path = "backend/data/osopenusrn_202507_gpkg/osopenusrn_202507.gpkg"
layer_name = "openUSRN"
try:
    with fiona.open(gpkg_path, layer=layer_name) as src:
        print(f"✅ GPKG file '{gpkg_path}' and layer '{layer_name}' opened successfully.")
        print(f"   CRS: {src.crs}, Feature count: {len(src)}")
except Exception as e:
    print(f"❌ Error opening GPKG file or layer: {e}")
    sys.exit(3)

print("=== All checks passed! You can now run the full ingestion script. ===") 