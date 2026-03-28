import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import styled from 'styled-components';
import axios from 'axios';

const PredictionContainer = styled.div`
  min-height: 100vh;
  background-color: var(--bg-color);
  padding: 20px;
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  color: var(--text-main);
  font-size: 32px;
  margin-bottom: 12px;
  font-weight: 700;
`;

const Subtitle = styled.p`
  color: var(--text-secondary);
  font-size: 16px;
  max-width: 600px;
  margin: 0 auto;
`;

const FormContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 40px;
`;

const FormSection = styled.div`
  background: var(--surface-color);
  border-radius: 20px;
  padding: 30px;
  box-shadow:
    10px 10px 20px var(--shadow-dark),
    -10px -10px 20px var(--shadow-light);
`;

const SectionTitle = styled.h2`
  color: var(--text-main);
  font-size: 20px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--bg-color);
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const FormLabel = styled.label`
  display: block;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  padding-left: 4px;
`;

const FormInput = styled.input`
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 16px;
  background: var(--surface-color);
  color: var(--text-main);
  font-size: 14px;
  box-shadow:
    inset 4px 4px 8px var(--shadow-dark),
    inset -4px -4px 8px var(--shadow-light);
  outline: none;
  transition: all 0.3s ease;
  
  &:focus {
    box-shadow:
      inset 6px 6px 12px var(--shadow-dark),
      inset -6px -6px 12px var(--shadow-light);
  }
`;

const FormSelect = styled.select`
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 16px;
  background: var(--surface-color);
  color: var(--text-main);
  font-size: 14px;
  box-shadow:
    inset 4px 4px 8px var(--shadow-dark),
    inset -4px -4px 8px var(--shadow-light);
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232D3436' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1em;
  transition: all 0.3s ease;
  
  &:focus {
    box-shadow:
      inset 6px 6px 12px var(--shadow-dark),
      inset -6px -6px 12px var(--shadow-light);
  }
`;

const RadioGroup = styled.div`
  display: flex;
  gap: 20px;
  margin-top: 8px;
`;

const RadioOption = styled.label`
  display: flex;
  align-items: center;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  
  input {
    margin-right: 8px;
    accent-color: var(--primary);
  }
`;

const FileUpload = styled.div`
  border: 2px dashed var(--shadow-dark);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--surface-color);
  
  &:hover {
    border-color: var(--primary);
    box-shadow: inset 4px 4px 8px var(--shadow-dark);
  }
  
  input {
    display: none;
  }
`;

const FileUploadText = styled.p`
  color: #6B7280;
  margin: 0;
  font-size: 14px;
`;

const FilePreview = styled.div`
  margin-top: 16px;
  text-align: center;
  
  img {
    max-width: 100%;
    max-height: 200px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border: none;
  border-radius: 16px;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  box-shadow:
    6px 6px 12px rgba(108, 99, 255, 0.4),
    -6px -6px 12px rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  margin-top: 20px;
  letter-spacing: 0.5px;

  &:hover {
    background: linear-gradient(135deg, var(--primary-light), var(--primary));
    transform: translateY(-2px);
    box-shadow:
      8px 8px 16px rgba(108, 99, 255, 0.4),
      -8px -8px 16px rgba(255, 255, 255, 0.9);
  }
  
  &:active {
    transform: translateY(0);
    box-shadow:
      inset 4px 4px 8px rgba(0, 0, 0, 0.2);
  }
  
  &:disabled {
    background: var(--shadow-dark);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const ErrorMessage = styled.div`
  color: #EF4444;
  margin: 10px 0;
  font-size: 14px;
