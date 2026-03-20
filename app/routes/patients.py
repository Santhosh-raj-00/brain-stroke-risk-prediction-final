from flask import jsonify, request
from extensions import db
from database.models.patient import Patient
from database.models.user import User
import uuid

# Import blueprint from parent package
from . import main_bp

@main_bp.route('/api/patients', methods=['GET'])
def get_patients():
    doctor_id = request.args.get('doctor_id')
    
    if doctor_id:
        patients = Patient.query.filter_by(doctor_id=doctor_id).all()
    else:
        patients = Patient.query.all()
    
    return jsonify([patient.to_dict() for patient in patients])

@main_bp.route('/api/patients', methods=['POST'])
def create_patient():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('full_name') or not data.get('doctor_id'):
        return jsonify({'error': 'Missing required fields: full_name, doctor_id'}), 400
    
    # Check if doctor exists
    doctor = User.query.filter_by(id=data['doctor_id']).first()
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404
    
    # Create new patient
    patient = Patient(
        doctor_id=data['doctor_id'],
        full_name=data['full_name'],
        age=data.get('age'),
        gender=data.get('gender'),
        marital_status=data.get('marital_status'),
        residence_type=data.get('residence_type'),
        work_type=data.get('work_type')
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return jsonify(patient.to_dict()), 201

@main_bp.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id).first_or_404()
    return jsonify(patient.to_dict())

@main_bp.route('/api/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id).first_or_404()
    data = request.get_json()
    
    # Update allowed fields
    if 'full_name' in data:
        patient.full_name = data['full_name']
    if 'age' in data:
        patient.age = data['age']
    if 'gender' in data:
        patient.gender = data['gender']
    if 'marital_status' in data:
        patient.marital_status = data['marital_status']
    if 'residence_type' in data:
        patient.residence_type = data['residence_type']
    if 'work_type' in data:
        patient.work_type = data['work_type']
    
    db.session.commit()
    return jsonify(patient.to_dict())

@main_bp.route('/api/patients/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id).first_or_404()
    
    # Delete the patient - cascade delete will handle predictions automatically
    db.session.delete(patient)
    db.session.commit()
    
    return jsonify({'message': 'Patient and all related predictions deleted successfully'})