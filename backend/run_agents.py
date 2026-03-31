#!/usr/bin/env python3
"""
Run Agents - Main entry point for the agent platform

Usage:
    python run_agents.py source --job-id 1      # Source leads for job
    python run_agents.py screen --job-id 1      # Screen applications for job
    python run_agents.py screen --all           # Screen all pending
    python run_agents.py full --job-id 1        # Source + Screen for job
    python run_agents.py test                   # Test ATS connection
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.sourcer_agent import SourcerAgent
from agents.screening_pipeline import ScreeningPipeline
from services.ats_client import ats_client


def test_connection():
    """Test ATS connection"""
    print("=" * 50)
    print("Testing ATS Connection")
    print("=" * 50)

    try:
        health = ats_client.health_check()
        print(f"✅ ATS Status: {health['status']}")
        print(f"   Database: {health['database']}")

        jobs = ats_client.get_jobs()
        candidates = ats_client.get_candidates()
        applications = ats_client.get_applications()

        print(f"\n📊 Current Data:")
        print(f"   Jobs: {len(jobs)}")
        print(f"   Candidates: {len(candidates)}")
        print(f"   Applications: {len(applications)}")

        if jobs:
            print(f"\n💼 Available Jobs:")
            for job in jobs[:5]:
                print(f"   [{job['id']}] {job['title']} ({job.get('status', 'N/A')})")

        pending = [a for a in applications if a['status'] == 'reviewing']
        print(f"\n👁️ Pending Review: {len(pending)}")

        print("\n✅ Connection Successful!")
        return True

    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("\nMake sure your ATS is running:")
        print("  cd mctf66nf/backend && python app.py")
        return False


def source_leads(job_id, max_leads=10):
    """Source leads for a job"""
    print("=" * 50)
    print(f"Sourcing Leads for Job #{job_id}")
    print("=" * 50)

    agent = SourcerAgent()
    result = agent.source_for_job(job_id, max_leads)

    print(f"\n✅ Sourcing Complete!")
    print(f"   Job: {result['job']['title']}")
    print(f"   Leads Created: {result['leads_created']}")

    return result


def screen_applications(job_id=None, all_pending=False):
    """Screen applications"""
    print("=" * 50)
    if job_id:
        print(f"Screening Applications for Job #{job_id}")
    else:
        print("Screening All Pending Applications")
    print("=" * 50)

    pipeline = ScreeningPipeline()

    if all_pending:
        result = pipeline.screen_all_pending()
        print(f"\n✅ Screening Complete!")
        print(f"   Total Screened: {result['total_screened']}")
    else:
        result = pipeline.screen_job(job_id)
        print(f"\n✅ Screening Complete!")
        print(f"   Job: {result['job']['title']}")
        print(f"   Screened: {result['screened']}")
        print(f"   Advanced to Review: {result['advanced_to_review']}")

    return result


def full_pipeline(job_id, max_leads=10):
    """Run full pipeline: Source + Screen"""
    print("=" * 50)
    print(f"Full Pipeline for Job #{job_id}")
    print("=" * 50)

    # 1. Source leads
    print("\n📥 Step 1: Sourcing Leads...")
    source_result = source_leads(job_id, max_leads)

    # 2. Screen applications
    print("\n🔍 Step 2: Screening Applications...")
    screen_result = screen_applications(job_id)

    print("\n" + "=" * 50)
    print("Pipeline Complete!")
    print("=" * 50)
    print(f"   Leads Created: {source_result['leads_created']}")
    print(f"   Applications Screened: {screen_result['screened']}")
    print(f"   Pending Human Review: {screen_result['advanced_to_review']}")

    return {'source': source_result, 'screen': screen_result}


def main():
    parser = argparse.ArgumentParser(description='Run Agent Platform')
    subparsers = parser.add_subparsers(dest='command')

    # Test command
    subparsers.add_parser('test', help='Test ATS connection')

    # Source command
    source_parser = subparsers.add_parser('source', help='Source leads')
    source_parser.add_argument('--job-id', type=int, required=True)
    source_parser.add_argument('--max-leads', type=int, default=10)

    # Screen command
    screen_parser = subparsers.add_parser('screen', help='Screen applications')
    screen_parser.add_argument('--job-id', type=int)
    screen_parser.add_argument('--all', action='store_true')

    # Full command
    full_parser = subparsers.add_parser('full', help='Full pipeline')
    full_parser.add_argument('--job-id', type=int, required=True)
    full_parser.add_argument('--max-leads', type=int, default=10)

    args = parser.parse_args()

    if args.command == 'test':
        test_connection()
    elif args.command == 'source':
        source_leads(args.job_id, args.max_leads)
    elif args.command == 'screen':
        if args.all:
            screen_applications(all_pending=True)
        elif args.job_id:
            screen_applications(job_id=args.job_id)
        else:
            print("Error: Provide --job-id or --all")
    elif args.command == 'full':
        full_pipeline(args.job_id, args.max_leads)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
