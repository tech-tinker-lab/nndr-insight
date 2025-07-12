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