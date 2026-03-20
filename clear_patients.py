import sys
import os
sys.path.append('.')

from app import create_app
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction

def clear_all_patient_data():
    """Clear all patients and their predictions from the database"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== Clearing Patient Data ===")
            
            # Count existing data
            patient_count = Patient.query.count()
            prediction_count = Prediction.query.count()
            
            print(f"Current data:")
            print(f"  - Patients: {patient_count}")
            print(f"  - Predictions: {prediction_count}")
            
            # Delete all predictions first (due to foreign key constraints)
            print("\nDeleting all predictions...")
            Prediction.query.delete()
            db.session.commit()
            print("✓ All predictions deleted")
            
            # Delete all patients
            print("Deleting all patients...")
            Patient.query.delete()
            db.session.commit()
            print("✓ All patients deleted")
            
            # Verify cleanup
            final_patient_count = Patient.query.count()
            final_prediction_count = Prediction.query.count()
            
            print(f"\nFinal data count:")
            print(f"  - Patients: {final_patient_count}")
            print(f"  - Predictions: {final_prediction_count}")
            
            print("\n✅ Database cleared successfully!")
            
        except Exception as e:
            print(f"❌ Error clearing data: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    clear_all_patient_data()