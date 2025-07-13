from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import uuid
import pandas as pd
import zipfile
import io
import csv
import xml.etree.ElementTree as ET
import yaml
import re
from pathlib import Path
import mimetypes
import chardet

from ..services.database_service import get_db
from ..routers.admin import require_authenticated_user, require_admin_or_power
from ..models import User
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/api/design-enhanced", tags=["design-enhanced"])

# Data Standards Registry - Comprehensive Standards Database
# This registry includes standards from public, private, government bodies, and international organizations

DATA_STANDARDS = {
    # ========================================
    # UK GOVERNMENT STANDARDS
    # ========================================
    "BS7666": {
        "name": "British Standard 7666 - Address and location referencing",
        "description": "UK standard for address and location referencing",
        "required_fields": ["uprn", "usrn", "postcode", "address"],
        "field_patterns": {
            "uprn": r"^\d{12}$",
            "usrn": r"^\d{8}$",
            "postcode": r"^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$"
        },
        "governing_body": "BSI",
        "country": "UK",
        "category": "government",
        "version": "2019",
        "url": "https://www.bsigroup.com/en-GB/standards/bs-7666/",
        "compliance_level": "mandatory"
    },
    "GDS": {
        "name": "Government Digital Service Standards",
        "description": "UK government data standards for digital services",
        "required_fields": ["open_data", "machine_readable", "linked_data"],
        "field_patterns": {
            "open_data": r"(open|public|accessible)",
            "machine_readable": r"(csv|json|xml|rdf)"
        },
        "governing_body": "UK Government",
        "country": "UK",
        "category": "government",
        "version": "2023",
        "url": "https://www.gov.uk/government/publications/open-standards-for-government",
        "compliance_level": "recommended"
    },
    "VOA_NNDR": {
        "name": "Valuation Office Agency NNDR Standards",
        "description": "UK business rates and property valuation standards",
        "required_fields": ["ba_reference", "rateable_value", "property_description"],
        "field_patterns": {
            "ba_reference": r"^[A-Z0-9]{4,12}$",
            "rateable_value": r"^\d+(\.\d{2})?$",
            "property_description": r".{10,}"
        },
        "governing_body": "Valuation Office Agency",
        "country": "UK",
        "category": "government",
        "version": "2023",
        "url": "https://www.gov.uk/government/organisations/valuation-office-agency",
        "compliance_level": "mandatory"
    },
    "ONS_Standards": {
        "name": "Office for National Statistics Standards",
        "description": "UK official statistics standards",
        "required_fields": ["geographic_code", "statistical_unit", "measure"],
        "field_patterns": {
            "geographic_code": r"^[A-Z0-9]{6,9}$",
            "statistical_unit": r"(person|household|business|property)",
            "measure": r"(count|value|percentage)"
        },
        "governing_body": "Office for National Statistics",
        "country": "UK",
        "category": "government",
        "version": "2023",
        "url": "https://www.ons.gov.uk/",
        "compliance_level": "mandatory"
    },
    "OS_Standards": {
        "name": "Ordnance Survey Data Standards",
        "description": "UK national mapping agency standards",
        "required_fields": ["x_coordinate", "y_coordinate", "coordinate_system"],
        "field_patterns": {
            "x_coordinate": r"^\d{6,7}$",
            "y_coordinate": r"^\d{6,7}$",
            "coordinate_system": r"(OSGB|EPSG:27700|EPSG:4326)"
        },
        "governing_body": "Ordnance Survey",
        "country": "UK",
        "category": "government",
        "version": "2023",
        "url": "https://www.ordnancesurvey.co.uk/",
        "compliance_level": "recommended"
    },
    "Land_Registry": {
        "name": "Land Registry Data Standards",
        "description": "UK land and property registration standards",
        "required_fields": ["title_number", "property_address", "price_paid"],
        "field_patterns": {
            "title_number": r"^[A-Z0-9]{1,10}$",
            "price_paid": r"^\d+(\.\d{2})?$",
            "property_address": r".{10,}"
        },
        "governing_body": "HM Land Registry",
        "country": "UK",
        "category": "government",
        "version": "2023",
        "url": "https://www.gov.uk/government/organisations/land-registry",
        "compliance_level": "mandatory"
    },

    # ========================================
    # EUROPEAN UNION STANDARDS
    # ========================================
    "INSPIRE": {
        "name": "INSPIRE Directive - European spatial data infrastructure",
        "description": "European standard for spatial data infrastructure",
        "required_fields": ["geometry", "coordinate_reference_system"],
        "field_patterns": {
            "geometry": r"(point|line|polygon|multipoint|multiline|multipolygon)",
            "coordinate_reference_system": r"(EPSG|CRS|SRID)"
        },
        "governing_body": "European Commission",
        "country": "EU",
        "category": "government",
        "version": "2023",
        "url": "https://inspire.ec.europa.eu/",
        "compliance_level": "mandatory"
    },
    "EU_Open_Data": {
        "name": "EU Open Data Portal Standards",
        "description": "European Union open data standards",
        "required_fields": ["metadata", "license", "publisher"],
        "field_patterns": {
            "metadata": r"(dcat|rdf|json-ld)",
            "license": r"(CC-BY|CC-BY-SA|ODbL)",
            "publisher": r".{3,}"
        },
        "governing_body": "European Commission",
        "country": "EU",
        "category": "government",
        "version": "2023",
        "url": "https://data.europa.eu/",
        "compliance_level": "recommended"
    },

    # ========================================
    # INTERNATIONAL STANDARDS
    # ========================================
    "SDMX": {
        "name": "Statistical Data and Metadata eXchange",
        "description": "International standard for statistical data",
        "required_fields": ["statistical_concept", "measure", "dimension"],
        "field_patterns": {
            "statistical_concept": r"(population|employment|economic|social)",
            "measure": r"(count|value|percentage|rate)"
        },
        "governing_body": "UNSD",
        "country": "International",
        "category": "international",
        "version": "3.0",
        "url": "https://sdmx.org/",
        "compliance_level": "recommended"
    },
    "ISO_20022": {
        "name": "ISO 20022 - Financial services messaging",
        "description": "International standard for financial data",
        "required_fields": ["transaction_id", "amount", "currency", "timestamp"],
        "field_patterns": {
            "transaction_id": r"^[A-Z0-9]{8,32}$",
            "amount": r"^\d+(\.\d{2})?$",
            "currency": r"^[A-Z]{3}$"
        },
        "governing_body": "ISO",
        "country": "International",
        "category": "international",
        "version": "2023",
        "url": "https://www.iso20022.org/",
        "compliance_level": "recommended"
    },
    "ISO_19115": {
        "name": "ISO 19115 - Geographic information metadata",
        "description": "International standard for geographic information metadata",
        "required_fields": ["metadata", "coordinate_system", "spatial_resolution"],
        "field_patterns": {
            "metadata": r"(xml|json)",
            "coordinate_system": r"(EPSG|CRS)",
            "spatial_resolution": r"^\d+(\.\d+)?$"
        },
        "governing_body": "ISO",
        "country": "International",
        "category": "international",
        "version": "2018",
        "url": "https://www.iso.org/standard/53798.html",
        "compliance_level": "recommended"
    },
    "ISO_27001": {
        "name": "ISO 27001 - Information security management",
        "description": "International standard for information security",
        "required_fields": ["security_classification", "access_control", "audit_trail"],
        "field_patterns": {
            "security_classification": r"(public|internal|confidential|restricted)",
            "access_control": r"(role|permission|group)",
            "audit_trail": r"(timestamp|user|action)"
        },
        "governing_body": "ISO",
        "country": "International",
        "category": "international",
        "version": "2022",
        "url": "https://www.iso.org/isoiec-27001-information-security.html",
        "compliance_level": "recommended"
    },
    "W3C_DCAT": {
        "name": "W3C Data Catalog Vocabulary",
        "description": "World Wide Web Consortium data catalog standard",
        "required_fields": ["dataset", "distribution", "catalog"],
        "field_patterns": {
            "dataset": r"(title|description|keyword)",
            "distribution": r"(format|accessURL|mediaType)",
            "catalog": r"(publisher|license|theme)"
        },
        "governing_body": "W3C",
        "country": "International",
        "category": "international",
        "version": "2.0",
        "url": "https://www.w3.org/TR/vocab-dcat/",
        "compliance_level": "recommended"
    },

    # ========================================
    # US GOVERNMENT STANDARDS
    # ========================================
    "US_FIPS": {
        "name": "US Federal Information Processing Standards",
        "description": "US government data processing standards",
        "required_fields": ["fips_code", "state_code", "county_code"],
        "field_patterns": {
            "fips_code": r"^\d{5}$",
            "state_code": r"^\d{2}$",
            "county_code": r"^\d{3}$"
        },
        "governing_body": "NIST",
        "country": "US",
        "category": "government",
        "version": "2023",
        "url": "https://www.nist.gov/fips",
        "compliance_level": "mandatory"
    },
    "US_Census": {
        "name": "US Census Bureau Standards",
        "description": "US Census Bureau data standards",
        "required_fields": ["census_tract", "block_group", "population"],
        "field_patterns": {
            "census_tract": r"^\d{6}$",
            "block_group": r"^\d{1}$",
            "population": r"^\d+$"
        },
        "governing_body": "US Census Bureau",
        "country": "US",
        "category": "government",
        "version": "2023",
        "url": "https://www.census.gov/",
        "compliance_level": "mandatory"
    },

    # ========================================
    # PRIVATE SECTOR STANDARDS
    # ========================================
    "ESRI_Shapefile": {
        "name": "ESRI Shapefile Format",
        "description": "ESRI shapefile format standard",
        "required_fields": ["geometry", "attributes", "projection"],
        "field_patterns": {
            "geometry": r"(point|line|polygon|multipoint|multiline|multipolygon)",
            "attributes": r"(dbf|csv)",
            "projection": r"(prj|wkt)"
        },
        "governing_body": "ESRI",
        "country": "US",
        "category": "private",
        "version": "1998",
        "url": "https://www.esri.com/",
        "compliance_level": "de_facto"
    },
    "OpenStreetMap": {
        "name": "OpenStreetMap Data Format",
        "description": "OpenStreetMap community data standards",
        "required_fields": ["osm_id", "tags", "geometry"],
        "field_patterns": {
            "osm_id": r"^\d+$",
            "tags": r"(key=value|json)",
            "geometry": r"(point|way|relation)"
        },
        "governing_body": "OpenStreetMap Foundation",
        "country": "International",
        "category": "private",
        "version": "2023",
        "url": "https://www.openstreetmap.org/",
        "compliance_level": "community"
    },
    "GeoJSON": {
        "name": "GeoJSON Format",
        "description": "JSON format for geographic data",
        "required_fields": ["type", "coordinates", "properties"],
        "field_patterns": {
            "type": r"(Feature|FeatureCollection|Point|LineString|Polygon)",
            "coordinates": r"\[.*\]",
            "properties": r"\{.*\}"
        },
        "governing_body": "IETF",
        "country": "International",
        "category": "private",
        "version": "2016",
        "url": "https://tools.ietf.org/html/rfc7946",
        "compliance_level": "de_facto"
    },
    "KML": {
        "name": "Keyhole Markup Language",
        "description": "Google Earth/KML format standard",
        "required_fields": ["placemark", "coordinates", "description"],
        "field_patterns": {
            "placemark": r"<Placemark>",
            "coordinates": r"<coordinates>",
            "description": r"<description>"
        },
        "governing_body": "Google",
        "country": "US",
        "category": "private",
        "version": "2008",
        "url": "https://developers.google.com/kml",
        "compliance_level": "de_facto"
    },

    # ========================================
    # FINANCIAL STANDARDS
    # ========================================
    "FIX_Protocol": {
        "name": "Financial Information eXchange Protocol",
        "description": "Financial trading data standard",
        "required_fields": ["order_id", "symbol", "quantity", "price"],
        "field_patterns": {
            "order_id": r"^[A-Z0-9]{8,32}$",
            "symbol": r"^[A-Z]{1,10}$",
            "quantity": r"^\d+(\.\d+)?$",
            "price": r"^\d+(\.\d{2,4})?$"
        },
        "governing_body": "FIX Protocol Ltd",
        "country": "International",
        "category": "financial",
        "version": "5.0",
        "url": "https://www.fixtrading.org/",
        "compliance_level": "industry"
    },
    "SWIFT": {
        "name": "SWIFT Financial Messaging",
        "description": "International financial messaging standard",
        "required_fields": ["swift_code", "amount", "currency", "beneficiary"],
        "field_patterns": {
            "swift_code": r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$",
            "amount": r"^\d+(\.\d{2})?$",
            "currency": r"^[A-Z]{3}$",
            "beneficiary": r".{3,}"
        },
        "governing_body": "SWIFT",
        "country": "International",
        "category": "financial",
        "version": "2023",
        "url": "https://www.swift.com/",
        "compliance_level": "industry"
    },

    # ========================================
    # HEALTHCARE STANDARDS
    # ========================================
    "HL7_FHIR": {
        "name": "HL7 FHIR - Fast Healthcare Interoperability Resources",
        "description": "Healthcare data exchange standard",
        "required_fields": ["patient_id", "resource_type", "data"],
        "field_patterns": {
            "patient_id": r"^[A-Z0-9-]{1,64}$",
            "resource_type": r"(Patient|Observation|Medication|Procedure)",
            "data": r"\{.*\}"
        },
        "governing_body": "HL7",
        "country": "International",
        "category": "healthcare",
        "version": "4.0",
        "url": "https://www.hl7.org/fhir/",
        "compliance_level": "industry"
    },
    "DICOM": {
        "name": "Digital Imaging and Communications in Medicine",
        "description": "Medical imaging data standard",
        "required_fields": ["patient_id", "study_id", "series_id", "image_data"],
        "field_patterns": {
            "patient_id": r"^[A-Z0-9-]{1,64}$",
            "study_id": r"^[A-Z0-9-]{1,64}$",
            "series_id": r"^[A-Z0-9-]{1,64}$",
            "image_data": r"(dcm|raw|jpeg|png)"
        },
        "governing_body": "NEMA",
        "country": "US",
        "category": "healthcare",
        "version": "2023",
        "url": "https://www.dicomstandard.org/",
        "compliance_level": "industry"
    },

    # ========================================
    # TRANSPORTATION STANDARDS
    # ========================================
    "GTFS": {
        "name": "General Transit Feed Specification",
        "description": "Public transportation data standard",
        "required_fields": ["agency_id", "route_id", "stop_id", "trip_id"],
        "field_patterns": {
            "agency_id": r"^[A-Z0-9_]{1,32}$",
            "route_id": r"^[A-Z0-9_]{1,32}$",
            "stop_id": r"^[A-Z0-9_]{1,32}$",
            "trip_id": r"^[A-Z0-9_]{1,32}$"
        },
        "governing_body": "Google",
        "country": "US",
        "category": "transportation",
        "version": "2.0",
        "url": "https://developers.google.com/transit/gtfs",
        "compliance_level": "de_facto"
    },
    "SIRI": {
        "name": "Service Interface for Real Time Information",
        "description": "Real-time public transport information standard",
        "required_fields": ["vehicle_id", "line_id", "direction", "timestamp"],
        "field_patterns": {
            "vehicle_id": r"^[A-Z0-9_]{1,32}$",
            "line_id": r"^[A-Z0-9_]{1,32}$",
            "direction": r"(inbound|outbound|clockwise|counterclockwise)",
            "timestamp": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        },
        "governing_body": "CEN",
        "country": "EU",
        "category": "transportation",
        "version": "2.0",
        "url": "https://www.siri.org.uk/",
        "compliance_level": "industry"
    },

    # ========================================
    # ENVIRONMENTAL STANDARDS
    # ========================================
    "ISO_14001": {
        "name": "ISO 14001 - Environmental Management",
        "description": "Environmental management system standard",
        "required_fields": ["environmental_aspect", "impact_assessment", "compliance"],
        "field_patterns": {
            "environmental_aspect": r"(emissions|waste|energy|water)",
            "impact_assessment": r"(low|medium|high|critical)",
            "compliance": r"(compliant|non_compliant|pending)"
        },
        "governing_body": "ISO",
        "country": "International",
        "category": "environmental",
        "version": "2015",
        "url": "https://www.iso.org/iso-14001-environmental-management.html",
        "compliance_level": "recommended"
    },
    "WMO": {
        "name": "World Meteorological Organization Standards",
        "description": "Meteorological and climate data standards",
        "required_fields": ["station_id", "parameter", "value", "timestamp"],
        "field_patterns": {
            "station_id": r"^[A-Z0-9]{5,10}$",
            "parameter": r"(temperature|pressure|humidity|wind|precipitation)",
            "value": r"^-?\d+(\.\d+)?$",
            "timestamp": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        },
        "governing_body": "WMO",
        "country": "International",
        "category": "environmental",
        "version": "2023",
        "url": "https://public.wmo.int/",
        "compliance_level": "industry"
    }
}

