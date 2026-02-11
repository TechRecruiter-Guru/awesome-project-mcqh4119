# Data Flow: ATS ↔ Agent Platform Connection Map

## The Two Systems

| System | Repo | Purpose |
|--------|------|---------|
| **ATS** | mctf66nf | Stores candidates, jobs, applications - the "database of record" |
| **Agent Platform** | mcqh4119 | AI agents that screen/score candidates - the "brain" |

---

## Current Reality Check ⚠️

Right now, these systems are **NOT automatically connected**. Here's what exists:

### ATS (mctf66nf) Has:
```
✅ Candidates table (with profiles, skills, publications)
✅ Jobs table (with requirements)
✅ Applications table (with scoring fields ready)
✅ Webhook endpoints (just added - ready to receive)
✅ AI Matching endpoint (/api/jobs/{id}/match-candidates)
```

### Agent Platform (mcqh4119) Has:
```
✅ Agent architecture designed
✅ Whitepaper & documentation
✅ Frontend demo
❌ NO backend that actually calls the ATS
❌ NO live agent processing
```

---

## How It SHOULD Flow (The Vision)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ATS (mctf66nf)                                 │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────────────┐ │
│  │  CANDIDATES │    │    JOBS     │    │         APPLICATIONS            │ │
│  │             │    │             │    │                                 │ │
│  │ • Profile   │    │ • Title     │    │ • candidate_id ──────┐         │ │
│  │ • Skills    │    │ • Requires  │    │ • job_id ───────────┐│         │ │
│  │ • Papers    │    │ • Company   │    │ • status ◄──────────┼┼── Agent │ │
│  │ • Scores    │    │             │    │ • technical_score ◄─┼┼── Writes│ │
│  └─────────────┘    └─────────────┘    │ • research_score ◄──┼┼── Here  │ │
│         │                  │           │ • overall_score ◄───┼┼─────────│ │
│         │                  │           │ • notes ◄───────────┘│         │ │
│         └────────┬─────────┘           │ • stage ◄────────────┘         │ │
│                  │                     └─────────────────────────────────┘ │
│                  ▼                                                         │
│         ┌───────────────┐                                                  │
│         │  GET /api/... │ ◄─────────── Agent Platform READS from here     │
│         └───────────────┘                                                  │
│                                                                            │
│         ┌───────────────────────────┐                                      │
│         │ POST /webhooks/agent-results │ ◄── Agent Platform WRITES here   │
│         └───────────────────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT PLATFORM (mcqh4119)                           │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        SCREENING PIPELINE                             │  │
│  │                                                                       │  │
│  │  1. SourcerAgent      2. MatcherAgent     3. ScreenerAgent           │  │
│  │     │                      │                    │                     │  │
│  │     │ Fetches jobs &       │ Compares skills    │ Generates score    │  │
│  │     │ candidates from      │ & requirements     │ & recommendation   │  │
│  │     │ ATS API              │ Calculates 0-100   │                     │  │
│  │     ▼                      ▼                    ▼                     │  │
│  │  GET /api/jobs         Match Logic          Decision:                │  │
│  │  GET /api/candidates                        • advance_to_human_review│  │
│  │                                             • pass                    │  │
│  │                                             • maybe                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         WRITE BACK TO ATS                             │  │
│  │                                                                       │  │
│  │  POST /webhooks/agent-results                                        │  │
│  │  {                                                                    │  │
│  │    "application_id": 123,                                            │  │
│  │    "results": {                                                       │  │
│  │      "technical_score": 85,      ──► Updates Application.technical   │  │
│  │      "research_score": 72,       ──► Updates Application.research    │  │
│  │      "overall_score": 80,        ──► Updates Application.overall     │  │
│  │      "recommendation": "advance", ──► Updates Application.status     │  │
│  │      "reasoning": "Strong match"  ──► Updates Application.notes      │  │
│  │    }                                                                  │  │
│  │  }                                                                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Specific Field Mapping

### Where LEADS Come From:
```
SOURCE                          → DESTINATION
─────────────────────────────────────────────────────────────────
ATS: New Candidate created      → Application with status='applied'
ATS: Boolean Search results     → Candidates added to pipeline
Agent: SourcerAgent finds match → Creates Application in ATS
```

### Where PENDING REVIEW Comes From:
```
TRIGGER                                    → RESULT
─────────────────────────────────────────────────────────────────
Agent sends recommendation='advance'       → Application.status = 'reviewing'
                                          → Application.stage = 'pending_human_review'

Frontend queries:                         → Shows in "Pending Review" tab
  GET /api/applications
  WHERE status='reviewing'
```

### Where SCORES Come From:
```
FIELD                    CALCULATED BY           STORED IN
─────────────────────────────────────────────────────────────────
technical_score          MatcherAgent            Application.technical_score
research_score           Impact calculation      Application.research_score
culture_fit_score        (Future: Interview)     Application.culture_fit_score
overall_score            Weighted average        Application.overall_score
```

---

## The Gap: What's Missing

### Currently NOT Connected:

1. **No Agent Backend Running**
   - The agent platform (mcqh4119) is documentation/frontend only
   - No Python service actually calling the ATS API
   - No screening pipeline executing

