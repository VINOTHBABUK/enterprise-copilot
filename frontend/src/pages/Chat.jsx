import React, { useState, useEffect, useRef } from 'react';
import { sendMessage, getMe } from '../api/client';
import ReactMarkdown from 'react-markdown';

function Chat({ onLogout }) {
  const [messages, setMessages] = useState([
    {
      role:    'assistant',
      content: 'Hello! I am your Enterprise Copilot. Ask me anything about company knowledge, meetings, or workflows.'
    }
  ]);
  const [input,   setInput]   = useState('');
  const [loading, setLoading] = useState(false);
  const [user,    setUser]    = useState(null);
  const bottomRef             = useRef(null);

  useEffect(() => {
    getMe().then(res => setUser(res.data))
           .catch(() => onLogout());
  }, [onLogout]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMsg = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [
      ...prev,
      { role: 'user', content: userMessage }
    ]);
    setLoading(true);

    try {
      const response = await sendMessage(userMessage);
      const data     = response.data;

      setMessages(prev => [
        ...prev,
        {
          role:     'assistant',
          content:  data.answer,
          tool:     data.tool_used,
          latency:  data.latency_ms
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role:    'assistant',
          content: 'Sorry, something went wrong. Please try again.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>

      {/* Sidebar */}
      <div style={styles.sidebar}>
        <div style={styles.sidebarHeader}>
          <h2 style={styles.sidebarTitle}>Enterprise Copilot</h2>
        </div>

        {user && (
          <div style={styles.userInfo}>
            <div style={styles.avatar}>
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <p style={styles.userName}>{user.name}</p>
              <p style={styles.userRole}>{user.role}</p>
            </div>
          </div>
        )}

        <div style={styles.examples}>
          <p style={styles.examplesTitle}>Try asking:</p>
          {[
            'What is incident management?',
            'What is a knowledge base?',
            'Give me all risks from meetings',
            'Summarise all meetings',
          ].map((ex, i) => (
            <button
              key={i}
              style={styles.exampleBtn}
              onClick={() => setInput(ex)}
            >
              {ex}
            </button>
          ))}
        </div>

        <button
          onClick={onLogout}
          style={styles.logoutBtn}
        >
          Logout
        </button>
      </div>

      {/* Chat area */}
      <div style={styles.chatArea}>

        <div style={styles.messages}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                ...styles.message,
                ...(msg.role === 'user'
                  ? styles.userMessage
                  : styles.assistantMessage)
              }}
            >
              {msg.role === 'assistant' && (
                <div style={styles.messageMeta}>
                  {msg.tool && (
                    <span style={styles.toolBadge}>
                      {msg.tool.replace('_', ' ')}
                    </span>
                  )}
                  {msg.latency && (
                    <span style={styles.latency}>
                      {msg.latency}ms
                    </span>
                  )}
                </div>
              )}
              <div style={styles.messageContent}>
                {msg.role === 'assistant' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={styles.assistantMessage}>
              <div style={styles.typing}>
                <span>Thinking</span>
                <span style={styles.dots}>...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={sendMsg} style={styles.inputArea}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about company knowledge..."
            style={styles.input}
            disabled={loading}
          />
          <button
            type="submit"
            style={styles.sendBtn}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </form>

      </div>
    </div>
  );
}

const styles = {
  container: {
    display:    'flex',
    height:     '100vh',
    background: '#f0f2f5',
  },
  sidebar: {
    width:          '260px',
    background:     '#1e293b',
    display:        'flex',
    flexDirection:  'column',
    padding:        '20px',
    flexShrink:     0,
  },
  sidebarHeader: {
    marginBottom: '24px',
  },
  sidebarTitle: {
    color:      '#f8fafc',
    fontSize:   '16px',
    fontWeight: '600',
  },
  userInfo: {
    display:      'flex',
    alignItems:   'center',
    gap:          '10px',
    padding:      '12px',
    background:   '#334155',
    borderRadius: '8px',
    marginBottom: '24px',
  },
  avatar: {
    width:          '36px',
    height:         '36px',
    borderRadius:   '50%',
    background:     '#2563eb',
    color:          '#fff',
    display:        'flex',
    alignItems:     'center',
    justifyContent: 'center',
    fontWeight:     '600',
    fontSize:       '14px',
    flexShrink:     0,
  },
  userName: {
    color:     '#f8fafc',
    fontSize:  '13px',
    fontWeight:'500',
    margin:    0,
  },
  userRole: {
    color:    '#94a3b8',
    fontSize: '11px',
    margin:   0,
  },
  examples: {
    flex: 1,
  },
  examplesTitle: {
    color:        '#94a3b8',
    fontSize:     '11px',
    fontWeight:   '500',
    textTransform:'uppercase',
    letterSpacing:'0.05em',
    marginBottom: '8px',
  },
  exampleBtn: {
    display:      'block',
    width:        '100%',
    textAlign:    'left',
    background:   'transparent',
    border:       'none',
    color:        '#cbd5e1',
    fontSize:     '12px',
    padding:      '8px 10px',
    borderRadius: '6px',
    marginBottom: '4px',
    cursor:       'pointer',
    lineHeight:   '1.4',
  },
  logoutBtn: {
    background:   'transparent',
    border:       '1px solid #475569',
    color:        '#94a3b8',
    borderRadius: '8px',
    padding:      '10px',
    fontSize:     '13px',
    width:        '100%',
    marginTop:    '16px',
  },
  chatArea: {
    flex:          1,
    display:       'flex',
    flexDirection: 'column',
    overflow:      'hidden',
  },
  messages: {
    flex:       1,
    overflowY:  'auto',
    padding:    '24px',
    display:    'flex',
    flexDirection: 'column',
    gap:        '16px',
  },
  message: {
    maxWidth:     '75%',
    borderRadius: '12px',
    padding:      '12px 16px',
    fontSize:     '14px',
    lineHeight:   '1.6',
  },
  userMessage: {
    background:  '#2563eb',
    color:       '#ffffff',
    alignSelf:   'flex-end',
    borderBottomRightRadius: '4px',
  },
  assistantMessage: {
    background:  '#ffffff',
    color:       '#1a1a1a',
    alignSelf:   'flex-start',
    borderBottomLeftRadius: '4px',
    boxShadow:   '0 1px 4px rgba(0,0,0,0.06)',
    maxWidth:    '80%',
  },
  messageMeta: {
    display:      'flex',
    gap:          '8px',
    marginBottom: '6px',
    alignItems:   'center',
  },
  toolBadge: {
    background:   '#eff6ff',
    color:        '#2563eb',
    fontSize:     '11px',
    padding:      '2px 8px',
    borderRadius: '20px',
    fontWeight:   '500',
    textTransform:'capitalize',
  },
  latency: {
    fontSize: '11px',
    color:    '#94a3b8',
  },
  messageContent: {
    fontSize:   '14px',
    lineHeight: '1.6',
  },
  typing: {
    color:    '#94a3b8',
    fontSize: '13px',
    padding:  '4px 0',
  },
  dots: {
    animation: 'pulse 1.5s infinite',
  },
  inputArea: {
    display:    'flex',
    gap:        '12px',
    padding:    '16px 24px',
    background: '#ffffff',
    borderTop:  '1px solid #e2e8f0',
  },
  input: {
    flex:         1,
    padding:      '12px 16px',
    borderRadius: '8px',
    border:       '1px solid #e2e8f0',
    fontSize:     '14px',
    color:        '#333',
  },
  sendBtn: {
    background:   '#2563eb',
    color:        '#ffffff',
    border:       'none',
    borderRadius: '8px',
    padding:      '12px 24px',
    fontSize:     '14px',
    fontWeight:   '500',
  },
};

export default Chat;