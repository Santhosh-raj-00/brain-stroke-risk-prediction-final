import sqlite3
import os

# Check current database state
db_path = os.path.join('instance', 'stroke_prediction.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check predictions table
print("=== PREDICTIONS TABLE ===")
cursor.execute("SELECT COUNT(*) FROM predictions")
prediction_count = cursor.fetchone()[0]
print(f"Total predictions: {prediction_count}")

if prediction_count > 0:
    cursor.execute("""
        SELECT p.full_name, pr.risk_score, pr.risk_category, pr.created_at
        FROM patients p
        JOIN predictions pr ON p.id = pr.patient_id
        ORDER BY pr.created_at DESC
        LIMIT 10
    """)
    predictions = cursor.fetchall()
    print("Recent predictions:")
    for pred in predictions:
        print(f"  - {pred[0]}: {pred[1]} ({pred[2]}) on {pred[3]}")
else:
    print("No predictions found")

# Check patients with predictions
print("\n=== PATIENTS WITH PREDICTIONS ===")
cursor.execute("""
    SELECT p.full_name, 
           pr.risk_score, 
           pr.risk_category,
           pr.created_at
    FROM patients p
    LEFT JOIN (
        SELECT DISTINCT patient_id, 
               risk_score, 
               risk_category,
               created_at
        FROM predictions
        ORDER BY created_at DESC
    ) pr ON p.id = pr.patient_id
    ORDER BY p.full_name
""")
patients = cursor.fetchall()
print("Patients and their latest predictions:")
for patient in patients:
    risk_info = f"{patient[1]} ({patient[2]})" if patient[1] is not None else "No predictions"
    print(f"  - {patient[0]}: {risk_info}")

conn.close()