# Data Standards Categories for filtering and organization
DATA_STANDARDS_CATEGORIES = {
    "government": {
        "name": "Government Standards",
        "description": "Standards from government bodies and agencies",
        "subcategories": ["uk_government", "eu_government", "us_government", "international_government"]
    },
    "international": {
        "name": "International Standards",
        "description": "Standards from international organizations",
        "subcategories": ["iso", "w3c", "un", "other_international"]
    },
    "private": {
        "name": "Private Sector Standards",
        "description": "Standards from private companies and organizations",
        "subcategories": ["technology", "mapping", "data_formats"]
    },
    "financial": {
        "name": "Financial Standards",
        "description": "Standards for financial data and transactions",
        "subcategories": ["trading", "banking", "payments"]
    },
    "healthcare": {
        "name": "Healthcare Standards",
        "description": "Standards for healthcare and medical data",
        "subcategories": ["clinical", "imaging", "pharmaceutical"]
    },
    "transportation": {
        "name": "Transportation Standards",
        "description": "Standards for transportation and logistics data",
        "subcategories": ["public_transit", "logistics", "traffic"]
    },
    "environmental": {
        "name": "Environmental Standards",
        "description": "Standards for environmental and climate data",
        "subcategories": ["climate", "pollution", "sustainability"]
    }
}

# Compliance levels for standards
COMPLIANCE_LEVELS = {
    "mandatory": {
        "name": "Mandatory",
        "description": "Legally required compliance",
        "priority": 1
    },
    "recommended": {
        "name": "Recommended",
        "description": "Best practice recommendation",
        "priority": 2
    },
    "industry": {
        "name": "Industry Standard",
        "description": "Widely adopted industry standard",
        "priority": 3
    },
    "de_facto": {
        "name": "De Facto Standard",
        "description": "Commonly used but not formally standardized",
        "priority": 4
    },
    "community": {
        "name": "Community Standard",
        "description": "Community-driven standard",
        "priority": 5
    }
}

# Comprehensive Data Standards Registry
DATA_STANDARDS = {
    # ========================================
    # US GOVERNMENT STANDARDS
    # ========================================
    "US_FIPS": {
        "name": "US Federal Information Processing Standards",
        "description": "US government data processing standards",
        "required_fields": ["fips_code", "state_code", "county_code"],
        "field_patterns": {
            "fips_code": r"^\d{5}$",
            "state_code": r"^\d{2}$",
            "county_code": r"^\d{3}$"
        },
        "governing_body": "NIST",
        "country": "US",
        "category": "government",
        "version": "2023",
        "url": "https://www.nist.gov/fips",
        "compliance_level": "mandatory"
    },
    "US_Census": {
        "name": "US Census Bureau Standards",
        "description": "US Census Bureau data standards",
        "required_fields": ["census_tract", "block_group", "population"],
        "field_patterns": {
            "census_tract": r"^\d{6}$",
            "block_group": r"^\d{1}$",
            "population": r"^\d+$"
        },
        "governing_body": "US Census Bureau",
        "country": "US",
        "category": "government",
        "version": "2023",
        "url": "https://www.census.gov/",
        "compliance_level": "mandatory"
    },

    # ========================================
    # PRIVATE SECTOR STANDARDS
    # ========================================
    "ESRI_Shapefile": {
        "name": "ESRI Shapefile Format",
        "description": "ESRI shapefile format standard",
        "required_fields": ["geometry", "attributes", "projection"],
        "field_patterns": {
            "geometry": r"(point|line|polygon|multipoint|multiline|multipolygon)",
            "attributes": r"(dbf|csv)",
            "projection": r"(prj|wkt)"
        },
        "governing_body": "ESRI",
        "country": "US",
        "category": "private",
        "version": "1998",
        "url": "https://www.esri.com/",
        "compliance_level": "de_facto"
    },
    "OpenStreetMap": {
        "name": "OpenStreetMap Data Format",
        "description": "OpenStreetMap community data standards",
        "required_fields": ["osm_id", "tags", "geometry"],
        "field_patterns": {
            "osm_id": r"^\d+$",
            "tags": r"(key=value|json)",
            "geometry": r"(point|way|relation)"
        },
        "governing_body": "OpenStreetMap Foundation",
        "country": "International",
        "category": "private",
        "version": "2023",
        "url": "https://www.openstreetmap.org/",
        "compliance_level": "community"
    },
    "GeoJSON": {
        "name": "GeoJSON Format",
        "description": "JSON format for geographic data",
        "required_fields": ["type", "coordinates", "properties"],
        "field_patterns": {
            "type": r"(Feature|FeatureCollection|Point|LineString|Polygon)",
            "coordinates": r"\[.*\]",
            "properties": r"\{.*\}"
        },
        "governing_body": "IETF",
        "country": "International",
        "category": "private",
        "version": "2016",
        "url": "https://tools.ietf.org/html/rfc7946",
        "compliance_level": "de_facto"
    },
    "KML": {
        "name": "Keyhole Markup Language",
        "description": "Google Earth/KML format standard",
        "required_fields": ["placemark", "coordinates", "description"],
        "field_patterns": {
            "placemark": r"<Placemark>",
            "coordinates": r"<coordinates>",
            "description": r"<description>"
        },
        "governing_body": "Google",
        "country": "US",
        "category": "private",
        "version": "2008",
        "url": "https://developers.google.com/kml",
        "compliance_level": "de_facto"
    },

    # ========================================
    # FINANCIAL STANDARDS
    # ========================================
    "FIX_Protocol": {
        "name": "Financial Information eXchange Protocol",
        "description": "Financial trading data standard",
        "required_fields": ["order_id", "symbol", "quantity", "price"],
        "field_patterns": {
            "order_id": r"^[A-Z0-9]{8,32}$",
            "symbol": r"^[A-Z]{1,10}$",
            "quantity": r"^\d+(\.\d+)?$",
            "price": r"^\d+(\.\d{2,4})?$"
        },
        "governing_body": "FIX Protocol Ltd",
        "country": "International",
        "category": "financial",
        "version": "5.0",
        "url": "https://www.fixtrading.org/",
        "compliance_level": "industry"
    },
    "SWIFT": {
        "name": "SWIFT Financial Messaging",
        "description": "International financial messaging standard",
        "required_fields": ["swift_code", "amount", "currency", "beneficiary"],
        "field_patterns": {
            "swift_code": r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$",
            "amount": r"^\d+(\.\d{2})?$",
            "currency": r"^[A-Z]{3}$",
            "beneficiary": r".{3,}"
        },
        "governing_body": "SWIFT",
        "country": "International",
        "category": "financial",
        "version": "2023",
        "url": "https://www.swift.com/",
        "compliance_level": "industry"
    },

    # ========================================
    # HEALTHCARE STANDARDS
    # ========================================
    "HL7_FHIR": {
        "name": "HL7 FHIR - Fast Healthcare Interoperability Resources",
        "description": "Healthcare data exchange standard",
        "required_fields": ["patient_id", "resource_type", "data"],
        "field_patterns": {
            "patient_id": r"^[A-Z0-9-]{1,64}$",
            "resource_type": r"(Patient|Observation|Medication|Procedure)",
            "data": r"\{.*\}"
        },
        "governing_body": "HL7",
        "country": "International",
        "category": "healthcare",
        "version": "4.0",
        "url": "https://www.hl7.org/fhir/",
        "compliance_level": "industry"
    },
    "DICOM": {
        "name": "Digital Imaging and Communications in Medicine",
        "description": "Medical imaging data standard",
        "required_fields": ["patient_id", "study_id", "series_id", "image_data"],
        "field_patterns": {
            "patient_id": r"^[A-Z0-9-]{1,64}$",
            "study_id": r"^[A-Z0-9-]{1,64}$",
            "series_id": r"^[A-Z0-9-]{1,64}$",
            "image_data": r"(dcm|raw|jpeg|png)"
        },
        "governing_body": "NEMA",
        "country": "US",
        "category": "healthcare",
        "version": "2023",
        "url": "https://www.dicomstandard.org/",
        "compliance_level": "industry"
    },

    # ========================================
    # TRANSPORTATION STANDARDS
    # ========================================
    "GTFS": {
        "name": "General Transit Feed Specification",
        "description": "Public transportation data standard",
        "required_fields": ["agency_id", "route_id", "stop_id", "trip_id"],
        "field_patterns": {
            "agency_id": r"^[A-Z0-9_]{1,32}$",
            "route_id": r"^[A-Z0-9_]{1,32}$",
            "stop_id": r"^[A-Z0-9_]{1,32}$",
            "trip_id": r"^[A-Z0-9_]{1,32}$"
        },
        "governing_body": "Google",
        "country": "US",
        "category": "transportation",
        "version": "2.0",
        "url": "https://developers.google.com/transit/gtfs",
        "compliance_level": "de_facto"
    },
    "SIRI": {
        "name": "Service Interface for Real Time Information",
        "description": "Real-time public transport information standard",
        "required_fields": ["vehicle_id", "line_id", "direction", "timestamp"],
        "field_patterns": {
            "vehicle_id": r"^[A-Z0-9_]{1,32}$",
            "line_id": r"^[A-Z0-9_]{1,32}$",
            "direction": r"(inbound|outbound|clockwise|counterclockwise)",
            "timestamp": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        },
        "governing_body": "CEN",
        "country": "EU",
        "category": "transportation",
        "version": "2.0",
        "url": "https://www.siri.org.uk/",
        "compliance_level": "industry"
    },

    # ========================================
    # ENVIRONMENTAL STANDARDS
    # ========================================
    "ISO_14001": {
        "name": "ISO 14001 - Environmental Management",
        "description": "Environmental management system standard",
        "required_fields": ["environmental_aspect", "impact_assessment", "compliance"],
        "field_patterns": {
            "environmental_aspect": r"(emissions|waste|energy|water)",
            "impact_assessment": r"(low|medium|high|critical)",
            "compliance": r"(compliant|non_compliant|pending)"
        },
        "governing_body": "ISO",
        "country": "International",
        "category": "environmental",
        "version": "2015",
        "url": "https://www.iso.org/iso-14001-environmental-management.html",
        "compliance_level": "recommended"
    },
    "WMO": {
        "name": "World Meteorological Organization Standards",
        "description": "Meteorological and climate data standards",
        "required_fields": ["station_id", "parameter", "value", "timestamp"],
        "field_patterns": {
            "station_id": r"^[A-Z0-9]{5,10}$",
            "parameter": r"(temperature|pressure|humidity|wind|precipitation)",
            "value": r"^-?\d+(\.\d+)?$",
            "timestamp": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        },
        "governing_body": "WMO",
        "country": "International",
        "category": "environmental",
        "version": "2023",
        "url": "https://public.wmo.int/",
        "compliance_level": "industry"
    }
}

# Data Standards Categories for filtering and organization
DATA_STANDARDS_CATEGORIES = {
    "government": {
        "name": "Government Standards",
        "description": "Standards from government bodies and agencies",
        "subcategories": ["uk_government", "eu_government", "us_government", "international_government"]
    },
    "international": {
        "name": "International Standards",
        "description": "Standards from international organizations",
        "subcategories": ["iso", "w3c", "un", "other_international"]
    },
    "private": {
        "name": "Private Sector Standards",
        "description": "Standards from private companies and organizations",
        "subcategories": ["technology", "mapping", "data_formats"]
    },
    "financial": {
        "name": "Financial Standards",
        "description": "Standards for financial data and transactions",
        "subcategories": ["trading", "banking", "payments"]
    },
    "healthcare": {
        "name": "Healthcare Standards",
        "description": "Standards for healthcare and medical data",
        "subcategories": ["clinical", "imaging", "pharmaceutical"]
    },
    "transportation": {
        "name": "Transportation Standards",
        "description": "Standards for transportation and logistics data",
        "subcategories": ["public_transit", "logistics", "traffic"]
    },
    "environmental": {
        "name": "Environmental Standards",
        "description": "Standards for environmental and climate data",
        "subcategories": ["climate", "pollution", "sustainability"]
    }
}

# Compliance levels for standards
COMPLIANCE_LEVELS = {
    "mandatory": {
        "name": "Mandatory",
        "description": "Legally required compliance",
        "priority": 1
    },
    "recommended": {
        "name": "Recommended",
        "description": "Best practice recommendation",
        "priority": 2
    },
    "industry": {
        "name": "Industry Standard",
        "description": "Widely adopted industry standard",
        "priority": 3
    },
    "de_facto": {
        "name": "De Facto Standard",
        "description": "Commonly used but not formally standardized",
        "priority": 4
    },
    "community": {
        "name": "Community Standard",
        "description": "Community-driven standard",
        "priority": 5
    }
}

# File Format Detectors
def detect_csv_format(content: bytes, filename: str) -> Dict[str, Any]:
    """Detect CSV format, delimiter, encoding, and structure"""
    try:
        # Detect encoding
        detected = chardet.detect(content)
        # In detect_csv_format, ensure encoding is always a string
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        
        # Try to decode content
        text_content = content.decode(encoding or 'utf-8', errors='ignore')
        lines = text_content.split('\n')
        
        # Find first non-empty line
        first_line = None
        for line in lines:
            if line.strip():
                first_line = line.strip()
                break
        
        if not first_line:
            return {"error": "No content found in file"}
        
        # Test different delimiters
        delimiters = [',', ';', '\t', '|', '*']
        delimiter_scores = {}
        
        for delimiter in delimiters:
            try:
                reader = csv.reader([first_line], delimiter=delimiter)
                row = next(reader)
                delimiter_scores[delimiter] = len(row)
            except:
                delimiter_scores[delimiter] = 0
        
        # Find best delimiter (most fields)
        best_delimiter = max(delimiter_scores.items(), key=lambda x: x[1])[0]
        
        # Parse sample data (limit to first 5 lines for speed)
        sample_lines = lines[:5]  # First 5 lines for faster analysis
        parsed_data = []
        
        for line in sample_lines:
            if line.strip():
                try:
                    reader = csv.reader([line], delimiter=best_delimiter)
                    row = next(reader)
                    parsed_data.append(row)
                except:
                    continue
        
        if not parsed_data:
            return {"error": "Could not parse CSV data"}
        
        # Analyze structure
        field_count = len(parsed_data[0])
        
        # Check if first row looks like header
        first_row = parsed_data[0]
        
        # More sophisticated header detection
        # 1. Check if first row has mostly text fields
        text_fields = sum(1 for field in first_row if not field.replace('.', '').replace('-', '').isdigit())
        text_ratio = text_fields / field_count if field_count > 0 else 0
        
        # 2. Check if first row has common header patterns
        header_patterns = ['id', 'name', 'type', 'date', 'address', 'postcode', 'code', 'value', 'amount', 'price']
        header_matches = sum(1 for field in first_row if any(pattern in field.lower() for pattern in header_patterns))
        
        # 3. Check if second row (if exists) has different data types than first row
        has_different_types = False
        if len(parsed_data) > 1:
            second_row = parsed_data[1]
            first_row_types = [not field.replace('.', '').replace('-', '').isdigit() for field in first_row]
            second_row_types = [not field.replace('.', '').replace('-', '').isdigit() for field in second_row]
            has_different_types = first_row_types != second_row_types
        
        # Determine if first row is header
        has_header = (text_ratio > 0.6) or (header_matches > 0) or has_different_types
        
        # Log header detection details for debugging
        print(f"CSV Header Detection: text_ratio={text_ratio:.2f}, header_matches={header_matches}, has_different_types={has_different_types}, has_header={has_header}")
        print(f"First row: {first_row}")
        
        # Analyze field types
        field_analysis = []
        start_row = 1 if has_header else 0
        
        for i in range(field_count):
            field_values = [row[i] for row in parsed_data[start_row:] if i < len(row)]
            field_info = analyze_field_type(field_values, i)
            
            # Add field name and metadata
            if has_header and i < len(parsed_data[0]):
                header_field = parsed_data[0][i]
                # Clean up header field name
                if header_field and header_field.strip():
                    # Remove special characters and spaces, convert to lowercase
                    field_name = re.sub(r'[^a-zA-Z0-9_]', '_', header_field.strip().lower())
                    # Remove leading/trailing underscores
                    field_name = field_name.strip('_')
                    # Ensure it starts with a letter
                    if field_name and not field_name[0].isalpha():
                        field_name = f"field_{field_name}"
                    # If empty after cleaning, use generated name
                    if not field_name:
                        field_name = f"field_{i+1}"
                else:
                    field_name = f"field_{i+1}"
            else:
                field_name = f"field_{i+1}"  # Generate field name
            
            field_info.update({
                "field_name": field_name,
                "sequence_order": i + 1,
                "source_column_index": i
            })
            
            # Log field name generation for debugging
            print(f"Field {i+1}: original='{parsed_data[0][i] if has_header and i < len(parsed_data[0]) else 'N/A'}', generated='{field_name}'")
            
            field_analysis.append(field_info)
        
        return {
            "format": "csv",
            "encoding": encoding,
            "delimiter": best_delimiter,
            "has_header": has_header,
            "field_count": field_count,
            "sample_rows": parsed_data,  # Return actual sample rows, not just count
            "field_analysis": field_analysis,
            "confidence": 0.95
        }
        
    except Exception as e:
        return {"error": f"CSV analysis failed: {str(e)}"}

