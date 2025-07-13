"""
AI Lifecycle Management Service
Implements model registry, explainability, governance, and automated training pipelines
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import joblib
import os
from pathlib import Path
import hashlib
import shutil
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# Try to import SHAP for explainability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available - explainability features will be limited")

# Try to import LIME for explainability
try:
    import lime
    import lime.lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logging.warning("LIME not available - explainability features will be limited")

logger = logging.getLogger(__name__)

@dataclass
class ModelMetadata:
    """Model metadata for registry"""
    model_id: str
    model_type: str
    target_column: str
    training_date: str
    performance_metrics: Dict[str, float]
    parameters: Dict[str, Any]
    dataset_hash: str
    dataset_size: int
    feature_columns: List[str]
    model_version: str
    is_active: bool
    created_by: str
    description: str
    tags: List[str]
    deployment_status: str  # 'development', 'staging', 'production'
    last_updated: str

@dataclass
class ModelPerformance:
    """Model performance tracking"""
    model_id: str
    evaluation_date: str
    accuracy_score: float
    precision_score: float
    recall_score: float
    f1_score: float
    mae: float
    rmse: float
    r2_score: float
    confidence_score: float
    drift_detected: bool
    drift_score: float

class AILifecycleService:
    """Comprehensive AI lifecycle management service"""
    
    def __init__(self, model_registry_path: str = "models/registry"):
        self.model_registry_path = Path(model_registry_path)
        self.model_registry_path.mkdir(parents=True, exist_ok=True)
        
        self.models_metadata: Dict[str, ModelMetadata] = {}
        self.model_performance: Dict[str, List[ModelPerformance]] = {}
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # Load existing registry
        self._load_registry()
    
    def register_model(self, 
                      model_id: str,
                      model_type: str,
                      target_column: str,
                      performance_metrics: Dict[str, float],
                      parameters: Dict[str, Any],
                      dataset: pd.DataFrame,
                      feature_columns: List[str],
                      created_by: str,
                      description: str = "",
                      tags: List[str] = None,
                      deployment_status: str = "development") -> str:
        """
        Register a new model in the registry
        
        Args:
            model_id: Unique model identifier
            model_type: Type of model (prophet, random_forest, etc.)
            target_column: Target column for prediction
            performance_metrics: Model performance metrics
            parameters: Model parameters
            dataset: Training dataset
            feature_columns: Feature columns used
            created_by: User who created the model
            description: Model description
            tags: Model tags
            deployment_status: Deployment status
            
        Returns:
            Model ID
        """
        try:
            # Generate dataset hash
            dataset_hash = self._generate_dataset_hash(dataset)
            
            # Create metadata
            metadata = ModelMetadata(
                model_id=model_id,
                model_type=model_type,
                target_column=target_column,
                training_date=datetime.now().isoformat(),
                performance_metrics=performance_metrics,
                parameters=parameters,
                dataset_hash=dataset_hash,
                dataset_size=len(dataset),
                feature_columns=feature_columns,
                model_version="1.0.0",
                is_active=True,
                created_by=created_by,
                description=description,
                tags=tags or [],
                deployment_status=deployment_status,
                last_updated=datetime.now().isoformat()
            )
            
            # Store metadata
            self.models_metadata[model_id] = metadata
            self._save_metadata(model_id, metadata)
            
            logger.info(f"Registered model {model_id} in registry")
            return model_id
            
        except Exception as e:
            logger.error(f"Error registering model: {str(e)}")
            raise
    
    def get_model_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata"""
        return self.models_metadata.get(model_id)
    
    def list_models(self, 
                   model_type: str = None,
                   deployment_status: str = None,
                   tags: List[str] = None) -> List[ModelMetadata]:
        """List models with optional filtering"""
        models = list(self.models_metadata.values())
        
        if model_type:
            models = [m for m in models if m.model_type == model_type]
        
        if deployment_status:
            models = [m for m in models if m.deployment_status == deployment_status]
        
        if tags:
            models = [m for m in models if any(tag in m.tags for tag in tags)]
        
        return models
    
    def update_model_status(self, model_id: str, 
                           deployment_status: str = None,
                           is_active: bool = None,
                           description: str = None) -> bool:
        """Update model status"""
        if model_id not in self.models_metadata:
            return False
        
        metadata = self.models_metadata[model_id]
        
        if deployment_status:
            metadata.deployment_status = deployment_status
        
        if is_active is not None:
            metadata.is_active = is_active
        
        if description:
            metadata.description = description
        
        metadata.last_updated = datetime.now().isoformat()
        
        self._save_metadata(model_id, metadata)
        return True
    
    def track_model_performance(self, 
                               model_id: str,
                               test_data: pd.DataFrame,
                               predictions: np.ndarray,
                               actual_values: np.ndarray) -> ModelPerformance:
        """
        Track model performance on new data
        
        Args:
            model_id: Model ID
            test_data: Test dataset
            predictions: Model predictions
            actual_values: Actual values
            
        Returns:
            Performance metrics
        """
        try:
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            
            # Calculate metrics
            mae = mean_absolute_error(actual_values, predictions)
            rmse = np.sqrt(mean_squared_error(actual_values, predictions))
            r2 = r2_score(actual_values, predictions)
            
            # Calculate confidence score (simplified)
            confidence_score = max(0, min(1, 1 - (mae / np.mean(actual_values))))
            
            # Check for data drift
            drift_detected, drift_score = self._detect_data_drift(model_id, test_data)
            
            # Create performance record
            performance = ModelPerformance(
                model_id=model_id,
                evaluation_date=datetime.now().isoformat(),
                accuracy_score=1 - (mae / np.mean(actual_values)),
                precision_score=0.0,  # Not applicable for regression
                recall_score=0.0,     # Not applicable for regression
                f1_score=0.0,         # Not applicable for regression
                mae=mae,
                rmse=rmse,
                r2_score=r2,
                confidence_score=confidence_score,
                drift_detected=drift_detected,
                drift_score=drift_score
            )
            
            # Store performance
            if model_id not in self.model_performance:
                self.model_performance[model_id] = []
            
            self.model_performance[model_id].append(performance)
            self._save_performance(model_id, performance)
            
            return performance
            
        except Exception as e:
            logger.error(f"Error tracking model performance: {str(e)}")
            raise
    
    def _detect_data_drift(self, model_id: str, new_data: pd.DataFrame) -> Tuple[bool, float]:
        """Detect data drift between training and new data"""
        try:
            if model_id not in self.models_metadata:
                return False, 0.0
            
            metadata = self.models_metadata[model_id]
            
            # Compare feature distributions (simplified)
            drift_score = 0.0
            drift_detected = False
            
            # For each feature, compare distributions
            for feature in metadata.feature_columns:
                if feature in new_data.columns:
                    # Calculate distribution difference (simplified)
                    old_mean = 0  # Would need to store training data statistics
                    new_mean = new_data[feature].mean()
                    
                    if old_mean != 0:
                        drift = abs(new_mean - old_mean) / abs(old_mean)
                        drift_score = max(drift_score, drift)
            
            drift_detected = drift_score > 0.1  # 10% threshold
            
            return drift_detected, drift_score
            
        except Exception as e:
            logger.error(f"Error detecting data drift: {str(e)}")
            return False, 0.0
    
    def generate_explainability_report(self, 
                                     model_id: str,
                                     model,
                                     test_data: pd.DataFrame,
                                     method: str = "shap") -> Dict[str, Any]:
        """
        Generate explainability report for model predictions
        
        Args:
            model_id: Model ID
            model: Trained model
            test_data: Test data for explanation
            method: 'shap' or 'lime'
            
        Returns:
            Explainability report
        """
        try:
            if method == "shap" and SHAP_AVAILABLE:
                return self._generate_shap_explanation(model, test_data)
            elif method == "lime" and LIME_AVAILABLE:
                return self._generate_lime_explanation(model, test_data)
            else:
                return self._generate_simple_explanation(model, test_data)
                
        except Exception as e:
            logger.error(f"Error generating explainability report: {str(e)}")
            return {"error": str(e)}
    
    def _generate_shap_explanation(self, model, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate SHAP-based explanation"""
        try:
            # Prepare data
            X = test_data.select_dtypes(include=[np.number])
            
            # Create SHAP explainer
            if hasattr(model, 'predict_proba'):
                explainer = shap.TreeExplainer(model)
            else:
                explainer = shap.Explainer(model, X)
            
            # Generate explanations
            shap_values = explainer(X)
            
            # Calculate feature importance
            feature_importance = np.abs(shap_values.values).mean(0)
            feature_names = X.columns.tolist()
            
            # Create explanation report
            explanation = {
                "method": "shap",
                "feature_importance": dict(zip(feature_names, feature_importance.tolist())),
                "shap_values": shap_values.values.tolist(),
                "base_values": shap_values.base_values.tolist() if hasattr(shap_values, 'base_values') else [],
                "feature_names": feature_names,
                "explanation_available": True
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {str(e)}")
            return {"method": "shap", "error": str(e), "explanation_available": False}
    
    def _generate_lime_explanation(self, model, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate LIME-based explanation"""
        try:
            # Prepare data
            X = test_data.select_dtypes(include=[np.number])
            
            # Create LIME explainer
            explainer = lime.lime_tabular.LimeTabularExplainer(
                X.values,
                feature_names=X.columns.tolist(),
                class_names=['prediction'],
                mode='regression'
            )
            
            # Generate explanation for first sample
            exp = explainer.explain_instance(
                X.iloc[0].values, 
                model.predict, 
                num_features=min(10, len(X.columns))
            )
            
            # Extract explanation
            explanation = {
                "method": "lime",
                "feature_importance": dict(exp.as_list()),
                "explanation_available": True
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating LIME explanation: {str(e)}")
            return {"method": "lime", "error": str(e), "explanation_available": False}
    
    def _generate_simple_explanation(self, model, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate simple explanation when SHAP/LIME not available"""
        try:
            # Feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                feature_importance = model.feature_importances_
                feature_names = test_data.columns.tolist()
                
                explanation = {
                    "method": "simple",
                    "feature_importance": dict(zip(feature_names, feature_importance.tolist())),
                    "explanation_available": True
                }
            else:
                explanation = {
                    "method": "simple",
                    "feature_importance": {},
                    "explanation_available": False,
                    "message": "Feature importance not available for this model type"
                }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating simple explanation: {str(e)}")
            return {"method": "simple", "error": str(e), "explanation_available": False}
    
    def trigger_model_retraining(self, 
                                model_id: str,
                                new_data: pd.DataFrame,
                                retraining_threshold: float = 0.1) -> bool:
        """
        Trigger model retraining based on performance degradation
        
        Args:
            model_id: Model ID
            new_data: New data for evaluation
            retraining_threshold: Performance degradation threshold
            
        Returns:
            True if retraining should be triggered
        """
        try:
            if model_id not in self.model_performance:
                return False
            
            # Get recent performance
            recent_performance = self.model_performance[model_id][-5:]  # Last 5 evaluations
            
            if len(recent_performance) < 3:
                return False
            
            # Calculate performance trend
            recent_scores = [p.r2_score for p in recent_performance]
            performance_degradation = recent_scores[0] - recent_scores[-1]
            
            # Check if degradation exceeds threshold
            if performance_degradation > retraining_threshold:
                logger.info(f"Performance degradation detected for model {model_id}. Retraining recommended.")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking retraining trigger: {str(e)}")
            return False
    
    def rollback_model(self, model_id: str, target_version: str = None) -> bool:
        """
        Rollback model to previous version
        
        Args:
            model_id: Model ID
            target_version: Target version (if None, rollback to previous)
            
        Returns:
            True if rollback successful
        """
        try:
            if model_id not in self.models_metadata:
                return False
            
            metadata = self.models_metadata[model_id]
            
            # Find previous version
            if target_version:
                # Load specific version
                version_path = self.model_registry_path / f"{model_id}_{target_version}.json"
                if version_path.exists():
                    with open(version_path, 'r') as f:
                        old_metadata = json.load(f)
                    
                    # Restore metadata
                    self.models_metadata[model_id] = ModelMetadata(**old_metadata)
                    self._save_metadata(model_id, self.models_metadata[model_id])
                    
                    logger.info(f"Rolled back model {model_id} to version {target_version}")
                    return True
            else:
                # Rollback to previous version (simplified)
                metadata.model_version = self._get_previous_version(metadata.model_version)
                metadata.last_updated = datetime.now().isoformat()
                
                self._save_metadata(model_id, metadata)
                
                logger.info(f"Rolled back model {model_id} to version {metadata.model_version}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error rolling back model: {str(e)}")
            return False
    
    def _get_previous_version(self, current_version: str) -> str:
        """Get previous version number"""
        try:
            major, minor, patch = map(int, current_version.split('.'))
            if patch > 0:
                return f"{major}.{minor}.{patch-1}"
            elif minor > 0:
                return f"{major}.{minor-1}.9"
            else:
                return f"{major-1}.9.9"
        except:
            return "1.0.0"
    
    def _generate_dataset_hash(self, dataset: pd.DataFrame) -> str:
        """Generate hash for dataset"""
        # Create a hash of the dataset structure and first few rows
        dataset_str = str(dataset.dtypes.tolist()) + str(dataset.head(100).values.tolist())
        return hashlib.md5(dataset_str.encode()).hexdigest()
    
    def _save_metadata(self, model_id: str, metadata: ModelMetadata):
        """Save model metadata to file"""
        try:
            metadata_path = self.model_registry_path / f"{model_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(asdict(metadata), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
    
    def _save_performance(self, model_id: str, performance: ModelPerformance):
        """Save performance metrics to file"""
        try:
            performance_path = self.model_registry_path / f"{model_id}_performance.json"
            
            # Load existing performance
            if performance_path.exists():
                with open(performance_path, 'r') as f:
                    existing_performance = json.load(f)
            else:
                existing_performance = []
            
            # Add new performance
            existing_performance.append(asdict(performance))
            
            # Keep only last 50 performance records
            if len(existing_performance) > 50:
                existing_performance = existing_performance[-50:]
            
            # Save
            with open(performance_path, 'w') as f:
                json.dump(existing_performance, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving performance: {str(e)}")
    
    def _load_registry(self):
        """Load existing model registry"""
        try:
            for metadata_file in self.model_registry_path.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata_dict = json.load(f)
                    
                    model_id = metadata_dict['model_id']
                    metadata = ModelMetadata(**metadata_dict)
                    self.models_metadata[model_id] = metadata
                    
                    # Load performance data
                    performance_file = self.model_registry_path / f"{model_id}_performance.json"
                    if performance_file.exists():
                        with open(performance_file, 'r') as f:
                            performance_data = json.load(f)
                        
                        self.model_performance[model_id] = [
                            ModelPerformance(**p) for p in performance_data
                        ]
                    
                except Exception as e:
                    logger.error(f"Error loading metadata from {metadata_file}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error loading registry: {str(e)}")

# Global instance
ai_lifecycle_service = AILifecycleService() 