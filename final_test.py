import requests
import json

# Test the patients endpoint with risk level filtering
r = requests.get('http://localhost:5000/api/patients?risk_level=LOW')
print('Status:', r.status_code)
data = r.json()
print('Total patients returned:', len(data))
print('Patients with risk data:')
for p in data[:5]:
    print(f'  - {p.get("full_name", "N/A")}: {p.get("last_risk_category", "No data")} ({p.get("last_risk_score", "N/A")})')