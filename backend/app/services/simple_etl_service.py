"""
Simple ETL Service
Provides easy-to-use data transformation and loading capabilities
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import json
import re
from pathlib import Path
import io

logger = logging.getLogger(__name__)

class SimpleETLService:
    """Simplified ETL service for easy data transformation and loading"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.json', '.xml']
        self.transformations = {
            'uppercase': self._transform_uppercase,
            'lowercase': self._transform_lowercase,
            'trim': self._transform_trim,
            'number_format': self._transform_number_format,
            'date_format': self._transform_date_format,
            'postcode_clean': self._transform_postcode_clean,
            'coordinate_validate': self._transform_coordinate_validate
        }
    
    def preview_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Preview uploaded file content
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Preview data with columns and sample rows
        """
        try:
            file_ext = Path(filename).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(io.BytesIO(file_content), nrows=10)
            elif file_ext == '.xlsx':
                df = pd.read_excel(io.BytesIO(file_content), nrows=10)
            elif file_ext == '.json':
                df = pd.read_json(io.BytesIO(file_content))
                df = df.head(10)
            elif file_ext == '.xml':
                # Simple XML parsing - in production, use more robust XML parser
                df = pd.read_xml(io.BytesIO(file_content))
                df = df.head(10)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return {
                'columns': df.columns.tolist(),
                'data': df.to_dict('records'),
                'total_rows': len(df),
                'file_type': file_ext
            }
            
        except Exception as e:
            logger.error(f"Error previewing file: {str(e)}")
            raise
    
    def transform_data(self, data: pd.DataFrame, transformations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Apply transformations to data
        
        Args:
            data: Input DataFrame
            transformations: List of transformation rules
            
        Returns:
            Transformed DataFrame
        """
        try:
            df = data.copy()
            
            for rule in transformations:
                column = rule.get('column')
                transformation = rule.get('transformation')
                parameters = rule.get('parameters', {})
                
                if column in df.columns and transformation in self.transformations:
                    df[column] = self.transformations[transformation](df[column], parameters)
                    logger.info(f"Applied {transformation} to column {column}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error transforming data: {str(e)}")
            raise
    
    def _transform_uppercase(self, series: pd.Series, parameters: Dict[str, Any]) -> pd.Series:
        """Convert text to uppercase"""
        return series.astype(str).str.upper()
    
    def _transform_lowercase(self, series: pd.Series, parameters: Dict[str, Any]) -> pd.Series:
        """Convert text to lowercase"""
        return series.astype(str).str.lower()
    
    def _transform_trim(self, series: pd.Series, parameters: Dict[str, Any]) -> pd.Series:
        """Trim whitespace"""
        return series.astype(str).str.strip()
    
    def _transform_number_format(self, series: pd.Series, parameters: Dict[str, Any]) -> pd.Series:
        """Format numbers"""
        try:
            # Remove currency symbols and commas
            cleaned = series.astype(str).str.replace(r'[£$,]', '', regex=True)
            # Convert to numeric, handling errors
            return pd.to_numeric(cleaned, errors='coerce')
        except Exception:
            return series
    
    def _transform_date_format(self, series: pd.Series, parameters: Dict[str, Any]) -> pd.Series:
        """Format dates"""
        try:
            # Try common date formats
            date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            for fmt in date_formats:
                try:
                    return pd.to_datetime(series, format=fmt, errors='coerce')
                except:
                    continue
            # If no specific format works, try pandas auto-detection
            return pd.to_datetime(series, errors='coerce')
        except Exception:
            return series
    
    def _transform_postcode_clean(self, series: pd.Series, parameters: Dict[str, Any]) -> pd.Series:
        """Clean UK postcodes"""
        try:
            # Remove extra spaces and convert to uppercase
            cleaned = series.astype(str).str.upper().str.strip()
            # Basic UK postcode validation
            uk_postcode_pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$'
            return cleaned.apply(lambda x: x if re.match(uk_postcode_pattern, x) else None)
        except Exception:
            return series
    
    def _transform_coordinate_validate(self, series: pd.Series, parameters: Dict[str, Any]) -> pd.Series:
        """Validate and convert coordinates"""
        try:
            # Convert to numeric
            coords = pd.to_numeric(series, errors='coerce')
            # Basic UK coordinate validation (approximate bounds)
            # Longitude: -8 to 2, Latitude: 49 to 61
            if 'longitude' in str(series.name).lower():
                return coords.apply(lambda x: x if -8 <= x <= 2 else None)
            elif 'latitude' in str(series.name).lower():
                return coords.apply(lambda x: x if 49 <= x <= 61 else None)
            else:
                return coords
        except Exception:
            return series
    
    def validate_data(self, data: pd.DataFrame, target_table: str) -> Dict[str, Any]:
        """
        Validate data before loading
        
        Args:
            data: DataFrame to validate
            target_table: Target table name
            
        Returns:
            Validation results
        """
        try:
            validation_results = {
                'total_rows': len(data),
                'null_counts': {},
                'data_types': {},
                'warnings': [],
                'errors': []
            }
            
            # Check for null values
            for column in data.columns:
                null_count = data[column].isnull().sum()
                validation_results['null_counts'][column] = null_count
                
                if null_count > len(data) * 0.5:  # More than 50% nulls
                    validation_results['warnings'].append(f"Column {column} has {null_count} null values")
            
            # Check data types
            for column in data.columns:
                validation_results['data_types'][column] = str(data[column].dtype)
            
            # Specific validations for common fields
            if 'postcode' in data.columns:
                postcode_validation = self._validate_postcodes(data['postcode'])
                validation_results['warnings'].extend(postcode_validation['warnings'])
            
            if 'rateable_value' in data.columns:
                value_validation = self._validate_rateable_values(data['rateable_value'])
                validation_results['warnings'].extend(value_validation['warnings'])
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            validation_results['errors'].append(str(e))
            return validation_results
    
    def _validate_postcodes(self, series: pd.Series) -> Dict[str, Any]:
        """Validate UK postcodes"""
        results = {'warnings': []}
        
        # Check for valid UK postcode format
        uk_postcode_pattern = r'^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$'
        valid_postcodes = series.astype(str).str.match(uk_postcode_pattern)
        
        invalid_count = (~valid_postcodes).sum()
        if invalid_count > 0:
            results['warnings'].append(f"Found {invalid_count} invalid postcode formats")
        
        return results
    
    def _validate_rateable_values(self, series: pd.Series) -> Dict[str, Any]:
        """Validate rateable values"""
        results = {'warnings': []}
        
        # Convert to numeric
        values = pd.to_numeric(series, errors='coerce')
        
        # Check for reasonable ranges
        negative_count = (values < 0).sum()
        if negative_count > 0:
            results['warnings'].append(f"Found {negative_count} negative rateable values")
        
        high_count = (values > 10000000).sum()  # £10M threshold
        if high_count > 0:
            results['warnings'].append(f"Found {high_count} rateable values over £10M")
        
        return results
    
    def generate_sql_insert(self, data: pd.DataFrame, target_table: str, 
                           column_mapping: Dict[str, str]) -> str:
        """
        Generate SQL INSERT statement
        
        Args:
            data: DataFrame to insert
            target_table: Target table name
            column_mapping: Column mapping from source to target
            
        Returns:
            SQL INSERT statement
        """
        try:
            # Map columns
            mapped_data = data.copy()
            for source_col, target_col in column_mapping.items():
                if source_col in mapped_data.columns:
                    mapped_data[target_col] = mapped_data[source_col]
                    if source_col != target_col:
                        mapped_data = mapped_data.drop(columns=[source_col])
            
            # Generate column list
            columns = list(mapped_data.columns)
            columns_sql = ', '.join([f'"{col}"' for col in columns])
            
            # Generate values
            values_list = []
            for _, row in mapped_data.iterrows():
                values = []
                for col in columns:
                    value = row[col]
                    if pd.isna(value):
                        values.append('NULL')
                    elif isinstance(value, (int, float)):
                        values.append(str(value))
                    else:
                        # Escape single quotes in strings
                        escaped_value = str(value).replace("'", "''")
                        values.append(f"'{escaped_value}'")
                values_list.append(f"({', '.join(values)})")
            
            values_sql = ',\n'.join(values_list)
            
            # Generate full INSERT statement
            sql = f"""
INSERT INTO {target_table} ({columns_sql})
VALUES
{values_sql};
"""
            return sql
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            raise
    
    def process_etl_job(self, etl_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process complete ETL job
        
        Args:
            etl_config: ETL configuration including file, mappings, transformations
            
        Returns:
            ETL results
        """
        start_time = datetime.now()
        
        try:
            logger.info("Starting ETL job")
            
            # Extract configuration
            source_file = etl_config.get('source_file')
            target_table = etl_config.get('target_table')
            column_mapping = etl_config.get('column_mapping', {})
            transformations = etl_config.get('transformations', [])
            parameters = etl_config.get('parameters', {})
            
            # Load data (this would come from file upload in real implementation)
            # For now, we'll assume data is already loaded
            data = pd.DataFrame()  # Placeholder
            
            # Apply transformations
            if transformations:
                data = self.transform_data(data, transformations)
                logger.info(f"Applied {len(transformations)} transformations")
            
            # Validate data
            validation_results = self.validate_data(data, target_table)
            logger.info(f"Validation completed: {len(validation_results['warnings'])} warnings")
            
            # Generate SQL
            sql = self.generate_sql_insert(data, target_table, column_mapping)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'records_processed': len(data),
                'records_loaded': len(data),
                'errors': len(validation_results['errors']),
                'warnings': len(validation_results['warnings']),
                'processing_time': round(processing_time, 2),
                'validation_results': validation_results,
                'sql_generated': sql
            }
            
        except Exception as e:
            logger.error(f"ETL job failed: {str(e)}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': False,
                'error': str(e),
                'processing_time': round(processing_time, 2),
                'records_processed': 0,
                'records_loaded': 0
            }

# Global instance
simple_etl_service = SimpleETLService() 