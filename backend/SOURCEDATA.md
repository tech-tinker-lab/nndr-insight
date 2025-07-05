# Source Data for NNDR Insight Backend

## What is Source Data?

**Source data** refers to the original datasets ingested into the system, providing the foundational information for all downstream analytics, business logic, and reporting. In the context of NNDR Insight, source data includes authoritative, open, and/or official datasets that describe properties, addresses, locations, administrative boundaries, business rates, and related economic indicators for the UK.

Source data is essential for:
- Building a comprehensive gazetteer (property/address/location reference)
- Linking properties to ratepayers and business rates (NNDR)
- Enabling spatial analysis, geocoding, and mapping
- Supporting business, economic, and valuation reporting

## Current Source Datasets

The system currently ingests the following key datasets:

- **OS Open UPRN**: Unique Property Reference Numbers with coordinates for every property in Great Britain
- **Code-Point Open**: Postcode to coordinate mapping for the UK
- **ONSPD (ONS Postcode Directory)**: Postcode centroids and administrative/statistical geographies
- **OS Open USRN**: Unique Street Reference Numbers for every street
- **OS Open Names**: Gazetteer of place names, settlements, and streets
- **OS Open Map – Local**: Vector map data (buildings, roads, etc.)
- **Local Authority District Shapefiles**: Administrative boundaries for spatial joins and mapping
- **NNDR/VOA Rating List and Valuations**: Business rates, ratepayer, and valuation data for multiple years

## Additional Data Required for a Comprehensive System

To provide a full suite of business services—such as advanced gazetteer queries, ratepayer analytics, NNDR forecasting, economic and business valuation reports, and more—the following additional data sources are recommended or required:

### 1. **Enhanced Property & Address Data**
- **Land Registry Price Paid Data**: For property sales, ownership, and transaction history
- **Commercial property datasets**: For non-domestic property details, usage, and classifications
- **Building footprints and heights**: For 3D mapping, valuation, and planning

### 2. **Business & Economic Data**
- **Companies House**: Business registrations, directors, and company status
- **Business rates reliefs and exemptions**: Detailed records of reliefs, exemptions, and appeals
- **Employment and economic activity data**: ONS or local authority datasets on jobs, sectors, and economic output
- **Business directories**: For linking ratepayers to active businesses and economic sectors

### 3. **Valuation & Market Data**
- **VOA (Valuation Office Agency) datasets**: More granular valuation data, appeals, and historic changes
- **Commercial property market data**: Rents, yields, and vacancy rates
- **Planning applications and consents**: For understanding development pipeline and property changes

### 4. **Spatial & Environmental Data**
- **Flood risk, environmental constraints, and land use**: For risk assessment and planning
- **Transport and accessibility data**: Proximity to stations, roads, and public transport
- **Points of interest (POI) datasets**: For context in valuation and economic analysis

### 5. **Temporal & Change Data**
- **Historic rating lists and property changes**: For time series analysis and forecasting
- **Boundary changes and administrative updates**: To maintain accurate spatial joins over time

## Why These Are Needed
- **Comprehensive Analytics**: To answer complex business questions about property, ratepayers, and economic value
- **Accurate Valuation**: To support robust, defensible business and economic valuation reports
- **Policy & Planning**: To inform local authority, government, and business decision-making
- **Forecasting & Trends**: To enable predictive analytics and scenario planning

## Summary Table

| Data Type | Example Sources | Use Cases |
|-----------|----------------|-----------|
| Property & Address | OS Open UPRN, Land Registry | Gazetteer, ownership, sales history |
| Business & Economic | Companies House, ONS, business directories | Ratepayer linkage, sector analysis |
| Valuation & Market | VOA, commercial market data | NNDR, valuation, forecasting |
| Spatial & Environmental | OS, DEFRA, transport datasets | Risk, planning, accessibility |
| Temporal & Change | VOA, ONS, local authorities | Time series, forecasting, change detection |

---

*This document should be updated as new data sources are integrated or as business requirements evolve.* 