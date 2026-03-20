from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from .user import Base

class DoctorProfile(Base):
    __tablename__ = 'doctor_profiles'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    license_id = Column(String(50), unique=True)
    hospital_name = Column(String(150))
    specialization = Column(String(100))
    
    # Relationship
    user = relationship("User", back_populates="doctor_profile")
    
    def __repr__(self):
        return f"<DoctorProfile(id={self.id}, user_id={self.user_id}, license_id='{self.license_id}')>"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'license_id': self.license_id,
            'hospital_name': self.hospital_name,
            'specialization': self.specialization
        }