from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from extensions import db

Base = db.Model

class GenderType:
    MALE = 'Male'
    FEMALE = 'Female'

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    full_name = Column(String(100))
    age = Column(Integer)  # Will add check constraint in migration
    gender = Column(Enum(GenderType.MALE, GenderType.FEMALE, name='gender_type'))
    marital_status = Column(String(50))
    residence_type = Column(String(50))  # Urban/Rural
    work_type = Column(String(50))  # Private/Self-employed/Never_worked/Govt_job/children
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = relationship("User", back_populates="patients")
    predictions = relationship("Prediction", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, full_name='{self.full_name}', age={self.age})>"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'doctor_id': str(self.doctor_id),
            'full_name': self.full_name,
            'age': self.age,
            'gender': self.gender,
            'marital_status': self.marital_status,
            'residence_type': self.residence_type,
            'work_type': self.work_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }