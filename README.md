# AI-Based Brain Stroke Risk Prediction System

## 🚨 IMPORTANT: MAJOR UPDATE (v3.0) 🚨
**The system has been upgraded to use REAL CLINICAL DATA only.**
Please read `IMPLEMENTATION_GUIDE.md` immediately to set up the required datasets.
Synthetic data generation has been removed. The app will NOT predict without the Kaggle dataset.

---


A comprehensive healthcare application designed to predict stroke risk using machine learning models with explainable AI capabilities.

## Features

- **Secure Authentication**: Role-based access control for doctors and administrators
- **Patient Management**: Comprehensive patient records with demographic information
- **Stroke Risk Prediction**: ML-powered risk assessment with probability scores
- **Explainable AI**: SHAP values for understanding model decisions
- **Medical Imaging**: Support for MRI/CT scan processing
- **Clinical Alerts**: Automated flagging of critical health indicators
- **Audit Trail**: Complete security and compliance logging

## Database Schema

The system uses PostgreSQL with the following tables:

### Core Tables
- `users` - Authentication and role management
- `doctor_profiles` - Doctor-specific information
- `patients` - Patient demographic and clinical data
- `predictions` - Stroke risk predictions with ML inputs
- `prediction_images` - Medical imaging data
- `clinical_flags` - Health alerts and warnings
- `audit_logs` - Security and compliance logs

### Security Features
- Password hashing with bcrypt
- UUID primary keys
- Role-enforced access
- Comprehensive audit trails

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database:
   ```bash
   # Make sure PostgreSQL is running
   # Update database URL in config/database.py
   flask db upgrade  # If using Flask-Migrate
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## API Endpoints

### Users
- `GET /api/users` - Get all users
- `POST /api/users` - Create a new user
- `GET /api/users/{id}` - Get a specific user
- `GET/POST /api/users/{id}/profile` - Manage doctor profile

### Patients
- `GET /api/patients` - Get all patients
- `POST /api/patients` - Create a new patient
- `GET /api/patients/{id}` - Get a specific patient
- `PUT /api/patients/{id}` - Update patient information
- `DELETE /api/patients/{id}` - Delete a patient

### Predictions
- `GET /api/predictions` - Get all predictions
- `POST /api/predictions` - Create a new prediction
- `GET /api/predictions/{id}` - Get a specific prediction

## Data Flow

1. Doctor logs in → `users`
2. Doctor adds patient → `patients`
3. Doctor runs prediction → `predictions`
4. Image uploaded → `prediction_images`
5. Flags generated → `clinical_flags`
6. Actions logged → `audit_logs`

## Architecture Philosophy

- **Clinical Accuracy**: Every prediction is traceable to a doctor, patient, timestamp, and input data
- **Longitudinal Tracking**: Patients can have multiple predictions over time
- **Explainable AI**: Stores SHAP values and raw model inputs
- **Security & Compliance**: Password hashing, role-based access, audit logs

## Technologies Used

- Flask - Web framework
- SQLAlchemy - ORM
- PostgreSQL - Database
- Alembic - Migration tool
- Python - Backend language

## Configuration

Update the database connection string in `config/database.py` to match your PostgreSQL setup:

```python
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://username:password@localhost:5432/stroke_prediction_db"
)
```

## Sample Usage

```python
# Create a new patient
POST /api/patients
{
    "doctor_id": "uuid-of-doctor",
    "full_name": "John Doe",
    "age": 65,
    "gender": "male",
    "marital_status": "married",
    "residence_type": "urban",
    "work_type": "private"
}

# Create a stroke risk prediction
POST /api/predictions
{
    "patient_id": "uuid-of-patient",
    "doctor_id": "uuid-of-doctor",
    "risk_probability": 0.75,
    "risk_category": "HIGH",
    "input_features": {...},
    "shap_values": {...}
}
```

## License

This project is created for educational and research purposes.