"""
Plugin Service for NNDR Insight
Implements plugin execution framework, marketplace, and lifecycle management
"""

import os
import json
import yaml
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import logging
from datetime import datetime
import uuid
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class PluginManifest:
    """Plugin manifest for registration"""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    category: str
    tags: List[str]
    required_datasets: List[str]
    required_ai_models: List[str]
    outputs: List[str]
    lifecycle_stages: List[str]  # preprocess, transform, analyze, output
    parameters: Dict[str, Any]
    dependencies: List[str]
    entry_point: str
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class PluginExecution:
    """Plugin execution record"""
    execution_id: str
    plugin_id: str
    status: str  # running, completed, failed, cancelled
    start_time: str
    end_time: Optional[str] = None
    progress: float = 0.0
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    input_datasets: Optional[List[str]] = None
    output_files: Optional[List[str]] = None

class PluginService:
    """Comprehensive plugin management and execution service"""
    
    def __init__(self, plugins_path: str = "plugins"):
        self.plugins_path = Path(plugins_path)
        self.plugins_path.mkdir(parents=True, exist_ok=True)
        
        self.plugins: Dict[str, PluginManifest] = {}
        self.executions: Dict[str, PluginExecution] = {}
        self.plugin_instances: Dict[str, Any] = {}
        
        # Load existing plugins
        self._load_plugins()
    
    def register_plugin(self, manifest_data: Dict[str, Any]) -> str:
        """
        Register a new plugin
        
        Args:
            manifest_data: Plugin manifest data
            
        Returns:
            Plugin ID
        """
        try:
            plugin_id = manifest_data.get('plugin_id') or f"plugin_{uuid.uuid4().hex[:8]}"
            # Remove plugin_id from manifest_data to avoid multiple values error
            manifest_data_clean = dict(manifest_data)
            if 'plugin_id' in manifest_data_clean:
                del manifest_data_clean['plugin_id']
            # Ensure all required fields are present and not None
            required_fields = [
                'name', 'version', 'description', 'author', 'category', 'tags',
                'required_datasets', 'required_ai_models', 'outputs', 'lifecycle_stages',
                'parameters', 'dependencies', 'entry_point'
            ]
            str_fields = ['name', 'version', 'description', 'author', 'category', 'entry_point']
            dict_fields = ['parameters']
            for field in required_fields:
                if field not in manifest_data_clean or manifest_data_clean[field] is None:
                    if field in ['tags', 'required_datasets', 'required_ai_models', 'outputs', 'lifecycle_stages', 'dependencies']:
                        manifest_data_clean[field] = []
                    elif field in dict_fields:
                        manifest_data_clean[field] = {}
                    elif field in str_fields:
                        manifest_data_clean[field] = ""
                    else:
                        manifest_data_clean[field] = ""
            # Ensure parameters is always a dict
            if manifest_data_clean['parameters'] is None:
                manifest_data_clean['parameters'] = {}
            # Create manifest
            manifest = PluginManifest(
                plugin_id=plugin_id,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                **manifest_data_clean
            )
            
            # Save manifest
            self._save_manifest(manifest)
            
            # Register in memory
            self.plugins[plugin_id] = manifest
            
            logger.info(f"Registered plugin: {manifest.name} ({plugin_id})")
            return plugin_id
            
        except Exception as e:
            logger.error(f"Error registering plugin: {str(e)}")
            raise
    
    def list_plugins(self, 
                    category: Optional[str] = None,
                    tags: Optional[List[str]] = None,
                    is_active: Optional[bool] = None) -> List[PluginManifest]:
        """List plugins with optional filtering"""
        plugins = list(self.plugins.values())
        
        if category:
            plugins = [p for p in plugins if p.category == category]
        
        if tags:
            plugins = [p for p in plugins if any(tag in p.tags for tag in tags)]
        
        if is_active is not None:
            plugins = [p for p in plugins if p.is_active == is_active]
        
        return plugins
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginManifest]:
        """Get plugin by ID"""
        return self.plugins.get(plugin_id)
    
    def execute_plugin(self, 
                      plugin_id: str,
                      parameters: Dict[str, Any] = None,
                      input_datasets: Dict[str, Any] = None) -> str:
        """
        Execute a plugin
        
        Args:
            plugin_id: Plugin ID to execute
            parameters: Plugin parameters
            input_datasets: Input datasets
            
        Returns:
            Execution ID
        """
        try:
            # Get plugin
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                raise ValueError(f"Plugin {plugin_id} not found")
            
            if not plugin.is_active:
                raise ValueError(f"Plugin {plugin_id} is not active")
            
            # Create execution record
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            execution = PluginExecution(
                execution_id=execution_id,
                plugin_id=plugin_id,
                status="running",
                start_time=datetime.now().isoformat(),
                parameters=parameters if parameters is not None else {},
                input_datasets=list(input_datasets.keys()) if input_datasets else [],
                results=None,
                error_message=None,
                output_files=[]
            )
            
            # Store execution
            self.executions[execution_id] = execution
            self._save_execution(execution)
            
            # Execute plugin
            self._execute_plugin_async(execution, plugin, parameters, input_datasets)
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Error executing plugin: {str(e)}")
            raise
    
    def _execute_plugin_async(self, execution: PluginExecution, plugin: PluginManifest, 
                            parameters: Dict[str, Any], input_datasets: Dict[str, Any]):
        """Execute plugin asynchronously"""
        try:
            # Load plugin module
            plugin_module = self._load_plugin_module(plugin)
            
            # Execute lifecycle stages
            results = {}
            
            for stage in plugin.lifecycle_stages:
                execution.progress = (plugin.lifecycle_stages.index(stage) / len(plugin.lifecycle_stages)) * 100
                self._save_execution(execution)
                
                if stage == "preprocess":
                    results[stage] = self._execute_preprocess(plugin_module, input_datasets, parameters)
                elif stage == "transform":
                    results[stage] = self._execute_transform(plugin_module, results.get("preprocess", {}), parameters)
                elif stage == "analyze":
                    results[stage] = self._execute_analyze(plugin_module, results.get("transform", {}), parameters)
                elif stage == "output":
                    results[stage] = self._execute_output(plugin_module, results, parameters)
            
            # Update execution
            execution.status = "completed"
            execution.end_time = datetime.now().isoformat()
            execution.progress = 100.0
            execution.results = results
            
            self._save_execution(execution)
            
            logger.info(f"Plugin execution completed: {execution.execution_id}")
            
        except Exception as e:
            # Update execution with error
            execution.status = "failed"
            execution.end_time = datetime.now().isoformat()
            execution.error_message = str(e)
            
            self._save_execution(execution)
            logger.error(f"Plugin execution failed: {execution.execution_id} - {str(e)}")
    
    def _execute_preprocess(self, plugin_module, input_datasets: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute preprocessing stage"""
        if hasattr(plugin_module, 'preprocess'):
            return plugin_module.preprocess(input_datasets, parameters)
        return {"status": "skipped", "message": "No preprocessing required"}
    
    def _execute_transform(self, plugin_module, preprocess_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation stage"""
        if hasattr(plugin_module, 'transform'):
            return plugin_module.transform(preprocess_results, parameters)
        return {"status": "skipped", "message": "No transformation required"}
    
    def _execute_analyze(self, plugin_module, transform_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis stage"""
        if hasattr(plugin_module, 'analyze'):
            return plugin_module.analyze(transform_results, parameters)
        return {"status": "skipped", "message": "No analysis required"}
    
    def _execute_output(self, plugin_module, all_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute output stage"""
        if hasattr(plugin_module, 'output'):
            return plugin_module.output(all_results, parameters)
        return {"status": "skipped", "message": "No output processing required"}
    
    def _load_plugin_module(self, plugin: PluginManifest):
        """Load plugin module"""
        try:
            # Create plugin directory if it doesn't exist
            plugin_dir = self.plugins_path / plugin.plugin_id
            plugin_dir.mkdir(exist_ok=True)
            
            # Create plugin module if it doesn't exist
            plugin_file = plugin_dir / f"{plugin.plugin_id}.py"
            if not plugin_file.exists():
                self._create_plugin_template(plugin)
            
            # Import plugin module
            spec = importlib.util.spec_from_file_location(
                plugin.plugin_id, 
                plugin_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            logger.error(f"Error loading plugin module: {str(e)}")
            raise
    
    def _create_plugin_template(self, plugin: PluginManifest):
        """Create plugin template file"""
        template = f'''
"""
{plugin.name} Plugin
{plugin.description}
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def preprocess(input_datasets: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess input datasets
    
    Args:
        input_datasets: Dictionary of input datasets
        parameters: Plugin parameters
        
    Returns:
        Preprocessed data
    """
    logger.info("Starting preprocessing stage")
    
    # Add your preprocessing logic here
    processed_data = {{}}
    
    for dataset_name, dataset in input_datasets.items():
        if isinstance(dataset, pd.DataFrame):
            # Process DataFrame
            processed_data[dataset_name] = dataset.copy()
        else:
            # Process other data types
            processed_data[dataset_name] = dataset
    
    logger.info("Preprocessing completed")
    return processed_data

def transform(preprocess_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform preprocessed data
    
    Args:
        preprocess_results: Results from preprocessing stage
        parameters: Plugin parameters
        
    Returns:
        Transformed data
    """
    logger.info("Starting transformation stage")
    
    # Add your transformation logic here
    transformed_data = {{}}
    
    for key, data in preprocess_results.items():
        if isinstance(data, pd.DataFrame):
            # Apply transformations
            transformed_data[key] = data.copy()
        else:
            transformed_data[key] = data
    
    logger.info("Transformation completed")
    return transformed_data

def analyze(transform_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze transformed data
    
    Args:
        transform_results: Results from transformation stage
        parameters: Plugin parameters
        
    Returns:
        Analysis results
    """
    logger.info("Starting analysis stage")
    
    # Add your analysis logic here
    analysis_results = {{
        "summary": "Analysis completed",
        "metrics": {{}},
        "insights": []
    }}
    
    logger.info("Analysis completed")
    return analysis_results

def output(all_results: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate output from all previous stages
    
    Args:
        all_results: Results from all previous stages
        parameters: Plugin parameters
        
    Returns:
        Final output
    """
    logger.info("Starting output stage")
    
    # Add your output generation logic here
    output_data = {{
        "status": "completed",
        "results": all_results,
        "output_files": [],
        "visualizations": []
    }}
    
    logger.info("Output generation completed")
    return output_data
'''
        
        plugin_file = self.plugins_path / plugin.plugin_id / f"{plugin.plugin_id}.py"
        with open(plugin_file, 'w') as f:
            f.write(template)
    
    def get_execution_status(self, execution_id: str) -> Optional[PluginExecution]:
        """Get execution status"""
        return self.executions.get(execution_id)
    
    def list_executions(self, 
                       plugin_id: str = None,
                       status: str = None) -> List[PluginExecution]:
        """List executions with optional filtering"""
        executions = list(self.executions.values())
        
        if plugin_id:
            executions = [e for e in executions if e.plugin_id == plugin_id]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        return executions
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status == "running":
            execution.status = "cancelled"
            execution.end_time = datetime.now().isoformat()
            self._save_execution(execution)
            return True
        
        return False
    
    def update_plugin_status(self, plugin_id: str, is_active: bool) -> bool:
        """Update plugin active status"""
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            return False
        
        plugin.is_active = is_active
        plugin.updated_at = datetime.now().isoformat()
        
        self._save_manifest(plugin)
        return True
    
    def delete_plugin(self, plugin_id: str) -> bool:
        """Delete a plugin"""
        if plugin_id not in self.plugins:
            return False
        
        # Remove plugin directory
        plugin_dir = self.plugins_path / plugin_id
        if plugin_dir.exists():
            import shutil
            shutil.rmtree(plugin_dir)
        
        # Remove from memory
        del self.plugins[plugin_id]
        
        # Remove manifest file
        manifest_file = self.plugins_path / f"{plugin_id}_manifest.json"
        if manifest_file.exists():
            manifest_file.unlink()
        
        return True
    
    def _save_manifest(self, manifest: PluginManifest):
        """Save plugin manifest to file"""
        try:
            manifest_file = self.plugins_path / f"{manifest.plugin_id}_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(asdict(manifest), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving manifest: {str(e)}")
    
    def _save_execution(self, execution: PluginExecution):
        """Save execution record to file"""
        try:
            execution_file = self.plugins_path / f"{execution.execution_id}_execution.json"
            with open(execution_file, 'w') as f:
                json.dump(asdict(execution), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving execution: {str(e)}")
    
    def _load_plugins(self):
        """Load existing plugins from disk"""
        try:
            for manifest_file in self.plugins_path.glob("*_manifest.json"):
                try:
                    with open(manifest_file, 'r') as f:
                        manifest_data = json.load(f)
                    # Ensure all required fields are present and not None
                    required_fields = [
                        'plugin_id', 'name', 'version', 'description', 'author', 'category', 'tags',
                        'required_datasets', 'required_ai_models', 'outputs', 'lifecycle_stages',
                        'parameters', 'dependencies', 'entry_point', 'is_active', 'created_at', 'updated_at'
                    ]
                    str_fields = ['plugin_id', 'name', 'version', 'description', 'author', 'category', 'entry_point', 'created_at', 'updated_at']
                    dict_fields = ['parameters']
                    for field in required_fields:
                        if field not in manifest_data or manifest_data[field] is None:
                            if field in ['tags', 'required_datasets', 'required_ai_models', 'outputs', 'lifecycle_stages', 'dependencies']:
                                manifest_data[field] = []
                            elif field in dict_fields:
                                manifest_data[field] = {}
                            elif field in str_fields:
                                manifest_data[field] = ""
                            elif field == 'is_active':
                                manifest_data[field] = True
                            else:
                                manifest_data[field] = ""
                    # Ensure parameters is always a dict
                    if manifest_data['parameters'] is None:
                        manifest_data['parameters'] = {}
                    manifest = PluginManifest(**manifest_data)
                    self.plugins[manifest.plugin_id] = manifest
                except Exception as e:
                    logger.error(f"Error loading manifest from {manifest_file}: {str(e)}")
            # Load execution records
            for execution_file in self.plugins_path.glob("*_execution.json"):
                try:
                    with open(execution_file, 'r') as f:
                        execution_data = json.load(f)
                    # Ensure all required fields are present and not None
                    exec_required_fields = [
                        'execution_id', 'plugin_id', 'status', 'start_time', 'end_time', 'progress',
                        'results', 'error_message', 'parameters', 'input_datasets', 'output_files'
                    ]
                    for field in exec_required_fields:
                        if field not in execution_data or execution_data[field] is None:
                            if field == 'progress':
                                execution_data[field] = 0.0
                            elif field == 'results':
                                execution_data[field] = None
                            elif field == 'error_message':
                                execution_data[field] = None
                            elif field == 'parameters':
                                execution_data[field] = {}
                            elif field == 'end_time':
                                execution_data[field] = None
                            elif field in ['input_datasets', 'output_files']:
                                execution_data[field] = []
                            else:
                                execution_data[field] = ""
                    # Ensure parameters is always a dict
                    if execution_data['parameters'] is None:
                        execution_data['parameters'] = {}
                    # Ensure all str fields are not None
                    str_fields_exec = ['execution_id', 'plugin_id', 'status', 'start_time', 'end_time']
                    for field in str_fields_exec:
                        if field in execution_data and execution_data[field] is None:
                            execution_data[field] = ""
                    execution = PluginExecution(**execution_data)
                    self.executions[execution.execution_id] = execution
                except Exception as e:
                    logger.error(f"Error loading execution from {execution_file}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading plugins: {str(e)}")

# Global instance
plugin_service = PluginService()

# Built-in plugins
def register_builtin_plugins():
    """Register built-in plugins"""
    
    # NNDR Insight Plugin
    nndr_manifest = {
        "plugin_id": "nndr_insight",
        "name": "NNDR Insight",
        "version": "1.0.0",
        "description": "Business rate forecasting and non-rated property identification",
        "author": "NNDR Insight Team",
        "category": "business_rates",
        "tags": ["forecasting", "anomaly_detection", "property_analysis"],
        "required_datasets": ["properties", "ratepayers", "valuations"],
        "required_ai_models": ["forecasting", "anomaly_detection"],
        "outputs": ["forecasts", "anomalies", "insights"],
        "lifecycle_stages": ["preprocess", "transform", "analyze", "output"],
        "parameters": {
            "forecast_periods": 12,
            "anomaly_threshold": 2.0,
            "confidence_level": "medium"
        },
        "dependencies": ["pandas", "numpy", "prophet"],
        "entry_point": "nndr_insight.py"
    }
    
    # Finance Insight Plugin
    finance_manifest = {
        "plugin_id": "finance_insight",
        "name": "Finance Insight",
        "version": "1.0.0",
        "description": "Financial analysis and spend tracking",
        "author": "NNDR Insight Team",
        "category": "finance",
        "tags": ["spend_analysis", "grant_tracking", "vendor_risk"],
        "required_datasets": ["transactions", "grants", "vendors"],
        "required_ai_models": ["anomaly_detection", "risk_assessment"],
        "outputs": ["spend_analysis", "risk_scores", "insights"],
        "lifecycle_stages": ["preprocess", "transform", "analyze", "output"],
        "parameters": {
            "risk_threshold": 0.7,
            "analysis_period": "12m"
        },
        "dependencies": ["pandas", "numpy"],
        "entry_point": "finance_insight.py"
    }
    
    # Business Demography Plugin
    business_manifest = {
        "plugin_id": "business_demography",
        "name": "Business Demography",
        "version": "1.0.0",
        "description": "Business survival rates and startup growth analysis",
        "author": "NNDR Insight Team",
        "category": "business_analysis",
        "tags": ["survival_rates", "startup_growth", "sic_evolution"],
        "required_datasets": ["businesses", "registrations", "closures"],
        "required_ai_models": ["trend_analysis", "clustering"],
        "outputs": ["survival_analysis", "growth_trends", "cluster_analysis"],
        "lifecycle_stages": ["preprocess", "transform", "analyze", "output"],
        "parameters": {
            "analysis_period": "5y",
            "cluster_count": 5
        },
        "dependencies": ["pandas", "numpy", "scikit-learn"],
        "entry_point": "business_demography.py"
    }
    
    # Geo Insight Plugin
    geo_manifest = {
        "plugin_id": "geo_insight",
        "name": "Geo Insight",
        "version": "1.0.0",
        "description": "Geographic analysis and spatial clustering",
        "author": "NNDR Insight Team",
        "category": "geospatial",
        "tags": ["spatial_analysis", "land_values", "change_detection"],
        "required_datasets": ["properties", "boundaries", "land_values"],
        "required_ai_models": ["spatial_clustering", "change_detection"],
        "outputs": ["spatial_clusters", "change_maps", "insights"],
        "lifecycle_stages": ["preprocess", "transform", "analyze", "output"],
        "parameters": {
            "cluster_radius": 1000,
            "change_threshold": 0.1
        },
        "dependencies": ["pandas", "numpy", "geopandas"],
        "entry_point": "geo_insight.py"
    }
    
    # Register all built-in plugins
    manifests = [nndr_manifest, finance_manifest, business_manifest, geo_manifest]
    
    for manifest_data in manifests:
        try:
            plugin_service.register_plugin(manifest_data)
        except Exception as e:
            logger.error(f"Error registering built-in plugin {manifest_data['plugin_id']}: {str(e)}")

# Register built-in plugins on startup
register_builtin_plugins() 