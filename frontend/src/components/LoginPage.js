import React, { useState } from 'react';
import axios from 'axios';
import { User, Lock, School, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LoginPage = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    teacher_id: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/login`, formData);
      if (response.data.success) {
        onLogin(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem'
      }}>
        <div className="card" style={{ maxWidth: '400px', width: '100%' }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{
              width: '4rem',
              height: '4rem',
              background: 'linear-gradient(135deg, #1e40af, #fbbf24)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem',
              color: 'white'
            }}>
              <School size={24} />
            </div>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: '700',
              color: '#1e40af',
              marginBottom: '0.5rem'
            }}>
              Punjab Government Schools
            </h1>
            <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>
              Student Attendance Management System
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="teacher_id">
                <User size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                Teacher ID
              </label>
              <input
                type="text"
                id="teacher_id"
                name="teacher_id"
                className="form-input"
                value={formData.teacher_id}
                onChange={handleChange}
                placeholder="Enter your Teacher ID"
                required
                style={{ paddingLeft: '1rem' }}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">
                <Lock size={16} style={{ display: 'inline', marginRight: '0.5rem' }} />
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                className="form-input"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
                style={{ paddingLeft: '1rem' }}
              />
            </div>

            {error && (
              <div className="error" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: '100%', marginTop: '1rem' }}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          <div style={{
            marginTop: '2rem',
            padding: '1rem',
            background: '#f3f4f6',
            borderRadius: '6px',
            fontSize: '0.8rem',
            color: '#6b7280'
          }}>
            <p><strong>Demo Credentials:</strong></p>
            <p>Teacher ID: abcd@</p>
            <p>Password: 1234</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;