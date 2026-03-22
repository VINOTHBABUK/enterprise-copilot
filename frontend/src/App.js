import React, { useState, useEffect } from 'react';
import Login from './pages/Login';
import Chat  from './pages/Chat';
import Admin from './pages/Admin';
import { getMe } from './api/client';

function App() {
  const [token, setToken] = useState(
    localStorage.getItem('token')
  );
  const [user,  setUser]  = useState(null);

  useEffect(() => {
    if (token) {
      getMe()
        .then(res => setUser(res.data))
        .catch(() => handleLogout());
    }
  }, [token]);

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  if (user?.role === 'admin') {
    return (
      <div>
        <div style={styles.tabs}>
          <button
            style={styles.tab}
            onClick={() => setUser({
              ...user, view: 'chat'
            })}
          >
            Chat
          </button>
          <button
            style={styles.tab}
            onClick={() => setUser({
              ...user, view: 'admin'
            })}
          >
            Admin
          </button>
        </div>
        {user.view === 'admin'
          ? <Admin onLogout={handleLogout} />
          : <Chat  onLogout={handleLogout} />
        }
      </div>
    );
  }

  return <Chat onLogout={handleLogout} />;
}

const styles = {
  tabs: {
    display:    'flex',
    gap:        '8px',
    padding:    '12px 24px',
    background: '#1e293b',
  },
  tab: {
    background:   'transparent',
    border:       '1px solid #475569',
    color:        '#cbd5e1',
    borderRadius: '6px',
    padding:      '6px 16px',
    fontSize:     '13px',
    cursor:       'pointer',
  },
};

export default App;
