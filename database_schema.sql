-- BRAIN STROKE RISK PREDICTION SYSTEM
-- Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('doctor', 'admin');
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');
CREATE TYPE risk_category_type AS ENUM ('LOW', 'MEDIUM', 'HIGH');
CREATE TYPE image_modality_type AS ENUM ('MRI', 'CT');
CREATE TYPE flag_severity_type AS ENUM ('INFO', 'WARNING', 'CRITICAL');

-- 1. USERS TABLE
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP NULL,
    
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);

-- 2. DOCTOR_PROFILES TABLE
CREATE TABLE doctor_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    license_id VARCHAR(50) UNIQUE,
    hospital_name VARCHAR(150),
    specialization VARCHAR(100),
    
    -- Ensure user_id is unique (one profile per user)
    CONSTRAINT uk_doctor_profiles_user_id UNIQUE (user_id)
);

-- 3. PATIENTS TABLE
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES users(id),
    full_name VARCHAR(100),
    age INT CHECK (age BETWEEN 0 AND 120),
    gender gender_type,
    marital_status VARCHAR(50),
    residence_type VARCHAR(50),
    work_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    

);

-- 4. PREDICTIONS TABLE
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES users(id),
    risk_probability FLOAT CHECK (risk_probability >= 0 AND risk_probability <= 1),
    risk_category risk_category_type NOT NULL,
    model_version VARCHAR(20),
    input_features JSONB,
    shap_values JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    

);

-- 5. PREDICTION_IMAGES TABLE
CREATE TABLE prediction_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    modality image_modality_type,
    is_valid BOOLEAN DEFAULT true,
    validation_score FLOAT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- 6. CLINICAL_FLAGS TABLE
CREATE TABLE clinical_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
    flag_type VARCHAR(100) NOT NULL,
    severity flag_severity_type NOT NULL
);

-- 7. AUDIT_LOGS TABLE
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    entity TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address TEXT,
    

);

-- Create indexes
CREATE INDEX idx_patients_doctor_id ON patients(doctor_id);
CREATE INDEX idx_predictions_patient_id ON predictions(patient_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);
CREATE INDEX idx_predictions_risk_category ON predictions(risk_category);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);

-- Insert sample admin user (password should be hashed in real implementation)
INSERT INTO users (full_name, email, password_hash, role) 
VALUES ('System Administrator', 'admin@strokeprediction.com', '$2b$12$example_hash_for_demo', 'admin');

-- Insert sample doctor user
INSERT INTO users (full_name, email, password_hash, role) 
VALUES ('Dr. John Smith', 'dr.smith@hospital.com', '$2b$12$example_hash_for_demo', 'doctor');

-- Add doctor profile
INSERT INTO doctor_profiles (user_id, license_id, hospital_name, specialization)
SELECT id, 'MED12345', 'City General Hospital', 'Neurology'
FROM users WHERE email = 'dr.smith@hospital.com';