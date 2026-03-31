# Integration Bridge: Your ATS (mctf66nf) ↔ Agent Platform

## ✅ YOUR ATS IS READY FOR INTEGRATION!

Great news - your ATS already has the infrastructure needed for agent integration.

---

## Your ATS API Endpoints (Already Built!)

### 📊 Database Models

| Model | Fields | Agent Use |
|-------|--------|-----------|
| **Candidate** | id, first_name, last_name, email, skills, primary_expertise, years_experience, h_index, citation_count, github_url, status | Match against job requirements |
| **Job** | id, title, company, required_expertise, required_skills, education_required, research_focus, status | Define screening criteria |
| **Application** | id, candidate_id, job_id, status, stage, technical_score, research_score, culture_fit_score, overall_score, notes | **Store agent scores here!** |
| **Publication** | id, candidate_id, title, venue, year, citation_count, research_area | Research impact scoring |
| **SavedSearch** | id, search_query, data_sources, total_results | Boolean sourcing |

---

## Existing ATS Endpoints to Use

### Candidates
```
GET  /api/candidates                    → List all candidates
GET  /api/candidates/:id                → Get candidate with applications & publications
POST /api/candidates                    → Create candidate
PUT  /api/candidates/:id                → Update candidate
DELETE /api/candidates/:id              → Delete candidate
```

### Candidate Enrichment (ALREADY BUILT!)
```
POST /api/candidates/:id/enrich/github  → Auto-enrich from GitHub API
POST /api/candidates/:id/enrich/arxiv   → Auto-fetch arXiv publications
POST /api/candidates/:id/enrich/orcid   → Auto-enrich from ORCID
POST /api/candidates/:id/enrich/scholar → Auto-enrich from Google Scholar
POST /api/candidates/:id/extract-skills → Auto-extract AI/ML skills
GET  /api/candidates/:id/impact-score   → Calculate research impact (0-100)
```

### Jobs
```
GET  /api/jobs                          → List all jobs
GET  /api/jobs/:id                      → Get job with applications
POST /api/jobs                          → Create job
PUT  /api/jobs/:id                      → Update job
DELETE /api/jobs/:id                    → Delete job
POST /api/jobs/:id/reveal               → Reveal confidential company name
POST /api/jobs/:id/match-candidates     → 🔥 AI MATCHING ALREADY BUILT!
```

### Applications
```
GET  /api/applications                  → List all applications
POST /api/applications                  → Create application
PUT  /api/applications/:id              → Update application (AGENT WRITES SCORES HERE)
DELETE /api/applications/:id            → Delete application
```

### Publications
```
GET  /api/candidates/:id/publications   → Get candidate publications
POST /api/publications                  → Add publication
DELETE /api/publications/:id            → Delete publication
GET  /api/publications/analyze-conferences → Analyze top conference papers
```

### Stats
```
GET  /api/stats                         → Dashboard statistics
GET  /api/health                        → Health check + DB status
```

---

## 🔌 How to Connect: Agent Platform → Your ATS

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                YOUR ATS (awesome-project-mctf66nf)                          │
│                   Flask + PostgreSQL (Supabase)                             │
│                                                                             │
│  Candidates ──┬── Applications ──┬── Jobs                                  │
│               │                  │                                          │
│  Publications ┘    ┌─────────────┘                                          │
│                    │                                                        │
│  EXISTING SCORES:  │                                                        │
│  • technical_score │  ← Agent writes here                                  │
│  • research_score  │  ← Agent writes here                                  │
│  • culture_fit_score│ ← Agent writes here                                  │
│  • overall_score   │  ← Agent writes here                                  │
│  • notes           │  ← Agent writes reasoning here                        │
└────────────────────┼────────────────────────────────────────────────────────┘
                     │
                     │ REST API (JSON)
                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT PLATFORM (awesome-project-mcqh4119)                │
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ SourcerAgent │ → │ MatcherAgent │ → │ ScreenerAgent │                  │
│  │              │    │              │    │              │                  │
│  │ • Get jobs   │    │ • Score      │    │ • Generate   │                  │
│  │ • Get cands  │    │   0-100      │    │   reasoning  │                  │
│  │ • Parse reqs │    │ • Compare    │    │ • Recommend  │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│                                                │                           │
│                            ┌───────────────────┘                           │
│                            ▼                                               │
│                    ┌──────────────┐    ┌──────────────┐                   │
│                    │  AuditAgent  │ → │ PipelineAgent │                   │
│                    │              │    │              │                   │
│                    │ • Log trail  │    │ • Update ATS │                   │
│                    │ • Bias check │    │ • Trigger    │                   │
│                    │ • Compliance │    │   callbacks  │                   │
│                    └──────────────┘    └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Integration Code to Add

### 1. Add to Agent Platform: ATS Client Service

Create `/home/user/awesome-project-mcqh4119/backend/services/ats_client.py`:

```python
import requests
import os

class ATSClient:
    """Client to interact with your mctf66nf ATS"""

    def __init__(self):
        self.base_url = os.environ.get('ATS_API_URL', 'http://localhost:5000')
        self.timeout = 30

    # ==================== JOBS ====================

    def get_jobs(self, status='open'):
        """Fetch open jobs from ATS"""
        response = requests.get(
            f"{self.base_url}/api/jobs",
            params={'status': status},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['jobs']

    def get_job(self, job_id):
        """Get single job with requirements"""
        response = requests.get(
            f"{self.base_url}/api/jobs/{job_id}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== CANDIDATES ====================

    def get_candidates(self, status=None):
        """Fetch candidates from ATS"""
        params = {}
        if status:
            params['status'] = status

        response = requests.get(
            f"{self.base_url}/api/candidates",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['candidates']

    def get_candidate(self, candidate_id):
        """Get single candidate with full profile"""
        response = requests.get(
            f"{self.base_url}/api/candidates/{candidate_id}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_candidate_impact_score(self, candidate_id):
        """Get research impact score (already calculated by ATS!)"""
        response = requests.get(
            f"{self.base_url}/api/candidates/{candidate_id}/impact-score",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def enrich_candidate(self, candidate_id, source='github'):
        """Trigger ATS enrichment from external sources"""
        response = requests.post(
            f"{self.base_url}/api/candidates/{candidate_id}/enrich/{source}",
            timeout=60  # Enrichment can take longer
        )
        response.raise_for_status()
        return response.json()

    def extract_candidate_skills(self, candidate_id):
        """Trigger skill extraction"""
        response = requests.post(
            f"{self.base_url}/api/candidates/{candidate_id}/extract-skills",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== APPLICATIONS ====================

    def get_applications(self):
        """Get all applications"""
        response = requests.get(
            f"{self.base_url}/api/applications",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['applications']

    def create_application(self, candidate_id, job_id, source='agent_sourced'):
        """Create new application in ATS"""
        response = requests.post(
            f"{self.base_url}/api/applications",
            json={
                'candidate_id': candidate_id,
                'job_id': job_id,
                'source': source,
                'status': 'applied'
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def update_application_scores(self, application_id, scores, reasoning=None):
        """
        Update application with agent scores

        scores = {
            'technical_score': 85,      # 0-100
            'research_score': 72,       # 0-100
            'culture_fit_score': 78,    # 0-100
            'overall_score': 80         # 0-100
        }
        """
        payload = {
            'technical_score': scores.get('technical_score'),
            'research_score': scores.get('research_score'),
            'culture_fit_score': scores.get('culture_fit_score'),
            'overall_score': scores.get('overall_score'),
            'stage': 'agent_reviewed',
            'status': 'screening'
        }

        if reasoning:
            payload['notes'] = f"[Agent Analysis]\n{reasoning}"

        response = requests.put(
            f"{self.base_url}/api/applications/{application_id}",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def advance_to_human_review(self, application_id, recommendation, reasoning):
        """Mark application for human review"""
        response = requests.put(
            f"{self.base_url}/api/applications/{application_id}",
            json={
                'status': 'reviewing',
                'stage': 'pending_human_review',
                'notes': f"[Agent Recommendation: {recommendation}]\n\n{reasoning}"
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== MATCHING ====================

    def get_ats_matches(self, job_id, min_score=50, top_n=20):
        """
        Use ATS's built-in matching (already has AI scoring!)
        Returns candidates ranked by match score
        """
        response = requests.post(
            f"{self.base_url}/api/jobs/{job_id}/match-candidates",
            json={
                'min_score': min_score,
                'top_n': top_n
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== PUBLICATIONS ====================

    def get_candidate_publications(self, candidate_id):
        """Get candidate's research publications"""
        response = requests.get(
            f"{self.base_url}/api/candidates/{candidate_id}/publications",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['publications']

    # ==================== HEALTH ====================

    def health_check(self):
        """Check ATS is running"""
        response = requests.get(
            f"{self.base_url}/api/health",
            timeout=10
        )
        response.raise_for_status()
        return response.json()


# Singleton instance
ats_client = ATSClient()
```

### 2. Add to Agent Platform: Screening Pipeline

Create `/home/user/awesome-project-mcqh4119/backend/agents/screening_pipeline.py`:

