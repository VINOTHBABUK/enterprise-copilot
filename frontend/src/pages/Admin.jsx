import React, { useState, useEffect } from 'react';
import { getStats } from '../api/client';

function Admin({ onLogout }) {
  const [stats,   setStats]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');

  useEffect(() => {
    getStats()
      .then(res => {
        setStats(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(
          err.response?.status === 403
            ? 'Admin access required'
            : 'Failed to load stats'
        );
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <div style={styles.center}>
      <p>Loading dashboard...</p>
    </div>
  );

  if (error) return (
    <div style={styles.center}>
      <p style={{ color: '#cc0000' }}>{error}</p>
    </div>
  );

  return (
    <div style={styles.container}>

      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Admin Dashboard</h1>
        <button onClick={onLogout} style={styles.logoutBtn}>
          Logout
        </button>
      </div>

      {/* Metric cards */}
      <div style={styles.metricsRow}>
        <MetricCard
          label="Total Queries"
          value={stats.total_queries}
        />
        <MetricCard
          label="Total Cost"
          value={`$${stats.total_cost.toFixed(5)}`}
        />
        <MetricCard
          label="Avg Latency"
          value={`${stats.avg_latency}ms`}
        />
        <MetricCard
          label="Avg Quality"
          value={`${(stats.avg_score * 100).toFixed(0)}%`}
        />
      </div>

      {/* Two column layout */}
      <div style={styles.row}>

        {/* By Model */}
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Usage by Model</h3>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Model</th>
                <th style={styles.th}>Queries</th>
                <th style={styles.th}>Cost</th>
                <th style={styles.th}>Latency</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(stats.by_model).map(
                ([model, data]) => (
                  <tr key={model}>
                    <td style={styles.td}>{model}</td>
                    <td style={styles.td}>{data.count}</td>
                    <td style={styles.td}>
                      ${data.cost.toFixed(5)}
                    </td>
                    <td style={styles.td}>
                      {data.avg_latency.toFixed(0)}ms
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>

        {/* By Tool */}
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Usage by Tool</h3>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Tool</th>
                <th style={styles.th}>Queries</th>
                <th style={styles.th}>Cost</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(stats.by_tool).map(
                ([tool, data]) => (
                  <tr key={tool}>
                    <td style={styles.td}>
                      {tool.replace(/_/g, ' ')}
                    </td>
                    <td style={styles.td}>{data.count}</td>
                    <td style={styles.td}>
                      ${data.cost.toFixed(5)}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>

      </div>

      {/* By User */}
      <div style={styles.card}>
        <h3 style={styles.cardTitle}>Usage by User</h3>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>User</th>
              <th style={styles.th}>Queries</th>
              <th style={styles.th}>Cost</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(stats.by_user).map(
              ([user, data]) => (
                <tr key={user}>
                  <td style={styles.td}>{user}</td>
                  <td style={styles.td}>{data.count}</td>
                  <td style={styles.td}>
                    ${data.cost.toFixed(5)}
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div style={styles.metricCard}>
      <p style={styles.metricValue}>{value}</p>
      <p style={styles.metricLabel}>{label}</p>
    </div>
  );
}

const styles = {
  container: {
    padding:   '32px',
    maxWidth:  '1200px',
    margin:    '0 auto',
  },
  center: {
    display:        'flex',
    alignItems:     'center',
    justifyContent: 'center',
    height:         '100vh',
    fontSize:       '16px',
    color:          '#666',
  },
  header: {
    display:        'flex',
    justifyContent: 'space-between',
    alignItems:     'center',
    marginBottom:   '32px',
  },
  title: {
    fontSize:   '24px',
    fontWeight: '600',
    color:      '#1a1a1a',
  },
  logoutBtn: {
    background:   'transparent',
    border:       '1px solid #ddd',
    borderRadius: '8px',
    padding:      '8px 16px',
    fontSize:     '13px',
    color:        '#666',
  },
  metricsRow: {
    display:             'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap:                 '16px',
    marginBottom:        '24px',
  },
  metricCard: {
    background:   '#ffffff',
    borderRadius: '12px',
    padding:      '20px',
    boxShadow:    '0 1px 4px rgba(0,0,0,0.06)',
    textAlign:    'center',
  },
  metricValue: {
    fontSize:   '28px',
    fontWeight: '600',
    color:      '#1a1a1a',
    margin:     '0 0 4px',
  },
  metricLabel: {
    fontSize: '13px',
    color:    '#666',
    margin:   0,
  },
  row: {
    display:             'grid',
    gridTemplateColumns: '1fr 1fr',
    gap:                 '16px',
    marginBottom:        '16px',
  },
  card: {
    background:   '#ffffff',
    borderRadius: '12px',
    padding:      '20px',
    boxShadow:    '0 1px 4px rgba(0,0,0,0.06)',
    marginBottom: '16px',
  },
  cardTitle: {
    fontSize:     '15px',
    fontWeight:   '600',
    color:        '#1a1a1a',
    marginBottom: '16px',
  },
  table: {
    width:           '100%',
    borderCollapse:  'collapse',
    fontSize:        '13px',
  },
  th: {
    textAlign:     'left',
    padding:       '8px 12px',
    background:    '#f8f9fa',
    color:         '#666',
    fontWeight:    '500',
    borderBottom:  '1px solid #e2e8f0',
  },
  td: {
    padding:      '10px 12px',
    borderBottom: '1px solid #f0f0f0',
    color:        '#333',
  },
};

export default Admin;