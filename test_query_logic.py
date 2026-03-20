# Simple database test to verify the query logic
import sqlite3
import os

db_path = os.path.join('instance', 'stroke_prediction.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Testing patient prediction query logic ===")

# Test 1: Get all patients with their latest predictions
print("\n1. All patients with latest predictions:")
cursor.execute("""
    SELECT p.full_name, 
           pr.risk_score, 
           pr.risk_category,
           pr.created_at
    FROM patients p
    LEFT JOIN (
        SELECT patient_id, 
               risk_score, 
               risk_category,
               created_at,
               ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY created_at DESC) as rn
        FROM predictions
    ) pr ON p.id = pr.patient_id AND pr.rn = 1
    ORDER BY p.full_name
""")
results = cursor.fetchall()
for row in results:
    risk_info = f"{row[1]} ({row[2]})" if row[1] is not None else "No predictions"
    print(f"  - {row[0]}: {risk_info}")

# Test 2: Count patients by risk level
print("\n2. Patient count by risk level (using query logic):")
cursor.execute("""
    SELECT pr.risk_category, COUNT(*) as count
    FROM patients p
    JOIN (
        SELECT patient_id, 
               risk_score, 
               risk_category,
               ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY created_at DESC) as rn
        FROM predictions
    ) pr ON p.id = pr.patient_id AND pr.rn = 1
    GROUP BY pr.risk_category
    ORDER BY pr.risk_category
""")
risk_counts = cursor.fetchall()
for category, count in risk_counts:
    print(f"  - {category}: {count}")

conn.close()