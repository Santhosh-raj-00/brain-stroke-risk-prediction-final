import os
import json
import base64
from flask import Blueprint, current_app, jsonify, send_file
from extensions import db
from database.models.prediction import Prediction
from middleware.auth import token_required

visualizations_bp = Blueprint('visualizations', __name__)

def get_plot_base64():
    """Helper to convert plot to base64 string"""
    import io
    import base64
    import matplotlib.pyplot as plt
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

@visualizations_bp.route('/api/model/visualizations/heatmap', methods=['GET'])
@token_required
def get_correlation_heatmap(current_user):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
    import io
    """Generate correlation heatmap of features from recent predictions"""
    try:
        print("Generating correlation heatmap...")
        
        # Try to serve static heatmap first
        possible_paths = [
            os.path.join(current_app.root_path, '..', 'static', 'images', 'correlation_heatmap.png'),
            os.path.join(current_app.root_path, 'static', 'images', 'correlation_heatmap.png'),
            os.path.join(os.getcwd(), 'static', 'images', 'correlation_heatmap.png')
        ]
        
        for path in possible_paths:
            path = os.path.abspath(path)
            print(f"Checking static heatmap at: {path}")
            if os.path.exists(path):
                print(f"Static heatmap found at: {path}")
                with open(path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return jsonify({'image': encoded_string})
        
        print("Static heatmap not found, generating dynamically...")
        
        # Fetch recent predictions to build dataset
        predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(100).all()
        
        data = []
        for p in predictions:
            if hasattr(p, 'input_features') and p.input_features:
                if isinstance(p.input_features, dict):
                    data.append(p.input_features)
                elif isinstance(p.input_features, str):
                    try:
                        data.append(json.loads(p.input_features))
                    except:
                        pass
        
        print(f"Found {len(data)} prediction records with input features")
        
        if not data:
            # Create dummy data if empty to avoid error
            print("No data found, creating placeholder heatmap")
            plt.figure(figsize=(10, 8))
            plt.text(0.5, 0.5, 'No data available', ha='center')
            return jsonify({'image': get_plot_base64()})

        df = pd.DataFrame(data)
        
        # Select numeric columns only
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
             # Fallback if no numeric columns
            print("No numeric data found for correlation")
            plt.figure(figsize=(10, 8))
            plt.text(0.5, 0.5, "No numeric data for correlation", ha='center', va='center')
            return jsonify({'image': get_plot_base64()})
            
        # Compute correlation
        corr = numeric_df.corr()
        print(f"Correlation matrix shape: {corr.shape}")
        
        # Plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
        plt.title('Feature Correlation Heatmap')
        
        result = jsonify({'image': get_plot_base64()})
        print("Heatmap generated successfully")
        return result
        
    except Exception as e:
        print(f"Error generating heatmap: {e}")
        import traceback
        traceback.print_exc()
        plt.figure()
        plt.text(0.5, 0.5, f"Error: {str(e)}", ha='center')
        return jsonify({'image': get_plot_base64()})

@visualizations_bp.route('/api/model/visualizations/confusion-matrix', methods=['GET'])
def get_confusion_matrix():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    
    """Serve the static confusion matrix image"""
    try:
        print("Serving confusion matrix image...")
        
        # Try multiple possible paths
        possible_paths = [
            os.path.join(current_app.root_path, '..', 'static', 'images', 'confusion_matrix.png'),
            os.path.join(current_app.root_path, 'static', 'images', 'confusion_matrix.png'),
            os.path.join(os.getcwd(), 'static', 'images', 'confusion_matrix.png')
        ]
        
        file_path = None
        for path in possible_paths:
            path = os.path.abspath(path)
            print(f"Checking path: {path}")
            if os.path.exists(path):
                file_path = path
                print(f"File found at: {file_path}")
                break
        
        if file_path and os.path.exists(file_path):
            print("File found, serving static image")
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return jsonify({'image': encoded_string})
        else:
            print("File not found in any location, creating placeholder")
            print(f"Tried paths: {possible_paths}")
            # Create a placeholder if missing
            plt.figure(figsize=(6, 5))
            plt.text(0.5, 0.5, "Confusion Matrix\nNot Available", ha='center', va='center')
            plt.axis('off')
            
            img = io.BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
            plt.close()
            img.seek(0)
            encoded_string = base64.b64encode(img.getvalue()).decode('utf-8')
            
            return jsonify({'image': encoded_string})
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@visualizations_bp.route('/api/predictions/<prediction_id>/visualizations/shap', methods=['GET'])
@token_required
def get_shap_waterfall(current_user, prediction_id):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import io
    """Generate SHAP waterfall plot for a specific prediction"""
    try:
        print(f"Generating SHAP waterfall for prediction ID: {prediction_id}")
        
        prediction = Prediction.query.get_or_404(prediction_id)
        
        # Permission check
        if current_user.role == 'doctor' and prediction.doctor_id != current_user.id:
            print(f"Access denied for user {current_user.id} to prediction {prediction_id}")
            return jsonify({'error': 'Access denied'}), 403
        
        # Parse SHAP values
        shap_data = prediction.shap_values
        print(f"Raw SHAP data: {shap_data}")
        
        if isinstance(shap_data, str):
            shap_data = json.loads(shap_data)
            
        feature_importance = {}
        if shap_data:
            if 'feature_importance' in shap_data:
                feature_importance = shap_data['feature_importance']
            else:
                feature_importance = shap_data
        
        print(f"Processed feature importance: {feature_importance}")

        if not feature_importance:
            print("No SHAP data available, creating placeholder")
            plt.figure()
            plt.text(0.5, 0.5, "No SHAP data available", ha='center')
            return jsonify({'image': get_plot_base64()})

        # Prepare data for detailed bar chart (Waterfall approximation)
        features = list(feature_importance.keys())
        values = list(feature_importance.values())
        
        print(f"Features: {features}")
        print(f"Values: {values}")
        
        # Sort by absolute value
        sorted_indices = np.argsort([abs(x) for x in values])
        features = [features[i] for i in sorted_indices]
        values = [values[i] for i in sorted_indices]
        
        # Plot
        plt.figure(figsize=(10, 6))
        colors = ['#EF4444' if x > 0 else '#3B82F6' for x in values]  # Red for risk increase, Blue for decrease
        plt.barh(features, values, color=colors)
        plt.xlabel('SHAP Value (Impact on Model Output)')
        plt.title('Feature Contribution (SHAP)')
        plt.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        result = jsonify({'image': get_plot_base64()})
        print("SHAP plot generated successfully")
        return result
        
    except Exception as e:
        print(f"Error generating SHAP plot: {e}")
        import traceback
        traceback.print_exc()
        plt.figure()
        plt.text(0.5, 0.5, f"Error: {str(e)}", ha='center')
        return jsonify({'image': get_plot_base64()})

@visualizations_bp.route('/api/predictions/<prediction_id>/visualizations/glucose', methods=['GET'])
@token_required
def get_glucose_plot(current_user, prediction_id):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import io
    """Generate Glucose vs Risk box plot with patient marker"""
    try:
        print(f"Generating glucose plot for prediction ID: {prediction_id}")
        
        prediction = Prediction.query.get_or_404(prediction_id)
        
        # Permission check
        if current_user.role == 'doctor' and prediction.doctor_id != current_user.id:
            print(f"Access denied for user {current_user.id} to prediction {prediction_id}")
            return jsonify({'error': 'Access denied'}), 403
        
        # Get current patient glucose
        input_features = prediction.input_features
        print(f"Input features: {input_features}")
        
        if isinstance(input_features, str):
            input_features = json.loads(input_features)
            
        patient_glucose = input_features.get('avg_glucose_level')
        print(f"Patient glucose level: {patient_glucose}")
        
        if patient_glucose is None:
            print("Glucose data not found, creating placeholder")
            plt.figure()
            plt.text(0.5, 0.5, "Glucose data not found", ha='center')
            return jsonify({'image': get_plot_base64()})

        # Fetch population data
        # Ideally we'd query all predictions, but let's limit to 200 for speed
        recent_preds = Prediction.query.order_by(Prediction.created_at.desc()).limit(200).all()
        
        data = []
        for p in recent_preds:
            feats = p.input_features
            if isinstance(feats, str):
                try: 
                    feats = json.loads(feats)
                except: 
                    continue
            if isinstance(feats, dict) and 'avg_glucose_level' in feats:
                data.append({
                    'Risk': p.risk_category,
                    'Glucose': feats['avg_glucose_level']
                })
        
        print(f"Found {len(data)} records with glucose data")
        df = pd.DataFrame(data)
        
        if df.empty:
            # Just plot the patient
            print("No population data, plotting only patient")
            plt.figure(figsize=(8, 6))
            plt.bar(['Patient'], [patient_glucose], color='purple')
            plt.ylabel('Avg Glucose Level')
            plt.title('Patient Glucose Level')
            return jsonify({'image': get_plot_base64()})
            
        # Plot Boxplot
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='Risk', y='Glucose', data=df, order=['LOW', 'MEDIUM', 'HIGH'], palette="Set2")
        
        # Add patient marker
        # We need to find x-coordinate for patient's risk
        risk_map = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
        patient_risk_idx = risk_map.get(prediction.risk_category, 0)
        
        plt.scatter(patient_risk_idx, patient_glucose, color='red', s=200, zorder=10, marker='*', label='This Patient')
        plt.legend()
        plt.title('Glucose Levels by Risk Category')
        plt.ylabel('Average Glucose Level (mg/dL)')
        
        result = jsonify({'image': get_plot_base64()})
        print("Glucose plot generated successfully")
        return result
        
    except Exception as e:
        print(f"Error generating glucose plot: {e}")
        import traceback
        traceback.print_exc()
        plt.figure()
        plt.text(0.5, 0.5, f"Error: {str(e)}", ha='center')
        return jsonify({'image': get_plot_base64()})
