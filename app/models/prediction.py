from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .user import Base

class RiskCategoryType:
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    risk_probability = Column(Float)  # Will add check constraint in migration
    risk_category = Column(Enum(RiskCategoryType.LOW, RiskCategoryType.MEDIUM, RiskCategoryType.HIGH, name='risk_category_type'), nullable=False)
    model_version = Column(String(20))
    input_features = Column(JSONB)
    shap_values = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="predictions")
    doctor = relationship("User", back_populates="predictions")
    images = relationship("PredictionImage", back_populates="prediction", cascade="all, delete-orphan")
    clinical_flags = relationship("ClinicalFlag", back_populates="prediction", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, patient_id={self.patient_id}, risk_probability={self.risk_probability})>"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'patient_id': str(self.patient_id),
            'doctor_id': str(self.doctor_id),
            'risk_probability': self.risk_probability,
            'risk_category': self.risk_category,
            'model_version': self.model_version,
            'input_features': self.input_features,
            'shap_values': self.shap_values,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }