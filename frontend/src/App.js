import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import GlobalStyles from './styles/GlobalStyles';
import LoginSelectionPage from './pages/LoginSelectionPage';
import DoctorLoginPage from './pages/DoctorLoginPage';
import AdminLoginPage from './pages/AdminLoginPage';
import DoctorRegistrationPage from './pages/DoctorRegistrationPage';
import AdminRegistrationPage from './pages/AdminRegistrationPage';
import HomePage from './pages/HomePage';
import PredictionPage from './pages/PredictionPage';
import ResultPage from './pages/ResultPage';
import PatientsPage from './pages/PatientsPage';
import HistoryPage from './pages/HistoryPage';
import DashboardPage from './pages/DashboardPage';
import AdminAnalyticsPage from './pages/AdminAnalyticsPage';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <GlobalStyles />
        <Router>
          <div className="App">
            <Navbar />
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LoginSelectionPage />} />
              <Route path="/login/doctor" element={<DoctorLoginPage />} />
              <Route path="/login/admin" element={<AdminLoginPage />} />
              <Route path="/register/doctor" element={<DoctorRegistrationPage />} />
              <Route path="/register/admin" element={<AdminRegistrationPage />} />
              
              {/* Protected Routes */}
              <Route 
                path="/home" 
                element={
                  <ProtectedRoute>
                    <HomePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/prediction" 
                element={
                  <ProtectedRoute>
                    <PredictionPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/result/:predictionId" 
                element={
                  <ProtectedRoute>
                    <ResultPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/patients" 
                element={
                  <ProtectedRoute>
                    <PatientsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/history" 
                element={
                  <ProtectedRoute>
                    <HistoryPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/admin/analytics" 
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <AdminAnalyticsPage />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;