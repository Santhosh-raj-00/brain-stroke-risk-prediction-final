import json
from flask import Blueprint, request, jsonify
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction
from database.models.user import User
from middleware.auth import token_required, role_required
from middleware.roles import doctor_required, admin_required
from datetime import datetime, timedelta
import uuid

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
@token_required
def get_dashboard(current_user):
    """
    Get dashboard data for the current user
    """
    try:
        # Build query based on user role
        if current_user.role == 'admin':
            # Admin sees all data
            patients_query = Patient.query
            predictions_query = Prediction.query
        else:
            # Doctors see only their data
            patients_query = Patient.query.filter_by(doctor_id=current_user.id)
            predictions_query = Prediction.query.filter_by(doctor_id=current_user.id)
        
        # Get counts
        total_patients = patients_query.count()
        total_predictions = predictions_query.count()
        
        # Get recent predictions (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_predictions = predictions_query.filter(
            Prediction.created_at >= seven_days_ago
        ).count()
        
        # Get risk distribution
        low_risk = predictions_query.filter(Prediction.risk_category == 'LOW').count()
        medium_risk = predictions_query.filter(Prediction.risk_category == 'MEDIUM').count()
        high_risk = predictions_query.filter(Prediction.risk_category == 'HIGH').count()
        
        # Get top risk factors (from SHAP values in recent predictions)
        recent_preds_for_shap = predictions_query.filter(
            Prediction.created_at >= seven_days_ago
        ).limit(50).all()
        
        # Aggregate SHAP values to find important features
        shap_aggregated = {}
        for pred in recent_preds_for_shap:
            if pred.shap_values:
                try:
                    if isinstance(pred.shap_values, dict):
                        shap_dict = pred.shap_values
                    elif isinstance(pred.shap_values, str):
                        shap_dict = json.loads(pred.shap_values)
                    else:
                        shap_dict = {}
                    
                    # Handle both nested and flat SHAP formats
                    feature_importance_map = {}
                    if 'feature_importance' in shap_dict:
                        feature_importance_map = shap_dict['feature_importance']
                    elif shap_dict:
                        feature_importance_map = shap_dict
                        
                    if feature_importance_map:
                        for feature, importance in feature_importance_map.items():
                            if feature not in shap_aggregated:
                                shap_aggregated[feature] = 0
                            shap_aggregated[feature] += abs(importance)
                except Exception as e:
                    # Skip invalid SHAP data
                    print(f"Error processing SHAP values: {e}")
                    continue
        
        # Sort features by importance
        sorted_features = sorted(shap_aggregated.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get alerts summary
        high_risk_predictions = predictions_query.filter(
            Prediction.risk_category == 'HIGH'
        ).limit(10).all()
        
        alerts_summary = []
        for pred in high_risk_predictions:
            if pred.input_features:
                try:
                    if isinstance(pred.input_features, dict):
                        input_features = pred.input_features
                    elif isinstance(pred.input_features, str):
                        input_features = json.loads(pred.input_features)
                    else:
                        input_features = {}
                                    
                    alert_info = {
                        'patient_id': str(pred.patient_id),
                        'risk_score': pred.risk_score,
                        'date': pred.created_at.isoformat()
                    }
                                    
                    # Add notable risk factors
                    notable_factors = []
                    if input_features.get('hypertension', 0) == 1:
                        notable_factors.append('Hypertension')
                    if input_features.get('heart_disease', 0) == 1:
                        notable_factors.append('Heart Disease')
                    if input_features.get('avg_glucose_level', 0) > 120:
                        notable_factors.append('High Glucose')
                    if input_features.get('bmi', 0) > 30:
                        notable_factors.append('Obesity')
                                 
                    alert_info['factors'] = notable_factors
                    alerts_summary.append(alert_info)
                except Exception as e:
                    # Skip invalid input features
                    print(f"Error processing input features: {e}")
                    continue
        
        dashboard_data = {
            'summary': {
                'total_patients': total_patients,
                'total_predictions': total_predictions,
                'recent_predictions': recent_predictions,
                'low_risk_count': low_risk,
                'medium_risk_count': medium_risk,
                'high_risk_count': high_risk
            },
            'risk_distribution': {
                'LOW': low_risk,
                'MEDIUM': medium_risk,
                'HIGH': high_risk
            },
            'top_risk_factors': [{'factor': f[0], 'importance': f[1]} for f in sorted_features],
            'alerts_summary': alerts_summary
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@dashboard_bp.route('/api/dashboard/summary', methods=['GET'])
@token_required
def get_dashboard_summary(current_user):
    """
    Get unified dashboard summary with exact counts
    """
    try:
        # Build query based on user role
        if current_user.role == 'admin':
            # Admin sees all data
            patients_query = Patient.query
            predictions_query = Prediction.query
        else:
            # Doctors see only their data
            patients_query = Patient.query.filter_by(doctor_id=current_user.id)
            predictions_query = Prediction.query.filter_by(doctor_id=current_user.id)
        
        # Get counts
        total_patients = patients_query.count()
        total_predictions = predictions_query.count()
        
        # Get recent predictions (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_predictions = predictions_query.filter(
            Prediction.created_at >= seven_days_ago
        ).count()
        
        # Get high risk cases
        high_risk_cases = predictions_query.filter(
            Prediction.risk_category == 'HIGH'
        ).count()
        
        # Log the counts for debugging
        print(f'Dashboard summary - Total Patients: {total_patients}, '
              f'Total Predictions: {total_predictions}, '
              f'Recent: {recent_predictions}, '
              f'High Risk: {high_risk_cases}')
        
        summary_data = {
            'totalPatients': total_patients,
            'totalPredictions': total_predictions,
            'recentPredictions': recent_predictions,
            'highRiskCases': high_risk_cases
        }
        
        return jsonify(summary_data), 200
        
    except Exception as e:
        print(f'Error in get_dashboard_summary: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@dashboard_bp.route('/api/dashboard/shap', methods=['GET'])
@token_required
def get_dashboard_shap(current_user):
    """
    Get SHAP values for dashboard visualization
    """
    try:
        # Build query based on user role
        if current_user.role == 'admin':
            predictions_query = Prediction.query
        else:
            predictions_query = Prediction.query.filter_by(doctor_id=current_user.id)
        
        # Get recent predictions with SHAP data
        recent_predictions = predictions_query.order_by(Prediction.created_at.desc()).limit(20).all()
        
        # Aggregate SHAP values
        shap_aggregated = {}
        valid_predictions = 0
        
        for pred in recent_predictions:
            if pred.shap_values:
                try:
                    if isinstance(pred.shap_values, str):
                        shap_dict = json.loads(pred.shap_values)
                    else:
                        shap_dict = pred.shap_values
                    
                    # Extract feature importance
                    feature_importance_map = {}
                    if 'feature_importance' in shap_dict:
                        feature_importance_map = shap_dict['feature_importance']
                    elif shap_dict:
                        feature_importance_map = shap_dict
                    
                    if feature_importance_map:
                        for feature, importance in feature_importance_map.items():
                            if feature not in shap_aggregated:
                                shap_aggregated[feature] = 0
                            shap_aggregated[feature] += abs(importance)
                        valid_predictions += 1
                except Exception as e:
                    print(f"Error processing SHAP for prediction {pred.id}: {e}")
                    continue
        
        # Average the importance values
        if valid_predictions > 0:
            for feature in shap_aggregated:
                shap_aggregated[feature] /= valid_predictions
        
        # Convert to array format and sort
        shap_features = []
        for feature, importance in shap_aggregated.items():
            shap_features.append({
                'feature': feature,
                'importance': importance
            })
        
        # Sort by importance and return top 10
        shap_features.sort(key=lambda x: x['importance'], reverse=True)
        
        print(f"Returning {len(shap_features[:10])} SHAP features for dashboard")
        return jsonify(shap_features[:10]), 200
        
    except Exception as e:
        print(f'Error in get_dashboard_shap: {str(e)}')
        return jsonify([]), 200


@dashboard_bp.route('/api/dashboard/risk-distribution', methods=['GET'])
@token_required
def get_risk_distribution(current_user):
    """
    Get risk distribution always returning all categories
    """
    try:
        # Build query based on user role
        if current_user.role == 'admin':
            # Admin sees all data
            predictions_query = Prediction.query
        else:
            # Doctors see only their data
            predictions_query = Prediction.query.filter_by(doctor_id=current_user.id)
        
        # Get counts for each risk category (always return all)
        low_count = predictions_query.filter(Prediction.risk_category == 'LOW').count()
        medium_count = predictions_query.filter(Prediction.risk_category == 'MEDIUM').count()
        high_count = predictions_query.filter(Prediction.risk_category == 'HIGH').count()
        
        # Log the distribution for debugging
        print(f'Risk distribution - Low: {low_count}, Medium: {medium_count}, High: {high_count}')
        
        risk_distribution = {
            'low': low_count,
            'medium': medium_count,
            'high': high_count
        }
        
        return jsonify(risk_distribution), 200
        
    except Exception as e:
        print(f'Error in get_risk_distribution: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@dashboard_bp.route('/api/dashboard/patients', methods=['GET'])
@token_required
def get_dashboard_patients(current_user):
    """
    Get patient data for dashboard visualization
    """
    try:
        # Build query based on user role
        if current_user.role == 'admin':
            patients_query = Patient.query
        else:
            patients_query = Patient.query.filter_by(doctor_id=current_user.id)
        
        # Get patient demographics
        patients = patients_query.all()
        
        # Group by various demographics
        age_groups = {'0-30': 0, '31-50': 0, '51-70': 0, '71+': 0}
        gender_counts = {'Male': 0, 'Female': 0, 'Other': 0}
        residence_counts = {'Urban': 0, 'Rural': 0}
        
        for patient in patients:
            # Age groups
            if patient.age is not None:
                if patient.age <= 30:
                    age_groups['0-30'] += 1
                elif patient.age <= 50:
                    age_groups['31-50'] += 1
                elif patient.age <= 70:
                    age_groups['51-70'] += 1
                else:
                    age_groups['71+'] += 1
            
            # Gender
            if patient.gender:
                gender_counts[patient.gender] = gender_counts.get(patient.gender, 0) + 1
        
        # Get prediction stats for patients
        patient_stats = []
        for patient in patients[:10]:  # Limit for performance
            latest_pred = Prediction.query.filter_by(patient_id=patient.id)\
                                         .order_by(Prediction.created_at.desc()).first()
            
            if latest_pred:
                patient_stats.append({
                    'patient_id': str(patient.id),
                    'name': patient.full_name,
                    'age': patient.age,
                    'gender': patient.gender,
                    'latest_risk_score': latest_pred.risk_score,
                    'latest_risk_category': latest_pred.risk_category,
                    'last_prediction_date': latest_pred.created_at.isoformat()
                })
        
        demographics_data = {
            'age_distribution': age_groups,
            'gender_distribution': gender_counts,
            'residence_distribution': residence_counts,
            'patient_list': patient_stats
        }
        
        return jsonify(demographics_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500