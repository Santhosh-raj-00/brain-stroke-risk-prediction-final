from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from extensions import db

Base = db.Model

class RiskCategoryType:
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    risk_score = Column(Float)  # Final Risk probability (0-1)
    ml_score = Column(Float)    # Baseline Clinical ML probability
    dl_result = Column(String)  # Neuroimaging result (JSON: class, confidence)
    risk_category = Column(Enum(RiskCategoryType.LOW, RiskCategoryType.MEDIUM, RiskCategoryType.HIGH, name='risk_category_type'), nullable=False)
    input_features = Column(String)  # ML inputs
    shap_values = Column(String)  # SHAP explanations
    scan_path = Column(String)  # Path to medical scan
    scan_valid = Column(Boolean, default=False)  # Whether scan is valid medical image
    model_version = Column(String(50), default='3.0.0')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="predictions")
    doctor = relationship("User", back_populates="predictions")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, patient_id={self.patient_id}, risk_score={self.risk_score})>"
    
    def to_dict(self):
        import json
        return {
            'id': str(self.id),
            'patient_id': str(self.patient_id),
            'doctor_id': str(self.doctor_id),
            'risk_score': self.risk_score,
            'risk_category': self.risk_category,
            'input_features': json.loads(self.input_features) if self.input_features else {},
            'shap_values': json.loads(self.shap_values) if self.shap_values else {},
            'scan_path': self.scan_path,
            'scan_valid': self.scan_valid,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }