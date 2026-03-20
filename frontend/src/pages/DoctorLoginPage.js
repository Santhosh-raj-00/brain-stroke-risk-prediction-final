import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import styled from 'styled-components';

const LoginContainer = styled.div`
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-color);
  padding: 20px;
`;

const LoginForm = styled.div`
  background: var(--surface-color);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  text-align: center;
  box-shadow:
    10px 10px 20px var(--shadow-dark),
    -10px -10px 20px var(--shadow-light);
`;

const LoginTitle = styled.h2`
  color: var(--text-main);
  margin-bottom: 30px;
  font-size: 24px;
`;

const FormField = styled.div`
  margin-bottom: 20px;
  text-align: left;
`;

const FormLabel = styled.label`
  display: block;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
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

const SubmitButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border: none;
  border-radius: 16px;
  padding: 14px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  box-shadow:
    6px 6px 12px rgba(108, 99, 255, 0.4),
    -6px -6px 12px rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  margin-top: 10px;

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

const DoctorLoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError('');

      const result = await login(email, password, 'doctor');

      if (result.success) {
        navigate('/home');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to log in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LoginContainer>
      <LoginForm>
        <LoginTitle>Doctor Login</LoginTitle>

        <form onSubmit={handleSubmit}>
          <FormField>
            <FormLabel>Email</FormLabel>
            <FormInput
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Enter your email"
            />
          </FormField>

          <FormField>
            <FormLabel>Password</FormLabel>
            <FormInput
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password"
            />
          </FormField>

          {error && <ErrorMessage>{error}</ErrorMessage>}

          <SubmitButton type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </SubmitButton>
        </form>

        <LinkContainer>
          Don't have an account? <Link to="/register/doctor">Sign up</Link>
        </LinkContainer>
        <LinkContainer>
          <Link to="/">Back to portal selection</Link>
        </LinkContainer>
      </LoginForm>
    </LoginContainer>
  );
};

export default DoctorLoginPage;