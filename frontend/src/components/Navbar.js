import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import styled from 'styled-components';

const Nav = styled.nav`
  background: #F6F8FB;
  padding: 16px 20px;
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.05),
    inset 0 -1px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled(Link)`
  font-size: 20px;
  font-weight: 600;
  color: #1F2937;
  text-decoration: none;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 30px;
  align-items: center;
`;

const NavLink = styled(Link)`
  color: ${props => props.active ? '#6C7CFF' : '#6B7280'};
  text-decoration: none;
  font-weight: ${props => props.active ? '600' : '400'};
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  
  &:hover {
    background-color: rgba(108, 124, 255, 0.1);
    color: #6C7CFF;
  }
`;

const UserMenu = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const UserName = styled.span`
  color: #6B7280;
  font-size: 14px;
`;

const LogoutButton = styled.button`
  background: #EF4444;
  color: white;
  border: none;
  border-radius: 16px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  box-shadow:
    4px 4px 10px rgba(239, 68, 68, 0.2),
    -4px -4px 10px rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;

  &:hover {
    background: #DC2626;
    box-shadow:
      2px 2px 6px rgba(239, 68, 68, 0.2),
      -2px -2px 6px rgba(255, 255, 255, 0.6);
  }
`;

const Navbar = () => {
  const { currentUser, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  // List of paths where the authenticated parts of the navbar should not be shown
  const authRoutes = ['/', '/login/doctor', '/login/admin', '/register/doctor', '/register/admin'];
  const isAuthRoute = authRoutes.includes(location.pathname);

  const navLinks = currentUser?.role === 'admin'
    ? [
      { path: '/dashboard', label: 'Dashboard' },
      { path: '/patients', label: 'Patients' },
      { path: '/history', label: 'History' },
      { path: '/admin/analytics', label: 'Analytics' }
    ]
    : [
      { path: '/dashboard', label: 'Dashboard' },
      { path: '/patients', label: 'Patients' },
      { path: '/history', label: 'History' },
      { path: '/prediction', label: 'Predict' }
    ];

  const handleLogout = () => {
    logout();
  };

  return (
    <Nav>
      <Logo to="/home">Stroke Predictor</Logo>

      {currentUser && !isAuthRoute && (
        <NavLinks>
          {navLinks.map(link => (
            <NavLink
              key={link.path}
              to={link.path}
              active={isActive(link.path) ? 'true' : undefined}
            >
              {link.label}
            </NavLink>
          ))}
        </NavLinks>
      )}

      {currentUser && !isAuthRoute && (
        <UserMenu>
          <UserName>Hello, {currentUser.full_name}</UserName>
          <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
        </UserMenu>
      )}
    </Nav>
  );
};

export default Navbar;