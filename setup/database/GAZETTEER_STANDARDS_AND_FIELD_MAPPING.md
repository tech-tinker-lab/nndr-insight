# Gazetteer Standards and Field Mapping Documentation

## Overview

This document outlines the proper field mapping and gazetteer standards for the NNDR Insight project, ensuring compliance with UK property data standards and industrial best practices.

## 1. Gazetteer Standards

### Primary Property Identifiers

According to UK gazetteer standards:

1. **UPRN (Unique Property Reference Number)** - The primary, authoritative property identifier
   - Official standard: BS 7666
   - Managed by: Ordnance Survey
   - Format: 12-digit numeric identifier
   - Purpose: Unique identification of every addressable location

2. **BA Reference (Billing Authority Reference)** - Local authority billing identifier
   - Managed by: Individual local authorities
   - Format: Varies by authority
   - Purpose: Local billing and administration

3. **Property ID** - Internal system identifier
   - Should be derived from UPRN when available
   - Format: String representation of UPRN
   - Purpose: Internal system reference

### Field Hierarchy (Priority Order)

1. **UPRN** (Highest priority) - Official UK standard
2. **Property ID** (Derived from UPRN)
3. **BA Reference** (Local authority specific)
4. **Address-based matching** (Fallback)

## 2. Data Source Analysis

### VOA (Valuation Office Agency) Data

**File Structure**: Pipe-delimited (*) format, 29 fields
**Coordinate System**: Not provided (requires geocoding)
**Quality Score**: 0.95 (Official source)

**Field Mapping**:
```
Field 0:  row_id                    -> Internal row identifier
Field 1:  billing_auth_code         -> Billing authority code
Field 2:  empty1                    -> Unused field
Field 3:  ba_reference              -> Billing Authority Reference
Field 4:  scat_code                 -> Property category code
Field 5:  description               -> Property description
Field 6:  herid                     -> Hereditament ID
Field 7:  address_full              -> Full address
Field 8:  empty2                    -> Unused field
Field 9:  address1                  -> Street descriptor
Field 10: address2                  -> Post town
Field 11: address3                  -> Locality
Field 12: address4                  -> Address line 4
Field 13: address5                  -> Address line 5
Field 14: postcode                  -> Postcode
Field 15: effective_date            -> Effective date
Field 16: empty3                    -> Unused field
Field 17: rateable_value            -> Rateable value
Field 18: empty4                    -> Unused field
Field 19: uprn                      -> Unique Property Reference Number
Field 20: compiled_list_date        -> Compiled list date
Field 21: list_code                 -> List code
Field 22: empty5                    -> Unused field
Field 23: empty6                    -> Unused field
Field 24: empty7                    -> Unused field
Field 25: property_link_number      -> Property link number
Field 26: entry_date                -> Entry date
Field 27: empty8                    -> Unused field
Field 28: empty9                    -> Unused field
```

**Corrected Mapping**:
- `uprn`: Field 19 (Primary identifier)
- `ba_reference`: Field 3 (Billing reference)
- `property_id`: Derived from UPRN (Field 19)
- `property_address`: Field 7 (Full address)
- `street_descriptor`: Field 9 (Street name)
- `post_town`: Field 10 (Town)
- `locality`: Field 11 (Locality)
- `postcode`: Field 14 (Postcode)
- `property_category_code`: Field 4 (SCAT code)
- `property_description`: Field 5 (Description)
- `rateable_value`: Field 17 (Rateable value)
- `effective_date`: Field 15 (Effective date)

### Local Council Data (2015)

**File Structure**: CSV format with headers
**Coordinate System**: Not provided
**Quality Score**: 0.85 (Local authority source)

**Field Mapping**:
```
BAReference              -> ba_reference
PropertyCategoryCode     -> property_category_code
PropertyDescription      -> property_description
PropertyAddress          -> property_address
StreetDescriptor         -> street_descriptor
Locality                 -> locality
PostTown                 -> post_town
AdministrativeArea       -> administrative_area
PostCode                 -> postcode
RateableValue            -> rateable_value
SCATCode                 -> scat_code
UniquePropertyRef        -> uprn (Primary identifier)
EffectiveDate            -> effective_date
```

**Corrected Mapping**:
- `uprn`: UniquePropertyRef (Primary identifier)
- `ba_reference`: BAReference (Billing reference)
- `property_id`: Derived from UPRN (UniquePropertyRef)
- All other fields mapped directly

### OS Open UPRN Data

**File Structure**: CSV format
**Coordinate System**: OSGB (EPSG:27700) and WGS84
**Quality Score**: 0.98 (Official OS source)

**Field Mapping**:
```
UPRN         -> uprn (Primary identifier)
X_COORDINATE -> x_coordinate (OSGB Easting)
Y_COORDINATE -> y_coordinate (OSGB Northing)
LATITUDE     -> latitude (WGS84)
LONGITUDE    -> longitude (WGS84)
```

**Corrected Mapping**:
- `uprn`: UPRN (Primary identifier)
- `property_id`: Derived from UPRN
- `ba_reference`: None (Not provided by OS)
- Coordinates: Direct mapping

### CodePoint Open Data

**File Structure**: CSV format, multiple files by postcode area
**Coordinate System**: OSGB (EPSG:27700)
**Quality Score**: 0.90 (Official OS source)

