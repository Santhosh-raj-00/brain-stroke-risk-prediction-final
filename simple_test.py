import sys
sys.path.append('.')

from app import create_app
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction

app = create_app()
with app.app_context():
    print('Total patients:', Patient.query.count())
    print('Total predictions:', Prediction.query.count())
    
    # Test simple join
    from sqlalchemy import func
    result = db.session.query(
        Patient.full_name,
        Prediction.risk_category
    ).join(Prediction, Patient.id == Prediction.patient_id).all()
    
    print("Patients with predictions:")
    for name, category in result:
        print(f"  - {name}: {category}")