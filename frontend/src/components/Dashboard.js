import React from 'react';
import { Link } from 'react-router-dom';
import { ClipboardList, Camera, Users, LogOut, School } from 'lucide-react';

const Dashboard = ({ teacherInfo, onLogout }) => {
  return (
    <div className="page-container">
      <header className="page-header">
        <div className="header-content">
          <div className="header-title">
            <School size={24} />
            Punjab Government Schools - Attendance System
          </div>
          <div className="header-actions">
            <div className="teacher-info">
              Welcome, {teacherInfo?.name || 'Teacher'}
            </div>
            <button onClick={onLogout} className="logout-btn">
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="dashboard-hero fade-in">
          <h1>Student Attendance Dashboard</h1>
          <p>
            Manage student attendance efficiently with manual entry, face recognition, 
            and comprehensive reporting for Punjab Government Schools.
          </p>
        </div>

        <div className="dashboard-actions slide-up">
          <div className="action-card">
            <div className="action-icon">
              <ClipboardList size={24} />
            </div>
            <h3>Mark Manual Attendance</h3>
            <p>
              Take attendance manually with a comprehensive view of all students, 
              their photos, and attendance statistics.
            </p>
            <Link to="/manual-attendance" className="btn btn-primary">
              Start Manual Attendance
            </Link>
          </div>

          <div className="action-card">
            <div className="action-icon" style={{ background: '#fef3c7', color: '#92400e' }}>
              <Camera size={24} />
            </div>
            <h3>Face Recognition Attendance</h3>
            <p>
              Automated attendance marking using face recognition technology. 
              Ensure accurate and efficient attendance tracking.
            </p>
            <button 
              className="btn btn-secondary"
              onClick={() => alert('Face recognition is handled by your external Python script. Students will be automatically marked present when recognized by your camera system.')}
            >
              Face Recognition Info
            </button>
          </div>

          <div className="action-card">
            <div className="action-icon" style={{ background: '#dcfce7', color: '#166534' }}>
              <Users size={24} />
            </div>
            <h3>Student Status</h3>
            <p>
              View individual student attendance records, search by student ID, 
              and access detailed attendance analytics.
            </p>
            <Link to="/student-status" className="btn btn-success">
              View Student Status
            </Link>
          </div>
        </div>

        <div className="card" style={{ marginTop: '3rem' }}>
          <div className="card-header">
            <h3 className="card-title">System Information</h3>
            <p className="card-description">Important information about the attendance system</p>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
            <div>
              <h4 style={{ color: '#1e40af', marginBottom: '1rem', fontWeight: '600' }}>Face Recognition Integration</h4>
              <p style={{ color: '#6b7280', fontSize: '0.9rem', lineHeight: '1.6' }}>
                Your external Python face recognition application can mark attendance by making API calls to:
                <br />
                <code style={{ background: '#f3f4f6', padding: '0.25rem 0.5rem', borderRadius: '4px', marginTop: '0.5rem', display: 'inline-block' }}>
                  POST /api/external/mark-attendance
                </code>
              </p>
            </div>
            
            <div>
              <h4 style={{ color: '#1e40af', marginBottom: '1rem', fontWeight: '600' }}>Current Students</h4>
              <p style={{ color: '#6b7280', fontSize: '0.9rem', lineHeight: '1.6' }}>
                The system currently has 5 sample students with 30 days of attendance history. 
                All attendance data is stored in the shared database for both manual and automatic access.
              </p>
            </div>
            
            <div>
              <h4 style={{ color: '#1e40af', marginBottom: '1rem', fontWeight: '600' }}>Database Access</h4>
              <p style={{ color: '#6b7280', fontSize: '0.9rem', lineHeight: '1.6' }}>
                Both the web application and your Python face recognition script share the same MongoDB database, 
                ensuring seamless integration and real-time updates.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;