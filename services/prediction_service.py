import joblib
import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any

class PredictionService:
    """Service for making stroke risk predictions using Real ML Model"""
    
    def __init__(self, model_dir='ml_models'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_dir = os.path.join(base_dir, model_dir)
        self.model_path = os.path.join(self.model_dir, 'xgboost_stroke.pkl')
        self.scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        self.config_path = os.path.join(self.model_dir, 'model_config.json')
        
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.config = None
        
        # Load model on initialization
        self._load_model()
    
    def _load_model(self):
        """Load trained model, scaler, and configuration with proper error handling"""
        try:
            # Load model
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found at {self.model_path}")
            
            self.model = joblib.load(self.model_path)
            print(f"[OK] Model loaded from {self.model_path}")
            
            # Load scaler
            if not os.path.exists(self.scaler_path):
                raise FileNotFoundError(f"Scaler not found at {self.scaler_path}")
            
            self.scaler = joblib.load(self.scaler_path)
            print(f"[OK] Scaler loaded from {self.scaler_path}")
            
            # Load configuration
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Config not found at {self.config_path}")
            
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                self.feature_columns = self.config['feature_columns']
            
            print(f"[OK] Configuration loaded (Model v{self.config['model_version']})")

            
        except Exception as e:
            print(f"ERROR loading model: {e}")
            raise
    
    def _validate_input(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Validate input data and return errors if any"""
        errors = {}
        
        # Required numeric fields
        required_numeric = {
            'age': (0, 120),
            'avg_glucose_level': (50, 300),
            'bmi': (10, 60)
        }
        
        for field, (min_val, max_val) in required_numeric.items():
            if field not in data:
                errors[field] = f"{field} is required"
            else:
                try:
                    value = float(data[field])
                    if not min_val <= value <= max_val:
                        errors[field] = f"{field} must be between {min_val} and {max_val}"
                except (ValueError, TypeError):
                    errors[field] = f"{field} must be a valid number"
        
        # Required binary fields
        required_binary = ['hypertension', 'heart_disease']
        for field in required_binary:
            if field not in data:
                errors[field] = f"{field} is required"
            else:
                if str(data[field]) not in ['0', '1']:
                    errors[field] = f"{field} must be 0 or 1"
        
        # Required categorical fields
        required_categorical = {
            'gender': ['Male', 'Female', 'Other'],
            'work_type': ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'],
            'Residence_type': ['Urban', 'Rural'],
            'smoking_status': ['never smoked', 'formerly smoked', 'smokes', 'Unknown']
        }
        
        for field, valid_values in required_categorical.items():
            if field not in data or not data[field]:
                # Optional fields - provide defaults
                if field == 'work_type':
                    data[field] = 'Private'
                elif field == 'Residence_type':
                    data[field] = 'Urban'
                elif field == 'smoking_status':
                    data[field] = 'Unknown'
            elif data[field] not in valid_values:
                errors[field] = f"{field} must be one of: {', '.join(valid_values)}"
        
        # ever_married field
        if 'ever_married' not in data or not data['ever_married']:
            # Default based on age
            data['ever_married'] = 'Yes' if float(data.get('age', 0)) >= 30 else 'No'
        elif data['ever_married'] not in ['Yes', 'No']:
            errors['ever_married'] = "ever_married must be 'Yes' or 'No'"
        
        return errors
    
    def _prepare_features(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Prepare and encode features for prediction"""
        
        # Map frontend field names to model field names
        field_mapping = {
            'marital_status': 'ever_married',
            'residence_type': 'Residence_type'
        }
        
        # Create a copy and rename fields
        processed_data = {}
        for key, value in data.items():
            new_key = field_mapping.get(key, key)
            processed_data[new_key] = value
        
        # Ensure all required fields are present with defaults
        defaults = {
            'age': 50,
            'hypertension': 0,
            'heart_disease': 0,
            'avg_glucose_level': 100,
            'bmi': 25,
            'gender': 'Female',
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'smoking_status': 'Unknown'
        }
        
        for key, default_value in defaults.items():
            if key not in processed_data or processed_data[key] is None or processed_data[key] == '':
                processed_data[key] = default_value
        
        # Convert to DataFrame
        df = pd.DataFrame([processed_data])
        
        # Convert numeric fields to proper types
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df['hypertension'] = pd.to_numeric(df['hypertension'], errors='coerce').astype(int)
        df['heart_disease'] = pd.to_numeric(df['heart_disease'], errors='coerce').astype(int)
        df['avg_glucose_level'] = pd.to_numeric(df['avg_glucose_level'], errors='coerce')
        df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')
        
        # One-hot encode categorical variables (must match training)
        categorical_columns = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
        df_encoded = pd.get_dummies(df, columns=categorical_columns, drop_first=True)
        
        # Ensure all expected features are present (add missing columns with 0)
        for col in self.feature_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        
        # Reorder columns to match training order
        df_encoded = df_encoded[self.feature_columns]
        
        return df_encoded
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make stroke risk prediction for a patient
        
        Args:
            patient_data: Dictionary containing patient information
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Validate input
            errors = self._validate_input(patient_data)
            if errors:
                return {
                    'success': False,
                    'error': 'Validation failed',
                    'validation_errors': errors
                }
            
            # Prepare features
            X = self._prepare_features(patient_data)
            
            # Scale features (numerical only)
            numerical_cols = ['age', 'avg_glucose_level', 'bmi']
            X[numerical_cols] = self.scaler.transform(X[numerical_cols])
            
            # Use X (DataFrame) for prediction to preserve feature names
            X_scaled = X
            
            # Make prediction
            risk_probability = float(self.model.predict_proba(X_scaled)[0, 1])
            
            # Determine risk category based on thresholds
            # 0-20%: LOW, 21-60%: MEDIUM, 61-100%: HIGH
            thresholds = self.config.get('risk_thresholds', {'low': 0.2, 'medium': 0.6})
            
            if risk_probability <= thresholds['low']:
                risk_category = 'LOW'
            elif risk_probability <= thresholds['medium']:
                risk_category = 'MEDIUM'
            else:
                risk_category = 'HIGH'
            
            # Get feature importance (SHAP values simulation)
            feature_importance = self._calculate_feature_importance(X)
            
            return {
                'success': True,
                'risk_probability': risk_probability,
                'risk_category': risk_category,
                'model_version': self.config['model_version'],
                'input_features': patient_data,
                'feature_importance': feature_importance,
                'thresholds': thresholds
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Prediction failed: {str(e)}'
            }
    
    def _calculate_feature_importance(self, X: pd.DataFrame) -> Dict[str, float]:
        """Calculate feature importance for interpretability"""
        try:
            # Get feature importances from the model
            importances = self.model.feature_importances_
            
            # Map to feature names
            feature_importance = {}
            for i, col in enumerate(self.feature_columns):
                if i < len(importances):
                    feature_importance[col] = float(importances[i])
            
            # Sort by importance
            feature_importance = dict(sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])  # Top 10 features
            
            return feature_importance
            
        except Exception as e:
            print(f"Error calculating feature importance: {e}")
            return {}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_version': self.config.get('model_version', 'unknown'),
            'training_date': self.config.get('training_date', 'unknown'),
            'risk_thresholds': self.config.get('risk_thresholds', {}),
            'feature_count': len(self.feature_columns),
            'model_type': 'XGBoost Classifier'
        }


# Singleton instance
_prediction_service = None

def get_prediction_service(model_dir='ml_models'):
    """Get or create prediction service singleton"""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService(model_dir)
    return _prediction_service
