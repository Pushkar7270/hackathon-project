import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Search, Calendar, User, TrendingUp, AlertCircle, School, LogOut } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StudentStatus = ({ teacherInfo, onLogout }) => {
  const [searchId, setSearchId] = useState('');
  const [studentData, setStudentData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const getStudentImage = (imagePath, studentId) => {
    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
    const color = colors[parseInt(studentId?.slice(-1)) % colors.length] || '#3b82f6';
    
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(imagePath?.split('/').pop()?.split('.')[0] || 'Student')}&background=${color.slice(1)}&color=fff&size=120&rounded=true`;
  };

  const getAttendanceStatus = (percentage) => {
    if (percentage >= 90) return { class: 'status-excellent', label: 'Excellent' };
    if (percentage >= 75) return { class: 'status-good', label: 'Good' };
    return { class: 'status-needs-attention', label: 'Needs Attention' };
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchId.trim()) return;

    setLoading(true);
    setError('');
    setStudentData(null);

    try {
      const response = await axios.get(`${API}/student-status/${searchId.trim()}`);
      setStudentData(response.data);
    } catch (err) {
      setError(err.response?.status === 404 ? 
        'Student not found. Please check the Student ID.' : 
        'Failed to fetch student data. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const generateCalendar = () => {
    if (!studentData) return null;

    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const absentDates = studentData.absent_dates.map(date => {
      const d = new Date(date);
      return d.getDate();
    });

    const calendar = [];
    const monthNames = ["January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"];

    // Calendar header
    calendar.push(
      <div key="header" className="calendar-header">
        <h4>{monthNames[currentMonth]} {currentYear}</h4>
        <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>
          <span style={{ color: '#991b1b' }}>● Absent</span>
          <span style={{ marginLeft: '1rem', color: '#166534' }}>● Present</span>
        </div>
      </div>
    );

    // Days of week headers
    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const headerRow = dayHeaders.map(day => (
      <div key={day} className="calendar-day header">{day}</div>
    ));

    // Empty cells for days before month starts
    const emptyCells = [];
    for (let i = 0; i < startingDayOfWeek; i++) {
      emptyCells.push(<div key={`empty-${i}`} className="calendar-day"></div>);
    }

    // Days of the month
    const monthDays = [];
    for (let day = 1; day <= daysInMonth; day++) {
      const isAbsent = absentDates.includes(day);
      const isToday = day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear();
      
      let dayClass = 'calendar-day';
      if (isAbsent) dayClass += ' absent';
      else if (day <= today.getDate()) dayClass += ' present';
      if (isToday) dayClass += ' today';

      monthDays.push(
        <div key={day} className={dayClass}>
          {day}
        </div>
      );
    }

    return (
      <div className="calendar-container">
        {calendar}
        <div className="calendar-grid">
          {headerRow}
          {emptyCells}
          {monthDays}
        </div>
      </div>
    );
  };

  return (
    <div className="page-container">
      <header className="page-header">
        <div className="header-content">
          <div className="header-title">
            <School size={24} />
            Student Status
          </div>
          <div className="header-actions">
            <div className="teacher-info">
              {teacherInfo?.name || 'Teacher'}
            </div>
            <button onClick={onLogout} className="logout-btn">
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="main-content fade-in">
        <div style={{ marginBottom: '2rem' }}>
          <Link to="/dashboard" className="btn btn-outline" style={{ marginBottom: '1rem' }}>
            <ArrowLeft size={16} />
            Back to Dashboard
          </Link>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Search Student Status</h2>
            <p className="card-description">
              Enter a student ID to view detailed attendance information and calendar view.
            </p>
          </div>

          <form onSubmit={handleSearch}>
            <div className="search-section">
              <div className="search-group">
                <label className="form-label" htmlFor="studentId">
                  <User size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                  Student ID
                </label>
                <input
                  type="text"
                  id="studentId"
                  className="form-input"
                  value={searchId}
                  onChange={(e) => setSearchId(e.target.value)}
                  placeholder="Enter Student ID (e.g., STU001)"
                  required
                />
              </div>
              <div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  <Search size={16} />
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>
          </form>

          {error && (
            <div className="error" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={16} />
              {error}
            </div>
          )}
        </div>

        {studentData && (
          <div className="slide-up" style={{ marginTop: '2rem' }}>
            {/* Student Information Card */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Student Information</h3>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '2rem', alignItems: 'start' }}>
                <div style={{ textAlign: 'center' }}>
                  <img
                    src={getStudentImage(studentData.image_path, studentData.student_id)}
                    alt={studentData.name}
                    style={{
                      width: '120px',
                      height: '120px',
                      borderRadius: '50%',
                      border: '4px solid #dbeafe',
                      marginBottom: '1rem'
                    }}
                  />
                  <div>
                    <h4 style={{ color: '#1e40af', marginBottom: '0.5rem' }}>{studentData.name}</h4>
                    <code style={{ 
                      background: '#f3f4f6', 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '4px',
                      fontSize: '0.8rem'
                    }}>
                      {studentData.student_id}
                    </code>
                  </div>
                </div>

                <div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                    <div style={{ textAlign: 'center', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px' }}>
                      <TrendingUp size={24} style={{ color: '#1e40af', marginBottom: '0.5rem' }} />
                      <div style={{ fontSize: '2rem', fontWeight: '700', color: '#1e40af', marginBottom: '0.25rem' }}>
                        {studentData.overall_percentage}%
                      </div>
                      <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Overall Attendance</div>
                      <div style={{ marginTop: '0.5rem' }}>
                        <span className={`status-badge ${getAttendanceStatus(studentData.overall_percentage).class}`}>
                          {getAttendanceStatus(studentData.overall_percentage).label}
                        </span>
                      </div>
                    </div>

                    <div style={{ textAlign: 'center', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px' }}>
                      <Calendar size={24} style={{ color: '#10b981', marginBottom: '0.5rem' }} />
                      <div style={{ fontSize: '2rem', fontWeight: '700', color: '#10b981', marginBottom: '0.25rem' }}>
                        {studentData.monthly_stats.present}
                      </div>
                      <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Days Present</div>
                      <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: '0.25rem' }}>
                        out of {studentData.monthly_stats.total} days
                      </div>
                    </div>

                    <div style={{ textAlign: 'center', padding: '1.5rem', background: '#f8fafc', borderRadius: '8px' }}>
                      <AlertCircle size={24} style={{ color: '#ef4444', marginBottom: '0.5rem' }} />
                      <div style={{ fontSize: '2rem', fontWeight: '700', color: '#ef4444', marginBottom: '0.25rem' }}>
                        {studentData.monthly_stats.absent}
                      </div>
                      <div style={{ fontSize: '0.9rem', color: '#6b7280' }}>Days Absent</div>
                      <div style={{ fontSize: '0.8rem', color: '#6b7280', marginTop: '0.25rem' }}>
                        {studentData.absent_dates.length} absent days
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Calendar View */}
            <div className="card" style={{ marginTop: '2rem' }}>
              <div className="card-header">
                <h3 className="card-title">Monthly Attendance Calendar</h3>
                <p className="card-description">
                  Visual representation of attendance for the current month. Red dates indicate absences.
                </p>
              </div>
              
              {generateCalendar()}
            </div>
          </div>
        )}

        {/* Sample Student IDs for demo */}
        <div className="card" style={{ marginTop: '2rem' }}>
          <div className="card-header">
            <h3 className="card-title">Demo Student IDs</h3>
            <p className="card-description">Use these sample student IDs to test the system</p>
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            {['STU001', 'STU002', 'STU003', 'STU004', 'STU005'].map(id => (
              <button
                key={id}
                className="btn btn-outline"
                style={{ fontSize: '0.8rem', padding: '0.5rem 1rem' }}
                onClick={() => setSearchId(id)}
              >
                {id}
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default StudentStatus;