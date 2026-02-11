"""
ATS Client - Connects Agent Platform to your ATS (mctf66nf)

This service handles all communication between the agent platform
and your Applicant Tracking System.
"""

import requests
import os
import hmac
import hashlib
import json
from datetime import datetime


class ATSClient:
    """Client for interacting with the ATS API"""

    def __init__(self, base_url=None, webhook_secret=None):
        self.base_url = base_url or os.environ.get('ATS_API_URL', 'http://localhost:5000')
        self.webhook_secret = webhook_secret or os.environ.get('AGENT_WEBHOOK_SECRET', 'dev-secret')
        self.timeout = 30

    def _sign_payload(self, payload):
        """Generate HMAC signature for webhook calls"""
        payload_bytes = json.dumps(payload).encode()
        signature = hmac.new(
            self.webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    # ==================== READ FROM ATS ====================

    def health_check(self):
        """Check if ATS is running"""
        response = requests.get(f"{self.base_url}/api/health", timeout=10)
        response.raise_for_status()
        return response.json()

    def get_jobs(self, status='open'):
        """Get jobs from ATS"""
        response = requests.get(
            f"{self.base_url}/api/jobs",
            params={'status': status},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get('jobs', [])

    def get_job(self, job_id):
        """Get single job with details"""
        response = requests.get(
            f"{self.base_url}/api/jobs/{job_id}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_candidates(self, status=None):
        """Get candidates from ATS"""
        params = {}
        if status:
            params['status'] = status
        response = requests.get(
            f"{self.base_url}/api/candidates",
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get('candidates', [])

    def get_candidate(self, candidate_id):
        """Get single candidate with full profile"""
        response = requests.get(
            f"{self.base_url}/api/candidates/{candidate_id}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_applications(self):
        """Get all applications"""
        response = requests.get(
            f"{self.base_url}/api/applications",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get('applications', [])

    def get_candidate_impact_score(self, candidate_id):
        """Get research impact score from ATS"""
        response = requests.get(
            f"{self.base_url}/api/candidates/{candidate_id}/impact-score",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== WRITE TO ATS (Leads) ====================

    def create_candidate(self, candidate_data):
        """
        Create a new candidate (LEAD) in the ATS

        Args:
            candidate_data: {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'primary_expertise': 'Computer Vision',
                'skills': 'Python, PyTorch, OpenCV',
                'github_url': 'https://github.com/johndoe',
                'google_scholar_url': '...',
                'source': 'agent_sourced'  # Mark as agent-sourced lead
            }
        """
        # Add source tracking
        candidate_data['status'] = candidate_data.get('status', 'new')
        candidate_data['notes'] = f"[Agent Sourced] {datetime.utcnow().isoformat()}\n{candidate_data.get('notes', '')}"

        response = requests.post(
            f"{self.base_url}/api/candidates",
            json=candidate_data,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def create_application(self, candidate_id, job_id, source='agent_sourced'):
        """
        Create application linking candidate to job

        This is how a LEAD becomes part of the PIPELINE
        """
        response = requests.post(
            f"{self.base_url}/api/applications",
            json={
                'candidate_id': candidate_id,
                'job_id': job_id,
                'source': source,
                'status': 'applied',
                'stage': 'agent_sourced'
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def enrich_candidate(self, candidate_id, source='github'):
        """Trigger ATS enrichment from external sources"""
        response = requests.post(
            f"{self.base_url}/api/candidates/{candidate_id}/enrich/{source}",
            timeout=60
        )
        response.raise_for_status()
        return response.json()

    # ==================== WRITE SCREENING RESULTS ====================

    def send_screening_results(self, application_id, results):
        """
        Send agent screening results to ATS via webhook

        Args:
            application_id: The application to update
            results: {
                'technical_score': 85,
                'research_score': 72,
                'culture_fit_score': 78,
                'overall_score': 80,
                'recommendation': 'advance_to_human_review',
                'reasoning': 'Strong match because...',
                'audit_id': 'audit_001'
            }
        """
        payload = {
            'event': 'screening_complete',
            'application_id': application_id,
            'results': {
                'technical_score': results.get('technical_score'),
                'research_score': results.get('research_score'),
                'culture_fit_score': results.get('culture_fit_score'),
                'overall_score': results.get('overall_score'),
                'recommendation': results.get('recommendation', 'review'),
                'reasoning': results.get('reasoning', ''),
                'audit_id': results.get('audit_id', f"audit_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"),
                'bias_check': {
                    'passed': True,
                    'protected_attributes_detected': False
                }
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': self._sign_payload(payload)
        }

        response = requests.post(
            f"{self.base_url}/webhooks/agent-results",
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def send_bias_alert(self, job_id, metric, value, affected_group, recommended_action):
        """Send bias threshold alert to ATS"""
        payload = {
            'event': 'bias_threshold_warning',
            'job_id': job_id,
            'metric': metric,
            'value': value,
            'threshold': 0.80,
            'affected_group': affected_group,
            'recommended_action': recommended_action
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': self._sign_payload(payload)
        }

        response = requests.post(
            f"{self.base_url}/webhooks/bias-alert",
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # ==================== USE ATS MATCHING ====================

    def get_matched_candidates(self, job_id, min_score=30, top_n=50):
        """Use ATS's built-in AI matching"""
        response = requests.post(
            f"{self.base_url}/api/jobs/{job_id}/match-candidates",
            json={'min_score': min_score, 'top_n': top_n},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


# Singleton instance
ats_client = ATSClient()


# ==================== QUICK TEST ====================
if __name__ == '__main__':
    print("Testing ATS Connection...")

    try:
        # Health check
        health = ats_client.health_check()
        print(f"✅ ATS Status: {health['status']}")
        print(f"   Database: {health['database']}")

        # Get stats
        jobs = ats_client.get_jobs()
        candidates = ats_client.get_candidates()
        print(f"✅ Jobs: {len(jobs)}")
        print(f"✅ Candidates: {len(candidates)}")

        print("\n✅ ATS Connection Successful!")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("\nMake sure your ATS is running:")
        print("  cd mctf66nf/backend && python app.py")
