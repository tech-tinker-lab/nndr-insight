# Comprehensive Data Analysis Report
## NNDR Insight Project - Data Structure Analysis

### Executive Summary

This document provides a comprehensive analysis of all data files in the `backend/data` folder, including their structures, relationships, and implications for the enhanced database schema and ingestion pipeline. The analysis reveals multiple data sources for the same council/type of data, requiring sophisticated data management and deduplication strategies.

---

## 1. Data Source Overview

### 1.1 Data Categories Identified

#### **A. NNDR Business Rate Data**
- **Primary Sources**: VOA (Valuation Office Agency) compiled lists
- **Secondary Sources**: Local council data (South Cambridgeshire 2015)
- **Tertiary Sources**: Sample data and revaluation tables

#### **B. Geospatial Reference Data**
- **OS Open UPRN**: Unique Property Reference Numbers with coordinates
- **CodePoint Open**: Postcode to coordinate mapping
- **ONSPD**: ONS Postcode Directory with administrative geographies
- **LAD Boundaries**: Local Authority District boundaries (multiple formats)

#### **C. Economic and Statistical Data**
- **NDR Revaluation Tables**: Statistical summaries by geography and property type
- **ONS Administrative Geographies**: Hierarchical geographic classifications

---

## 2. Detailed Data File Analysis

### 2.1 NNDR Business Rate Data

#### **A. VOA Compiled Lists (Primary Source)**

**File**: `uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv.csv`
- **Size**: 522MB
- **Format**: Pipe-delimited (|)
- **Structure**: Complex multi-field format
- **Sample Record**: `1*0435**087099*CW*WAREHOUSE AND PREMISES*4323101000*SUZUKI GB PLC, STEINBECK CRESCENT, SNELSHALL WEST, MILTON KEYNES**SUZUKI GB PLC*STEINBECK CRESCENT*MILTON KEYNES*SNELSHALL WEST**MK4 4AE***1100000**26641211000**151S****32409301281*01-APR-2023**`

**Field Analysis**:
- Field 1: Record ID
- Field 2: BA Code (0435 = Milton Keynes)
- Field 3: BA Reference (087099)
- Field 4: Property Category (CW = Warehouse)
- Field 5: Description
- Field 6: SCAT Code (4323101000)
- Field 7: Full Address
- Field 8: Property Name
- Field 9: Street
- Field 10: Town
- Field 11: Locality
- Field 12: Postcode
- Field 13: Rateable Value (1100000)
- Field 14: UPRN (26641211000)
- Field 15: Appeal Code (151S)
- Field 16: Effective Date (01-APR-2023)

**Performance Implications**:
- **Bottleneck**: Large file size (522MB) requires chunked processing
- **Complexity**: Pipe-delimited format with variable field lengths
- **Data Quality**: Mixed data quality with some missing fields

#### **B. Historic NNDR Data**

**File**: `uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-historic-csv.csv`
- **Size**: 29MB
- **Format**: Pipe-delimited
- **Purpose**: Historic changes and updates
- **Structure**: Similar to main file but with change tracking

#### **C. Local Council Data (Secondary Source)**

**File**: `NNDR Rating List  March 2015_0.csv`
- **Size**: 630KB
- **Format**: CSV with headers
- **Structure**: Standard CSV format
- **Fields**: ListAltered, CommunityCode, BAReference, PropertyCategoryCode, PropertyDescription, PropertyAddress, StreetDescriptor, Locality, PostTown, AdministrativeArea, PostCode, EffectiveDate, PartiallyDomesticSignal, RateableValue, SCATCode, AppealSettlementCode, UniquePropertyRef

**File**: `nndr-ratepayers March 2015_0.csv`
- **Size**: 624KB
- **Format**: CSV with headers
- **Structure**: Ratepayer information linked to properties
- **Fields**: Name, PropertyAddress, PostCode, PropertyDescription, PropertyRateableValuePlaceRef, LiabilityPeriodStartDate, AnnualCharge, ExemptionAmount, ExemptionCode, RateableValue, MandatoryAmount, MandatoryRelief, CharityReliefAmount, DiscReliefAmount, DiscretionaryCharitableRelief, AdditionalRlf, AdditionalRelief, SBRApplied, SBRSupplement, SBRAmount, ChargeType, ReportDate

