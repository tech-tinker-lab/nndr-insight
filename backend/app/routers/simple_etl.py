"""
Simple ETL Router
Provides easy-to-use endpoints for data transformation and loading
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import pandas as pd
import io

from ..services.database_service import get_db
from ..routers.admin import require_authenticated_user
from ..models import User
from ..services.simple_etl_service import simple_etl_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/simple-etl", tags=["simple-etl"])

@router.post("/upload/preview")
async def preview_uploaded_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Preview uploaded file content
    
    Returns:
        File preview with columns and sample data
    """
    try:
        # Read file content
        content = await file.read()
        
        # Get preview
        preview = simple_etl_service.preview_file(content, file.filename)
        
        return {
            "success": True,
            "preview": preview,
            "filename": file.filename,
            "file_size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Error previewing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to preview file: {str(e)}")

@router.get("/tables")
async def get_available_tables(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get list of available database tables"""
    try:
        # Query to get all tables
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
        
        result = db.execute(query)
        tables = [row[0] for row in result.fetchall()]
        
        return {
            "success": True,
            "tables": tables,
            "total_count": len(tables)
        }
        
    except Exception as e:
        logger.error(f"Error getting tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")

@router.get("/tables/{table_name}/columns")
async def get_table_columns(
    table_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get column information for a specific table"""
    try:
        # Query to get column information
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = :table_name
        ORDER BY ordinal_position
        """
        
        result = db.execute(query, {"table_name": table_name})
        columns = [
            {
                "name": row[0],
                "type": row[1],
                "nullable": row[2] == "YES",
                "default": row[3]
            }
            for row in result.fetchall()
        ]
        
        return {
            "success": True,
            "table_name": table_name,
            "columns": columns,
            "total_columns": len(columns)
        }
        
    except Exception as e:
        logger.error(f"Error getting table columns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get table columns: {str(e)}")

@router.post("/validate")
async def validate_etl_config(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Validate ETL configuration before running
    
    Request:
    {
        "source_file": "filename.csv",
        "target_table": "properties",
        "column_mapping": {"source_col": "target_col"},
        "transformations": [...]
    }
    """
    try:
        source_file = request.get("source_file")
        target_table = request.get("target_table")
        column_mapping = request.get("column_mapping", {})
        transformations = request.get("transformations", [])
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Validate target table exists
        table_query = """
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = :table_name
        """
        result = db.execute(table_query, {"table_name": target_table})
        table_exists = result.fetchone()[0] > 0
        
        if not table_exists:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Target table '{target_table}' does not exist")
        
        # Validate column mappings
        if table_exists:
            column_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = :table_name
            """
            result = db.execute(column_query, {"table_name": target_table})
            available_columns = [row[0] for row in result.fetchall()]
            
            for source_col, target_col in column_mapping.items():
                if target_col not in available_columns:
                    validation_results["warnings"].append(
                        f"Target column '{target_col}' not found in table '{target_table}'"
                    )
        
        # Validate transformations
        available_transformations = list(simple_etl_service.transformations.keys())
        for rule in transformations:
            transformation = rule.get("transformation")
            if transformation not in available_transformations:
                validation_results["warnings"].append(
                    f"Unknown transformation: '{transformation}'"
                )
        
        return {
            "success": True,
            "validation": validation_results
        }
        
    except Exception as e:
        logger.error(f"Error validating ETL config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate config: {str(e)}")

@router.post("/run")
async def run_etl_job(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Run ETL job
    
    Request:
    {
        "source_file": "filename.csv",
        "target_table": "properties",
        "column_mapping": {"source_col": "target_col"},
        "transformations": [...],
        "parameters": {...}
    }
    """
    try:
        # Process ETL job
        results = simple_etl_service.process_etl_job(request)
        
        if results["success"]:
            return {
                "success": True,
                "results": results,
                "message": "ETL job completed successfully"
            }
        else:
            return {
                "success": False,
                "error": results["error"],
                "processing_time": results["processing_time"]
            }
        
    except Exception as e:
        logger.error(f"Error running ETL job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to run ETL job: {str(e)}")

@router.get("/transformations")
async def get_available_transformations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get list of available data transformations"""
    try:
        transformations = [
            {
                "id": "uppercase",
                "name": "Convert to Uppercase",
                "description": "Convert text to uppercase",
                "category": "text"
            },
            {
                "id": "lowercase",
                "name": "Convert to Lowercase",
                "description": "Convert text to lowercase",
                "category": "text"
            },
            {
                "id": "trim",
                "name": "Trim Whitespace",
                "description": "Remove leading and trailing spaces",
                "category": "text"
            },
            {
                "id": "number_format",
                "name": "Format Number",
                "description": "Format numeric values",
                "category": "numeric"
            },
            {
                "id": "date_format",
                "name": "Format Date",
                "description": "Convert date formats",
                "category": "date"
            },
            {
                "id": "postcode_clean",
                "name": "Clean Postcode",
                "description": "Standardize UK postcode format",
                "category": "validation"
            },
            {
                "id": "coordinate_validate",
                "name": "Validate Coordinates",
                "description": "Validate and convert coordinates",
                "category": "validation"
            }
        ]
        
        return {
            "success": True,
            "transformations": transformations,
            "total_count": len(transformations)
        }
        
    except Exception as e:
        logger.error(f"Error getting transformations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get transformations: {str(e)}")

@router.post("/test-transformation")
async def test_transformation(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Test a transformation on sample data
    
    Request:
    {
        "transformation": "uppercase",
        "sample_data": ["test1", "test2", "test3"],
        "parameters": {}
    }
    """
    try:
        transformation = request.get("transformation")
        sample_data = request.get("sample_data", [])
        parameters = request.get("parameters", {})
        
        if transformation not in simple_etl_service.transformations:
            raise HTTPException(status_code=400, detail=f"Unknown transformation: {transformation}")
        
        # Create sample DataFrame
        df = pd.DataFrame({"test_column": sample_data})
        
        # Apply transformation
        transformed = simple_etl_service.transformations[transformation](df["test_column"], parameters)
        
        return {
            "success": True,
            "original": sample_data,
            "transformed": transformed.tolist(),
            "transformation": transformation
        }
        
    except Exception as e:
        logger.error(f"Error testing transformation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test transformation: {str(e)}")

@router.get("/jobs")
async def get_etl_jobs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get list of recent ETL jobs"""
    try:
        # This would typically query a jobs table
        # For now, return a placeholder
        jobs = [
            {
                "job_id": "job_001",
                "status": "completed",
                "source_file": "properties.csv",
                "target_table": "properties",
                "records_processed": 1000,
                "records_loaded": 995,
                "errors": 5,
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:32:00Z"
            }
        ]
        
        return {
            "success": True,
            "jobs": jobs,
            "total_count": len(jobs)
        }
        
    except Exception as e:
        logger.error(f"Error getting ETL jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ETL jobs: {str(e)}")

@router.get("/jobs/{job_id}")
async def get_etl_job_details(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get details of a specific ETL job"""
    try:
        # This would typically query a jobs table
        # For now, return a placeholder
        job = {
            "job_id": job_id,
            "status": "completed",
            "source_file": "properties.csv",
            "target_table": "properties",
            "column_mapping": {"BA_Reference": "ba_reference", "Postcode": "postcode"},
            "transformations": [
                {"column": "postcode", "transformation": "postcode_clean"}
            ],
            "records_processed": 1000,
            "records_loaded": 995,
            "errors": 5,
            "warnings": 2,
            "processing_time": 120.5,
            "created_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T10:32:00Z",
            "validation_results": {
                "total_rows": 1000,
                "null_counts": {"postcode": 5},
                "warnings": ["5 invalid postcode formats found"]
            }
        }
        
        return {
            "success": True,
            "job": job
        }
        
    except Exception as e:
        logger.error(f"Error getting ETL job details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job details: {str(e)}") 