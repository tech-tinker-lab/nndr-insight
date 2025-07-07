import os
import glob
import fiona
from shapely.geometry import shape
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
                
                # Collect statistics
                themes.add(props.get("theme", "Unknown"))
                descriptive_groups.add(props.get("descriptivegroup", "Unknown"))
                if geom:
                    geometry_types.add(geom["type"])
                
                print(f"Record {feature_count}:")
                print(f"  🆔 FID: {feature.get('id', 'N/A')}")
                print(f"  🏷️ Theme: {props.get('theme', 'N/A')}")
                print(f"  🏗️ Make: {props.get('make', 'N/A')}")
                print(f"  📍 Physical Presence: {props.get('physicalpresence', 'N/A')}")
                print(f"  📂 Descriptive Group: {props.get('descriptivegroup', 'N/A')}")
                print(f"  📝 Descriptive Term: {props.get('descriptiveterm', 'N/A')}")
                print(f"  🏛️ Feature Class: {props.get('fclass', 'N/A')}")
                
                if geom:
                    geom_shape = shape(geom)
                    print(f"  📐 Geometry Type: {geom['type']}")
                    print(f"  📍 Coordinates: {list(geom_shape.coords)[:3]}...")  # Show first 3 coordinate pairs
                    print(f"  📏 Area: {geom_shape.area:.2f} sq units")
                else:
                    print(f"  📐 Geometry: None")
                
                print()
            
            # Show summary statistics
            print("📊 File Summary:")
            print("-" * 60)
            print(f"📁 Total Features Analyzed: {feature_count}")
            print(f"🎨 Themes Found: {', '.join(sorted(themes))}")
            print(f"📂 Descriptive Groups: {', '.join(sorted(descriptive_groups))}")
            print(f"📐 Geometry Types: {', '.join(sorted(geometry_types))}")
            
            # Show all available properties from first feature
            if feature_count > 0:
                print(f"\n🔍 All Available Properties:")
                print("-" * 60)
                with fiona.open(filepath, driver="GML") as src2:
                    first_feature = next(iter(src2))
                    for key, value in first_feature["properties"].items():
                        print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error analyzing file: {e}")

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
    print("🗺️ OS Open Map Local GML File Analyzer")
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