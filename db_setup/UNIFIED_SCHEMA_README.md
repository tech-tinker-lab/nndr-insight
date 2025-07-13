# Unified Schema System

## Overview

The Unified Schema System provides a comprehensive, AI-powered database setup that eliminates duplication and provides operational data for immediate use. This system replaces manual schema creation with automated, intelligent database management.

## Key Features

### 🎯 **Single Schema File**
- `unified_schema.txt` - One file listing all SQL scripts in execution order
- No duplication in table structures, indexes, or constraints
- Proper dependency management and execution order

### 🤖 **AI-Powered Management**
- Uses your existing AI analysis service for intelligent schema validation
- Automatic pattern recognition and standards compliance checking
- Smart field mapping and data type inference

### 🌱 **Operational Seeding Data**
- **Data Standards**: ISO, UK Government, sector-specific standards
- **Sectors**: All government departments, private sector, industries
- **Dataset Structures**: ONS Postcode Directory, Code-Point Open, NNDR Properties
- **Governing Bodies**: 25+ UK government bodies and agencies
- **Sample Datasets**: Training data for AI pattern recognition

### 🔧 **JSONB Configuration**
- Flexible configuration storage without schema changes
- Zero-downtime deployments and A/B testing
- Dynamic UI adaptation and feature flags

## Schema Structure

```
db_setup/schemas/
├── unified_schema.txt              # Main execution file
├── 00_enable_postgis.sql          # Core extensions
├── design/                         # AI-powered design system
│   ├── 00_drop_enhanced_schemas.sql
│   ├── 01_create_design_schema.sql
│   ├── 02_create_dataset_pipeline_schema.sql
│   └── 03_create_enhanced_design_system.sql
├── reference/                      # Core reference tables
│   ├── create_migration_history.sql
│   ├── create_upload_history.sql
│   ├── users.sql
│   ├── users_seed.sql
│   └── staging_configs.sql
├── create_staging_schema.sql       # Unified staging system
└── seeding/                        # Operational data
    ├── 01_data_standards_seed.sql
    ├── 02_sectors_seed.sql
    ├── 03_dataset_structures_seed.sql
    ├── 04_governing_bodies_seed.sql
    └── 05_sample_datasets_seed.sql
```

## Quick Start

### 1. Run the Unified Schema Creation

```bash
cd db_setup
python create_unified_schema.py
```

### 2. What Gets Created

#### Design System Tables
- `design_enhanced.data_standards` - 18 data standards (ISO, UK Gov, sector-specific)
- `design_enhanced.sectors` - 20 sectors (government, private, industry)
- `design_enhanced.dataset_structures` - 3 major dataset structures
- `design_enhanced.governing_bodies` - 25+ governing bodies
- `design_enhanced.sample_datasets` - 8 sample datasets for AI training

#### Reference Tables
- `reference.migration_history` - Track all schema changes
- `reference.upload_history` - Monitor data uploads
- `reference.users` - User management
- `reference.staging_configs` - Unified staging configuration

#### Staging System
- `staging` schema - Unified staging for all data types
- No more manual staging table creation
- AI-powered field mapping and validation

## Benefits

### ✅ **No Duplication**
- Single source of truth for all table structures
- Unified validation rules and constraints
- Consistent naming conventions

### ✅ **AI-Powered Intelligence**
- Automatic dataset type detection
- Smart field mapping and validation
- Standards compliance checking
- Pattern recognition for new datasets

### ✅ **Operational Ready**
- Pre-seeded with all major UK data standards
- Complete sector coverage
- Sample datasets for training
- Governing body information

### ✅ **Flexible & Scalable**
- JSONB configuration for easy evolution
- No schema changes needed for new features
- Automated migration tracking
- Comprehensive audit trail

## Dataset Structures Included

### 1. ONS Postcode Directory
- **Governing Body**: Office for National Statistics
- **Standards**: BS7666, OS_Standards
- **Fields**: 40+ fields including coordinates, administrative codes
- **Sample File**: ONSPD_MAY_2023_UK.csv (2.8M records)

### 2. Code-Point Open
- **Governing Body**: Ordnance Survey
- **Standards**: OS_Standards, BS7666
- **Fields**: Postcode, coordinates, quality indicators
- **Sample File**: codepo_gb.zip (1.7M records)

### 3. NNDR Properties
- **Governing Body**: Valuation Office Agency
- **Standards**: NNDR_Standard, VOA_Standards
- **Fields**: Business rates, property details, coordinates
- **Sample File**: nndr_properties_2023.csv (2M records)

## Data Standards Coverage

### ISO Standards
- ISO_19115 - Geographic Information Metadata
- ISO_19139 - XML Schema Implementation
- ISO_19110 - Feature Cataloguing
- ISO_19111 - Spatial Referencing
- ISO_19112 - Geographic Identifiers