2. **No Automatic Trigger**
   - When a new application is created in ATS, nothing triggers the agent
   - Manual trigger needed

3. **Pipeline View Not Populated**
   - ATS has the data structure
   - But no agent is writing to it yet

---

## To Make It Work: Required Connections

### Option A: Agent Platform Calls ATS (Recommended)

```python
# In Agent Platform backend (mcqh4119)

# 1. Fetch from ATS
jobs = requests.get("https://your-ats.com/api/jobs")
candidates = requests.get("https://your-ats.com/api/candidates")

# 2. Run through agents
for job in jobs:
    matches = match_candidates(job, candidates)
    for match in matches:
        scores = screen_candidate(match)

        # 3. Write back to ATS
        requests.post("https://your-ats.com/webhooks/agent-results", {
            "application_id": match.application_id,
            "results": scores
        })
```

### Option B: ATS Calls Agent Platform

```python
# In ATS backend (mctf66nf) - when new application created

@app.route('/api/applications', methods=['POST'])
def create_application():
    # ... create application ...

    # Trigger agent screening
    requests.post("https://agent-platform.com/api/screen", {
        "job_id": application.job_id,
        "candidate_id": application.candidate_id,
        "callback_url": "https://your-ats.com/webhooks/agent-results"
    })
```

---

## Visual: Where Each Piece Lives

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR ATS (mctf66nf)                     │
│                                                                 │
│  DATA STORAGE:                                                  │
│  ├── Candidates (profiles, skills, papers)                     │
│  ├── Jobs (requirements, company)                              │
│  ├── Applications (scores, status, stage) ◄── PIPELINE DATA    │
│  ├── Publications (research papers)                            │
│  ├── BiasAlerts (compliance tracking)                          │
│  └── AgentAuditLog (decision trail)                            │
│                                                                 │
│  API ENDPOINTS:                                                 │
│  ├── GET /api/candidates        (Agent reads)                  │
│  ├── GET /api/jobs              (Agent reads)                  │
│  ├── GET /api/applications      (Frontend reads for pipeline)  │
│  ├── POST /webhooks/agent-results (Agent writes scores)        │
│  └── POST /webhooks/bias-alert    (Agent writes alerts)        │
│                                                                 │
│  FRONTEND VIEWS:                                                │
│  ├── Dashboard (stats + pending alert)                         │
│  ├── Pending Review (candidates needing human review)          │
│  ├── Candidates (all candidates)                               │
│  ├── Jobs (all jobs with AI matching)                          │
│  └── Analytics (pipeline metrics)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    AGENT PLATFORM (mcqh4119)                    │
│                                                                 │
│  AGENTS (Logic/Processing):                                     │
│  ├── SourcerAgent (finds candidates)                           │
│  ├── MatcherAgent (scores match 0-100)                         │
│  ├── ScreenerAgent (makes recommendation)                      │
│  ├── AuditAgent (logs decisions)                               │
│  └── PipelineAgent (orchestrates flow)                         │
│                                                                 │
│  WOULD NEED TO BUILD:                                          │
│  ├── ATSClient service (to call your ATS API)                  │
│  ├── ScreeningPipeline (orchestrate agents)                    │
│  ├── Webhook sender (to push results back)                     │
│  └── Scheduler (to run periodically or on-demand)              │
│                                                                 │
│  FRONTEND (Demo/Showcase):                                      │
│  ├── DefensibleHiring landing page                             │
│  ├── Whitepaper product                                        │
│  └── Agent activity visualization                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Answer: Why You Don't See Data Matching

| Issue | Reason |
|-------|--------|
| Pending Review empty | No agent has written `status='reviewing'` to any application yet |
| Pipeline not populated | Applications exist but no scores written by agent |
| No connection visible | The two repos aren't talking to each other via API yet |

---

## To Connect Them Right Now

### Simplest Test:

```bash
# 1. Start your ATS backend
cd mctf66nf/backend && python app.py

# 2. Manually simulate an agent result
curl -X POST http://localhost:5000/webhooks/agent-results \
  -H "Content-Type: application/json" \
  -d '{
    "event": "screening_complete",
    "application_id": 1,
    "results": {
      "technical_score": 85,
      "research_score": 72,
      "overall_score": 80,
      "recommendation": "advance_to_human_review",
      "reasoning": "Strong technical match with required skills"
    }
  }'

# 3. Check Pending Review tab - should now show the candidate!
```

This will populate the Pending Review with real data.

---

## Summary

| What | Where It Lives | How It Gets There |
|------|---------------|-------------------|
| Candidate profiles | ATS.candidates | Manual entry / enrichment APIs |
| Job requirements | ATS.jobs | Manual entry |
| Applications | ATS.applications | Created when candidate applies |
| **Agent Scores** | ATS.applications | **Agent writes via webhook** |
| **Pending Review** | ATS.applications | **Where status='reviewing'** |
| Agent logic | Agent Platform | Runs screening pipeline |
| Audit trail | ATS.agent_audit_log | Agent writes via webhook |

The **connection point** is the webhook: `POST /webhooks/agent-results`

Without an agent actually calling that webhook, no scores appear in your ATS.
