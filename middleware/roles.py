from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from database.models.user import User, UserRole
from extensions import db


def doctor_required(f):
    """
    Decorator to restrict access to doctors only
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            current_user = User.query.filter_by(id=current_user_id).first()
            if not current_user:
                return jsonify({'message': 'User not found'}), 404
            
            if current_user.role != UserRole.DOCTOR:
                return jsonify({'message': 'Doctor access required'}), 403
            
            return f(current_user, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Token validation failed: {str(e)}")
            return jsonify({'message': f'Token is invalid: {str(e)}'}), 401
    
    return decorated


def admin_required(f):
    """
    Decorator to restrict access to admins only
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            current_user = User.query.filter_by(id=current_user_id).first()
            if not current_user:
                return jsonify({'message': 'User not found'}), 404
            
            if current_user.role != UserRole.ADMIN:
                return jsonify({'message': 'Admin access required'}), 403
            
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Token is invalid'}), 401
    
    return decorated