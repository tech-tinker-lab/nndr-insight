# Table Analysis and Business Rate Forecasting System Design

## Executive Summary

This document provides a comprehensive analysis of all database tables and presents a complete system design for South Cambridgeshire District Council's business rate forecasting and non-rated property identification system.

## Database Table Analysis

### Current Table Structure Overview

| Table Category | Tables | Records | Purpose |
|---------------|--------|---------|---------|
| **Core NNDR** | 5 tables | Variable | Business rates and property data |
| **Geospatial** | 7 tables | Variable | Location and mapping data |
| **Staging** | 5 tables | Variable | Temporary data for ingestion |
| **Total** | **17 tables** | **Variable** | Complete NNDR Insight schema |

### Detailed Table Analysis

#### 1. Core NNDR Tables

##### A. `properties` Table
- **Purpose**: Main property records with addresses and categories
- **Key Fields**: 
  - `ba_reference` (Billing Authority Reference) - Primary identifier
  - `property_category_code` - Property classification
  - `rateable_value` - Current rateable value
  - `postcode` - Geographic location
- **Data Quality**: High - official NNDR data
- **Forecasting Value**: Critical - base data for all forecasts

##### B. `ratepayers` Table
- **Purpose**: Ratepayer information linked to properties
- **Key Fields**:
  - `property_id` - Links to properties table
  - `name` - Ratepayer name
  - `annual_charge` - Current annual charge
  - `exemption_code` - Relief/exemption information
- **Data Quality**: High - official billing data
- **Forecasting Value**: Important - payment behavior analysis

##### C. `valuations` Table
- **Purpose**: Current property valuations
- **Key Fields**:
  - `ba_reference` - Property identifier
  - `rateable_value` - Valuation amount
  - `effective_date` - When valuation takes effect
  - `uprn` - Unique Property Reference Number
- **Data Quality**: High - official valuation data
- **Forecasting Value**: Critical - valuation trends

##### D. `historic_valuations` Table
- **Purpose**: Historical valuation records
- **Key Fields**:
  - `ba_reference` - Property identifier
  - `rateable_value` - Historical value
  - `change_date` - When change occurred
  - `source` - Data source
- **Data Quality**: High - official historical data
- **Forecasting Value**: Critical - trend analysis

##### E. `categories` Table
- **Purpose**: Property category codes and descriptions
- **Key Fields**:
  - `code` - Category code
  - `description` - Category description
- **Data Quality**: High - reference data
- **Forecasting Value**: Important - category-based analysis

#### 2. Geospatial Tables

##### A. `gazetteer` Table
- **Purpose**: Property location data with coordinates
- **Key Fields**:
  - `property_id` - Unique property identifier
  - `latitude/longitude` - Geographic coordinates
  - `address` - Property address
  - `postcode` - Postal code
- **Data Quality**: High - OS data
- **Forecasting Value**: Important - location-based analysis

##### B. `os_open_uprn` Table
- **Purpose**: OS Open UPRN data with coordinates
- **Key Fields**:
  - `uprn` - Unique Property Reference Number
  - `x_coordinate/y_coordinate` - OSGB coordinates
  - `latitude/longitude` - WGS84 coordinates
- **Data Quality**: Very High - official OS data
- **Forecasting Value**: Critical - property identification

##### C. `code_point_open` Table
- **Purpose**: Postcode to coordinate mapping
- **Key Fields**:
  - `postcode` - Postal code
  - `easting/northing` - OSGB coordinates
  - `admin_district_code` - Administrative area
- **Data Quality**: High - official OS data
- **Forecasting Value**: Important - geographic analysis

##### D. `onspd` Table
- **Purpose**: ONS Postcode Directory data
- **Key Fields**:
  - `pcds` - Postcode
  - `lat/long` - Coordinates
  - `lsoa11/msoa11` - Statistical areas
  - `imd` - Index of Multiple Deprivation
- **Data Quality**: High - official ONS data
- **Forecasting Value**: Important - socioeconomic analysis

##### E. `os_open_names` Table
- **Purpose**: OS Open Names with spatial geometry
- **Key Fields**:
  - `os_id` - OS identifier
  - `name1/name2` - Place names
  - `geom` - PostGIS geometry
  - `type` - Feature type
- **Data Quality**: High - official OS data
- **Forecasting Value**: Moderate - location context

