import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(() => {
    // Initialize from localStorage if available
    const savedUser = localStorage.getItem('currentUser');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));

  // Set up axios interceptor for auth headers
  useEffect(() => {
    if (authToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [authToken]);

  // Persist user to localStorage whenever it changes
  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('currentUser', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('currentUser');
    }
  }, [currentUser]);

  const login = async (email, password, requestedRole = null) => {
    try {
      // Use relative path for proxy configuration
      const apiUrl = process.env.REACT_APP_API_URL;
      const url = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/auth/login` : '/api/auth/login';
      const response = await axios.post(url, {
        email,
        password,
        requested_role: requestedRole
      });

      const { access_token, user } = response.data;

      localStorage.setItem('authToken', access_token);
      setAuthToken(access_token);
      setCurrentUser(user);

      return { success: true, user };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Login failed'
      };
    }
  };

  const register = async (userData) => {
    try {
      console.log('Attempting registration with data:', userData);
      // Use relative path for proxy configuration
      const apiUrl = process.env.REACT_APP_API_URL;
      const url = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/auth/register` : '/api/auth/register';

      console.log('API URL:', url);

      // Add timeout and more detailed config
      const config = {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        },
        // Add additional debugging
        validateStatus: function (status) {
          console.log('Received status:', status);
          return status >= 200 && status < 500; // Accept all statuses for debugging
        }
      };

      console.log('Making request with config:', config);
      const response = await axios.post(url, userData, config);
      console.log('Registration response:', response.data);

      const { access_token, user } = response.data;

      localStorage.setItem('authToken', access_token);
      setAuthToken(access_token);
      setCurrentUser(user);

      return { success: true, user };
    } catch (error) {
      console.error('Registration error:', error);
      console.error('Error config:', error.config);
      console.error('Error request:', error.request);
      console.error('Error response:', error.response);

      // More detailed error handling
      let errorMessage = 'Registration failed';
      if (error.code === 'ERR_NETWORK') {
        errorMessage = 'Network connection failed - cannot reach the server';
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout - server took too long to respond';
      } else if (error.response) {
        errorMessage = error.response.data?.message || `Server error: ${error.response.status}`;
      } else if (error.request) {
        errorMessage = 'No response received from server';
      }

      return {
        success: false,
        error: errorMessage
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    setAuthToken(null);
    setCurrentUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    currentUser,
    login,
    register,
    logout,
    authToken,
    // loading state removed - authentication state managed by authToken and currentUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export { AuthProvider, useAuth };