from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
# from config.database import engine
# from app.models import Base

# Import extensions
from extensions import db, migrate

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stroke_prediction.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize JWT
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
    jwt = JWTManager(app)
    CORS(app)
    
    # Import and register blueprints
    from app.routes import main_bp
    from routes.auth import auth_bp
    from routes.prediction import prediction_bp
    from routes.patients import patients_bp
    from routes.history import history_bp
    from routes.dashboard import dashboard_bp
    from routes.admin import admin_bp
    from routes.visualizations import visualizations_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(prediction_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(visualizations_bp)
    
    # Create tables
    with app.app_context():
        # Import all models to ensure they are registered
        from app.models import doctor_profile
        db.create_all()
        
    return app