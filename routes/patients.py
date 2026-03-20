from flask import Blueprint, request, jsonify
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction
from middleware.auth import token_required, role_required
from middleware.roles import doctor_required, admin_required
import uuid

patients_bp = Blueprint('patients', __name__)


@patients_bp.route('/api/patients', methods=['GET'])
@token_required
def get_patients(current_user):
    """
    Get all patients for the current user (doctor) or all patients (admin)
    Supports filtering by risk category
    Returns patients with their latest prediction data
    """
    try:
        # Get query parameters
        risk_filter = request.args.get('risk_level', None)  # LOW, MEDIUM, HIGH
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        
        print(f"DEBUG: risk_filter = {risk_filter}")  # Debug log
        print(f"DEBUG: current_user.role = {current_user.role}")  # Debug log
        print(f"DEBUG: current_user.id = {current_user.id}")  # Debug log
        
        # Simple approach - get all patients first
        if current_user.role == 'doctor':
            patients = Patient.query.filter(Patient.doctor_id == current_user.id).all()
        else:
            patients = Patient.query.all()
        
        print(f"DEBUG: Found {len(patients)} total patients")  # Debug log
        
        # Get latest prediction for each patient
        result = []
        for patient in patients:
            patient_dict = patient.to_dict()
            
            # Get latest prediction for this patient
            latest_prediction = Prediction.query.filter(
                Prediction.patient_id == patient.id
            ).order_by(Prediction.created_at.desc()).first()
            
            if latest_prediction:
                # Apply risk filter if specified
                if risk_filter and latest_prediction.risk_category != risk_filter.upper():
                    continue  # Skip this patient
                
                patient_dict['last_risk_score'] = float(latest_prediction.risk_score)
                patient_dict['last_risk_category'] = latest_prediction.risk_category
                patient_dict['last_prediction_date'] = latest_prediction.created_at.isoformat() if latest_prediction.created_at else None
            else:
                # No predictions for this patient
                if risk_filter:
                    continue  # Skip patients without predictions when filtering
                patient_dict['last_risk_score'] = None
                patient_dict['last_risk_category'] = None
                patient_dict['last_prediction_date'] = None
            
            result.append(patient_dict)
        
        print(f"DEBUG: Returning {len(result)} patients after filtering")  # Debug log
        return jsonify(result)
        
    except Exception as e:
        print(f"DEBUG: Error in get_patients: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500


@patients_bp.route('/api/patients', methods=['POST'])
@doctor_required
def create_patient(current_user):
    """
    Create a new patient
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'age', 'gender']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if patient already exists
        existing_patient = Patient.query.filter_by(
            full_name=data['full_name'],
            age=data['age'],
            doctor_id=current_user.id
        ).first()
        
        if existing_patient:
            return jsonify({'error': 'Patient already exists'}), 409
        
        # Create new patient
        patient = Patient(
            doctor_id=current_user.id,
            full_name=data['full_name'],
            age=int(data['age']),
            gender=data['gender'],
            marital_status=data.get('marital_status'),
            residence_type=data.get('residence_type'),
            work_type=data.get('work_type')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify(patient.to_dict()), 201
        
    except ValueError as ve:
        return jsonify({'error': f'Invalid input value: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@patients_bp.route('/api/patients/<patient_id>', methods=['GET'])
@token_required
def get_patient(current_user, patient_id):
    """
    Get a specific patient by ID
    """
    try:
        patient = Patient.query.filter_by(id=patient_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Check if user has permission to access this patient
        if current_user.role == 'doctor':
            if patient.doctor_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403
        # Admins can access all patients
        
        # Get all predictions for this patient
        predictions = Prediction.query.filter_by(patient_id=patient_id)\
                                     .order_by(Prediction.created_at.desc()).all()
        
        patient_dict = patient.to_dict()
        patient_dict['predictions'] = [pred.to_dict() for pred in predictions]
        
        return jsonify(patient_dict), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@patients_bp.route('/api/patients/<patient_id>', methods=['PUT'])
@doctor_required
def update_patient(current_user, patient_id):
    """
    Update a patient's information
    """
    try:
        patient = Patient.query.filter_by(id=patient_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Check if user owns this patient
        if patient.doctor_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data:
            patient.full_name = data['full_name']
        if 'age' in data:
            patient.age = int(data['age'])
        if 'gender' in data:
            patient.gender = data['gender']
        if 'marital_status' in data:
            patient.marital_status = data['marital_status']
        if 'residence_type' in data:
            patient.residence_type = data['residence_type']
        if 'work_type' in data:
            patient.work_type = data['work_type']
        
        db.session.commit()
        
        return jsonify(patient.to_dict()), 200
        
    except ValueError as ve:
        return jsonify({'error': f'Invalid input value: {str(ve)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@patients_bp.route('/api/patients/<patient_id>', methods=['DELETE'])
@doctor_required
def delete_patient(current_user, patient_id):
    """
    Delete a patient (hard delete with cascade)
    """
    try:
        patient = Patient.query.filter_by(id=patient_id).first()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Check if user owns this patient
        if patient.doctor_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Log before deletion
        print(f'Deleting patient {patient_id} and associated predictions...')
        
        # Count predictions that will be deleted due to cascade
        pred_count = Prediction.query.filter_by(patient_id=patient_id).count()
        print(f'Will delete {pred_count} predictions for patient {patient_id}')
        
        db.session.delete(patient)
        db.session.commit()
        
        print(f'Patient {patient_id} deleted successfully. {pred_count} predictions also deleted due to cascade.')
        
        return jsonify({'message': f'Patient deleted successfully. {pred_count} predictions also deleted.'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f'Error deleting patient {patient_id}: {str(e)}')
        return jsonify({'error': f'Server error: {str(e)}'}), 500