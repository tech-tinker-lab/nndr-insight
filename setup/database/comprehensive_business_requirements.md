# Comprehensive NNDR Business Requirements & Database Design

## Executive Summary

This document outlines the comprehensive business requirements for the NNDR (National Non-Domestic Rates) Insight system and how the enhanced database schema addresses each requirement with a focus on **performance**, **accuracy**, and **comprehensive data coverage**.

## 1. Core Business Requirements

### 1.1 Comprehensive Data Staging & Processing
**Requirement**: All data must go through a staging process before final ingestion to ensure data quality and consistency.

**Solution**: 
- **Staging Schema**: Complete staging area with tables for raw data ingestion
- **Data Quality Framework**: Automated quality checks and validation
- **Error Handling**: Comprehensive error tracking and recovery
- **Performance Optimization**: Batch processing and parallel ingestion

### 1.2 Multi-Level Forecasting System
**Requirement**: Forecasting for various classifications and types, including NNDR and economic factors.

**Solution**:
- **Enhanced Forecasting Models**: Support for regression, time series, ML, and ensemble models
- **Multiple Scenarios**: Baseline, optimistic, pessimistic, and stress test scenarios
- **Economic Integration**: Direct integration with economic indicators
- **Classification Types**: Property type, business sector, geographic level forecasting

### 1.3 Master Gazetteer & Comprehensive Data
**Requirement**: Master gazetteer with all relevant data required for analysis.

**Solution**:
- **Enhanced Master Gazetteer**: Comprehensive property reference with 50+ fields
- **Data Sources Integration**: Multiple data sources with confidence scoring
- **Historical Tracking**: Complete valuation and property history
- **Business Intelligence**: Business indicators and market data

### 1.4 Local Council & Public Data Integration
**Requirement**: Local council forecasts and public data ingestion.

**Solution**:
- **Hierarchical Geography**: Country → Region → County → LAD → Ward → Parish
- **Economic Indicators**: Local economic data by geography and time
- **Public Data Sources**: Integration with ONS, OS, and other public datasets
- **Council-Specific Data**: Local authority boundaries and administrative data

### 1.5 Custom Map Layers & Visualization
**Requirement**: Custom map layers with controlled look, feel, pin icons, and styling.

**Solution**:
- **Map Layer Management**: Custom layer definitions and styling
- **Icon System**: Custom pin icons and symbols with color variants
- **Dynamic Styling**: Configurable colors, opacity, and visual properties
- **Interactive Features**: Popup configurations and legend management

## 2. Database Schema Architecture

### 2.1 Schema Organization

```
nndr_db/
├── public/                    # Core NNDR tables
│   ├── properties            # NNDR properties
│   ├── ratepayers            # NNDR ratepayers  
│   ├── valuations            # NNDR valuations
│   └── master_gazetteer      # Master property reference
├── staging/                   # Data staging and processing
│   ├── raw_nndr_list_entries # Raw NNDR data
│   ├── raw_geospatial_data   # Raw geospatial data
│   └── data_quality_checks   # Quality check results
├── geography/                 # Hierarchical geographic data
│   ├── countries             # Country level
│   ├── regions               # Region level (England, Scotland, etc.)
│   ├── counties              # County level
│   ├── local_authority_districts # LAD level
│   ├── electoral_wards       # Ward level
│   └── parishes              # Parish level
├── economic/                  # Economic data and indicators
│   ├── economic_indicators   # Economic indicators by geography/time
│   └── sector_economic_data  # Sector-specific economic data
├── forecasting/               # Enhanced forecasting system
│   ├── forecasting_models    # Model definitions and metadata
│   ├── forecasts             # Property and economic forecasts
│   ├── economic_scenario_forecasts # Economic scenario forecasts
│   └── non_rated_properties  # Non-rated property analysis
├── mapping/                   # Custom map layers and styling
│   ├── map_layers            # Layer definitions and styling
│   ├── custom_icons          # Custom pin icons and symbols
│   └── layer_icon_assignments # Icon assignments to layers
├── business_intelligence/     # KPIs and business metrics
│   ├── kpis                  # Key Performance Indicators
│   ├── kpi_measurements      # KPI measurements over time
│   ├── dashboards            # Dashboard configurations
│   └── dashboard_widgets     # Dashboard widget definitions
└── data_quality/              # Data quality and audit
    ├── quality_rules         # Data quality rules
    ├── quality_check_results # Quality check results
    └── data_lineage          # Data lineage tracking
```

### 2.2 Key Table Specifications