`;

const PredictionPage = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    age: '',
    gender: '',
    marital_status: '',
    residence_type: '',
    work_type: '',
    hypertension: '',
    heart_disease: '',
    avg_glucose_level: '',
    bmi: '',
    smoking_status: '',
    blood_pressure_systolic: '',
    blood_pressure_diastolic: ''
  });

  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { currentUser } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const validateForm = () => {
    const requiredFields = ['full_name', 'age', 'gender', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi'];
    for (const field of requiredFields) {
      if (!formData[field]) {
        setError(`Please fill in all required fields: ${field}`);
        return false;
      }
    }

    // Validate age
    const age = parseInt(formData.age);
    if (isNaN(age) || age < 0 || age > 120) {
      setError('Age must be a valid number between 0 and 120');
      return false;
    }

    // Validate numeric fields
    const glucose = parseFloat(formData.avg_glucose_level);
    if (isNaN(glucose) || glucose < 50 || glucose > 300) {
      setError('Average glucose level must be between 50 and 300 mg/dL');
      return false;
    }

    const bmi = parseFloat(formData.bmi);
    if (isNaN(bmi) || bmi < 10 || bmi > 60) {
      setError('BMI must be between 10 and 60');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    // Check if user is authenticated
    if (!currentUser) {
      setError('You must be logged in to create predictions. Redirecting to login...');
      setTimeout(() => {
        navigate('/login/doctor');
      }, 2000);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const formDataToSend = new FormData();

      // Add patient details
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          formDataToSend.append(key, formData[key]);
        }
      });

      // Add image if provided
      if (image) {
        formDataToSend.append('scan', image);
      }

      // Add doctor_id - with null check
      if (currentUser && currentUser.id) {
        formDataToSend.append('doctor_id', currentUser.id);
      } else {
        throw new Error('User authentication required');
      }

      // Use relative path for proxy configuration
      const apiUrl = process.env.REACT_APP_API_URL;
      const url = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/predictions` : '/api/predictions';

        const response = await axios.post(
          url,
          formDataToSend,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
          }
        );


      if (response.data.prediction_id) {
        navigate(`/result/${response.data.prediction_id}`);
      } else {
        setError('Unexpected response from server');
      }
    } catch (err) {
      console.error('Prediction error:', err);
      let errorMessage = err.response?.data?.error || err.response?.data?.message || err.message || 'Failed to create prediction';

      if (err.response?.data?.details) {
        const details = Object.values(err.response.data.details).join(', ');
        errorMessage += `: ${details}`;
      }

      if (err.response?.status === 401) {
        setError('Session expired or invalid. Please log out and sign in again.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <PredictionContainer>
      <ContentWrapper>
        <Header>
          <Title>Stroke Risk Prediction</Title>
          <Subtitle>Enter patient information for ML-powered stroke risk assessment</Subtitle>
        </Header>

        <form onSubmit={handleSubmit}>
          <FormContainer>
            <FormSection>
              <SectionTitle>Patient Details</SectionTitle>

              <FormGroup>
                <FormLabel>Full Name *</FormLabel>
                <FormInput
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  placeholder="Enter patient's full name"
                  required
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>Age *</FormLabel>
                <FormInput
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  placeholder="Enter patient's age"
                  min="0"
                  max="120"
                  required
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>Gender *</FormLabel>
                <FormSelect
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>Marital Status</FormLabel>
                <FormSelect
                  name="marital_status"
                  value={formData.marital_status}
                  onChange={handleChange}
                >
                  <option value="">Select marital status</option>
                  <option value="Yes">Married</option>
                  <option value="No">Single</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>Residence Type</FormLabel>
                <FormSelect
                  name="residence_type"
                  value={formData.residence_type}
                  onChange={handleChange}
                >
                  <option value="">Select residence type</option>
                  <option value="Urban">Urban</option>
                  <option value="Rural">Rural</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>Work Type</FormLabel>
                <FormSelect
                  name="work_type"
                  value={formData.work_type}
                  onChange={handleChange}
                >
                  <option value="">Select work type</option>
                  <option value="Private">Private</option>
                  <option value="Self-employed">Self-employed</option>
                  <option value="Govt_job">Government Job</option>
                  <option value="children">Children</option>
                  <option value="Never_worked">Never Worked</option>
                </FormSelect>
              </FormGroup>
            </FormSection>

            <FormSection>
              <SectionTitle>Medical Data Input</SectionTitle>

              <FormGroup>
                <FormLabel>Hypertension *</FormLabel>
                <RadioGroup>
                  <RadioOption>
                    <input
                      type="radio"
                      name="hypertension"
                      value="1"
                      checked={formData.hypertension === '1'}
                      onChange={handleChange}
                    />
                    Yes
                  </RadioOption>
                  <RadioOption>
                    <input
                      type="radio"
                      name="hypertension"
                      value="0"
                      checked={formData.hypertension === '0'}
                      onChange={handleChange}
                    />
                    No
                  </RadioOption>
                </RadioGroup>
              </FormGroup>

              <FormGroup>
                <FormLabel>Heart Disease *</FormLabel>
                <RadioGroup>
                  <RadioOption>
                    <input
                      type="radio"
                      name="heart_disease"
                      value="1"
                      checked={formData.heart_disease === '1'}
                      onChange={handleChange}
                    />
                    Yes
                  </RadioOption>
                  <RadioOption>
                    <input
                      type="radio"
                      name="heart_disease"
                      value="0"
                      checked={formData.heart_disease === '0'}
                      onChange={handleChange}
                    />
                    No
                  </RadioOption>
                </RadioGroup>
              </FormGroup>

              <FormGroup>
                <FormLabel>Average Glucose Level *</FormLabel>
                <FormInput
                  type="number"
                  name="avg_glucose_level"
                  value={formData.avg_glucose_level}
                  onChange={handleChange}
                  placeholder="Enter glucose level (mg/dL)"
                  step="0.01"
                  required
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>BMI (Body Mass Index) *</FormLabel>
                <FormInput
                  type="number"
                  name="bmi"
                  value={formData.bmi}
                  onChange={handleChange}
                  placeholder="Enter BMI value"
                  step="0.01"
                  required
                />
              </FormGroup>

              <FormGroup>
                <FormLabel>Smoking Status</FormLabel>
                <FormSelect
                  name="smoking_status"
                  value={formData.smoking_status}
                  onChange={handleChange}
                >
                  <option value="">Select smoking status</option>
                  <option value="smokes">Smokes</option>
                  <option value="formerly smoked">Formerly Smoked</option>
                  <option value="never smoked">Never Smoked</option>
                  <option value="Unknown">Unknown</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>Blood Pressure (Systolic/Diastolic)</FormLabel>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <FormInput
                    type="number"
                    name="blood_pressure_systolic"
                    value={formData.blood_pressure_systolic}
                    onChange={handleChange}
                    placeholder="Systolic"
                    min="70"
                    max="250"
                  />
                  <FormInput
                    type="number"
                    name="blood_pressure_diastolic"
                    value={formData.blood_pressure_diastolic}
                    onChange={handleChange}
                    placeholder="Diastolic"
                    min="40"
                    max="150"
                  />
                </div>
              </FormGroup>

              <FormGroup>
                <FormLabel>MRI / CT Scan</FormLabel>
                <FileUpload onClick={() => document.getElementById('scan-upload')?.click()}>
                  <input
                    type="file"
                    id="scan-upload"
                    accept=".jpg,.jpeg,.png,.dcm,.nii,.nii.gz"
                    onChange={handleImageChange}
                    style={{ display: 'none' }}
                  />
                  <FileUploadText>
                    {image ? image.name : 'Click to upload medical scan (JPG, PNG, DCM, NII)'}
                  </FileUploadText>
                </FileUpload>

                {imagePreview && (
                  <FilePreview>
                    <img src={imagePreview} alt="Scan Preview" />
                  </FilePreview>
                )}
              </FormGroup>
            </FormSection>
          </FormContainer>

          {error && <ErrorMessage>{error}</ErrorMessage>}

          <SubmitButton type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Predict Stroke Risk'}
          </SubmitButton>
        </form>
      </ContentWrapper>
    </PredictionContainer>
  );
};

export default PredictionPage;