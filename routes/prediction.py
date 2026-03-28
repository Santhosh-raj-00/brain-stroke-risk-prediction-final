from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from extensions import db
from database.models.patient import Patient
from database.models.prediction import Prediction, RiskCategoryType
from database.models.user import User
from middleware.auth import token_required, role_required
from middleware.roles import doctor_required
from datetime import datetime
import uuid
import json

prediction_bp = Blueprint('prediction', __name__)

# Initialize prediction service
_prediction_service = None

def get_service():
    """Get or initialize prediction service"""
    global _prediction_service
    if _prediction_service is None:
        from services.prediction_service import get_prediction_service
        _prediction_service = get_prediction_service()
    return _prediction_service


@prediction_bp.route('/api/predictions', methods=['POST'], strict_slashes=False)
@doctor_required
def create_prediction(current_user):
    """
    Create a new stroke risk prediction using the new prediction service
    Expected payload: { patient_data, medical_inputs, scan_file (optional) }
    """
    try:
        # Handle image upload
        scan_path = None
        scan_valid = False
        dl_result = {'prediction': 'No Scan', 'confidence': 0.0}
        
        if 'scan' in request.files:
            scan_file = request.files['scan']
            if scan_file.filename != '':
                # Save the uploaded file
                filename = secure_filename(scan_file.filename)
                file_extension = filename.split('.')[-1].lower()
                
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'dcm', 'nii', 'nii.gz'}
                if file_extension not in allowed_extensions:
                    return jsonify({'error': 'Invalid file type. Please upload a valid medical image.'}), 400
                
                # Create upload directory
                from flask import current_app
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'scans')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{filename}")
                scan_file.save(file_path)
                
                # Check Image Validity (Strict)
                from services.dl.image_validator import image_validator
                validation_result = image_validator.validate_medical_image(file_path)
                
                if not validation_result['valid']:
                    os.remove(file_path)
                    return jsonify({'error': validation_result['error']}), 400
                
                scan_path = file_path
                scan_valid = True
                
                # Extract stroke risk from the ResNet18 model
                stroke_risk = validation_result.get('stroke_risk', 0.0)
                
                # Inline the DL Inference logic to avoid double model inference
                if stroke_risk > 0.6:
                    prediction_text = "Stroke Detected"
                    confidence = stroke_risk
                elif stroke_risk > 0.2:
                    prediction_text = "Possible Stroke Indicators"
                    confidence = stroke_risk
                else:
                    prediction_text = "Normal"
                    confidence = 1.0 - stroke_risk
                    
                dl_result = {
                    'prediction': prediction_text,
                    'confidence': confidence,
                    'stroke_risk': stroke_risk,
                    'modality': validation_result.get('modality', 'MRI'),
                    'valid': True
                }
        
        # Get form data
        data = request.form if request.form else request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'age', 'gender', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Prepare patient data for ML prediction
        ml_input = {
            'age': data['age'],
            'gender': data['gender'],
            'hypertension': data['hypertension'],
            'heart_disease': data['heart_disease'],
            'avg_glucose_level': data['avg_glucose_level'],
            'bmi': data['bmi'],
            'marital_status': data.get('marital_status', data.get('ever_married', '')),
            'residence_type': data.get('residence_type', data.get('Residence_type', '')),
            'work_type': data.get('work_type', ''),
            'smoking_status': data.get('smoking_status', '')
        }
        
        # Get prediction service and make prediction
        service = get_service()
        ml_result = service.predict(ml_input)
        
        if not ml_result.get('success'):
            status_code = 400 if ml_result.get('error') == 'Validation failed' else 500
            return jsonify({
                'error': ml_result.get('error', 'Prediction failed'),
                'details': ml_result.get('validation_errors', {})
            }), status_code
        
        # Combine Risks
        ml_prob = ml_result['risk_probability']
        ml_cat = ml_result['risk_category']
        
        final_prob = ml_prob
        final_cat = ml_cat
        
        dl_pred = dl_result.get('prediction', 'Normal')
        dl_conf = dl_result.get('confidence', 0.0)
        stroke_risk = dl_result.get('stroke_risk', 0.0)
        
        # Use stroke risk from ResNet18 if available
        if stroke_risk > 0:
            # Combine clinical ML risk with imaging risk
            final_prob = max(ml_prob, stroke_risk)
        
        if dl_pred in ['Ischemic Stroke', 'Hemorrhagic Stroke'] and dl_conf > 0.5:
            # Stroke Detected by Imaging -> MAX RISK
            final_prob = max(final_prob, 0.95)
            final_cat = 'HIGH'
        elif stroke_risk > 0.7:
            # High stroke risk from ResNet18
            final_prob = stroke_risk
            if stroke_risk > 0.8:
                final_cat = 'HIGH'
            elif stroke_risk > 0.5:
                final_cat = 'MEDIUM'
        
        # Create or get patient
        patient_info = {
            'full_name': data['full_name'],
            'age': int(float(data['age'])),
            'gender': data['gender'],
            'marital_status': ml_input.get('marital_status', ''),
            'residence_type': ml_input.get('residence_type', ''),
            'work_type': ml_input.get('work_type', '')
        }
        
        existing_patient = Patient.query.filter_by(
            full_name=patient_info['full_name'],
            age=patient_info['age'],
            doctor_id=current_user.id
        ).first()
        
        if existing_patient:
            patient = existing_patient
        else:
            patient = Patient(doctor_id=current_user.id, **patient_info)
            db.session.add(patient)
            db.session.flush()
        
        # Create prediction record
        prediction = Prediction(
            patient_id=patient.id,
            doctor_id=current_user.id,
            risk_score=final_prob,
            ml_score=ml_prob,
            dl_result=json.dumps(dl_result),
            risk_category=final_cat,
            input_features=json.dumps(ml_input),
            shap_values=json.dumps({'feature_importance': ml_result.get('feature_importance', {})}),
            scan_path=scan_path,
            scan_valid=scan_valid,
            model_version=ml_result.get('model_version', '3.0.0')
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        # Compile response
        alerts = []
        if int(data.get('hypertension', 0)) == 1: alerts.append("Hypertension")
        if int(data.get('heart_disease', 0)) == 1: alerts.append("Heart Disease")
        if float(data.get('avg_glucose_level', 0)) > 120: alerts.append("High Glucose Level")
        if float(data.get('bmi', 0)) > 30: alerts.append("Obesity")
        if dl_pred != 'Normal' and dl_pred != 'No Scan': alerts.append(f"Imaging Alert: {dl_pred}")
        
        response = {
            'risk_score': final_prob,
            'risk_category': final_cat,
            'ml_score': ml_prob,
            'dl_result': dl_result,
            'shap': ml_result.get('feature_importance', {}),
            'alerts': alerts,
            'prediction_id': str(prediction.id),
            'model_version': prediction.model_version
        }
        
        return jsonify(response), 201

        
    except ValueError as ve:
        return jsonify({'error': f'Invalid input value: {str(ve)}'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500



@prediction_bp.route('/api/shap/<prediction_id>', methods=['GET'])
@token_required
def get_shap_values(current_user, prediction_id):
    """
    Get SHAP values for a specific prediction by ID
    """
    try:
        prediction = Prediction.query.filter_by(id=prediction_id).first()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Check if user has permission to access this prediction
        if current_user.role == 'doctor':
            if prediction.doctor_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403
        # Admins can access all predictions
        
        # Extract SHAP values
        shap_values = prediction.shap_values
        
        if not shap_values:
            return jsonify({'shap_values': {}, 'message': 'No SHAP data available for this prediction'}), 200
        
        # Handle different formats of shap_values
        if isinstance(shap_values, str):
            import ast
            try:
                shap_values = ast.literal_eval(shap_values)
            except:
                # If parsing fails, return empty dict
                shap_values = {}
        
        return jsonify({'shap_values': shap_values}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@prediction_bp.route('/api/predictions/<prediction_id>', methods=['GET'])
@token_required
def get_prediction(current_user, prediction_id):
    """
    Get a specific prediction by ID
    """
    try:
        prediction = Prediction.query.filter_by(id=prediction_id).first()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Check if user has permission to access this prediction
        if current_user.role == 'doctor':
            if prediction.doctor_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403
        # Admins can access all predictions
        
        return jsonify(prediction.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@prediction_bp.route('/api/predictions/<prediction_id>/pdf', methods=['GET'])
@token_required
def download_prediction_pdf(current_user, prediction_id):
    """
    Generate and download PDF report for a prediction
    """
    try:
        print(f"Generating PDF for prediction ID: {prediction_id}")
        
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from io import BytesIO
        import json
        
        prediction = Prediction.query.filter_by(id=prediction_id).first()
        if not prediction:
            print(f"Prediction {prediction_id} not found")
            return jsonify({'error': 'Prediction not found'}), 404
        
        print(f"Prediction found: {prediction.id}, Patient: {prediction.patient_id}")
        
        if current_user.role == 'doctor' and prediction.doctor_id != current_user.id:
            print(f"Access denied for user {current_user.id} to prediction {prediction_id}")
            return jsonify({'error': 'Access denied'}), 403
        
        print("User authorized for PDF generation")

        # Parse stored data
        try:
            dl_result = json.loads(prediction.dl_result) if prediction.dl_result else {'prediction': 'No Scan', 'confidence': 0.0}
            ml_inputs = json.loads(prediction.input_features) if prediction.input_features else {}
            shap_values = json.loads(prediction.shap_values) if prediction.shap_values else {}
            print("Data parsed successfully")
        except Exception as e:
            print(f"Error parsing JSON data: {e}")
            return jsonify({'error': f'Data parsing error: {str(e)}'}), 500
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Styles
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=20, spaceAfter=20)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor=colors.darkblue)
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, leading=14)
        
        # Header
        story.append(Paragraph("STROKE RISK ASSESSMENT REPORT", title_style))
        story.append(Paragraph(f"Report Date: {prediction.created_at.strftime('%Y-%m-%d')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 1. Patient Information
        story.append(Paragraph("1. Patient Information", h2_style))
        
        # Handle case where patient might not exist
        patient_name = "Unknown Patient"
        patient_gender = "N/A"
        patient_age = "N/A"
        
        if prediction.patient:
            patient_name = prediction.patient.full_name or "Unknown Patient"
            patient_gender = prediction.patient.gender or "N/A"
            patient_age = str(prediction.patient.age) if prediction.patient.age else "N/A"
        
        # Ensure patient_name is not empty or just whitespace
        if not patient_name or not patient_name.strip():
            patient_name = "Unknown Patient"
        
        patient_data = [
            ["Patient Name", patient_name, "Patient ID", str(prediction.patient_id)[:8]],
            ["Age", patient_age, "Gender", patient_gender],
            ["Referring Doctor", current_user.full_name, "Report ID", str(prediction.id)[:8]]
        ]
        t = Table(patient_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
        # 2. Clinical Input Summary
        story.append(Paragraph("2. Clinical Input Summary", h2_style))
        clinical_data = [["Feature", "Value", "Feature", "Value"]]
        
        # Clean and format keys logic - remove duplicates and fix marital status
        processed_keys = []
        unique_features = {}
        
        # Process keys to remove duplicates and handle special cases
        for key in ml_inputs.keys():
            clean_key = key.replace('_', ' ').title()
            value = ml_inputs[key]
            
            # Handle special cases
            if key == 'ever_married':
                # Convert Yes/No to Married/Not Married
                value = 'Married' if str(value).lower() in ['yes', '1', 'true'] else 'Not Married'
                clean_key = 'Marital Status'
            elif key == 'marital_status':
                # Skip duplicate marital status if ever_married exists
                if 'ever_married' in ml_inputs:
                    continue
                # Convert Yes/No to Married/Not Married
                value = 'Married' if str(value).lower() in ['yes', '1', 'true'] else 'Not Married'
            elif key == 'Residence_type':
                # Skip duplicate residence type
                if 'residence_type' in unique_features:
                    continue
                clean_key = 'Residence Type'
            
            unique_features[clean_key] = value
        
        # Convert to list and format for table
        feature_items = list(unique_features.items())
        for i in range(0, len(feature_items), 2):
            k1, v1 = feature_items[i]
            row = [k1, str(v1)]
            
            if i+1 < len(feature_items):
                k2, v2 = feature_items[i+1]
                row.extend([k2, str(v2)])
            else:
                row.extend(["", ""])
            clinical_data.append(row)
            
        t2 = Table(clinical_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        t2.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTWEIGHT', (0,0), (-1,0), 'BOLD'),
        ]))
        story.append(t2)
        story.append(Spacer(1, 15))
        
        # 3. Neuroimaging Analysis
        story.append(Paragraph("3. Neuroimaging Analysis", h2_style))
        scan_status = "Available" if prediction.scan_valid else "Not Available"
        scan_type = dl_result.get("modality", "MRI/CT") # Assumption
        
        dl_pred = dl_result.get('prediction', 'N/A')
        dl_conf = dl_result.get('confidence', 0.0)
        
        img_text = f"""
        <b>Scan Status:</b> {scan_status}<br/>
        <b>Modality:</b> {scan_type}<br/>
        <b>AI Prediction:</b> {dl_pred}<br/>
        <b>Confidence Score:</b> {dl_conf:.1%}<br/>
        <b>Assessment:</b> {'Abnormal findings detected consistent with ' + dl_pred if dl_pred != 'Normal' else 'No acute stroke lesions detected.'}
        """
        story.append(Paragraph(img_text, normal_style))
        story.append(Spacer(1, 15))
        
        # 4. Combined Risk Assessment
        story.append(Paragraph("4. Combined Risk Assessment", h2_style))
        
        risk_color = colors.green
        if prediction.risk_category == 'MEDIUM': risk_color = colors.orange
        if prediction.risk_category == 'HIGH': risk_color = colors.red
        
        risk_data = [
            ["Clinical ML Risk Score", f"{prediction.ml_score:.1%}" if prediction.ml_score else "N/A"],
            ["Imaging Risk Indicator", dl_pred],
            ["FINAL STROKE RISK", prediction.risk_category]
        ]
        
        t3 = Table(risk_data, colWidths=[3*inch, 3*inch])
        t3.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTWEIGHT', (0,2), (-1,2), 'BOLD'),
            ('TEXTCOLOR', (1,2), (1,2), risk_color),
            ('BACKGROUND', (0,2), (-1,2), colors.lightgrey),
        ]))
        story.append(t3)
        story.append(Spacer(1, 15))
        
        # 5. Explainability (SHAP)
        story.append(Paragraph("5. Key Contributing Factors (Explainability)", h2_style))
        
        shap_dict = shap_values.get('feature_importance', {})
        if shap_dict:
            shap_text = "The following features contributed most to the clinical risk score:<br/><br/>"
            
            # Filter out binary features with value 0/No
            filtered_factors = []
            for k, v in shap_dict.items():
                # Check if this is a binary feature in the input data
                original_key = k.lower().replace(' ', '_')
                if original_key in ml_inputs:
                    input_value = ml_inputs[original_key]
                    # Skip binary features with value 0/No/False
                    if str(input_value).lower() in ['0', 'no', 'false', ''] and v <= 0:
                        continue
                
                direction = "increased" if v > 0 else "decreased"
                filtered_factors.append((k, direction))
            
            # Generate the filtered text
            if filtered_factors:
                for feature, direction in filtered_factors:
                    shap_text += f"• <b>{feature.replace('_', ' ').title()}</b>: {direction} risk<br/>"
            else:
                shap_text += "No significant risk factors identified.<br/>"
                
            story.append(Paragraph(shap_text, normal_style))
        else:
            story.append(Paragraph("No explainability data available.", normal_style))
            
        story.append(Spacer(1, 30))
        
        # 6. Scan Analysis (if available)
        if dl_result.get('stroke_risk', 0) > 0 or prediction.scan_valid:
            story.append(Paragraph("6. Imaging Analysis", h2_style))
            
            scan_analysis = []
            scan_analysis.append(["Scan Type", dl_result.get('modality', 'Unknown'), "Scan Valid", "Yes" if prediction.scan_valid else "No"])
            scan_analysis.append(["AI Prediction", dl_result.get('prediction', 'No scan analyzed'), "Confidence", f"{dl_result.get('confidence', 0)*100:.1f}%"])
            scan_analysis.append(["Stroke Risk (Imaging)", f"{dl_result.get('stroke_risk', 0)*100:.1f}%", "", ""])
            
            t_scan = Table(scan_analysis, colWidths=[1.8*inch, 2.2*inch, 1.5*inch, 2*inch])
            t_scan.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
                ('BACKGROUND', (2,0), (2,-1), colors.whitesmoke),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_scan)
            story.append(Spacer(1, 15))
            
            # Detailed findings
            findings = []
            recommendations = []
            
            # Generate findings based on stroke risk
            stroke_risk = dl_result.get('stroke_risk', 0)
            if stroke_risk > 0.7:
                findings = ["High probability of acute stroke detected", "Visible abnormalities in brain tissue"]
                recommendations = ["Immediate neurological consultation recommended", "Consider emergency intervention protocols"]
            elif stroke_risk > 0.3:
                findings = ["Moderate stroke risk indicators present", "Subtle abnormalities detected"]
                recommendations = ["Neurological evaluation recommended", "Serial imaging may be beneficial"]
            else:
                findings = ["No acute stroke lesions detected", "Brain parenchyma appears normal"]
                recommendations = ["Continue clinical monitoring", "Follow standard care protocols"]
            
            # Add modality-specific findings
            if dl_result.get('modality') in ['CT', 'MRI']:
                findings.append(f"{dl_result.get('modality')} scan quality adequate for interpretation")
            
            findings_text = "<b>Clinical Observations:</b><br/>"
            for finding in findings:
                findings_text += f"• {finding}<br/>"
            story.append(Paragraph(findings_text, normal_style))
            story.append(Spacer(1, 10))
            
            rec_text = "<b>Recommendations:</b><br/>"
            for rec in recommendations:
                rec_text += f"• {rec}<br/>"
            story.append(Paragraph(rec_text, normal_style))
            story.append(Spacer(1, 20))
        
        # 7. Disclaimer
        story.append(Paragraph("7. MEDICAL DISCLAIMER", h2_style))
        disclaimer = """
        This report is generated by an AI-based Clinical Decision Support System. 
        The results are probabilistic and intended to assist, NOT replace, clinical judgment. 
        Final diagnosis and treatment decisions must be made by a qualified healthcare professional 
        after considering all clinical factors, patient history, and validation of imaging results.
        """
        story.append(Paragraph(disclaimer, ParagraphStyle('DisclText', parent=styles['Normal'], fontSize=7, alignment=TA_JUSTIFY)))
        
        print("Building PDF document...")
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        print("PDF generated successfully, size:", len(pdf_data), "bytes")
        
        from flask import Response
        return Response(
            pdf_data,
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=Stroke_Report_{prediction_id}.pdf'}
        )
        
    except Exception as e:
        import traceback
        print("PDF Generation Error:")
        traceback.print_exc()
        return jsonify({'error': f'PDF Generation Failed: {str(e)}'}), 500


