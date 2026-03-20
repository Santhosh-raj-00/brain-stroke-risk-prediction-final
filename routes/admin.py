import json
from flask import Blueprint, request, jsonify
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction
from database.models.user import User
from middleware.auth import token_required, role_required
from middleware.roles import admin_required
from datetime import datetime, timedelta
import uuid
import numpy as np

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/api/admin/ml-metrics', methods=['GET'])
@admin_required
def get_ml_metrics(current_user):
    """
    Get ML model performance metrics from stored predictions
    """
    try:
        # Get all predictions for analysis
        all_predictions = Prediction.query.all()
        
        if not all_predictions:
            return jsonify({'error': 'No predictions available for analysis'}), 404
        
        # Calculate metrics based on stored predictions
        # Note: In a real system, you'd compare predictions to ground truth labels
        # For this demo, we'll calculate metrics based on risk thresholds
        
        # Count predictions by category
        low_count = sum(1 for p in all_predictions if p.risk_category == 'LOW')
        medium_count = sum(1 for p in all_predictions if p.risk_category == 'MEDIUM')
        high_count = sum(1 for p in all_predictions if p.risk_category == 'HIGH')
        
        # Calculate some statistical measures
        risk_scores = []
        for p in all_predictions:
            # Use risk_probability if available, otherwise fall back to risk_score
            score = getattr(p, 'risk_probability', None) or getattr(p, 'risk_score', None)
            if score is not None:
                risk_scores.append(score)
        
        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            std_risk = np.std(risk_scores) if len(risk_scores) > 1 else 0
        else:
            avg_risk = 0
            std_risk = 0
        
        # Calculate metrics
        total_predictions = len(all_predictions)
        metrics = {
            'total_predictions': total_predictions,
            'risk_distribution': {
                'LOW': low_count,
                'MEDIUM': medium_count,
                'HIGH': high_count
            },
            'statistical_measures': {
                'average_risk_score': avg_risk,
                'std_deviation': std_risk,
                'min_risk_score': min(risk_scores) if risk_scores else 0,
                'max_risk_score': max(risk_scores) if risk_scores else 1
            }
        }
        
        return jsonify(metrics), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/api/admin/predictions', methods=['GET'])
