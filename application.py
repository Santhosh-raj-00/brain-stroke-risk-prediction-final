from flask import Flask
from config import config
from extensions import db, migrate, jwt, cors
import os


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors_origin = os.environ.get("CORS_ORIGINS", "*")
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": cors_origin,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.patients import patients_bp
    from routes.prediction import prediction_bp
    from routes.history import history_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp
    from routes.shap import shap_bp
    
    print(f"Registering auth_bp: {auth_bp.name}")
    app.register_blueprint(auth_bp)
    print(f"Registering patients_bp: {patients_bp.name}")
    app.register_blueprint(patients_bp)
    print(f"Registering prediction_bp: {prediction_bp.name}")
    app.register_blueprint(prediction_bp)
    print(f"Registering history_bp: {history_bp.name}")
    app.register_blueprint(history_bp)
    print(f"Registering dashboard_bp: {dashboard_bp.name}")
    app.register_blueprint(dashboard_bp)
    print(f"Registering admin_bp: {admin_bp.name}")
    app.register_blueprint(admin_bp)
    
    print(f"Registering shap_bp: {shap_bp.name}")
    app.register_blueprint(shap_bp)

    from routes.visualizations import visualizations_bp
    print(f"Registering visualizations_bp: {visualizations_bp.name}")
    app.register_blueprint(visualizations_bp)
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Ensure database tables exist BEFORE returning the app
    with app.app_context():
        # Import models so SQLAlchemy knows the schemas
        from database.models.user import User
        from database.models.patient import Patient
        from database.models.prediction import Prediction
        db.create_all()
        
    return app


# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'message': 'Token has expired'}, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'message': 'Invalid token'}, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'message': 'Access token required'}, 401


app = create_app(os.environ.get("FLASK_ENV", "production"))

@app.route("/api/health")
def health():
    return {"status": "ok", "timestamp": "2026-02-09T00:00:00Z"}, 200

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the actual error for debugging
    app.logger.error(f"Internal server error: {str(e)}", exc_info=True)
    # Return generic error to frontend
    return {"error": "An internal error occurred. Please try again later."}, 500

if __name__ == "__main__":
    # Production configuration - no debug mode
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))