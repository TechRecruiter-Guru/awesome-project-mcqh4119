"""
SourcerAgent - Finds and creates leads in the ATS

This agent:
1. Searches external sources (GitHub, arXiv, etc.) for candidates
2. Creates candidate records (LEADS) in the ATS
3. Links candidates to matching jobs (PIPELINE)
4. Triggers enrichment from external APIs
"""

import os
import sys
import requests
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ats_client import ats_client


class SourcerAgent:
    """Agent that sources candidates and creates leads in ATS"""

    def __init__(self):
        self.ats = ats_client
        self.audit_log = []

    def _log(self, action, data):
        """Log agent action"""
        self.audit_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'agent': 'SourcerAgent',
            'action': action,
            'data': data
        })
        print(f"[SourcerAgent] {action}: {data}")

    def search_github_for_candidates(self, skills, location=None, min_repos=5, max_results=10):
        """Search GitHub for potential candidates based on skills"""
        self._log('search_github', {'skills': skills, 'location': location})

        query_parts = []
        for skill in skills[:3]:
            query_parts.append(f"language:{skill}")
        if location:
            query_parts.append(f"location:{location}")
        query_parts.append(f"repos:>{min_repos}")
        query = ' '.join(query_parts)

        headers = {'Accept': 'application/vnd.github.v3+json'}
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'

        try:
            response = requests.get(
                'https://api.github.com/search/users',
                params={'q': query, 'per_page': max_results},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                users = response.json().get('items', [])
                self._log('github_results', {'count': len(users)})
                return users
            return []
        except Exception as e:
            self._log('github_error', {'error': str(e)})
            return []

    def create_lead_from_github(self, github_user, job_id=None):
        """Create a candidate lead in ATS from GitHub profile"""
        username = github_user.get('login')
        self._log('create_lead', {'github_user': username})

        headers = {'Accept': 'application/vnd.github.v3+json'}
        github_token = os.environ.get('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'

        try:
            profile_response = requests.get(
                f"https://api.github.com/users/{username}",
                headers=headers, timeout=15
            )
            if profile_response.status_code != 200:
                return None

            profile = profile_response.json()
            full_name = profile.get('name', username) or username
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            candidate_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': profile.get('email') or f"{username}@github.sourced",
                'github_url': profile.get('html_url'),
                'location': profile.get('location'),
                'company': profile.get('company'),
                'bio': profile.get('bio'),
                'primary_expertise': 'Software Engineering',
                'status': 'new',
                'notes': f"Sourced from GitHub\nFollowers: {profile.get('followers', 0)}\nRepos: {profile.get('public_repos', 0)}"
            }

            candidate = self.ats.create_candidate(candidate_data)
            self._log('lead_created', {'candidate_id': candidate.get('id'), 'name': full_name})

            try:
                self.ats.enrich_candidate(candidate['id'], 'github')
            except:
                pass

            if job_id:
                application = self.ats.create_application(candidate['id'], job_id, 'github_sourced')
                return {'candidate': candidate, 'application': application}

            return {'candidate': candidate, 'application': None}
        except Exception as e:
            self._log('error', {'error': str(e)})
            return None

    def source_for_job(self, job_id, max_leads=10):
        """Source candidates for a specific job - main entry point"""
        self._log('source_for_job', {'job_id': job_id})

        job = self.ats.get_job(job_id)
        self._log('job_loaded', {'title': job.get('title')})

        leads_created = []
        skills = []
        if job.get('required_skills'):
            skills = [s.strip().lower() for s in job['required_skills'].split(',')]
        if not skills:
            skills = ['python', 'machine-learning']

        github_users = self.search_github_for_candidates(skills[:3], max_results=max_leads)
        for user in github_users:
            result = self.create_lead_from_github(user, job_id)
            if result:
                leads_created.append(result)

        self._log('sourcing_complete', {'leads_created': len(leads_created)})
        return {'job': job, 'leads_created': len(leads_created), 'leads': leads_created}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SourcerAgent - Find and create leads')
    parser.add_argument('--job-id', type=int, help='Job ID to source for')
    parser.add_argument('--max-leads', type=int, default=10)
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    agent = SourcerAgent()

    if args.test:
        print("Testing ATS Connection...")
        health = agent.ats.health_check()
        print(f"✅ ATS: {health['status']}")
        jobs = agent.ats.get_jobs()
        print(f"✅ Jobs: {len(jobs)}")
    elif args.job_id:
        result = agent.source_for_job(args.job_id, args.max_leads)
        print(f"✅ Created {result['leads_created']} leads")
    else:
        print("Usage: python sourcer_agent.py --job-id 1")
