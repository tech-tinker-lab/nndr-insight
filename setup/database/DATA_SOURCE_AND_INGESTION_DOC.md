# NNDR Insight Data Sources & Ingestion Documentation

## 1. Data Sources Overview

### A. NNDR Business Rate Data
- **VOA 2023 List**: Official, pipe-delimited, no headers, complex structure.
- **Historic VOA**: Change tracking, similar structure.
- **Local Council 2015**: CSV, descriptive headers, different field names.
- **Sample Data**: Simple CSV for dev/testing.
- **Revaluation Tables**: Multiple CSVs, statistical breakdowns.

### B. Geospatial Reference Data
- **OS Open UPRN**: UPRN to coordinates, OSGB and WGS84.
- **CodePoint Open**: Postcode to coordinates, OSGB.
- **ONSPD**: Postcodes with admin geography, both coordinate systems.
- **LAD Boundaries**: Shapefile, CSV, geodatabase formats.

---

## 2. Field Mapping Examples

| Standard Field         | VOA 2023           | Local Council 2015      | OS UPRN         | CodePoint         |
|-----------------------|--------------------|-------------------------|-----------------|------------------|
| ba_reference          | Field 3            | BAReference             |                 |                  |
| property_category     | Field 4            | PropertyCategoryCode    |                 |                  |
| description           | Field 5            | PropertyDescription     |                 |                  |
| full_address          | Field 7            | PropertyAddress         |                 |                  |
| street                | Field 8            | StreetDescriptor        |                 |                  |
| town                  | Field 10           | PostTown                |                 |                  |
| postcode              | Field 12           | PostCode                |                 | postcode         |
| rateable_value        | Field 13           | RateableValue           |                 |                  |
| scat_code             | Field 6            | SCATCode                |                 |                  |
| uprn                  | Field 14           | UniquePropertyRef       | UPRN            |                  |
| latitude              |                    |                         | LATITUDE        |                  |
| longitude             |                    |                         | LONGITUDE       |                  |

---

## 3. Ingestion Logic

- **Chunked/Parallel Processing**: Large files are read in chunks and/or processed in parallel.
- **Field Mapping**: Each source is mapped to the standard schema (see above).
- **Source Tagging**: Every record is tagged with its source, priority, and confidence.
- **Duplicate Detection**: Duplicates are detected by BA Reference + Postcode, UPRN, or fuzzy address match. Preferred record is chosen by source priority.
- **Coordinate Normalization**: All coordinates are converted to a standard system (OSGB 27700 or WGS84 as needed).
- **Data Quality Checks**: Rules for coordinate range, postcode format, rateable value, etc.
- **Bulk Insert Optimization**: Indexes are disabled during load and rebuilt after.

---

## 4. Adding a New Data Source

1. **Update `data_sources` Table**: Add a new row with source name, type, description, priority, etc.
2. **Update Ingestion Pipeline**: Add a new processing function for the new format, and map its fields to the standard schema.
3. **Update Field Mapping**: Add new mappings to the documentation and code.
4. **Test Ingestion**: Run the pipeline and check logs for errors or data quality issues.
5. **Update Visualization/Filtering**: Add new source to filters and map layers if needed.

---

## 5. Example: Adding a New Council CSV

- Add to `data_sources`:
  - `source_name`: 'council_2024'
  - `source_type`: 'nndr'
  - `source_description`: 'Council 2024 NNDR Data'
  - `source_priority`: 2
  - `source_quality_score`: 0.85
  - `source_file_pattern`: 'council_2024.csv'
- Add a new function in the ingestion script to parse and map the new CSV.
- Update the field mapping table above.
- Test and validate.

---

## 6. Troubleshooting & Logs

- All ingestion and schema update scripts log to `.log` files in the same directory.
- Check logs for errors, warnings, and performance bottlenecks.
- Use example queries in `example_queries.sql` to validate data.

---

## 7. Contact & Maintenance

- For schema or ingestion changes, update this documentation and the relevant scripts.
- For new data sources, follow the steps above and document the changes here. 