##### F. `lad_boundaries` Table
- **Purpose**: Local Authority District boundaries
- **Key Fields**:
  - `lad_code` - LAD code
  - `lad_name` - LAD name
  - `geometry` - PostGIS geometry
- **Data Quality**: High - official boundary data
- **Forecasting Value**: Important - administrative analysis

##### G. `os_open_map_local` Table
- **Purpose**: OS Open Map Local features
- **Key Fields**:
  - `feature_id` - Feature identifier
  - `feature_type` - Type of feature
  - `geometry` - PostGIS geometry
- **Data Quality**: High - official OS data
- **Forecasting Value**: Moderate - building footprint analysis

#### 3. Staging Tables
- **Purpose**: Temporary data storage during ingestion
- **Data Quality**: Variable - depends on source
- **Forecasting Value**: Low - processing only

## Master Gazetteer Design

### Purpose
The master gazetteer consolidates all property and location data into a single, comprehensive table for business rate forecasting and analysis.

### Key Features
1. **Unified Property Identification**: Combines UPRN, BA Reference, and internal IDs
2. **Complete Address Hierarchy**: Full address structure with postcode
3. **Geographic Data**: Coordinates, PostGIS geometry, administrative boundaries
4. **Property Characteristics**: Type, size, construction details, business indicators
5. **Rating Information**: Current and historical rateable values
6. **Forecasting Data**: Forecasted values, confidence scores, influencing factors
7. **Quality Metrics**: Data quality scores, source tracking

### Data Integration Strategy
1. **Primary Sources**: Properties table (NNDR data)
2. **Geographic Enrichment**: OS Open UPRN, Code-Point Open
3. **Socioeconomic Context**: ONSPD data
4. **Ratepayer Information**: Ratepayers table
5. **Historical Data**: Historic valuations table

## Business Rate Forecasting System

### System Architecture

#### 1. Data Layer
- **Master Gazetteer**: Central data repository
- **Forecasting Models**: Machine learning and statistical models
- **Forecasts**: Individual property forecasts
- **Scenarios**: Economic and policy scenarios
- **Reports**: Generated forecasting reports

#### 2. Analytics Layer
- **Data Processing**: Cleaning, enrichment, feature engineering
- **Model Development**: Regression, time series, machine learning
- **Validation**: Cross-validation, back-testing, performance metrics
- **Forecasting**: Multi-scenario forecasting with confidence intervals

#### 3. Application Layer
- **APIs**: RESTful APIs for data access
- **Dashboards**: Interactive visualization and reporting
- **Workflows**: Investigation and compliance workflows
- **Alerts**: Automated alerts and notifications

### Forecasting Methodology

#### 1. Data Preparation
- **Data Cleaning**: Remove duplicates, standardize formats
- **Data Enrichment**: Add missing information from multiple sources
- **Feature Engineering**: Create derived features for machine learning
- **Quality Assessment**: Score data quality and completeness

#### 2. Model Development
- **Regression Models**: Linear regression, polynomial regression
- **Time Series Models**: ARIMA, SARIMA, Prophet
- **Machine Learning**: Random Forest, Gradient Boosting, Neural Networks
- **Ensemble Methods**: Combine multiple models for improved accuracy

#### 3. Feature Selection
- **Property Characteristics**: Size, type, age, condition
- **Location Factors**: Area type, accessibility, economic indicators
- **Market Factors**: Local market trends, supply/demand
- **Economic Indicators**: GDP growth, inflation, employment rates
- **Policy Factors**: Rate changes, relief schemes, exemptions

#### 4. Validation and Testing
- **Cross-Validation**: K-fold cross-validation for model robustness
- **Back-Testing**: Test models on historical data
- **Performance Metrics**: RMSE, MAE, MAPE, R-squared
- **Confidence Intervals**: Quantify forecast uncertainty

### Non-Rated Property Identification

#### 1. Detection Methods
- **Geographic Analysis**: Building footprint analysis, postcode comparison
- **Business Activity Indicators**: Company registration, planning applications
- **Property Characteristics**: Building type, size thresholds, location context

#### 2. Scoring Algorithm
- **Multi-Factor Scoring**: Combine multiple indicators
- **Weighted Scoring**: Different weights for different factors
- **Confidence Levels**: Quantify certainty of rating potential
- **Priority Ranking**: Rank properties for investigation