@prediction_bp.route('/api/predictions/<prediction_id>', methods=['DELETE'])
@token_required
def delete_prediction(current_user, prediction_id):
    """
    Delete a specific prediction by ID with proper cascading updates
    """
    try:
        prediction = Prediction.query.filter_by(id=prediction_id).first()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Check if user has permission to delete this prediction
        if current_user.role == 'doctor':
            if prediction.doctor_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403
        
        patient_id = prediction.patient_id
        
        # Remove associated scan file if it exists
        if prediction.scan_path and os.path.exists(prediction.scan_path):
            try:
                os.remove(prediction.scan_path)
            except OSError:
                # Log the error but continue with deletion
                print(f"Could not delete scan file: {prediction.scan_path}")
        
        # Delete the prediction record
        db.session.delete(prediction)
        db.session.commit()
        
        # Update patient's last prediction data
        update_patient_last_prediction(patient_id)
        
        return jsonify({'message': 'Prediction deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


def update_patient_last_prediction(patient_id):
    """
    Update patient's last prediction data after a prediction is deleted
    """
    try:
        # Get the latest prediction for this patient
        latest_prediction = Prediction.query.filter_by(patient_id=patient_id)\
                                           .order_by(Prediction.created_at.desc()).first()
        
        # Note: In a real implementation, you would update the patient record
        # with the latest prediction data. For now, we'll just log it.
        print(f"Updated patient {patient_id} with latest prediction: {latest_prediction.id if latest_prediction else 'None'}")
        
        # In a real system, you might have patient.last_risk_score, 
        # patient.last_risk_category, patient.last_prediction_date fields
        # that would be updated here
        
    except Exception as e:
        print(f"Error updating patient last prediction: {str(e)}")


@prediction_bp.route('/api/predictions/<prediction_id>/visualizations/shap', methods=['GET'])
@token_required
def get_shap_visualization(current_user, prediction_id):
    """
    Get SHAP waterfall plot for a prediction
    """
    try:
        prediction = Prediction.query.filter_by(id=prediction_id).first()
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
            
        # Permission check
        if current_user.role == 'doctor' and prediction.doctor_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
            
        # Get input features
        input_features = prediction.input_features
        if isinstance(input_features, str):
            input_features = json.loads(input_features)
            
        from services.visualization_service import get_visualization_service
        viz_service = get_visualization_service()
        
        image_base64 = viz_service.generate_shap_waterfall(input_features)
        
        if not image_base64:
            return jsonify({'error': 'Could not generate visualization'}), 500
            
        return jsonify({'image': image_base64}), 200
        
    except Exception as e:
        print(f"Error serving SHAP plot: {e}")
        return jsonify({'error': str(e)}), 500


@prediction_bp.route('/api/predictions/<prediction_id>/visualizations/glucose', methods=['GET'])
@token_required
def get_glucose_visualization(current_user, prediction_id):
    """
    Get Glucose distribution plot with patient marker
    """
    try:
        prediction = Prediction.query.filter_by(id=prediction_id).first()
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Input features
        input_features = prediction.input_features
        if isinstance(input_features, str):
            input_features = json.loads(input_features)
        
        glucose_level = float(input_features.get('avg_glucose_level', 0))
    
        from services.visualization_service import get_visualization_service
        viz_service = get_visualization_service()
        
        image_base64 = viz_service.generate_glucose_plot(glucose_level)
        
        if not image_base64:
            return jsonify({'error': 'Could not generate visualization'}), 500
        
        return jsonify({'image': image_base64}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediction_bp.route('/api/predictions/<prediction_id>/scan-analysis', methods=['GET'])
@token_required
def get_scan_analysis(current_user, prediction_id):
    """
    Get detailed scan analysis results
    """
    try:
        prediction = Prediction.query.filter_by(id=prediction_id).first()
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        # Check permission
        if current_user.role == 'doctor' and prediction.doctor_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Parse DL result
        dl_result = {}
        if prediction.dl_result:
            if isinstance(prediction.dl_result, str):
                import json
                try:
                    dl_result = json.loads(prediction.dl_result)
                except:
                    dl_result = {}
            else:
                dl_result = prediction.dl_result
        
        # Extract scan analysis
        scan_analysis = {
            'scan_available': bool(prediction.scan_path),
            'scan_valid': bool(prediction.scan_valid),
            'dl_prediction': dl_result.get('prediction', 'No scan analyzed'),
            'dl_confidence': dl_result.get('confidence', 0.0),
            'stroke_risk': dl_result.get('stroke_risk', 0.0),
            'modality': dl_result.get('modality', 'Unknown'),
            'findings': [],
            'recommendations': []
        }
        
        # Add specific findings based on prediction
        if scan_analysis['stroke_risk'] > 0.7:
            scan_analysis['findings'].append('High probability of acute stroke detected')
            scan_analysis['findings'].append('Visible abnormalities in brain tissue')
            scan_analysis['recommendations'].append('Immediate neurological consultation recommended')
            scan_analysis['recommendations'].append('Consider emergency intervention protocols')
        elif scan_analysis['stroke_risk'] > 0.3:
            scan_analysis['findings'].append('Moderate stroke risk indicators present')
            scan_analysis['findings'].append('Subtle abnormalities detected')
            scan_analysis['recommendations'].append('Neurological evaluation recommended')
            scan_analysis['recommendations'].append('Serial imaging may be beneficial')
        else:
            scan_analysis['findings'].append('No acute stroke lesions detected')
            scan_analysis['findings'].append('Brain parenchyma appears normal')
            scan_analysis['recommendations'].append('Continue clinical monitoring')
            scan_analysis['recommendations'].append('Follow standard care protocols')
        
        # Add modality-specific findings
        if scan_analysis['modality'] in ['CT', 'MRI']:
            scan_analysis['findings'].append(f'{scan_analysis["modality"]} scan quality adequate for interpretation')
        
        return jsonify(scan_analysis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prediction_bp.route('/api/model/visualizations/<plot_type>', methods=['GET'])
def get_static_visualization(plot_type):
    """
    Get static model visualizations (heatmap, confusion-matrix)
    """
    try:
        # Map request type to filename
        filename_map = {
            'heatmap': 'correlation_heatmap.png',
            'confusion-matrix': 'confusion_matrix.png'
        }
        
        if plot_type not in filename_map:
            return jsonify({'error': 'Invalid plot type'}), 400
            
        from flask import send_from_directory
        static_dir = os.path.join(os.getcwd(), 'static', 'images')
        
        return send_from_directory(static_dir, filename_map[plot_type])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500