#### Master Gazetteer (Enhanced)
```sql
CREATE TABLE master_gazetteer (
    -- Primary identification
    id SERIAL PRIMARY KEY,
    uprn BIGINT UNIQUE,                    -- Unique Property Reference Number
    ba_reference VARCHAR(32),              -- Billing Authority Reference
    property_id VARCHAR(64),               -- Internal property identifier
    
    -- Property details (50+ fields)
    property_name TEXT,
    property_description TEXT,
    property_category_code VARCHAR(16),
    property_category_description TEXT,
    
    -- Address information (comprehensive)
    address_line_1 TEXT,
    address_line_2 TEXT,
    address_line_3 TEXT,
    address_line_4 TEXT,
    address_line_5 TEXT,
    street_descriptor TEXT,
    locality TEXT,
    post_town TEXT,
    administrative_area TEXT,
    postcode VARCHAR(16),
    postcode_district VARCHAR(8),
    
    -- Geographic coordinates (multiple systems)
    x_coordinate DOUBLE PRECISION,         -- Easting (OSGB)
    y_coordinate DOUBLE PRECISION,         -- Northing (OSGB)
    latitude DOUBLE PRECISION,             -- WGS84
    longitude DOUBLE PRECISION,            -- WGS84
    geom GEOMETRY(Point, 27700),           -- PostGIS geometry
    
    -- Administrative boundaries (hierarchical)
    lad_code VARCHAR(10),                  -- Local Authority District code
    lad_name TEXT,                         -- Local Authority District name
    ward_code VARCHAR(10),                 -- Electoral ward code
    ward_name TEXT,                        -- Electoral ward name
    parish_code VARCHAR(10),               -- Parish code
    parish_name TEXT,                      -- Parish name
    constituency_code VARCHAR(10),         -- Parliamentary constituency
    constituency_name TEXT,                -- Parliamentary constituency name
    
    -- Statistical areas
    lsoa_code VARCHAR(10),                 -- Lower Super Output Area
    lsoa_name TEXT,                        -- Lower Super Output Area name
    msoa_code VARCHAR(10),                 -- Middle Super Output Area
    msoa_name TEXT,                        -- Middle Super Output Area name
    oa_code VARCHAR(10),                   -- Output Area code
    
    -- Economic indicators
    imd_decile INTEGER,                    -- Index of Multiple Deprivation decile
    imd_rank INTEGER,                      -- Index of Multiple Deprivation rank
    rural_urban_code VARCHAR(2),           -- Rural/Urban classification
    
    -- Property characteristics
    property_type TEXT,                    -- Type of property (commercial, industrial, etc.)
    building_type TEXT,                    -- Specific building type
    floor_area NUMERIC,                    -- Floor area in square meters
    number_of_floors INTEGER,              -- Number of floors
    construction_year INTEGER,             -- Year of construction
    last_refurbished INTEGER,              -- Year of last refurbishment
    
    -- Current rating information
    current_rateable_value NUMERIC,
    current_effective_date DATE,
    current_scat_code VARCHAR(16),
    current_appeal_status VARCHAR(32),
    current_exemption_code VARCHAR(16),
    current_relief_code VARCHAR(16),
    
    -- Historical rating data
    historical_rateable_values JSONB,      -- Array of historical values with dates
    valuation_history_count INTEGER,       -- Number of historical valuations
    
    -- Ratepayer information
    current_ratepayer_name TEXT,
    current_ratepayer_type VARCHAR(32),    -- Individual, Company, Charity, etc.
    current_ratepayer_company_number VARCHAR(32),
    current_liability_start_date DATE,
    current_annual_charge NUMERIC,
    
    -- Business indicators
    business_type VARCHAR(64),             -- Type of business
    business_sector VARCHAR(64),           -- Business sector classification
    employee_count_range VARCHAR(32),      -- Estimated employee count range
    turnover_range VARCHAR(32),            -- Estimated turnover range
    
    -- Development and planning
    planning_permission_status VARCHAR(32),
    last_planning_decision_date DATE,
    development_potential_score NUMERIC,   -- 0-100 score for development potential
    
    -- Market indicators
    market_value_estimate NUMERIC,
    market_value_source VARCHAR(32),
    market_value_date DATE,
    rental_value_estimate NUMERIC,
    rental_value_source VARCHAR(32),
    rental_value_date DATE,
    
    -- Risk and compliance
    compliance_risk_score NUMERIC,         -- 0-100 risk score
    last_inspection_date DATE,
    enforcement_notices_count INTEGER,
    
    -- Forecasting indicators
    forecast_rateable_value NUMERIC,
    forecast_effective_date DATE,
    forecast_confidence_score NUMERIC,     -- 0-100 confidence in forecast
    forecast_factors JSONB,                -- Factors influencing forecast
    
    -- Data quality and sources
    data_quality_score NUMERIC,            -- 0-100 data quality score
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_sources JSONB,                    -- Array of data sources used
    source_priority INTEGER,               -- Priority of source (1=highest)
    
    -- System fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);
```

