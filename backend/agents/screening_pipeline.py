"""
Screening Pipeline - Scores candidates and writes to ATS

This is the main orchestrator that:
1. Fetches candidates/applications from ATS
2. Runs them through scoring logic
3. Writes scores back to ATS via webhook
4. Updates pipeline status (Pending Review, etc.)
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.ats_client import ats_client


class ScreeningPipeline:
    """Orchestrates the full screening flow"""

    def __init__(self):
        self.ats = ats_client
        self.audit_log = []

    def _log(self, agent, action, data):
        self.audit_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'agent': agent,
            'action': action,
            'data': data
        })
        print(f"[{agent}] {action}")

    def calculate_scores(self, job, candidate, impact_data=None):
        """Calculate screening scores for a candidate"""
        scores = {
            'technical_score': 50,
            'research_score': 50,
            'culture_fit_score': 70,
            'overall_score': 50
        }

        # Technical Score (based on skills match)
        if job.get('required_skills') and candidate.get('skills'):
            job_skills = set(s.strip().lower() for s in job['required_skills'].split(','))
            cand_skills = set(s.strip().lower() for s in candidate['skills'].split(','))
            overlap = len(job_skills.intersection(cand_skills))
            total = len(job_skills) if job_skills else 1
            scores['technical_score'] = min(int((overlap / total) * 100), 100)

        # Research Score (from impact data or h-index)
        if impact_data:
            scores['research_score'] = int(impact_data.get('impact_score', 50))
        elif candidate.get('h_index'):
            scores['research_score'] = min(candidate['h_index'] * 5, 100)
        elif candidate.get('citation_count'):
            scores['research_score'] = min(int(candidate['citation_count'] / 100), 100)

        # Overall Score
        scores['overall_score'] = int(
            (scores['technical_score'] * 0.4) +
            (scores['research_score'] * 0.35) +
            (scores['culture_fit_score'] * 0.25)
        )

        return scores

    def generate_reasoning(self, job, candidate, scores):
        """Generate human-readable reasoning"""
        parts = []

        if scores['technical_score'] >= 70:
            parts.append(f"Strong technical match ({scores['technical_score']}/100)")
        elif scores['technical_score'] >= 50:
            parts.append(f"Moderate technical fit ({scores['technical_score']}/100)")
        else:
            parts.append(f"Technical gaps identified ({scores['technical_score']}/100)")

        if scores['research_score'] >= 70:
            parts.append(f"Strong research profile ({scores['research_score']}/100)")

        if candidate.get('h_index'):
            parts.append(f"H-index: {candidate['h_index']}")
        if candidate.get('citation_count'):
            parts.append(f"Citations: {candidate['citation_count']}")

        parts.append(f"Overall: {scores['overall_score']}/100")

        return '\n'.join(parts)

    def determine_recommendation(self, scores):
        """Determine recommendation based on scores"""
        if scores['overall_score'] >= 70:
            return 'advance_to_human_review'
        elif scores['overall_score'] >= 50:
            return 'maybe'
        else:
            return 'pass'

    def screen_application(self, application_id):
        """Screen a single application and write results to ATS"""
        self._log('ScreenerAgent', 'screen_application', {'app_id': application_id})

        # Get application details
        applications = self.ats.get_applications()
        application = next((a for a in applications if a['id'] == application_id), None)

        if not application:
            return {'error': 'Application not found'}

        # Get job and candidate
        job = self.ats.get_job(application['job_id'])
        candidate = self.ats.get_candidate(application['candidate_id'])

        # Get impact score
        impact_data = None
        try:
            impact_data = self.ats.get_candidate_impact_score(application['candidate_id'])
        except:
            pass

        # Calculate scores
        scores = self.calculate_scores(job, candidate, impact_data)
        reasoning = self.generate_reasoning(job, candidate, scores)
        recommendation = self.determine_recommendation(scores)

        self._log('MatcherAgent', 'scores_calculated', scores)
        self._log('ScreenerAgent', 'recommendation', {'rec': recommendation})

        # Send results to ATS
        result = self.ats.send_screening_results(application_id, {
            'technical_score': scores['technical_score'],
            'research_score': scores['research_score'],
            'culture_fit_score': scores['culture_fit_score'],
            'overall_score': scores['overall_score'],
            'recommendation': recommendation,
            'reasoning': reasoning
        })

        self._log('PipelineAgent', 'results_sent', {'status': 'success'})

        return {
            'application_id': application_id,
            'candidate_name': candidate.get('full_name'),
            'job_title': job.get('title'),
            'scores': scores,
            'recommendation': recommendation,
            'ats_response': result
        }

    def screen_job(self, job_id):
        """Screen all pending applications for a job"""
        self._log('PipelineAgent', 'screen_job', {'job_id': job_id})

        job = self.ats.get_job(job_id)
        applications = self.ats.get_applications()

        # Filter for this job, pending screening
        pending = [a for a in applications 
                   if a['job_id'] == job_id 
                   and a['status'] in ('applied', 'new', 'screening')]

        self._log('PipelineAgent', 'pending_found', {'count': len(pending)})

        results = []
        for app in pending:
            result = self.screen_application(app['id'])
            results.append(result)

        advanced = len([r for r in results if r.get('recommendation') == 'advance_to_human_review'])

        self._log('PipelineAgent', 'screening_complete', {
            'total': len(results),
            'advanced': advanced
        })

        return {
            'job': job,
            'screened': len(results),
            'advanced_to_review': advanced,
            'results': results
        }

    def screen_all_pending(self):
        """Screen all pending applications across all jobs"""
        self._log('PipelineAgent', 'screen_all', {})

        applications = self.ats.get_applications()
        pending = [a for a in applications 
                   if a['status'] in ('applied', 'new', 'agent_sourced')]

        self._log('PipelineAgent', 'total_pending', {'count': len(pending)})

        results = []
        for app in pending:
            result = self.screen_application(app['id'])
            results.append(result)

        return {
            'total_screened': len(results),
            'results': results
        }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Screening Pipeline')
    parser.add_argument('--job-id', type=int, help='Screen applications for a job')
    parser.add_argument('--application-id', type=int, help='Screen single application')
    parser.add_argument('--all', action='store_true', help='Screen all pending')
    parser.add_argument('--test', action='store_true', help='Test connection')
    args = parser.parse_args()

    pipeline = ScreeningPipeline()

    if args.test:
        print("Testing connection...")
        health = pipeline.ats.health_check()
        print(f"✅ ATS: {health['status']}")
        apps = pipeline.ats.get_applications()
        print(f"✅ Applications: {len(apps)}")

    elif args.application_id:
        result = pipeline.screen_application(args.application_id)
        print(f"✅ Screened: {result.get('candidate_name')}")
        print(f"   Score: {result['scores']['overall_score']}/100")
        print(f"   Recommendation: {result['recommendation']}")

    elif args.job_id:
        result = pipeline.screen_job(args.job_id)
        print(f"✅ Screened {result['screened']} applications")
        print(f"   Advanced to review: {result['advanced_to_review']}")

    elif args.all:
        result = pipeline.screen_all_pending()
        print(f"✅ Screened {result['total_screened']} applications")

    else:
        print("Usage:")
        print("  python screening_pipeline.py --test")
        print("  python screening_pipeline.py --application-id 1")
        print("  python screening_pipeline.py --job-id 1")
        print("  python screening_pipeline.py --all")
