from flask import jsonify, request
from app import db
from app.models.user import User
from app.models.doctor_profile import DoctorProfile
from werkzeug.security import generate_password_hash
import uuid

# Import blueprint from parent package
from . import main_bp

@main_bp.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@main_bp.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('full_name') or not data.get('role'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400
    
    # Hash the password
    password_hash = generate_password_hash(data.get('password', 'default_password'))
    
    # Create new user
    new_user = User(
        full_name=data['full_name'],
        email=data['email'],
        password_hash=password_hash,
        role=data['role']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.to_dict()), 201

@main_bp.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    return jsonify(user.to_dict())

@main_bp.route('/api/users/<user_id>/profile', methods=['GET'])
def get_doctor_profile(user_id):
    profile = DoctorProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Doctor profile not found'}), 404
    return jsonify(profile.to_dict())

@main_bp.route('/api/users/<user_id>/profile', methods=['POST'])
def create_doctor_profile(user_id):
    data = request.get_json()
    
    # Check if user exists
    user = User.query.filter_by(id=user_id).first_or_404()
    
    # Check if profile already exists
    existing_profile = DoctorProfile.query.filter_by(user_id=user_id).first()
    if existing_profile:
        return jsonify({'error': 'Doctor profile already exists for this user'}), 400
    
    # Create new doctor profile
    profile = DoctorProfile(
        user_id=user_id,
        license_id=data.get('license_id'),
        hospital_name=data.get('hospital_name'),
        specialization=data.get('specialization')
    )
    
    db.session.add(profile)
    db.session.commit()
    
    return jsonify(profile.to_dict()), 201