#### Economic Indicators (Comprehensive)
```sql
CREATE TABLE economic.economic_indicators (
    id SERIAL PRIMARY KEY,
    geography_type VARCHAR(20),            -- 'country', 'region', 'county', 'lad', 'ward'
    geography_code VARCHAR(10),
    indicator_date DATE NOT NULL,
    
    -- Economic indicators
    gdp_growth_rate NUMERIC(5,4),
    inflation_rate NUMERIC(5,4),
    unemployment_rate NUMERIC(5,4),
    interest_rate NUMERIC(5,4),
    exchange_rate_gbp_usd NUMERIC(8,4),
    exchange_rate_gbp_eur NUMERIC(8,4),
    
    -- Property market indicators
    commercial_property_growth_rate NUMERIC(5,4),
    industrial_property_growth_rate NUMERIC(5,4),
    retail_property_growth_rate NUMERIC(5,4),
    office_property_growth_rate NUMERIC(5,4),
    
    -- Business indicators
    business_formation_rate NUMERIC(5,4),
    business_closure_rate NUMERIC(5,4),
    employment_growth_rate NUMERIC(5,4),
    wage_growth_rate NUMERIC(5,4),
    
    -- Consumer indicators
    consumer_confidence_index NUMERIC(5,2),
    retail_sales_growth NUMERIC(5,4),
    housing_market_index NUMERIC(5,2),
    
    data_source VARCHAR(100),
    confidence_level NUMERIC(3,2),         -- 0-1 confidence in data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Enhanced Forecasting System
```sql
CREATE TABLE forecasting.forecasts (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES forecasting.forecasting_models(id),
    property_id INTEGER REFERENCES master_gazetteer(id),
    forecast_period_start DATE NOT NULL,
    forecast_period_end DATE NOT NULL,
    forecast_date DATE NOT NULL,
    forecast_scenario VARCHAR(50),         -- 'baseline', 'optimistic', 'pessimistic', 'stress_test'
    
    -- NNDR specific forecasts
    forecasted_rateable_value NUMERIC(15,2),
    forecasted_annual_charge NUMERIC(15,2),
    forecasted_net_charge NUMERIC(15,2),
    
    -- Economic factor forecasts
    forecasted_inflation_impact NUMERIC(5,4),
    forecasted_economic_growth_impact NUMERIC(5,4),
    forecasted_market_conditions_score NUMERIC(5,2),
    
    -- Confidence and uncertainty
    confidence_interval_lower NUMERIC(15,2),
    confidence_interval_upper NUMERIC(15,2),
    confidence_score NUMERIC(3,2),
    
    -- Forecast factors and reasoning
    forecast_factors JSONB,
    forecast_assumptions JSONB,
    economic_factors_considered JSONB,
    
    -- Validation
    actual_value NUMERIC(15,2),
    forecast_error NUMERIC(15,2),
    is_validated BOOLEAN DEFAULT FALSE,
    validation_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);
```

#### Custom Map Layers
```sql
CREATE TABLE mapping.map_layers (
    id SERIAL PRIMARY KEY,
    layer_name VARCHAR(100) UNIQUE NOT NULL,
    layer_description TEXT,
    layer_type VARCHAR(50),                -- 'choropleth', 'point', 'line', 'heatmap', 'custom'
    data_source_table VARCHAR(100),
    data_source_column VARCHAR(100),
    geometry_column VARCHAR(100),
    
    -- Styling configuration
    style_config JSONB,                    -- Colors, opacity, stroke width, etc.
    legend_config JSONB,                   -- Legend title, breaks, colors
    popup_config JSONB,                    -- Popup fields and formatting
    
    -- Display settings
    min_zoom INTEGER DEFAULT 0,
    max_zoom INTEGER DEFAULT 18,
    default_visible BOOLEAN DEFAULT TRUE,
    layer_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);
