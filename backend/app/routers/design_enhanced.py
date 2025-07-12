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
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/api/design-enhanced", tags=["design-enhanced"])

# Data Standards Database
DATA_STANDARDS = {
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
        "country": "UK"
    },
    "INSPIRE": {
        "name": "INSPIRE Directive - European spatial data infrastructure",
        "description": "European standard for spatial data infrastructure",
        "required_fields": ["geometry", "coordinate_reference_system"],
        "field_patterns": {
            "geometry": r"(point|line|polygon|multipoint|multiline|multipolygon)",
            "coordinate_reference_system": r"(EPSG|CRS|SRID)"
        },
        "governing_body": "European Commission",
        "country": "EU"
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
        "country": "UK"
    },
    "GDS": {
        "name": "Government Digital Service Standards",
        "description": "UK government data standards",
        "required_fields": ["open_data", "machine_readable", "linked_data"],
        "field_patterns": {
            "open_data": r"(open|public|accessible)",
            "machine_readable": r"(csv|json|xml|rdf)"
        },
        "governing_body": "UK Government",
        "country": "UK"
    },
    "SDMX": {
        "name": "Statistical Data and Metadata eXchange",
        "description": "International standard for statistical data",
        "required_fields": ["statistical_concept", "measure", "dimension"],
        "field_patterns": {
            "statistical_concept": r"(population|employment|economic|social)",
            "measure": r"(count|value|percentage|rate)"
        },
        "governing_body": "UNSD",
        "country": "International"
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
        "country": "International"
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
        "country": "UK"
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
        "country": "UK"
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
        has_header = True  # Assume first row is header
        
        # Check if first row looks like header (contains text, not just numbers)
        first_row = parsed_data[0]
        text_fields = sum(1 for field in first_row if not field.replace('.', '').replace('-', '').isdigit())
        has_header = text_fields > field_count / 2
        
        # Analyze field types
        field_analysis = []
        start_row = 1 if has_header else 0
        
        for i in range(field_count):
            field_values = [row[i] for row in parsed_data[start_row:] if i < len(row)]
            field_analysis.append(analyze_field_type(field_values, i))
        
        return {
            "format": "csv",
            "encoding": encoding,
            "delimiter": best_delimiter,
            "has_header": has_header,
            "field_count": field_count,
            "sample_rows": len(parsed_data),
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
        return {"type": "unknown", "confidence": 0.0}
    
    # Remove empty values
    non_empty_values = [v.strip() for v in values if v.strip()]
    
    if not non_empty_values:
        return {"type": "empty", "confidence": 0.0}
    
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
        # Test integer
        if value.replace('-', '').isdigit():
            type_scores["integer"] += 1
        
        # Test decimal
        try:
            float(value)
            if '.' in value:
                type_scores["decimal"] += 1
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
        
        # Test boolean
        if value.lower() in ['true', 'false', 'yes', 'no', '1', '0']:
            type_scores["boolean"] += 1
        
        # Test UK postcode
        if re.match(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$', value.upper()):
            type_scores["postcode"] += 1
        
        # Test UPRN (12-digit number)
        if re.match(r'^\d{12}$', value):
            type_scores["uprn"] += 1
        
        # Test coordinates
        try:
            coord = float(value)
            if -180 <= coord <= 180:  # Likely longitude
                type_scores["coordinate"] += 1
            elif -90 <= coord <= 90:  # Likely latitude
                type_scores["coordinate"] += 1
        except:
            pass
        
        # Default to text
        type_scores["text"] += 1
    
    # Find best type
    best_type = max(type_scores.items(), key=lambda x: x[1])[0]
    confidence = type_scores[best_type] / len(non_empty_values)
    
    return {
        "type": best_type,
        "confidence": confidence,
        "sample_values": non_empty_values[:5],
        "unique_count": len(set(non_empty_values))
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
    """Identify which data standards the file might follow"""
    filename = filename or 'uploaded_file'
    identified_standards = []
    
    # Extract field names and types
    field_names = [field.get("name", f"field_{i}") for i, field in enumerate(field_analysis)]
    field_types = [field.get("type", "unknown") for field in field_analysis]
    
    # Check each standard
    for standard_id, standard in DATA_STANDARDS.items():
        score = 0
        matched_fields = []
        
        # Check required fields
        for required_field in standard["required_fields"]:
            for i, field_name in enumerate(field_names):
                if required_field.lower() in field_name.lower():
                    score += 2
                    matched_fields.append(field_name)
                    break
        
        # Check field patterns
        for pattern_name, pattern in standard["field_patterns"].items():
            for i, field_name in enumerate(field_names):
                if re.search(pattern, field_name, re.IGNORECASE):
                    score += 1
                    matched_fields.append(field_name)
                    break
        
        # Check filename patterns
        if standard_id in filename.upper():
            score += 1
        
        # Calculate confidence
        confidence = min(score / len(standard["required_fields"]), 1.0)
        
        if confidence > 0.3:  # Only include if reasonably confident
            identified_standards.append({
                "standard_id": standard_id,
                "name": standard["name"],
                "description": standard["description"],
                "governing_body": standard["governing_body"],
                "country": standard["country"],
                "confidence": confidence,
                "matched_fields": matched_fields,
                "requirements": standard["required_fields"]
            })
    
    # Sort by confidence
    identified_standards.sort(key=lambda x: x["confidence"], reverse=True)
    return identified_standards

@router.post("/ai/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    """AI-powered file analysis to detect format, structure, and data standards"""
    try:
        # Read file content
        content = await file.read()
        
        # Detect file type
        filename = file.filename or "uploaded_file"
        file_extension = Path(filename).suffix.lower()
        mime_type = file.content_type
        
        # Analyze based on file type
        if file_extension == '.csv' or mime_type == 'text/csv':
            analysis = detect_csv_format(content, filename)
        elif file_extension == '.json' or mime_type == 'application/json':
            analysis = detect_json_format(content, filename)
        elif file_extension in ['.xml', '.gml'] or mime_type in ['application/xml', 'text/xml']:
            analysis = detect_xml_format(content, filename)
        elif file_extension == '.zip' or mime_type == 'application/zip':
            analysis = detect_zip_format(content, filename)
        else:
            # Try to detect format from content
            if content.startswith(b'{') or content.startswith(b'['):
                analysis = detect_json_format(content, filename)
            elif content.startswith(b'<'):
                analysis = detect_xml_format(content, filename)
            else:
                # Assume CSV and try to detect
                analysis = detect_csv_format(content, filename)
        
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
        
        # Add file metadata
        analysis["filename"] = file.filename
        analysis["file_size"] = len(content)
        analysis["mime_type"] = mime_type
        
        # Identify data standards if we have field analysis
        if "field_analysis" in analysis:
            standards = identify_data_standards(analysis["field_analysis"], filename or 'uploaded_file')
            analysis["identified_standards"] = standards
        
        # Generate recommendations
        analysis["recommendations"] = generate_recommendations(analysis)
        
        return {
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
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

def determine_postgis_type(field_name: str, data_type: str, analysis_data: dict) -> str:
    """Determine the appropriate PostGIS type for a field"""
    if data_type == "postcode":
        return "VARCHAR(8)"
    elif data_type == "uprn":
        return "BIGINT"
    elif data_type == "usrn":
        return "BIGINT"
    elif data_type == "coordinate":
        return "DECIMAL(10, 6)"
    elif data_type == "date":
        return "DATE"
    elif data_type == "decimal":
        return "DECIMAL(15, 2)"
    elif data_type == "integer":
        return "INTEGER"
    elif data_type == "boolean":
        return "BOOLEAN"
    elif data_type == "text":
        # Estimate length based on field name
        if any(pattern in field_name.lower() for pattern in ['description', 'notes', 'comments']):
            return "TEXT"
        else:
            return "VARCHAR(255)"
    else:
        return "VARCHAR(255)"

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
async def get_data_standards():
    """Get list of supported data standards"""
    return {
        "standards": DATA_STANDARDS,
        "count": len(DATA_STANDARDS)
    }

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
    current_user: dict = Depends(require_admin_or_power)
):
    """Create new dataset structure"""
    try:
        structure_id = str(uuid.uuid4())
        query = """
            INSERT INTO design_enhanced.dataset_structures 
            (structure_id, dataset_name, description, source_type, file_formats, 
             governing_body, data_standards, business_owner, data_steward, created_by, tags)
            VALUES (:structure_id, :dataset_name, :description, :source_type, :file_formats,
                    :governing_body, :data_standards, :business_owner, :data_steward, :created_by, :tags)
        """
        
        db.execute(text(query), {
            "structure_id": structure_id,
            "dataset_name": structure_data["dataset_name"],
            "description": structure_data.get("description", ""),
            "source_type": structure_data.get("source_type", "file"),
            "file_formats": json.dumps(structure_data.get("file_formats", [])),
            "governing_body": structure_data.get("governing_body"),
            "data_standards": json.dumps(structure_data.get("data_standards", [])),
            "business_owner": structure_data.get("business_owner"),
            "data_steward": structure_data.get("data_steward"),
            "created_by": current_user["username"],
            "tags": json.dumps(structure_data.get("tags", []))
        })
        db.commit()
        
        return {"message": "Dataset structure created successfully", "structure_id": structure_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating dataset structure: {str(e)}")

@router.get("/structures/{structure_id}")
async def get_dataset_structure(
    structure_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
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
    current_user: dict = Depends(require_admin_or_power)
):
    """Create new field definition"""
    try:
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
        
        db.execute(text(query), {
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
            "created_by": current_user["username"]
        })
        db.commit()
        
        return {"message": "Field definition created successfully", "field_id": field_id}
    except Exception as e:
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
    current_user: dict = Depends(require_admin_or_power)
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
            "created_by": current_user["username"]
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
    current_user: dict = Depends(require_admin_or_power)
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
            "created_by": current_user["username"]
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
    current_user: dict = Depends(require_admin_or_power)
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
            "created_by": current_user["username"]
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
    current_user: dict = Depends(require_authenticated_user)
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
            "uploaded_by": current_user["username"]
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
    current_user: dict = Depends(require_authenticated_user)
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
            "reviewer_id": current_user["username"],
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