import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import styled from 'styled-components';

const RegisterContainer = styled.div`
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #EEF1F5;
  padding: 20px;
`;

const RegisterForm = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 500px;
  text-align: center;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const RegisterTitle = styled.h2`
  color: #1F2937;
  margin-bottom: 30px;
  font-size: 24px;
`;

const FormRow = styled.div`
  display: flex;
  gap: 15px;
  
  & > div {
    flex: 1;
  }
  
  margin-bottom: 20px;
`;

const FormField = styled.div`
  margin-bottom: 20px;
  text-align: left;
`;

const FormLabel = styled.label`
  display: block;
  color: #6B7280;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
`;

const FormInput = styled.input`
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 16px;
  background: #F6F8FB;
  color: #1F2937;
  font-size: 14px;
  box-shadow:
    inset 4px 4px 8px #D1D9E6,
    inset -4px -4px 8px #FFFFFF;
  outline: none;
  
  &:focus {
    box-shadow:
      inset 6px 6px 12px #D1D9E6,
      inset -6px -6px 12px #FFFFFF;
  }
`;

const FormSelect = styled.select`
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 16px;
  background: #F6F8FB;
  color: #1F2937;
  font-size: 14px;
  box-shadow:
    inset 4px 4px 8px #D1D9E6,
    inset -4px -4px 8px #FFFFFF;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231F2937' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1em;
  
  &:focus {
    box-shadow:
      inset 6px 6px 12px #D1D9E6,
      inset -6px -6px 12px #FFFFFF;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #6C7CFF;
  color: white;
  border: none;
  border-radius: 16px;
  padding: 14px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  box-shadow:
    4px 4px 10px rgba(108, 124, 255, 0.2),
    -4px -4px 10px rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
  margin-top: 10px;

  &:hover {
    background: #5a6ae6;
    box-shadow:
      2px 2px 6px rgba(108, 124, 255, 0.2),
      -2px -2px 6px rgba(255, 255, 255, 0.6);
  }
  
  &:disabled {
    background: #D1D5DB;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: #EF4444;
  margin: 10px 0;
  font-size: 14px;
`;

const LinkContainer = styled.div`
  margin-top: 20px;
  color: #6B7280;
  font-size: 14px;
  
  a {
    color: #6C7CFF;
    text-decoration: none;
    margin-left: 5px;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const DoctorRegistrationPage = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',
    license_id: '',
    hospital_name: '',
    specialty: ''
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  console.log('Auth context register function:', typeof register);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    console.log('handleSubmit called with event:', e);
    e.preventDefault();
    console.log('Form prevented default');
    
    // Validation
    if (formData.password !== formData.confirm_password) {
      console.log('Password validation failed');
      setError('Passwords do not match');
      return;
    }
    
    console.log('Form data validation passed');
    console.log('Current form data:', formData);
    
    try {
      setLoading(true);
      setError('');
      
      console.log('Form data being sent:', {
        email: formData.email,
        full_name: formData.full_name,
        role: 'doctor'
      });
      
      const result = await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: 'doctor'
      });
      
      console.log('Registration result:', result);
      
      if (result.success) {
        console.log('Registration successful, navigating to home');
        navigate('/home');
      } else {
        console.log('Registration failed with error:', result.error);
        setError(result.error);
      }
    } catch (err) {
      console.error('Registration caught error:', err);
      setError('Failed to register');
    } finally {
      console.log('Setting loading to false');
      setLoading(false);
    }
  };

  return (
    <RegisterContainer>
      <RegisterForm>
        <RegisterTitle>Doctor Registration</RegisterTitle>
        
        <form onSubmit={handleSubmit}>
          <FormRow>
            <FormField>
              <FormLabel>Full Name</FormLabel>
              <FormInput
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
              />
            </FormField>
          </FormRow>
          
          <FormRow>
            <FormField>
              <FormLabel>Email</FormLabel>
              <FormInput
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="Enter your email"
              />
            </FormField>
          </FormRow>
          
          <FormRow>
            <FormField>
              <FormLabel>Password</FormLabel>
              <FormInput
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
              />
            </FormField>
            <FormField>
              <FormLabel>Confirm Password</FormLabel>
              <FormInput
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
              />
            </FormField>
          </FormRow>
          
          <FormRow>
            <FormField>
              <FormLabel>Medical License ID</FormLabel>
              <FormInput
                type="text"
                name="license_id"
                value={formData.license_id}
                onChange={handleChange}
                required
                placeholder="Enter your license ID"
              />
            </FormField>
          </FormRow>
          
          <FormRow>
            <FormField>
              <FormLabel>Hospital / Clinic Name</FormLabel>
              <FormInput
                type="text"
                name="hospital_name"
                value={formData.hospital_name}
                onChange={handleChange}
                required
                placeholder="Enter hospital/clinic name"
              />
            </FormField>
          </FormRow>
          
          <FormRow>
            <FormField>
              <FormLabel>Specialty</FormLabel>
              <FormSelect
                name="specialty"
                value={formData.specialty}
                onChange={handleChange}
                required
              >
                <option value="">Select specialty</option>
                <option value="neurology">Neurology</option>
                <option value="cardiology">Cardiology</option>
                <option value="internal_medicine">Internal Medicine</option>
                <option value="emergency_medicine">Emergency Medicine</option>
                <option value="radiology">Radiology</option>
                <option value="other">Other</option>
              </FormSelect>
            </FormField>
          </FormRow>
          
          {error && <ErrorMessage>{error}</ErrorMessage>}
          
          <SubmitButton type="submit" disabled={loading}>
            {loading ? 'Creating Account...' : 'Create Doctor Account'}
          </SubmitButton>
        </form>
        
        <LinkContainer>
          Already have an account? <Link to="/login/doctor">Sign in</Link>
        </LinkContainer>
        <LinkContainer>
          <Link to="/">Back to portal selection</Link>
        </LinkContainer>
      </RegisterForm>
    </RegisterContainer>
  );
};

export default DoctorRegistrationPage;