```

## 3. Performance Optimization Strategy

### 3.1 Database Performance
- **Partitioning**: Large tables partitioned by date and geography
- **Indexing Strategy**: Comprehensive indexing for all query patterns
- **Materialized Views**: Pre-computed aggregations for dashboard queries
- **Query Optimization**: Optimized queries with proper joins and filters

### 3.2 Data Ingestion Performance
- **Parallel Processing**: Multi-threaded data ingestion
- **Batch Operations**: Bulk inserts and updates
- **Staging Tables**: Efficient staging for data processing
- **Memory Management**: Chunked processing for large datasets

### 3.3 Query Performance
- **Spatial Indexes**: GIST indexes for all spatial data
- **Composite Indexes**: Multi-column indexes for complex queries
- **Partial Indexes**: Indexes on filtered data subsets
- **Covering Indexes**: Indexes that include all query columns

## 4. Data Quality Framework

### 4.1 Quality Rules
- **Null Value Checks**: Critical fields must not be null
- **Range Validation**: Numeric values within expected ranges
- **Format Validation**: Data format compliance
- **Referential Integrity**: Foreign key relationships
- **Geometric Validation**: Spatial data validity

### 4.2 Quality Monitoring
- **Automated Checks**: Scheduled quality checks
- **Issue Tracking**: Quality issue logging and resolution
- **Data Lineage**: Complete data flow tracking
- **Confidence Scoring**: Data quality confidence levels

## 5. Business Intelligence & Reporting

### 5.1 Key Performance Indicators
- **Financial KPIs**: Revenue collection, arrears, growth rates
- **Operational KPIs**: Processing times, error rates, data quality
- **Compliance KPIs**: Regulatory compliance, audit results
- **Forecasting KPIs**: Model accuracy, prediction confidence

### 5.2 Dashboard System
- **Executive Dashboards**: High-level business metrics
- **Operational Dashboards**: Day-to-day operational data
- **Analytical Dashboards**: Deep-dive analysis capabilities
- **Custom Dashboards**: User-defined dashboards

### 5.3 Reporting Framework
- **Automated Reports**: Scheduled report generation
- **Ad-hoc Queries**: Flexible query capabilities
- **Export Functionality**: Multiple export formats
- **Data Visualization**: Charts, graphs, and maps

## 6. Implementation Roadmap

### Phase 1: Core Infrastructure (Weeks 1-2)
- [ ] Enhanced database schema creation
- [ ] Staging area setup
- [ ] Data quality framework implementation
- [ ] Basic ingestion pipeline

### Phase 2: Data Integration (Weeks 3-4)
- [ ] NNDR data ingestion
- [ ] Geospatial data integration
- [ ] Economic data sources
- [ ] Master gazetteer population

### Phase 3: Forecasting System (Weeks 5-6)
- [ ] Forecasting model implementation
- [ ] Economic scenario modeling
- [ ] Non-rated property analysis
- [ ] Model validation framework

### Phase 4: Visualization & BI (Weeks 7-8)
- [ ] Custom map layers
- [ ] Dashboard development
- [ ] KPI implementation
- [ ] Reporting system

### Phase 5: Optimization & Testing (Weeks 9-10)
- [ ] Performance optimization
- [ ] Data quality validation
- [ ] User acceptance testing
- [ ] Production deployment

## 7. Success Metrics

### 7.1 Performance Metrics
- **Query Response Time**: < 2 seconds for dashboard queries
- **Data Ingestion Speed**: > 100,000 records/minute
- **System Availability**: > 99.9% uptime
- **Data Quality Score**: > 95% accuracy

### 7.2 Business Metrics
- **Forecasting Accuracy**: > 90% within 10% margin
- **Data Coverage**: > 95% of UK commercial properties
- **User Adoption**: > 80% of target users
- **ROI**: Positive return within 6 months

## 8. Risk Mitigation

### 8.1 Technical Risks
- **Data Quality Issues**: Comprehensive validation framework
- **Performance Problems**: Extensive testing and optimization
- **Integration Challenges**: Modular architecture design
- **Scalability Concerns**: Partitioning and indexing strategy

### 8.2 Business Risks
- **Data Availability**: Multiple data source agreements
- **Regulatory Changes**: Flexible schema design
- **User Adoption**: Comprehensive training and support
- **Budget Overruns**: Phased implementation approach

## 9. Conclusion

This enhanced database design provides a comprehensive solution that addresses all business requirements while ensuring optimal performance and accuracy. The modular architecture allows for phased implementation and future scalability, while the robust data quality framework ensures reliable and trustworthy data for business decision-making.

The system is designed to handle the complexity of NNDR data while providing the flexibility needed for custom analysis, forecasting, and visualization. With proper implementation and ongoing maintenance, this system will provide significant value to local authorities and other stakeholders in the business rates ecosystem. 