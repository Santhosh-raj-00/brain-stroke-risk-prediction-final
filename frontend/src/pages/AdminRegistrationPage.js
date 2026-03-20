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

const AdminRegistrationPage = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',
    organization: '',
    admin_access_key: ''
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    
    if (!formData.admin_access_key) {
      setError('Admin access key is required');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      const result = await register({
        ...formData,
        role: 'admin'
      });
      
      if (result.success) {
        navigate('/home');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to register');
    } finally {
      setLoading(false);
    }
  };

  return (
    <RegisterContainer>
      <RegisterForm>
        <RegisterTitle>Admin Registration</RegisterTitle>
        
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
              <FormLabel>Organization</FormLabel>
              <FormInput
                type="text"
                name="organization"
                value={formData.organization}
                onChange={handleChange}
                required
                placeholder="Enter organization name"
              />
            </FormField>
          </FormRow>
          
          <FormRow>
            <FormField>
              <FormLabel>Admin Access Key</FormLabel>
              <FormInput
                type="password"
                name="admin_access_key"
                value={formData.admin_access_key}
                onChange={handleChange}
                required
                placeholder="Enter admin access key"
              />
            </FormField>
          </FormRow>
          
          {error && <ErrorMessage>{error}</ErrorMessage>}
          
          <SubmitButton type="submit" disabled={loading}>
            {loading ? 'Creating Account...' : 'Create Admin Account'}
          </SubmitButton>
        </form>
        
        <LinkContainer>
          Already have an account? <Link to="/login/admin">Sign in</Link>
        </LinkContainer>
        <LinkContainer>
          <Link to="/">Back to portal selection</Link>
        </LinkContainer>
      </RegisterForm>
    </RegisterContainer>
  );
};

export default AdminRegistrationPage;