from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .user import Base

class FlagSeverityType:
    INFO = 'INFO'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'

class ClinicalFlag(Base):
    __tablename__ = 'clinical_flags'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey('predictions.id', ondelete='CASCADE'), nullable=False)
    flag_type = Column(String(100), nullable=False)
    severity = Column(Enum(FlagSeverityType.INFO, FlagSeverityType.WARNING, FlagSeverityType.CRITICAL, name='flag_severity_type'), nullable=False)
    
    # Relationship
    prediction = relationship("Prediction", back_populates="clinical_flags")
    
    def __repr__(self):
        return f"<ClinicalFlag(id={self.id}, prediction_id={self.prediction_id}, flag_type='{self.flag_type}', severity='{self.severity}')>"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'prediction_id': str(self.prediction_id),
            'flag_type': self.flag_type,
            'severity': self.severity
        }