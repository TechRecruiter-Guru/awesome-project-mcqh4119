import React, { useState, useEffect, useCallback } from 'react';
import config from './config';

function App() {
  const [apiStatus, setApiStatus] = useState(null);
  const [agents, setAgents] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [pipeline, setPipeline] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [jobs, setJobs] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [screeningQueue, setScreeningQueue] = useState(null);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoState, setDemoState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [eliteSources, setEliteSources] = useState(null);
  const [auditCompliance, setAuditCompliance] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, agentsRes, statsRes, pipelineRes, funnelRes, jobsRes, queueRes, sourcesRes, auditRes] = await Promise.all([
        fetch(`${config.API_URL}/`),
        fetch(`${config.API_URL}/api/agents`),
        fetch(`${config.API_URL}/api/dashboard/stats`),
        fetch(`${config.API_URL}/api/pipeline`),
        fetch(`${config.API_URL}/api/pipeline/funnel`),
        fetch(`${config.API_URL}/api/jobs`),
        fetch(`${config.API_URL}/api/screening/queue`),
        fetch(`${config.API_URL}/api/sources`),
        fetch(`${config.API_URL}/api/audit/compliance-report`)
      ]);
      setApiStatus(await statusRes.json());
      setAgents(await agentsRes.json());
      setDashboardStats(await statsRes.json());
      setPipeline(await pipelineRes.json());
      setFunnel(await funnelRes.json());
      setJobs(await jobsRes.json());
      setScreeningQueue(await queueRes.json());
      setEliteSources(await sourcesRes.json());
      setAuditCompliance(await auditRes.json());
    } catch (err) { console.error('Failed to fetch:', err); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const callEndpoint = async (endpoint, method = 'GET', body = null, showAlert = true) => {
    try {
      const res = await fetch(`${config.API_URL}${endpoint}`, {
        method, headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : null
      });
      const data = await res.json();
      if (showAlert) alert(JSON.stringify(data, null, 2));
      fetchData();
      return data;
    } catch (err) {
      if (showAlert) alert('Error: ' + err.message);
      return null;
    }
  };

  const searchCandidates = async () => {
    const data = await callEndpoint('/api/candidates/search', 'POST', {
      role: 'Senior Robotics Engineer',
      skills: ['ROS/ROS2', 'Python', 'C++', 'Computer Vision', 'SLAM'],
      experience_min: 5
    }, false);
    if (data?.candidates) {
      setCandidates(data.candidates);
    }
  };

  const runDemoWorkflow = async () => {
    setDemoRunning(true);
    const data = await callEndpoint('/api/demo/workflow', 'GET', null, false);
    if (data) {
      setDemoState(data);
      if (data.steps?.[0]?.data?.top_3) {
        setCandidates(data.steps[0].data.top_3);
      }
    }
    setDemoRunning(false);
  };

  const styles = {
    container: { minHeight: '100vh', background: '#0a0a0f', color: '#e0e0e0', fontFamily: "'Inter', system-ui, sans-serif" },
    header: { background: 'linear-gradient(90deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%)', padding: '20px 40px', borderBottom: '1px solid #2a2a3e' },
    logo: { display: 'flex', alignItems: 'center', gap: '15px' },
    logoIcon: { width: '50px', height: '50px', background: 'linear-gradient(135deg, #9b5de5, #f15bb5)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', fontWeight: 'bold' },
    title: { fontSize: '1.8rem', fontWeight: 700, background: 'linear-gradient(90deg, #9b5de5, #f15bb5, #00bbf9)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
    subtitle: { fontSize: '0.9rem', color: '#888', marginTop: '2px' },
    nav: { display: 'flex', gap: '5px', background: '#12121a', padding: '10px 40px', borderBottom: '1px solid #2a2a3e', flexWrap: 'wrap' },
    navBtn: { padding: '12px 24px', background: 'transparent', border: 'none', color: '#888', cursor: 'pointer', borderRadius: '8px', fontSize: '0.9rem', transition: 'all 0.2s' },
    navActive: { background: 'linear-gradient(135deg, #1a1a2e, #2a2a4e)', color: '#9b5de5', borderBottom: '2px solid #9b5de5' },
    main: { padding: '30px 40px' },
    grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' },
    card: { background: 'linear-gradient(135deg, #12121a 0%, #1a1a2e 100%)', borderRadius: '16px', padding: '24px', border: '1px solid #2a2a3e' },
    cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' },
    cardTitle: { fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '10px' },
    statusDot: { width: '8px', height: '8px', borderRadius: '50%' },
    active: { background: '#9b5de5', boxShadow: '0 0 10px #9b5de5' },
    success: { background: '#00f5d4', boxShadow: '0 0 10px #00f5d4' },
    warning: { background: '#fbbf24', boxShadow: '0 0 10px #fbbf24' },
    metric: { display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #2a2a3e' },
    metricLabel: { color: '#888', fontSize: '0.85rem' },
    metricValue: { fontWeight: 600, color: '#9b5de5' },
    btn: { padding: '10px 20px', background: 'linear-gradient(135deg, #9b5de5, #f15bb5)', border: 'none', borderRadius: '8px', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem', margin: '4px' },
    btnSecondary: { background: 'linear-gradient(135deg, #2a2a4e, #3a3a5e)', color: '#e0e0e0' },
    btnSuccess: { background: 'linear-gradient(135deg, #00f5d4, #00bbf9)', color: '#0a0a0f' },
    btnDanger: { background: 'linear-gradient(135deg, #f87171, #dc2626)' },
    agentGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '15px' },
    agentCard: { background: '#1a1a2e', borderRadius: '12px', padding: '20px', border: '1px solid #2a2a3e' },
    tag: { display: 'inline-block', padding: '4px 12px', background: '#2a2a4e', borderRadius: '20px', fontSize: '0.75rem', margin: '2px' },
    skillTag: { background: 'linear-gradient(135deg, #1a1a2e, #2a2a4e)', border: '1px solid #9b5de5', color: '#9b5de5' },
    bigNumber: { fontSize: '2.5rem', fontWeight: 700, color: '#9b5de5' },
    candidateCard: { background: '#1a1a2e', borderRadius: '12px', padding: '20px', border: '1px solid #2a2a3e', marginBottom: '15px' },
    funnelBar: { height: '40px', borderRadius: '8px', marginBottom: '10px', display: 'flex', alignItems: 'center', paddingLeft: '15px', color: '#fff', fontWeight: '600', fontSize: '0.9rem', transition: 'width 0.5s ease' },
    stageCard: { background: '#1a1a2e', borderRadius: '12px', padding: '15px', border: '1px solid #2a2a3e', textAlign: 'center' },
    demoCard: { background: 'linear-gradient(135deg, #1a1a2e, #2a2a4e)', border: '2px solid #9b5de5', borderRadius: '16px', padding: '24px', marginBottom: '20px' },
    stepIndicator: { display: 'flex', justifyContent: 'space-between', marginBottom: '20px' },
    step: { flex: 1, textAlign: 'center', padding: '15px', borderRadius: '8px', background: '#1a1a2e', margin: '0 5px' },
    stepActive: { background: 'linear-gradient(135deg, #9b5de5, #f15bb5)', color: '#fff' },
    stepComplete: { background: 'linear-gradient(135deg, #00f5d4, #00bbf9)', color: '#0a0a0f' },
    independentBadge: { background: 'linear-gradient(135deg, #fbbf24, #f97316)', color: '#0a0a0f', padding: '2px 8px', borderRadius: '10px', fontSize: '0.7rem', fontWeight: 700, marginLeft: '8px' },
    researchBadge: { background: 'linear-gradient(135deg, #00f5d4, #00bbf9)', color: '#0a0a0f', padding: '2px 8px', borderRadius: '10px', fontSize: '0.7rem', fontWeight: 700 },
    sourceCard: { background: '#1a1a2e', borderRadius: '12px', padding: '20px', border: '1px solid #2a2a3e', textAlign: 'center' },
    sourceIcon: { fontSize: '2rem', marginBottom: '10px' },
    complianceCard: { background: 'linear-gradient(135deg, #12121a, #1a1a2e)', borderRadius: '16px', padding: '24px', border: '1px solid #00f5d4' },
    complianceGood: { color: '#00f5d4' },
    complianceWarning: { color: '#fbbf24' }
  };

  const renderDashboard = () => (
    <>
      {/* Demo Banner */}
      <div style={styles.demoCard}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
          <div>
            <h2 style={{margin: 0, color: '#fff', fontSize: '1.5rem'}}>AI-Powered Recruiting Demo</h2>
            <p style={{color: '#aaa', margin: '5px 0 0'}}>Watch our agentic system source, screen, and pipeline Physical AI talent</p>
          </div>
          <button
            style={{...styles.btn, padding: '15px 30px', fontSize: '1rem'}}
            onClick={runDemoWorkflow}
            disabled={demoRunning}
          >
            {demoRunning ? 'Running Demo...' : 'Run Full Demo'}
          </button>
        </div>

        {demoState && (
          <div>
            <div style={styles.stepIndicator}>
              {demoState.steps?.map((step, i) => (
                <div key={i} style={{...styles.step, ...styles.stepComplete}}>
                  <div style={{fontSize: '0.75rem', opacity: 0.8}}>Step {step.step}</div>
                  <div style={{fontWeight: 600}}>{step.agent}</div>
                  <div style={{fontSize: '0.8rem', marginTop: '5px'}}>{step.result}</div>
                </div>
              ))}
            </div>
            <div style={{background: '#12121a', padding: '20px', borderRadius: '12px'}}>
              <h4 style={{color: '#00f5d4', margin: '0 0 10px'}}>Summary - Human-in-the-Loop Required</h4>
              <p style={{color: '#aaa', margin: 0}}>{demoState.summary?.message}</p>
              <div style={{marginTop: '15px', display: 'flex', gap: '20px'}}>
                <div><span style={{color: '#888'}}>Sourced:</span> <span style={{color: '#9b5de5', fontWeight: 600}}>{demoState.summary?.total_candidates_sourced}</span></div>
                <div><span style={{color: '#888'}}>AI Approved:</span> <span style={{color: '#00f5d4', fontWeight: 600}}>{demoState.summary?.approved_by_ai}</span></div>
                <div><span style={{color: '#888'}}>Pending Review:</span> <span style={{color: '#fbbf24', fontWeight: 600}}>{demoState.summary?.pending_human_review}</span></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div style={styles.grid}>
        {/* Stats Cards */}
        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.active}}></span> Sourcing</div>
          </div>
          <div style={styles.bigNumber}>{dashboardStats?.sourcing?.total_sourced || 0}</div>
          <div style={{color: '#888', marginBottom: '15px'}}>Candidates Sourced</div>
          <div style={styles.metric}><span style={styles.metricLabel}>Sources Active</span><span style={styles.metricValue}>{dashboardStats?.sourcing?.sources_active || 6}</span></div>
          <div style={styles.metric}><span style={styles.metricLabel}>Avg Match Score</span><span style={styles.metricValue}>{(dashboardStats?.sourcing?.avg_match_score * 100 || 82).toFixed(0)}%</span></div>
          <button style={{...styles.btn, width: '100%', marginTop: '15px'}} onClick={searchCandidates}>Source Candidates</button>
        </div>

        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.success}}></span> Screening</div>
          </div>
          <div style={styles.bigNumber}>{dashboardStats?.screening?.total_screened || 0}</div>
          <div style={{color: '#888', marginBottom: '15px'}}>Candidates Screened</div>
          <div style={styles.metric}><span style={styles.metricLabel}>Approved</span><span style={{...styles.metricValue, color: '#00f5d4'}}>{dashboardStats?.screening?.approved || 0}</span></div>
          <div style={styles.metric}><span style={styles.metricLabel}>Pending Review</span><span style={{...styles.metricValue, color: '#fbbf24'}}>{dashboardStats?.screening?.pending_review || 0}</span></div>
          <div style={styles.metric}><span style={styles.metricLabel}>Approval Rate</span><span style={styles.metricValue}>{((dashboardStats?.screening?.approval_rate || 0) * 100).toFixed(0)}%</span></div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.active}}></span> Pipeline</div>
          </div>
          <div style={styles.bigNumber}>{dashboardStats?.pipeline?.total_in_pipeline || 0}</div>
          <div style={{color: '#888', marginBottom: '15px'}}>Active Candidates</div>
          <div style={styles.metric}><span style={styles.metricLabel}>Open Jobs</span><span style={styles.metricValue}>{dashboardStats?.pipeline?.active_jobs || 3}</span></div>
          <div style={styles.metric}><span style={styles.metricLabel}>Hired This Month</span><span style={{...styles.metricValue, color: '#00f5d4'}}>{dashboardStats?.pipeline?.hired_this_month || 0}</span></div>
          <div style={styles.metric}><span style={styles.metricLabel}>Conversion Rate</span><span style={styles.metricValue}>{((dashboardStats?.pipeline?.avg_conversion || 0.12) * 100).toFixed(0)}%</span></div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardHeader}>
            <div style={styles.cardTitle}><span style={{...styles.statusDot, ...styles.active}}></span> Matching</div>
          </div>
          <div style={styles.bigNumber}>{dashboardStats?.matching?.total_matches || 0}</div>
          <div style={{color: '#888', marginBottom: '15px'}}>Matches Analyzed</div>
          <div style={styles.metric}><span style={styles.metricLabel}>Avg Score</span><span style={styles.metricValue}>{((dashboardStats?.matching?.avg_score || 0) * 100).toFixed(0)}%</span></div>
          <div style={styles.metric}><span style={styles.metricLabel}>Strong Matches</span><span style={{...styles.metricValue, color: '#00f5d4'}}>{dashboardStats?.matching?.strong_matches || 0}</span></div>
          <div style={styles.metric}><span style={styles.metricLabel}>Skills Tracked</span><span style={styles.metricValue}>{dashboardStats?.matching?.skills_tracked || 12}</span></div>
        </div>
      </div>

      {/* Latest Candidates */}
      {candidates.length > 0 && (
        <div style={{marginTop: '30px'}}>
          <h3 style={{color: '#fff', marginBottom: '20px'}}>Latest Sourced Candidates</h3>
          <div style={styles.grid}>
            {candidates.slice(0, 6).map((c, i) => (
              <div key={i} style={styles.candidateCard}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                  <span style={{fontWeight: 600, color: '#fff'}}>
                    {c.name}
                    {c.is_independent_researcher && <span style={styles.independentBadge}>INDEPENDENT</span>}
                  </span>
                  <span style={{background: 'linear-gradient(135deg, #9b5de5, #f15bb5)', padding: '2px 10px', borderRadius: '12px', fontSize: '0.75rem'}}>{(c.match_score * 100).toFixed(0)}%</span>
                </div>
                <p style={{color: '#9b5de5', fontSize: '0.9rem', margin: '0 0 5px'}}>{c.title}</p>
                <p style={{color: '#888', fontSize: '0.85rem', margin: '0 0 10px'}}>{c.current_company} • {c.experience_years} yrs</p>
                {/* Research Metrics */}
                {(c.h_index || c.citations || c.publications) && (
                  <div style={{display: 'flex', gap: '10px', marginBottom: '10px', flexWrap: 'wrap'}}>
                    {c.h_index > 0 && <span style={styles.researchBadge}>H-index: {c.h_index}</span>}
                    {c.citations > 0 && <span style={styles.researchBadge}>{c.citations} citations</span>}
                    {c.publications > 0 && <span style={styles.researchBadge}>{c.publications} papers</span>}
                  </div>
                )}
                <div style={{marginBottom: '10px'}}>
                  {c.skills?.slice(0, 4).map(s => <span key={s} style={{...styles.tag, ...styles.skillTag}}>{s}</span>)}
                </div>
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                  <span style={{fontSize: '0.8rem', color: '#888'}}>{c.source || c.availability}</span>
                  <span style={{fontSize: '0.85rem', color: '#00f5d4'}}>{c.salary_expectation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );

  const renderPipeline = () => (
    <>
      {/* Funnel Visualization */}
      <div style={styles.card}>
        <div style={styles.cardTitle}>Recruiting Funnel</div>
        <div style={{marginTop: '20px'}}>
          {funnel?.funnel?.map((stage, i) => (
            <div key={stage.stage}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '5px'}}>
                <span style={{color: '#888'}}>{stage.stage_display}</span>
                <span style={{color: '#9b5de5'}}>{stage.count} ({stage.percentage}%)</span>
              </div>
              <div style={{
                ...styles.funnelBar,
                width: `${Math.max(stage.percentage, 10)}%`,
                background: `linear-gradient(90deg, hsl(${280 - i * 30}, 70%, 50%), hsl(${280 - i * 30 + 20}, 70%, 60%))`
              }}>
                {stage.count}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline Stages */}
      <div style={{marginTop: '30px'}}>
        <h3 style={{color: '#fff', marginBottom: '20px'}}>Pipeline by Stage</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px'}}>
          {pipeline?.pipeline && Object.entries(pipeline.pipeline).map(([stage, data]) => (
            <div key={stage} style={styles.stageCard}>
              <div style={{fontSize: '2rem', fontWeight: 700, color: '#9b5de5'}}>{data.count}</div>
              <div style={{color: '#888', fontSize: '0.85rem', textTransform: 'capitalize'}}>{stage.replace('_', ' ')}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Jobs */}
      <div style={{marginTop: '30px'}}>
        <h3 style={{color: '#fff', marginBottom: '20px'}}>Open Positions</h3>
        <div style={styles.grid}>
          {jobs?.jobs?.map(job => (
            <div key={job.id} style={styles.candidateCard}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                <span style={{fontWeight: 600, color: '#fff'}}>{job.title}</span>
                <span style={{...styles.tag, background: job.priority === 'high' ? '#f15bb5' : '#2a2a4e'}}>{job.priority}</span>
              </div>
              <p style={{color: '#888', fontSize: '0.85rem', margin: '0 0 10px'}}>{job.location} • {job.department}</p>
              <div style={{marginBottom: '10px'}}>
                {job.required_skills?.slice(0, 3).map(s => <span key={s} style={{...styles.tag, ...styles.skillTag}}>{s}</span>)}
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <span style={{fontSize: '0.8rem', color: '#00f5d4'}}>{job.salary_range}</span>
                <span style={{fontSize: '0.85rem', color: '#9b5de5'}}>{job.pipeline_count || 0} in pipeline</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div style={{marginTop: '20px'}}>
        <button style={styles.btn} onClick={() => callEndpoint('/api/pipeline/metrics')}>View Metrics</button>
        <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => callEndpoint('/api/pipeline/predict')}>Predict Outcomes</button>
      </div>
    </>
  );

  const renderReview = () => (
    <>
      <div style={styles.demoCard}>
        <h2 style={{margin: '0 0 10px', color: '#fff'}}>Human-in-the-Loop Review Queue</h2>
        <p style={{color: '#aaa', margin: 0}}>AI has pre-screened these candidates. Your review is required for final decisions.</p>
      </div>

      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={styles.cardTitle}>Queue Status</div>
          <div style={{...styles.bigNumber, marginTop: '10px'}}>{screeningQueue?.queue_length || 0}</div>
          <div style={{color: '#888'}}>Pending Review</div>
          <button style={{...styles.btn, width: '100%', marginTop: '20px'}} onClick={() => callEndpoint('/api/screening/queue')}>Refresh Queue</button>
        </div>

        <div style={styles.card}>
          <div style={styles.cardTitle}>Review Actions</div>
          <p style={{color: '#888', fontSize: '0.85rem', marginBottom: '20px'}}>Click on a candidate below to approve or reject</p>
          <button style={{...styles.btn, ...styles.btnSuccess, width: '100%', marginBottom: '10px'}}>Approve Selected</button>
          <button style={{...styles.btn, ...styles.btnDanger, width: '100%'}}>Reject Selected</button>
        </div>
      </div>

      {screeningQueue?.candidates?.length > 0 && (
        <div style={{marginTop: '30px'}}>
          <h3 style={{color: '#fff', marginBottom: '20px'}}>Candidates Pending Review</h3>
          {screeningQueue.candidates.map((c, i) => (
            <div key={i} style={{...styles.candidateCard, border: '1px solid #fbbf24'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'start'}}>
                <div>
                  <span style={{fontWeight: 600, color: '#fff', fontSize: '1.1rem'}}>{c.candidate_name}</span>
                  <div style={{marginTop: '10px'}}>
                    <span style={{color: '#888'}}>Overall Score: </span>
                    <span style={{color: '#9b5de5', fontWeight: 600}}>{(c.scores?.overall * 100).toFixed(0)}%</span>
                  </div>
                  <div style={{marginTop: '5px', fontSize: '0.85rem', color: '#aaa'}}>{c.ai_notes}</div>
                </div>
                <div style={{display: 'flex', gap: '10px'}}>
                  <button style={{...styles.btn, ...styles.btnSuccess}} onClick={() => callEndpoint(`/api/screening/${c.candidate_id}/approve`, 'POST', {reviewer: 'recruiter'})}>Approve</button>
                  <button style={{...styles.btn, ...styles.btnDanger}} onClick={() => callEndpoint(`/api/screening/${c.candidate_id}/reject`, 'POST', {reviewer: 'recruiter', reason: 'Not a fit'})}>Reject</button>
                </div>
              </div>
              {c.red_flags?.length > 0 && (
                <div style={{marginTop: '10px', padding: '10px', background: 'rgba(251, 191, 36, 0.1)', borderRadius: '8px'}}>
                  <span style={{color: '#fbbf24', fontWeight: 600}}>Review Flags: </span>
                  {c.red_flags.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {(!screeningQueue?.candidates || screeningQueue.candidates.length === 0) && (
        <div style={{textAlign: 'center', padding: '40px', color: '#888'}}>
          <p>No candidates pending review. Run the demo or source candidates to populate the queue.</p>
          <button style={styles.btn} onClick={runDemoWorkflow}>Run Demo Workflow</button>
        </div>
      )}
    </>
  );

  const renderAgents = () => (
    <div style={styles.agentGrid}>
      {agents?.agents && Object.entries(agents.agents).map(([name, agent]) => (
        <div key={name} style={styles.agentCard}>
          <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px'}}>
            <span style={{...styles.statusDot, ...(agent.status === 'running' ? styles.active : styles.warning)}}></span>
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

  const renderArchitecture = () => (
    <div style={{maxWidth: '1000px', margin: '0 auto'}}>
      <div style={styles.card}>
        <div style={styles.cardTitle}>PhysicalAI Talent - Multi-Agent Recruiting Architecture</div>
        <pre style={{background: '#0a0a0f', padding: '20px', borderRadius: '12px', overflow: 'auto', fontSize: '0.75rem', color: '#9b5de5'}}>
{`
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                    PHYSICALAI TALENT v3.0 - AI RECRUITING PLATFORM                         ║
║          VanguardLab - Human-in-the-Loop AI + Defensible AI Hiring                         ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                           ║
║   ┌─────────────────────────────────────────────────────────────────────────────────┐    ║
║   │                           ORCHESTRATOR AGENT                                     │    ║
║   │                    Central Workflow Coordinator                                  │    ║
║   └─────────────────────────────────┬───────────────────────────────────────────────┘    ║
║                                     │                                                     ║
║   ┌─────────────────────────────────┼─────────────────────────────────────┐              ║
║   │                                 │                                     │              ║
║   ▼                                 ▼                                     ▼              ║
║ ┌─────────────────┐         ┌─────────────────┐                 ┌─────────────────┐     ║
║ │  SOURCER AGENT  │         │  MATCHER AGENT  │                 │ SCREENER AGENT  │     ║
║ │ 16 Elite Sources│ ──────► │ Research-Weight │ ─────────────►  │    AI Screen    │     ║
║ └─────────────────┘         └─────────────────┘                 └────────┬────────┘     ║
║         │                           │                                    │              ║
║         ▼                           ▼                                    ▼              ║
║ ┌─────────────────┐         ┌─────────────────┐              ┌─────────────────────┐    ║
║ │ RESEARCH        │         │ SCORING         │              │   HUMAN REVIEW      │    ║
║ │ ▪ ArXiv         │         │ ▪ Skills: 30%   │              │      QUEUE          │    ║
║ │ ▪ Zenodo        │         │ ▪ Research: 25% │              │  (Human-in-Loop)    │    ║
║ │ ▪ Papers w/Code │         │ ▪ Experience:15%│              └──────────┬──────────┘    ║
║ │ ML PLATFORMS    │         │ ▪ Platform: 10% │                         │              ║
║ │ ▪ HuggingFace   │         │ ▪ Independent:  │                         ▼              ║
║ │ ▪ Kaggle        │         │   Boost: 10%    │              ┌─────────────────────┐    ║
║ │ ROBOTICS        │         └─────────────────┘              │   PIPELINE AGENT    │    ║
║ │ ▪ ROS Discourse │                                          └─────────────────────┘    ║
║ │ ▪ Robotics SE   │                                                     │              ║
║ └─────────────────┘                                                     ▼              ║
║                                     ┌───────────────────────────────────────────────┐   ║
║                                     │              TALENT PIPELINE                   │   ║
║                                     │ Sourced → Screened → Interview → Offer → Hired│   ║
║                                     └───────────────────────────────────────────────┘   ║
║                                                          │                              ║
║   ┌──────────────────────────────────────────────────────┼──────────────────────────┐   ║
║   │                                                      ▼                          │   ║
║   │                        ┌─────────────────────────────────────────────┐          │   ║
║   │                        │            AUDIT AGENT                       │          │   ║
║   │   DEFENSIBLE AI        │     Zero Data Risk Architecture             │          │   ║
║   │   HIRING               │  ▪ NO PII Stored - Only Hashed IDs          │          │   ║
║   │                        │  ▪ Full Decision Explainability             │          │   ║
║   │                        │  ▪ EEOC/OFCCP Compliance                    │          │   ║
║   │                        │  ▪ Human-in-Loop Tracking                   │          │   ║
║   │                        └─────────────────────────────────────────────┘          │   ║
║   └─────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                         ║
╠═════════════════════════════════════════════════════════════════════════════════════════╣
║  YOUR EDGE: 16 Sources ATS Miss | Independent Researcher Boost | Zero Data Risk Audit   ║
╚═════════════════════════════════════════════════════════════════════════════════════════╝
`}
        </pre>
        <div style={{marginTop: '20px'}}>
          <h4 style={{color: '#9b5de5'}}>Key Features:</h4>
          <ul style={{color: '#888', lineHeight: '2'}}>
            <li><strong style={{color: '#00f5d4'}}>Elite Sourcing:</strong> 16+ platforms where traditional ATS don't look (ArXiv, Zenodo, HuggingFace, Kaggle)</li>
            <li><strong style={{color: '#00f5d4'}}>Research Profiles:</strong> H-index, citations, ORCID, publication tracking</li>
            <li><strong style={{color: '#00f5d4'}}>Independent Researcher Boost:</strong> 10% boost for researchers not tied to company benchmarks</li>
            <li><strong style={{color: '#00f5d4'}}>Human-in-the-Loop:</strong> Recruiters make final decisions on borderline candidates</li>
            <li><strong style={{color: '#00f5d4'}}>Defensible AI:</strong> Zero PII audit trails for legal protection</li>
          </ul>
        </div>
      </div>
    </div>
  );

  const renderEliteSources = () => {
    const sourcesByType = eliteSources?.sources_by_type || {};
    const typeLabels = {
      research: { label: 'Research Platforms', icon: '📚', color: '#9b5de5' },
      ml_platform: { label: 'ML & AI Platforms', icon: '🤖', color: '#f15bb5' },
      code: { label: 'Code & OSS', icon: '💻', color: '#00bbf9' },
      robotics: { label: 'Robotics Communities', icon: '🦾', color: '#00f5d4' },
      professional: { label: 'Professional Networks', icon: '👔', color: '#fbbf24' },
      jobs: { label: 'Job Boards', icon: '💼', color: '#f97316' }
    };

    return (
      <>
        <div style={styles.demoCard}>
          <h2 style={{margin: '0 0 10px', color: '#fff'}}>Elite Sourcing - Where Top 5 ATS Don't Look</h2>
          <p style={{color: '#aaa', margin: 0}}>
            {eliteSources?.total_sources || 16} unique sources targeting PASSIVE candidates in Physical AI, Robotics & ML.
            Traditional ATS (Greenhouse, Lever, Workday) miss these talent pools entirely.
          </p>
        </div>

        <div style={styles.grid}>
          <div style={styles.card}>
            <div style={styles.cardTitle}>Sourcing Stats</div>
            <div style={{...styles.bigNumber, marginTop: '10px'}}>{eliteSources?.total_sources || 16}</div>
            <div style={{color: '#888'}}>Elite Sources Active</div>
            <div style={{marginTop: '20px'}}>
              <div style={styles.metric}><span style={styles.metricLabel}>Research Platforms</span><span style={styles.metricValue}>{sourcesByType.research?.length || 4}</span></div>
              <div style={styles.metric}><span style={styles.metricLabel}>ML Platforms</span><span style={styles.metricValue}>{sourcesByType.ml_platform?.length || 3}</span></div>
              <div style={styles.metric}><span style={styles.metricLabel}>Robotics Communities</span><span style={styles.metricValue}>{sourcesByType.robotics?.length || 3}</span></div>
            </div>
          </div>

          <div style={styles.card}>
            <div style={styles.cardTitle}>Your Edge</div>
            <div style={{marginTop: '15px', color: '#888', lineHeight: '1.8'}}>
              <p><strong style={{color: '#00f5d4'}}>PASSIVE Candidates:</strong> Researchers publishing papers, not job hunting</p>
              <p><strong style={{color: '#fbbf24'}}>Independent Researchers:</strong> Boosted 10% - not tied to company benchmarks</p>
              <p><strong style={{color: '#9b5de5'}}>Research Signals:</strong> H-index, citations, publications weighted 25%</p>
            </div>
          </div>
        </div>

        {Object.entries(sourcesByType).map(([type, sources]) => (
          <div key={type} style={{marginTop: '30px'}}>
            <h3 style={{color: typeLabels[type]?.color || '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px'}}>
              <span>{typeLabels[type]?.icon}</span> {typeLabels[type]?.label || type}
            </h3>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px'}}>
              {sources.map(source => (
                <div key={source.name} style={styles.sourceCard}>
                  <div style={{fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '8px'}}>{source.name}</div>
                  <div style={{fontSize: '0.85rem', color: '#888', marginBottom: '10px'}}>{source.description}</div>
                  <div style={{background: typeLabels[type]?.color || '#9b5de5', color: '#0a0a0f', padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600, display: 'inline-block'}}>
                    {(source.weight * 100).toFixed(0)}% weight
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div style={{marginTop: '30px'}}>
          <button style={styles.btn} onClick={() => callEndpoint('/api/research/search', 'POST', { area: 'robotics', skills: ['ROS', 'SLAM'] }, false)}>
            Search Researchers
          </button>
        </div>
      </>
    );
  };

  const renderAuditCompliance = () => {
    const summary = auditCompliance?.summary || {};
    const humanLoop = auditCompliance?.human_in_loop_compliance || {};
    const aiOversight = auditCompliance?.ai_oversight || {};
    const dataProtection = auditCompliance?.data_protection || {};

    return (
      <>
        <div style={{...styles.demoCard, borderColor: '#00f5d4'}}>
          <h2 style={{margin: '0 0 10px', color: '#fff'}}>Defensible AI Hiring - Internal Protection</h2>
          <p style={{color: '#aaa', margin: 0}}>
            Zero Data Risk Architecture: Only audit breadcrumbs stored, NO PII.
            Full explainability for EEOC/OFCCP compliance. Inspired by defensibleaihiring.com.
          </p>
        </div>

        <div style={styles.grid}>
          {/* Decision Audit */}
          <div style={styles.complianceCard}>
            <div style={styles.cardTitle}>Decision Audit Trail</div>
            <div style={{...styles.bigNumber, marginTop: '10px', color: '#00f5d4'}}>{summary.total_decisions_logged || 0}</div>
            <div style={{color: '#888'}}>Total Decisions Logged</div>
            <div style={{marginTop: '20px'}}>
              <div style={styles.metric}><span style={styles.metricLabel}>AI Decisions</span><span style={styles.metricValue}>{summary.ai_decisions || 0}</span></div>
              <div style={styles.metric}><span style={styles.metricLabel}>Human Decisions</span><span style={styles.metricValue}>{summary.human_decisions || 0}</span></div>
              <div style={styles.metric}><span style={styles.metricLabel}>Explainability Rate</span><span style={{...styles.metricValue, color: '#00f5d4'}}>{((summary.explainability_rate || 1) * 100).toFixed(0)}%</span></div>
            </div>
          </div>

          {/* Human-in-Loop Compliance */}
          <div style={styles.complianceCard}>
            <div style={styles.cardTitle}>Human-in-the-Loop Compliance</div>
            <div style={{...styles.bigNumber, marginTop: '10px', color: humanLoop.compliance_rate >= 0.8 ? '#00f5d4' : '#fbbf24'}}>
              {((humanLoop.compliance_rate || 1) * 100).toFixed(0)}%
            </div>
            <div style={{color: '#888'}}>Compliance Rate</div>
            <div style={{marginTop: '20px'}}>
              <div style={styles.metric}><span style={styles.metricLabel}>Requiring Review</span><span style={styles.metricValue}>{humanLoop.decisions_requiring_review || 0}</span></div>
              <div style={styles.metric}><span style={styles.metricLabel}>Reviews Completed</span><span style={{...styles.metricValue, color: '#00f5d4'}}>{humanLoop.reviews_completed || 0}</span></div>
              <div style={styles.metric}><span style={styles.metricLabel}>Pending Reviews</span><span style={{...styles.metricValue, color: humanLoop.pending_reviews > 0 ? '#fbbf24' : '#00f5d4'}}>{humanLoop.pending_reviews || 0}</span></div>
            </div>
          </div>

          {/* AI Oversight */}
          <div style={styles.complianceCard}>
            <div style={styles.cardTitle}>AI Oversight Metrics</div>
            <div style={{...styles.bigNumber, marginTop: '10px', color: '#9b5de5'}}>
              {((aiOversight.ai_human_agreement_rate || 1) * 100).toFixed(0)}%
            </div>
            <div style={{color: '#888'}}>AI-Human Agreement</div>
            <div style={{marginTop: '20px'}}>
              <div style={styles.metric}><span style={styles.metricLabel}>AI Override Count</span><span style={styles.metricValue}>{aiOversight.ai_override_count || 0}</span></div>
              <div style={styles.metric}><span style={styles.metricLabel}>Override Rate</span><span style={styles.metricValue}>{((aiOversight.ai_override_rate || 0) * 100).toFixed(0)}%</span></div>
            </div>
          </div>

          {/* Data Protection */}
          <div style={styles.complianceCard}>
            <div style={styles.cardTitle}>Zero Data Risk Architecture</div>
            <div style={{marginTop: '20px'}}>
              <div style={styles.metric}>
                <span style={styles.metricLabel}>PII Stored</span>
                <span style={{...styles.metricValue, color: dataProtection.pii_stored === false ? '#00f5d4' : '#f87171'}}>
                  {dataProtection.pii_stored === false ? 'NONE' : 'YES'}
                </span>
              </div>
              <div style={styles.metric}>
                <span style={styles.metricLabel}>Only Hashed IDs</span>
                <span style={{...styles.metricValue, color: dataProtection.only_hashed_ids ? '#00f5d4' : '#f87171'}}>
                  {dataProtection.only_hashed_ids ? 'YES' : 'NO'}
                </span>
              </div>
              <div style={styles.metric}>
                <span style={styles.metricLabel}>GDPR Compliant</span>
                <span style={{...styles.metricValue, color: dataProtection.gdpr_compliant ? '#00f5d4' : '#f87171'}}>
                  {dataProtection.gdpr_compliant ? 'YES' : 'NO'}
                </span>
              </div>
              <div style={styles.metric}>
                <span style={styles.metricLabel}>CCPA Compliant</span>
                <span style={{...styles.metricValue, color: dataProtection.ccpa_compliant ? '#00f5d4' : '#f87171'}}>
                  {dataProtection.ccpa_compliant ? 'YES' : 'NO'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Adverse Impact */}
        <div style={{marginTop: '30px'}}>
          <div style={styles.card}>
            <div style={styles.cardTitle}>Adverse Impact Monitoring</div>
            <div style={{display: 'flex', alignItems: 'center', gap: '15px', marginTop: '15px'}}>
              <div style={{...styles.bigNumber, fontSize: '1.5rem'}}>{auditCompliance?.adverse_impact_flags || 0}</div>
              <div style={{color: '#888'}}>
                {auditCompliance?.adverse_impact_flags === 0
                  ? 'No adverse impact flags detected. System operating within compliance parameters.'
                  : 'Flags require review by compliance team.'}
              </div>
            </div>
          </div>
        </div>

        <div style={{marginTop: '20px'}}>
          <button style={styles.btn} onClick={() => callEndpoint('/api/audit/trail')}>View Full Audit Trail</button>
          <button style={{...styles.btn, ...styles.btnSecondary}} onClick={() => callEndpoint('/api/audit/compliance-report')}>Refresh Report</button>
        </div>
      </>
    );
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.logo}>
          <div style={styles.logoIcon}>AI</div>
          <div>
            <div style={styles.title}>PhysicalAI Talent</div>
            <div style={styles.subtitle}>AI-Powered Recruiting for Robotics & Autonomous Systems</div>
          </div>
        </div>
      </header>

      <nav style={styles.nav}>
        {[
          {id: 'dashboard', label: 'Dashboard'},
          {id: 'sources', label: 'Elite Sources'},
          {id: 'pipeline', label: 'Pipeline'},
          {id: 'review', label: 'Human Review'},
          {id: 'audit', label: 'Audit & Compliance'},
          {id: 'agents', label: 'AI Agents'},
          {id: 'architecture', label: 'Architecture'}
        ].map(t => (
          <button key={t.id} style={{...styles.navBtn, ...(activeTab === t.id ? styles.navActive : {})}} onClick={() => setActiveTab(t.id)}>
            {t.label}
            {t.id === 'review' && screeningQueue?.queue_length > 0 && (
              <span style={{marginLeft: '8px', background: '#fbbf24', color: '#0a0a0f', padding: '2px 8px', borderRadius: '10px', fontSize: '0.7rem', fontWeight: 700}}>{screeningQueue.queue_length}</span>
            )}
          </button>
        ))}
        <button style={styles.navBtn} onClick={fetchData}>Refresh</button>
      </nav>

      <main style={styles.main}>
        {loading ? <p style={{textAlign: 'center', color: '#888'}}>Loading recruiting platform...</p> : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'sources' && renderEliteSources()}
            {activeTab === 'pipeline' && renderPipeline()}
            {activeTab === 'review' && renderReview()}
            {activeTab === 'audit' && renderAuditCompliance()}
            {activeTab === 'agents' && renderAgents()}
            {activeTab === 'architecture' && renderArchitecture()}
          </>
        )}
      </main>

      <footer style={{textAlign: 'center', padding: '30px', borderTop: '1px solid #2a2a3e', color: '#666'}}>
        <p>PhysicalAI Talent v3.0 | VanguardLab | AI-Powered Recruiting for Physical AI, Robotics & Autonomous Systems</p>
        <p style={{fontSize: '0.8rem', marginTop: '5px'}}>16 Elite Sources | Research-Weighted Scoring | Defensible AI Hiring | Zero Data Risk</p>
        <p style={{fontSize: '0.8rem', marginTop: '5px'}}>Backend: {config.API_URL}</p>
      </footer>
    </div>
  );
}

export default App;