### UK Government Standards
- BS7666 - Spatial Datasets for Geographical Referencing
- GDS_Standards - Government Digital Service Standards
- INSPIRE_UK - UK INSPIRE Implementation
- OS_Standards - Ordnance Survey Standards
- VOA_Standards - Valuation Office Agency Standards

### Sector-Specific Standards
- NNDR_Standard - Business Rates
- Planning_Standard - Planning Applications
- Highways_Standard - Transport Data
- Environmental_Standard - Environmental Data
- Health_Standard - Public Health Data

### Quality Standards
- DQ_Completeness - Data Completeness
- DQ_Accuracy - Data Accuracy
- DQ_Consistency - Data Consistency
- DQ_Timeliness - Data Timeliness
- DQ_Accessibility - Data Accessibility

## Sector Coverage

### Government Sectors
- Central Government (ONS, DWP, DfT, etc.)
- Local Government (LGA, GLA, TfL)
- Devolved Administrations (Scotland, Wales, NI)
- Government Agencies (VOA, OS, EA, etc.)

### Private Sector
- Financial Services
- Property and Real Estate
- Transport and Logistics
- Utilities and Energy
- Retail and Commerce

### Industry Sectors
- Healthcare and Social Care
- Education and Training
- Environmental and Conservation
- Planning and Development
- Emergency Services

### Cross-Sector
- Infrastructure and Construction
- Technology and Digital
- Research and Academia
- Regulatory and Compliance

## AI Integration

The system integrates with your existing AI analysis service to provide:

### Pattern Recognition
- Automatic field type detection
- Data format validation
- Geographic coordinate recognition
- Reference code validation

### Standards Compliance
- BS7666 address format checking
- OS coordinate system validation
- Government data standards verification
- Quality assessment scoring

### Smart Mapping
- Automatic field-to-field mapping
- Data type conversion suggestions
- Validation rule generation
- Transformation recommendations

## Migration from Manual Schemas

The unified system replaces all manual schema files that have been archived:

### Archived Files
- All files in `db_setup/schemas/archive/manual_schemas/`
- Individual schema files for UPRN, NNDR, postcodes, etc.
- Manual staging table definitions
- Duplicate table structures

### Benefits of Migration
- **Reduced Maintenance**: Single schema file to manage
- **Consistency**: Unified validation and constraints
- **Intelligence**: AI-powered analysis and mapping
- **Flexibility**: JSONB configuration for easy changes
- **Scalability**: Automated table generation

## Usage Examples

### 1. Upload a New Dataset

```python
# The AI system automatically:
# - Detects dataset type (postcode, business rates, etc.)
# - Maps fields to appropriate structures
# - Validates against relevant standards
# - Generates staging table if needed
# - Provides confidence scores and recommendations
```

### 2. Add New Data Standard

```sql
-- Simply insert into JSONB configuration
INSERT INTO design_enhanced.data_standards (
    standard_code, standard_name, standard_type, 
    governing_body, compliance_rules
) VALUES (
    'NEW_STANDARD', 'New Data Standard', 'Sector_Specific',
    'New Body', '{"validation_rules": ["rule1", "rule2"]}'
);
```

### 3. Create New Dataset Structure

```sql
-- AI system uses existing patterns to suggest structure
INSERT INTO design_enhanced.dataset_structures (
    dataset_name, dataset_type, governing_body,
    field_definitions, validation_rules
) VALUES (
    'New Dataset', 'new_type', 'Governing Body',
    '[{"field_name": "field1", "data_type": "VARCHAR(50)"}]',
    '[{"rule_name": "validation1", "rule_type": "regex"}]'
);
```

## Monitoring and Maintenance

### Migration History
All schema changes are tracked in `design_enhanced.migration_history`:
- Schema creation events
- Seeding operations
- Validation results
- AI analysis reports

### Validation Reports
The system provides comprehensive validation:
- Table existence checks
- Seeding data counts
- Standards compliance scores
- AI confidence assessments

### AI Recommendations
Continuous AI analysis provides:
- Performance optimization suggestions
- Standards compliance improvements
- Data quality enhancements
- Schema evolution recommendations

## Conclusion

The Unified Schema System provides a complete, AI-powered database foundation that:

1. **Eliminates duplication** through unified schema management
2. **Provides operational data** for immediate use
3. **Uses AI intelligence** for automatic analysis and mapping
4. **Ensures flexibility** through JSONB configuration
5. **Maintains scalability** through automated processes

This system transforms your database from a collection of manual schemas into an intelligent, self-managing data platform that grows with your needs.

---

**Ready to get started?** Run `python create_unified_schema.py` to create your AI-powered database! 