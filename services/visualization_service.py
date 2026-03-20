
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import io
import base64
import shap
import os
import joblib

class VisualizationService:
    def __init__(self, static_dir='static/images'):
        from services.prediction_service import get_prediction_service
        self.static_dir = static_dir
        self.prediction_service = get_prediction_service()
        self.explainer = None
        os.makedirs(static_dir, exist_ok=True)
    
    def _get_explainer(self):
        """Lazy load SHAP explainer"""
        if self.explainer is None:
            # Ensure model is strictly loaded
            if self.prediction_service.model is None:
                print("Loading model for SHAP visualization...")
                self.prediction_service.load_model()
                
            try:
                # XGBoost models can often be used directly with TreeExplainer
                self.explainer = shap.TreeExplainer(self.prediction_service.model)
            except Exception as e:
                print(f"Error initializing SHAP explainer: {e}")
        return self.explainer

    def generate_shap_waterfall(self, input_features, max_display=10):
        """
        Generate SHAP waterfall plot for a single observation
        Returns: base64 encoded image string
        """
        try:
            explainer = self._get_explainer()
            if not explainer:
                return None
                
            # Prepare input data (DataFrame)
            X = self.prediction_service._prepare_features(input_features)
            
            # Calculate SHAP values
            shap_values = explainer(X)
            
            # Create plot
            plt.figure(figsize=(10, 6))
            shap.plots.waterfall(shap_values[0], max_display=max_display, show=False)
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"Error generating SHAP plot: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_glucose_plot(self, patient_glucose):
        """
        Generate Glucose vs Stroke distributions with patient marker
        Returns: base64 encoded image string
        """
        try:
            # We need the background distribution. 
            # Since we don't have the training data loaded, we can generate a simplified 
            # distribution or load the static base image and draw on top.
            # Calculating dynamic overlay is better.
            
            # Generate synthetic "population" data (simplified normal distributions for demo)
            np.random.seed(42)
            n = 1000
            # Stroke group (higher glucose)
            glucose_stroke = np.random.normal(160, 40, int(n*0.2)) 
            # No-stroke group
            glucose_healthy = np.random.normal(100, 25, int(n*0.8))
            
            plt.figure(figsize=(10, 6))
            sns.set_style("whitegrid")
            
            # Plot distributions
            sns.kdeplot(glucose_stroke, fill=True, color='#EF4444', label='Stroke Population', alpha=0.3)
            sns.kdeplot(glucose_healthy, fill=True, color='#22C55E', label='Healthy Population', alpha=0.3)
            
            # Add patient marker
            plt.axvline(x=patient_glucose, color='#6C7CFF', linestyle='--', linewidth=2, label='You')
            plt.scatter([patient_glucose], [0.001], color='#6C7CFF', s=100, zorder=5)
            
            plt.title('Your Glucose Level vs. Population Risk Groups')
            plt.xlabel('Average Glucose Level (mg/dL)')
            plt.ylabel('Density')
            plt.legend()
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"Error generating Glucose plot: {e}")
            return None

_visualization_service = None

def get_visualization_service():
    global _visualization_service
    if _visualization_service is None:
        _visualization_service = VisualizationService()
    return _visualization_service
