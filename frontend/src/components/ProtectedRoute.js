import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, allowedRoles = ['doctor', 'admin'], redirectUnauthorized = true }) => {
  const { currentUser, authToken } = useAuth();

  if (!authToken) {
    return <Navigate to="/" replace />;
  }

  if (currentUser && !allowedRoles.includes(currentUser.role)) {
    if (redirectUnauthorized) {
      // If user doesn't have required role, redirect based on their role
      if (currentUser.role === 'doctor') {
        return <Navigate to="/dashboard" replace />;
      } else if (currentUser.role === 'admin') {
        return <Navigate to="/admin/analytics" replace />;
      } else {
        return <Navigate to="/" replace />;
      }
    } else {
      // Don't render the component if user doesn't have required role
      return null;
    }
  }

  return children;
};

export default ProtectedRoute;