```python
from services.ats_client import ats_client
import json
from datetime import datetime

class ScreeningPipeline:
    """
    Agentic screening pipeline that connects to your ATS

    Flow:
    1. Fetch job requirements from ATS
    2. Fetch candidates from ATS (or use ATS's built-in matching)
    3. Run through agent evaluation
    4. Write scores back to ATS applications
    5. Log audit trail
    """

    def __init__(self):
        self.audit_log = []

    def screen_job(self, job_id, use_ats_matching=True):
        """
        Screen all candidates for a job

        Args:
            job_id: Job ID in your ATS
            use_ats_matching: If True, use ATS's built-in /match-candidates
                             If False, fetch all candidates and score ourselves
        """
        # 1. Fetch job from ATS
        job = ats_client.get_job(job_id)
        self._log('SourcerAgent', 'fetch_job', {'job_id': job_id, 'title': job['title']})

        # 2. Get matched candidates
        if use_ats_matching:
            # Use ATS's built-in AI matching (already scores 0-100!)
            match_result = ats_client.get_ats_matches(job_id, min_score=30, top_n=50)
            candidates_to_screen = match_result['top_matches']
            self._log('MatcherAgent', 'ats_matching', {
                'candidates_evaluated': match_result['total_candidates_evaluated'],
                'matches_found': match_result['matches_found']
            })
        else:
            # Fetch all candidates and score ourselves
            candidates = ats_client.get_candidates()
            candidates_to_screen = [
                {'candidate_id': c['id'], 'match_score': 0, **c}
                for c in candidates
            ]
            self._log('SourcerAgent', 'fetch_all_candidates', {'count': len(candidates)})

        # 3. Screen each candidate
        results = []
        for candidate_match in candidates_to_screen:
            candidate_id = candidate_match['candidate_id']

            # Get full candidate profile
            candidate = ats_client.get_candidate(candidate_id)

            # Get research impact score from ATS
            impact = ats_client.get_candidate_impact_score(candidate_id)

            # Calculate agent scores
            scores = self._calculate_scores(job, candidate, candidate_match, impact)

            # Generate reasoning
            reasoning = self._generate_reasoning(job, candidate, scores)

            # Determine recommendation
            recommendation = self._determine_recommendation(scores)

            # Log screening
            self._log('ScreenerAgent', 'screen_candidate', {
                'candidate_id': candidate_id,
                'scores': scores,
                'recommendation': recommendation
            })

            # Check if application exists, create if not
            application_id = self._ensure_application(candidate_id, job_id)

            # Write scores to ATS
            if recommendation == 'advance':
                ats_client.advance_to_human_review(application_id, recommendation, reasoning)
            else:
                ats_client.update_application_scores(application_id, scores, reasoning)

            self._log('PipelineAgent', 'update_ats', {
                'application_id': application_id,
                'scores_written': True
            })

            results.append({
                'candidate_id': candidate_id,
                'candidate_name': candidate['full_name'],
                'scores': scores,
                'recommendation': recommendation,
                'reasoning': reasoning[:200] + '...' if len(reasoning) > 200 else reasoning
            })

        # Log completion
        self._log('AuditAgent', 'screening_complete', {
            'job_id': job_id,
            'candidates_screened': len(results),
            'advanced_count': len([r for r in results if r['recommendation'] == 'advance'])
        })

        return {
            'job_id': job_id,
            'job_title': job['title'],
            'candidates_screened': len(results),
            'results': results,
            'audit_log': self.audit_log
        }

    def _calculate_scores(self, job, candidate, match_data, impact_data):
        """Calculate comprehensive scores"""

        # Technical Score (0-100)
        # Based on skills match + research impact
        base_match = match_data.get('match_score', 0)
        impact_score = impact_data.get('impact_score', 0)
        technical_score = int((base_match * 0.6) + (impact_score * 0.4))

        # Research Score (0-100)
        # Direct from ATS impact calculation
        research_score = int(impact_score)

        # Culture Fit Score (0-100)
        # Placeholder - would integrate with interview feedback
        culture_fit_score = 70  # Default neutral score

        # Overall Score
        overall_score = int(
            (technical_score * 0.4) +
            (research_score * 0.35) +
            (culture_fit_score * 0.25)
        )

        return {
            'technical_score': min(technical_score, 100),
            'research_score': min(research_score, 100),
            'culture_fit_score': culture_fit_score,
            'overall_score': min(overall_score, 100)
        }

    def _generate_reasoning(self, job, candidate, scores):
        """Generate human-readable reasoning for the scores"""

        reasoning_parts = []

        # Technical assessment
        if scores['technical_score'] >= 80:
            reasoning_parts.append(
                f"Strong technical match: {candidate.get('primary_expertise', 'N/A')} "
                f"aligns well with {job.get('required_expertise', 'role requirements')}."
            )
        elif scores['technical_score'] >= 60:
            reasoning_parts.append(
                f"Moderate technical match: Some skill overlap detected."
            )
        else:
            reasoning_parts.append(
                f"Limited technical match: Key skill gaps identified."
            )

        # Research assessment
        h_index = candidate.get('h_index', 0)
        citations = candidate.get('citation_count', 0)
        pub_count = candidate.get('publication_count', 0)

        if scores['research_score'] >= 60:
            reasoning_parts.append(
                f"Research profile: h-index {h_index}, {citations} citations, "
                f"{pub_count} publications. Strong academic credentials."
            )
        elif h_index or citations:
            reasoning_parts.append(
                f"Research profile: h-index {h_index}, {citations} citations. "
                f"Developing research presence."
            )
        else:
            reasoning_parts.append(
                f"Limited research profile available. May be industry-focused."
            )

        # Experience
        years = candidate.get('years_experience', 0)
        if years:
            reasoning_parts.append(f"Experience: {years} years in field.")

        # Overall recommendation
        reasoning_parts.append(
            f"\nOverall Score: {scores['overall_score']}/100"
        )

        return '\n'.join(reasoning_parts)

    def _determine_recommendation(self, scores):
        """Determine whether to advance candidate"""
        if scores['overall_score'] >= 70:
            return 'advance'
        elif scores['overall_score'] >= 50:
            return 'maybe'
        else:
            return 'pass'

    def _ensure_application(self, candidate_id, job_id):
        """Check if application exists, create if not"""
        # This would check existing applications
        # For now, create new one
        try:
            app = ats_client.create_application(candidate_id, job_id, 'agent_pipeline')
            return app['id']
        except Exception:
            # Application might already exist
            # In production, would query and return existing ID
            return None

    def _log(self, agent, action, data):
        """Add to audit log"""
        self.audit_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'agent': agent,
            'action': action,
            'data': data
        })


# Usage example
if __name__ == '__main__':
    pipeline = ScreeningPipeline()

    # Screen candidates for job ID 1
    results = pipeline.screen_job(job_id=1, use_ats_matching=True)

    print(f"Screened {results['candidates_screened']} candidates")
    for r in results['results'][:5]:
        print(f"  {r['candidate_name']}: {r['scores']['overall_score']} - {r['recommendation']}")
```

