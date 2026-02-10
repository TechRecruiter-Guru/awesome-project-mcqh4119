# ATS Integration Specification
## Connecting Your ATS (mctf66nf) to the Agentic AI Platform

---

## Overview

This document specifies the integration points between your custom ATS and the DefensibleHiring.ai Agentic Platform.

---

## Architecture: ATS → Agent Platform Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        YOUR ATS (awesome-project-mctf66nf)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Jobs Table          │  Candidates Table    │  Applications Table          │
│  - job_id            │  - candidate_id      │  - application_id            │
│  - title             │  - hashed_email      │  - job_id (FK)               │
│  - requirements      │  - resume_vector     │  - candidate_id (FK)         │
│  - status            │  - skills_json       │  - status                    │
│  - created_at        │  - created_at        │  - created_at                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API / Webhooks
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Zero-Trust Security Layer)                │
│  • JWT Token Validation          • Rate Limiting (1000 req/min)            │
│  • mTLS Certificate Verification • Request Signing (HMAC-SHA256)           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENT ORCHESTRATOR                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  SourcerAgent  →  MatcherAgent  →  ScreenerAgent  →  AuditAgent            │
│       ↓                ↓                 ↓                ↓                │
│  Finds candidates  Scores match    Generates       Logs decision           │
│  from job reqs     0-100 scale     explanation     with reasoning          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Webhook Callback
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        YOUR ATS (Updates Received)                          │
│  • Candidate scores updated       • Human review queue populated           │
│  • Audit trail attached           • Bias metrics logged                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Required ATS API Endpoints

Your ATS should expose these endpoints for the agent platform to consume:

### 1. Jobs API

```javascript
// GET /api/jobs - List active jobs
// Response:
{
  "jobs": [
    {
      "id": "job_abc123",
      "title": "Senior Robotics Engineer",
      "department": "Engineering",
      "requirements": ["Python", "ROS2", "Computer Vision"],
      "experience_years_min": 5,
      "education_requirements": ["BS Computer Science", "MS Robotics"],
      "location": "San Francisco, CA",
      "remote_eligible": true,
      "status": "active",
      "created_at": "2026-02-01T00:00:00Z"
    }
  ]
}

// GET /api/jobs/:id - Get specific job details
// GET /api/jobs/:id/requirements - Get parsed requirements
```

### 2. Candidates API

```javascript
// GET /api/candidates - List candidates (paginated)
// Query params: ?status=new&limit=50&offset=0
// Response:
{
  "candidates": [
    {
      "id": "cand_xyz789",
      "hashed_identifier": "sha256:a1b2c3...",  // NO PII
      "skills": ["Python", "TensorFlow", "ROS"],
      "experience_years": 7,
      "education_level": "masters",
      "resume_vector": [0.123, 0.456, ...],  // Embedding
      "created_at": "2026-02-05T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 1500,
    "limit": 50,
    "offset": 0
  }
}

// GET /api/candidates/:id - Get candidate details (no PII)
// GET /api/candidates/:id/applications - List their applications
```

### 3. Applications API

```javascript
// GET /api/applications - List applications
// Query params: ?job_id=job_abc123&status=pending
// Response:
{
  "applications": [
    {
      "id": "app_def456",
      "job_id": "job_abc123",
      "candidate_id": "cand_xyz789",
      "status": "pending_review",
      "source": "linkedin",
      "applied_at": "2026-02-06T14:30:00Z"
    }
  ]
}

// PATCH /api/applications/:id - Update application status
// Body: { "status": "in_review", "agent_score": 87, "agent_reasoning": "..." }
```

### 4. Webhooks (Agent Platform → ATS)

Your ATS should accept these webhook callbacks:

```javascript
// POST /webhooks/agent-results
// Headers: X-Webhook-Signature: sha256=...
// Body:
{
  "event": "screening_complete",
  "application_id": "app_def456",
  "results": {
    "match_score": 87,
    "confidence": 0.92,
    "reasoning": "Strong match: 7 years Python experience exceeds 5-year requirement...",
    "recommendation": "advance_to_human_review",
    "bias_check": {
      "passed": true,
      "protected_attributes_detected": false
    },
    "audit_id": "audit_001",
    "timestamp": "2026-02-06T14:35:00Z"
  }
}

// POST /webhooks/bias-alert
// Body:
{
  "event": "bias_threshold_warning",
  "job_id": "job_abc123",
  "metric": "selection_rate",
  "value": 0.78,  // Below 0.80 four-fifths rule
  "affected_group": "age_40_plus",
  "recommended_action": "pause_automated_screening"
}
```

---

## Agent Platform API Endpoints

The agent platform exposes these endpoints for your ATS to call:

### 1. Screening Requests

```javascript
// POST /api/v1/screen
// Headers: Authorization: Bearer <jwt_token>
// Body:
{
  "job_id": "job_abc123",
  "candidate_id": "cand_xyz789",
  "application_id": "app_def456",
  "job_requirements": {
    "skills": ["Python", "ROS2"],
    "experience_min": 5
  },
  "candidate_profile": {
    "skills": ["Python", "TensorFlow", "ROS"],
    "experience_years": 7,
    "resume_vector": [0.123, 0.456, ...]
  },
  "callback_url": "https://your-ats.com/webhooks/agent-results"
}

// Response:
{
  "request_id": "req_abc123",
  "status": "queued",
  "estimated_completion": "2026-02-06T14:35:00Z"
}
```

### 2. Batch Screening

```javascript
// POST /api/v1/screen/batch
// Body:
{
  "job_id": "job_abc123",
  "candidate_ids": ["cand_001", "cand_002", "cand_003"],
  "callback_url": "https://your-ats.com/webhooks/agent-results"
}
```

### 3. Audit Trail

```javascript
// GET /api/v1/audit/:application_id
// Response:
{
  "audit_id": "audit_001",
  "application_id": "app_def456",
  "decision_chain": [
    {
      "agent": "SourcerAgent",
      "action": "parse_requirements",
      "timestamp": "2026-02-06T14:30:01Z",
      "output": { "skills_extracted": ["Python", "ROS2"] }
    },
    {
      "agent": "MatcherAgent",
      "action": "compute_match_score",
      "timestamp": "2026-02-06T14:30:02Z",
      "output": { "score": 87, "method": "cosine_similarity" }
    },
    {
      "agent": "ScreenerAgent",
      "action": "generate_recommendation",
      "timestamp": "2026-02-06T14:30:03Z",
      "output": { "recommendation": "advance", "reasoning": "..." }
    }
  ],
  "bias_analysis": {
    "protected_attributes_in_decision": false,
    "selection_rates_by_group": { ... }
  }
}
```

### 4. Bias Metrics

```javascript
// GET /api/v1/metrics/bias/:job_id
// Response:
{
  "job_id": "job_abc123",
  "period": "last_30_days",
  "selection_rates": {
    "overall": 0.23,
    "by_gender": { "male": 0.24, "female": 0.22 },
    "by_age": { "under_40": 0.25, "40_plus": 0.20 },
    "by_ethnicity": { ... }
  },
  "four_fifths_compliance": {
    "gender": true,
    "age": false,  // Warning: 0.20/0.25 = 0.80, at threshold
    "ethnicity": true
  },
  "alerts": [
    {
      "type": "threshold_warning",
      "group": "age_40_plus",
      "message": "Selection rate at four-fifths threshold"
    }
  ]
}
```

---

## Integration Implementation Steps

### Step 1: Configure ATS Webhook Endpoints

In your ATS (mctf66nf), add webhook handlers:

```javascript
// routes/webhooks.js
const express = require('express');
const crypto = require('crypto');
const router = express.Router();

// Verify webhook signature
const verifySignature = (req, res, next) => {
  const signature = req.headers['x-webhook-signature'];
  const payload = JSON.stringify(req.body);
  const expected = `sha256=${crypto
    .createHmac('sha256', process.env.WEBHOOK_SECRET)
    .update(payload)
    .digest('hex')}`;

  if (signature !== expected) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  next();
};

// Handle screening results
router.post('/agent-results', verifySignature, async (req, res) => {
  const { application_id, results } = req.body;

  // Update application with agent results
  await db.applications.update({
    where: { id: application_id },
    data: {
      agent_score: results.match_score,
      agent_reasoning: results.reasoning,
      agent_recommendation: results.recommendation,
      status: results.recommendation === 'advance_to_human_review'
        ? 'pending_human_review'
        : 'agent_reviewed',
      audit_id: results.audit_id
    }
  });

  res.json({ received: true });
});

// Handle bias alerts
router.post('/bias-alert', verifySignature, async (req, res) => {
  const { job_id, metric, value, affected_group, recommended_action } = req.body;

  // Log alert and notify admins
  await db.bias_alerts.create({
    data: { job_id, metric, value, affected_group, recommended_action }
  });

  // Optionally pause automated screening
  if (recommended_action === 'pause_automated_screening') {
    await db.jobs.update({
      where: { id: job_id },
      data: { automated_screening_enabled: false }
    });
  }

  res.json({ received: true });
});

module.exports = router;
```

### Step 2: Add API Client for Agent Platform

```javascript
// services/agentPlatform.js
const axios = require('axios');

class AgentPlatformClient {
  constructor() {
    this.baseUrl = process.env.AGENT_PLATFORM_URL;
    this.apiKey = process.env.AGENT_PLATFORM_API_KEY;
  }

  async screenCandidate(jobId, candidateId, applicationId, jobReqs, candidateProfile) {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/screen`,
      {
        job_id: jobId,
        candidate_id: candidateId,
        application_id: applicationId,
        job_requirements: jobReqs,
        candidate_profile: candidateProfile,
        callback_url: `${process.env.ATS_BASE_URL}/webhooks/agent-results`
      },
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  }

  async getAuditTrail(applicationId) {
    const response = await axios.get(
      `${this.baseUrl}/api/v1/audit/${applicationId}`,
      {
        headers: { 'Authorization': `Bearer ${this.apiKey}` }
      }
    );
    return response.data;
  }

  async getBiasMetrics(jobId) {
    const response = await axios.get(
      `${this.baseUrl}/api/v1/metrics/bias/${jobId}`,
      {
        headers: { 'Authorization': `Bearer ${this.apiKey}` }
      }
    );
    return response.data;
  }
}

