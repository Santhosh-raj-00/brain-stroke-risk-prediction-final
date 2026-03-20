import sqlite3
import os

# Direct database test to verify the expected results
db_path = os.path.join('instance', 'stroke_prediction.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Direct Database Query Test ===")

# Test the exact logic that should be happening
print("\n1. Patients with LOW risk predictions:")
cursor.execute("""
    SELECT p.full_name, 
           pr.risk_score,
           pr.risk_category
    FROM patients p
    JOIN (
        SELECT patient_id, 
               risk_score,
               risk_category,
               ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY created_at DESC) as rn
        FROM predictions
    ) pr ON p.id = pr.patient_id AND pr.rn = 1
    WHERE pr.risk_category = 'LOW'
    ORDER BY p.full_name
""")
low_risk_patients = cursor.fetchall()
print(f"Found {len(low_risk_patients)} LOW risk patients:")
for name, score, category in low_risk_patients:
    print(f"  - {name}: {score} ({category})")

print("\n2. Patients with MEDIUM risk predictions:")
cursor.execute("""
    SELECT p.full_name, 
           pr.risk_score,
           pr.risk_category
    FROM patients p
    JOIN (
        SELECT patient_id, 
               risk_score,
               risk_category,
               ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY created_at DESC) as rn
        FROM predictions
    ) pr ON p.id = pr.patient_id AND pr.rn = 1
    WHERE pr.risk_category = 'MEDIUM'
    ORDER BY p.full_name
""")
medium_risk_patients = cursor.fetchall()
print(f"Found {len(medium_risk_patients)} MEDIUM risk patients:")
for name, score, category in medium_risk_patients:
    print(f"  - {name}: {score} ({category})")

conn.close()