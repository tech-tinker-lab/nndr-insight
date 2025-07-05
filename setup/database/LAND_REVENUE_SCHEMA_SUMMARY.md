# Land Revenue and Property Sales Schema Summary

## Overview
The NNDR Insight system now includes comprehensive tables for land revenue, property sales, valuations, and market analysis data. This enables advanced analytics, forecasting, and business intelligence capabilities.

---

## New Tables Created

### 1. Property Sales (`property_sales`)
**Purpose**: Track property sales transactions and market activity

**Key Fields**:
- `ba_reference` - Billing Authority Reference (links to master_gazetteer)
- `uprn` - Unique Property Reference Number
- `sale_date` - Date of sale transaction
- `sale_price` - Sale price in GBP
- `sale_type` - freehold, leasehold, assignment, etc.
- `transaction_type` - arm_length, non_arm_length, auction, etc.
- `buyer_type` - individual, company, trust, government
- `property_condition` - good, fair, poor, development
- `planning_permission` - none, outline, full, implemented
- `development_potential` - none, low, medium, high

**Data Sources**: Land Registry (priority 1), Rightmove, Zoopla

---

### 2. Land Revenue (`land_revenue`)
**Purpose**: Track rental income and revenue streams from properties

**Key Fields**:
- `ba_reference` - Billing Authority Reference
- `uprn` - Unique Property Reference Number
- `revenue_year` - Year of revenue
- `revenue_type` - rental_income, service_charges, ground_rent, other
- `revenue_amount` - Revenue amount in GBP
- `revenue_frequency` - monthly, quarterly, annually, one_off
- `tenant_type` - retail, office, industrial, residential, mixed
- `lease_start_date` - Lease commencement date
- `lease_end_date` - Lease expiry date
- `lease_term_years` - Length of lease in years
- `rent_review_frequency` - 3_years, 5_years, 10_years, none
- `break_clause` - Whether lease has break clause
- `break_date` - Break clause date

**Data Sources**: Rental data providers, property management systems

---

### 3. Property Valuations (`property_valuations`)
**Purpose**: Track historic and current property valuations

**Key Fields**:
- `ba_reference` - Billing Authority Reference
- `uprn` - Unique Property Reference Number
- `valuation_date` - Date of valuation
- `valuation_type` - market_value, investment_value, development_value, rateable_value
- `valuation_method` - comparable_sales, income_capitalisation, cost_approach, residual
- `valuation_amount` - Valuation amount in GBP
- `valuer_name` - Name of valuer
- `valuer_qualification` - Professional qualification
- `confidence_level` - high, medium, low
- `assumptions` - Valuation assumptions and notes
- `market_conditions` - stable, rising, falling, volatile

**Data Sources**: RICS surveyors, valuation firms, automated valuation models

---

### 4. Market Analysis (`market_analysis`)
**Purpose**: Track market indicators and trends by LAD and property type

**Key Fields**:
- `lad_code` - Local Authority District code
- `lad_name` - Local Authority District name
- `analysis_date` - Date of analysis
- `property_type` - retail, office, industrial, mixed
- `market_indicator` - yield, capital_growth, rental_growth, vacancy_rate
- `indicator_value` - Numeric value of indicator
- `trend_direction` - up, down, stable
- `trend_strength` - strong, moderate, weak

**Data Sources**: Estates Gazette, property market reports, industry publications

---

### 5. Economic Indicators (`economic_indicators`)
**Purpose**: Track macroeconomic and regional economic data

**Key Fields**:
- `indicator_name` - Name of economic indicator
- `indicator_category` - macroeconomic, property_specific, regional
- `geographic_level` - national, regional, local
- `geographic_code` - Geographic area code
- `geographic_name` - Geographic area name
- `indicator_date` - Date of indicator
- `indicator_value` - Numeric value of indicator
- `unit_of_measure` - Unit of measurement

**Data Sources**: ONS, Bank of England, regional economic data

---

## Data Sources Configured

### Property Sales Sources
- **Land Registry** (Priority 1, Quality 0.98) - Official property sales data
- **Rightmove** (Priority 2, Quality 0.85) - Property listings and sales data
- **Zoopla** (Priority 2, Quality 0.85) - Property market data and valuations

### Market Analysis Sources
- **Estates Gazette** (Priority 1, Quality 0.90) - Commercial property market analysis

### Economic Indicators Sources
- **ONS Economic** (Priority 1, Quality 0.95) - Official economic data
- **Bank of England** (Priority 1, Quality 0.98) - Interest rates and monetary policy

### Land Revenue Sources
- **Rental Data** (Priority 2, Quality 0.80) - Commercial property rental information

---

## Performance Optimizations

### Indexes Created
- **Property Sales**: ba_reference, uprn, sale_date, sale_price
- **Land Revenue**: ba_reference, uprn, revenue_year
- **Property Valuations**: ba_reference, uprn, valuation_date
- **Market Analysis**: lad_code + analysis_date, property_type
- **Economic Indicators**: indicator_date, indicator_category

### Data Quality Rules
- Sale price validation (0 < price < 1B)
- Revenue amount validation (0 ≤ amount < 10M)
- Rateable value validation (0 < value < 100M)

---

## Use Cases Enabled

### 1. Property Market Analysis
- Track sales trends by property type and location
- Analyze price movements and market cycles
- Identify development opportunities

### 2. Revenue Forecasting
- Predict rental income based on market trends
- Forecast rateable value changes
- Model revenue impacts of market changes

### 3. Investment Analysis
- Compare property yields across locations
- Analyze investment performance
- Identify high-potential investment areas

### 4. Risk Assessment
- Monitor market volatility
- Track economic indicators
- Assess property-specific risks

### 5. Business Intelligence
- Generate market reports
- Create dashboards for stakeholders
- Support strategic decision-making

---

## Integration with NNDR System

### Links to Master Gazetteer
- All tables link via `ba_reference` to the master property database
- UPRN provides additional linking capability
- Enables comprehensive property analysis

### Source Tracking
- All records include source tracking information
- Confidence scores for data quality assessment
- Duplicate detection and resolution capabilities

### Forecasting Integration
- Data feeds into the existing forecasting system
- Enables more sophisticated forecasting models
- Supports scenario analysis and what-if modeling

---

## Next Steps

### 1. Data Ingestion
- Implement ingestion scripts for each data source
- Set up automated data collection processes
- Establish data quality monitoring

### 2. Analytics Development
- Create market analysis dashboards
- Develop forecasting models using new data
- Build reporting tools for stakeholders

### 3. Integration
- Connect with existing NNDR analysis tools
- Integrate with visualization systems
- Link to external data sources

### 4. Validation
- Test data quality and accuracy
- Validate forecasting model performance
- Conduct user acceptance testing

---

## Benefits

1. **Comprehensive Analysis**: Full picture of property market and revenue
2. **Better Forecasting**: More data sources improve prediction accuracy
3. **Risk Management**: Early warning of market changes
4. **Strategic Planning**: Data-driven decision making
5. **Revenue Optimization**: Identify opportunities for revenue growth
6. **Regulatory Compliance**: Track and report on market conditions

This enhanced schema provides a solid foundation for advanced NNDR analytics and business intelligence capabilities. 