@admin_required
def get_all_predictions(current_user):
    """
    Get all predictions for admin analytics
    """
    try:
        # Get query parameters
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        risk_filter = request.args.get('risk', None)
        doctor_id = request.args.get('doctor_id', None)
        
        # Build query
        query = Prediction.query
        
        # Apply filters
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(Prediction.created_at >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(Prediction.created_at <= date_to_obj)
        
        if risk_filter:
            query = query.filter(Prediction.risk_category == risk_filter.upper())
        
        if doctor_id:
            query = query.filter(Prediction.doctor_id == doctor_id)
        
        # Execute query and order by date
        predictions = query.order_by(Prediction.created_at.desc()).all()
        
        # Format response
        result = []
        for pred in predictions:
            # Get patient and doctor info
            patient = Patient.query.filter_by(id=pred.patient_id).first()
            doctor = User.query.filter_by(id=pred.doctor_id).first()
            
            pred_dict = pred.to_dict()
            pred_dict['patient'] = patient.to_dict() if patient else None
            pred_dict['doctor'] = doctor.to_dict() if doctor else None
            result.append(pred_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    """
    Get all users for admin management
    """
    try:
        users = User.query.all()
        
        result = []
        for user in users:
            user_dict = user.to_dict()
            # Add patient and prediction counts
            patient_count = Patient.query.filter_by(doctor_id=user.id).count()
            prediction_count = Prediction.query.filter_by(doctor_id=user.id).count()
            
            user_dict['stats'] = {
                'patient_count': patient_count,
                'prediction_count': prediction_count
            }
            result.append(user_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/api/admin/model-performance', methods=['GET'])
@admin_required
def get_model_performance(current_user):
    """
    Get model performance analysis
    """
    try:
        # Get predictions grouped by model version
        predictions = Prediction.query.all()
        
        model_versions = {}
        for pred in predictions:
            version = pred.model_version or 'unknown'
            if version not in model_versions:
                model_versions[version] = {
                    'predictions': [],
                    'risk_scores': [],
                    'categories': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0}
                }
            
            model_versions[version]['predictions'].append(pred)
            # Use risk_probability if available, otherwise fall back to risk_score
            risk_score = getattr(pred, 'risk_probability', None) or getattr(pred, 'risk_score', None)
            if risk_score is not None:
                model_versions[version]['risk_scores'].append(risk_score)
            model_versions[version]['categories'][pred.risk_category] = \
                model_versions[version]['categories'].get(pred.risk_category, 0) + 1
        
        # Analyze each model version
        performance_data = {}
        for version, data in model_versions.items():
            risk_scores = data['risk_scores']
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            performance_data[version] = {
                'total_predictions': len(data['predictions']),
                'average_risk_score': avg_risk,
                'risk_distribution': data['categories'],
                'date_range': {
                    'start': min(p.created_at for p in data['predictions']).isoformat() if data['predictions'] else None,
                    'end': max(p.created_at for p in data['predictions']).isoformat() if data['predictions'] else None
                }
            }
        
        return jsonify({
            'model_versions': performance_data,
            'total_predictions_analyzed': len(predictions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/api/admin/shap-summary', methods=['GET'])
@admin_required
def get_shap_summary(current_user):
    """
    Get SHAP summary statistics for feature importance
    """
    try:
        # Get recent predictions for SHAP analysis
        predictions = Prediction.query.limit(100).all()  # Limit for performance
        
        # Aggregate SHAP values across all predictions
        feature_importance = {}
        for pred in predictions:
            try:
                if pred.shap_values:
                    # Handle different formats of shap_values
                    if isinstance(pred.shap_values, dict):
                        shap_dict = pred.shap_values
                    elif isinstance(pred.shap_values, str):
                        shap_dict = json.loads(pred.shap_values)
                    else:
                        shap_dict = {}
                    
                    feature_importance_map = {}
                    if 'feature_importance' in shap_dict:
                        feature_importance_map = shap_dict['feature_importance']
                    elif shap_dict:
                        feature_importance_map = shap_dict
                        
                    if feature_importance_map:
                        for feature, importance in feature_importance_map.items():
                            if feature not in feature_importance:
                                feature_importance[feature] = {'sum': 0, 'count': 0, 'values': []}
                            feature_importance[feature]['sum'] += abs(importance)
                            feature_importance[feature]['count'] += 1
                            feature_importance[feature]['values'].append(abs(importance))
            except Exception as e:
                print(f"Error processing SHAP values for prediction {pred.id}: {e}")
                continue
        
        # Calculate average importance for each feature
        shap_summary = {}
        for feature, data in feature_importance.items():
            shap_summary[feature] = {
                'avg_importance': data['sum'] / data['count'] if data['count'] > 0 else 0,
                'max_importance': max(data['values']) if data['values'] else 0,
                'min_importance': min(data['values']) if data['values'] else 0,
                'sample_count': data['count']
            }
        
        # Sort features by average importance
        sorted_features = dict(sorted(shap_summary.items(), key=lambda x: x[1]['avg_importance'], reverse=True))
        
        return jsonify({'feature_importance': sorted_features}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/api/admin/error-analysis', methods=['GET'])
@admin_required
def get_error_analysis(current_user):
    """
    Get error analysis for predictions
    """
    try:
        # In a real system, you would compare predictions to actual outcomes
        # For this demo, we'll analyze high-risk predictions and their features
        
        high_risk_predictions = Prediction.query.filter(
            Prediction.risk_category == 'HIGH'
        ).limit(50).all()
        
        # Analyze common patterns in high-risk predictions
        common_factors = {}
        for pred in high_risk_predictions:
            try:
                if pred.input_features:
                    # Handle different formats of input_features
                    if isinstance(pred.input_features, dict):
                        features_dict = pred.input_features
                    elif isinstance(pred.input_features, str):
                        features_dict = json.loads(pred.input_features)
                    else:
                        features_dict = {}
                    
                    for feature, value in features_dict.items():
                        if feature not in common_factors:
                            common_factors[feature] = {'values': [], 'count': 0}
                        common_factors[feature]['values'].append(value)
                        common_factors[feature]['count'] += 1
            except Exception as e:
                print(f"Error processing input features for prediction {pred.id}: {e}")
                continue
        
        # Calculate statistics for each factor
        error_analysis = {}
        for feature, data in common_factors.items():
            if isinstance(data['values'][0], (int, float)):
                error_analysis[feature] = {
                    'mean_value': sum(data['values']) / len(data['values']),
                    'median_value': sorted(data['values'])[len(data['values']) // 2],
                    'min_value': min(data['values']),
                    'max_value': max(data['values']),
                    'sample_count': data['count']
                }
            else:
                # For categorical values
                value_counts = {}
                for val in data['values']:
                    value_counts[val] = value_counts.get(val, 0) + 1
                error_analysis[feature] = {
                    'value_distribution': value_counts,
                    'sample_count': data['count']
                }
        
        return jsonify({'high_risk_patterns': error_analysis}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@admin_bp.route('/api/admin/threshold-analysis', methods=['GET'])
@admin_required
def get_threshold_analysis(current_user):
    """
    Analyze different risk thresholds and their impact
    """
    try:
        # Get all predictions with risk scores
        predictions = Prediction.query.all()
        
        if not predictions:
            return jsonify({'error': 'No predictions available'}), 404
        
        risk_scores = []
        for p in predictions:
            # Use risk_probability if available, otherwise fall back to risk_score
            score = getattr(p, 'risk_probability', None) or getattr(p, 'risk_score', None)
            if score is not None:
                risk_scores.append(score)
        
        if not risk_scores:
            return jsonify({'error': 'No predictions with risk scores available'}), 404
        
        # Analyze different threshold scenarios
        threshold_analysis = {}
        for low_thresh in [0.2, 0.3, 0.4]:
            for high_thresh in [0.6, 0.7, 0.8]:
                if low_thresh >= high_thresh:
                    continue
                
                low_count = sum(1 for score in risk_scores if score < low_thresh)
                medium_count = sum(1 for score in risk_scores if low_thresh <= score < high_thresh)
                high_count = sum(1 for score in risk_scores if score >= high_thresh)
                
                scenario_name = f"{int(low_thresh*100)}-{int(high_thresh*100)}"
                threshold_analysis[scenario_name] = {
                    'low_threshold': low_thresh,
                    'high_threshold': high_thresh,
                    'distribution': {
                        'LOW': low_count,
                        'MEDIUM': medium_count,
                        'HIGH': high_count
                    },
                    'percentages': {
                        'LOW': round((low_count / len(risk_scores)) * 100, 2),
                        'MEDIUM': round((medium_count / len(risk_scores)) * 100, 2),
                        'HIGH': round((high_count / len(risk_scores)) * 100, 2)
                    }
                }
        
        return jsonify({'threshold_scenarios': threshold_analysis}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500