from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
import uuid

from app.services.database_service import get_db
from app.models import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/design", tags=["Design System"])
logger = logging.getLogger(__name__)

# RBAC dependency
def require_admin_or_power(user: User = Depends(get_current_user)):
    if user.role not in ("admin", "power_user"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return user

def require_authenticated_user(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

# Design System Models
class TableDesignCreate:
    def __init__(self, design_name: str, table_name: str, description: str, 
                 columns: List[Dict], table_type: str, category: str):
        self.design_name = design_name
        self.table_name = table_name
        self.description = description
        self.columns = columns
        self.table_type = table_type
        self.category = category

class MappingConfigCreate:
    def __init__(self, config_name: str, design_id: str, source_patterns: List[str],
                 mapping_rules: List[Dict], priority: int = 1):
        self.config_name = config_name
        self.design_id = design_id
        self.source_patterns = source_patterns
        self.mapping_rules = mapping_rules
        self.priority = priority

# Audit Models
class AuditLog:
    def __init__(self, user_id: str, action: str, resource_type: str, resource_id: str,
                 details: Dict, timestamp: Optional[datetime] = None):
        self.audit_id = str(uuid.uuid4())
        self.user_id = str(user_id)
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details
        self.timestamp = timestamp or datetime.utcnow()

@router.get("/test")
async def test_design_router():
    """Test endpoint for design system router"""
    return {"message": "Design System Router is working", "status": "success"}

# Table Design Management
@router.post("/tables")
async def create_table_design(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Create a new table design with column definitions
    """
    try:
        design_name = request.get("design_name")
        table_name = request.get("table_name")
        description = request.get("description", "")
        columns = request.get("columns", [])
        table_type = request.get("table_type", "custom")
        category = request.get("category", "general")
        
        if not design_name or not table_name:
            raise HTTPException(status_code=400, detail="Design name and table name are required")
        
        # Generate design ID
        design_id = str(uuid.uuid4())
        
        # Create table design
        design_query = text("""
            INSERT INTO design.table_designs (
                design_id, design_name, table_name, description, columns, 
                table_type, category, created_by, created_at, version
            ) VALUES (
                :design_id, :design_name, :table_name, :description, :columns,
                :table_type, :category, :created_by, :created_at, 1
            )
        """)
        
        db.execute(design_query, {
            "design_id": design_id,
            "design_name": design_name,
            "table_name": table_name,
            "description": description,
            "columns": json.dumps(columns),
            "table_type": table_type,
            "category": category,
            "created_by": user.id,
            "created_at": datetime.utcnow()
        })
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="CREATE",
            resource_type="table_design",
            resource_id=design_id,
            details={
                "design_name": design_name,
                "table_name": table_name,
                "table_type": table_type,
                "category": category,
                "column_count": len(columns)
            }
        )
        
        log_audit_event(db, audit_log)
        
        db.commit()
        
        return {
            "design_id": design_id,
            "design_name": design_name,
            "table_name": table_name,
            "message": "Table design created successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating table design: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating table design: {str(e)}")

@router.get("/tables")
async def list_table_designs(
    table_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    List table designs with filtering and search
    """
    try:
        query = """
            SELECT design_id, design_name, table_name, description, columns,
                   table_type, category, created_by, created_at, version,
                   updated_at, is_active
            FROM design.table_designs
            WHERE is_active = true
        """
        params = {}
        
        if table_type:
            query += " AND table_type = :table_type"
            params["table_type"] = table_type
            
        if category:
            query += " AND category = :category"
            params["category"] = category
            
        if search:
            query += " AND (design_name ILIKE :search OR table_name ILIKE :search OR description ILIKE :search)"
            params["search"] = f"%{search}%"
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(text(query), params)
        designs = []
        
        for row in result.fetchall():
            designs.append({
                "design_id": row[0],
                "design_name": row[1],
                "table_name": row[2],
                "description": row[3],
                "columns": json.loads(row[4]) if row[4] else [],
                "table_type": row[5],
                "category": row[6],
                "created_by": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
                "version": row[9],
                "updated_at": row[10].isoformat() if row[10] else None,
                "is_active": row[11]
            })
        
        return {"designs": designs, "count": len(designs)}
        
    except Exception as e:
        logger.error(f"Error listing table designs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing table designs: {str(e)}")

@router.get("/tables/{design_id}")
async def get_table_design(
    design_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Get a specific table design by ID
    """
    try:
        query = text("""
            SELECT design_id, design_name, table_name, description, columns,
                   table_type, category, created_by, created_at, version,
                   updated_at, is_active
            FROM design.table_designs
            WHERE design_id = :design_id AND is_active = true
        """)
        
        result = db.execute(query, {"design_id": design_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Table design not found")
        
        design = {
            "design_id": row[0],
            "design_name": row[1],
            "table_name": row[2],
            "description": row[3],
            "columns": json.loads(row[4]) if row[4] else [],
            "table_type": row[5],
            "category": row[6],
            "created_by": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "version": row[9],
            "updated_at": row[10].isoformat() if row[10] else None,
            "is_active": row[11]
        }
        
        return design
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting table design: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting table design: {str(e)}")

@router.put("/tables/{design_id}")
async def update_table_design(
    design_id: str,
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Update an existing table design
    """
    try:
        # Get current design
        current_query = text("SELECT version FROM design.table_designs WHERE design_id = :design_id")
        current_result = db.execute(current_query, {"design_id": design_id})
        current_row = current_result.fetchone()
        
        if not current_row:
            raise HTTPException(status_code=404, detail="Table design not found")
        
        current_version = current_row[0]
        new_version = current_version + 1
        
        # Update design
        update_query = text("""
            UPDATE design.table_designs SET
                design_name = :design_name,
                table_name = :table_name,
                description = :description,
                columns = :columns,
                table_type = :table_type,
                category = :category,
                version = :version,
                updated_at = :updated_at,
                updated_by = :updated_by
            WHERE design_id = :design_id
        """)
        
        db.execute(update_query, {
            "design_id": design_id,
            "design_name": request.get("design_name"),
            "table_name": request.get("table_name"),
            "description": request.get("description", ""),
            "columns": json.dumps(request.get("columns", [])),
            "table_type": request.get("table_type", "custom"),
            "category": request.get("category", "general"),
            "version": new_version,
            "updated_at": datetime.utcnow(),
            "updated_by": user.id
        })
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="UPDATE",
            resource_type="table_design",
            resource_id=design_id,
            details={
                "old_version": current_version,
                "new_version": new_version,
                "changes": request
            }
        )
        
        log_audit_event(db, audit_log)
        
        db.commit()
        
        return {
            "design_id": design_id,
            "version": new_version,
            "message": "Table design updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating table design: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating table design: {str(e)}")

# Mapping Configuration Management
@router.post("/configs")
async def create_mapping_config(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Create a new mapping configuration
    """
    try:
        config_name = request.get("config_name")
        design_id = request.get("design_id")
        source_patterns = request.get("source_patterns", [])
        mapping_rules = request.get("mapping_rules", [])
        priority = request.get("priority", 1)
        
        if not config_name or not design_id:
            raise HTTPException(status_code=400, detail="Config name and design ID are required")
        
        # Verify design exists
        design_query = text("SELECT design_id FROM design.table_designs WHERE design_id = :design_id")
        design_result = db.execute(design_query, {"design_id": design_id})
        if not design_result.fetchone():
            raise HTTPException(status_code=404, detail="Table design not found")
        
        # Generate config ID
        config_id = str(uuid.uuid4())
        
        # Create mapping config
        config_query = text("""
            INSERT INTO design.mapping_configs (
                config_id, config_name, design_id, source_patterns, mapping_rules,
                priority, created_by, created_at, version
            ) VALUES (
                :config_id, :config_name, :design_id, :source_patterns, :mapping_rules,
                :priority, :created_by, :created_at, 1
            )
        """)
        
        db.execute(config_query, {
            "config_id": config_id,
            "config_name": config_name,
            "design_id": design_id,
            "source_patterns": json.dumps(source_patterns),
            "mapping_rules": json.dumps(mapping_rules),
            "priority": priority,
            "created_by": user.id,
            "created_at": datetime.utcnow()
        })
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="CREATE",
            resource_type="mapping_config",
            resource_id=config_id,
            details={
                "config_name": config_name,
                "design_id": design_id,
                "priority": priority,
                "pattern_count": len(source_patterns),
                "rule_count": len(mapping_rules)
            }
        )
        
        log_audit_event(db, audit_log)
        
        db.commit()
        
        return {
            "config_id": config_id,
            "config_name": config_name,
            "message": "Mapping configuration created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating mapping config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating mapping config: {str(e)}")

@router.get("/configs")
async def list_mapping_configs(
    design_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    List mapping configurations with filtering
    """
    try:
        query = """
            SELECT mc.config_id, mc.config_name, mc.design_id, mc.source_patterns,
                   mc.mapping_rules, mc.priority, mc.created_by, mc.created_at,
                   mc.version, mc.updated_at, mc.is_active,
                   td.design_name, td.table_name
            FROM design.mapping_configs mc
            JOIN design.table_designs td ON mc.design_id = td.design_id
            WHERE mc.is_active = true
        """
        params = {}
        
        if design_id:
            query += " AND mc.design_id = :design_id"
            params["design_id"] = design_id
            
        if search:
            query += " AND (mc.config_name ILIKE :search OR td.design_name ILIKE :search)"
            params["search"] = f"%{search}%"
        
        query += " ORDER BY mc.priority DESC, mc.created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(text(query), params)
        configs = []
        
        for row in result.fetchall():
            configs.append({
                "config_id": row[0],
                "config_name": row[1],
                "design_id": row[2],
                "source_patterns": json.loads(row[3]) if row[3] else [],
                "mapping_rules": json.loads(row[4]) if row[4] else [],
                "priority": row[5],
                "created_by": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "version": row[8],
                "updated_at": row[9].isoformat() if row[9] else None,
                "is_active": row[10],
                "design_name": row[11],
                "table_name": row[12]
            })
        
        return {"configs": configs, "count": len(configs)}
        
    except Exception as e:
        logger.error(f"Error listing mapping configs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing mapping configs: {str(e)}")

# AI Matching System
@router.post("/match")
async def match_design_to_file(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Match file headers to existing table designs and mapping configurations
    """
    try:
        headers = request.get("headers", [])
        file_name = request.get("file_name", "")
        file_type = request.get("file_type", "")
        content_preview = request.get("content_preview", "")
        
        if not headers:
            raise HTTPException(status_code=400, detail="Headers are required")
        
        # Get all active mapping configs
        configs_query = text("""
            SELECT mc.config_id, mc.config_name, mc.design_id, mc.source_patterns,
                   mc.mapping_rules, mc.priority,
                   td.design_name, td.table_name, td.columns, td.table_type, td.category
            FROM design.mapping_configs mc
            JOIN design.table_designs td ON mc.design_id = td.design_id
            WHERE mc.is_active = true AND td.is_active = true
            ORDER BY mc.priority DESC
        """)
        
        result = db.execute(configs_query)
        matches = []
        
        for row in result.fetchall():
            config_id = row[0]
            config_name = row[1]
            design_id = row[2]
            source_patterns = json.loads(row[3]) if row[3] else []
            mapping_rules = json.loads(row[4]) if row[4] else []
            priority = row[5]
            design_name = row[6]
            table_name = row[7]
            columns = json.loads(row[8]) if row[8] else []
            table_type = row[9]
            category = row[10]
            
            # Calculate match score
            match_score = calculate_design_match_score(
                headers, file_name, file_type, source_patterns, mapping_rules
            )
            
            if match_score > 0.3:  # Only include relevant matches
                matches.append({
                    "config_id": config_id,
                    "config_name": config_name,
                    "design_id": design_id,
                    "design_name": design_name,
                    "table_name": table_name,
                    "table_type": table_type,
                    "category": category,
                    "match_score": match_score,
                    "priority": priority,
                    "source_patterns": source_patterns,
                    "mapping_rules": mapping_rules,
                    "columns": columns
                })
        
        # Sort by match score and priority
        matches.sort(key=lambda x: (x["match_score"], x["priority"]), reverse=True)
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="MATCH",
            resource_type="file_analysis",
            resource_id=str(uuid.uuid4()),
            details={
                "file_name": file_name,
                "file_type": file_type,
                "header_count": len(headers),
                "match_count": len(matches),
                "best_match_score": matches[0]["match_score"] if matches else 0
            }
        )
        
        log_audit_event(db, audit_log)
        
        return {
            "matches": matches[:10],  # Top 10 matches
            "file_analysis": {
                "headers": headers,
                "file_name": file_name,
                "file_type": file_type,
                "header_count": len(headers)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching design to file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error matching design to file: {str(e)}")

# Audit System
@router.get("/audit")
async def get_audit_logs(
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_power)
):
    """
    Get audit logs with filtering
    """
    try:
        query = """
            SELECT audit_id, user_id, action, resource_type, resource_id,
                   details, timestamp
            FROM design.audit_logs
            WHERE 1=1
        """
        params = {}
        
        if resource_type:
            query += " AND resource_type = :resource_type"
            params["resource_type"] = resource_type
            
        if resource_id:
            query += " AND resource_id = :resource_id"
            params["resource_id"] = resource_id
            
        if action:
            query += " AND action = :action"
            params["action"] = action
            
        if user_id:
            query += " AND user_id = :user_id"
            params["user_id"] = user_id
            
        if start_date:
            query += " AND timestamp >= :start_date"
            params["start_date"] = start_date
            
        if end_date:
            query += " AND timestamp <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY timestamp DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(text(query), params)
        logs = []
        
        for row in result.fetchall():
            logs.append({
                "audit_id": row[0],
                "user_id": row[1],
                "action": row[2],
                "resource_type": row[3],
                "resource_id": row[4],
                "details": json.loads(row[5]) if row[5] else {},
                "timestamp": row[6].isoformat() if row[6] else None
            })
        
        return {"logs": logs, "count": len(logs)}
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting audit logs: {str(e)}")

# Helper Functions
def calculate_design_match_score(headers, file_name, file_type, source_patterns, mapping_rules):
    """Calculate how well a design matches a file"""
    score = 0.0
    
    # Pattern matching (30% weight)
    pattern_score = 0.0
    for pattern in source_patterns:
        if pattern.lower() in file_name.lower():
            pattern_score += 0.3
        if pattern.lower() in file_type.lower():
            pattern_score += 0.2
    
    score += min(pattern_score, 0.3)
    
    # Header matching (50% weight)
    header_score = 0.0
    for rule in mapping_rules:
        source_col = rule.get("source_column", "").lower()
        for header in headers:
            if source_col in header.lower() or header.lower() in source_col:
                header_score += 0.1
    
    score += min(header_score, 0.5)
    
    # File type matching (20% weight)
    if file_type in ["csv", "xlsx", "json"]:
        score += 0.2
    
    return min(score, 1.0)

def log_audit_event(db: Session, audit_log: AuditLog):
    """Log an audit event to the database"""
    try:
        audit_query = text("""
            INSERT INTO design.audit_logs (
                audit_id, user_id, action, resource_type, resource_id,
                details, timestamp
            ) VALUES (
                :audit_id, :user_id, :action, :resource_type, :resource_id,
                :details, :timestamp
            )
        """)
        
        db.execute(audit_query, {
            "audit_id": audit_log.audit_id,
            "user_id": audit_log.user_id,
            "action": audit_log.action,
            "resource_type": audit_log.resource_type,
            "resource_id": audit_log.resource_id,
            "details": json.dumps(audit_log.details),
            "timestamp": audit_log.timestamp
        })
        
    except Exception as e:
        logger.error(f"Error logging audit event: {str(e)}")
        # Don't fail the main operation if audit logging fails 

# Dataset Pipeline Management
@router.post("/datasets")
async def create_dataset(
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Create a new dataset with pipeline configuration
    """
    try:
        dataset_name = request.get("dataset_name")
        description = request.get("description", "")
        source_type = request.get("source_type", "file")  # file, api, database
        pipeline_config = request.get("pipeline_config", {})
        business_owner = request.get("business_owner", "")
        data_steward = request.get("data_steward", "")
        
        if not dataset_name:
            raise HTTPException(status_code=400, detail="Dataset name is required")
        
        # Generate dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Create dataset record
        dataset_query = text("""
            INSERT INTO design.datasets (
                dataset_id, dataset_name, description, source_type, pipeline_config,
                business_owner, data_steward, created_by, created_at, status, version
            ) VALUES (
                :dataset_id, :dataset_name, :description, :source_type, :pipeline_config,
                :business_owner, :data_steward, :created_by, :created_at, 'draft', 1
            )
        """)
        
        db.execute(dataset_query, {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "description": description,
            "source_type": source_type,
            "pipeline_config": json.dumps(pipeline_config),
            "business_owner": business_owner,
            "data_steward": data_steward,
            "created_by": user.id,
            "created_at": datetime.utcnow()
        })
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="CREATE",
            resource_type="dataset",
            resource_id=dataset_id,
            details={
                "dataset_name": dataset_name,
                "source_type": source_type,
                "business_owner": business_owner,
                "data_steward": data_steward
            }
        )
        
        log_audit_event(db, audit_log)
        
        db.commit()
        
        return {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "status": "draft",
            "message": "Dataset created successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating dataset: {str(e)}")

@router.get("/datasets")
async def list_datasets(
    status: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    List datasets with filtering and search
    """
    try:
        query = """
            SELECT dataset_id, dataset_name, description, source_type, pipeline_config,
                   business_owner, data_steward, created_by, created_at, status, version,
                   updated_at, is_active
            FROM design.datasets
            WHERE is_active = true
        """
        params = {}
        
        if status:
            query += " AND status = :status"
            params["status"] = status
            
        if source_type:
            query += " AND source_type = :source_type"
            params["source_type"] = source_type
            
        if search:
            query += " AND (dataset_name ILIKE :search OR description ILIKE :search OR business_owner ILIKE :search)"
            params["search"] = f"%{search}%"
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(text(query), params)
        datasets = []
        
        for row in result.fetchall():
            datasets.append({
                "dataset_id": row[0],
                "dataset_name": row[1],
                "description": row[2],
                "source_type": row[3],
                "pipeline_config": json.loads(row[4]) if row[4] else {},
                "business_owner": row[5],
                "data_steward": row[6],
                "created_by": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
                "status": row[9],
                "version": row[10],
                "updated_at": row[11].isoformat() if row[11] else None,
                "is_active": row[12]
            })
        
        return {
            "datasets": datasets,
            "total": len(datasets),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing datasets: {str(e)}")

@router.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Get dataset details by ID
    """
    try:
        query = text("""
            SELECT dataset_id, dataset_name, description, source_type, pipeline_config,
                   business_owner, data_steward, created_by, created_at, status, version,
                   updated_at, is_active
            FROM design.datasets
            WHERE dataset_id = :dataset_id AND is_active = true
        """)
        
        result = db.execute(query, {"dataset_id": dataset_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = {
            "dataset_id": row[0],
            "dataset_name": row[1],
            "description": row[2],
            "source_type": row[3],
            "pipeline_config": json.loads(row[4]) if row[4] else {},
            "business_owner": row[5],
            "data_steward": row[6],
            "created_by": row[7],
            "created_at": row[8].isoformat() if row[8] else None,
            "status": row[9],
            "version": row[10],
            "updated_at": row[11].isoformat() if row[11] else None,
            "is_active": row[12]
        }
        
        return dataset
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dataset: {str(e)}")

@router.post("/datasets/{dataset_id}/pipeline")
async def create_pipeline_stage(
    dataset_id: str,
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Create a new pipeline stage for a dataset
    """
    try:
        stage_name = request.get("stage_name")
        stage_type = request.get("stage_type")  # upload, staging, filtered, final
        stage_config = request.get("stage_config", {})
        validation_rules = request.get("validation_rules", [])
        approval_required = request.get("approval_required", False)
        approvers = request.get("approvers", [])
        
        if not stage_name or not stage_type:
            raise HTTPException(status_code=400, detail="Stage name and type are required")
        
        # Validate stage type
        valid_stages = ["upload", "staging", "filtered", "final", "custom"]
        if stage_type not in valid_stages:
            raise HTTPException(status_code=400, detail=f"Invalid stage type. Must be one of: {valid_stages}")
        
        # Generate stage ID
        stage_id = str(uuid.uuid4())
        
        # Create pipeline stage
        stage_query = text("""
            INSERT INTO design.pipeline_stages (
                stage_id, dataset_id, stage_name, stage_type, stage_config,
                validation_rules, approval_required, approvers, created_by, created_at,
                status, sequence_order
            ) VALUES (
                :stage_id, :dataset_id, :stage_name, :stage_type, :stage_config,
                :validation_rules, :approval_required, :approvers, :created_by, :created_at,
                'active', (SELECT COALESCE(MAX(sequence_order), 0) + 1 FROM design.pipeline_stages WHERE dataset_id = :dataset_id)
            )
        """)
        
        db.execute(stage_query, {
            "stage_id": stage_id,
            "dataset_id": dataset_id,
            "stage_name": stage_name,
            "stage_type": stage_type,
            "stage_config": json.dumps(stage_config),
            "validation_rules": json.dumps(validation_rules),
            "approval_required": approval_required,
            "approvers": json.dumps(approvers),
            "created_by": user.id,
            "created_at": datetime.utcnow()
        })
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="CREATE_STAGE",
            resource_type="pipeline_stage",
            resource_id=stage_id,
            details={
                "dataset_id": dataset_id,
                "stage_name": stage_name,
                "stage_type": stage_type,
                "approval_required": approval_required
            }
        )
        
        log_audit_event(db, audit_log)
        
        db.commit()
        
        return {
            "stage_id": stage_id,
            "stage_name": stage_name,
            "stage_type": stage_type,
            "message": "Pipeline stage created successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating pipeline stage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating pipeline stage: {str(e)}")

@router.get("/datasets/{dataset_id}/pipeline")
async def get_dataset_pipeline(
    dataset_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Get pipeline stages for a dataset
    """
    try:
        query = text("""
            SELECT stage_id, stage_name, stage_type, stage_config, validation_rules,
                   approval_required, approvers, created_by, created_at, status,
                   sequence_order, updated_at
            FROM design.pipeline_stages
            WHERE dataset_id = :dataset_id AND status = 'active'
            ORDER BY sequence_order ASC
        """)
        
        result = db.execute(query, {"dataset_id": dataset_id})
        stages = []
        
        for row in result.fetchall():
            stages.append({
                "stage_id": row[0],
                "stage_name": row[1],
                "stage_type": row[2],
                "stage_config": json.loads(row[3]) if row[3] else {},
                "validation_rules": json.loads(row[4]) if row[4] else [],
                "approval_required": row[5],
                "approvers": json.loads(row[6]) if row[6] else [],
                "created_by": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
                "status": row[9],
                "sequence_order": row[10],
                "updated_at": row[11].isoformat() if row[11] else None
            })
        
        return {
            "dataset_id": dataset_id,
            "stages": stages,
            "total_stages": len(stages)
        }
        
    except Exception as e:
        logger.error(f"Error getting dataset pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dataset pipeline: {str(e)}")

@router.post("/datasets/{dataset_id}/upload")
async def upload_dataset_file(
    dataset_id: str,
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    Upload a file for dataset processing
    """
    try:
        file_name = request.get("file_name")
        file_size = request.get("file_size")
        file_type = request.get("file_type")
        file_path = request.get("file_path")
        metadata = request.get("metadata", {})
        
        if not file_name or not file_path:
            raise HTTPException(status_code=400, detail="File name and path are required")
        
        # Generate upload ID
        upload_id = str(uuid.uuid4())
        
        # Create upload record
        upload_query = text("""
            INSERT INTO design.dataset_uploads (
                upload_id, dataset_id, file_name, file_size, file_type, file_path,
                metadata, uploaded_by, uploaded_at, status, current_stage
            ) VALUES (
                :upload_id, :dataset_id, :file_name, :file_size, :file_type, :file_path,
                :metadata, :uploaded_by, :uploaded_at, 'uploaded', 'upload'
            )
        """)
        
        db.execute(upload_query, {
            "upload_id": upload_id,
            "dataset_id": dataset_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "file_path": file_path,
            "metadata": json.dumps(metadata),
            "uploaded_by": user.id,
            "uploaded_at": datetime.utcnow()
        })
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="UPLOAD",
            resource_type="dataset_upload",
            resource_id=upload_id,
            details={
                "dataset_id": dataset_id,
                "file_name": file_name,
                "file_size": file_size,
                "file_type": file_type
            }
        )
        
        log_audit_event(db, audit_log)
        
        db.commit()
        
        return {
            "upload_id": upload_id,
            "dataset_id": dataset_id,
            "file_name": file_name,
            "status": "uploaded",
            "current_stage": "upload",
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading dataset file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading dataset file: {str(e)}")

@router.post("/uploads/{upload_id}/approve")
async def approve_upload_stage(
    upload_id: str,
    request: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin_or_power)
):
    """
    Approve a dataset upload for the next stage
    """
    try:
        approval_notes = request.get("approval_notes", "")
        next_stage = request.get("next_stage")
        
        # Get current upload status
        upload_query = text("""
            SELECT u.upload_id, u.dataset_id, u.current_stage, u.status,
                   p.approval_required, p.approvers
            FROM design.dataset_uploads u
            LEFT JOIN design.pipeline_stages p ON u.dataset_id = p.dataset_id AND u.current_stage = p.stage_type
            WHERE u.upload_id = :upload_id
        """)
        
        result = db.execute(upload_query, {"upload_id": upload_id})
        upload = result.fetchone()
        
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        approval_required = bool(upload[4]) if upload[4] is not None else False
        if approval_required:
            # Check if user is in approvers list
            approvers = json.loads(upload[5]) if upload[5] else []
            if str(user.id) not in approvers and user.role != "admin":
                raise HTTPException(status_code=403, detail="Not authorized to approve this upload")
        
        # Update upload status
        update_query = text("""
            UPDATE design.dataset_uploads
            SET status = 'approved', current_stage = :next_stage, approved_by = :approved_by,
                approved_at = :approved_at, approval_notes = :approval_notes
            WHERE upload_id = :upload_id
        """)
        
        db.execute(update_query, {
            "next_stage": next_stage,
            "approved_by": user.id,
            "approved_at": datetime.utcnow(),
            "approval_notes": approval_notes,
            "upload_id": upload_id
        })
        
        # Log audit event
        audit_log = AuditLog(
            user_id=str(user.id),
            action="APPROVE",
            resource_type="dataset_upload",
            resource_id=upload_id,
            details={
                "dataset_id": upload[1],
                "current_stage": upload[2],
                "next_stage": next_stage,
                "approval_notes": approval_notes
            }
        )
        
        log_audit_event(db, audit_log)
        
        db.commit()
        
        return {
            "upload_id": upload_id,
            "status": "approved",
            "current_stage": next_stage,
            "approved_by": user.id,
            "message": "Upload approved successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error approving upload: {str(e)}")

@router.get("/uploads")
async def list_dataset_uploads(
    dataset_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(require_authenticated_user)
):
    """
    List dataset uploads with filtering
    """
    try:
        query = """
            SELECT upload_id, dataset_id, file_name, file_size, file_type,
                   uploaded_by, uploaded_at, status, current_stage, approved_by,
                   approved_at, approval_notes
            FROM design.dataset_uploads
            WHERE 1=1
        """
        params = {}
        
        if dataset_id:
            query += " AND dataset_id = :dataset_id"
            params["dataset_id"] = dataset_id
            
        if status:
            query += " AND status = :status"
            params["status"] = status
            
        if stage:
            query += " AND current_stage = :stage"
            params["stage"] = stage
        
        query += " ORDER BY uploaded_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = db.execute(text(query), params)
        uploads = []
        
        for row in result.fetchall():
            uploads.append({
                "upload_id": row[0],
                "dataset_id": row[1],
                "file_name": row[2],
                "file_size": row[3],
                "file_type": row[4],
                "uploaded_by": row[5],
                "uploaded_at": row[6].isoformat() if row[6] else None,
                "status": row[7],
                "current_stage": row[8],
                "approved_by": row[9],
                "approved_at": row[10].isoformat() if row[10] else None,
                "approval_notes": row[11]
            })
        
        return {
            "uploads": uploads,
            "total": len(uploads),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing uploads: {str(e)}") 