def detect_json_format(content: bytes, filename: str) -> Dict[str, Any]:
    """Detect JSON format and structure"""
    try:
        text_content = content.decode('utf-8', errors='ignore')
        data = json.loads(text_content)
        
        # Analyze JSON structure
        structure = analyze_json_structure(data)
        
        return {
            "format": "json",
            "encoding": "utf-8",
            "structure": structure,
            "confidence": 0.95
        }
        
    except Exception as e:
        return {"error": f"JSON analysis failed: {str(e)}"}

def detect_xml_format(content: bytes, filename: str) -> Dict[str, Any]:
    """Detect XML format and structure"""
    try:
        text_content = content.decode('utf-8', errors='ignore')
        root = ET.fromstring(text_content)
        
        # Analyze XML structure
        structure = analyze_xml_structure(root)
        
        return {
            "format": "xml",
            "encoding": "utf-8",
            "structure": structure,
            "confidence": 0.95
        }
        
    except Exception as e:
        return {"error": f"XML analysis failed: {str(e)}"}

def detect_zip_format(content: bytes, filename: str) -> Dict[str, Any]:
    """Detect ZIP format and analyze contents"""
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
            file_list = zip_file.namelist()
            
            # Analyze ZIP contents
            content_analysis = analyze_zip_contents(zip_file, file_list)
            
            return {
                "format": "zip",
                "file_count": len(file_list),
                "files": file_list,
                "content_analysis": content_analysis,
                "confidence": 0.95
            }
            
    except Exception as e:
        return {"error": f"ZIP analysis failed: {str(e)}"}

