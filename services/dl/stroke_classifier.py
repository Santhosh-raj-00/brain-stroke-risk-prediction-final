"""
Stroke Classifier Service using ResNet18 model
"""


class StrokeClassifier:
    def __init__(self):
        # The actual classification is handled by the image_validator
        # which now uses ResNet18 to predict stroke risk
        pass
    
    def predict(self, image_path: str):
        """
        Predict stroke from medical image using ResNet18
        
        Args:
            image_path: Path to the medical image
            
        Returns:
            Dictionary with prediction results
        """
        try:
            # Use the image_validator to get validation and stroke risk
            from services.dl.image_validator import image_validator
            validation_result = image_validator.validate_medical_image(image_path)
            
            stroke_risk = validation_result.get('stroke_risk', 0.0)
            
            # Determine prediction based on stroke risk
            # 0-20%: Normal, 21-60%: Possible Indicators, 61-100%: Stroke Detected
            if stroke_risk > 0.6:
                prediction = "Stroke Detected"
                confidence = stroke_risk
            elif stroke_risk > 0.2:
                prediction = "Possible Stroke Indicators"
                confidence = stroke_risk
            else:
                prediction = "Normal"
                confidence = 1.0 - stroke_risk
                
            return {
                'prediction': prediction,
                'confidence': confidence,
                'stroke_risk': stroke_risk,
                'modality': validation_result.get('modality', 'MRI'),
                'valid': validation_result.get('valid', False)
            }
        except Exception as e:
            return {
                'prediction': 'Error',
                'confidence': 0.0,
                'stroke_risk': 0.0,
                'modality': 'Unknown',
                'valid': False,
                'error': str(e)
            }

def get_stroke_classifier():
    """Get or create stroke classifier instance"""
    return StrokeClassifier()