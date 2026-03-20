# Test the actual SQL query being generated
import sys
import os
sys.path.append('.')

from app import create_app
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction
from sqlalchemy import func, and_, desc

app = create_app()
with app.app_context():
    print("=== Testing SQL Query Generation ===")
    
    # Test the exact query logic from patients.py
    latest_pred_subquery = db.session.query(
        Prediction.patient_id,
        Prediction.risk_score.label('last_risk_score'),
        Prediction.risk_category.label('last_risk_category'),
        Prediction.created_at.label('last_prediction_date'),
        func.row_number().over(
            partition_by=Prediction.patient_id,
            order_by=desc(Prediction.created_at)
        ).label('rn')
    ).subquery()
    
    # Filter to only get the latest prediction per patient
    latest_predictions = db.session.query(
        latest_pred_subquery.c.patient_id,
        latest_pred_subquery.c.last_risk_score,
        latest_pred_subquery.c.last_risk_category,
        latest_pred_subquery.c.last_prediction_date
    ).filter(latest_pred_subquery.c.rn == 1).subquery()
    
    # Main query joining patients with latest predictions
    query = db.session.query(
        Patient,
        latest_predictions.c.last_risk_score,
        latest_predictions.c.last_risk_category,
        latest_predictions.c.last_prediction_date
    ).outerjoin(
        latest_predictions, 
        Patient.id == latest_predictions.c.patient_id
    )
    
    print("Query without filter:")
    print(str(query.statement.compile(dialect=db.engine.dialect)))
    
    # Test with risk filter
    risk_filter = "LOW"
    filtered_query = query.filter(
        and_(
            latest_predictions.c.last_risk_category == risk_filter.upper(),
            latest_predictions.c.last_risk_score.isnot(None)
        )
    )
    
    print("\nQuery with LOW risk filter:")
    print(str(filtered_query.statement.compile(dialect=db.engine.dialect)))
    
    # Execute queries
    print("\n=== Executing Queries ===")
    print("All patients count:", query.count())
    print("LOW risk patients count:", filtered_query.count())
    
    # Show results
    print("\nLOW risk patients:")
    results = filtered_query.all()
    for patient, risk_score, risk_category, prediction_date in results:
        print(f"  - {patient.full_name}: {risk_score} ({risk_category})")