#### 3. Investigation Workflow
- **Automated Screening**: Initial automated assessment
- **Manual Review**: Human review of high-priority cases
- **Field Investigation**: Physical inspection where needed
- **Decision Tracking**: Record investigation outcomes

## Implementation Plan

### Phase 1: Foundation (Months 1-3)
1. **Database Schema Implementation**
   - Create master gazetteer table
   - Implement forecasting system tables
   - Set up data integration pipelines

2. **Data Integration**
   - Populate master gazetteer from existing tables
   - Implement data quality scoring
   - Establish data validation processes

3. **Basic Forecasting Models**
   - Develop simple regression models
   - Implement time series analysis
   - Create baseline forecasting algorithms

### Phase 2: Core Features (Months 4-6)
1. **Advanced Forecasting Algorithms**
   - Machine learning model development
   - Ensemble method implementation
   - Confidence interval calculation

2. **Non-Rated Property Detection**
   - Detection algorithm development
   - Scoring system implementation
   - Investigation workflow design

3. **Basic Reporting and Dashboards**
   - Forecast reporting system
   - Basic visualization dashboards
   - Data export capabilities

### Phase 3: Advanced Features (Months 7-9)
1. **Machine Learning Models**
   - Advanced ML model development
   - Model performance optimization
   - Automated model selection

2. **Advanced Analytics**
   - Market analysis implementation
   - Trend prediction algorithms
   - Risk assessment systems

3. **Compliance Monitoring**
   - Compliance tracking system
   - Enforcement action management
   - Risk scoring algorithms

### Phase 4: Optimization (Months 10-12)
1. **Performance Optimization**
   - Database query optimization
   - API performance tuning
   - System scalability improvements

2. **User Training and Adoption**
   - User interface refinement
   - Training program development
   - User feedback integration

3. **System Refinement**
   - Bug fixes and improvements
   - Feature enhancements
   - Documentation completion

## Expected Outcomes

### 1. Forecasting Accuracy
- **Target**: 95% accuracy within 5% margin of error
- **Confidence Intervals**: Provide uncertainty quantification
- **Scenario Analysis**: Multiple economic scenarios

### 2. Non-Rated Property Detection
- **Detection Rate**: Identify 90%+ of non-rated properties
- **False Positive Rate**: <10% false positives
- **Investigation Efficiency**: Prioritize high-value cases

### 3. Revenue Impact
- **Additional Revenue**: Identify significant additional rateable value
- **Forecast Accuracy**: Improve budget planning accuracy
- **Compliance**: Increase compliance rates

## Success Metrics

### 1. Forecasting Metrics
- **Accuracy**: Mean Absolute Percentage Error (MAPE)
- **Reliability**: Confidence interval coverage
- **Timeliness**: Forecast generation speed

### 2. Detection Metrics
- **Recall**: Percentage of non-rated properties identified
- **Precision**: Percentage of identified properties actually rateable
- **Efficiency**: Investigation success rate

### 3. Business Metrics
- **Revenue Impact**: Additional revenue identified
- **Cost Savings**: Reduced investigation costs
- **User Satisfaction**: System usability and adoption

## Risk Management

### 1. Data Quality Risks
- **Mitigation**: Comprehensive data validation and quality scoring
- **Monitoring**: Regular data quality assessments
- **Backup**: Multiple data sources for validation

### 2. Model Accuracy Risks
- **Mitigation**: Multiple model types and ensemble methods
- **Validation**: Extensive back-testing and validation
- **Monitoring**: Continuous performance monitoring

### 3. Legal and Compliance Risks
- **Mitigation**: Legal review of detection methods
- **Documentation**: Comprehensive audit trail
- **Appeals Process**: Clear appeals and review process

## Conclusion

This comprehensive system will provide South Cambridgeshire District Council with:

1. **Accurate Business Rate Forecasting**: Reliable predictions for budget planning
2. **Systematic Non-Rated Property Identification**: Systematic approach to finding missing properties
3. **Data-Driven Insights**: Comprehensive analytics for strategic decision-making
4. **Improved Compliance**: Enhanced monitoring and enforcement capabilities
5. **Operational Efficiency**: Streamlined processes and automated workflows

The system leverages advanced analytics, machine learning, and comprehensive data integration to deliver reliable, actionable insights for NNDR management, meeting the council's requirements for accurate forecasting and non-rated property identification. 