import React, { useState } from 'react';
import { login } from '../api/client';

function Login({ onLogin }) {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login(email, password);
      const token    = response.data.token;
      localStorage.setItem('token', token);
      onLogin(token);
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Login failed'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>Enterprise Copilot</h1>
          <p style={styles.subtitle}>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@company.com"
              style={styles.input}
              required
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              style={styles.input}
              required
            />
          </div>

          {error && (
            <div style={styles.error}>{error}</div>
          )}

          <button
            type="submit"
            style={styles.button}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={styles.hint}>
          <p style={styles.hintText}>Test accounts:</p>
          <p style={styles.hintText}>admin@company.com / Admin@123</p>
          <p style={styles.hintText}>hr@company.com / Hr@123</p>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight:      '100vh',
    display:        'flex',
    alignItems:     'center',
    justifyContent: 'center',
    background:     '#f0f2f5',
  },
  card: {
    background:   '#ffffff',
    borderRadius: '12px',
    padding:      '40px',
    width:        '100%',
    maxWidth:     '400px',
    boxShadow:    '0 2px 20px rgba(0,0,0,0.08)',
  },
  header: {
    textAlign:    'center',
    marginBottom: '32px',
  },
  title: {
    fontSize:   '24px',
    fontWeight: '600',
    color:      '#1a1a1a',
    margin:     '0 0 8px',
  },
  subtitle: {
    fontSize: '14px',
    color:    '#666',
    margin:   0,
  },
  form: {
    display:       'flex',
    flexDirection: 'column',
    gap:           '16px',
  },
  field: {
    display:       'flex',
    flexDirection: 'column',
    gap:           '6px',
  },
  label: {
    fontSize:   '13px',
    fontWeight: '500',
    color:      '#333',
  },
  input: {
    padding:      '10px 12px',
    borderRadius: '8px',
    border:       '1px solid #ddd',
    fontSize:     '14px',
    color:        '#333',
  },
  error: {
    background:   '#fff0f0',
    border:       '1px solid #ffcccc',
    borderRadius: '8px',
    padding:      '10px 12px',
    fontSize:     '13px',
    color:        '#cc0000',
  },
  button: {
    background:   '#2563eb',
    color:        '#ffffff',
    border:       'none',
    borderRadius: '8px',
    padding:      '12px',
    fontSize:     '14px',
    fontWeight:   '500',
    marginTop:    '8px',
  },
  hint: {
    marginTop:    '24px',
    padding:      '12px',
    background:   '#f8f9fa',
    borderRadius: '8px',
  },
  hintText: {
    fontSize: '12px',
    color:    '#888',
    margin:   '2px 0',
  },
};

export default Login;