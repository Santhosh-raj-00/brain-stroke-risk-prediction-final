from flask import jsonify, request
from app import db
from app.models.prediction import Prediction
from app.models.patient import Patient
from app.models.user import User
import uuid

# Import blueprint from parent package
from . import main_bp

@main_bp.route('/api/predictions-crud', methods=['GET'])
def get_predictions_crud():
    patient_id = request.args.get('patient_id')
    doctor_id = request.args.get('doctor_id')
    
    query = Prediction.query
    
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    
    predictions = query.order_by(Prediction.created_at.desc()).all()
    
    return jsonify([pred.to_dict() for pred in predictions])

@main_bp.route('/api/predictions-crud', methods=['POST'])
def create_prediction_crud():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('patient_id') or not data.get('doctor_id') or data.get('risk_probability') is None:
        return jsonify({'error': 'Missing required fields: patient_id, doctor_id, risk_probability'}), 400
    
    # Check if patient exists
    patient = Patient.query.filter_by(id=data['patient_id']).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Check if doctor exists
    doctor = User.query.filter_by(id=data['doctor_id']).first()
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Create new prediction
    prediction = Prediction(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        risk_probability=float(data['risk_probability']),
        risk_category=data.get('risk_category', 'MEDIUM'),  # Default to MEDIUM
        model_version=data.get('model_version', '1.0.0'),
        input_features=data.get('input_features'),
        shap_values=data.get('shap_values')
    )
    
    db.session.add(prediction)
    db.session.commit()
    
    return jsonify(prediction.to_dict()), 201

@main_bp.route('/api/predictions-crud/<prediction_id>', methods=['GET'])
def get_prediction_crud(prediction_id):
    prediction = Prediction.query.filter_by(id=prediction_id).first_or_404()
    return jsonify(prediction.to_dict())

@main_bp.route('/api/predictions-crud/<prediction_id>', methods=['PUT'])
def update_prediction_crud(prediction_id):
    prediction = Prediction.query.filter_by(id=prediction_id).first_or_404()
    data = request.get_json()
    
    # Update allowed fields
    if 'risk_probability' in data:
        prediction.risk_probability = float(data['risk_probability'])
    if 'risk_category' in data:
        prediction.risk_category = data['risk_category']
    if 'model_version' in data:
        prediction.model_version = data['model_version']
    if 'input_features' in data:
        prediction.input_features = data['input_features']
    if 'shap_values' in data:
        prediction.shap_values = data['shap_values']
    
    db.session.commit()
    return jsonify(prediction.to_dict())