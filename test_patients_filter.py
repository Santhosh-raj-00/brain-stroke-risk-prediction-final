import requests
import json

# Test the patients endpoint with risk level filtering
base_url = 'http://localhost:5000'

# Test without risk filter (should show all patients)
print("=== Testing without risk filter ===")
response = requests.get(f'{base_url}/api/patients')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total patients: {len(data)}")
    for patient in data[:3]:  # Show first 3 patients
        print(f"  - {patient.get('full_name', 'N/A')}: {patient.get('last_risk_category', 'No predictions')}")

print("\n=== Testing with LOW risk filter ===")
response = requests.get(f'{base_url}/api/patients?risk_level=LOW')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"LOW risk patients: {len(data)}")
    for patient in data:
        print(f"  - {patient.get('full_name', 'N/A')}: {patient.get('last_risk_category', 'No predictions')}")

print("\n=== Testing with HIGH risk filter ===")
response = requests.get(f'{base_url}/api/patients?risk_level=HIGH')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"HIGH risk patients: {len(data)}")
    for patient in data:
        print(f"  - {patient.get('full_name', 'N/A')}: {patient.get('last_risk_category', 'No predictions')}")