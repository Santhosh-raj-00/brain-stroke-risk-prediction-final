from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash
from extensions import db
from database.models.user import User
from middleware.auth import token_required
from datetime import datetime
import uuid

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/test-cors', methods=['GET'])
def test_cors():
    """
    Simple test endpoint to verify CORS is working
    """
    return jsonify({'message': 'CORS is working!', 'timestamp': datetime.utcnow().isoformat()})


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    Expected payload: { "email": "...", "password": "...", "requested_role": "..." }
    """
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials. If you are new, please Register.'}), 401
    
    # Check if the requested role matches the user's role
    requested_role = data.get('requested_role')
    if requested_role and user.role != requested_role:
        return jsonify({'message': f'Access denied: This is a {requested_role} login portal. Your account is registered as {user.role}.'}), 403
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create access token with user info
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name
        }
    }), 200


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """
    User registration endpoint
    Expected payload: { "email": "...", "password": "...", "full_name": "...", "role": "doctor|admin" }
    For admin registration, also requires: { "admin_access_key": "..." }
    """
    data = request.get_json()
    
    required_fields = ['email', 'password', 'full_name', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400
    
    # Validate role
    if data['role'] not in ['doctor', 'admin']:
        return jsonify({'message': 'Invalid role. Must be doctor or admin'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'User with this email already exists'}), 409
    
    # For admin registration, validate admin access key
    if data['role'] == 'admin':
        admin_access_key = data.get('admin_access_key')
        if not admin_access_key:
            return jsonify({'message': 'Admin access key is required for admin registration'}), 400
        
        # In a real application, you would validate this against a secret key
        # For this demo, we'll use a simple hardcoded key
        import os
        expected_key = os.environ.get('ADMIN_ACCESS_KEY', 'admin#143')
        if admin_access_key != expected_key:
            return jsonify({'message': 'Invalid admin access key'}), 401
    
    # Create new user
    user = User(
        full_name=data['full_name'],
        email=data['email'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
            'full_name': user.full_name
        }
    }), 201


@auth_bp.route('/api/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Get current user profile
    Requires valid JWT token
    """
    return jsonify({
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout endpoint (client-side token invalidation)
    """
    # In a real application, you might want to add tokens to a blacklist
    return jsonify({'message': 'Successfully logged out'}), 200