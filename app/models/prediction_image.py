from sqlalchemy import Column, String, Boolean, Float, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .user import Base

class ImageModalityType:
    MRI = 'MRI'
    CT = 'CT'

class PredictionImage(Base):
    __tablename__ = 'prediction_images'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey('predictions.id', ondelete='CASCADE'), nullable=False)
    image_path = Column(String, nullable=False)
    modality = Column(Enum(ImageModalityType.MRI, ImageModalityType.CT, name='image_modality_type'))
    is_valid = Column(Boolean, default=True)
    validation_score = Column(Float)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    prediction = relationship("Prediction", back_populates="images")
    
    def __repr__(self):
        return f"<PredictionImage(id={self.id}, prediction_id={self.prediction_id}, image_path='{self.image_path}')>"
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'prediction_id': str(self.prediction_id),
            'image_path': self.image_path,
            'modality': self.modality,
            'is_valid': self.is_valid,
            'validation_score': self.validation_score,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }