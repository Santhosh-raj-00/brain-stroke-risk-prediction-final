from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.routes import users, patients, predictions

# Basic route
@main_bp.route('/')
def home():
    return {
        "message": "Brain Stroke Risk Prediction System API",
        "version": "1.0.0",
        "endpoints": [
            "/api/users",
            "/api/patients", 
            "/api/predictions"
        ]
    }