from flask import Blueprint, request, jsonify
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction
from middleware.auth import token_required, role_required
from middleware.roles import doctor_required, admin_required
from datetime import datetime
import uuid

history_bp = Blueprint('history', __name__)


@history_bp.route('/api/history', methods=['GET'])
@token_required
def get_history(current_user):
    """
    Get prediction history for patients
    Supports filtering by patient, date range, and risk category
    """
    try:
        # Get query parameters
        patient_id = request.args.get('patient_id', None)
        doctor_id = request.args.get('doctor_id', None)
        risk_filter = request.args.get('risk', None)  # LOW, MEDIUM, HIGH
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        
        # Build query based on user role
        query = Prediction.query
        
        if current_user.role == 'doctor':
            # Doctors can only see their patients' predictions
            query = query.filter(Prediction.doctor_id == current_user.id)
        # Admins can see all predictions
        
        # Apply filters
        if patient_id:
            query = query.filter(Prediction.patient_id == patient_id)
        
        if doctor_id and current_user.role == 'admin':
            # Only admins can filter by other doctors
            query = query.filter(Prediction.doctor_id == doctor_id)
        
        if risk_filter:
            # Handle case-insensitive risk filter
            risk_upper = risk_filter.upper()
            if risk_upper in ['LOW', 'MEDIUM', 'HIGH']:
                query = query.filter(Prediction.risk_category == risk_upper)
        
        if date_from:
            try:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(Prediction.created_at >= date_from_obj)
            except ValueError:
                # Handle different date formats
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                    query = query.filter(Prediction.created_at >= date_from_obj)
                except ValueError:
                    pass  # Invalid date format, ignore filter
        
        if date_to:
            try:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(Prediction.created_at <= date_to_obj)
            except ValueError:
                # Handle different date formats
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                    query = query.filter(Prediction.created_at <= date_to_obj)
                except ValueError:
                    pass  # Invalid date format, ignore filter
        
        # Execute query and order by date
        predictions = query.order_by(Prediction.created_at.desc()).all()
        
        # Format response with patient details
        result = []
        for pred in predictions:
            # Get patient info
            patient = Patient.query.filter_by(id=pred.patient_id).first()
            
            history_item = pred.to_dict()
            history_item['patient'] = patient.to_dict() if patient else None
            # Ensure risk score is properly referenced
            if hasattr(pred, 'risk_probability') and pred.risk_probability is not None:
                history_item['risk_score'] = pred.risk_probability
            elif hasattr(pred, 'risk_score'):
                history_item['risk_score'] = pred.risk_score
            result.append(history_item)
        
        print(f"History query returned {len(result)} records with risk filter: {risk_filter}")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in get_history: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@history_bp.route('/api/history/trends', methods=['GET'])
@token_required
def get_trends(current_user):
    """
    Get risk trends for a patient over time
    """
    try:
        patient_id = request.args.get('patient_id')
        
        if not patient_id:
            return jsonify({'error': 'patient_id is required'}), 400
        
        # Check if user has access to this patient
        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        if current_user.role == 'doctor' and patient.doctor_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all predictions for the patient ordered by date
        predictions = Prediction.query.filter_by(patient_id=patient_id)\
                                    .order_by(Prediction.created_at.asc()).all()
        
        # Format trends data
        trends = []
        for pred in predictions:
            # Ensure risk score is properly referenced
            risk_score = pred.risk_probability if hasattr(pred, 'risk_probability') and pred.risk_probability is not None else getattr(pred, 'risk_score', 0)
            
            # Extract input features for glucose level
            input_features = {}
            if hasattr(pred, 'input_features'):
                if isinstance(pred.input_features, str):
                    try:
                        import json
                        input_features = json.loads(pred.input_features)
                    except:
                        input_features = {}
                elif isinstance(pred.input_features, dict):
                    input_features = pred.input_features
                else:
                    input_features = {}
            
            trends.append({
                'date': pred.created_at.isoformat(),
                'risk_score': risk_score,
                'risk_category': pred.risk_category,
                'model_version': pred.model_version,
                'input_features': input_features
            })
        
        return jsonify({
            'patient_id': patient_id,
            'trends': trends
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500