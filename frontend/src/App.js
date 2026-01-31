import React, { useState, useEffect } from 'react';
import config from './config';

function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const [agents, setAgents] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const statusRes = await fetch(`${config.API_URL}/`);
      const statusData = await statusRes.json();
      setApiStatus(statusData);

      const agentsRes = await fetch(`${config.API_URL}/api/agents`);
      const agentsData = await agentsRes.json();
      setAgents(agentsData);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
    setLoading(false);
  };

  const executeAgentAction = async (agentName, action) => {
    try {
      const res = await fetch(`${config.API_URL}/api/agents/${agentName}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, payload: {} })
      });
      const data = await res.json();
      alert(JSON.stringify(data, null, 2));
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
      color: 'white',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '20px'
    },
    header: { textAlign: 'center', marginBottom: '30px' },
    title: {
      fontSize: '2.5rem',
      margin: 0,
      background: 'linear-gradient(90deg, #667eea, #764ba2, #f093fb)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    subtitle: { opacity: 0.7, marginTop: '10px' },
    tabs: { display: 'flex', justifyContent: 'center', gap: '10px', marginBottom: '30px' },
    tab: {
      padding: '10px 20px',
      background: 'rgba(255,255,255,0.1)',
      border: 'none',
      borderRadius: '8px',
      color: 'white',
      cursor: 'pointer'
    },
    tabActive: { background: 'linear-gradient(90deg, #667eea, #764ba2)' },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '20px',
      maxWidth: '1200px',
      margin: '0 auto'
    },
    card: {
      background: 'rgba(255,255,255,0.1)',
      borderRadius: '12px',
      padding: '20px',
      backdropFilter: 'blur(10px)'
    },
    cardTitle: { fontSize: '1.2rem', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' },
    statusDot: { width: '10px', height: '10px', borderRadius: '50%', display: 'inline-block' },
    statusRunning: { background: '#4ade80' },
    statusIdle: { background: '#fbbf24' },
    button: {
      padding: '8px 16px',
      background: 'linear-gradient(90deg, #667eea, #764ba2)',
      border: 'none',
      borderRadius: '6px',
      color: 'white',
      cursor: 'pointer',
      marginRight: '8px',
      marginTop: '8px'
    },
    code: { background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '6px', fontSize: '0.85rem' },
    list: { listStyle: 'none', padding: 0, margin: 0 },
    listItem: { padding: '8px 0', borderBottom: '1px solid rgba(255,255,255,0.1)' }
  };

  const renderDashboard = () => (
    <div style={styles.grid}>
      <div style={styles.card}>
        <div style={styles.cardTitle}>
          <span style={{...styles.statusDot, ...styles.statusRunning}}></span>
          API Status
        </div>
        {apiStatus ? (
          <div>
            <p><strong>Service:</strong> {apiStatus.service}</p>
            <p><strong>Version:</strong> {apiStatus.version}</p>
            <p><strong>Architecture:</strong> {apiStatus.architecture}</p>
          </div>
        ) : <p>Loading...</p>}
      </div>

      <div style={styles.card}>
        <div style={styles.cardTitle}>
          <span style={{...styles.statusDot, ...(agents?.orchestrator?.status === 'running' ? styles.statusRunning : styles.statusIdle)}}></span>
          Orchestrator
        </div>
        {agents?.orchestrator ? (
          <div>
            <p><strong>Status:</strong> {agents.orchestrator.status}</p>
            <p><strong>Workflows:</strong> {agents.workflows?.length || 0}</p>
            <p><strong>Agents:</strong> {Object.keys(agents.agents || {}).length}</p>
          </div>
        ) : <p>Loading...</p>}
      </div>

      <div style={styles.card}>
        <div style={styles.cardTitle}>API Endpoints</div>
        {apiStatus?.endpoints ? (
          <ul style={styles.list}>
            {Object.entries(apiStatus.endpoints).map(([name, path]) => (
              <li key={name} style={styles.listItem}>
                <strong>{name}:</strong> <code>{path}</code>
              </li>
            ))}
          </ul>
        ) : <p>Loading...</p>}
      </div>
    </div>
  );

  const renderAgents = () => (
    <div style={styles.grid}>
      {agents?.agents && Object.entries(agents.agents).map(([name, agent]) => (
        <div key={name} style={styles.card}>
          <div style={styles.cardTitle}>
            <span style={{...styles.statusDot, ...(agent.status === 'running' ? styles.statusRunning : styles.statusIdle)}}></span>
            {name.charAt(0).toUpperCase() + name.slice(1)} Agent
          </div>
          <p><strong>Status:</strong> {agent.status}</p>
          <p><strong>Description:</strong> {agent.description}</p>
          <p><strong>Handlers:</strong></p>
          <div style={styles.code}>{agent.handlers?.join(', ') || 'None'}</div>
          <div style={{ marginTop: '15px' }}>
            {agent.handlers?.slice(0, 3).map(handler => (
              <button key={handler} style={styles.button} onClick={() => executeAgentAction(name, handler)}>
                {handler}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  const renderArchitecture = () => (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={styles.card}>
        <div style={styles.cardTitle}>Agentic System Architecture</div>
        <pre style={{...styles.code, whiteSpace: 'pre', overflow: 'auto'}}>
{`┌─────────────────────────────────────────┐
│         Frontend (React/Vercel)          │
└────────────────────┬────────────────────┘
                     │ API Calls
                     ▼
┌─────────────────────────────────────────┐
│        Flask Backend (Render)            │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │      ORCHESTRATOR AGENT           │  │
│  │   Central Task Coordinator        │  │
│  └─────────────────┬─────────────────┘  │
│          ┌─────────┼─────────┐          │
│          ▼         ▼         ▼          │
│     ┌─────────┐ ┌──────┐ ┌──────────┐   │
│     │ GATEWAY │ │ DATA │ │INTEGRATION│  │
│     │  AGENT  │ │AGENT │ │  AGENT   │   │
│     └─────────┘ └──────┘ └──────────┘   │
│                    │                     │
│                    ▼                     │
│              ┌──────────┐               │
│              │ Database │               │
│              └──────────┘               │
└─────────────────────────────────────────┘`}
        </pre>
      </div>
    </div>
  );

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Agentic System</h1>
        <p style={styles.subtitle}>Multi-Agent Architecture with Flask + React</p>
      </header>

      <div style={styles.tabs}>
        {['dashboard', 'agents', 'architecture'].map(tab => (
          <button
            key={tab}
            style={{...styles.tab, ...(activeTab === tab ? styles.tabActive : {})}}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
        <button style={styles.tab} onClick={fetchData}>Refresh</button>
      </div>

      {loading ? (
        <p style={{ textAlign: 'center' }}>Loading...</p>
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'agents' && renderAgents()}
          {activeTab === 'architecture' && renderArchitecture()}
        </>
      )}

      <footer style={{ textAlign: 'center', marginTop: '40px', opacity: 0.5 }}>
        <p>Backend: {config.API_URL}</p>
      </footer>
    </div>
  );
}

export default App;
