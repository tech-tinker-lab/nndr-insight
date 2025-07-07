import csv
import glob
import os
import sqlalchemy
from sqlalchemy import text

# DB connection info
USER = "nndr"
PASSWORD = "nndrpass"
HOST = "localhost"
PORT = "5432"
DBNAME = "nndr_db"

BATCH_SIZE = 1000  # number of rows per batch insert

def point_wkt(x, y):
    if x and y:
        return f"POINT({x} {y})"
    return None

def load_data(engine, folder_path):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    print(f"Found {len(csv_files)} CSV files in {folder_path}")

    total_rows_inserted = 0

    with engine.begin() as conn:
        for file_path in csv_files:
            print(f"Loading {file_path}...")
            rows_batch = []
            rows_in_file = 0

            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter='\t')  # assuming TSV files

                for row in reader:
                    geom_wkt = point_wkt(row.get('GEOMETRY_X'), row.get('GEOMETRY_Y'))

                    rows_batch.append({
                        "os_id": row.get("ID"),
                        "names_uri": row.get("NAMES_URI"),
                        "name1": row.get("NAME1"),
                        "name1_lang": row.get("NAME1_LANG"),
                        "name2": row.get("NAME2"),
                        "name2_lang": row.get("NAME2_LANG"),
                        "type": row.get("TYPE"),
                        "local_type": row.get("LOCAL_TYPE"),
                        "geometry_x": float(row["GEOMETRY_X"]) if row.get("GEOMETRY_X") else None,
                        "geometry_y": float(row["GEOMETRY_Y"]) if row.get("GEOMETRY_Y") else None,
                        "most_detail_view_res": int(row["MOST_DETAIL_VIEW_RES"]) if row.get("MOST_DETAIL_VIEW_RES") else None,
                        "least_detail_view_res": int(row["LEAST_DETAIL_VIEW_RES"]) if row.get("LEAST_DETAIL_VIEW_RES") else None,
                        "mbr_xmin": float(row["MBR_XMIN"]) if row.get("MBR_XMIN") else None,
                        "mbr_ymin": float(row["MBR_YMIN"]) if row.get("MBR_YMIN") else None,
                        "mbr_xmax": float(row["MBR_XMAX"]) if row.get("MBR_XMAX") else None,
                        "mbr_ymax": float(row["MBR_YMAX"]) if row.get("MBR_YMAX") else None,
                        "postcode_district": row.get("POSTCODE_DISTRICT"),
                        "postcode_district_uri": row.get("POSTCODE_DISTRICT_URI"),
                        "populated_place": row.get("POPULATED_PLACE"),
                        "populated_place_uri": row.get("POPULATED_PLACE_URI"),
                        "populated_place_type": row.get("POPULATED_PLACE_TYPE"),
                        "district_borough": row.get("DISTRICT_BOROUGH"),
                        "district_borough_uri": row.get("DISTRICT_BOROUGH_URI"),
                        "district_borough_type": row.get("DISTRICT_BOROUGH_TYPE"),
                        "county_unitary": row.get("COUNTY_UNITARY"),
                        "county_unitary_uri": row.get("COUNTY_UNITARY_URI"),
                        "county_unitary_type": row.get("COUNTY_UNITARY_TYPE"),
                        "region": row.get("REGION"),
                        "region_uri": row.get("REGION_URI"),
                        "country": row.get("COUNTRY"),
                        "country_uri": row.get("COUNTRY_URI"),
                        "related_spatial_object": row.get("RELATED_SPATIAL_OBJECT"),
                        "same_as_dbpedia": row.get("SAME_AS_DBPEDIA"),
                        "same_as_geonames": row.get("SAME_AS_GEONAMES"),
                        "geom": geom_wkt,
                    })

                    rows_in_file += 1

                    if len(rows_batch) >= BATCH_SIZE:
                        _bulk_insert(conn, rows_batch)
                        total_rows_inserted += len(rows_batch)
                        print(f"  Inserted {total_rows_inserted} rows so far...")
                        rows_batch.clear()

                # Insert remaining rows from last batch
                if rows_batch:
                    _bulk_insert(conn, rows_batch)
                    total_rows_inserted += len(rows_batch)
                    print(f"  Inserted {total_rows_inserted} rows so far...")
                    rows_batch.clear()

            print(f"Finished loading {file_path} with {rows_in_file} rows.")

    print(f"✅ Total rows inserted across all files: {total_rows_inserted}")

def _bulk_insert(conn, rows):
    insert_stmt = text("""
        INSERT INTO os_open_names (
            os_id, names_uri, name1, name1_lang, name2, name2_lang, type, local_type,
            geometry_x, geometry_y, most_detail_view_res, least_detail_view_res,
            mbr_xmin, mbr_ymin, mbr_xmax, mbr_ymax, postcode_district, postcode_district_uri,
            populated_place, populated_place_uri, populated_place_type,
            district_borough, district_borough_uri, district_borough_type,
            county_unitary, county_unitary_uri, county_unitary_type,
            region, region_uri, country, country_uri,
            related_spatial_object, same_as_dbpedia, same_as_geonames, geom
        ) VALUES (
            :os_id, :names_uri, :name1, :name1_lang, :name2, :name2_lang, :type, :local_type,
            :geometry_x, :geometry_y, :most_detail_view_res, :least_detail_view_res,
            :mbr_xmin, :mbr_ymin, :mbr_xmax, :mbr_ymax, :postcode_district, :postcode_district_uri,
            :populated_place, :populated_place_uri, :populated_place_type,
            :district_borough, :district_borough_uri, :district_borough_type,
            :county_unitary, :county_unitary_uri, :county_unitary_type,
            :region, :region_uri, :country, :country_uri,
            :related_spatial_object, :same_as_dbpedia, :same_as_geonames,
            ST_GeomFromText(:geom, 27700)
        )
    """)
    conn.execute(insert_stmt, rows)

def main():
    engine = sqlalchemy.create_engine(
        f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    )
    load_data(engine, "data/opname_csv_gb/Data")

if __name__ == "__main__":
    main()