module.exports = new AgentPlatformClient();
```

### Step 3: Trigger Screening on New Applications

```javascript
// In your application submission handler
const agentPlatform = require('./services/agentPlatform');

async function handleNewApplication(application) {
  const job = await db.jobs.findById(application.job_id);
  const candidate = await db.candidates.findById(application.candidate_id);

  // Extract requirements (no PII)
  const jobReqs = {
    skills: job.required_skills,
    experience_min: job.experience_years_min,
    education: job.education_requirements
  };

  // Extract profile (no PII - use hashed identifier)
  const candidateProfile = {
    skills: candidate.skills,
    experience_years: candidate.experience_years,
    education_level: candidate.education_level,
    resume_vector: candidate.resume_embedding
  };

  // Send to agent platform
  const result = await agentPlatform.screenCandidate(
    application.job_id,
    candidate.hashed_id,  // Never send real email/name
    application.id,
    jobReqs,
    candidateProfile
  );

  // Update application status
  await db.applications.update({
    where: { id: application.id },
    data: {
      status: 'agent_processing',
      agent_request_id: result.request_id
    }
  });
}
```

---

## Environment Variables Required

### In your ATS (.env):
```bash
# Agent Platform Connection
AGENT_PLATFORM_URL=https://api.defensiblehiringai.com
AGENT_PLATFORM_API_KEY=your_api_key_here
WEBHOOK_SECRET=your_webhook_secret_here

# Your ATS Base URL (for callbacks)
ATS_BASE_URL=https://your-ats-domain.com
```

### In Agent Platform (.env):
```bash
# ATS Integration
ATS_API_URL=https://your-ats-domain.com/api
ATS_API_KEY=your_ats_api_key
ATS_WEBHOOK_SECRET=matching_webhook_secret
```

---

## Database Schema Additions for ATS

Add these columns to your existing tables:

```sql
-- Add to applications table
ALTER TABLE applications ADD COLUMN agent_score INTEGER;
ALTER TABLE applications ADD COLUMN agent_reasoning TEXT;
ALTER TABLE applications ADD COLUMN agent_recommendation VARCHAR(50);
ALTER TABLE applications ADD COLUMN audit_id VARCHAR(100);
ALTER TABLE applications ADD COLUMN agent_request_id VARCHAR(100);

-- Create bias alerts table
CREATE TABLE bias_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES jobs(id),
  metric VARCHAR(50) NOT NULL,
  value DECIMAL(5,4) NOT NULL,
  affected_group VARCHAR(100),
  recommended_action VARCHAR(100),
  resolved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS on new table
ALTER TABLE bias_alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their org alerts" ON bias_alerts
  FOR SELECT USING (auth.uid() IN (
    SELECT user_id FROM organization_members
    WHERE organization_id = (SELECT organization_id FROM jobs WHERE id = bias_alerts.job_id)
  ));
```

---

## Testing the Integration

### 1. Health Check
```bash
curl -X GET https://api.defensiblehiringai.com/health \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 2. Test Screening Request
```bash
curl -X POST https://api.defensiblehiringai.com/api/v1/screen \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "test_job_001",
    "candidate_id": "test_candidate_001",
    "application_id": "test_app_001",
    "job_requirements": {
      "skills": ["Python", "Machine Learning"],
      "experience_min": 3
    },
    "candidate_profile": {
      "skills": ["Python", "TensorFlow", "PyTorch"],
      "experience_years": 5
    },
    "callback_url": "https://your-ats.com/webhooks/agent-results"
  }'
```

### 3. Verify Webhook Receipt
Check your ATS logs for incoming webhook with screening results.

---

## Security Checklist

- [ ] All API calls use HTTPS
- [ ] JWT tokens have short expiry (1 hour)
- [ ] Webhook signatures verified on every request
- [ ] No PII transmitted - only hashed identifiers
- [ ] Rate limiting configured (1000 req/min per client)
- [ ] Audit logs retained for 7 years
- [ ] RLS enabled on all database tables
- [ ] API keys rotated every 90 days

---

## Next Steps

1. **Clone mctf66nf repo** into this environment
2. **Identify existing API routes** in the ATS
3. **Add webhook handlers** as specified above
4. **Configure environment variables**
5. **Test integration** with sandbox credentials
6. **Deploy to production** with monitoring

---

*Document Version: 1.0*
*Last Updated: 2026-02-10*
*Contact: defensiblehiringai.com*