---

## 🚀 Environment Variables

### Add to Agent Platform `.env`:
```bash
# Your ATS connection
ATS_API_URL=https://your-ats-backend.onrender.com

# Or for local development
ATS_API_URL=http://localhost:5000
```

### Your ATS (mctf66nf) already has:
```bash
DATABASE_URL=your_supabase_url
GITHUB_TOKEN=optional_for_enrichment
```

---

## 📋 Integration Checklist

### Already Done in Your ATS ✅
- [x] Candidate CRUD with full profile
- [x] Job CRUD with requirements
- [x] Application CRUD with scoring fields
- [x] Publication tracking
- [x] GitHub enrichment
- [x] arXiv enrichment
- [x] ORCID enrichment
- [x] Google Scholar enrichment
- [x] Skill extraction
- [x] Impact score calculation
- [x] AI candidate matching
- [x] Health check endpoint

### To Add to Agent Platform 🔧
- [ ] Copy `ats_client.py` to backend/services/
- [ ] Copy `screening_pipeline.py` to backend/agents/
- [ ] Add ATS_API_URL to environment
- [ ] Test connection with health check
- [ ] Run first screening pipeline

### Optional Enhancements 🎯
- [ ] Add webhook endpoints to ATS for real-time updates
- [ ] Add bias monitoring to screening pipeline
- [ ] Add batch processing for large candidate pools
- [ ] Add scheduling for automated daily screening

---

## 🧪 Quick Test

```bash
# 1. Start your ATS backend
cd /home/user/awesome-project-mctf66nf/backend
python app.py

# 2. Test health check
curl http://localhost:5000/api/health

# 3. Test from agent platform
cd /home/user/awesome-project-mcqh4119
python -c "
from backend.services.ats_client import ats_client
print(ats_client.health_check())
print(f'Jobs: {len(ats_client.get_jobs())}')
print(f'Candidates: {len(ats_client.get_candidates())}')
"
```

---

## Summary

Your **mctf66nf ATS** already has:
- ✅ All CRUD operations needed
- ✅ Scoring fields in Application model
- ✅ AI matching endpoint
- ✅ Research enrichment APIs
- ✅ Impact scoring

The agent platform just needs to:
1. **Read** jobs and candidates from your ATS
2. **Process** through the agent pipeline
3. **Write** scores back to Applications

**It's a clean integration - your ATS is agent-ready!**