**Key Insight**: **Multiple data sources for same council** - VOA data vs local council data may have different structures and quality levels.

#### **D. Sample Data**

**File**: `sample_nndr.csv`
- **Size**: 332B
- **Format**: CSV with headers
- **Purpose**: Development and testing
- **Fields**: PropertyID, Address, Postcode, RateableValue, Description, Latitude, Longitude, CurrentRatingStatus, LastBilledDate

### 2.2 NDR Revaluation Statistical Tables

**Directory**: `NDR_Revaluation_2023_Compiled_List_Tables/`

#### **Table_1_0.csv - Geographic Level Changes**
- **Purpose**: Percentage changes by geographic level and property type
- **Fields**: geographical_level_presented, ons_area_codes, ons_names, all_percent_change_rv, retail_percent_change_rv, industry_percent_change_rv, offices_percent_change_rv, other_percent_change_rv
- **Coverage**: England & Wales, Regions, Local Authorities

#### **Table_2_0.csv - Geographic Level Statistics**
- **Purpose**: Detailed statistics by geographic level
- **Fields**: geographical_level_presented, ba_code, ons_area_codes, ons_names, count, total_rv_1, mean_rv_1, median_rv_1, total_rv_2, mean_rv_2, median_rv_2, change_rv, percent_change_rv
- **Coverage**: Complete statistical breakdown

#### **Table_3_0.csv - Rateable Value Bands**
- **Purpose**: Distribution by rateable value bands
- **Fields**: rv_band, percent_count_1, total_rv_1, percent_rv_1, count, percent_count_2, total_rv_2, percent_rv_2, change_rv, percent_change_rv
- **Coverage**: Value band analysis

#### **Table_4_0.csv - Property Type Analysis**
- **Purpose**: Analysis by SCAT codes and property types
- **Fields**: type, scat_code, description, count, total_rv_1, mean_rv_1, median_rv_1, total_rv_2, mean_rv_2, median_rv_2, change_rv, percent_change_rv
- **Coverage**: Detailed property type breakdown

#### **Table_5_0.csv - Property Type Codes**
- **Purpose**: Analysis by property type codes
- **Fields**: type, prop_type_code, description, count, total_rv_1, mean_rv_1, median_rv_1, total_rv_2, mean_rv_2, median_rv_2, change_rv, percent_change_rv
- **Coverage**: Property type code analysis

#### **Table_6_0.csv - Revision Data**
- **Purpose**: Revision data for revaluation
- **Fields**: geographical_level_presented, ba_code, ons_area_codes, ons_names, all_percent_change_rv_revision, retail_percent_change_rv_revision, industry_percent_change_rv_revision, office_percent_change_rv_revision, other_percent_change_rv_revision
- **Coverage**: Revision tracking

### 2.3 Geospatial Reference Data

#### **A. OS Open UPRN**

**File**: `osopenuprn_202506_csv/osopenuprn_202506.csv`
- **Size**: 583MB (compressed)
- **Format**: CSV with headers
- **Fields**: UPRN, X_COORDINATE, Y_COORDINATE, LATITUDE, LONGITUDE
- **Coverage**: All UK properties with UPRNs
- **Coordinate System**: OSGB (X_COORDINATE, Y_COORDINATE) and WGS84 (LATITUDE, LONGITUDE)

#### **B. CodePoint Open**

**Directory**: `codepo_gb/Data/CSV/`
- **Format**: Individual CSV files by postcode area (ab.csv, ac.csv, etc.)
- **Structure**: Postcode, Positional Quality Indicator, Easting, Northing, Country Code, NHS Regional HA Code, NHS HA Code, Admin County Code, Admin District Code, Admin Ward Code
- **Coverage**: All UK postcodes
- **Performance**: 120+ individual files requiring parallel processing

#### **C. ONSPD (ONS Postcode Directory)**

