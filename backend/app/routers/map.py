# Geospatial logic router
from fastapi import APIRouter, Query
from pathlib import Path
import csv
import pandas as pd
import geopandas as gpd

router = APIRouter()

@router.get("/map")
def get_map(
    dataset: str = "NNDR Rating List  March 2015_0.csv",  # Default to your real file
    lat_col: str = "Latitude",
    lon_col: str = "Longitude",
    id_col: str = "PropertyID",
    address_col: str = "Address",
    postcode_col: str = "PostCode",
    delimiter: str = ",",
    header: str = None,
    district: str = "South Cambridgeshire"
):
    data_file = Path(__file__).parent.parent.parent / "data" / dataset
    shp_path = Path(__file__).parent.parent.parent / "data" / "LAD_MAY_2025_UK_BFC.shp"
    properties = []
    try:
        df = pd.read_csv(data_file, delimiter=delimiter, header=0 if header != "none" else None, encoding='utf-8')
        if header == "none":
            df.columns = [f"col{i+1}" for i in range(len(df.columns))]
        # Load district boundary
        gdf = gpd.read_file(shp_path)
        district_poly = gdf[gdf["LAD23NM"].str.contains(district, case=False, na=False)]
        if district_poly.empty:
            return {"error": f"District '{district}' not found in shapefile."}
        # Spatial filter
        df = df.dropna(subset=[lat_col, lon_col])
        points_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), crs=gdf.crs)
        within = gpd.sjoin(points_gdf, district_poly, how="inner", predicate="within")
        for _, row in within.iterrows():
            properties.append({
                "PropertyID": row.get(id_col, ""),
                "Address": row.get(address_col, ""),
                "Postcode": row.get(postcode_col, ""),
                "Latitude": row[lat_col],
                "Longitude": row[lon_col],
                "CurrentRatingStatus": row.get("CurrentRatingStatus", "")
            })
    except Exception as e:
        return {"error": str(e)}
    return {"properties": properties}

# NEW: Postcode centroid lookup endpoint
@router.get("/postcode-centroid")
def postcode_centroid(postcode: str = Query(..., description="Postcode to look up")):
    data_file = Path(__file__).parent.parent.parent / "data" / "ONSPD_Online_Latest_Centroids.csv"
    df = pd.read_csv(data_file, dtype=str)
    # Normalize postcode (remove spaces, uppercase)
    norm_postcode = postcode.replace(" ", "").upper()
    df["pcds_norm"] = df["pcds"].str.replace(" ", "").str.upper()
    row = df[df["pcds_norm"] == norm_postcode]
    if row.empty:
        return {"error": "Postcode not found"}
    lat = float(row.iloc[0]["lat"])
    lon = float(row.iloc[0]["long"])
    return {"postcode": postcode, "latitude": lat, "longitude": lon}

# NEW: Local Authority Districts GeoJSON endpoint
@router.get("/districts-geojson")
def districts_geojson():
    shp_path = Path(__file__).parent.parent.parent / "data" / "LAD_MAY_2025_UK_BFC.shp"
    gdf = gpd.read_file(shp_path)
    return gdf.to_json()

@router.get("/non-rated-properties-map")
def non_rated_properties_map(
    gazetteer_file: str = "all_commercial_properties.csv",
    nndr_file: str = "NNDR Rating List  March 2015_0.csv",
    lat_col: str = "Latitude",
    lon_col: str = "Longitude",
    postcode_col: str = "PostCode",
    id_col: str = "PropertyID",
    delimiter: str = ",",
    header: str = None,
    district: str = "South Cambridgeshire"
):
    data_dir = Path(__file__).parent.parent.parent / "data"
    shp_path = data_dir / "LAD_MAY_2025_UK_BFC.shp"
    try:
        gaz_df = pd.read_csv(data_dir / gazetteer_file, delimiter=delimiter, header=0 if header != "none" else None, encoding='utf-8')
        nndr_df = pd.read_csv(data_dir / nndr_file, delimiter=delimiter, header=0 if header != "none" else None, encoding='utf-8')
        # Load district boundary
        gdf = gpd.read_file(shp_path)
        district_poly = gdf[gdf["LAD23NM"].str.contains(district, case=False, na=False)]
        if district_poly.empty:
            return {"error": f"District '{district}' not found in shapefile."}
        # Filter gazetteer to district
        gaz_df = gaz_df.dropna(subset=[lat_col, lon_col])
        gaz_points = gpd.GeoDataFrame(gaz_df, geometry=gpd.points_from_xy(gaz_df[lon_col], gaz_df[lat_col]), crs=gdf.crs)
        gaz_within = gpd.sjoin(gaz_points, district_poly, how="inner", predicate="within")
        # Build set of rated postcodes/ids
        nndr_postcodes = set(nndr_df[postcode_col].dropna().str.replace(" ", "").str.upper())
        # Find non-rated
        missing = gaz_within[~gaz_within[postcode_col].str.replace(" ", "").str.upper().isin(nndr_postcodes)]
        properties = []
        for _, row in missing.iterrows():
            properties.append({
                "PropertyID": row.get(id_col, ""),
                "Address": row.get("Address", ""),
                "Postcode": row.get(postcode_col, ""),
                "Latitude": row[lat_col],
                "Longitude": row[lon_col],
            })
    except Exception as e:
        return {"error": str(e)}
    return {"non_rated_properties": properties, "total": len(properties)}
