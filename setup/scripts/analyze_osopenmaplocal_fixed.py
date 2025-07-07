import os
import glob
import fiona
from dotenv import load_dotenv

# Load .env file from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

GML_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'data', 'opmplc_gml3_gb', 'data')

def analyze_gml_file(filepath):
    """Analyze a GML file and display detailed information"""
    print(f"🗺️ Analyzing: {os.path.basename(filepath)}")
    print("=" * 60)
    
    try:
        with fiona.open(filepath, driver="GML") as src:
            # Get file metadata
            print(f"📁 File: {filepath}")
            print(f"📊 Total Features: {len(src)}")
            print(f"🗺️ CRS: {src.crs}")
            print(f"📐 Bounds: {src.bounds}")
            print(f"🏗️ Schema: {src.schema}")
            print()
            
            # Analyze first few features
            print("📋 Sample Records (4-5):")
            print("-" * 60)
            
            feature_count = 0
            themes = set()
            descriptive_groups = set()
            geometry_types = set()
            
            for feature in src:
                if feature_count >= 5:  # Show only first 5 records
                    break
                    
                feature_count += 1
                props = feature["properties"]
                geom = feature["geometry"]
                
                print(f"Record {feature_count}:")
                print(f"  🆔 FID: {feature.get('id', 'N/A')}")
                
                # Show all properties
                print(f"  📋 Properties:")
                for key, value in props.items():
                    print(f"    {key}: {value}")
                
                # Show geometry info
                if geom:
                    print(f"  📐 Geometry Type: {geom.get('type', 'Unknown')}")
                    if 'coordinates' in geom:
                        coords = geom['coordinates']
                        if isinstance(coords, list) and len(coords) > 0:
                            print(f"  📍 First coordinate: {coords[0]}")
                            print(f"  📍 Total coordinates: {len(coords)}")
                else:
                    print(f"  📐 Geometry: None")
                
                print()
            
            # Show summary statistics
            print("📊 File Summary:")
            print("-" * 60)
            print(f"📁 Total Features Analyzed: {feature_count}")
            
            # Collect all unique property values
            all_props = {}
            with fiona.open(filepath, driver="GML") as src2:
                for feature in src2:
                    props = feature["properties"]
                    for key, value in props.items():
                        if key not in all_props:
                            all_props[key] = set()
                        all_props[key].add(str(value))
            
            print(f"🔍 All Properties Found:")
            for key, values in all_props.items():
                if len(values) <= 10:  # Show all if 10 or fewer
                    print(f"  {key}: {', '.join(sorted(values))}")
                else:  # Show first 5 if more
                    print(f"  {key}: {', '.join(sorted(list(values)[:5]))}... ({len(values)} total)")
            
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")
        import traceback
        traceback.print_exc()

def list_available_files():
    """List all available GML files"""
    files = glob.glob(os.path.join(GML_ROOT, "**", "*.gml"), recursive=True)
    files = sorted(files)
    
    print(f"📂 Available GML Files ({len(files)} total):")
    print("-" * 60)
    
    for i, filepath in enumerate(files[:20]):  # Show first 20 files
        filename = os.path.basename(filepath)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"{i+1:2d}. {filename} ({size_mb:.1f} MB)")
    
    if len(files) > 20:
        print(f"... and {len(files) - 20} more files")
    
    return files

def main():
    print("🗺️ OS Open Map Local GML File Analyzer (Fixed)")
    print("=" * 60)
    
    # Check if GML directory exists
    if not os.path.exists(GML_ROOT):
        print(f"❌ GML directory not found: {GML_ROOT}")
        return
    
    # List available files
    files = list_available_files()
    
    if not files:
        print("❌ No GML files found!")
        return
    
    print()
    
    # Analyze first file by default
    print("🔍 Analyzing first file by default...")
    analyze_gml_file(files[0])
    
    print("\n" + "=" * 60)
    print("💡 To analyze a specific file, modify the script or run:")
    print("   analyze_gml_file('path/to/your/file.gml')")

if __name__ == "__main__":
    main() 