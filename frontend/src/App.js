import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import ManualAttendance from './components/ManualAttendance';
import StudentStatus from './components/StudentStatus';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [teacherInfo, setTeacherInfo] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const savedAuth = localStorage.getItem('teacherAuth');
    if (savedAuth) {
      const authData = JSON.parse(savedAuth);
      setIsAuthenticated(true);
      setTeacherInfo(authData);
    }
  }, []);

  const handleLogin = (teacherData) => {
    setIsAuthenticated(true);
    setTeacherInfo(teacherData);
    localStorage.setItem('teacherAuth', JSON.stringify(teacherData));
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setTeacherInfo(null);
    localStorage.removeItem('teacherAuth');
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/login" 
            element={
              !isAuthenticated ? 
              <LoginPage onLogin={handleLogin} /> : 
              <Navigate to="/dashboard" replace />
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? 
              <Dashboard teacherInfo={teacherInfo} onLogout={handleLogout} /> : 
              <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/manual-attendance" 
            element={
              isAuthenticated ? 
              <ManualAttendance teacherInfo={teacherInfo} onLogout={handleLogout} /> : 
              <Navigate to="/login" replace />
            } 
          />
          <Route 
            path="/student-status" 
            element={
              isAuthenticated ? 
              <StudentStatus teacherInfo={teacherInfo} onLogout={handleLogout} /> : 
              <Navigate to="/login" replace />
            } 
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;