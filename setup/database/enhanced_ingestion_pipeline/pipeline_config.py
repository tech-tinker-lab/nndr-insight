#!/usr/bin/env python3
"""
Configuration file for the Comprehensive Data Ingestion Pipeline
"""

import os
from typing import Dict, Any

# Database Configuration
DB_CONFIG = {
    'connection_string': None,  # Will be loaded from db_config
    'batch_size': 10000,
    'max_workers': 4,
    'chunk_size': 50000,
    'temp_dir': '/tmp/ingestion_temp'
}

# Data Directory Configuration
DATA_DIRECTORIES = {
    'main_data': os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'data'),
    'backup_data': os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'data', 'backup'),
    'temp_data': os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'data', 'temp')
}

# Enhanced Data Source Configurations
ENHANCED_DATA_SOURCES = {
    # NNDR Business Rate Data
    'voa_2023': {
        'priority': 1,
        'description': 'VOA 2023 NNDR Compiled List - Official source',
        'file_pattern': 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-csv.csv',
        'format': 'pipe_delimited',
        'coordinate_system': 'wgs84',
        'quality_score': 0.95,
        'update_frequency': 'annual',
        'source_type': 'nndr',
        'enabled': True,
        'field_mapping': {
            'ba_reference': 2,
            'property_category_code': 3,
            'property_description': 4,
            'scat_code': 5,
            'property_address': 6,
            'street_descriptor': 8,
            'post_town': 9,
            'locality': 10,
            'postcode': 11,
            'rateable_value': 12,
            'uprn': 13,
            'effective_date': 15
        }
    },
    
    # 'voa_historic': {
    #     'priority': 1,
    #     'description': 'VOA Historic NNDR Data',
    #     'file_pattern': 'uk-englandwales-ndr-2023-listentries-compiled-epoch-0015-baseline-historic-csv.csv',
    #     'format': 'pipe_delimited',
    #     'coordinate_system': 'wgs84',
    #     'quality_score': 0.95,
    #     'update_frequency': 'annual',
    #     'source_type': 'nndr',
    #     'enabled': True,
    #     'field_mapping': {
    #         'ba_reference': 2,
    #         'property_category_code': 3,
    #         'property_description': 4,
    #         'scat_code': 5,
    #         'property_address': 6,
    #         'street_descriptor': 8,
    #         'post_town': 9,
    #         'locality': 10,
    #         'postcode': 11,
    #         'rateable_value': 12,
    #         'uprn': 13,
    #         'effective_date': 15
    #     }
    # },
    
    'local_council_2015': {
        'priority': 2,
        'description': 'Local Council NNDR Data 2015 - Supplementary source',
        'file_pattern': 'NNDR Rating List  March 2015_0.csv',
        'format': 'csv',
        'coordinate_system': 'unknown',
        'quality_score': 0.85,
        'update_frequency': 'annual',
        'source_type': 'nndr',
        'enabled': True,
        'field_mapping': {
            'BAReference': 'ba_reference',
            'PropertyCategoryCode': 'property_category_code',
            'PropertyDescription': 'property_description',
            'PropertyAddress': 'property_address',
            'StreetDescriptor': 'street_descriptor',
            'Locality': 'locality',
            'PostTown': 'post_town',
            'AdministrativeArea': 'administrative_area',
            'PostCode': 'postcode',
            'RateableValue': 'rateable_value',
            'SCATCode': 'scat_code',
            'UniquePropertyRef': 'uprn',
            'EffectiveDate': 'effective_date'
        }
    },
    
    # 'sample_nndr': {
    #     'priority': 3,
    #     'description': 'Sample NNDR Data - Development and testing',
    #     'file_pattern': 'sample_nndr.csv',
    #     'format': 'csv',
    #     'coordinate_system': 'wgs84',
    #     'quality_score': 0.80,
    #     'update_frequency': 'manual',
    #     'source_type': 'nndr',
    #     'enabled': True,
    #     'field_mapping': {
    #         'PropertyID': 'ba_reference',
    #         'Address': 'property_address',
    #         'Postcode': 'postcode',
    #         'RateableValue': 'rateable_value',
    #         'Description': 'property_description',
    #         'Latitude': 'latitude',
    #         'Longitude': 'longitude',
    #         'CurrentRatingStatus': 'property_category_code',
    #         'LastBilledDate': 'effective_date'
    #     }
    # },
    
    # Geospatial Reference Data
    'os_uprn': {
        'priority': 1,
        'description': 'OS Open UPRN - Official property reference numbers with coordinates',
        'file_pattern': 'osopenuprn_202506_csv/osopenuprn_202506.csv',
        'format': 'csv',
        'coordinate_system': 'osgb',
        'quality_score': 0.98,
        'update_frequency': 'monthly',
        'source_type': 'reference',
        'enabled': True,
        'field_mapping': {
            'UPRN': 'uprn',
            'X_COORDINATE': 'x_coordinate',
            'Y_COORDINATE': 'y_coordinate',
            'LATITUDE': 'latitude',
            'LONGITUDE': 'longitude'
        }
    },
    
    'codepoint': {
        'priority': 2,
        'description': 'CodePoint Open - Postcode to coordinate mapping',
        'file_pattern': 'codepo_gb/Data/CSV/*.csv',
        'format': 'csv',
        'coordinate_system': 'osgb',
        'quality_score': 0.90,
        'update_frequency': 'quarterly',
        'source_type': 'reference',
        'enabled': False,
        'field_mapping': {
            'postcode': 'postcode',
            'positional_quality_indicator': 'positional_quality_indicator',
            'easting': 'eastings',
            'northing': 'northings',
            'country_code': 'country_code',
            'nhs_regional_ha_code': 'nhs_regional_ha_code',
            'nhs_ha_code': 'nhs_ha_code',
            'admin_county_code': 'admin_county_code',
            'admin_district_code': 'admin_district_code',
            'admin_ward_code': 'admin_ward_code'
        }
    },
    
    'onspd': {
        'priority': 1,
        'description': 'ONS Postcode Directory - Comprehensive postcode data with administrative geographies',
        'file_pattern': 'ONSPD_Online_Latest_Centroids.csv',
        'format': 'csv',
        'coordinate_system': 'osgb',
        'quality_score': 0.95,
        'update_frequency': 'quarterly',
        'source_type': 'reference',
        'enabled': False,
        'field_mapping': {
            'X': 'x',
            'Y': 'y',
            'OBJECTID': 'objectid',
            'PCD': 'pcd',
            'PCD2': 'pcd2',
            'PCDS': 'pcds',
            'DOINTR': 'dointr',
            'DOTERM': 'doterm',
            'OSCTY': 'oscty',
            'CED': 'ced',
            'OSLAUA': 'oslaua',
            'OSWARD': 'osward',
            'PARISH': 'parish',
            'USERTYPE': 'usertype',
            'OSEAST1M': 'oseast1m',
            'OSNRTH1M': 'osnrth1m',
            'OSGRDIND': 'osgrdind',
            'OSHLTHAU': 'oshlthau',
            'NHSER': 'nhser',
            'CTRY': 'ctry',
            'RGN': 'rgn',
            'STREG': 'streg',
            'PCON': 'pcon',
            'EER': 'eer',
            'TECLEC': 'teclec',
            'TTWA': 'ttwa',
            'PCT': 'pct',
            'ITL': 'itl',
            'STATSWARD': 'statsward',
            'OA01': 'oa01',
            'CASWARD': 'casward',
            'NPARK': 'npark',
            'LSOA01': 'lsoa01',
            'MSOA01': 'msoa01',
            'UR01IND': 'ur01ind',
            'OAC01': 'oac01',
            'OA11': 'oa11',
            'LSOA11': 'lsoa11',
            'MSOA11': 'msoa11',
            'WZ11': 'wz11',
            'SICBL': 'sicbl',
            'BUA24': 'bua24',
            'RU11IND': 'ru11ind',
            'OAC11': 'oac11',
            'LAT': 'lat',
            'LONG': 'long',
            'LEP1': 'lep1',
            'LEP2': 'lep2',
            'PFA': 'pfa',
            'IMD': 'imd',
            'CALNCV': 'calncv',
            'ICB': 'icb',
            'OA21': 'oa21',
            'LSOA21': 'lsoa21',
            'MSOA21': 'msoa21',
            'RUC21IND': 'ruc21ind',
            'GlobalID': 'globalid'
        }
    },
    
    # Land Revenue and Property Sales Data
    'land_registry': {
        'priority': 1,
        'description': 'HM Land Registry - Official property sales data',
        'file_pattern': 'land_registry_sales_*.csv',
        'format': 'csv',
        'coordinate_system': 'osgb',
        'quality_score': 0.98,
        'update_frequency': 'monthly',
        'source_type': 'property_sales',
        'enabled': False,  # Disabled until data files are available
        'field_mapping': {
            'price': 'sale_price',
            'date_of_transfer': 'sale_date',
            'property_type': 'sale_type',
            'new_build': 'property_condition',
            'estate_type': 'transaction_type',
            'paon': 'property_name',
            'saon': 'property_unit',
            'street': 'street_descriptor',
            'locality': 'locality',
            'town_city': 'post_town',
            'district': 'administrative_area',
            'county': 'county',
            'postcode': 'postcode'
        }
    },
    
    'rightmove': {
        'priority': 2,
        'description': 'Rightmove - Property listings and sales data',
        'file_pattern': 'rightmove_*.csv',
        'format': 'csv',
        'coordinate_system': 'wgs84',
        'quality_score': 0.85,
        'update_frequency': 'weekly',
        'source_type': 'property_sales',
        'enabled': False,  # Disabled until data files are available
        'field_mapping': {
            'price': 'sale_price',
            'date_added': 'listing_date',
            'property_type': 'sale_type',
            'address': 'property_address',
            'postcode': 'postcode',
            'latitude': 'latitude',
            'longitude': 'longitude'
        }
    },
    
    'estates_gazette': {
        'priority': 1,
        'description': 'Estates Gazette - Commercial property market analysis',
        'file_pattern': 'estates_gazette_*.csv',
        'format': 'csv',
        'coordinate_system': 'unknown',
        'quality_score': 0.90,
        'update_frequency': 'monthly',
        'source_type': 'market_analysis',
        'enabled': False,  # Disabled until data files are available
        'field_mapping': {
            'lad_code': 'lad_code',
            'property_type': 'property_type',
            'yield': 'indicator_value',
            'capital_growth': 'capital_growth',
            'rental_growth': 'rental_growth',
            'vacancy_rate': 'vacancy_rate'
        }
    },
    
    'ons_economic': {
        'priority': 1,
        'description': 'ONS Economic Indicators - Official economic data',
        'file_pattern': 'ons_economic_*.csv',
        'format': 'csv',
        'coordinate_system': 'n/a',
        'quality_score': 0.95,
        'update_frequency': 'monthly',
        'source_type': 'economic_indicators',
        'enabled': False,  # Disabled until data files are available
        'field_mapping': {
            'indicator_name': 'indicator_name',
            'geographic_code': 'geographic_code',
            'geographic_name': 'geographic_name',
            'indicator_date': 'indicator_date',
            'indicator_value': 'indicator_value',
            'unit_of_measure': 'unit_of_measure'
        }
    },
    'os_open_names': {
        'priority': 1,
        'description': 'OS Open Names - Address reference data',
        'file_pattern': 'opname_csv_gb/Data/*.csv',
        'format': 'csv',
        'coordinate_system': 'osgb',
        'quality_score': 0.95,
        'update_frequency': 'annual',
        'source_type': 'reference',
        'enabled': False,
        'field_mapping': {
            'ID': 'os_id',
            'NAMES_URI': 'names_uri',
            'NAME1': 'name1',
            'NAME1_LANG': 'name1_lang',
            'NAME2': 'name2',
            'NAME2_LANG': 'name2_lang',
            'TYPE': 'type',
            'LOCAL_TYPE': 'local_type',
            'GEOMETRY_X': 'geometry_x',
            'GEOMETRY_Y': 'geometry_y',
            'MOST_DETAIL_VIEW_RES': 'most_detail_view_res',
            'LEAST_DETAIL_VIEW_RES': 'least_detail_view_res',
            'MBR_XMIN': 'mbr_xmin',
            'MBR_YMIN': 'mbr_ymin',
            'MBR_XMAX': 'mbr_xmax',
            'MBR_YMAX': 'mbr_ymax',
            'POSTCODE_DISTRICT': 'postcode_district',
            'POSTCODE_DISTRICT_URI': 'postcode_district_uri',
            'POPULATED_PLACE': 'populated_place',
            'POPULATED_PLACE_URI': 'populated_place_uri',
            'POPULATED_PLACE_TYPE': 'populated_place_type',
            'DISTRICT_BOROUGH': 'district_borough',
            'DISTRICT_BOROUGH_URI': 'district_borough_uri',
            'DISTRICT_BOROUGH_TYPE': 'district_borough_type',
            'COUNTY_UNITARY': 'county_unitary',
            'COUNTY_UNITARY_URI': 'county_unitary_uri',
            'COUNTY_UNITARY_TYPE': 'county_unitary_type',
            'REGION': 'region',
            'REGION_URI': 'region_uri',
            'COUNTRY': 'country',
            'COUNTRY_URI': 'country_uri',
            'RELATED_SPATIAL_OBJECT': 'related_spatial_object',
            'SAME_AS_DBPEDIA': 'same_as_dbpedia',
            'SAME_AS_GEONAMES': 'same_as_geonames'
        }
    },
    'lad_boundaries': {
        'priority': 1,
        'description': 'Local Authority District Boundaries',
        'file_pattern': 'LAD_MAY_2025_UK_BFC.shp',
        'format': 'shapefile',
        'coordinate_system': 'osgb',
        'quality_score': 0.98,
        'update_frequency': 'annual',
        'source_type': 'reference',
        'enabled': True,
        'field_mapping': {
            'LAD_CODE': 'lad_code',
            'LAD_NAME': 'lad_name',
            'GEOMETRY': 'geometry',
        }
    },
    'os_open_map_local': {
        'priority': 1,
        'description': 'OS Open Map Local - Map features',
        'file_pattern': 'opmplc_gml3_gb/data/*/*.gml',
        'format': 'gml',
        'coordinate_system': 'osgb',
        'quality_score': 0.95,
        'update_frequency': 'annual',
        'source_type': 'reference',
        'enabled': True,
        'field_mapping': {
            'FEATURE_ID': 'feature_id',
            'FEATURE_TYPE': 'feature_type',
            'THEME': 'theme',
            'GEOMETRY': 'geometry',
        }
    },
}

