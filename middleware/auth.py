from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from database.models.user import User
from extensions import db


def token_required(f):
    """
    Decorator to protect routes with JWT token
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            # Get user from database
            current_user = User.query.filter_by(id=current_user_id).first()
            if not current_user:
                return jsonify({'message': 'User session invalid. Please login again.'}), 401
            
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Token is invalid'}), 401
    
    return decorated


def role_required(allowed_roles):
    """
    Decorator to restrict access based on user role
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # Get user from database
                current_user = User.query.filter_by(id=current_user_id).first()
                if not current_user:
                    return jsonify({'message': 'User session invalid. Please login again.'}), 401
                
                # Check if user role is in allowed roles
                if current_user.role not in allowed_roles:
                    return jsonify({'message': 'Insufficient permissions'}), 403
                
                return f(current_user, *args, **kwargs)
            except Exception as e:
                return jsonify({'message': 'Token is invalid'}), 401
        return decorated
    return decorator