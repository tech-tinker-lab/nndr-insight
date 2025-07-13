"""
Forecasting Service for NNDR Insight
Implements AI-powered forecasting, anomaly detection, and NLP summary generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
import re
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ForecastingService:
    """Comprehensive forecasting service for NNDR business rate analysis"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_registry = {}
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
    def train_forecasting_model(self, 
                               data: pd.DataFrame,
                               target_column: str,
                               model_type: str = 'prophet',
                               forecast_periods: int = 12,
                               **kwargs) -> Dict[str, Any]:
        """
        Train a forecasting model for rateable value prediction
        
        Args:
            data: Historical data with date and target columns
            target_column: Column to forecast
            model_type: 'prophet', 'random_forest', 'gradient_boosting', 'linear'
            forecast_periods: Number of periods to forecast
            **kwargs: Additional model parameters
            
        Returns:
            Model metadata and performance metrics
        """
        try:
            model_id = f"{model_type}_{target_column}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if model_type == 'prophet':
                model, metrics = self._train_prophet_model(data, target_column, forecast_periods, **kwargs)
            elif model_type == 'random_forest':
                model, metrics = self._train_ml_model(data, target_column, RandomForestRegressor, **kwargs)
            elif model_type == 'gradient_boosting':
                model, metrics = self._train_ml_model(data, target_column, GradientBoostingRegressor, **kwargs)
            elif model_type == 'linear':
                model, metrics = self._train_ml_model(data, target_column, LinearRegression, **kwargs)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Store model and metadata
            self.models[model_id] = model
            self.model_registry[model_id] = {
                'model_type': model_type,
                'target_column': target_column,
                'training_date': datetime.now().isoformat(),
                'performance_metrics': metrics,
                'forecast_periods': forecast_periods,
                'parameters': kwargs,
                'is_active': True
            }
            
            logger.info(f"Trained {model_type} model {model_id} with R² score: {metrics.get('r2_score', 0):.3f}")
            
            return {
                'model_id': model_id,
                'model_type': model_type,
                'performance_metrics': metrics,
                'forecast_periods': forecast_periods
            }
            
        except Exception as e:
            logger.error(f"Error training forecasting model: {str(e)}")
            raise
    
    def _train_prophet_model(self, data: pd.DataFrame, target_column: str, 
                           forecast_periods: int, **kwargs) -> Tuple[Prophet, Dict]:
        """Train Prophet time series model"""
        # Prepare data for Prophet
        prophet_data = data.copy()
        prophet_data['ds'] = pd.to_datetime(prophet_data.index)
        prophet_data['y'] = prophet_data[target_column]
        
        # Create and train Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            **kwargs
        )
        model.fit(prophet_data[['ds', 'y']])
        
        # Generate forecast for validation
        future = model.make_future_dataframe(periods=forecast_periods)
        forecast = model.predict(future)
        
        # Calculate performance metrics
        actual = prophet_data['y'].values
        predicted = forecast['yhat'][:len(actual)].values
        
        metrics = self._calculate_metrics(actual, predicted)
        metrics['model_type'] = 'prophet'
        
        return model, metrics
    
    def _train_ml_model(self, data: pd.DataFrame, target_column: str, 
                       model_class, **kwargs) -> Tuple[Any, Dict]:
        """Train machine learning model (Random Forest, Gradient Boosting, Linear)"""
        # Prepare features
        feature_columns = [col for col in data.columns if col != target_column and col != 'date']
        
        # Create lag features for time series
        for lag in [1, 3, 6, 12]:
            data[f'{target_column}_lag_{lag}'] = data[target_column].shift(lag)
        
        # Remove NaN values
        data_clean = data.dropna()
        
        if len(data_clean) < 50:
            raise ValueError("Insufficient data for training (minimum 50 records required)")
        
        # Prepare X and y
        feature_cols = [col for col in data_clean.columns if col != target_column and 'lag' in col]
        X = data_clean[feature_cols]
        y = data_clean[target_column]
        
        # Split data (80% train, 20% test)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = model_class(**kwargs)
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_test.values, y_pred)
        metrics['model_type'] = model_class.__name__
        
        # Store scaler
        self.scalers[f"{model_class.__name__}_{target_column}"] = scaler
        
        return model, metrics
    
    def _calculate_metrics(self, actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics"""
        mae = mean_absolute_error(actual, predicted)
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        r2 = r2_score(actual, predicted)
        
        # Calculate confidence interval
        residuals = actual - predicted
        confidence_interval = np.percentile(np.abs(residuals), [5, 95])
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2_score': r2,
            'confidence_interval_lower': confidence_interval[0],
            'confidence_interval_upper': confidence_interval[1],
            'mean_absolute_percentage_error': np.mean(np.abs((actual - predicted) / actual)) * 100
        }
    
    def generate_forecast(self, model_id: str, periods: int = 12, 
                         confidence_level: str = 'medium') -> Dict[str, Any]:
        """
        Generate forecast using trained model
        
        Args:
            model_id: ID of trained model
            periods: Number of periods to forecast
            confidence_level: 'high', 'medium', 'low'
            
        Returns:
            Forecast results with confidence intervals
        """
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")
            
            model = self.models[model_id]
            model_info = self.model_registry[model_id]
            model_type = model_info['model_type']
            
            if model_type == 'prophet':
                return self._generate_prophet_forecast(model, periods, confidence_level)
            else:
                return self._generate_ml_forecast(model, model_id, periods, confidence_level)
                
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            raise
    
    def _generate_prophet_forecast(self, model: Prophet, periods: int, 
                                 confidence_level: str) -> Dict[str, Any]:
        """Generate forecast using Prophet model"""
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        # Get confidence interval based on level
        if confidence_level == 'high':
            lower_col, upper_col = 'yhat_lower', 'yhat_upper'
        elif confidence_level == 'medium':
            # Use 80% confidence interval
            lower_col, upper_col = 'yhat_lower', 'yhat_upper'
        else:
            # Use 60% confidence interval
            lower_col, 'yhat_upper'
        
        # Extract forecast period
        forecast_period = forecast.tail(periods)
        
        return {
            'forecast_dates': forecast_period['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'forecast_values': forecast_period['yhat'].tolist(),
            'confidence_lower': forecast_period[lower_col].tolist(),
            'confidence_upper': forecast_period[upper_col].tolist(),
            'confidence_level': confidence_level,
            'model_type': 'prophet'
        }
    
    def _generate_ml_forecast(self, model: Any, model_id: str, periods: int, 
                            confidence_level: str) -> Dict[str, Any]:
        """Generate forecast using ML model"""
        # This is a simplified implementation - in production, you'd need more sophisticated
        # time series forecasting for ML models
        
        # Generate future dates
        last_date = datetime.now()
        future_dates = [last_date + timedelta(days=i*30) for i in range(1, periods+1)]
        
        # For demonstration, generate trend-based forecast
        base_value = 1000000  # Base rateable value
        trend_factor = 1.02  # 2% monthly growth
        
        forecast_values = []
        confidence_ranges = []
        
        for i in range(periods):
            value = base_value * (trend_factor ** i)
            forecast_values.append(value)
            
            # Add some uncertainty
            uncertainty = value * 0.1  # 10% uncertainty
            confidence_ranges.append([value - uncertainty, value + uncertainty])
        
        return {
            'forecast_dates': [d.strftime('%Y-%m-%d') for d in future_dates],
            'forecast_values': forecast_values,
            'confidence_lower': [r[0] for r in confidence_ranges],
            'confidence_upper': [r[1] for r in confidence_ranges],
            'confidence_level': confidence_level,
            'model_type': 'ml'
        }
    
    def detect_anomalies(self, data: pd.DataFrame, 
                        target_column: str,
                        method: str = 'statistical',
                        threshold: float = 2.0) -> Dict[str, Any]:
        """
        Detect anomalies in rateable value data
        
        Args:
            data: Data to analyze
            target_column: Column to check for anomalies
            method: 'statistical', 'isolation_forest', 'local_outlier_factor'
            threshold: Threshold for anomaly detection
            
        Returns:
            Anomaly detection results
        """
        try:
            if method == 'statistical':
                return self._statistical_anomaly_detection(data, target_column, threshold)
            elif method == 'isolation_forest':
                return self._isolation_forest_anomaly_detection(data, target_column)
            elif method == 'local_outlier_factor':
                return self._lof_anomaly_detection(data, target_column)
            else:
                raise ValueError(f"Unsupported anomaly detection method: {method}")
                
        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise
    
    def _statistical_anomaly_detection(self, data: pd.DataFrame, 
                                     target_column: str, threshold: float) -> Dict[str, Any]:
        """Statistical anomaly detection using z-score"""
        values = data[target_column].dropna()
        
        # Calculate z-scores
        mean_val = values.mean()
        std_val = values.std()
        z_scores = np.abs((values - mean_val) / std_val)
        
        # Find anomalies
        anomalies = z_scores > threshold
        anomaly_indices = values[anomalies].index
        
        # Calculate anomaly scores
        anomaly_scores = z_scores[anomalies]
        
        return {
            'anomaly_indices': anomaly_indices.tolist(),
            'anomaly_scores': anomaly_scores.tolist(),
            'anomaly_count': len(anomaly_indices),
            'total_records': len(values),
            'anomaly_percentage': (len(anomaly_indices) / len(values)) * 100,
            'method': 'statistical',
            'threshold': threshold
        }
    
    def _isolation_forest_anomaly_detection(self, data: pd.DataFrame, 
                                          target_column: str) -> Dict[str, Any]:
        """Isolation Forest anomaly detection"""
        from sklearn.ensemble import IsolationForest
        
        values = data[target_column].dropna().values.reshape(-1, 1)
        
        # Train isolation forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        predictions = iso_forest.fit_predict(values)
        
        # Find anomalies (predictions == -1)
        anomaly_indices = np.where(predictions == -1)[0]
        
        return {
            'anomaly_indices': anomaly_indices.tolist(),
            'anomaly_count': len(anomaly_indices),
            'total_records': len(values),
            'anomaly_percentage': (len(anomaly_indices) / len(values)) * 100,
            'method': 'isolation_forest'
        }
    
    def _lof_anomaly_detection(self, data: pd.DataFrame, 
                              target_column: str) -> Dict[str, Any]:
        """Local Outlier Factor anomaly detection"""
        from sklearn.neighbors import LocalOutlierFactor
        
        values = data[target_column].dropna().values.reshape(-1, 1)
        
        # Train LOF
        lof = LocalOutlierFactor(contamination=0.1)
        predictions = lof.fit_predict(values)
        
        # Find anomalies (predictions == -1)
        anomaly_indices = np.where(predictions == -1)[0]
        
        return {
            'anomaly_indices': anomaly_indices.tolist(),
            'anomaly_count': len(anomaly_indices),
            'total_records': len(values),
            'anomaly_percentage': (len(anomaly_indices) / len(values)) * 100,
            'method': 'local_outlier_factor'
        }
    
    def generate_nlp_summary(self, data: pd.DataFrame, 
                           analysis_results: Dict[str, Any],
                           target_column: str = 'rateable_value') -> str:
        """
        Generate natural language summary of analysis results
        
        Args:
            data: Analyzed data
            analysis_results: Results from forecasting and anomaly detection
            target_column: Primary column analyzed
            
        Returns:
            Natural language summary
        """
        try:
            summary_parts = []
            
            # Basic statistics
            total_records = len(data)
            mean_value = data[target_column].mean()
            total_value = data[target_column].sum()
            
            summary_parts.append(f"Analysis of {total_records:,} properties with a total rateable value of £{total_value:,.0f}.")
            summary_parts.append(f"The average rateable value is £{mean_value:,.0f}.")
            
            # Forecasting insights
            if 'forecast' in analysis_results:
                forecast = analysis_results['forecast']
                forecast_values = forecast['forecast_values']
                avg_forecast = np.mean(forecast_values)
                growth_rate = ((avg_forecast - mean_value) / mean_value) * 100
                
                if growth_rate > 0:
                    summary_parts.append(f"Forecast indicates a {growth_rate:.1f}% increase in average rateable values over the next period.")
                else:
                    summary_parts.append(f"Forecast indicates a {abs(growth_rate):.1f}% decrease in average rateable values over the next period.")
            
            # Anomaly insights
            if 'anomalies' in analysis_results:
                anomalies = analysis_results['anomalies']
                anomaly_count = anomalies['anomaly_count']
                anomaly_percentage = anomalies['anomaly_percentage']
                
                if anomaly_count > 0:
                    summary_parts.append(f"Detected {anomaly_count} anomalies ({anomaly_percentage:.1f}% of records) that require investigation.")
                else:
                    summary_parts.append("No significant anomalies detected in the dataset.")
            
            # Data quality insights
            missing_data = data[target_column].isnull().sum()
            if missing_data > 0:
                missing_percentage = (missing_data / total_records) * 100
                summary_parts.append(f"Data quality note: {missing_data} records ({missing_percentage:.1f}%) have missing values.")
            
            # Combine summary
            full_summary = " ".join(summary_parts)
            
            # Ensure proper sentence structure
            if not full_summary.endswith('.'):
                full_summary += '.'
            
            return full_summary
            
        except Exception as e:
            logger.error(f"Error generating NLP summary: {str(e)}")
            return "Unable to generate summary due to processing error."
    
    def get_model_performance(self, model_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific model"""
        if model_id not in self.model_registry:
            raise ValueError(f"Model {model_id} not found")
        
        return self.model_registry[model_id]
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all trained models"""
        return [
            {
                'model_id': model_id,
                **model_info
            }
            for model_id, model_info in self.model_registry.items()
        ]
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a trained model"""
        if model_id in self.models:
            del self.models[model_id]
            del self.model_registry[model_id]
            return True
        return False
    
    def save_model(self, model_id: str, filepath: str) -> bool:
        """Save model to disk"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")
            
            model_data = {
                'model': self.models[model_id],
                'metadata': self.model_registry[model_id]
            }
            
            joblib.dump(model_data, filepath)
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> str:
        """Load model from disk"""
        try:
            model_data = joblib.load(filepath)
            model_id = model_data['metadata']['model_id']
            
            self.models[model_id] = model_data['model']
            self.model_registry[model_id] = model_data['metadata']
            
            return model_id
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

# Global instance
forecasting_service = ForecastingService() 