# Data Quality Rules
DATA_QUALITY_RULES = {
    'coordinate_validation': {
        'latitude_range': (49.0, 61.0),
        'longitude_range': (-8.0, 2.0),
        'severity': 'error'
    },
    'postcode_format': {
        'pattern': r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$',
        'severity': 'warning'
    },
    'rateable_value_range': {
        'min_value': 0,
        'max_value': 100000000,
        'severity': 'error'
    },
    'sale_price_range': {
        'min_value': 0,
        'max_value': 1000000000,
        'severity': 'error'
    },
    'revenue_amount_range': {
        'min_value': 0,
        'max_value': 10000000,
        'severity': 'error'
    }
}

# Duplicate Detection Configuration
DUPLICATE_DETECTION_CONFIG = {
    'criteria': [
        ['ba_reference', 'postcode'],
        ['uprn'],
        ['street_descriptor', 'post_town', 'postcode']
    ],
    'confidence_threshold': 0.8,
    'fuzzy_matching': True,
    'fuzzy_threshold': 0.85
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'batch_size': 10000,
    'chunk_size': 50000,
    'max_workers': 4,
    'memory_limit_gb': 8,
    'temp_file_size_mb': 100,
    'index_disable_during_load': True,
    'parallel_processing': True
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file_handler': True,
    'console_handler': True,
    'log_file': 'comprehensive_ingestion.log',
    'max_file_size_mb': 100,
    'backup_count': 5
}

# Validation Configuration
VALIDATION_CONFIG = {
    'pre_ingestion_validation': True,
    'post_ingestion_validation': True,
    'data_quality_checks': True,
    'duplicate_detection': True,
    'source_tracking': True,
    'performance_monitoring': True
}

def get_enabled_sources() -> Dict[str, Any]:
    """Get only enabled data sources"""
    return {k: v for k, v in ENHANCED_DATA_SOURCES.items() if v.get('enabled', False)}

def get_sources_by_type(source_type: str) -> Dict[str, Any]:
    """Get data sources filtered by type"""
    return {k: v for k, v in ENHANCED_DATA_SOURCES.items() 
            if v.get('source_type') == source_type and v.get('enabled', False)}

def get_priority_sources(priority: int) -> Dict[str, Any]:
    """Get data sources filtered by priority"""
    return {k: v for k, v in ENHANCED_DATA_SOURCES.items() 
            if v.get('priority') == priority and v.get('enabled', False)} 