**File**: `ONSPD_Online_Latest_Centroids.csv`
- **Size**: 1.2GB
- **Format**: CSV with comprehensive headers
- **Fields**: 60+ fields including X, Y, OBJECTID, PCD, PCD2, PCDS, DOINTR, DOTERM, OSCTY, CED, OSLAUA, OSWARD, PARISH, USERTYPE, OSEAST1M, OSNRTH1M, OSGRDIND, OSHLTHAU, NHSER, CTRY, RGN, STREG, PCON, EER, TECLEC, TTWA, PCT, ITL, STATSWARD, OA01, CASWARD, NPARK, LSOA01, MSOA01, UR01IND, OAC01, OA11, LSOA11, MSOA11, WZ11, SICBL, BUA24, RU11IND, OAC11, LAT, LONG, LEP1, LEP2, PFA, IMD, CALNCV, ICB, OA21, LSOA21, MSOA21, RUC21IND, GlobalID
- **Coverage**: Complete UK postcode coverage with administrative geographies

### 2.4 Local Authority Boundaries

#### **Multiple LAD Boundary Sources**

**Primary Source**: `LAD_MAY_2025_UK_BFC.shp` (116MB)
- **Format**: Shapefile with associated files (.dbf, .prj, .shx, .cpg, .xml)
- **Coverage**: UK Local Authority District boundaries

**Additional Sources in `/others/` directory**:
1. `LAD_MAY_2025_UK_BSC_-7755873515688619755.csv` (53KB)
2. `LAD_MAY_2025_UK_BFE_3090425641073732517.csv` (53KB)
3. `LAD_MAY_2025_UK_BFC_-4381170276035528708.csv` (53KB)
4. `LAD_MAY_2025_UK_BFC_5054533363948813637.txt` (189MB)
5. `LAD_MAY_2025_UK_BSC_3932072579627664896.geodatabase` (1.0MB)
6. `LAD_MAY_2025_UK_BFC_9040442334161396065.geodatabase` (41MB)

**Key Insight**: **Multiple boundary sources for same LADs** - Different formats (CSV, Shapefile, Geodatabase) with potentially different coordinate systems and precision levels.

---

## 3. Data Source Conflicts and Duplication Analysis

### 3.1 Same Council, Multiple Sources

#### **A. NNDR Data Conflicts**
- **VOA Source**: `uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv.csv`
- **Local Council Source**: `NNDR Rating List  March 2015_0.csv`
- **Sample Source**: `sample_nndr.csv`

**Potential Conflicts**:
1. **Different field structures** (pipe-delimited vs CSV)
2. **Different data quality levels**
3. **Different update frequencies**
4. **Different property coverage**
5. **Different coordinate systems**

#### **B. LAD Boundary Conflicts**
- **Primary**: Shapefile format (116MB)
- **Secondary**: CSV format (53KB each)
- **Tertiary**: Geodatabase format (1MB-41MB)

**Potential Conflicts**:
1. **Different coordinate systems**
2. **Different precision levels**
3. **Different update dates**
4. **Different boundary definitions**

### 3.2 Data Quality Variations

#### **A. Coordinate System Variations**
- **OS UPRN**: OSGB (X_COORDINATE, Y_COORDINATE) + WGS84 (LATITUDE, LONGITUDE)
- **CodePoint**: OSGB (Easting, Northing)
- **ONSPD**: OSGB (X, Y) + WGS84 (LAT, LONG)
- **Sample Data**: WGS84 only (Latitude, Longitude)

#### **B. Field Naming Variations**
- **VOA Data**: Pipe-delimited with no headers
- **Local Council**: CSV with descriptive headers
- **Sample Data**: CSV with simple headers

---

## 4. Performance Bottlenecks Identified

### 4.1 File Size Bottlenecks

#### **Critical Performance Issues**:
1. **ONSPD File**: 1.2GB - Requires chunked processing
2. **VOA NNDR File**: 522MB - Complex parsing required
3. **OS UPRN File**: 583MB compressed - Large coordinate dataset
4. **LAD Boundaries**: 116MB - Complex geometry processing

#### **Processing Challenges**:
1. **Memory Usage**: Large files exceed typical memory limits
2. **Processing Time**: Sequential processing would take hours
3. **Error Recovery**: Large files make error recovery expensive

