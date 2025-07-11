"""
AI Analysis Service for Government Data
Provides intelligent analysis of government datasets for automatic mapping and standards detection
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class GovernmentDataAnalyzer:
    """AI-powered analyzer for government datasets"""
    
    def __init__(self):
        self.uk_standards = {
            'BS7666': self._load_bs7666_patterns(),
            'INSPIRE': self._load_inspire_patterns(),
            'OS_Standards': self._load_os_patterns(),
            'GDS': self._load_gds_patterns()
        }
        
        self.field_patterns = self._load_field_patterns()
        self.data_quality_rules = self._load_quality_rules()
        
    def analyze_dataset(self, file_content: str, file_type: str, file_name: str) -> Dict[str, Any]:
        """
        Main analysis function for government datasets
        
        Args:
            file_content: Raw file content
            file_type: Type of file (csv, json, xml, etc.)
            file_name: Name of the file
            
        Returns:
            Comprehensive analysis results
        """
        try:
            analysis = {
                'file_info': {
                    'name': file_name,
                    'type': file_type,
                    'analyzed_at': datetime.now().isoformat()
                },
                'content_analysis': {},
                'schema_detection': {},
                'standards_compliance': {},
                'mapping_suggestions': {},
                'data_quality': {},
                'confidence_score': 0.0,
                'recommendations': []
            }
            
            # Step 1: Content Analysis
            analysis['content_analysis'] = self._analyze_content(file_content, file_type)
            
            # Step 2: Schema Detection
            analysis['schema_detection'] = self._detect_schema(file_content, file_type)
            
            # Step 3: Standards Compliance
            analysis['standards_compliance'] = self._check_standards_compliance(
                analysis['content_analysis'], 
                analysis['schema_detection']
            )
            
            # Step 4: Generate Mapping Suggestions
            analysis['mapping_suggestions'] = self._generate_mapping_suggestions(analysis)
            
            # Step 5: Data Quality Assessment
            analysis['data_quality'] = self._assess_data_quality(file_content, file_type)
            
            # Step 6: Calculate Confidence Score
            analysis['confidence_score'] = self._calculate_confidence(analysis)
            
            # Step 7: Generate Recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                'error': str(e),
                'confidence_score': 0.0
            }
    
    def _analyze_content(self, content: str, file_type: str) -> Dict[str, Any]:
        """Analyze content patterns and structure"""
        analysis = {
            'data_patterns': [],
            'field_types': [],
            'value_patterns': [],
            'government_indicators': [],
            'data_characteristics': {}
        }
        
        if file_type == 'csv':
            analysis.update(self._analyze_csv_content(content))
        elif file_type in ['json', 'geojson']:
            analysis.update(self._analyze_json_content(content))
        elif file_type in ['xml', 'gml']:
            analysis.update(self._analyze_xml_content(content))
            
        return analysis
    
    def _analyze_csv_content(self, content: str) -> Dict[str, Any]:
        """Analyze CSV content for government data patterns"""
        try:
            # Parse CSV content
            lines = content.split('\n')
            if len(lines) < 2:
                return {}
                
            headers = [h.strip().lower() for h in lines[0].split(',')]
            data_lines = lines[1:100]  # Analyze first 100 data rows
            
            analysis = {
                'data_patterns': self._detect_csv_patterns(headers, data_lines),
                'field_types': self._detect_field_types(headers, data_lines),
                'government_indicators': self._detect_government_indicators(headers, data_lines),
                'data_characteristics': self._analyze_data_characteristics(data_lines)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"CSV analysis failed: {str(e)}")
            return {}
    
    def _analyze_json_content(self, content: str) -> Dict[str, Any]:
        """Analyze JSON content for government data patterns"""
        try:
            import json
            data = json.loads(content)
            
            analysis = {
                'data_patterns': [],
                'field_types': [],
                'government_indicators': [],
                'data_characteristics': {}
            }
            
            # Analyze JSON structure
            if isinstance(data, dict):
                analysis['data_patterns'] = self._detect_json_patterns(data)
                analysis['field_types'] = self._detect_json_field_types(data)
                analysis['government_indicators'] = self._detect_government_indicators_json(data)
            elif isinstance(data, list) and len(data) > 0:
                # Analyze first item in array
                first_item = data[0] if isinstance(data[0], dict) else {}
                analysis['data_patterns'] = self._detect_json_patterns(first_item)
                analysis['field_types'] = self._detect_json_field_types(first_item)
                analysis['government_indicators'] = self._detect_government_indicators_json(first_item)
            
            return analysis
            
        except Exception as e:
            logger.error(f"JSON analysis failed: {str(e)}")
            return {}
    
    def _analyze_xml_content(self, content: str) -> Dict[str, Any]:
        """Analyze XML/GML content for government data patterns"""
        try:
            from xml.etree import ElementTree
            
            analysis = {
                'data_patterns': [],
                'field_types': [],
                'government_indicators': [],
                'data_characteristics': {}
            }
            
            # Parse XML content
            root = ElementTree.fromstring(content)
            
            # Analyze XML structure
            analysis['data_patterns'] = self._detect_xml_patterns(root)
            analysis['field_types'] = self._detect_xml_field_types(root)
            analysis['government_indicators'] = self._detect_government_indicators_xml(root)
            
            return analysis
            
        except Exception as e:
            logger.error(f"XML analysis failed: {str(e)}")
            return {}
    
    def _detect_json_patterns(self, data: Dict) -> List[Dict]:
        """Detect patterns in JSON data"""
        patterns = []
        
        for key, value in data.items():
            pattern = {
                'header': key,
                'detected_types': [],
                'confidence_scores': {},
                'sample_values': [str(value)],
                'suggestions': []
            }
            
            # Detect patterns based on key name and value
            if self._is_government_field(key, [str(value)]):
                pattern['detected_types'].append('government_data')
                pattern['confidence_scores']['government_data'] = 0.9
                pattern['suggestions'].append('Government data field detected')
            
            # Detect data types
            if isinstance(value, (int, float)):
                pattern['detected_types'].append('numeric')
                pattern['confidence_scores']['numeric'] = 1.0
            elif isinstance(value, str):
                # Check for specific patterns
                if re.match(r'^\d{12}$', value):
                    pattern['detected_types'].append('uprn')
                    pattern['confidence_scores']['uprn'] = 0.95
                elif re.match(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$', value, re.IGNORECASE):
                    pattern['detected_types'].append('postcode')
                    pattern['confidence_scores']['postcode'] = 0.9
            
            patterns.append(pattern)
        
        return patterns
    
    def _detect_json_field_types(self, data: Dict) -> List[Dict]:
        """Detect field types in JSON data"""
        field_types = []
        
        for key, value in data.items():
            field_type = {
                'column': key,
                'detected_type': self._infer_json_type(value),
                'confidence': 0.8,
                'sample_values': [str(value)]
            }
            field_types.append(field_type)
        
        return field_types
    
    def _infer_json_type(self, value) -> str:
        """Infer data type from JSON value"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'decimal'
        elif isinstance(value, str):
            # Check for specific patterns
            if re.match(r'^\d{4}-\d{2}-\d{2}', value):
                return 'date'
            elif re.match(r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$', value, re.IGNORECASE):
                return 'postcode'
            else:
                return 'text'
        else:
            return 'text'
    
    def _detect_government_indicators_json(self, data: Dict) -> List[str]:
        """Detect government indicators in JSON data"""
        indicators = []
        
        for key in data.keys():
            key_lower = key.lower()
            if any(term in key_lower for term in ['uprn', 'usrn', 'postcode', 'address', 'council', 'borough']):
                indicators.append(f"Contains {key} field")
        
        return indicators
    
    def _detect_xml_patterns(self, root) -> List[Dict]:
        """Detect patterns in XML data"""
        patterns = []
        
        # Analyze root element and immediate children
        for child in root:
            pattern = {
                'header': child.tag,
                'detected_types': [],
                'confidence_scores': {},
                'sample_values': [child.text or ''],
                'suggestions': []
            }
            
            # Check for government data patterns
            if self._is_government_field(child.tag, [child.text or '']):
                pattern['detected_types'].append('government_data')
                pattern['confidence_scores']['government_data'] = 0.9
            
            patterns.append(pattern)
        
        return patterns
    
    def _detect_xml_field_types(self, root) -> List[Dict]:
        """Detect field types in XML data"""
        field_types = []
        
        for child in root:
            field_type = {
                'column': child.tag,
                'detected_type': self._infer_xml_type(child),
                'confidence': 0.8,
                'sample_values': [child.text or '']
            }
            field_types.append(field_type)
        
        return field_types
    
    def _infer_xml_type(self, element) -> str:
        """Infer data type from XML element"""
        text = element.text or ''
        
        if text.isdigit():
            return 'integer'
        elif text.replace('.', '').isdigit():
            return 'decimal'
        elif text.lower() in ['true', 'false']:
            return 'boolean'
        else:
            return 'text'
    
    def _detect_government_indicators_xml(self, root) -> List[str]:
        """Detect government indicators in XML data"""
        indicators = []
        
        for child in root:
            if self._is_government_field(child.tag, [child.text or '']):
                indicators.append(f"Contains {child.tag} element")
        
        return indicators
    
    def _analyze_value_patterns(self, content: str) -> List[Dict]:
        """Analyze value patterns in data"""
        patterns = []
        
        # This is a placeholder for value pattern analysis
        # In a full implementation, this would analyze data values for patterns
        
        return patterns
    
    def _detect_csv_patterns(self, headers: List[str], data_lines: List[str]) -> List[Dict]:
        """Detect patterns in CSV data"""
        patterns = []
        
        # UK Government data patterns
        uk_patterns = {
            'postcode': r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$',
            'uprn': r'^\d{12}$',
            'usrn': r'^\d{8}$',
            'toid': r'^\d{16}$',
            'date_uk': r'^\d{1,2}/\d{1,2}/\d{4}$',
            'date_iso': r'^\d{4}-\d{2}-\d{2}$',
            'currency_gbp': r'^£?\d+\.?\d*$',
            'percentage': r'^\d+\.?\d*%?$',
            'email': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
            'phone_uk': r'^(\+44|0)\d{10,11}$',
            'grid_reference': r'^[A-Z]{2}\d{6,10}$'
        }
        
        for i, header in enumerate(headers):
            pattern_info = {
                'column_index': i,
                'header': header,
                'detected_types': [],
                'confidence_scores': {},
                'sample_values': [],
                'suggestions': []
            }
            
            # Extract column values
            column_values = []
            for line in data_lines:
                if line.strip():
                    values = line.split(',')
                    if i < len(values):
                        value = values[i].strip().strip('"')
                        if value:
                            column_values.append(value)
                            if len(pattern_info['sample_values']) < 5:
                                pattern_info['sample_values'].append(value)
            
            # Test against patterns
            for pattern_name, regex in uk_patterns.items():
                matches = sum(1 for v in column_values if re.match(regex, v, re.IGNORECASE))
                if column_values:
                    match_rate = matches / len(column_values)
                    if match_rate > 0.7:  # 70% confidence threshold
                        pattern_info['detected_types'].append(pattern_name)
                        pattern_info['confidence_scores'][pattern_name] = match_rate
                        pattern_info['suggestions'].append(f"Likely {pattern_name} field")
            
            # Special government field detection
            if self._is_government_field(header, column_values):
                pattern_info['detected_types'].append('government_data')
                pattern_info['confidence_scores']['government_data'] = 0.9
                pattern_info['suggestions'].append('Government data field detected')
            
            patterns.append(pattern_info)
        
        return patterns
    
    def _is_government_field(self, header: str, values: List[str]) -> bool:
        """Check if field contains government data"""
        government_keywords = [
            'uprn', 'usrn', 'toid', 'lad', 'ward', 'constituency', 'parish',
            'rateable', 'valuation', 'business', 'property', 'address',
            'postcode', 'post_code', 'local_authority', 'council', 'borough',
            'district', 'county', 'region', 'boundary', 'geometry'
        ]
        
        header_lower = header.lower()
        return any(keyword in header_lower for keyword in government_keywords)
    
    def _detect_field_types(self, headers: List[str], data_lines: List[str]) -> List[Dict]:
        """Detect data types for each field"""
        field_types = []
        
        for i, header in enumerate(headers):
            values = []
            for line in data_lines:
                if line.strip():
                    parts = line.split(',')
                    if i < len(parts):
                        value = parts[i].strip().strip('"')
                        if value:
                            values.append(value)
            
            field_type = {
                'column': header,
                'detected_type': self._infer_data_type(values),
                'confidence': 0.8,
                'sample_values': values[:5]
            }
            
            field_types.append(field_type)
        
        return field_types
    
    def _infer_data_type(self, values: List[str]) -> str:
        """Infer data type from values"""
        if not values:
            return 'text'
        
        sample = values[:20]
        
        # Check for numbers
        numbers = [v for v in sample if v.replace('.', '').replace('-', '').isdigit()]
        if len(numbers) / len(sample) > 0.8:
            return 'numeric'
        
        # Check for dates
        date_patterns = [
            r'^\d{1,2}/\d{1,2}/\d{4}$',
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{2}/\d{2}/\d{2}$'
        ]
        dates = sum(1 for v in sample if any(re.match(p, v) for p in date_patterns))
        if dates / len(sample) > 0.8:
            return 'date'
        
        # Check for booleans
        boolean_values = ['true', 'false', 'yes', 'no', '1', '0', 'y', 'n']
        booleans = sum(1 for v in sample if v.lower() in boolean_values)
        if booleans / len(sample) > 0.8:
            return 'boolean'
        
        return 'text'
    
    def _detect_government_indicators(self, headers: List[str], data_lines: List[str]) -> List[str]:
        """Detect indicators of government data"""
        indicators = []
        
        # Check headers for government keywords
        government_terms = [
            'uprn', 'usrn', 'toid', 'lad', 'ward', 'constituency', 'parish',
            'rateable', 'valuation', 'business', 'property', 'address',
            'postcode', 'council', 'borough', 'district', 'county'
        ]
        
        header_text = ' '.join(headers).lower()
        for term in government_terms:
            if term in header_text:
                indicators.append(f"Contains {term.upper()} fields")
        
        # Check for UK-specific patterns
        uk_patterns = [
            'postcode', 'uprn', 'usrn', 'lad', 'ward'
        ]
        
        for pattern in uk_patterns:
            if any(pattern in header.lower() for header in headers):
                indicators.append(f"UK government data pattern: {pattern.upper()}")
        
        return indicators
    
    def _detect_schema(self, content: str, file_type: str) -> Dict[str, Any]:
        """Detect schema structure"""
        schema = {
            'type': file_type,
            'fields': [],
            'relationships': [],
            'constraints': [],
            'suggested_table_name': None
        }
        
        if file_type == 'csv':
            lines = content.split('\n')
            if lines:
                headers = [h.strip() for h in lines[0].split(',')]
                schema['fields'] = [
                    {
                        'name': header,
                        'position': i,
                        'suggested_type': 'text',
                        'constraints': [],
                        'description': self._generate_field_description(header)
                    }
                    for i, header in enumerate(headers)
                ]
                schema['suggested_table_name'] = self._suggest_table_name(headers, content)
        
        return schema
    
    def _generate_field_description(self, field_name: str) -> str:
        """Generate description for field"""
        descriptions = {
            'uprn': 'Unique Property Reference Number - UK standard property identifier',
            'usrn': 'Unique Street Reference Number - UK standard street identifier',
            'postcode': 'UK postal code for address location',
            'address': 'Property or location address',
            'name': 'Name of person, property, or entity',
            'value': 'Numeric value or amount',
            'date': 'Date information',
            'type': 'Classification or category',
            'code': 'Reference code or identifier'
        }
        
        field_lower = field_name.lower()
        for key, desc in descriptions.items():
            if key in field_lower:
                return desc
        
        return f"Field containing {field_name.lower()} information"
    
    def _suggest_table_name(self, headers: List[str], content: str) -> str:
        """Suggest table name based on content"""
        keywords = ' '.join(headers).lower()
        
        suggestions = {
            'uprn': 'properties',
            'usrn': 'streets',
            'postcode': 'addresses',
            'rateable': 'business_rates',
            'valuation': 'valuations',
            'boundary': 'boundaries',
            'ward': 'wards',
            'constituency': 'constituencies'
        }
        
        for keyword, suggestion in suggestions.items():
            if keyword in keywords:
                return f"staging_{suggestion}"
        
        return "staging_data"
    
    def _check_standards_compliance(self, content_analysis: Dict, schema_detection: Dict) -> Dict[str, Any]:
        """Check compliance with government standards"""
        compliance = {
            'detected_standards': [],
            'compliance_scores': {},
            'recommendations': []
        }
        
        # Check BS7666 (UK Address Standard)
        bs7666_score = self._check_bs7666_compliance(content_analysis, schema_detection)
        if bs7666_score > 0.5:
            compliance['detected_standards'].append({
                'name': 'BS7666',
                'score': bs7666_score,
                'details': f'Found {int(bs7666_score * 4)}/4 BS7666 fields'
            })
            compliance['compliance_scores']['BS7666'] = bs7666_score
        
        # Check INSPIRE compliance
        inspire_score = self._check_inspire_compliance(content_analysis, schema_detection)
        if inspire_score > 0.5:
            compliance['detected_standards'].append({
                'name': 'INSPIRE',
                'score': inspire_score,
                'details': f'INSPIRE spatial data compliance detected'
            })
            compliance['compliance_scores']['INSPIRE'] = inspire_score
        
        # Check OS Standards
        os_score = self._check_os_standards_compliance(content_analysis, schema_detection)
        if os_score > 0.5:
            compliance['detected_standards'].append({
                'name': 'OS_Standards',
                'score': os_score,
                'details': f'OS Standards compliance detected'
            })
            compliance['compliance_scores']['OS_Standards'] = os_score
        
        # Check GDS compliance
        gds_score = self._check_gds_compliance(content_analysis, schema_detection)
        if gds_score > 0.5:
            compliance['detected_standards'].append({
                'name': 'GDS',
                'score': gds_score,
                'details': f'GDS standards compliance detected'
            })
            compliance['compliance_scores']['GDS'] = gds_score
        
        return compliance
    
    def _check_bs7666_compliance(self, content_analysis: Dict, schema_detection: Dict) -> float:
        """Check BS7666 (UK Address Standard) compliance"""
        required_fields = ['uprn', 'usrn', 'postcode', 'address']
        found_fields = 0
        
        for field in schema_detection.get('fields', []):
            field_lower = field['name'].lower()
            if any(req in field_lower for req in required_fields):
                found_fields += 1
        
        return found_fields / len(required_fields) if required_fields else 0.0
    
    def _check_inspire_compliance(self, content_analysis: Dict, schema_detection: Dict) -> float:
        """Check INSPIRE compliance"""
        inspire_fields = ['geometry', 'coordinate', 'latitude', 'longitude', 'easting', 'northing']
        found_fields = 0
        
        for field in schema_detection.get('fields', []):
            field_lower = field['name'].lower()
            if any(inspire in field_lower for inspire in inspire_fields):
                found_fields += 1
        
        return 0.8 if found_fields > 0 else 0.2
    
    def _check_os_standards_compliance(self, content_analysis: Dict, schema_detection: Dict) -> float:
        """Check Ordnance Survey standards compliance"""
        os_fields = ['toid', 'osgb', 'easting', 'northing', 'grid_reference']
        found_fields = 0
        
        for field in schema_detection.get('fields', []):
            field_lower = field['name'].lower()
            if any(os_field in field_lower for os_field in os_fields):
                found_fields += 1
        
        return found_fields / len(os_fields) if os_fields else 0.0
    
    def _check_gds_compliance(self, content_analysis: Dict, schema_detection: Dict) -> float:
        """Check Government Digital Service standards compliance"""
        gds_indicators = ['open_data', 'machine_readable', 'linked_data', 'metadata']
        found_indicators = 0
        
        # Check for GDS principles in field names and content
        for field in schema_detection.get('fields', []):
            field_lower = field['name'].lower()
            if any(indicator in field_lower for indicator in gds_indicators):
                found_indicators += 1
        
        # Check content analysis for GDS indicators
        if content_analysis.get('government_indicators'):
            found_indicators += len(content_analysis['government_indicators'])
        
        return min(found_indicators / 4.0, 1.0)  # Normalize to 0-1 scale
    
    def _generate_mapping_suggestions(self, analysis: Dict) -> Dict[str, Any]:
        """Generate mapping suggestions"""
        suggestions = {
            'column_mappings': [],
            'transformations': [],
            'validations': [],
            'staging_table': {
                'name': analysis['schema_detection'].get('suggested_table_name', 'staging_data'),
                'fields': []
            }
        }
        
        # Generate column mappings
        for field in analysis['schema_detection'].get('fields', []):
            mapping = {
                'source_column': field['name'],
                'target_column': self._suggest_target_column(field['name']),
                'mapping_type': 'direct',
                'data_type': self._suggest_data_type(field),
                'transformations': [],
                'validations': []
            }
            
            # Add transformations based on detected patterns
            for pattern in analysis['content_analysis'].get('data_patterns', []):
                if pattern['header'] == field['name']:
                    mapping['transformations'] = self._suggest_transformations(pattern)
                    mapping['validations'] = self._suggest_validations(pattern)
                    break
            
            suggestions['column_mappings'].append(mapping)
        
        return suggestions
    
    def _suggest_target_column(self, source_name: str) -> str:
        """Suggest target column name"""
        mappings = {
            'uprn': 'uprn',
            'usrn': 'usrn',
            'postcode': 'postcode',
            'post_code': 'postcode',
            'address': 'address',
            'property_address': 'property_address',
            'name': 'name',
            'value': 'value',
            'amount': 'amount',
            'date': 'date',
            'type': 'type',
            'code': 'code'
        }
        
        source_lower = source_name.lower()
        for key, target in mappings.items():
            if key in source_lower:
                return target
        
        return source_name.lower().replace(' ', '_')
    
    def _suggest_data_type(self, field: Dict) -> str:
        """Suggest data type for field"""
        type_mappings = {
            'uprn': 'bigint',
            'usrn': 'bigint',
            'postcode': 'varchar(10)',
            'address': 'text',
            'date': 'date',
            'amount': 'decimal(10,2)',
            'value': 'decimal(10,2)',
            'percentage': 'decimal(5,2)',
            'boolean': 'boolean'
        }
        
        field_lower = field['name'].lower()
        for key, type_name in type_mappings.items():
            if key in field_lower:
                return type_name
        
        return 'text'
    
    def _suggest_transformations(self, pattern: Dict) -> List[str]:
        """Suggest transformations based on pattern"""
        transformations = []
        
        if 'postcode' in pattern.get('detected_types', []):
            transformations.append('uppercase')
            transformations.append('trim')
        
        if 'date' in pattern.get('detected_types', []):
            transformations.append('date_format')
        
        if 'currency' in pattern.get('detected_types', []):
            transformations.append('currency_format')
        
        return transformations
    
    def _suggest_validations(self, pattern: Dict) -> List[str]:
        """Suggest validations based on pattern"""
        validations = []
        
        if 'postcode' in pattern.get('detected_types', []):
            validations.append('uk_postcode_format')
        
        if 'uprn' in pattern.get('detected_types', []):
            validations.append('uprn_format')
        
        if 'email' in pattern.get('detected_types', []):
            validations.append('email_format')
        
        return validations
    
    def _assess_data_quality(self, content: str, file_type: str) -> Dict[str, Any]:
        """Assess data quality"""
        quality = {
            'completeness': 0.0,
            'consistency': 0.0,
            'accuracy': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        if file_type == 'csv':
            quality.update(self._assess_csv_quality(content))
        
        return quality
    
    def _assess_csv_quality(self, content: str) -> Dict[str, Any]:
        """Assess CSV data quality"""
        lines = content.split('\n')
        if len(lines) < 2:
            return {'completeness': 0.0, 'consistency': 0.0, 'accuracy': 0.0}
        
        headers = lines[0].split(',')
        data_lines = lines[1:]
        
        # Check completeness
        total_cells = len(headers) * len(data_lines)
        empty_cells = sum(1 for line in data_lines for cell in line.split(',') if not cell.strip())
        completeness = 1 - (empty_cells / total_cells) if total_cells > 0 else 0
        
        # Check consistency (same number of columns)
        expected_columns = len(headers)
        consistent_lines = sum(1 for line in data_lines if len(line.split(',')) == expected_columns)
        consistency = consistent_lines / len(data_lines) if data_lines else 0
        
        return {
            'completeness': completeness,
            'consistency': consistency,
            'accuracy': 0.8,  # Placeholder
            'issues': [],
            'recommendations': []
        }
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate overall confidence score"""
        confidence = 0.0
        factors = 0
        
        # Content analysis confidence
        if analysis['content_analysis'].get('data_patterns'):
            pattern_confidences = []
            for pattern in analysis['content_analysis']['data_patterns']:
                if pattern.get('confidence_scores'):
                    pattern_confidences.extend(pattern['confidence_scores'].values())
            if pattern_confidences:
                avg_confidence = sum(pattern_confidences) / len(pattern_confidences)
                confidence += avg_confidence * 0.3
                factors += 0.3
        
        # Standards compliance confidence
        if analysis['standards_compliance'].get('detected_standards'):
            avg_compliance = sum(analysis['standards_compliance']['compliance_scores'].values()) / len(analysis['standards_compliance']['detected_standards'])
            confidence += avg_compliance * 0.4
            factors += 0.4
        
        # Schema detection confidence
        if analysis['schema_detection'].get('fields'):
            confidence += 0.3
            factors += 0.3
        
        return confidence / factors if factors > 0 else 0.0
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Standards recommendations
        detected_standards = analysis['standards_compliance'].get('detected_standards', [])
        if not detected_standards:
            recommendations.append("Consider implementing UK government data standards (BS7666, INSPIRE)")
        
        if 'BS7666' in detected_standards:
            recommendations.append("BS7666 compliance detected - ensure proper address formatting")
        
        if 'INSPIRE' in detected_standards:
            recommendations.append("INSPIRE compliance detected - verify coordinate reference systems")
        
        # Data quality recommendations
        quality = analysis.get('data_quality', {})
        if quality.get('completeness', 1) < 0.9:
            recommendations.append("Data completeness below 90% - consider data cleaning")
        
        if quality.get('consistency', 1) < 0.95:
            recommendations.append("Data consistency issues detected - verify column structure")
        
        return recommendations
    
    def _load_bs7666_patterns(self) -> Dict:
        """Load BS7666 address standard patterns"""
        return {
            'required_fields': ['uprn', 'usrn', 'postcode', 'address'],
            'field_patterns': {
                'uprn': r'^\d{12}$',
                'usrn': r'^\d{8}$',
                'postcode': r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$'
            }
        }
    
    def _load_inspire_patterns(self) -> Dict:
        """Load INSPIRE directive patterns"""
        return {
            'spatial_fields': ['geometry', 'coordinate', 'latitude', 'longitude', 'easting', 'northing'],
            'required_metadata': ['crs', 'spatial_reference', 'coordinate_system']
        }
    
    def _load_os_patterns(self) -> Dict:
        """Load Ordnance Survey patterns"""
        return {
            'os_fields': ['toid', 'osgb', 'easting', 'northing', 'grid_reference'],
            'coordinate_systems': ['OSGB36', 'ETRS89', 'WGS84']
        }
    
    def _load_gds_patterns(self) -> Dict:
        """Load Government Digital Service patterns"""
        return {
            'data_standards': ['open_standards', 'machine_readable', 'linked_data'],
            'metadata_requirements': ['title', 'description', 'publisher', 'license']
        }
    
    def _load_field_patterns(self) -> Dict:
        """Load field detection patterns"""
        return {
            'postcode': r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$',
            'uprn': r'^\d{12}$',
            'usrn': r'^\d{8}$',
            'date_uk': r'^\d{1,2}/\d{1,2}/\d{4}$',
            'currency_gbp': r'^£?\d+\.?\d*$'
        }
    
    def _load_quality_rules(self) -> Dict:
        """Load data quality assessment rules"""
        return {
            'completeness_threshold': 0.9,
            'consistency_threshold': 0.95,
            'accuracy_threshold': 0.8
        }
    
    def _analyze_data_characteristics(self, data_lines: List[str]) -> Dict[str, Any]:
        """Analyze general data characteristics"""
        if not data_lines:
            return {}
        
        characteristics = {
            'total_rows': len(data_lines),
            'avg_columns': 0,
            'data_types': {},
            'value_distributions': {}
        }
        
        # Calculate average columns
        column_counts = [len(line.split(',')) for line in data_lines if line.strip()]
        if column_counts:
            characteristics['avg_columns'] = sum(column_counts) / len(column_counts)
        
        return characteristics 