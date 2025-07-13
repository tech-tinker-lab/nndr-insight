# Archived Manual Schema Files

## Overview

This directory contains manually created database schema files that have been archived since the implementation of the **Dataset Structures** and **Design System** features.

## Why These Files Were Archived

These schema files were created manually before the implementation of the proper Dataset Structures system. With the new system in place, these manual schemas are no longer needed because:

1. **Dataset Structures System**: Now provides automated schema generation based on dataset types
2. **Design System**: Offers standardized table templates and field definitions
3. **JSONB Configuration**: Allows flexible configuration without schema changes
4. **Automated Workflows**: Replaces manual table creation with systematic approaches

## Archived Files

### Reference Data Schemas
- `os_open_uprn.sql` - OS Open UPRN master table
- `os_open_uprn_staging.sql` - OS Open UPRN staging table
- `lad_boundaries.sql` - Local Authority District boundaries
- `lad_boundaries_staging.sql` - LAD boundaries staging table
- `gazetteer_staging.sql` - Gazetteer staging table

### NNDR (National Non-Domestic Rates) Schemas
- `nndr_rating_list.sql` - NNDR rating list master table
- `nndr_rating_list_staging.sql` - NNDR rating list staging table
- `nndr_ratepayers.sql` - NNDR ratepayers master table
- `nndr_ratepayers_staging.sql` - NNDR ratepayers staging table
- `nndr_properties_staging.sql` - NNDR properties staging table
- `nndr_summary_valuation_staging.sql` - NNDR summary valuation staging table

### Address and Street Schemas
- `os_open_names.sql` - OS Open Names master table
- `os_open_names_staging.sql` - OS Open Names staging table
- `os_open_usrn.sql` - OS Open USRN master table
- `os_open_usrn_staging.sql` - OS Open USRN staging table
- `os_open_map_local.sql` - OS Open Map Local master table
- `os_open_map_local_staging.sql` - OS Open Map Local staging table

### Postcode Schemas
- `code_point_open.sql` - Code-Point Open master table
- `onspd.sql` - ONS Postcode Directory master table
- `onspd_staging.sql` - ONS Postcode Directory staging table

### Valuation Schemas
- `historic_valuations_staging.sql` - Historic valuations staging table
- `valuations_staging.sql` - Valuations staging table

### Drop and Create Scripts
- `01_drop_os_open_uprn_staging.sql` - Drop UPRN staging table script
- `02_create_os_open_uprn_staging.sql` - Create UPRN staging table script
- `01_drop_os_open_usrn_staging.sql` - Drop USRN staging table script
- `02_create_os_open_usrn_staging.sql` - Create USRN staging table script
- `01_drop_os_open_map_local_staging.sql` - Drop Map Local staging table script
- `02_create_os_open_map_local_staging.sql` - Create Map Local staging table script
- `drop_lad_boundaries_staging.sql` - Drop LAD boundaries staging table script

## Migration to New System

### Before (Manual Approach)
```sql
-- Manual table creation
CREATE TABLE IF NOT EXISTS public.nndr_properties_staging (
    list_altered TEXT,
    community_code TEXT,
    ba_reference TEXT,
    -- ... many manual fields
    source_name TEXT,
    upload_user TEXT,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### After (Dataset Structures System)
```javascript
// Automated schema generation
const structureData = {
  dataset_name: "NNDR Properties",
  dataset_type: "property",
  source_type: "file",
  target_schema_type: "staging",
  governing_body: "Valuation Office Agency",
  data_standards: ["VOA_NNDR", "BS7666"]
};

// System automatically generates:
// - Appropriate field definitions
// - Validation rules
// - Table templates
// - Migration scripts
```

## Benefits of the New System

1. **Standardization**: Consistent table structures across all datasets
2. **Automation**: No more manual schema creation
3. **Flexibility**: JSONB configuration allows easy modifications
4. **Compliance**: Built-in data standards validation
5. **Maintainability**: Centralized schema management
6. **Scalability**: Easy to add new dataset types

## Current Active Schemas

The following schemas remain active and are managed by the new system:

- `db_setup/schemas/design/` - Design System schemas
- `db_setup/schemas/reference/staging_configs.sql` - Staging configuration system
- `db_setup/schemas/reference/create_migration_history.sql` - Migration tracking
- `db_setup/schemas/reference/create_upload_history.sql` - Upload tracking
- `db_setup/schemas/reference/users.sql` - User management

## Archive Date

**Archived**: December 2024  
**Reason**: Implementation of Dataset Structures and Design System  
**Status**: Replaced by automated schema generation system

---

**Note**: These files are kept for reference and potential rollback purposes. The new Dataset Structures system provides all the functionality these manual schemas offered, but with better automation, standardization, and flexibility. 