**Field Mapping**:
```
postcode              -> postcode
positional_quality    -> quality indicator
easting               -> x_coordinate (OSGB)
northing              -> y_coordinate (OSGB)
country_code          -> country
nhs_regional_ha       -> nhs_region
nhs_ha                -> nhs_area
admin_county          -> county_code
admin_district        -> district_code
admin_ward            -> ward_code
```

**Corrected Mapping**:
- `uprn`: None (Not provided)
- `ba_reference`: None (Not provided)
- `property_id`: None (No property identifier)
- `postcode`: Direct mapping
- Coordinates: Direct mapping

### ONSPD (ONS Postcode Directory)

**File Structure**: CSV format
**Coordinate System**: OSGB (EPSG:27700) and WGS84
**Quality Score**: 0.95 (Official ONS source)

**Field Mapping**:
```
PCD  -> postcode
x    -> x_coordinate (OSGB)
y    -> y_coordinate (OSGB)
lat  -> latitude (WGS84)
long -> longitude (WGS84)
```

**Corrected Mapping**:
- `uprn`: None (Not provided)
- `ba_reference`: None (Not provided)
- `property_id`: None (No property identifier)
- `postcode`: PCD
- Coordinates: Direct mapping

## 3. Industrial Standards

### UK Property Data Standards

1. **BS 7666** - Address and location referencing
   - Defines UPRN as primary identifier
   - Standardizes address components
   - Defines coordinate systems

2. **INSPIRE Directive** - European spatial data standards
   - Addresses (Annex I)
   - Cadastral parcels (Annex I)
   - Administrative units (Annex I)

3. **OS Data Standards**
   - OSGB coordinate system (EPSG:27700)
   - WGS84 coordinate system (EPSG:4326)
   - AddressBase Premium structure

### Data Quality Standards

1. **Coordinate Validation**
   - UK bounds: 49.0°N to 61.0°N, -8.0°W to 2.0°E
   - OSGB bounds: 0 to 700000 (Easting), 0 to 1300000 (Northing)

2. **Postcode Validation**
   - Format: ^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$
   - Examples: M1 1AA, B33 8TH, CR2 6XH

3. **UPRN Validation**
   - 12-digit numeric
   - Range: 100000000000 to 999999999999

4. **Rateable Value Validation**
   - Positive numeric values
   - Reasonable range: £0 to £100,000,000

## 4. Implementation Guidelines

### Field Mapping Priority

1. **Primary Identification**
   - Use UPRN as primary identifier when available
   - Generate property_id from UPRN
   - Use BA Reference as secondary identifier

2. **Address Components**
   - Follow BS 7666 address structure
   - Maintain address line hierarchy
   - Preserve original formatting

3. **Coordinate Systems**
   - Store both OSGB and WGS84 coordinates
   - Validate coordinate ranges
   - Use PostGIS geometry for spatial operations

4. **Data Quality**
   - Implement validation rules
   - Track data quality scores
   - Maintain audit trails

### Database Schema Alignment

The `master_gazetteer` table should maintain:

```sql
-- Primary identification (in priority order)
uprn BIGINT UNIQUE,                    -- Primary identifier (BS 7666)
property_id VARCHAR(64),               -- Derived from UPRN
ba_reference VARCHAR(32),              -- Billing authority reference

-- Address components (BS 7666 compliant)
address_line_1 TEXT,                   -- Building name/number
address_line_2 TEXT,                   -- Street
address_line_3 TEXT,                   -- Locality
address_line_4 TEXT,                   -- Town
address_line_5 TEXT,                   -- County
postcode VARCHAR(16),                  -- Postcode

-- Coordinates (dual system)
x_coordinate DOUBLE PRECISION,         -- OSGB Easting
y_coordinate DOUBLE PRECISION,         -- OSGB Northing
latitude DOUBLE PRECISION,             -- WGS84
longitude DOUBLE PRECISION,            -- WGS84
geom GEOMETRY(Point, 27700),           -- PostGIS geometry
```

## 5. Migration Strategy

### Phase 1: Schema Validation
- Verify current schema against standards
- Identify field mapping discrepancies
- Plan migration approach

### Phase 2: Data Quality Assessment
- Analyze existing data quality
- Identify missing or incorrect mappings
- Establish quality benchmarks

### Phase 3: Implementation
- Update field mappings
- Implement validation rules
- Test with sample data

### Phase 4: Full Migration
- Migrate all data sources
- Validate results
- Update documentation

## 6. Quality Assurance

### Validation Rules
1. UPRN format and range validation
2. Coordinate bounds validation
3. Postcode format validation
4. Rateable value range validation
5. Address component completeness

### Monitoring
1. Data quality scores by source
2. Validation error rates
3. Source priority conflicts
4. Duplicate detection accuracy

### Maintenance
1. Regular data quality reviews
2. Source priority updates
3. Field mapping refinements
4. Standards compliance monitoring

## Conclusion

This document provides the foundation for proper gazetteer implementation according to UK standards. The key principle is that **UPRN is the primary property identifier**, and all other identifiers should be secondary or derived from it. This ensures compliance with BS 7666 and enables proper data integration across multiple sources. 