### 4.2 Data Format Bottlenecks

#### **Complex Parsing Requirements**:
1. **Pipe-delimited VOA data**: No headers, variable field lengths
2. **Multiple coordinate systems**: Requires transformation
3. **Mixed data quality**: Requires validation and cleaning
4. **Multiple file formats**: CSV, Shapefile, Geodatabase, TXT

### 4.3 Database Performance Bottlenecks

#### **Indexing Challenges**:
1. **Spatial indexes**: Large geometry datasets
2. **Composite indexes**: Multiple field combinations
3. **Text search indexes**: Address and description fields

---

## 5. Enhanced Schema Requirements

### 5.1 Data Source Tracking

#### **Required Schema Enhancements**:
```sql
-- Add to master_gazetteer table
ALTER TABLE master_gazetteer ADD COLUMN data_source VARCHAR(100);
ALTER TABLE master_gazetteer ADD COLUMN source_priority INTEGER;
ALTER TABLE master_gazetteer ADD COLUMN source_confidence_score NUMERIC(3,2);
ALTER TABLE master_gazetteer ADD COLUMN last_source_update TIMESTAMP;
ALTER TABLE master_gazetteer ADD COLUMN source_file_reference VARCHAR(255);
```

#### **New Table for Source Management**:
```sql
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) UNIQUE,
    source_type VARCHAR(50), -- 'voa', 'local_council', 'os', 'ons'
    source_description TEXT,
    source_priority INTEGER, -- 1=highest priority
    source_quality_score NUMERIC(3,2),
    source_update_frequency VARCHAR(50),
    source_coordinate_system VARCHAR(50),
    source_file_pattern VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 Duplicate Management

#### **New Table for Duplicate Tracking**:
```sql
CREATE TABLE duplicate_management (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES master_gazetteer(id),
    duplicate_group_id INTEGER,
    duplicate_confidence_score NUMERIC(3,2),
    duplicate_reason TEXT,
    preferred_record BOOLEAN DEFAULT FALSE,
    merged_from_sources JSONB,
    merge_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.3 Data Quality Framework

#### **Enhanced Quality Rules**:
```sql
-- Add to data_quality.quality_rules
INSERT INTO data_quality.quality_rules (rule_name, rule_description, table_name, column_name, rule_type, rule_definition, severity) VALUES
('coordinate_validation', 'Validate coordinate ranges for UK', 'master_gazetteer', 'latitude', 'range', 'latitude BETWEEN 49.0 AND 61.0', 'error'),
('coordinate_validation', 'Validate coordinate ranges for UK', 'master_gazetteer', 'longitude', 'range', 'longitude BETWEEN -8.0 AND 2.0', 'error'),
('postcode_format', 'Validate UK postcode format', 'master_gazetteer', 'postcode', 'format', 'regex pattern for UK postcodes', 'warning'),
('rateable_value_range', 'Validate rateable value ranges', 'master_gazetteer', 'current_rateable_value', 'range', 'current_rateable_value > 0 AND current_rateable_value < 100000000', 'error');
```

---

## 6. Enhanced Ingestion Pipeline Requirements

### 6.1 Multi-Source Ingestion Strategy

#### **A. Source Priority Management**:
1. **VOA Data**: Priority 1 (official source)
2. **Local Council Data**: Priority 2 (supplementary)
3. **Sample Data**: Priority 3 (development only)

#### **B. Duplicate Detection Strategy**:
1. **Exact Match**: Same BA Reference + Postcode
2. **Fuzzy Match**: Similar address + coordinates
3. **UPRN Match**: Same UPRN across sources
4. **Manual Review**: Low confidence matches

#### **C. Data Transformation Pipeline**:
1. **Coordinate System Standardization**: Convert all to OSGB 27700
2. **Field Mapping**: Map different source fields to standard schema
3. **Data Cleaning**: Remove duplicates, fix formatting
4. **Quality Validation**: Apply quality rules
5. **Confidence Scoring**: Score data quality and source reliability

### 6.2 Performance Optimization

#### **A. Parallel Processing**:
```python
# Process multiple files simultaneously
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for file_path in data_files:
        future = executor.submit(process_file, file_path)
        futures.append(future)
```

#### **B. Chunked Processing**:
```python
# Process large files in chunks
chunk_size = 10000
for chunk in pd.read_csv(large_file, chunksize=chunk_size):
    process_chunk(chunk)
```

#### **C. Database Optimization**:
```sql
-- Disable indexes during bulk load
ALTER TABLE master_gazetteer SET UNLOGGED;
-- Bulk load data
-- Re-enable indexes
ALTER TABLE master_gazetteer SET LOGGED;
REINDEX TABLE master_gazetteer;
```

---

## 7. Visualization and Display Requirements

### 7.1 Source-Aware Display

#### **A. Source Filtering**:
- Allow users to filter by data source
- Show source confidence scores
- Display last update dates
- Highlight data quality issues

#### **B. Duplicate Visualization**:
- Show duplicate groups
- Display merge history
- Allow manual duplicate resolution
- Show confidence scores for matches

### 7.2 Custom Map Layers

#### **A. Source-Specific Layers**:
```sql
-- Create map layers for different sources
INSERT INTO mapping.map_layers (layer_name, layer_description, data_source_table, data_source_column, style_config) VALUES
('voa_properties', 'VOA NNDR Properties', 'master_gazetteer', 'data_source = ''voa''', '{"color": "#ff0000", "opacity": 0.8}'),
('local_council_properties', 'Local Council Properties', 'master_gazetteer', 'data_source = ''local_council''', '{"color": "#00ff00", "opacity": 0.8}'),
('duplicate_properties', 'Duplicate Properties', 'master_gazetteer', 'duplicate_group_id IS NOT NULL', '{"color": "#ffff00", "opacity": 0.9}');
```

#### **B. Quality-Based Styling**:
```sql
-- Style based on data quality
INSERT INTO mapping.map_layers (layer_name, layer_description, data_source_table, data_source_column, style_config) VALUES
('high_quality', 'High Quality Data', 'master_gazetteer', 'data_quality_score > 0.8', '{"color": "#00ff00", "opacity": 1.0}'),
('medium_quality', 'Medium Quality Data', 'master_gazetteer', 'data_quality_score BETWEEN 0.5 AND 0.8', '{"color": "#ffff00", "opacity": 0.8}'),
('low_quality', 'Low Quality Data', 'master_gazetteer', 'data_quality_score < 0.5', '{"color": "#ff0000", "opacity": 0.6}');
```

---

## 8. Implementation Recommendations

### 8.1 Immediate Actions

1. **Update Enhanced Schema**: Add data source tracking fields
2. **Create Source Management Tables**: Track all data sources
3. **Implement Duplicate Detection**: Handle multiple sources
4. **Enhance Quality Framework**: Add source-specific rules

### 8.2 Performance Optimizations

1. **Parallel Processing**: Process multiple files simultaneously
2. **Chunked Loading**: Handle large files efficiently
3. **Database Optimization**: Use bulk loading techniques
4. **Memory Management**: Process files in chunks

### 8.3 Data Quality Improvements

1. **Coordinate Standardization**: Convert all to OSGB 27700
2. **Field Mapping**: Standardize field names across sources
3. **Duplicate Resolution**: Implement intelligent matching
4. **Quality Scoring**: Score data based on source and content

### 8.4 Visualization Enhancements

1. **Source-Aware Display**: Show data source information
2. **Quality-Based Styling**: Color-code by data quality
3. **Duplicate Visualization**: Show duplicate groups
4. **Filtering Options**: Allow source-based filtering

---

## 9. Conclusion

The comprehensive data analysis reveals a complex ecosystem of multiple data sources for the same council and property types. The enhanced schema and ingestion pipeline must handle:

1. **Multiple data sources** with different formats and quality levels
2. **Duplicate detection and resolution** across sources
3. **Performance optimization** for large datasets
4. **Data quality tracking** and scoring
5. **Source-aware visualization** and filtering

The proposed enhancements will create a robust, scalable system capable of handling the complexity of real-world NNDR data while maintaining performance and data quality standards. 