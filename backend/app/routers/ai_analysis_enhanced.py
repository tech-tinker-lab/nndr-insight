"""
Enhanced AI Analysis Router
Provides comprehensive AI-powered analysis endpoints for the BA specification
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import io

from ..services.database_service import get_db
from ..routers.admin import require_authenticated_user, require_admin_or_power
from ..models import User
from ..services.forecasting_service import forecasting_service
from ..services.ai_lifecycle_service import ai_lifecycle_service
from ..services.ai_analysis_service import GovernmentDataAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai-enhanced", tags=["ai-enhanced"])

# Initialize AI analyzer
ai_analyzer = GovernmentDataAnalyzer()

@router.post("/forecast/train")
async def train_forecasting_model(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user)
):
    """
    Train a forecasting model for business rate prediction
    
    Request:
    {
        "data_source": "table_name or file",
        "target_column": "rateable_value",
        "model_type": "prophet|random_forest|gradient_boosting|linear",
        "forecast_periods": 12,
        "parameters": {...}
    }
    """
    try:
        data_source = request.get("data_source")
        target_column = request.get("target_column", "rateable_value")
        model_type = request.get("model_type", "prophet")
        forecast_periods = request.get("forecast_periods", 12)
        parameters = request.get("parameters", {})
        
        # Load data
        if data_source.endswith('.csv'):
            # Load from file
            data = pd.read_csv(data_source)
        else:
            # Load from database table
            query = text(f"SELECT * FROM {data_source}")
            result = db.execute(query)
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        # Ensure target column exists
        if target_column not in data.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{target_column}' not found in data")
        
        # Train model
        result = forecasting_service.train_forecasting_model(
            data=data,
            target_column=target_column,
            model_type=model_type,
            forecast_periods=forecast_periods,
            **parameters
        )
        
        # Register model in lifecycle service
        feature_columns = [col for col in data.columns if col != target_column]
        ai_lifecycle_service.register_model(
            model_id=result['model_id'],
            model_type=model_type,
            target_column=target_column,
            performance_metrics=result['performance_metrics'],
            parameters=parameters,
            dataset=data,
            feature_columns=feature_columns,
            created_by=current_user.username,
            description=f"Forecasting model for {target_column}",
            tags=["forecasting", "nndr"],
            deployment_status="development"
        )
        
        return {
            "success": True,
            "model_id": result['model_id'],
            "model_type": model_type,
            "performance_metrics": result['performance_metrics'],
            "message": f"Model trained successfully with R² score: {result['performance_metrics'].get('r2_score', 0):.3f}"
        }
        
    except Exception as e:
        logger.error(f"Error training forecasting model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.post("/forecast/generate")
async def generate_forecast(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Generate forecast using trained model
    
    Request:
    {
        "model_id": "model_id",
        "periods": 12,
        "confidence_level": "high|medium|low"
    }
    """
    try:
        model_id = request.get("model_id")
        periods = request.get("periods", 12)
        confidence_level = request.get("confidence_level", "medium")
        
        if not model_id:
            raise HTTPException(status_code=400, detail="Model ID is required")
        
        # Generate forecast
        forecast = forecasting_service.generate_forecast(
            model_id=model_id,
            periods=periods,
            confidence_level=confidence_level
        )
        
        return {
            "success": True,
            "forecast": forecast,
            "model_id": model_id,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@router.post("/anomaly/detect")
async def detect_anomalies(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Detect anomalies in data
    
    Request:
    {
        "data_source": "table_name or file",
        "target_column": "rateable_value",
        "method": "statistical|isolation_forest|local_outlier_factor",
        "threshold": 2.0
    }
    """
    try:
        data_source = request.get("data_source")
        target_column = request.get("target_column", "rateable_value")
        method = request.get("method", "statistical")
        threshold = request.get("threshold", 2.0)
        
        # Load data
        if data_source.endswith('.csv'):
            data = pd.read_csv(data_source)
        else:
            query = text(f"SELECT * FROM {data_source}")
            result = db.execute(query)
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        # Detect anomalies
        anomalies = forecasting_service.detect_anomalies(
            data=data,
            target_column=target_column,
            method=method,
            threshold=threshold
        )
        
        return {
            "success": True,
            "anomalies": anomalies,
            "data_source": data_source,
            "detected_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.post("/summary/generate")
async def generate_nlp_summary(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Generate NLP summary of analysis results
    
    Request:
    {
        "data_source": "table_name or file",
        "analysis_results": {...},
        "target_column": "rateable_value"
    }
    """
    try:
        data_source = request.get("data_source")
        analysis_results = request.get("analysis_results", {})
        target_column = request.get("target_column", "rateable_value")
        
        # Load data
        if data_source.endswith('.csv'):
            data = pd.read_csv(data_source)
        else:
            query = text(f"SELECT * FROM {data_source}")
            result = db.execute(query)
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        # Generate summary
        summary = forecasting_service.generate_nlp_summary(
            data=data,
            analysis_results=analysis_results,
            target_column=target_column
        )
        
        return {
            "success": True,
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@router.get("/models")
async def list_models(
    model_type: Optional[str] = None,
    deployment_status: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """List all registered models with optional filtering"""
    try:
        tag_list = tags.split(',') if tags else None
        
        models = ai_lifecycle_service.list_models(
            model_type=model_type,
            deployment_status=deployment_status,
            tags=tag_list
        )
        
        return {
            "success": True,
            "models": [asdict(model) for model in models],
            "total_count": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.get("/models/{model_id}")
async def get_model_details(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get detailed information about a specific model"""
    try:
        metadata = ai_lifecycle_service.get_model_metadata(model_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get performance history
        performance_history = ai_lifecycle_service.model_performance.get(model_id, [])
        
        return {
            "success": True,
            "model": asdict(metadata),
            "performance_history": [asdict(p) for p in performance_history[-10:]],  # Last 10 evaluations
            "total_evaluations": len(performance_history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get model details: {str(e)}")

@router.post("/models/{model_id}/explain")
async def explain_model_predictions(
    model_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Generate explainability report for model predictions
    
    Request:
    {
        "data_source": "table_name or file",
        "method": "shap|lime|simple"
    }
    """
    try:
        data_source = request.get("data_source")
        method = request.get("method", "shap")
        
        # Load data
        if data_source.endswith('.csv'):
            data = pd.read_csv(data_source)
        else:
            query = text(f"SELECT * FROM {data_source}")
            result = db.execute(query)
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        # Get model (simplified - in production you'd load the actual model)
        model = None  # Would load from model registry
        
        # Generate explanation
        explanation = ai_lifecycle_service.generate_explainability_report(
            model_id=model_id,
            model=model,
            test_data=data,
            method=method
        )
        
        return {
            "success": True,
            "explanation": explanation,
            "model_id": model_id,
            "method": method,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")

@router.post("/models/{model_id}/retrain")
async def trigger_model_retraining(
    model_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """
    Trigger model retraining based on performance degradation
    
    Request:
    {
        "data_source": "table_name or file",
        "retraining_threshold": 0.1
    }
    """
    try:
        data_source = request.get("data_source")
        retraining_threshold = request.get("retraining_threshold", 0.1)
        
        # Load data
        if data_source.endswith('.csv'):
            data = pd.read_csv(data_source)
        else:
            query = text(f"SELECT * FROM {data_source}")
            result = db.execute(query)
            data = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        # Check if retraining is needed
        should_retrain = ai_lifecycle_service.trigger_model_retraining(
            model_id=model_id,
            new_data=data,
            retraining_threshold=retraining_threshold
        )
        
        return {
            "success": True,
            "should_retrain": should_retrain,
            "model_id": model_id,
            "threshold": retraining_threshold,
            "message": "Retraining recommended" if should_retrain else "No retraining needed"
        }
        
    except Exception as e:
        logger.error(f"Error checking retraining: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retraining check failed: {str(e)}")

@router.post("/models/{model_id}/rollback")
async def rollback_model(
    model_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """
    Rollback model to previous version
    
    Request:
    {
        "target_version": "1.0.0"  # Optional
    }
    """
    try:
        target_version = request.get("target_version")
        
        success = ai_lifecycle_service.rollback_model(
            model_id=model_id,
            target_version=target_version
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Model not found or rollback failed")
        
        return {
            "success": True,
            "model_id": model_id,
            "target_version": target_version or "previous",
            "message": "Model rolled back successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")

@router.post("/analyze-comprehensive")
async def comprehensive_analysis(
    file: UploadFile = File(...),
    analysis_type: str = Form("full"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """
    Comprehensive AI analysis including forecasting, anomaly detection, and NLP summary
    
    Analysis types: "full", "forecast", "anomaly", "summary"
    """
    try:
        # Read file content
        content = await file.read()
        
        # Convert to DataFrame
        if file.filename.endswith('.csv'):
            data = pd.read_csv(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Only CSV files supported for comprehensive analysis")
        
        results = {
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "rows": len(data),
                "columns": len(data.columns)
            },
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Perform analysis based on type
        if analysis_type in ["full", "forecast"]:
            # Train forecasting model
            try:
                forecast_result = forecasting_service.train_forecasting_model(
                    data=data,
                    target_column="rateable_value" if "rateable_value" in data.columns else data.columns[0],
                    model_type="prophet",
                    forecast_periods=12
                )
                results["forecasting"] = forecast_result
            except Exception as e:
                results["forecasting"] = {"error": str(e)}
        
        if analysis_type in ["full", "anomaly"]:
            # Detect anomalies
            try:
                anomaly_result = forecasting_service.detect_anomalies(
                    data=data,
                    target_column="rateable_value" if "rateable_value" in data.columns else data.columns[0],
                    method="statistical"
                )
                results["anomalies"] = anomaly_result
            except Exception as e:
                results["anomalies"] = {"error": str(e)}
        
        if analysis_type in ["full", "summary"]:
            # Generate NLP summary
            try:
                summary = forecasting_service.generate_nlp_summary(
                    data=data,
                    analysis_results=results,
                    target_column="rateable_value" if "rateable_value" in data.columns else data.columns[0]
                )
                results["summary"] = summary
            except Exception as e:
                results["summary"] = {"error": str(e)}
        
        return {
            "success": True,
            "analysis": results
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/performance/metrics")
async def get_performance_metrics(
    model_id: Optional[str] = None,
    time_period: str = "30d",
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_authenticated_user)
):
    """Get performance metrics for models"""
    try:
        if model_id:
            # Get specific model performance
            metadata = ai_lifecycle_service.get_model_metadata(model_id)
            if not metadata:
                raise HTTPException(status_code=404, detail="Model not found")
            
            performance_history = ai_lifecycle_service.model_performance.get(model_id, [])
            
            return {
                "success": True,
                "model_id": model_id,
                "performance": {
                    "current_metrics": metadata.performance_metrics,
                    "history": [asdict(p) for p in performance_history[-10:]],
                    "total_evaluations": len(performance_history)
                }
            }
        else:
            # Get overall performance metrics
            models = ai_lifecycle_service.list_models()
            
            overall_metrics = {
                "total_models": len(models),
                "active_models": len([m for m in models if m.is_active]),
                "average_r2_score": np.mean([m.performance_metrics.get('r2_score', 0) for m in models]),
                "models_by_type": {},
                "models_by_status": {}
            }
            
            # Group by type and status
            for model in models:
                model_type = model.model_type
                status = model.deployment_status
                
                if model_type not in overall_metrics["models_by_type"]:
                    overall_metrics["models_by_type"][model_type] = 0
                overall_metrics["models_by_type"][model_type] += 1
                
                if status not in overall_metrics["models_by_status"]:
                    overall_metrics["models_by_status"][status] = 0
                overall_metrics["models_by_status"][status] += 1
            
            return {
                "success": True,
                "overall_metrics": overall_metrics
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.post("/models/{model_id}/deploy")
async def deploy_model(
    model_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_power)
):
    """
    Deploy model to production
    
    Request:
    {
        "deployment_status": "production|staging|development"
    }
    """
    try:
        deployment_status = request.get("deployment_status", "production")
        
        success = ai_lifecycle_service.update_model_status(
            model_id=model_id,
            deployment_status=deployment_status
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return {
            "success": True,
            "model_id": model_id,
            "deployment_status": deployment_status,
            "message": f"Model deployed to {deployment_status}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deploying model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}") 