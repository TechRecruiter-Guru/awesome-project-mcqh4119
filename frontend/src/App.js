import React, { useState, useEffect } from 'react';
import config from './config';

function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const [agents, setAgents] = useState(null);
  const [robotStatus, setRobotStatus] = useState(null);
  const [sensorData, setSensorData] = useState(null);
  const [visionData, setVisionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('command');

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statusRes, agentsRes, robotRes, sensorsRes] = await Promise.all([
        fetch(`${config.API_URL}/`),
        fetch(`${config.API_URL}/api/agents`),
        fetch(`${config.API_URL}/api/robot/status`),
        fetch(`${config.API_URL}/api/sensors`)
      ]);
      setApiStatus(await statusRes.json());
      setAgents(await agentsRes.json());
      setRobotStatus(await robotRes.json());
      setSensorData(await sensorsRes.json());
    } catch (err) { console.error('Failed to fetch:', err); }
    setLoading(false);
  };

  const callEndpoint = async (endpoint, method = 'GET', body = null) => {
    try {
      const res = await fetch(`${config.API_URL}${endpoint}`, {
        method, headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : null
      });
      const data = await res.json();
      alert(JSON.stringify(data, null, 2));
      fetchData();
    } catch (err) { alert('Error: ' + err.message); }
  };

  const styles = {
    container: { minHeight: '100vh', background: '#0a0a0f', color: '#e0e0e0', fontFamily: "'Inter', system-ui, sans-serif" },
    header: { background: 'linear-gradient(90deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%)', padding: '20px 40px', borderBottom: '1px solid #2a2a3e' },
    logo: { display: 'flex', alignItems: 'center', gap: '15px' },
    logoIcon: { width: '50px', height: '50px', background: 'linear-gradient(135deg, #00f5d4, #00bbf9)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' },
    title: { fontSize: '1.8rem', fontWeight: 700, background: 'linear-gradient(90deg, #00f5d4, #00bbf9, #9b5de5)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
    subtitle: { fontSize: '0.9rem', color: '#888', marginTop: '2px' },
    nav: { display: 'flex', gap: '5px', background: '#12121a', padding: '10px 40px', borderBottom: '1px solid #2a2a3e' },
    navBtn: { padding: '12px 24px', background: 'transparent', border: 'none', color: '#888', cursor: 'pointer', borderRadius: '8px', fontSize: '0.9rem', transition: 'all 0.2s' },
    navActive: { background: 'linear-gradient(135deg, #1a1a2e, #2a2a4e)', color: '#00f5d4', borderBottom: '2px solid #00f5d4' },
    main: { padding: '30px 40px' },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' },
    card: { background: 'linear-gradient(135deg, #12121a 0%, #1a1a2e 100%)', borderRadius: '16px', padding: '24px', border: '1px solid #2a2a3e' },
    cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
    cardTitle: { fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '10px' },
    statusDot: { width: '8px', height: '8px', borderRadius: '50%' },
    running: { background: '#00f5d4', boxShadow: '0 0 10px #00f5d4' },
    idle: { background: '#fbbf24' },
    metric: { display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #2a2a3e' },
    metricLabel: { color: '#888', fontSize: '0.85rem' },
    metricValue: { fontWeight: 600, color: '#00f5d4' },
    btn: { padding: '10px 20px', background: 'linear-gradient(135deg, #00f5d4, #00bbf9)', border: 'none', borderRadius: '8px', color: '#0a0a0f', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem', margin: '4px' },
    btnSecondary: { background: 'linear-gradient(135deg, #2a2a4e, #3a3a5e)', color: '#e0e0e0' },
    btnDanger: { background: 'linear-gradient(135deg, #f87171, #dc2626)' },
    agentGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '15px' },
    agentCard: { background: '#1a1a2e', borderRadius: '12px', padding: '20px', border: '1px solid #2a2a3e' },
    tag: { display: 'inline-block', padding: '4px 12px', background: '#2a2a4e', borderRadius: '20px', fontSize: '0.75rem', margin: '2px' },
    sensorGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' },
    sensorItem: { background: '#1a1a2e', padding: '15px', borderRadius: '10px', textAlign: 'center' },
    bigNumber: { fontSize: '2rem', fontWeight: 700, color: '#00f5d4' }
  };

  const renderCommand = () => (
    <div style={styles.grid}>
      <div style={styles.card}>
        <div style={styles.cardHeader}>
          <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.running}}></span> System Status</div>
          <span style={{color: '#00f5d4', fontSize: '0.8rem'}}>OPERATIONAL</span>
        </div>
        <div style={styles.metric}><span style={styles.metricLabel}>Service</span><span style={styles.metricValue}>{apiStatus?.service || 'PhysicalAI'}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Version</span><span style={styles.metricValue}>{apiStatus?.version || '2.0.0'}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Architecture</span><span style={styles.metricValue}>{apiStatus?.architecture || 'multi-agent'}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Active Agents</span><span style={styles.metricValue}>{Object.keys(agents?.agents || {}).length}</span></div>
        <div style={{marginTop: '20px'}}>
          <button style={styles.btn} onClick={fetchData}>Refresh Status</button>
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.cardHeader}>
          <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.running}}></span> Robot Control</div>
        </div>
        <div style={styles.metric}><span style={styles.metricLabel}>Position X</span><span style={styles.metricValue}>{robotStatus?.motion?.current_position?.x?.toFixed(2) || '0.00'} m</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Position Y</span><span style={styles.metricValue}>{robotStatus?.motion?.current_position?.y?.toFixed(2) || '0.00'} m</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Position Z</span><span style={styles.metricValue}>{robotStatus?.motion?.current_position?.z?.toFixed(2) || '0.00'} m</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Trajectories</span><span style={styles.metricValue}>{robotStatus?.motion?.trajectories_planned || 0}</span></div>
        <div style={{marginTop: '20px'}}>
          <button style={styles.btn} onClick={() => callEndpoint('/api/robot/move', 'POST', {target: {x: 1, y: 1, z: 0}, speed: 0.5})}>Plan Move</button>
          <button style={{...styles.btn, ...styles.btnDanger}} onClick={() => callEndpoint('/api/mission/abort', 'POST')}>Emergency Stop</button>
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.cardHeader}>
          <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.running}}></span> Autonomy</div>
        </div>
        <div style={styles.metric}><span style={styles.metricLabel}>Level</span><span style={styles.metricValue}>L{robotStatus?.autonomy?.autonomy_level || 4}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Safety Status</span><span style={styles.metricValue}>{robotStatus?.autonomy?.safety_status || 'nominal'}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Behavior</span><span style={styles.metricValue}>{robotStatus?.autonomy?.behavior_state || 'idle'}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Missions Done</span><span style={styles.metricValue}>{robotStatus?.autonomy?.missions_completed || 0}</span></div>
        <div style={{marginTop: '20px'}}>
          <button style={styles.btn} onClick={() => callEndpoint('/api/mission', 'POST', {type: 'navigation', target: {x: 5, y: 5}})}>New Mission</button>
          <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => callEndpoint('/api/autonomy/safety')}>Safety Check</button>
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.cardHeader}>
          <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.running}}></span> Sensors</div>
        </div>
        <div style={styles.metric}><span style={styles.metricLabel}>Total Sensors</span><span style={styles.metricValue}>{robotStatus?.sensors?.total_sensors || 8}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Active</span><span style={styles.metricValue}>{robotStatus?.sensors?.active_sensors || 8}</span></div>
        <div style={styles.metric}><span style={styles.metricLabel}>Readings</span><span style={styles.metricValue}>{robotStatus?.sensors?.total_readings || 0}</span></div>
        <div style={{marginTop: '20px'}}>
          <button style={styles.btn} onClick={() => callEndpoint('/api/sensors')}>All Readings</button>
          <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => callEndpoint('/api/sensors/obstacles')}>Detect Obstacles</button>
        </div>
      </div>
    </div>
  );

  const renderAgents = () => (
    <div style={styles.agentGrid}>
      {agents?.agents && Object.entries(agents.agents).map(([name, agent]) => (
        <div key={name} style={styles.agentCard}>
          <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px'}}>
            <span style={{...styles.statusDot, ...(agent.status === 'running' ? styles.running : styles.idle)}}></span>
            <span style={{fontWeight: 600, textTransform: 'capitalize'}}>{name} Agent</span>
          </div>
          <p style={{color: '#888', fontSize: '0.85rem', marginBottom: '10px'}}>{agent.description}</p>
          <div style={{marginBottom: '15px'}}>
            {agent.handlers?.slice(0, 5).map(h => <span key={h} style={styles.tag}>{h}</span>)}
            {agent.handlers?.length > 5 && <span style={styles.tag}>+{agent.handlers.length - 5}</span>}
          </div>
          <button style={{...styles.btn, width: '100%'}} onClick={() => callEndpoint(`/api/agents/${name}/action`, 'POST', {action: 'get_stats'})}>Get Stats</button>
        </div>
      ))}
    </div>
  );

  const renderVision = () => (
    <div style={styles.grid}>
      <div style={styles.card}>
        <div style={styles.cardTitle}>Object Detection</div>
        <p style={{color: '#888', marginBottom: '20px'}}>YOLOv8-robotics model for real-time detection</p>
        <button style={styles.btn} onClick={() => callEndpoint('/api/vision/detect')}>Detect Objects</button>
        <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => callEndpoint('/api/vision/slam')}>Visual SLAM</button>
      </div>
      <div style={styles.card}>
        <div style={styles.cardTitle}>Human-Robot Interaction</div>
        <p style={{color: '#888', marginBottom: '20px'}}>Pose estimation and gesture recognition</p>
        <button style={styles.btn} onClick={() => callEndpoint('/api/vision/pose')}>Estimate Pose</button>
        <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => callEndpoint('/api/vision/gesture')}>Recognize Gesture</button>
      </div>
      <div style={styles.card}>
        <div style={styles.cardTitle}>Sensor Fusion</div>
        <p style={{color: '#888', marginBottom: '20px'}}>Extended Kalman Filter for localization</p>
        <button style={styles.btn} onClick={() => callEndpoint('/api/sensors/fusion')}>Fuse Sensors</button>
        <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => callEndpoint('/api/sensors/obstacles')}>Obstacle Detection</button>
      </div>
    </div>
  );

  const renderArchitecture = () => (
    <div style={{maxWidth: '1000px', margin: '0 auto'}}>
      <div style={styles.card}>
        <div style={styles.cardTitle}>PhysicalAI Multi-Agent Architecture</div>
        <pre style={{background: '#0a0a0f', padding: '20px', borderRadius: '12px', overflow: 'auto', fontSize: '0.8rem', color: '#00f5d4'}}>
{`
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PHYSICALAI COMMAND CENTER - VANGUARDLAB                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────────────────────────────────────────────────────────────┐    ║
║   │                     ORCHESTRATOR AGENT                               │    ║
║   │              Central Task Coordinator & Router                       │    ║
║   └───────────────────────────────┬─────────────────────────────────────┘    ║
║                                   │                                          ║
║   ┌───────────┬───────────┬───────┴───────┬───────────┬───────────┐         ║
║   │           │           │               │           │           │         ║
║   ▼           ▼           ▼               ▼           ▼           ▼         ║
║ ┌───────┐ ┌───────┐ ┌─────────┐ ┌───────────┐ ┌───────┐ ┌──────────┐       ║
║ │MOTION │ │SENSOR │ │ VISION  │ │ AUTONOMY  │ │  DATA │ │INTEGRATION│       ║
║ │ AGENT │ │ AGENT │ │  AGENT  │ │   AGENT   │ │ AGENT │ │  AGENT   │       ║
║ └───┬───┘ └───┬───┘ └────┬────┘ └─────┬─────┘ └───┬───┘ └────┬─────┘       ║
║     │         │          │            │           │          │             ║
║     ▼         ▼          ▼            ▼           ▼          ▼             ║
║ ┌───────┐ ┌───────┐ ┌─────────┐ ┌───────────┐ ┌───────┐ ┌──────────┐       ║
║ │Motion │ │LiDAR  │ │YOLOv8   │ │Mission    │ │Postgre│ │External  │       ║
║ │Control│ │IMU    │ │MoveNet  │ │Planning   │ │  SQL  │ │  APIs    │       ║
║ │  IK   │ │Camera │ │SegFormer│ │Safety     │ │       │ │Webhooks  │       ║
║ └───────┘ └───────┘ └─────────┘ └───────────┘ └───────┘ └──────────┘       ║
║                                                                             ║
╠═════════════════════════════════════════════════════════════════════════════╣
║  CAPABILITIES: Motion Planning | Sensor Fusion | Computer Vision | Autonomy ║
╚═════════════════════════════════════════════════════════════════════════════╝
`}
        </pre>
      </div>
    </div>
  );

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.logo}>
          <div style={styles.logoIcon}>AI</div>
          <div>
            <div style={styles.title}>PhysicalAI Command Center</div>
            <div style={styles.subtitle}>VanguardLab - Enterprise Robotics Platform</div>
          </div>
        </div>
      </header>

      <nav style={styles.nav}>
        {[
          {id: 'command', label: 'Command Center'},
          {id: 'agents', label: 'Agents'},
          {id: 'vision', label: 'Vision & Sensors'},
          {id: 'architecture', label: 'Architecture'}
        ].map(t => (
          <button key={t.id} style={{...styles.navBtn, ...(activeTab === t.id ? styles.navActive : {})}} onClick={() => setActiveTab(t.id)}>{t.label}</button>
        ))}
        <button style={styles.navBtn} onClick={fetchData}>Refresh</button>
      </nav>

      <main style={styles.main}>
        {loading ? <p style={{textAlign: 'center', color: '#888'}}>Initializing systems...</p> : (
          <>
            {activeTab === 'command' && renderCommand()}
            {activeTab === 'agents' && renderAgents()}
            {activeTab === 'vision' && renderVision()}
            {activeTab === 'architecture' && renderArchitecture()}
          </>
        )}
      </main>

      <footer style={{textAlign: 'center', padding: '30px', borderTop: '1px solid #2a2a3e', color: '#666'}}>
        <p>PhysicalAI Command Center v2.0 | VanguardLab | Backend: {config.API_URL}</p>
      </footer>
    </div>
  );
}

export default App;
