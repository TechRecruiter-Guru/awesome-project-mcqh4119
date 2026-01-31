import React, { useState, useEffect } from 'react';
import config from './config';

function App() {
  const [apiMessage, setApiMessage] = useState('Loading...');

  useEffect(() => {
    fetch(`${config.API_URL}/api/hello`)
      .then(res => res.json())
      .then(data => setApiMessage(data.message))
      .catch(err => setApiMessage('Could not connect to API'));
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>
        awesome-project
      </h1>
      <p style={{ fontSize: '1.2rem', opacity: 0.9 }}>
        Full-stack app with React + Flask
      </p>
      <div style={{
        marginTop: '2rem',
        padding: '1rem 2rem',
        background: 'rgba(255,255,255,0.2)',
        borderRadius: '8px'
      }}>
        <p><strong>API Response:</strong> {apiMessage}</p>
      </div>
      <div style={{ marginTop: '2rem', fontSize: '0.9rem', opacity: 0.7 }}>
        <p>Backend: {config.API_URL}</p>
      </div>
    </div>
  );
}

export default App;
