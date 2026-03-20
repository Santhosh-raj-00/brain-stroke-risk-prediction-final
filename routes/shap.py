from flask import Blueprint, request, jsonify
from extensions import db
from database.models.prediction import Prediction
from middleware.auth import token_required, role_required
from middleware.roles import doctor_required, admin_required
from datetime import datetime, timedelta
import json

shap_bp = Blueprint('shap', __name__)


@shap_bp.route('/api/shap/latest', methods=['GET'])
@token_required
def get_latest_shap(current_user):
    """
    Get SHAP values for the most recent prediction
    """
    try:
        # Build query based on user role
        if current_user.role == 'admin':
            # Admin sees all data
            predictions_query = Prediction.query
        else:
            # Doctors see only their data
            predictions_query = Prediction.query.filter_by(doctor_id=current_user.id)
        
        # Get the most recent prediction
        latest_prediction = predictions_query.order_by(Prediction.created_at.desc()).first()
        
        if not latest_prediction or not latest_prediction.shap_values:
            # Return empty array if no SHAP data available
            return jsonify([]), 200
        
        # Parse SHAP values
        shap_data = latest_prediction.shap_values
        if isinstance(shap_data, str):
            shap_dict = json.loads(shap_data)
        else:
            shap_dict = shap_data
        
        # Extract feature importance
        feature_importance_map = {}
        if 'feature_importance' in shap_dict:
            feature_importance_map = shap_dict['feature_importance']
        elif shap_dict:
            feature_importance_map = shap_dict
        
        if feature_importance_map:
            # Convert to array format for frontend
            shap_features = []
            for feature, importance in feature_importance_map.items():
                shap_features.append({
                    'feature': feature,
                    'importance': abs(importance)
                })
            
            # Sort by importance (descending) and return top 10
            shap_features.sort(key=lambda x: x['importance'], reverse=True)
            return jsonify(shap_features[:10]), 200
        else:
            # If no feature importance, return empty array
            return jsonify([]), 200
        
    except json.JSONDecodeError:
        print('Error decoding SHAP JSON data')
        return jsonify([]), 200
    except Exception as e:
        print(f'Error in get_latest_shap: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@shap_bp.route('/api/shap/patient/<patient_id>', methods=['GET'])
@token_required
def get_patient_shap(current_user, patient_id):
    """
    Get SHAP values for the most recent prediction for a specific patient
    """
    try:
        # Build query based on user role
        if current_user.role == 'admin':
            # Admin sees all data
            predictions_query = Prediction.query.filter_by(patient_id=patient_id)
        else:
            # Doctors see only their data
            predictions_query = Prediction.query.filter_by(
                patient_id=patient_id,
                doctor_id=current_user.id
            )
        
        # Get the most recent prediction for this patient
        latest_prediction = predictions_query.order_by(Prediction.created_at.desc()).first()
        
        if not latest_prediction or not latest_prediction.shap_values:
            # Return empty array if no SHAP data available
            return jsonify([]), 200
        
        # Parse SHAP values
        shap_data = latest_prediction.shap_values
        if isinstance(shap_data, str):
            shap_dict = json.loads(shap_data)
        else:
            shap_dict = shap_data
        
        # Extract feature importance
        feature_importance_map = {}
        if 'feature_importance' in shap_dict:
            feature_importance_map = shap_dict['feature_importance']
        elif shap_dict:
            feature_importance_map = shap_dict
        
        if feature_importance_map:
            # Convert to array format for frontend
            shap_features = []
            for feature, importance in feature_importance_map.items():
                shap_features.append({
                    'feature': feature,
                    'importance': abs(importance)
                })
            
            # Sort by importance (descending) and return top 10
            shap_features.sort(key=lambda x: x['importance'], reverse=True)
            return jsonify(shap_features[:10]), 200
        else:
            # If no feature importance, return empty array
            return jsonify([]), 200
        
    except json.JSONDecodeError:
        print('Error decoding SHAP JSON data')
        return jsonify([]), 200
    except Exception as e:
        print(f'Error in get_patient_shap: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500