"""
AI Analysis Router
Provides endpoints for intelligent analysis of government datasets
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
from ..services.ai_analysis_service import GovernmentDataAnalyzer
from ..services.database_service import get_db
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI Analysis"])

# Initialize AI analyzer
ai_analyzer = GovernmentDataAnalyzer()

@router.post("/analyze-dataset")
async def analyze_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze a government dataset using AI
    
    This endpoint performs comprehensive analysis including:
    - Content pattern detection
    - Schema detection
    - Government standards compliance
    - Mapping suggestions
    - Data quality assessment
    """
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Determine file type
        filename = file.filename or "unknown_file"
        file_type = _determine_file_type(filename, content_str)
        
        # Perform AI analysis
        analysis = ai_analyzer.analyze_dataset(
            file_content=content_str,
            file_type=file_type,
            file_name=filename
        )
        
        # Log analysis request
        _log_analysis_request(db, filename, file_type, analysis)
        
        return JSONResponse(content=analysis)
        
    except Exception as e:
        logger.error(f"AI analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/detect-types")
async def detect_field_types(
    content: Dict[str, str],
    db: Session = Depends(get_db)
):
    """
    Detect field types in dataset content
    
    Args:
        content: Dictionary containing 'content' key with file content
        
    Returns:
        List of detected field types with confidence scores
    """
    try:
        file_content = content.get('content', '')
        if not file_content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Determine file type from content
        file_type = _determine_file_type_from_content(file_content)
        
        # Analyze content for field types
        analysis = ai_analyzer._analyze_content(file_content, file_type)
        
        return JSONResponse(content={
            'field_types': analysis.get('field_types', []),
            'data_patterns': analysis.get('data_patterns', []),
            'file_type': file_type
        })
        
    except Exception as e:
        logger.error(f"Field type detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@router.post("/suggest-mappings")
async def suggest_mappings(
    schema: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Generate mapping suggestions based on schema
    
    Args:
        schema: Schema information including fields and detected patterns
        
    Returns:
        Mapping suggestions with transformations and validations
    """
    try:
        # Generate mapping suggestions
        suggestions = ai_analyzer._generate_mapping_suggestions({
            'schema_detection': schema,
            'content_analysis': schema.get('content_analysis', {})
        })
        
        return JSONResponse(content=suggestions)
        
    except Exception as e:
        logger.error(f"Mapping suggestions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {str(e)}")

@router.post("/check-standards")
async def check_standards_compliance(
    content_analysis: Dict[str, Any],
    schema_detection: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Check compliance with government data standards
    
    Args:
        content_analysis: Content analysis results
        schema_detection: Schema detection results
        
    Returns:
        Standards compliance assessment
    """
    try:
        compliance = ai_analyzer._check_standards_compliance(
            content_analysis, 
            schema_detection
        )
        
        return JSONResponse(content=compliance)
        
    except Exception as e:
        logger.error(f"Standards compliance check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")

@router.post("/assess-quality")
async def assess_data_quality(
    content: Dict[str, str],
    file_type: str,
    db: Session = Depends(get_db)
):
    """
    Assess data quality of uploaded content
    
    Args:
        content: Dictionary containing 'content' key with file content
        file_type: Type of file (csv, json, xml, etc.)
        
    Returns:
        Data quality assessment results
    """
    try:
        file_content = content.get('content', '')
        if not file_content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        quality = ai_analyzer._assess_data_quality(file_content, file_type)
        
        return JSONResponse(content=quality)
        
    except Exception as e:
        logger.error(f"Data quality assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quality assessment failed: {str(e)}")

@router.get("/standards/{standard_name}")
async def get_standard_info(standard_name: str):
    """
    Get information about a specific government data standard
    
    Args:
        standard_name: Name of the standard (BS7666, INSPIRE, OS_Standards, GDS)
        
    Returns:
        Standard information and requirements
    """
    try:
        if standard_name not in ai_analyzer.uk_standards:
            raise HTTPException(status_code=404, detail=f"Standard {standard_name} not found")
        
        standard_info = {
            'name': standard_name,
            'patterns': ai_analyzer.uk_standards[standard_name],
            'description': _get_standard_description(standard_name),
            'requirements': _get_standard_requirements(standard_name)
        }
        
        return JSONResponse(content=standard_info)
        
    except Exception as e:
        logger.error(f"Standard info retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Info retrieval failed: {str(e)}")

@router.get("/patterns")
async def get_detection_patterns():
    """
    Get all available detection patterns for government data
    
    Returns:
        Dictionary of detection patterns
    """
    try:
        patterns = {
            'field_patterns': ai_analyzer.field_patterns,
            'government_keywords': _get_government_keywords(),
            'data_types': _get_data_type_patterns()
        }
        
        return JSONResponse(content=patterns)
        
    except Exception as e:
        logger.error(f"Pattern retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pattern retrieval failed: {str(e)}")

@router.post("/validate-mapping")
async def validate_mapping(
    mapping: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Validate a proposed mapping configuration
    
    Args:
        mapping: Mapping configuration to validate
        
    Returns:
        Validation results with suggestions
    """
    try:
        validation = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'confidence': 0.0
        }
        
        # Validate source columns
        if 'source_columns' not in mapping:
            validation['is_valid'] = False
            validation['issues'].append("Missing source columns")
        
        # Validate target columns
        if 'target_columns' not in mapping:
            validation['is_valid'] = False
            validation['issues'].append("Missing target columns")
        
        # Check for common mapping issues
        if mapping.get('source_columns') and mapping.get('target_columns'):
            source_cols = mapping['source_columns']
            target_cols = mapping['target_columns']
            
            if len(source_cols) != len(target_cols):
                validation['issues'].append("Source and target column counts don't match")
            
            # Check for duplicate target columns
            if len(set(target_cols)) != len(target_cols):
                validation['issues'].append("Duplicate target columns detected")
        
        # Generate suggestions based on mapping
        validation['suggestions'] = _generate_mapping_suggestions(mapping)
        
        # Calculate confidence
        validation['confidence'] = _calculate_mapping_confidence(mapping)
        
        return JSONResponse(content=validation)
        
    except Exception as e:
        logger.error(f"Mapping validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

def _determine_file_type(filename: str, content: str) -> str:
    """Determine file type from filename and content"""
    if filename.lower().endswith('.csv'):
        return 'csv'
    elif filename.lower().endswith('.json') or filename.lower().endswith('.geojson'):
        return 'json'
    elif filename.lower().endswith('.xml') or filename.lower().endswith('.gml'):
        return 'xml'
    elif filename.lower().endswith('.zip'):
        return 'zip'
    else:
        # Try to determine from content
        return _determine_file_type_from_content(content)

def _determine_file_type_from_content(content: str) -> str:
    """Determine file type from content analysis"""
    content_start = content.strip()[:100]
    
    if content_start.startswith('{') or content_start.startswith('['):
        return 'json'
    elif content_start.startswith('<'):
        return 'xml'
    elif ',' in content_start and '\n' in content_start:
        return 'csv'
    else:
        return 'text'

def _log_analysis_request(db: Session, filename: str, file_type: str, analysis: Dict):
    """Log AI analysis request to database"""
    try:
        # This would typically log to a database table
        # For now, just log to console
        logger.info(f"AI analysis completed for {filename} ({file_type})")
        logger.info(f"Confidence score: {analysis.get('confidence_score', 0)}")
        
    except Exception as e:
        logger.error(f"Failed to log analysis request: {str(e)}")

def _get_standard_description(standard_name: str) -> str:
    """Get description for a government standard"""
    descriptions = {
        'BS7666': 'UK Address Standard - defines the structure and content of address data',
        'INSPIRE': 'Infrastructure for Spatial Information in Europe - EU directive for spatial data',
        'OS_Standards': 'Ordnance Survey standards for geographic and spatial data',
        'GDS': 'Government Digital Service standards for digital government services'
    }
    return descriptions.get(standard_name, 'No description available')

def _get_standard_requirements(standard_name: str) -> Dict[str, Any]:
    """Get requirements for a government standard"""
    requirements = {
        'BS7666': {
            'required_fields': ['uprn', 'usrn', 'postcode', 'address'],
            'field_formats': {
                'uprn': '12-digit numeric identifier',
                'usrn': '8-digit numeric identifier',
                'postcode': 'UK postal code format'
            }
        },
        'INSPIRE': {
            'required_fields': ['geometry', 'coordinate_reference_system'],
            'metadata_requirements': ['title', 'description', 'publisher', 'license']
        },
        'OS_Standards': {
            'coordinate_systems': ['OSGB36', 'ETRS89', 'WGS84'],
            'precision_requirements': 'Sub-meter accuracy for most applications'
        },
        'GDS': {
            'data_principles': ['open', 'machine_readable', 'linked'],
            'format_requirements': ['CSV', 'JSON', 'XML']
        }
    }
    return requirements.get(standard_name, {})

def _get_government_keywords() -> List[str]:
    """Get list of government data keywords"""
    return [
        'uprn', 'usrn', 'toid', 'lad', 'ward', 'constituency', 'parish',
        'rateable', 'valuation', 'business', 'property', 'address',
        'postcode', 'post_code', 'local_authority', 'council', 'borough',
        'district', 'county', 'region', 'boundary', 'geometry'
    ]

def _get_data_type_patterns() -> Dict[str, str]:
    """Get patterns for data type detection"""
    return {
        'postcode': r'^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$',
        'uprn': r'^\d{12}$',
        'usrn': r'^\d{8}$',
        'date_uk': r'^\d{1,2}/\d{1,2}/\d{4}$',
        'currency_gbp': r'^£?\d+\.?\d*$',
        'email': r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    }

def _generate_mapping_suggestions(mapping: Dict) -> List[str]:
    """Generate suggestions for mapping configuration"""
    suggestions = []
    
    if not mapping.get('transformations'):
        suggestions.append("Consider adding data transformations for data cleaning")
    
    if not mapping.get('validations'):
        suggestions.append("Add validation rules to ensure data quality")
    
    if mapping.get('source_columns'):
        source_cols = mapping['source_columns']
        for col in source_cols:
            if 'postcode' in col.lower():
                suggestions.append(f"Consider uppercase transformation for {col}")
            if 'date' in col.lower():
                suggestions.append(f"Consider date format standardization for {col}")
    
    return suggestions

def _calculate_mapping_confidence(mapping: Dict) -> float:
    """Calculate confidence score for mapping configuration"""
    confidence = 0.0
    
    # Base confidence
    if mapping.get('source_columns') and mapping.get('target_columns'):
        confidence += 0.3
    
    # Transformations
    if mapping.get('transformations'):
        confidence += 0.2
    
    # Validations
    if mapping.get('validations'):
        confidence += 0.2
    
    # Data type specifications
    if mapping.get('data_types'):
        confidence += 0.3
    
    return min(confidence, 1.0) 