"""
Plugin Marketplace Router
Provides endpoints for plugin management, execution, and marketplace functionality
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import json
import yaml
from datetime import datetime, timedelta

from ..services.database_service import get_db
from ..routers.admin import require_authenticated_user, require_admin_or_power
from ..models import User
from ..services.plugin_service import plugin_service
from dataclasses import asdict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/plugin-marketplace", tags=["plugin-marketplace"])

@router.get("/plugins")
async def list_plugins(
    category: Optional[str] = None,
    tags: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """List available plugins with optional filtering"""
    try:
        tag_list = tags.split(',') if tags else None
        
        plugins = plugin_service.list_plugins(
            category=category,
            tags=tag_list,
            is_active=is_active
        )
        
        return {
            "success": True,
            "plugins": [asdict(plugin) for plugin in plugins],
            "total_count": len(plugins),
            "categories": list(set(p.category for p in plugins)),
            "tags": list(set(tag for p in plugins for tag in p.tags))
        }
        
    except Exception as e:
        logger.error(f"Error listing plugins: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list plugins: {str(e)}")

@router.get("/plugins/{plugin_id}")
async def get_plugin_details(
    plugin_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get detailed information about a specific plugin"""
    try:
        plugin = plugin_service.get_plugin(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        # Get execution history
        executions = plugin_service.list_executions(plugin_id=plugin_id)
        
        return {
            "success": True,
            "plugin": asdict(plugin),
            "execution_history": [asdict(execution) for execution in executions[-10:]],  # Last 10 executions
            "total_executions": len(executions),
            "successful_executions": len([e for e in executions if e.status == "completed"]),
            "failed_executions": len([e for e in executions if e.status == "failed"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get plugin details: {str(e)}")

@router.post("/plugins/register")
async def register_plugin(
    manifest_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Register a new plugin from manifest file"""
    try:
        # Read manifest file
        content = await manifest_file.read()
        
        if manifest_file.filename.endswith('.json'):
            manifest_data = json.loads(content.decode('utf-8'))
        elif manifest_file.filename.endswith('.yaml') or manifest_file.filename.endswith('.yml'):
            manifest_data = yaml.safe_load(content.decode('utf-8'))
        else:
            raise HTTPException(status_code=400, detail="Manifest file must be JSON or YAML")
        
        # Register plugin
        plugin_id = plugin_service.register_plugin(manifest_data)
        
        return {
            "success": True,
            "plugin_id": plugin_id,
            "message": "Plugin registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register plugin: {str(e)}")

@router.post("/plugins/{plugin_id}/execute")
async def execute_plugin(
    plugin_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Execute a plugin
    
    Request:
    {
        "parameters": {...},
        "input_datasets": {...}
    }
    """
    try:
        parameters = request.get("parameters", {})
        input_datasets = request.get("input_datasets", {})
        
        # Execute plugin
        execution_id = plugin_service.execute_plugin(
            plugin_id=plugin_id,
            parameters=parameters,
            input_datasets=input_datasets
        )
        
        return {
            "success": True,
            "execution_id": execution_id,
            "plugin_id": plugin_id,
            "message": "Plugin execution started"
        }
        
    except Exception as e:
        logger.error(f"Error executing plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute plugin: {str(e)}")

@router.get("/executions/{execution_id}")
async def get_execution_status(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get execution status and results"""
    try:
        execution = plugin_service.get_execution_status(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "success": True,
            "execution": asdict(execution)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get execution status: {str(e)}")

@router.get("/executions")
async def list_executions(
    plugin_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """List executions with optional filtering"""
    try:
        executions = plugin_service.list_executions(
            plugin_id=plugin_id,
            status=status
        )
        
        return {
            "success": True,
            "executions": [asdict(execution) for execution in executions],
            "total_count": len(executions),
            "status_counts": {
                "running": len([e for e in executions if e.status == "running"]),
                "completed": len([e for e in executions if e.status == "completed"]),
                "failed": len([e for e in executions if e.status == "failed"]),
                "cancelled": len([e for e in executions if e.status == "cancelled"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list executions: {str(e)}")

@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Cancel a running execution"""
    try:
        success = plugin_service.cancel_execution(execution_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Execution not found or cannot be cancelled")
        
        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Execution cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel execution: {str(e)}")

@router.put("/plugins/{plugin_id}/status")
async def update_plugin_status(
    plugin_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Update plugin active status"""
    try:
        is_active = request.get("is_active")
        if is_active is None:
            raise HTTPException(status_code=400, detail="is_active parameter is required")
        
        success = plugin_service.update_plugin_status(plugin_id, is_active)
        
        if not success:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return {
            "success": True,
            "plugin_id": plugin_id,
            "is_active": is_active,
            "message": f"Plugin {'activated' if is_active else 'deactivated'} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plugin status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update plugin status: {str(e)}")

@router.delete("/plugins/{plugin_id}")
async def delete_plugin(
    plugin_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """Delete a plugin"""
    try:
        success = plugin_service.delete_plugin(plugin_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        return {
            "success": True,
            "plugin_id": plugin_id,
            "message": "Plugin deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete plugin: {str(e)}")

@router.get("/marketplace/categories")
async def get_marketplace_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get available plugin categories"""
    try:
        plugins = plugin_service.list_plugins()
        
        categories = {}
        for plugin in plugins:
            if plugin.category not in categories:
                categories[plugin.category] = {
                    "name": plugin.category,
                    "plugin_count": 0,
                    "active_plugins": 0,
                    "tags": set()
                }
            
            categories[plugin.category]["plugin_count"] += 1
            if plugin.is_active:
                categories[plugin.category]["active_plugins"] += 1
            
            categories[plugin.category]["tags"].update(plugin.tags)
        
        # Convert sets to lists for JSON serialization
        for category in categories.values():
            category["tags"] = list(category["tags"])
        
        return {
            "success": True,
            "categories": list(categories.values()),
            "total_categories": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error getting marketplace categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@router.get("/marketplace/featured")
async def get_featured_plugins(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get featured plugins (most used/rated)"""
    try:
        plugins = plugin_service.list_plugins(is_active=True)
        
        # Calculate plugin scores based on execution success rate
        plugin_scores = []
        for plugin in plugins:
            executions = plugin_service.list_executions(plugin_id=plugin.plugin_id)
            
            if executions:
                success_rate = len([e for e in executions if e.status == "completed"]) / len(executions)
                plugin_scores.append((plugin, success_rate))
            else:
                plugin_scores.append((plugin, 0.0))
        
        # Sort by success rate and return top plugins
        plugin_scores.sort(key=lambda x: x[1], reverse=True)
        featured_plugins = [asdict(plugin) for plugin, score in plugin_scores[:limit]]
        
        return {
            "success": True,
            "featured_plugins": featured_plugins,
            "total_featured": len(featured_plugins)
        }
        
    except Exception as e:
        logger.error(f"Error getting featured plugins: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get featured plugins: {str(e)}")

@router.post("/marketplace/search")
async def search_plugins(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Search plugins by various criteria
    
    Request:
    {
        "query": "search term",
        "category": "category",
        "tags": ["tag1", "tag2"],
        "author": "author name",
        "min_version": "1.0.0"
    }
    """
    try:
        query = request.get("query", "").lower()
        category = request.get("category")
        tags = request.get("tags", [])
        author = request.get("author")
        min_version = request.get("min_version")
        
        # Get all plugins
        plugins = plugin_service.list_plugins(is_active=True)
        
        # Apply filters
        filtered_plugins = []
        for plugin in plugins:
            # Text search
            if query:
                search_text = f"{plugin.name} {plugin.description} {' '.join(plugin.tags)}".lower()
                if query not in search_text:
                    continue
            
            # Category filter
            if category and plugin.category != category:
                continue
            
            # Tags filter
            if tags and not any(tag in plugin.tags for tag in tags):
                continue
            
            # Author filter
            if author and author.lower() not in plugin.author.lower():
                continue
            
            # Version filter
            if min_version:
                # Simple version comparison (in production, use proper version comparison)
                if plugin.version < min_version:
                    continue
            
            filtered_plugins.append(plugin)
        
        return {
            "success": True,
            "plugins": [asdict(plugin) for plugin in filtered_plugins],
            "total_results": len(filtered_plugins),
            "search_criteria": {
                "query": query,
                "category": category,
                "tags": tags,
                "author": author,
                "min_version": min_version
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching plugins: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search plugins: {str(e)}")

@router.get("/marketplace/statistics")
async def get_marketplace_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get marketplace statistics"""
    try:
        plugins = plugin_service.list_plugins()
        executions = plugin_service.list_executions()
        
        # Calculate statistics
        total_plugins = len(plugins)
        active_plugins = len([p for p in plugins if p.is_active])
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == "completed"])
        
        # Category distribution
        category_distribution = {}
        for plugin in plugins:
            if plugin.category not in category_distribution:
                category_distribution[plugin.category] = 0
            category_distribution[plugin.category] += 1
        
        # Tag distribution
        tag_distribution = {}
        for plugin in plugins:
            for tag in plugin.tags:
                if tag not in tag_distribution:
                    tag_distribution[tag] = 0
                tag_distribution[tag] += 1
        
        # Execution trends (last 30 days)
        recent_executions = [
            e for e in executions 
            if datetime.fromisoformat(e.start_time) > datetime.now() - timedelta(days=30)
        ]
        
        return {
            "success": True,
            "statistics": {
                "total_plugins": total_plugins,
                "active_plugins": active_plugins,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
                "recent_executions": len(recent_executions),
                "category_distribution": category_distribution,
                "top_tags": dict(sorted(tag_distribution.items(), key=lambda x: x[1], reverse=True)[:10])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting marketplace statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}") 