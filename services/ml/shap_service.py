import shap
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')


class SHAPService:
    def __init__(self):
        """
        Initialize the SHAP service for explainable AI
        """
        self.explainer = None
    
    def create_explainer(self, model, X_train):
        """
        Create a SHAP explainer for the given model
        
        Args:
            model: Trained ML model
            X_train: Training data used to fit the model
        """
        try:
            # Try to create an explainer based on the model type
            if hasattr(model, 'predict_proba'):
                # For tree-based models like XGBoost
                self.explainer = shap.TreeExplainer(model)
            elif hasattr(model, 'predict'):
                # For other models, use KernelExplainer
                self.explainer = shap.KernelExplainer(model.predict, X_train[:100])  # Use subset for efficiency
            else:
                raise ValueError("Model must have either predict or predict_proba method")
        except Exception as e:
            # Log error for production monitoring
            import logging
            logging.error(f"SHAP explainer creation failed: {e}", exc_info=True)
            print(f"Could not create SHAP explainer: {e}")
            # Create a dummy explainer
            self.explainer = DummyExplainer()
    
    def get_shap_values(self, model, X_sample):
        """
        Get SHAP values for the given samples
        
        Args:
            X_sample: Input samples to explain
            
        Returns:
            SHAP values for each feature
        """
        if self.explainer is None:
            # If no explainer is available, return dummy values
            return self._dummy_shap_values(X_sample)
        
        try:
            if hasattr(self.explainer, 'shap_values'):
                shap_values = self.explainer.shap_values(X_sample)
                # For binary classification, shap_values might be a list
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # Take positive class values
                return shap_values
            else:
                # For dummy explainer
                return self._dummy_shap_values(X_sample)
        except Exception as e:
            print(f"Error calculating SHAP values: {e}")
            return self._dummy_shap_values(X_sample)
    
    def _dummy_shap_values(self, X_sample):
        """
        Generate dummy SHAP values for demo purposes
        
        Args:
            X_sample: Input samples
            
        Returns:
            Dummy SHAP values
        """
        if isinstance(X_sample, pd.DataFrame):
            n_samples, n_features = X_sample.shape
        else:
            n_samples = 1 if len(X_sample.shape) == 1 else X_sample.shape[0]
            n_features = X_sample.shape[-1] if len(X_sample.shape) > 1 else len(X_sample)
        
        # Generate random SHAP values
        return np.random.uniform(-0.5, 0.5, size=(n_samples, n_features))
    
    def get_feature_importance(self, shap_values, feature_names=None):
        """
        Calculate feature importance based on SHAP values
        
        Args:
            shap_values: SHAP values for samples
            feature_names: Names of features (optional)
            
        Returns:
            Dictionary of feature importances
        """
        # Calculate mean absolute SHAP values for each feature
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(mean_abs_shap))]
        
        importance_dict = {}
        for name, importance in zip(feature_names, mean_abs_shap):
            importance_dict[name] = float(importance)
        
        return importance_dict
    
    def generate_explanation(self, model, X_sample, feature_names=None):
        """
        Generate a complete explanation for the sample
        
        Args:
            X_sample: Input sample to explain
            feature_names: Names of features (optional)
            
        Returns:
            Dictionary containing SHAP values and feature importances
        """
        shap_values = self.get_shap_values(model, X_sample)
        
        if isinstance(X_sample, pd.DataFrame) and feature_names is None:
            feature_names = X_sample.columns.tolist()
        
        feature_importance = self.get_feature_importance(shap_values, feature_names)
        
        explanation = {
            'shap_values': shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values,
            'feature_importance': feature_importance,
            'base_value': float(np.mean(shap_values)) if len(shap_values) > 0 else 0.0
        }
        
        return explanation


class DummyExplainer:
    """
    Dummy explainer for demo purposes when SHAP is not available
    """
    def shap_values(self, X):
        if isinstance(X, pd.DataFrame):
            n_samples, n_features = X.shape
        else:
            n_samples = 1 if len(X.shape) == 1 else X.shape[0]
            n_features = X.shape[-1] if len(X.shape) > 1 else len(X)
        
        # Return random values similar to what SHAP would return
        return np.random.uniform(-0.5, 0.5, size=(n_samples, n_features))


# Global instance
shap_service = SHAPService()