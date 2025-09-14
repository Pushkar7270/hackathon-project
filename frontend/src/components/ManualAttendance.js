import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Calendar, Save, CheckCircle, XCircle, School, User, LogOut } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ManualAttendance = ({ teacherInfo, onLogout }) => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const getAttendanceStatus = (percentage) => {
    if (percentage >= 90) return 'status-excellent';
    if (percentage >= 75) return 'status-good';
    return 'status-needs-attention';
  };

  const getStudentImage = (imagePath, studentId) => {
    // Placeholder images for demo
    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
    const color = colors[parseInt(studentId.slice(-1)) % colors.length];
    
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(imagePath?.split('/').pop()?.split('.')[0] || 'Student')}&background=${color.slice(1)}&color=fff&size=50&rounded=true`;
  };

  useEffect(() => {
    fetchAttendanceData();
  }, [selectedDate]);

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/attendance/${selectedDate}`);
      setStudents(response.data);
    } catch (err) {
      setError('Failed to load attendance data');
    } finally {
      setLoading(false);
    }
  };

  const handleAttendanceChange = (studentId, isPresent) => {
    setStudents(students.map(student => 
      student.student_id === studentId 
        ? { ...student, daily_attendance: isPresent }
        : student
    ));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    setError('');

    try {
      const attendanceRecords = students.map(student => ({
        student_id: student.student_id,
        date: selectedDate,
        status: student.daily_attendance ? 'present' : 'absent'
      }));

      await axios.post(`${API}/attendance`, { attendance_records: attendanceRecords });
      setMessage('Attendance saved successfully!');
      
      // Refresh data to get updated percentages
      setTimeout(() => {
        fetchAttendanceData();
        setMessage('');
      }, 2000);
    } catch (err) {
      setError('Failed to save attendance. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <header className="page-header">
          <div className="header-content">
            <div className="header-title">
              <School size={24} />
              Manual Attendance
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
        <main className="main-content">
          <div className="loading">Loading attendance data...</div>
        </main>
      </div>
    );
  }

  return (
    <div className="page-container">
      <header className="page-header">
        <div className="header-content">
          <div className="header-title">
            <School size={24} />
            Manual Attendance
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
            <h2 className="card-title">Mark Student Attendance</h2>
            <p className="card-description">
              Select date and mark attendance for each student. The system shows monthly and overall attendance percentages.
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="search-section">
              <div className="search-group">
                <label className="form-label" htmlFor="date">
                  <Calendar size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                  Select Date
                </label>
                <input
                  type="date"
                  id="date"
                  className="form-input"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  max={new Date().toISOString().split('T')[0]}
                />
              </div>
            </div>

            {message && (
              <div className="success" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle size={16} />
                {message}
              </div>
            )}

            {error && (
              <div className="error" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <XCircle size={16} />
                {error}
              </div>
            )}

            <div style={{ overflowX: 'auto' }}>
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Student Photo</th>
                    <th>Student Name</th>
                    <th>Student ID</th>
                    <th>Present Today</th>
                    <th>Monthly %</th>
                    <th>Overall %</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr key={student.student_id}>
                      <td>
                        <img
                          src={getStudentImage(student.image_path, student.student_id)}
                          alt={student.name}
                          className="student-photo"
                        />
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <User size={16} style={{ color: '#6b7280' }} />
                          <strong>{student.name}</strong>
                        </div>
                      </td>
                      <td>
                        <code style={{ 
                          background: '#f3f4f6', 
                          padding: '0.25rem 0.5rem', 
                          borderRadius: '4px',
                          fontSize: '0.8rem'
                        }}>
                          {student.student_id}
                        </code>
                      </td>
                      <td>
                        <input
                          type="checkbox"
                          className="checkbox-input"
                          checked={student.daily_attendance}
                          onChange={(e) => handleAttendanceChange(student.student_id, e.target.checked)}
                        />
                      </td>
                      <td>
                        <span className={`status-badge ${getAttendanceStatus(student.monthly_percentage)}`}>
                          {student.monthly_percentage}%
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge ${getAttendanceStatus(student.overall_percentage)}`}>
                          {student.overall_percentage}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ color: '#6b7280', fontSize: '0.9rem' }}>
                <strong>Attendance Date:</strong> {new Date(selectedDate).toLocaleDateString('en-IN', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </div>
              <button
                type="submit"
                className="btn btn-success"
                disabled={saving}
              >
                <Save size={16} />
                {saving ? 'Saving...' : 'Save Attendance'}
              </button>
            </div>
          </form>
        </div>

        <div className="card" style={{ marginTop: '2rem' }}>
          <div className="card-header">
            <h3 className="card-title">Attendance Color Guide</h3>
          </div>
          <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="status-badge status-excellent">90%+</span>
              <span style={{ fontSize: '0.9rem', color: '#6b7280' }}>Excellent Attendance</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="status-badge status-good">75-89%</span>
              <span style={{ fontSize: '0.9rem', color: '#6b7280' }}>Good Attendance</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span className="status-badge status-needs-attention">Below 75%</span>
              <span style={{ fontSize: '0.9rem', color: '#6b7280' }}>Needs Attention</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ManualAttendance;