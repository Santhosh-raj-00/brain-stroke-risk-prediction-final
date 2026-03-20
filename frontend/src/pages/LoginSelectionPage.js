import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const LoginSelectionContainer = styled.div`
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--bg-color);
  padding: 20px;
`;

const LoginSelectionWrapper = styled.div`
  display: flex;
  gap: 40px;
  max-width: 900px;
  width: 100%;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
`;

const PortalCard = styled.div`
  background: var(--surface-color);
  border-radius: 20px;
  padding: 40px;
  width: 350px;
  text-align: center;
  box-shadow:
    10px 10px 20px var(--shadow-dark),
    -10px -10px 20px var(--shadow-light);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow:
      14px 14px 28px var(--shadow-dark),
      -14px -14px 28px var(--shadow-light);
  }
`;

const PortalIcon = styled.div`
  font-size: 48px;
  margin-bottom: 20px;
`;

const PortalTitle = styled.h2`
  color: var(--text-main);
  margin-bottom: 12px;
  font-size: 24px;
`;

const PortalDescription = styled.p`
  color: var(--text-secondary);
  margin-bottom: 30px;
  font-size: 14px;
  line-height: 1.5;
`;

const ActionButton = styled(Link)`
  display: inline-block;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border: none;
  border-radius: 16px;
  padding: 14px 28px;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  box-shadow:
    6px 6px 12px rgba(108, 99, 255, 0.4),
    -6px -6px 12px rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  margin: 10px;

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
`;

const LoginSelectionPage = () => {
  return (
    <LoginSelectionContainer>
      <LoginSelectionWrapper>
        <PortalCard>
          <PortalIcon>🩺</PortalIcon>
          <PortalTitle>Doctor Portal</PortalTitle>
          <PortalDescription>
            Access clinical tools for stroke risk prediction, patient management,
            and medical analytics.
          </PortalDescription>
          <ActionButton to="/login/doctor">Doctor Login</ActionButton>
          <ActionButton to="/register/doctor">Doctor Register</ActionButton>
        </PortalCard>

        <PortalCard>
          <PortalIcon>🛠️</PortalIcon>
          <PortalTitle>Admin Portal</PortalTitle>
          <PortalDescription>
            System administration, ML analytics, user management,
            and platform oversight.
          </PortalDescription>
          <ActionButton to="/login/admin">Admin Login</ActionButton>
          <ActionButton to="/register/admin">Admin Register</ActionButton>
        </PortalCard>
      </LoginSelectionWrapper>
    </LoginSelectionContainer>
  );
};

export default LoginSelectionPage;