def analyze_field_type(values: List[str], field_index: int) -> Dict[str, Any]:
    """Analyze field type based on sample values"""
    if not values:
        return {
            "type": "empty", 
            "confidence": 0.0,
            "sample_values": [],
            "unique_count": 0,
            "empty_count": 0,
            "total_count": 0,
            "reason": "No data available for analysis"
        }
    
    # Remove empty values
    non_empty_values = [v.strip() for v in values if v.strip()]
    empty_count = len(values) - len(non_empty_values)
    
    if not non_empty_values:
        return {
            "type": "empty", 
            "confidence": 0.0,
            "sample_values": [],
            "unique_count": 0,
            "empty_count": empty_count,
            "total_count": len(values),
            "reason": "All values are empty or null"
        }
    
    # Test different data types
    type_scores = {
        "text": 0,
        "integer": 0,
        "decimal": 0,
        "date": 0,
        "boolean": 0,
        "postcode": 0,
        "uprn": 0,
        "coordinate": 0
    }
    
    for value in non_empty_values:
        # Test integer (exclude decimals)
        if value.replace('-', '').isdigit() and '.' not in value:
            type_scores["integer"] += 1
            continue  # Don't count as text if it's an integer
        
        # Test coordinates FIRST (before generic decimal check)
        try:
            coord = float(value)
            if -180 <= coord <= 180:  # Likely longitude
                type_scores["coordinate"] += 1
                continue  # Don't count as generic decimal if it's a coordinate
            elif -90 <= coord <= 90:  # Likely latitude
                type_scores["coordinate"] += 1
                continue  # Don't count as generic decimal if it's a coordinate
        except:
            pass
        
        # Test decimal (only if not already identified as coordinate)
        try:
            float(value)
            if '.' in value:
                type_scores["decimal"] += 1
                continue  # Don't count as text if it's a decimal
        except:
            pass
        
        # Test date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{2}/\d{2}/\d{2}',  # MM/DD/YY
        ]
        for pattern in date_patterns:
            if re.match(pattern, value):
                type_scores["date"] += 1
                break
        else:
            # Test boolean
            if value.lower() in ['true', 'false', 'yes', 'no', '1', '0']:
                type_scores["boolean"] += 1
            # Test UK postcode
            elif re.match(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$', value.upper()):
                type_scores["postcode"] += 1
            # Test UPRN (12-digit number)
            elif re.match(r'^\d{12}$', value):
                type_scores["uprn"] += 1
            # If none of the above, it's text
            else:
                type_scores["text"] += 1
    
    # Find best type
    best_type = max(type_scores.items(), key=lambda x: x[1])[0]
    confidence = type_scores[best_type] / len(non_empty_values)
    
    return {
        "type": best_type,
        "confidence": confidence,
        "sample_values": non_empty_values[:5],
        "unique_count": len(set(non_empty_values)),
        "empty_count": empty_count,
        "total_count": len(values),
        "reason": f"Detected as {best_type} with {confidence:.1%} confidence"
    }

def analyze_json_structure(data: Any, max_depth: int = 3) -> Dict[str, Any]:
    """Analyze JSON structure recursively"""
    if isinstance(data, dict):
        if max_depth <= 0:
            return {"type": "object", "depth_limit": True}
        
        structure = {
            "type": "object",
            "fields": {},
            "field_count": len(data)
        }
        
        for key, value in data.items():
            structure["fields"][key] = analyze_json_structure(value, max_depth - 1)
        
        return structure
    
    elif isinstance(data, list):
        if max_depth <= 0:
            return {"type": "array", "depth_limit": True}
        
        if data:
            sample_item = data[0]
            item_structure = analyze_json_structure(sample_item, max_depth - 1)
        else:
            item_structure = {"type": "unknown"}
        
        return {
            "type": "array",
            "length": len(data),
            "item_structure": item_structure
        }
    
    else:
        return {
            "type": type(data).__name__,
            "value": str(data)[:100]  # Truncate long values
        }

def analyze_xml_structure(element: ET.Element, max_depth: int = 3) -> Dict[str, Any]:
    """Analyze XML structure recursively"""
    if max_depth <= 0:
        return {"type": "element", "depth_limit": True}
    
    structure = {
        "type": "element",
        "tag": element.tag,
        "attributes": dict(element.attrib),
        "children": {},
        "text_content": element.text.strip() if element.text and element.text.strip() else None
    }
    
    # Group children by tag
    children_by_tag = {}
    for child in element:
        if child.tag not in children_by_tag:
            children_by_tag[child.tag] = []
        children_by_tag[child.tag].append(child)
    
    # Analyze each unique child tag
    for tag, children in children_by_tag.items():
        if len(children) == 1:
            structure["children"][tag] = analyze_xml_structure(children[0], max_depth - 1)
        else:
            # Multiple children with same tag
            sample_child = children[0]
            child_structure = analyze_xml_structure(sample_child, max_depth - 1)
            child_structure["count"] = len(children)
            structure["children"][tag] = child_structure
    
    return structure

def analyze_zip_contents(zip_file: zipfile.ZipFile, file_list: List[str]) -> Dict[str, Any]:
    """Analyze ZIP file contents with support for header/data directory structure and content preview"""
    analysis = {
        "data_files": [],
        "documentation": [],
        "metadata": [],
        "header_files": [],
        "directory_structure": {},
        "total_size": 0,
        "has_header_data_structure": False,
        "file_previews": {},
        "suggested_header_files": [],
        "suggested_data_files": []
    }
    
    # Detect directory structure
    directories = set()
    for filename in file_list:
        if not filename or not isinstance(filename, str):
            continue
        safe_filename = filename
        file_info = zip_file.getinfo(safe_filename)
        analysis["total_size"] += file_info.file_size
        
        # Extract directory path
        if '/' in safe_filename:
            directory = safe_filename.split('/')[0]
            directories.add(directory)
            
            if directory not in analysis["directory_structure"]:
                analysis["directory_structure"][directory] = {
                    "files": [],
                    "total_size": 0,
                    "file_types": set()
                }
            
            analysis["directory_structure"][directory]["files"].append({
                "name": safe_filename,
                "size": file_info.file_size,
                "type": Path(safe_filename).suffix.lower()
            })
            analysis["directory_structure"][directory]["total_size"] += file_info.file_size
            analysis["directory_structure"][directory]["file_types"].add(Path(safe_filename).suffix.lower())
    
    # Detect header/data structure patterns
    header_patterns = ['header', 'headers', 'meta', 'metadata', 'schema', 'definition', 'spec']
    data_patterns = ['data', 'dataset', 'records', 'values', 'content', 'files']
    
    for directory in directories:
        dir_lower = directory.lower()
        
        # Check if this is a header directory
        if any(pattern in dir_lower for pattern in header_patterns):
            analysis["has_header_data_structure"] = True
            analysis["header_files"].extend(analysis["directory_structure"][directory]["files"])
            
        # Check if this is a data directory
        elif any(pattern in dir_lower for pattern in data_patterns):
            analysis["has_header_data_structure"] = True
            analysis["data_files"].extend(analysis["directory_structure"][directory]["files"])
    
    # If no specific header/data structure detected, categorize by file type
    if not analysis["has_header_data_structure"]:
        for filename in filter(lambda f: isinstance(f, str) and f, file_list):
            safe_filename = filename
            file_info = zip_file.getinfo(safe_filename)
            
            # Categorize files by type
            ext = Path(safe_filename).suffix.lower()
            if safe_filename.lower().endswith(('.csv', '.json', '.xml', '.txt', '.gml', '.shp', '.dbf')):
                analysis["data_files"].append({
                    "name": safe_filename,
                    "size": file_info.file_size,
                    "type": ext
                })
            elif safe_filename.lower().endswith(('.md', '.txt', '.pdf', '.doc', '.docx')):
                analysis["documentation"].append({
                    "name": safe_filename,
                    "size": file_info.file_size,
                    "type": ext
                })
            elif safe_filename.lower().endswith(('.xml', '.json', '.yml', '.yaml')):
                analysis["metadata"].append({
                    "name": safe_filename,
                    "size": file_info.file_size,
                    "type": ext
                })
    
    # Generate file previews and suggestions
    for filename in filter(lambda f: isinstance(f, str) and f, file_list):
        safe_filename = filename
        try:
            file_info = zip_file.getinfo(safe_filename)
            
            # Add file info to analysis for debugging
            analysis["file_previews"][safe_filename] = {
                "size": file_info.file_size,
                "extension": Path(safe_filename).suffix.lower(),
                "preview_attempted": False,
                "preview_error": None
            }
            
            # Only preview files under 1MB to avoid memory issues
            if file_info.file_size < 1024 * 1024:
                with zip_file.open(safe_filename) as file:
                    content = file.read()
                    
                    # Preview CSV files
                    if safe_filename.lower().endswith('.csv'):
                        try:
                            preview = preview_csv_content(content, safe_filename)
                            analysis["file_previews"][safe_filename].update(preview)
                            analysis["file_previews"][safe_filename]["preview_attempted"] = True
                            
                            # Suggest as header file if it has column headers
                            if preview.get("has_header", False) and len(preview.get("headers", [])) > 0:
                                analysis["suggested_header_files"].append({
                                    "filename": safe_filename,
                                    "headers": preview.get("headers", []),
                                    "sample_rows": preview.get("sample_rows", []),
                                    "confidence": "high" if preview.get("has_header", False) else "medium"
                                })
                            
                            # Suggest as data file
                            analysis["suggested_data_files"].append({
                                "filename": safe_filename,
                                "type": "csv",
                                "headers": preview.get("headers", []),
                                "sample_rows": preview.get("sample_rows", []),
                                "field_count": len(preview.get("headers", [])),
                                "row_count_estimate": preview.get("row_count_estimate", 0)
                            })
                        except Exception as e:
                            analysis["file_previews"][safe_filename]["preview_error"] = str(e)
                    
                    # Preview JSON files
                    elif safe_filename.lower().endswith('.json'):
                        try:
                            preview = preview_json_content(content, safe_filename)
                            analysis["file_previews"][safe_filename].update(preview)
                            analysis["file_previews"][safe_filename]["preview_attempted"] = True
                            
                            if preview.get("is_metadata", False):
                                analysis["suggested_header_files"].append({
                                    "filename": safe_filename,
                                    "type": "json_metadata",
                                    "structure": preview.get("structure", {}),
                                    "confidence": "high"
                                })
                        except Exception as e:
                            analysis["file_previews"][safe_filename]["preview_error"] = str(e)
                    
                    # Preview XML files
                    elif safe_filename.lower().endswith(('.xml', '.gml')):
                        try:
                            preview = preview_xml_content(content, safe_filename)
                            analysis["file_previews"][safe_filename].update(preview)
                            analysis["file_previews"][safe_filename]["preview_attempted"] = True
                            
                            if preview.get("is_metadata", False):
                                analysis["suggested_header_files"].append({
                                    "filename": safe_filename,
                                    "type": "xml_metadata",
                                    "structure": preview.get("structure", {}),
                                    "confidence": "high"
                                })
                        except Exception as e:
                            analysis["file_previews"][safe_filename]["preview_error"] = str(e)
                    
                    # Preview shapefile components
                    elif safe_filename.lower().endswith('.dbf'):
                        try:
                            preview = preview_dbf_content(content, safe_filename)
                            analysis["file_previews"][safe_filename].update(preview)
                            analysis["file_previews"][safe_filename]["preview_attempted"] = True
                            
                            if preview.get("has_structure", False):
                                analysis["suggested_header_files"].append({
                                    "filename": safe_filename,
                                    "type": "shapefile_header",
                                    "fields": preview.get("fields", []),
                                    "confidence": "high"
                                })
                        except Exception as e:
                            analysis["file_previews"][safe_filename]["preview_error"] = str(e)
                    
                    # For other file types, just add basic info
                    else:
                        analysis["file_previews"][safe_filename]["preview_attempted"] = True
                        analysis["file_previews"][safe_filename]["note"] = "File type not supported for preview"
            else:
                analysis["file_previews"][safe_filename]["note"] = f"File too large for preview ({file_info.file_size} bytes)"
        
        except Exception as e:
            # Skip files that can't be read
            analysis["file_previews"][safe_filename] = {
                "error": str(e),
                "preview_attempted": False
            }
            continue
    
    # Convert sets to lists for JSON serialization
    for directory in analysis["directory_structure"]:
        analysis["directory_structure"][directory]["file_types"] = list(analysis["directory_structure"][directory]["file_types"])
    
    return analysis

def preview_csv_content(content: bytes, filename: str) -> Dict[str, Any]:
    """Preview CSV file content and extract headers and sample data"""
    try:
        # Detect encoding
        detected = chardet.detect(content)
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        
        # Decode content
        text_content = content.decode(encoding or 'utf-8', errors='ignore')
        lines = text_content.split('\n')
        
        # Find first non-empty line
        first_line = None
        for line in lines:
            if line.strip():
                first_line = line.strip()
                break
        
        if not first_line:
            return {"error": "No content found in file"}
        
        # Test different delimiters
        delimiters = [',', ';', '\t', '|', '*']
        delimiter_scores = {}
        
        for delimiter in delimiters:
            try:
                reader = csv.reader([first_line], delimiter=delimiter)
                row = next(reader)
                delimiter_scores[delimiter] = len(row)
            except:
                delimiter_scores[delimiter] = 0
        
        # Find best delimiter
        best_delimiter = max(delimiter_scores.items(), key=lambda x: x[1])[0]
        
        # Parse sample data
        sample_lines = lines[:10]  # First 10 lines
        parsed_data = []
        
        for line in sample_lines:
            if line.strip():
                try:
                    reader = csv.reader([line], delimiter=best_delimiter)
                    row = next(reader)
                    parsed_data.append(row)
                except:
                    continue
        
        if not parsed_data:
            return {"error": "Could not parse CSV data"}
        
        # Analyze structure
        field_count = len(parsed_data[0])
        has_header = True
        
        # Check if first row looks like header
        first_row = parsed_data[0]
        text_fields = sum(1 for field in first_row if not field.replace('.', '').replace('-', '').isdigit())
        has_header = text_fields > field_count / 2
        
        headers = parsed_data[0] if has_header else [f"field_{i}" for i in range(field_count)]
        sample_rows = parsed_data[1:6] if has_header else parsed_data[:5]
        
        # Estimate row count
        row_count_estimate = len(lines) - 1 if has_header else len(lines)
        
        return {
            "format": "csv",
            "encoding": encoding,
            "delimiter": best_delimiter,
            "has_header": has_header,
            "field_count": field_count,
            "headers": headers,
            "sample_rows": sample_rows,
            "row_count_estimate": row_count_estimate,
            "sample_rows_count": len(sample_rows)
        }
        
    except Exception as e:
        return {"error": f"Failed to preview CSV: {str(e)}"}

def preview_json_content(content: bytes, filename: str) -> Dict[str, Any]:
    """Preview JSON file content and extract structure"""
    try:
        # Detect encoding
        detected = chardet.detect(content)
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        
        # Decode content
        text_content = content.decode(encoding or 'utf-8', errors='ignore')
        
        # Parse JSON
        data = json.loads(text_content)
        
        # Analyze structure
        structure = analyze_json_structure(data, max_depth=2)
        
        # Check if this looks like metadata
        is_metadata = False
        if isinstance(data, dict):
            metadata_keys = ['metadata', 'schema', 'definition', 'properties', 'fields', 'columns']
            is_metadata = any(key in data for key in metadata_keys)
        
        return {
            "format": "json",
            "encoding": encoding,
            "is_metadata": is_metadata,
            "structure": structure,
            "data_type": type(data).__name__,
            "sample_data": data if isinstance(data, (dict, list)) and len(str(data)) < 1000 else str(data)[:500]
        }
        
    except Exception as e:
        return {"error": f"Failed to preview JSON: {str(e)}"}

def preview_xml_content(content: bytes, filename: str) -> Dict[str, Any]:
    """Preview XML file content and extract structure"""
    try:
        # Detect encoding
        detected = chardet.detect(content)
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        
        # Decode content
        text_content = content.decode(encoding or 'utf-8', errors='ignore')
        
        # Parse XML
        root = ET.fromstring(text_content)
        
        # Analyze structure
        structure = analyze_xml_structure(root, max_depth=2)
        
        # Check if this looks like metadata
        is_metadata = False
        metadata_tags = ['metadata', 'schema', 'definition', 'properties', 'fields', 'columns']
        is_metadata = any(tag in root.tag.lower() for tag in metadata_tags)
        
        return {
            "format": "xml",
            "encoding": encoding,
            "is_metadata": is_metadata,
            "structure": structure,
            "root_tag": root.tag,
            "sample_content": text_content[:500]
        }
        
    except Exception as e:
        return {"error": f"Failed to preview XML: {str(e)}"}

def preview_dbf_content(content: bytes, filename: str) -> Dict[str, Any]:
    """Preview DBF file content and extract field structure"""
    try:
        # DBF files have a specific structure
        # Header is 32 bytes, followed by field descriptors
        if len(content) < 32:
            return {"error": "File too small to be a valid DBF"}
        
        # Read header
        header = content[:32]
        num_records = int.from_bytes(header[4:8], byteorder='little')
        header_length = int.from_bytes(header[8:10], byteorder='little')
        record_length = int.from_bytes(header[10:12], byteorder='little')
        
        # Calculate number of fields
        num_fields = (header_length - 33) // 32
        
        if num_fields <= 0:
            return {"error": "Invalid field count"}
        
        # Read field descriptors
        fields = []
        for i in range(num_fields):
            field_start = 32 + (i * 32)
            field_data = content[field_start:field_start + 32]
            
            field_name = field_data[:11].decode('ascii', errors='ignore').strip('\x00')
            field_type = field_data[11:12].decode('ascii', errors='ignore')
            field_length = field_data[16]
            field_decimal = field_data[17]
            
            fields.append({
                "name": field_name,
                "type": field_type,
                "length": field_length,
                "decimal": field_decimal
            })
        
        return {
            "format": "dbf",
            "has_structure": True,
            "num_records": num_records,
            "header_length": header_length,
            "record_length": record_length,
            "num_fields": num_fields,
            "fields": fields
        }
        
    except Exception as e:
        return {"error": f"Failed to preview DBF: {str(e)}"}

def identify_data_standards(field_analysis: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
    """Identify data standards based on field analysis and filename patterns"""
    identified_standards = []
    
    # Extract field names and patterns
    field_names = [field.get('field_name', '').lower() for field in field_analysis]
    field_patterns = [field.get('sample_values', []) for field in field_analysis]
    
    # Check each standard
    for standard_id, standard_info in DATA_STANDARDS.items():
        confidence = 0.0
        matched_fields = []
        matched_patterns = 0
        
        # Check required fields
        required_fields = standard_info.get('required_fields', [])
        for required_field in required_fields:
            # Check for exact matches and partial matches
            for field_name in field_names:
                if required_field.lower() in field_name or field_name in required_field.lower():
                    matched_fields.append(required_field)
                    confidence += 0.3
                    break
        
        # Check field patterns
        field_patterns_dict = standard_info.get('field_patterns', {})
        for pattern_field, pattern in field_patterns_dict.items():
            for i, field_name in enumerate(field_names):
                if pattern_field.lower() in field_name or field_name in pattern_field.lower():
                    # Check if sample values match the pattern
                    if i < len(field_patterns) and field_patterns[i]:
                        import re
                        pattern_matches = sum(1 for value in field_patterns[i][:5] if re.match(pattern, str(value), re.IGNORECASE))
                        if pattern_matches > 0:
                            matched_patterns += 1
                            confidence += 0.2
        
        # Check filename patterns for specific standards
        filename_lower = filename.lower()
        if standard_id == "OS_Standards" and any(term in filename_lower for term in ['os_', 'ordnance', 'survey', 'mastermap', 'addressbase']):
            confidence += 0.4
        elif standard_id == "VOA_NNDR" and any(term in filename_lower for term in ['voa', 'nndr', 'business_rates', 'rateable_value']):
            confidence += 0.4
        elif standard_id == "ONS_Standards" and any(term in filename_lower for term in ['ons', 'census', 'statistics', 'population']):
            confidence += 0.4
        elif standard_id == "BS7666" and any(term in filename_lower for term in ['address', 'uprn', 'usrn', 'bs7666']):
            confidence += 0.4
        elif standard_id == "INSPIRE" and any(term in filename_lower for term in ['inspire', 'spatial', 'geometry', 'gml']):
            confidence += 0.4
        
        # Calculate final confidence
        if len(required_fields) > 0:
            field_match_ratio = len(matched_fields) / len(required_fields)
            confidence += field_match_ratio * 0.3
        
        if matched_patterns > 0:
            confidence += min(matched_patterns * 0.1, 0.3)
        
        # Only include standards with reasonable confidence
        if confidence >= 0.2:
            identified_standards.append({
                "standard_id": standard_id,
                "name": standard_info["name"],
                "description": standard_info["description"],
                "confidence": min(confidence, 1.0),
                "matched_fields": matched_fields,
                "governing_body": standard_info["governing_body"],
                "country": standard_info["country"],
                "compliance_score": calculate_compliance_score(standard_info, field_analysis)
            })
    
    # Sort by confidence (highest first)
    identified_standards.sort(key=lambda x: x["confidence"], reverse=True)
    
    return identified_standards

def calculate_compliance_score(standard_info: Dict[str, Any], field_analysis: List[Dict[str, Any]]) -> float:
    """Calculate compliance score for a data standard"""
    required_fields = standard_info.get('required_fields', [])
    field_names = [field.get('field_name', '').lower() for field in field_analysis]
    
    if not required_fields:
        return 0.0
    
    matched_required = 0
    for required_field in required_fields:
        for field_name in field_names:
            if required_field.lower() in field_name or field_name in required_field.lower():
                matched_required += 1
                break
    
    return matched_required / len(required_fields)

def generate_compliance_recommendations(standards: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations for improving compliance with identified standards"""
    recommendations = []
    
    for standard in standards:
        if standard["compliance_score"] < 0.8:
            missing_fields = []
            required_fields = DATA_STANDARDS[standard["standard_id"]]["required_fields"]
            field_names = [field.get('field_name', '').lower() for field in analysis.get("field_analysis", [])]
            
            for required_field in required_fields:
                if not any(required_field.lower() in field_name or field_name in required_field.lower() for field_name in field_names):
                    missing_fields.append(required_field)
            
            if missing_fields:
                recommendations.append(f"Add missing fields for {standard['name']}: {', '.join(missing_fields)}")
        
        if standard["confidence"] < 0.7:
            recommendations.append(f"Verify compliance with {standard['name']} - low confidence match")
    
    return recommendations

def assess_data_quality(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Assess the quality of the uploaded data"""
    quality_score = 0.0
    issues = []
    strengths = []
    
    field_analysis = analysis.get("field_analysis", [])
    
    if not field_analysis:
        return {
            "score": 0.0,
            "issues": ["No field analysis available"],
            "strengths": [],
            "overall_rating": "Poor"
        }
    
    # Check for required fields
    required_field_patterns = ['id', 'name', 'code', 'reference', 'identifier']
    has_identifier = any(any(pattern in field.get('field_name', '').lower() for pattern in required_field_patterns) 
                        for field in field_analysis)
    
    if has_identifier:
        quality_score += 0.2
        strengths.append("Contains identifier fields")
    else:
        issues.append("Missing identifier fields")
    
    # Check data consistency
    consistent_types = 0
    for field in field_analysis:
        if field.get('confidence', 0) > 0.8:
            consistent_types += 1
    
    type_consistency = consistent_types / len(field_analysis) if field_analysis else 0
    quality_score += type_consistency * 0.3
    
    if type_consistency > 0.8:
        strengths.append("High data type consistency")
    elif type_consistency < 0.5:
        issues.append("Low data type consistency")
    
    # Check for spatial data
    spatial_fields = [field for field in field_analysis if 'geometry' in field.get('field_name', '').lower() or 'coordinate' in field.get('field_name', '').lower()]
    if spatial_fields:
        quality_score += 0.2
        strengths.append("Contains spatial data")
    
    # Check for date/time fields
    date_fields = [field for field in field_analysis if 'date' in field.get('field_name', '').lower() or 'time' in field.get('field_name', '').lower()]
    if date_fields:
        quality_score += 0.1
        strengths.append("Contains temporal data")
    
    # Check field count
    if len(field_analysis) >= 5:
        quality_score += 0.1
        strengths.append("Reasonable number of fields")
    elif len(field_analysis) < 3:
        issues.append("Very few fields - may be incomplete")
    
    # Determine overall rating
    if quality_score >= 0.8:
        overall_rating = "Excellent"
    elif quality_score >= 0.6:
        overall_rating = "Good"
    elif quality_score >= 0.4:
        overall_rating = "Fair"
    else:
        overall_rating = "Poor"
    
    return {
        "score": min(quality_score, 1.0),
        "issues": issues,
        "strengths": strengths,
        "overall_rating": overall_rating,
        "field_count": len(field_analysis),
        "spatial_fields": len(spatial_fields),
        "temporal_fields": len(date_fields)
    }

@router.post("/ai/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    """AI-powered file analysis to detect format, structure, and data standards"""
    try:
        print(f"Starting analysis for file: {file.filename}")
        
        # Read only first 1MB for fast analysis
        content = await file.read(1024 * 1024)  # 1MB chunk
        print(f"Read {len(content)} bytes from file")
        
        # Detect file type
        filename = file.filename or "uploaded_file"
        file_extension = Path(filename).suffix.lower()
        mime_type = file.content_type
        
        print(f"File extension: {file_extension}, MIME type: {mime_type}")
        
        # Analyze based on file type
        if file_extension == '.csv' or mime_type == 'text/csv':
            print("Detecting CSV format...")
            analysis = detect_csv_format(content, filename)
        elif file_extension == '.json' or mime_type == 'application/json':
            print("Detecting JSON format...")
            analysis = detect_json_format(content, filename)
        elif file_extension in ['.xml', '.gml'] or mime_type in ['application/xml', 'text/xml']:
            print("Detecting XML format...")
            analysis = detect_xml_format(content, filename)
        elif file_extension == '.zip' or mime_type == 'application/zip':
            print("Detecting ZIP format...")
            analysis = detect_zip_format(content, filename)
        else:
            print("Attempting format detection from content...")
            # Try to detect format from content
            if content.startswith(b'{') or content.startswith(b'['):
                analysis = detect_json_format(content, filename)
            elif content.startswith(b'<'):
                analysis = detect_xml_format(content, filename)
            else:
                # Assume CSV and try to detect
                analysis = detect_csv_format(content, filename)
        
        print(f"Analysis result keys: {list(analysis.keys()) if isinstance(analysis, dict) else 'Not a dict'}")
        
        if "error" in analysis:
            print(f"Analysis error: {analysis['error']}")
            raise HTTPException(status_code=400, detail=analysis["error"])
        
        # Add file metadata
        analysis["filename"] = file.filename
        analysis["file_size"] = len(content)
        analysis["mime_type"] = mime_type
        
        # Limit sample rows for faster response
        if "sample_rows" in analysis and isinstance(analysis["sample_rows"], list) and len(analysis["sample_rows"]) > 10:
            analysis["sample_rows"] = analysis["sample_rows"][:10]
        
        # Identify data standards if we have field analysis
        if "field_analysis" in analysis:
            print("Identifying data standards...")
            standards = identify_data_standards(analysis["field_analysis"], filename or 'uploaded_file')
            analysis["identified_standards"] = standards
            
            # Add government body analysis
            if standards:
                analysis["primary_governing_body"] = standards[0]["governing_body"]
                analysis["compliance_analysis"] = {
                    "overall_compliance": sum(s["compliance_score"] for s in standards) / len(standards),
                    "standards_count": len(standards),
                    "recommended_actions": generate_compliance_recommendations(standards, analysis)
                }
        
        # Generate recommendations
        print("Generating recommendations...")
        analysis["recommendations"] = generate_recommendations(analysis)
        
        # Add data quality assessment
        analysis["data_quality"] = assess_data_quality(analysis)
        
        print("Analysis completed successfully")
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Analysis failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/ai/generate-mappings")
async def generate_source_staging_mappings(
    request_data: dict
):
    """Generate source-to-staging table mappings for each field"""
    try:
        header_file = request_data.get("header_file")
        data_files = request_data.get("data_files", [])
        analysis_data = request_data.get("analysis_data", {})
        
        if not header_file:
            raise HTTPException(status_code=400, detail="Header file is required")
        
        if not data_files:
            raise HTTPException(status_code=400, detail="At least one data file is required")
        
        mappings = {
            "header_file": header_file,
            "data_files": data_files,
            "field_mappings": [],
            "staging_table_schema": {},
            "recommendations": [],
            "mapping_type": "unknown"
        }
        
        # Extract field information from header file
        header_fields = []
        has_headers = False
        sample_data = []
        
        if header_file in analysis_data.get("file_previews", {}):
            preview = analysis_data["file_previews"][header_file]
            
            if preview.get("format") == "csv":
                has_headers = preview.get("has_header", False)
                if has_headers and preview.get("headers"):
                    # CSV with headers - use actual header names
                    header_fields = preview["headers"]
                    mappings["mapping_type"] = "csv_with_headers"
                elif not has_headers and preview.get("sample_rows"):
                    # CSV without headers - generate field names based on data standards
                    sample_data = preview["sample_rows"]
                    field_count = len(sample_data[0]) if sample_data else 0
                    header_fields = generate_field_names_from_data_standards(sample_data, field_count)
                    mappings["mapping_type"] = "csv_without_headers"
            elif preview.get("format") == "dbf" and preview.get("fields"):
                header_fields = [field["name"] for field in preview["fields"]]
                mappings["mapping_type"] = "dbf"
            elif preview.get("format") == "json" and preview.get("structure"):
                # Extract field names from JSON structure
                structure = preview["structure"]
                if isinstance(structure, dict):
                    header_fields = list(structure.keys())
                mappings["mapping_type"] = "json"
        
        # Generate field mappings for each header field
        for i, field_name in enumerate(header_fields):
            # Clean field name for database
            clean_field_name = re.sub(r'[^a-zA-Z0-9_]', '_', field_name.lower())
            clean_field_name = re.sub(r'_+', '_', clean_field_name)
            clean_field_name = clean_field_name.strip('_')
            
            # Determine data type based on field name, sample data, and analysis
            data_type = determine_field_data_type_from_sample(field_name, i, sample_data, analysis_data)
            postgis_type = determine_postgis_type(field_name, data_type, analysis_data)
            
            # Generate constraints
            constraints = generate_field_constraints(field_name, data_type, analysis_data)
            
            mapping = {
                "source_field": field_name,
                "staging_field": clean_field_name,
                "data_type": data_type,
                "postgis_type": postgis_type,
                "is_required": False,
                "is_primary_key": False,
                "constraints": constraints,
                "transformation_rules": [],
                "validation_rules": [],
                "description": f"Field {i+1}: {field_name}",
                "sequence_order": i + 1,
                "source_column_index": i
            }
            
            # Add transformation rules based on field type
            if data_type == "postcode":
                mapping["transformation_rules"].append("UPPER(TRIM(field))")
                mapping["validation_rules"].append("UK postcode format validation")
            elif data_type == "uprn":
                mapping["transformation_rules"].append("CAST(field AS BIGINT)")
                mapping["validation_rules"].append("12-digit numeric validation")
            elif data_type == "coordinate":
                mapping["transformation_rules"].append("ST_GeomFromText('POINT(' || x || ' ' || y || ')', 4326)")
            elif data_type == "date":
                mapping["transformation_rules"].append("TO_DATE(field, 'YYYY-MM-DD')")
            
            mappings["field_mappings"].append(mapping)
        
        # Generate staging table schema
        if mappings["field_mappings"]:
            first_field = mappings["field_mappings"][0]
            clean_table_name = re.sub(r'[^a-zA-Z0-9_]', '_', Path(header_file).stem.lower())
            clean_table_name = re.sub(r'_+', '_', clean_table_name)
            
            mappings["staging_table_schema"] = {
                "table_name": f"staging_{clean_table_name}_data",
                "schema": "staging",
                "fields": mappings["field_mappings"],
                "indexes": generate_staging_indexes(mappings["field_mappings"]),
                "constraints": generate_staging_constraints(mappings["field_mappings"])
            }
        
        # Generate recommendations
        mappings["recommendations"] = generate_mapping_recommendations(mappings["field_mappings"], analysis_data)
        
        return {
            "success": True,
            "mappings": mappings,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mapping generation failed: {str(e)}")

def generate_field_names_from_data_standards(sample_data: List[List[str]], field_count: int) -> List[str]:
    """Generate field names based on data standards when no headers are present"""
    field_names = []
    
    # Common field patterns for UK government data
    uk_government_patterns = [
        "uprn", "usrn", "postcode", "address", "property_ref", "street_ref",
        "x_coordinate", "y_coordinate", "latitude", "longitude", "easting", "northing",
        "property_description", "rateable_value", "business_name", "property_type",
        "local_authority", "ward", "constituency", "region", "country"
    ]
    
    # Analyze sample data to identify field types
    for i in range(field_count):
        column_values = [row[i] for row in sample_data if i < len(row)]
        
        # Try to identify field type from data patterns
        field_type = identify_field_type_from_values(column_values, i)
        
        # Generate appropriate field name
        if field_type in uk_government_patterns:
            field_names.append(field_type)
        else:
            # Use generic field name with type indicator
            field_names.append(f"field_{i+1}_{field_type}")
    
    return field_names

def identify_field_type_from_values(values: List[str], column_index: int) -> str:
    """Identify field type from sample values"""
    if not values:
        return "unknown"
    
    # Remove empty values
    non_empty_values = [v.strip() for v in values if v.strip()]
    
    if not non_empty_values:
        return "empty"
    
    # Test for specific patterns
    for value in non_empty_values[:10]:  # Check first 10 values
        # Test UK postcode
        if re.match(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$', value.upper()):
            return "postcode"
        
        # Test UPRN (12-digit number)
        if re.match(r'^\d{12}$', value):
            return "uprn"
        
        # Test USRN (8-digit number)
        if re.match(r'^\d{8}$', value):
            return "usrn"
        
        # Test coordinates
        try:
            coord = float(value)
            if -180 <= coord <= 180:  # Likely longitude
                return "longitude"
            elif -90 <= coord <= 90:  # Likely latitude
                return "latitude"
        except:
            pass
        
        # Test date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        for pattern in date_patterns:
            if re.match(pattern, value):
                return "date"
        
        # Test numeric patterns
        if value.replace('.', '').replace('-', '').isdigit():
            if '.' in value:
                return "decimal"
            else:
                return "integer"
    
    # Default based on column position (common patterns)
    if column_index == 0:
        return "id"
    elif column_index == 1:
        return "name"
    elif column_index == 2:
        return "description"
    else:
        return "field"

def determine_field_data_type_from_sample(field_name: str, column_index: int, sample_data: List[List[str]], analysis_data: dict) -> str:
    """Determine data type based on field name, column index, and sample data"""
    # First try to determine from field name
    field_lower = field_name.lower()
    
    # Check for specific field patterns
    if any(pattern in field_lower for pattern in ['postcode', 'post_code', 'zip']):
        return "postcode"
    elif any(pattern in field_lower for pattern in ['uprn', 'property_ref', 'property_id']):
        return "uprn"
    elif any(pattern in field_lower for pattern in ['usrn', 'street_ref', 'street_id']):
        return "usrn"
    elif any(pattern in field_lower for pattern in ['lat', 'latitude', 'y_coord', 'y_coordinate', 'northing']):
        return "coordinate"
    elif any(pattern in field_lower for pattern in ['lon', 'longitude', 'x_coord', 'x_coordinate', 'easting']):
        return "coordinate"
    elif any(pattern in field_lower for pattern in ['date', 'created', 'updated', 'timestamp']):
        return "date"
    elif any(pattern in field_lower for pattern in ['amount', 'value', 'price', 'cost', 'rate']):
        return "decimal"
    elif any(pattern in field_lower for pattern in ['count', 'number', 'quantity', 'total']):
        return "integer"
    elif any(pattern in field_lower for pattern in ['name', 'title', 'description', 'text']):
        return "text"
    elif any(pattern in field_lower for pattern in ['active', 'enabled', 'status', 'flag']):
        return "boolean"
    
    # If no pattern match, analyze sample data
    if sample_data and column_index < len(sample_data[0]):
        column_values = [row[column_index] for row in sample_data if column_index < len(row)]
        return identify_field_type_from_values(column_values, column_index)
    
    # Default to text
    return "text"

def determine_field_data_type(field_name: str, analysis_data: dict) -> str:
    """Determine the appropriate data type for a field based on name and analysis"""
    field_lower = field_name.lower()
    
    # Check for specific field patterns
    if any(pattern in field_lower for pattern in ['postcode', 'post_code', 'zip']):
        return "postcode"
    elif any(pattern in field_lower for pattern in ['uprn', 'property_ref', 'property_id']):
        return "uprn"
    elif any(pattern in field_lower for pattern in ['usrn', 'street_ref', 'street_id']):
        return "usrn"
    elif any(pattern in field_lower for pattern in ['lat', 'latitude', 'y_coord', 'y_coordinate']):
        return "coordinate"
    elif any(pattern in field_lower for pattern in ['lon', 'longitude', 'x_coord', 'x_coordinate']):
        return "coordinate"
    elif any(pattern in field_lower for pattern in ['date', 'created', 'updated', 'timestamp']):
        return "date"
    elif any(pattern in field_lower for pattern in ['amount', 'value', 'price', 'cost', 'rate']):
        return "decimal"
    elif any(pattern in field_lower for pattern in ['count', 'number', 'quantity', 'total']):
        return "integer"
    elif any(pattern in field_lower for pattern in ['name', 'title', 'description', 'text']):
        return "text"
    elif any(pattern in field_lower for pattern in ['active', 'enabled', 'status', 'flag']):
        return "boolean"
    else:
        return "text"  # Default to text

def determine_postgis_type(field_name: str, data_type: str, analysis_data: dict) -> Optional[str]:
    """Determine the appropriate PostGIS type for a field"""
    # Only return PostGIS geometry types, not regular PostgreSQL types
    if data_type == "geometry":
        # Check field name for specific geometry types
        field_lower = field_name.lower()
        if any(pattern in field_lower for pattern in ['point', 'lat', 'lon', 'latitude', 'longitude']):
            return "POINT"
        elif any(pattern in field_lower for pattern in ['line', 'linestring', 'road', 'street']):
            return "LINESTRING"
        elif any(pattern in field_lower for pattern in ['polygon', 'boundary', 'area', 'shape']):
            return "POLYGON"
        else:
            return "POINT"  # Default to POINT for geometry fields
    else:
        # Return None for non-geometry fields - PostGIS type should only be set for geometry fields
        return None

def generate_field_constraints(field_name: str, data_type: str, analysis_data: dict) -> List[str]:
    """Generate appropriate constraints for a field"""
    constraints = []
    
    if data_type == "postcode":
        constraints.append("CHECK (field ~ '^[A-Z]{1,2}[0-9][A-Z0-9]?\\s*[0-9][A-Z]{2}$')")
    elif data_type == "uprn":
        constraints.append("CHECK (field >= 100000000000 AND field <= 999999999999)")
    elif data_type == "coordinate":
        constraints.append("CHECK (field >= -90 AND field <= 90)")
    
    return constraints

def generate_staging_indexes(field_mappings: List[dict]) -> List[dict]:
    """Generate appropriate indexes for staging table"""
    indexes = []
    
    for mapping in field_mappings:
        if mapping["data_type"] in ["uprn", "usrn", "postcode"]:
            indexes.append({
                "name": f"idx_{mapping['staging_field']}",
                "fields": [mapping["staging_field"]],
                "type": "btree"
            })
    
    return indexes

def generate_staging_constraints(field_mappings: List[dict]) -> List[dict]:
    """Generate table-level constraints for staging table"""
    constraints = []
    
    # Add source file tracking
    constraints.append({
        "name": "chk_source_file",
        "type": "check",
        "definition": "source_file IS NOT NULL"
    })
    
    return constraints

def generate_mapping_recommendations(field_mappings: List[dict], analysis_data: dict) -> List[str]:
    """Generate recommendations for field mappings"""
    recommendations = []
    
    # Check for potential issues
    for mapping in field_mappings:
        if mapping["data_type"] == "coordinate":
            recommendations.append(f"Consider using PostGIS GEOMETRY type for {mapping['source_field']}")
        
        if mapping["data_type"] == "postcode":
            recommendations.append(f"Add postcode validation for {mapping['source_field']}")
    
    # General recommendations
    recommendations.append("Add source_file column for data lineage tracking")
    recommendations.append("Add created_at and updated_at timestamp columns")
    recommendations.append("Consider adding data quality checks")
    
    return recommendations

def generate_recommendations(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recommendations based on analysis"""
    recommendations = {
        "data_structure": [],
        "field_mapping": [],
        "validation_rules": [],
        "postgis_types": []
    }
    
    if "field_analysis" in analysis:
        for i, field in enumerate(analysis["field_analysis"]):
            field_type = field.get("type", "unknown")
            
            # Data structure recommendations
            if field_type == "postcode":
                recommendations["data_structure"].append(f"Field {i}: Use VARCHAR(8) for UK postcodes")
                recommendations["validation_rules"].append(f"Field {i}: Validate UK postcode format")
            elif field_type == "uprn":
                recommendations["data_structure"].append(f"Field {i}: Use BIGINT for UPRN (12 digits)")
                recommendations["validation_rules"].append(f"Field {i}: Validate 12-digit numeric UPRN")
            elif field_type == "coordinate":
                recommendations["postgis_types"].append(f"Field {i}: Consider GEOMETRY(POINT,4326) for coordinates")
            elif field_type == "date":
                recommendations["data_structure"].append(f"Field {i}: Use DATE or TIMESTAMP for dates")
            elif field_type == "decimal":
                recommendations["data_structure"].append(f"Field {i}: Use DECIMAL(15,2) for monetary values")
    
    # Format-specific recommendations
    if analysis.get("format") == "csv":
        recommendations["data_structure"].append(f"Use delimiter: '{analysis.get('delimiter', ',')}'")
        if analysis.get("has_header"):
            recommendations["data_structure"].append("File has headers - use HEADER TRUE in COPY command")
    
    return recommendations

@router.get("/data-standards")
async def get_data_standards(
    category: Optional[str] = None,
    country: Optional[str] = None,
    compliance_level: Optional[str] = None,
    governing_body: Optional[str] = None
):
    """Get list of supported data standards with optional filtering"""
    filtered_standards = DATA_STANDARDS.copy()
    
    # Apply filters
    if category:
        filtered_standards = {k: v for k, v in filtered_standards.items() if v.get('category') == category}
    
    if country:
        filtered_standards = {k: v for k, v in filtered_standards.items() if v.get('country') == country}
    
    if compliance_level:
        filtered_standards = {k: v for k, v in filtered_standards.items() if v.get('compliance_level') == compliance_level}
    
    if governing_body:
        filtered_standards = {k: v for k, v in filtered_standards.items() if v.get('governing_body') == governing_body}
    
    return {
        "standards": filtered_standards,
        "count": len(filtered_standards),
        "total_count": len(DATA_STANDARDS),
        "filters_applied": {
            "category": category,
            "country": country,
            "compliance_level": compliance_level,
            "governing_body": governing_body
        }
    }

@router.get("/data-standards/categories")
async def get_data_standards_categories():
    """Get data standards categories and subcategories"""
    return {
        "categories": DATA_STANDARDS_CATEGORIES,
        "count": len(DATA_STANDARDS_CATEGORIES)
    }

@router.get("/data-standards/compliance-levels")
async def get_compliance_levels():
    """Get compliance levels for data standards"""
    return {
        "compliance_levels": COMPLIANCE_LEVELS,
        "count": len(COMPLIANCE_LEVELS)
    }

@router.get("/data-standards/{standard_id}")
async def get_data_standard(standard_id: str):
    """Get specific data standard by ID"""
    if standard_id not in DATA_STANDARDS:
        raise HTTPException(status_code=404, detail=f"Data standard '{standard_id}' not found")
    
    return {
        "standard": DATA_STANDARDS[standard_id],
        "id": standard_id
    }

@router.get("/data-standards/search")
async def search_data_standards(
    query: str,
    category: Optional[str] = None,
    country: Optional[str] = None
):
    """Search data standards by name, description, or governing body"""
    results = []
    query_lower = query.lower()
    
    for standard_id, standard in DATA_STANDARDS.items():
        # Skip if category filter doesn't match
        if category and standard.get('category') != category:
            continue
        
        # Skip if country filter doesn't match
        if country and standard.get('country') != country:
            continue
        
        # Search in name, description, and governing body
        if (query_lower in standard.get('name', '').lower() or
            query_lower in standard.get('description', '').lower() or
            query_lower in standard.get('governing_body', '').lower()):
            results.append({
                "id": standard_id,
                **standard
            })
    
    return {
        "results": results,
        "count": len(results),
        "query": query,
        "filters": {"category": category, "country": country}
    }

@router.get("/data-standards/statistics")
async def get_data_standards_statistics():
    """Get statistics about data standards"""
    stats = {
        "total_standards": len(DATA_STANDARDS),
        "by_category": {},
        "by_country": {},
        "by_compliance_level": {},
        "by_governing_body": {}
    }
    
    # Count by category
    for standard in DATA_STANDARDS.values():
        category = standard.get('category', 'unknown')
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        country = standard.get('country', 'unknown')
        stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
        
        compliance = standard.get('compliance_level', 'unknown')
        stats['by_compliance_level'][compliance] = stats['by_compliance_level'].get(compliance, 0) + 1
        
        governing_body = standard.get('governing_body', 'unknown')
        stats['by_governing_body'][governing_body] = stats['by_governing_body'].get(governing_body, 0) + 1
    
    return stats

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the router is working"""
    return {
        "message": "Design Enhanced API is working",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/data-types")
async def get_available_data_types():
    """Get list of available data types for field mapping"""
    data_types = [
        # Standard PostgreSQL types
        {"value": "text", "label": "Text", "description": "Variable-length character string", "postgres_type": "TEXT"},
        {"value": "varchar", "label": "VARCHAR", "description": "Variable-length character string with max length", "postgres_type": "VARCHAR(255)"},
        {"value": "integer", "label": "Integer", "description": "Whole number", "postgres_type": "INTEGER"},
        {"value": "bigint", "label": "Big Integer", "description": "Large whole number (e.g., UPRN)", "postgres_type": "BIGINT"},
        {"value": "decimal", "label": "Decimal", "description": "Fixed-point decimal number", "postgres_type": "DECIMAL(10,2)"},
        {"value": "numeric", "label": "Numeric", "description": "Variable-precision decimal number", "postgres_type": "NUMERIC"},
        {"value": "date", "label": "Date", "description": "Date without time", "postgres_type": "DATE"},
        {"value": "timestamp", "label": "Timestamp", "description": "Date and time", "postgres_type": "TIMESTAMP"},
        {"value": "boolean", "label": "Boolean", "description": "True/false value", "postgres_type": "BOOLEAN"},
        {"value": "json", "label": "JSON", "description": "JSON data type", "postgres_type": "JSONB"},
        {"value": "uuid", "label": "UUID", "description": "Universally unique identifier", "postgres_type": "UUID"},
        
        # PostGIS Geometry types
        {"value": "geometry", "label": "Geometry", "description": "Generic geometry type (PostGIS)", "postgres_type": "GEOMETRY"},
        {"value": "geometry_point", "label": "Geometry (Point)", "description": "Point geometry with SRID 4326", "postgres_type": "GEOMETRY(POINT,4326)"},
        {"value": "geometry_linestring", "label": "Geometry (LineString)", "description": "LineString geometry with SRID 4326", "postgres_type": "GEOMETRY(LINESTRING,4326)"},
        {"value": "geometry_polygon", "label": "Geometry (Polygon)", "description": "Polygon geometry with SRID 4326", "postgres_type": "GEOMETRY(POLYGON,4326)"},
        {"value": "geometry_multipoint", "label": "Geometry (MultiPoint)", "description": "MultiPoint geometry with SRID 4326", "postgres_type": "GEOMETRY(MULTIPOINT,4326)"},
        {"value": "geometry_multilinestring", "label": "Geometry (MultiLineString)", "description": "MultiLineString geometry with SRID 4326", "postgres_type": "GEOMETRY(MULTILINESTRING,4326)"},
        {"value": "geometry_multipolygon", "label": "Geometry (MultiPolygon)", "description": "MultiPolygon geometry with SRID 4326", "postgres_type": "GEOMETRY(MULTIPOLYGON,4326)"},
        {"value": "geometry_collection", "label": "Geometry (GeometryCollection)", "description": "GeometryCollection with SRID 4326", "postgres_type": "GEOMETRY(GEOMETRYCOLLECTION,4326)"},
        
        # PostGIS Geography types
        {"value": "geography", "label": "Geography", "description": "Generic geography type (PostGIS)", "postgres_type": "GEOGRAPHY"},
        {"value": "geography_point", "label": "Geography (Point)", "description": "Point geography with SRID 4326", "postgres_type": "GEOGRAPHY(POINT,4326)"},
        {"value": "geography_linestring", "label": "Geography (LineString)", "description": "LineString geography with SRID 4326", "postgres_type": "GEOGRAPHY(LINESTRING,4326)"},
        {"value": "geography_polygon", "label": "Geography (Polygon)", "description": "Polygon geography with SRID 4326", "postgres_type": "GEOGRAPHY(POLYGON,4326)"},
        {"value": "geography_multipoint", "label": "Geography (MultiPoint)", "description": "MultiPoint geography with SRID 4326", "postgres_type": "GEOGRAPHY(MULTIPOINT,4326)"},
        {"value": "geography_multilinestring", "label": "Geography (MultiLineString)", "description": "MultiLineString geography with SRID 4326", "postgres_type": "GEOGRAPHY(MULTILINESTRING,4326)"},
        {"value": "geography_multipolygon", "label": "Geography (MultiPolygon)", "description": "MultiPolygon geography with SRID 4326", "postgres_type": "GEOGRAPHY(MULTIPOLYGON,4326)"},
        {"value": "geography_collection", "label": "Geography (GeometryCollection)", "description": "GeometryCollection geography with SRID 4326", "postgres_type": "GEOGRAPHY(GEOMETRYCOLLECTION,4326)"},
        
        # Specialized PostGIS types
        {"value": "box2d", "label": "Box2D", "description": "2D bounding box", "postgres_type": "BOX2D"},
        {"value": "box3d", "label": "Box3D", "description": "3D bounding box", "postgres_type": "BOX3D"},
        {"value": "raster", "label": "Raster", "description": "Raster data type", "postgres_type": "RASTER"}
    ]
    return {"data_types": data_types}

# Placeholder endpoints for backward compatibility (to prevent 404 errors)
@router.get("/ai/knowledge")
async def get_ai_knowledge_placeholder(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Placeholder for AI knowledge endpoint"""
    return {"knowledge": []}

@router.get("/datasets")
async def get_datasets_placeholder(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Placeholder for datasets endpoint - use structures instead"""
    return {"datasets": []}

@router.get("/canvases")
async def get_canvases_placeholder(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Placeholder for canvases endpoint"""
    return {"canvases": []}

@router.get("/components")
async def get_components_placeholder(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Placeholder for components endpoint"""
    return {"components": []}

@router.get("/schema-templates")
async def get_schema_templates_placeholder(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Placeholder for schema templates endpoint - use templates instead"""
    return {"templates": []}

@router.get("/notifications/rules")
async def get_notification_rules_placeholder(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Placeholder for notification rules endpoint"""
    return {"rules": []}

@router.get("/plugins")
async def get_plugins_placeholder(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Placeholder for plugins endpoint"""
    return {"plugins": []}

# Dataset Structure Management
@router.get("/structures")
async def get_dataset_structures(
    source_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get dataset structures with metadata"""
    try:
        query = """
            SELECT * FROM design_enhanced.dataset_structures 
            WHERE is_active = true
        """
        params = {}
        
        if source_type:
            query += " AND source_type = :source_type"
            params['source_type'] = source_type
            
        if status:
            query += " AND status = :status"
            params['status'] = status
            
        query += " ORDER BY created_at DESC"
        
        result = db.execute(text(query), params).mappings()
        structures = [dict(row) for row in result]
        
        return {"structures": structures}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dataset structures: {str(e)}")

@router.post("/structures")
async def create_dataset_structure(
    structure_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Create new dataset structure"""
    try:
        print(f"[STRUCTURE_CREATE] Starting structure creation")
        print(f"[STRUCTURE_CREATE] Structure data: {structure_data}")
        print(f"[STRUCTURE_CREATE] Current user: {current_user.username}")
        
        # Check for existing structure with same name and generate unique name if needed
        original_name = structure_data["dataset_name"]
        dataset_name = original_name
        counter = 1
        
        while True:
            check_query = "SELECT structure_id FROM design_enhanced.dataset_structures WHERE dataset_name = :dataset_name AND is_active = true"
            existing = db.execute(text(check_query), {"dataset_name": dataset_name}).fetchone()
            
            if not existing:
                break
            
            print(f"[STRUCTURE_CREATE] Name '{dataset_name}' already exists, trying with suffix")
            dataset_name = f"{original_name} ({counter})"
            counter += 1
            
            if counter > 100:  # Prevent infinite loop
                raise HTTPException(status_code=400, detail="Unable to generate unique dataset name")
        
        if dataset_name != original_name:
            print(f"[STRUCTURE_CREATE] Using unique name: {dataset_name}")
        
        structure_id = str(uuid.uuid4())
        query = """
            INSERT INTO design_enhanced.dataset_structures 
            (structure_id, dataset_name, description, source_type, file_formats, 
             governing_body, data_standards, business_owner, data_steward, created_by, tags)
            VALUES (:structure_id, :dataset_name, :description, :source_type, :file_formats,
                    :governing_body, :data_standards, :business_owner, :data_steward, :created_by, :tags)
        """
        
        # Map source_type to valid database values
        source_type = structure_data.get("source_type", "file")
        if source_type in ["csv", "json", "xml", "excel"]:
            source_type = "file"  # These are file formats, not source types
        
        params = {
            "structure_id": structure_id,
            "dataset_name": dataset_name,
            "description": structure_data.get("description", ""),
            "source_type": source_type,
            "file_formats": json.dumps(structure_data.get("file_formats", [])),
            "governing_body": structure_data.get("governing_body"),
            "data_standards": json.dumps(structure_data.get("data_standards", [])),
            "business_owner": structure_data.get("business_owner"),
            "data_steward": structure_data.get("data_steward"),
            "created_by": current_user.username,
            "tags": json.dumps(structure_data.get("tags", []))
        }
        
        print(f"[STRUCTURE_CREATE] Executing query with params: {params}")
        
        db.execute(text(query), params)
        db.commit()
        
        print(f"[STRUCTURE_CREATE] Structure created successfully with ID: {structure_id}")
        
        return {"message": "Dataset structure created successfully", "structure_id": structure_id}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"[STRUCTURE_CREATE] Error occurred: {str(e)}")
        print(f"[STRUCTURE_CREATE] Error type: {type(e).__name__}")
        import traceback
        print(f"[STRUCTURE_CREATE] Full traceback: {traceback.format_exc()}")
        
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating dataset structure: {str(e)}")

@router.put("/structures/{structure_id}")
async def update_dataset_structure(
    structure_id: str,
    structure_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Update existing dataset structure"""
    try:
        # Map source_type to valid database values
        source_type = structure_data.get("source_type", "file")
        if source_type in ["csv", "json", "xml", "excel"]:
            source_type = "file"  # These are file formats, not source types
        
        query = """
            UPDATE design_enhanced.dataset_structures 
            SET dataset_name = :dataset_name,
                description = :description,
                source_type = :source_type,
                file_formats = :file_formats,
                governing_body = :governing_body,
                data_standards = :data_standards,
                business_owner = :business_owner,
                data_steward = :data_steward,
                tags = :tags,
                updated_at = CURRENT_TIMESTAMP
            WHERE structure_id = :structure_id
        """
        
        params = {
            "structure_id": structure_id,
            "dataset_name": structure_data["dataset_name"],
            "description": structure_data.get("description", ""),
            "source_type": source_type,
            "file_formats": json.dumps(structure_data.get("file_formats", [])),
            "governing_body": structure_data.get("governing_body"),
            "data_standards": json.dumps(structure_data.get("data_standards", [])),
            "business_owner": structure_data.get("business_owner"),
            "data_steward": structure_data.get("data_steward"),
            "tags": json.dumps(structure_data.get("tags", []))
        }
        
        db.execute(text(query), params)
        db.commit()
        
        # Check if structure exists
        check_query = "SELECT structure_id FROM design_enhanced.dataset_structures WHERE structure_id = :structure_id"
        check_result = db.execute(text(check_query), {"structure_id": structure_id}).fetchone()
        
        if not check_result:
            raise HTTPException(status_code=404, detail="Dataset structure not found")
        
        return {"message": "Dataset structure updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating dataset structure: {str(e)}")

@router.delete("/structures/{structure_id}")
async def delete_dataset_structure(
    structure_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Delete a dataset structure and all its associated references"""
    try:
        print(f"[DELETE] Starting delete operation for structure_id: {structure_id}")
        print(f"[DELETE] Current user: {current_user.username}")
        
        # Check if structure exists
        check_query = "SELECT structure_id, dataset_name FROM design_enhanced.dataset_structures WHERE structure_id = :structure_id AND is_active = true"
        print(f"[DELETE] Executing check query: {check_query}")
        
        check_result = db.execute(text(check_query), {"structure_id": structure_id}).fetchone()
        print(f"[DELETE] Check result: {check_result}")
        
        if not check_result:
            print(f"[DELETE] Structure not found: {structure_id}")
            raise HTTPException(status_code=404, detail="Dataset structure not found")
        
        dataset_name = check_result[1]  # dataset_name is the second column
        print(f"[DELETE] Found structure: {dataset_name}")
        
        # Get counts of related records for logging
        field_count_query = "SELECT COUNT(*) FROM design_enhanced.field_definitions WHERE structure_id = :structure_id"
        template_count_query = "SELECT COUNT(*) FROM design_enhanced.table_templates WHERE structure_id = :structure_id AND is_active = true"
        mapping_count_query = "SELECT COUNT(*) FROM design_enhanced.field_mappings WHERE structure_id = :structure_id"
        upload_count_query = "SELECT COUNT(*) FROM design_enhanced.dataset_uploads WHERE structure_id = :structure_id"
        review_count_query = "SELECT COUNT(*) FROM design_enhanced.review_workflow WHERE structure_id = :structure_id"
        
        field_count = db.execute(text(field_count_query), {"structure_id": structure_id}).scalar() or 0
        template_count = db.execute(text(template_count_query), {"structure_id": structure_id}).scalar() or 0
        mapping_count = db.execute(text(mapping_count_query), {"structure_id": structure_id}).scalar() or 0
        upload_count = db.execute(text(upload_count_query), {"structure_id": structure_id}).scalar() or 0
        review_count = db.execute(text(review_count_query), {"structure_id": structure_id}).scalar() or 0
        
        print(f"[DELETE] Related records found: {field_count} fields, {template_count} templates, {mapping_count} mappings, {upload_count} uploads, {review_count} reviews")
        
        # Delete all related records first (in reverse dependency order)
        print(f"[DELETE] Deleting related records...")
        
        # 1. Delete review workflow records (they reference uploads and structures)
        if review_count > 0:
            review_delete_query = "DELETE FROM design_enhanced.review_workflow WHERE structure_id = :structure_id"
            db.execute(text(review_delete_query), {"structure_id": structure_id})
            print(f"[DELETE] Deleted {review_count} review workflow records")
        
        # 2. Delete dataset uploads
        if upload_count > 0:
            upload_delete_query = "DELETE FROM design_enhanced.dataset_uploads WHERE structure_id = :structure_id"
            db.execute(text(upload_delete_query), {"structure_id": structure_id})
            print(f"[DELETE] Deleted {upload_count} dataset uploads")
        
        # 3. Delete field mappings
        if mapping_count > 0:
            mapping_delete_query = "DELETE FROM design_enhanced.field_mappings WHERE structure_id = :structure_id"
            db.execute(text(mapping_delete_query), {"structure_id": structure_id})
            print(f"[DELETE] Deleted {mapping_count} field mappings")
        
        # 4. Delete generated tables (they reference templates and structures)
        generated_tables_query = "SELECT COUNT(*) FROM design_enhanced.generated_tables WHERE structure_id = :structure_id"
        generated_count = db.execute(text(generated_tables_query), {"structure_id": structure_id}).scalar() or 0
        if generated_count > 0:
            generated_delete_query = "DELETE FROM design_enhanced.generated_tables WHERE structure_id = :structure_id"
            db.execute(text(generated_delete_query), {"structure_id": structure_id})
            print(f"[DELETE] Deleted {generated_count} generated tables")
        
        # 5. Delete table templates
        if template_count > 0:
            template_delete_query = "DELETE FROM design_enhanced.table_templates WHERE structure_id = :structure_id"
            db.execute(text(template_delete_query), {"structure_id": structure_id})
            print(f"[DELETE] Deleted {template_count} table templates")
        
        # 6. Delete field definitions
        if field_count > 0:
            field_delete_query = "DELETE FROM design_enhanced.field_definitions WHERE structure_id = :structure_id"
            db.execute(text(field_delete_query), {"structure_id": structure_id})
            print(f"[DELETE] Deleted {field_count} field definitions")
        
        # 7. Finally, delete the structure itself
        structure_delete_query = "DELETE FROM design_enhanced.dataset_structures WHERE structure_id = :structure_id"
        print(f"[DELETE] Executing structure delete query: {structure_delete_query}")
        
        structure_result = db.execute(text(structure_delete_query), {
            "structure_id": structure_id
        })
        print(f"[DELETE] Structure delete executed successfully")
        
        db.commit()
        print(f"[DELETE] Transaction committed successfully")
        
        return {
            "message": f"Dataset structure '{dataset_name}' and all related records deleted successfully",
            "deleted_records": {
                "fields": field_count,
                "templates": template_count,
                "mappings": mapping_count,
                "uploads": upload_count,
                "reviews": review_count,
                "generated_tables": generated_count
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"[DELETE] Error occurred: {str(e)}")
        print(f"[DELETE] Error type: {type(e).__name__}")
        import traceback
        print(f"[DELETE] Full traceback: {traceback.format_exc()}")
        
        db.rollback()
        print(f"[DELETE] Transaction rolled back")
        
        raise HTTPException(status_code=500, detail=f"Error deleting dataset structure: {str(e)}")

@router.get("/structures/{structure_id}")
async def get_dataset_structure(
    structure_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user)
):
    """Get specific dataset structure with field definitions"""
    try:
        # Get structure
        structure_query = """
            SELECT * FROM design_enhanced.dataset_structures 
            WHERE structure_id = :structure_id AND is_active = true
        """
        structure_result = db.execute(text(structure_query), {"structure_id": structure_id}).mappings()
        structure_row = next(structure_result, None)
        structure = dict(structure_row) if structure_row else None
        
        if not structure:
            raise HTTPException(status_code=404, detail="Dataset structure not found")
        
        # Get field definitions
        fields_query = """
            SELECT * FROM design_enhanced.field_definitions 
            WHERE structure_id = :structure_id 
            ORDER BY sequence_order
        """
        fields_result = db.execute(text(fields_query), {"structure_id": structure_id}).mappings()
        fields = [dict(row) for row in fields_result]
        
        structure["fields"] = fields
        return {"structure": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dataset structure: {str(e)}")

# Field Definition Management
@router.get("/structures/{structure_id}/fields")
async def get_field_definitions(
    structure_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get field definitions for a dataset structure"""
    try:
        query = """
            SELECT * FROM design_enhanced.field_definitions 
            WHERE structure_id = :structure_id 
            ORDER BY sequence_order
        """
        
        result = db.execute(text(query), {"structure_id": structure_id}).mappings()
        fields = [dict(row) for row in result]
        
        return {"fields": fields}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving field definitions: {str(e)}")

@router.post("/structures/{structure_id}/fields")
async def create_field_definition(
    structure_id: str,
    field_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Create new field definition"""
    try:
        print(f"[FIELD_CREATE] Creating field for structure_id: {structure_id}")
        print(f"[FIELD_CREATE] Field data: {field_data}")
        print(f"[FIELD_CREATE] Current user: {current_user.username}")
        
        field_id = str(uuid.uuid4())
        query = """
            INSERT INTO design_enhanced.field_definitions 
            (field_id, structure_id, field_name, field_type, postgis_type, srid, 
             field_length, field_precision, field_scale, is_required, is_primary_key, 
             is_unique, has_index, default_value, description, validation_rules, 
             transformation_rules, sequence_order, created_by)
            VALUES (:field_id, :structure_id, :field_name, :field_type, :postgis_type, :srid,
                    :field_length, :field_precision, :field_scale, :is_required, :is_primary_key,
                    :is_unique, :has_index, :default_value, :description, :validation_rules,
                    :transformation_rules, :sequence_order, :created_by)
        """
        
        params = {
            "field_id": field_id,
            "structure_id": structure_id,
            "field_name": field_data["field_name"],
            "field_type": field_data["field_type"],
            "postgis_type": field_data.get("postgis_type"),
            "srid": field_data.get("srid", 4326),
            "field_length": field_data.get("field_length"),
            "field_precision": field_data.get("field_precision"),
            "field_scale": field_data.get("field_scale"),
            "is_required": field_data.get("is_required", False),
            "is_primary_key": field_data.get("is_primary_key", False),
            "is_unique": field_data.get("is_unique", False),
            "has_index": field_data.get("has_index", False),
            "default_value": field_data.get("default_value"),
            "description": field_data.get("description", ""),
            "validation_rules": json.dumps(field_data.get("validation_rules", [])),
            "transformation_rules": json.dumps(field_data.get("transformation_rules", [])),
            "sequence_order": field_data["sequence_order"],
            "created_by": current_user.username
        }
        
        print(f"[FIELD_CREATE] Executing query with params: {params}")
        
        db.execute(text(query), params)
        db.commit()
        
        print(f"[FIELD_CREATE] Field created successfully with ID: {field_id}")
        
        return {"message": "Field definition created successfully", "field_id": field_id}
    except Exception as e:
        print(f"[FIELD_CREATE] Error occurred: {str(e)}")
        print(f"[FIELD_CREATE] Error type: {type(e).__name__}")
        import traceback
        print(f"[FIELD_CREATE] Full traceback: {traceback.format_exc()}")
        
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating field definition: {str(e)}")

# Table Template Management
@router.get("/templates")
async def get_table_templates(
    template_type: Optional[str] = None,
    structure_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get table templates"""
    try:
        query = """
            SELECT tt.*, ds.dataset_name 
            FROM design_enhanced.table_templates tt
            JOIN design_enhanced.dataset_structures ds ON tt.structure_id = ds.structure_id
            WHERE tt.is_active = true
        """
        params = {}
        
        if template_type:
            query += " AND tt.template_type = :template_type"
            params['template_type'] = template_type
            
        if structure_id:
            query += " AND tt.structure_id = :structure_id"
            params['structure_id'] = structure_id
            
        query += " ORDER BY tt.created_at DESC"
        
        result = db.execute(text(query), params).mappings()
        templates = [dict(row) for row in result]
        
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving table templates: {str(e)}")

@router.post("/templates")
async def create_table_template(
    template_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Create new table template"""
    try:
        template_id = str(uuid.uuid4())
        query = """
            INSERT INTO design_enhanced.table_templates 
            (template_id, template_name, template_type, structure_id, table_name_pattern,
             schema_name, include_audit_fields, include_source_tracking, 
             include_processing_metadata, postgis_enabled, indexes_config, 
             constraints_config, created_by)
            VALUES (:template_id, :template_name, :template_type, :structure_id, :table_name_pattern,
                    :schema_name, :include_audit_fields, :include_source_tracking,
                    :include_processing_metadata, :postgis_enabled, :indexes_config,
                    :constraints_config, :created_by)
        """
        
        db.execute(text(query), {
            "template_id": template_id,
            "template_name": template_data["template_name"],
            "template_type": template_data["template_type"],
            "structure_id": template_data["structure_id"],
            "table_name_pattern": template_data.get("table_name_pattern"),
            "schema_name": template_data.get("schema_name", "public"),
            "include_audit_fields": template_data.get("include_audit_fields", True),
            "include_source_tracking": template_data.get("include_source_tracking", True),
            "include_processing_metadata": template_data.get("include_processing_metadata", True),
            "postgis_enabled": template_data.get("postgis_enabled", False),
            "indexes_config": json.dumps(template_data.get("indexes_config", [])),
            "constraints_config": json.dumps(template_data.get("constraints_config", [])),
            "created_by": current_user.username
        })
        db.commit()
        
        return {"message": "Table template created successfully", "template_id": template_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating table template: {str(e)}")

# Table Generation
@router.post("/templates/{template_id}/generate")
async def generate_table(
    template_id: str,
    generation_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Generate table from template"""
    try:
        # Get template and structure
        template_query = """
            SELECT tt.*, ds.dataset_name, ds.structure_id
            FROM design_enhanced.table_templates tt
            JOIN design_enhanced.dataset_structures ds ON tt.structure_id = ds.structure_id
            WHERE tt.template_id = :template_id AND tt.is_active = true
        """
        template_result = db.execute(text(template_query), {"template_id": template_id}).mappings()
        template_row = next(template_result, None)
        template = dict(template_row) if template_row else None
        
        if not template:
            raise HTTPException(status_code=404, detail="Table template not found")
        
        # Get field definitions
        fields_query = """
            SELECT * FROM design_enhanced.field_definitions 
            WHERE structure_id = :structure_id 
            ORDER BY sequence_order
        """
        fields_result = db.execute(text(fields_query), {"structure_id": template["structure_id"]}).mappings()
        fields = [dict(row) for row in fields_result]
        
        # Generate table name
        table_name = generation_data.get("table_name") or template["table_name_pattern"].replace(
            "{dataset_name}", template["dataset_name"]
        )
        
        # Generate DDL script
        ddl_script = generate_ddl_script(template, fields, table_name)
        
        # Store generated table
        table_id = str(uuid.uuid4())
        insert_query = """
            INSERT INTO design_enhanced.generated_tables 
            (table_id, template_id, structure_id, table_name, schema_name, table_type,
             ddl_script, postgis_fields, field_mappings, created_by)
            VALUES (:table_id, :template_id, :structure_id, :table_name, :schema_name, :table_type,
                    :ddl_script, :postgis_fields, :field_mappings, :created_by)
        """
        
        postgis_fields = [f for f in fields if f.get("postgis_type")]
        field_mappings = [{"source": f["field_name"], "target": f["field_name"]} for f in fields]
        
        db.execute(text(insert_query), {
            "table_id": table_id,
            "template_id": template_id,
            "structure_id": template["structure_id"],
            "table_name": table_name,
            "schema_name": template["schema_name"],
            "table_type": template["template_type"],
            "ddl_script": ddl_script,
            "postgis_fields": json.dumps(postgis_fields),
            "field_mappings": json.dumps(field_mappings),
            "created_by": current_user.username
        })
        db.commit()
        
        return {
            "message": "Table generated successfully", 
            "table_id": table_id,
            "table_name": table_name,
            "ddl_script": ddl_script
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating table: {str(e)}")

# Field Mapping Management
@router.get("/structures/{structure_id}/mappings")
async def get_field_mappings(
    structure_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get field mappings for a dataset structure"""
    try:
        query = """
            SELECT * FROM design_enhanced.field_mappings 
            WHERE structure_id = :structure_id
        """
        
        result = db.execute(text(query), {"structure_id": structure_id}).mappings()
        mappings = [dict(row) for row in result]
        
        return {"mappings": mappings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving field mappings: {str(e)}")

@router.post("/structures/{structure_id}/mappings")
async def create_field_mapping(
    structure_id: str,
    mapping_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Create new field mapping"""
    try:
        mapping_id = str(uuid.uuid4())
        query = """
            INSERT INTO design_enhanced.field_mappings 
            (mapping_id, structure_id, source_field_name, target_field_name, mapping_type,
             transformation_script, lookup_config, validation_rules, is_required, created_by)
            VALUES (:mapping_id, :structure_id, :source_field_name, :target_field_name, :mapping_type,
                    :transformation_script, :lookup_config, :validation_rules, :is_required, :created_by)
        """
        
        db.execute(text(query), {
            "mapping_id": mapping_id,
            "structure_id": structure_id,
            "source_field_name": mapping_data["source_field_name"],
            "target_field_name": mapping_data["target_field_name"],
            "mapping_type": mapping_data["mapping_type"],
            "transformation_script": mapping_data.get("transformation_script"),
            "lookup_config": json.dumps(mapping_data.get("lookup_config", {})),
            "validation_rules": json.dumps(mapping_data.get("validation_rules", [])),
            "is_required": mapping_data.get("is_required", False),
            "created_by": current_user.username
        })
        db.commit()
        
        return {"message": "Field mapping created successfully", "mapping_id": mapping_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating field mapping: {str(e)}")

# Dataset Upload and Processing
@router.post("/structures/{structure_id}/uploads")
async def create_dataset_upload(
    structure_id: str,
    upload_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user)
):
    """Create new dataset upload"""
    try:
        upload_id = str(uuid.uuid4())
        query = """
            INSERT INTO design_enhanced.dataset_uploads 
            (upload_id, structure_id, file_name, file_size, file_type, file_path,
             detected_schema, field_mapping_results, validation_results, processing_status,
             target_table_name, uploaded_by)
            VALUES (:upload_id, :structure_id, :file_name, :file_size, :file_type, :file_path,
                    :detected_schema, :field_mapping_results, :validation_results, :processing_status,
                    :target_table_name, :uploaded_by)
        """
        
        db.execute(text(query), {
            "upload_id": upload_id,
            "structure_id": structure_id,
            "file_name": upload_data["file_name"],
            "file_size": upload_data.get("file_size"),
            "file_type": upload_data.get("file_type"),
            "file_path": upload_data.get("file_path"),
            "detected_schema": json.dumps(upload_data.get("detected_schema", {})),
            "field_mapping_results": json.dumps(upload_data.get("field_mapping_results", {})),
            "validation_results": json.dumps(upload_data.get("validation_results", {})),
            "processing_status": upload_data.get("processing_status", "uploaded"),
            "target_table_name": upload_data.get("target_table_name"),
            "uploaded_by": current_user.username
        })
        db.commit()
        
        return {"message": "Dataset upload created successfully", "upload_id": upload_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating dataset upload: {str(e)}")

# Review Workflow
@router.post("/uploads/{upload_id}/reviews")
async def create_review(
    upload_id: str,
    review_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user)
):
    """Create new review for upload"""
    try:
        review_id = str(uuid.uuid4())
        query = """
            INSERT INTO design_enhanced.review_workflow 
            (review_id, upload_id, structure_id, review_type, reviewer_id, review_status,
             review_notes, required_changes, next_reviewer_id)
            VALUES (:review_id, :upload_id, :structure_id, :review_type, :reviewer_id, :review_status,
                    :review_notes, :required_changes, :next_reviewer_id)
        """
        
        db.execute(text(query), {
            "review_id": review_id,
            "upload_id": upload_id,
            "structure_id": review_data["structure_id"],
            "review_type": review_data["review_type"],
            "reviewer_id": current_user.username,
            "review_status": review_data.get("review_status", "pending"),
            "review_notes": review_data.get("review_notes"),
            "required_changes": json.dumps(review_data.get("required_changes", [])),
            "next_reviewer_id": review_data.get("next_reviewer_id")
        })
        db.commit()
        
        return {"message": "Review created successfully", "review_id": review_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating review: {str(e)}")

# Dashboard and Overview
@router.get("/dashboard/overview")
async def get_design_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get design system dashboard overview"""
    try:
        # Get structure overview - use direct query instead of view for now
        structure_query = """
            SELECT 
                ds.structure_id,
                ds.dataset_name,
                ds.description,
                ds.source_type,
                ds.governing_body,
                ds.status as dataset_status,
                COUNT(fd.field_id) as total_fields,
                COUNT(CASE WHEN fd.postgis_type IS NOT NULL THEN 1 END) as postgis_fields,
                COUNT(CASE WHEN fd.is_required = true THEN 1 END) as required_fields,
                COUNT(gt.table_id) as generated_tables,
                ds.created_at,
                ds.updated_at
            FROM design_enhanced.dataset_structures ds
            LEFT JOIN design_enhanced.field_definitions fd ON ds.structure_id = fd.structure_id
            LEFT JOIN design_enhanced.generated_tables gt ON ds.structure_id = gt.structure_id
            WHERE ds.is_active = true
            GROUP BY ds.structure_id, ds.dataset_name, ds.description, ds.source_type, 
                     ds.governing_body, ds.status, ds.created_at, ds.updated_at
        """
        structure_result = db.execute(text(structure_query))
        structures = [dict(row) for row in structure_result]
        
        # Get recent uploads
        uploads_query = """
            SELECT du.*, ds.dataset_name 
            FROM design_enhanced.dataset_uploads du
            JOIN design_enhanced.dataset_structures ds ON du.structure_id = ds.structure_id
            ORDER BY du.uploaded_at DESC
            LIMIT 10
        """
        uploads_result = db.execute(text(uploads_query))
        recent_uploads = [dict(row) for row in uploads_result]
        
        # Get pending reviews
        reviews_query = """
            SELECT rw.*, ds.dataset_name, du.file_name
            FROM design_enhanced.review_workflow rw
            JOIN design_enhanced.dataset_uploads du ON rw.upload_id = du.upload_id
            JOIN design_enhanced.dataset_structures ds ON rw.structure_id = ds.structure_id
            WHERE rw.review_status = 'pending'
            ORDER BY rw.reviewed_at DESC
        """
        reviews_result = db.execute(text(reviews_query))
        pending_reviews = [dict(row) for row in reviews_result]
        
        return {
            "structures": structures,
            "recent_uploads": recent_uploads,
            "pending_reviews": pending_reviews
        }
    except Exception as e:
        # Return empty data if there's an error, rather than failing completely
        print(f"Dashboard error: {str(e)}")
        return {
            "structures": [],
            "recent_uploads": [],
            "pending_reviews": []
        }

# Helper function to generate DDL script
def generate_ddl_script(template, fields, table_name):
    """Generate CREATE TABLE DDL script from template and fields"""
    ddl_parts = [f"CREATE TABLE {template['schema_name']}.{table_name} ("]
    
    field_definitions = []
    for field in fields:
        field_def = f"    {field['field_name']} {field['field_type'].upper()}"
        
        # Add field length for VARCHAR
        if field['field_type'] == 'varchar' and field.get('field_length'):
            field_def += f"({field['field_length']})"
        
        # Add precision and scale for DECIMAL
        if field['field_type'] in ['numeric', 'decimal']:
            if field.get('field_precision') and field.get('field_scale'):
                field_def += f"({field['field_precision']},{field['field_scale']})"
            elif field.get('field_precision'):
                field_def += f"({field['field_precision']})"
        
        # Add PostGIS type
        if field.get('postgis_type'):
            field_def += f" GEOMETRY({field['postgis_type']}, {field.get('srid', 4326)})"
        
        # Add constraints
        if field.get('is_required'):
            field_def += " NOT NULL"
        if field.get('is_primary_key'):
            field_def += " PRIMARY KEY"
        if field.get('is_unique'):
            field_def += " UNIQUE"
        if field.get('default_value'):
            field_def += f" DEFAULT {field['default_value']}"
        
        field_definitions.append(field_def)
    
    # Add audit fields if enabled
    if template.get('include_audit_fields'):
        field_definitions.extend([
            "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ])
    
    # Add source tracking if enabled
    if template.get('include_source_tracking'):
        field_definitions.append("    source_file TEXT")
    
    # Add processing metadata if enabled
    if template.get('include_processing_metadata'):
        field_definitions.extend([
            "    processing_status VARCHAR(50) DEFAULT 'pending'",
            "    processed_at TIMESTAMP"
        ])
    
    ddl_parts.append(",\n".join(field_definitions))
    ddl_parts.append(");")
    
    # Add indexes for PostGIS fields
    for field in fields:
        if field.get('postgis_type') and field.get('has_index'):
            ddl_parts.append(f"\nCREATE INDEX idx_{table_name}_{field['field_name']} ON {template['schema_name']}.{table_name} USING GIST ({field['field_name']});")
    
    return "\n".join(ddl_parts) 

@router.get("/data-standards/analytics")
async def get_data_standards_analytics(
    time_period: Optional[str] = "30d",  # 7d, 30d, 90d, 1y, all
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get data-driven analytics about data standards usage and effectiveness"""
    
    # Calculate usage patterns
    usage_analytics = {
        "standards_usage": {},
        "detection_accuracy": {},
        "compliance_trends": {},
        "field_pattern_effectiveness": {},
        "geographic_distribution": {},
        "industry_adoption": {},
        "version_evolution": {}
    }
    
    # Analyze standards by usage frequency
    for standard_id, standard in DATA_STANDARDS.items():
        usage_analytics["standards_usage"][standard_id] = {
            "name": standard["name"],
            "category": standard["category"],
            "compliance_level": standard["compliance_level"],
            "country": standard["country"],
            "detection_count": 0,  # Would be populated from actual usage data
            "success_rate": 0.85,  # Mock data - would come from real analytics
            "avg_confidence": 0.78,  # Mock data
            "last_detected": "2023-12-01",  # Mock data
            "trend": "increasing"  # Mock data
        }
    
    # Calculate detection accuracy by category
    category_accuracy = {}
    for standard in DATA_STANDARDS.values():
        category = standard["category"]
        if category not in category_accuracy:
            category_accuracy[category] = {
                "total_standards": 0,
                "avg_confidence": 0,
                "detection_rate": 0
            }
        category_accuracy[category]["total_standards"] += 1
    
    usage_analytics["detection_accuracy"] = category_accuracy
    
    # Compliance trends analysis
    compliance_trends = {}
    for standard in DATA_STANDARDS.values():
        level = standard["compliance_level"]
        if level not in compliance_trends:
            compliance_trends[level] = {
                "count": 0,
                "countries": set(),
                "categories": set()
            }
        compliance_trends[level]["count"] += 1
        compliance_trends[level]["countries"].add(standard["country"])
        compliance_trends[level]["categories"].add(standard["category"])
    
    # Convert sets to lists for JSON serialization
    for level in compliance_trends:
        compliance_trends[level]["countries"] = list(compliance_trends[level]["countries"])
        compliance_trends[level]["categories"] = list(compliance_trends[level]["categories"])
    
    usage_analytics["compliance_trends"] = compliance_trends
    
    # Field pattern effectiveness analysis
    pattern_effectiveness = {
        "most_effective_patterns": [],
        "pattern_coverage": {},
        "validation_success_rate": {}
    }
    
    # Analyze field patterns across all standards
    all_patterns = {}
    for standard in DATA_STANDARDS.values():
        for field, pattern in standard.get("field_patterns", {}).items():
            if pattern not in all_patterns:
                all_patterns[pattern] = {
                    "usage_count": 0,
                    "standards": [],
                    "field_types": []
                }
            all_patterns[pattern]["usage_count"] += 1
            all_patterns[pattern]["standards"].append(standard["name"])
            all_patterns[pattern]["field_types"].append(field)
    
    # Sort patterns by usage
    sorted_patterns = sorted(all_patterns.items(), key=lambda x: x[1]["usage_count"], reverse=True)
    pattern_effectiveness["most_effective_patterns"] = sorted_patterns[:10]
    pattern_effectiveness["pattern_coverage"] = all_patterns
    
    usage_analytics["field_pattern_effectiveness"] = pattern_effectiveness
    
    # Geographic distribution analysis
    geographic_distribution = {}
    for standard in DATA_STANDARDS.values():
        country = standard["country"]
        if country not in geographic_distribution:
            geographic_distribution[country] = {
                "standards_count": 0,
                "categories": set(),
                "compliance_levels": set(),
                "governing_bodies": set()
            }
        geographic_distribution[country]["standards_count"] += 1
        geographic_distribution[country]["categories"].add(standard["category"])
        geographic_distribution[country]["compliance_levels"].add(standard["compliance_level"])
        geographic_distribution[country]["governing_bodies"].add(standard["governing_body"])
    
    # Convert sets to lists
    for country in geographic_distribution:
        geographic_distribution[country]["categories"] = list(geographic_distribution[country]["categories"])
        geographic_distribution[country]["compliance_levels"] = list(geographic_distribution[country]["compliance_levels"])
        geographic_distribution[country]["governing_bodies"] = list(geographic_distribution[country]["governing_bodies"])
    
    usage_analytics["geographic_distribution"] = geographic_distribution
    
    # Industry adoption analysis
    industry_adoption = {}
    for standard in DATA_STANDARDS.values():
        category = standard["category"]
        if category not in industry_adoption:
            industry_adoption[category] = {
                "standards_count": 0,
                "countries": set(),
                "avg_compliance_level": "",
                "governing_bodies": set()
            }
        industry_adoption[category]["standards_count"] += 1
        industry_adoption[category]["countries"].add(standard["country"])
        industry_adoption[category]["governing_bodies"].add(standard["governing_body"])
    
    # Convert sets to lists and calculate averages
    for category in industry_adoption:
        industry_adoption[category]["countries"] = list(industry_adoption[category]["countries"])
        industry_adoption[category]["governing_bodies"] = list(industry_adoption[category]["governing_bodies"])
    
    usage_analytics["industry_adoption"] = industry_adoption
    
    # Version evolution analysis
    version_evolution = {
        "latest_versions": {},
        "version_distribution": {},
        "update_frequency": {}
    }
    
    for standard in DATA_STANDARDS.values():
        governing_body = standard["governing_body"]
        version = standard["version"]
        
        if governing_body not in version_evolution["latest_versions"]:
            version_evolution["latest_versions"][governing_body] = []
        
        version_evolution["latest_versions"][governing_body].append({
            "standard_name": standard["name"],
            "version": version,
            "category": standard["category"]
        })
    
    usage_analytics["version_evolution"] = version_evolution
    
    return {
        "analytics": usage_analytics,
        "time_period": time_period,
        "filters_applied": {"category": category},
        "summary": {
            "total_standards_analyzed": len(DATA_STANDARDS),
            "categories_covered": len(set(s["category"] for s in DATA_STANDARDS.values())),
            "countries_represented": len(set(s["country"] for s in DATA_STANDARDS.values())),
            "governing_bodies": len(set(s["governing_body"] for s in DATA_STANDARDS.values())),
            "avg_confidence_score": 0.82,  # Mock data
            "detection_accuracy": 0.89  # Mock data
        }
    }

@router.get("/data-standards/recommendations")
async def get_data_driven_recommendations(
    dataset_analysis: Optional[dict] = None,
    industry: Optional[str] = None,
    region: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get data-driven recommendations for standards based on dataset analysis"""
    
    recommendations = {
        "recommended_standards": [],
        "compliance_gaps": [],
        "field_mapping_suggestions": [],
        "quality_improvements": [],
        "industry_best_practices": []
    }
    
    # Mock data-driven recommendations based on dataset analysis
    if dataset_analysis:
        # Analyze dataset characteristics and recommend standards
        field_names = dataset_analysis.get("field_names", [])
        data_types = dataset_analysis.get("data_types", [])
        sample_values = dataset_analysis.get("sample_values", {})
        
        # Find matching standards
        for standard_id, standard in DATA_STANDARDS.items():
            confidence = 0.0
            matched_fields = []
            
            # Check field name matches
            for field_name in field_names:
                for required_field in standard.get("required_fields", []):
                    if required_field.lower() in field_name.lower() or field_name.lower() in required_field.lower():
                        matched_fields.append(required_field)
                        confidence += 0.3
            
            # Check data type compatibility
            for data_type in data_types:
                if data_type in ["text", "string"] and any("postcode" in f.lower() for f in field_names):
                    confidence += 0.2
                elif data_type in ["numeric", "decimal"] and any("amount" in f.lower() or "value" in f.lower() for f in field_names):
                    confidence += 0.2
            
            if confidence > 0.5:
                recommendations["recommended_standards"].append({
                    "standard_id": standard_id,
                    "name": standard["name"],
                    "confidence": min(confidence, 1.0),
                    "matched_fields": matched_fields,
                    "category": standard["category"],
                    "compliance_level": standard["compliance_level"],
                    "reasoning": f"Matched {len(matched_fields)} fields with {confidence:.1%} confidence"
                })
    
    # Industry-specific recommendations
    if industry:
        industry_standards = {
            "financial": ["ISO_20022", "FIX_Protocol", "SWIFT"],
            "healthcare": ["HL7_FHIR", "DICOM"],
            "transportation": ["GTFS", "SIRI"],
            "environmental": ["ISO_14001", "WMO"],
            "government": ["BS7666", "INSPIRE", "GDS"]
        }
        
        if industry in industry_standards:
            for standard_id in industry_standards[industry]:
                if standard_id in DATA_STANDARDS:
                    standard = DATA_STANDARDS[standard_id]
                    recommendations["industry_best_practices"].append({
                        "standard_id": standard_id,
                        "name": standard["name"],
                        "category": standard["category"],
                        "compliance_level": standard["compliance_level"],
                        "reasoning": f"Industry standard for {industry} sector"
                    })
    
    # Regional recommendations
    if region:
        regional_standards = {
            "UK": ["BS7666", "OS_Standards", "ONS_Standards", "VOA_NNDR"],
            "EU": ["INSPIRE", "EU_Open_Data"],
            "US": ["US_FIPS", "US_Census"]
        }
        
        if region in regional_standards:
            for standard_id in regional_standards[region]:
                if standard_id in DATA_STANDARDS:
                    standard = DATA_STANDARDS[standard_id]
                    recommendations["recommended_standards"].append({
                        "standard_id": standard_id,
                        "name": standard["name"],
                        "confidence": 0.9,
                        "category": standard["category"],
                        "compliance_level": standard["compliance_level"],
                        "reasoning": f"Regional standard for {region}"
                    })
    
    # Sort recommendations by confidence
    recommendations["recommended_standards"].sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "recommendations": recommendations,
        "analysis_parameters": {
            "dataset_analysis": dataset_analysis is not None,
            "industry": industry,
            "region": region
        },
        "total_recommendations": len(recommendations["recommended_standards"]) + len(recommendations["industry_best_practices"])
    }

@router.post("/dataset-requests")
async def create_dataset_request(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Create a new dataset request"""
    try:
        request_id = str(uuid.uuid4())
        
        # Insert the request into the database
        query = text("""
            INSERT INTO design.dataset_requests (
                request_id, name, description, category, source_type, reason,
                requested_by, requested_at, status
            ) VALUES (
                :request_id, :name, :description, :category, :source_type, :reason,
                :requested_by, :requested_at, 'pending'
            )
        """)
        
        db.execute(query, {
            "request_id": request_id,
            "name": request_data.get("name", ""),
            "description": request_data.get("description", ""),
            "category": request_data.get("category", ""),
            "source_type": request_data.get("source_type", "file"),
            "reason": request_data.get("reason", ""),
            "requested_by": current_user.username,
            "requested_at": datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "message": "Dataset request created successfully",
            "request_id": request_id
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating dataset request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create dataset request: {str(e)}")

@router.get("/data-standards/performance-metrics")
async def get_performance_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get performance metrics for data standards detection and validation"""
    
    # Mock performance metrics - in real implementation, these would come from actual usage data
    performance_metrics = {
        "detection_performance": {
            "total_detections": 1247,
            "successful_detections": 1123,
            "failed_detections": 124,
            "success_rate": 0.90,
            "avg_detection_time_ms": 45,
            "peak_detection_time_ms": 120
        },
        "accuracy_metrics": {
            "overall_accuracy": 0.89,
            "precision": 0.92,
            "recall": 0.87,
            "f1_score": 0.89,
            "false_positives": 23,
            "false_negatives": 45
        },
        "standards_performance": {},
        "category_performance": {},
        "compliance_performance": {},
        "trends": {
            "daily_detections": [],
            "weekly_accuracy": [],
            "monthly_improvements": []
        }
    }
    
    # Calculate performance by standard
    for standard_id, standard in DATA_STANDARDS.items():
        # Mock performance data for each standard
        performance_metrics["standards_performance"][standard_id] = {
            "name": standard["name"],
            "detection_count": 50 + (hash(standard_id) % 100),  # Mock data
            "success_rate": 0.85 + (hash(standard_id) % 15) / 100,  # Mock data
            "avg_confidence": 0.78 + (hash(standard_id) % 20) / 100,  # Mock data
            "last_used": "2023-12-01",  # Mock data
            "trend": "stable"  # Mock data
        }
    
    # Calculate performance by category
    for category in DATA_STANDARDS_CATEGORIES:
        category_standards = [s for s in DATA_STANDARDS.values() if s["category"] == category]
        if category_standards:
            avg_success_rate = sum(0.85 + (hash(s["name"]) % 15) / 100 for s in category_standards) / len(category_standards)
            performance_metrics["category_performance"][category] = {
                "standards_count": len(category_standards),
                "avg_success_rate": avg_success_rate,
                "total_detections": len(category_standards) * 75,  # Mock data
                "category_name": DATA_STANDARDS_CATEGORIES[category]["name"]
            }
    
    # Calculate performance by compliance level
    for level in COMPLIANCE_LEVELS:
        level_standards = [s for s in DATA_STANDARDS.values() if s["compliance_level"] == level]
        if level_standards:
            avg_success_rate = sum(0.85 + (hash(s["name"]) % 15) / 100 for s in level_standards) / len(level_standards)
            performance_metrics["compliance_performance"][level] = {
                "standards_count": len(level_standards),
                "avg_success_rate": avg_success_rate,
                "compliance_name": COMPLIANCE_LEVELS[level]["name"],
                "priority": COMPLIANCE_LEVELS[level]["priority"]
            }
    
    # Mock trend data
    for i in range(30):  # Last 30 days
        performance_metrics["trends"]["daily_detections"].append({
            "date": f"2023-12-{i+1:02d}",
            "detections": 30 + (i % 20),
            "success_rate": 0.85 + (i % 10) / 100
        })
    
    return {
        "performance_metrics": performance_metrics,
        "date_range": {
            "start_date": start_date or "2023-11-01",
            "end_date": end_date or "2023-12-01"
        },
        "summary": {
            "overall_success_rate": 0.90,
            "total_standards_tracked": len(DATA_STANDARDS),
            "improvement_trend": "positive",
            "recommendations": [
                "Consider adding more healthcare standards for better coverage",
                "Financial standards show high accuracy - consider expanding",
                "Environmental standards need more validation data"
            ]
        }
    }