"""
PhysicalAI Talent - AI-Powered Recruiting Platform for Physical AI, Robotics & Autonomous Systems
Enterprise-grade multi-agent platform for sourcing, screening, and hiring top talent
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import asyncio
from functools import wraps
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS - allow all origins
CORS(app)

# Initialize database
from core.database import db, init_db
init_db(app)

# Initialize Recruiting Agents
from agents import (
    OrchestratorAgent, GatewayAgent, DataAgent, IntegrationAgent,
    SourcerAgent, MatcherAgent, ScreenerAgent, PipelineAgent
)

orchestrator = OrchestratorAgent()
gateway = GatewayAgent()
data_agent = DataAgent()
integration_agent = IntegrationAgent()
sourcer_agent = SourcerAgent()
matcher_agent = MatcherAgent()
screener_agent = ScreenerAgent()
pipeline_agent = PipelineAgent()

# Register ALL agents with orchestrator
orchestrator.register_agent(gateway)
orchestrator.register_agent(data_agent)
orchestrator.register_agent(integration_agent)
orchestrator.register_agent(sourcer_agent)
orchestrator.register_agent(matcher_agent)
orchestrator.register_agent(screener_agent)
orchestrator.register_agent(pipeline_agent)


def run_async(func):
    """Decorator to run async functions in Flask."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


# ============== ROOT & HEALTH ==============

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "PhysicalAI Talent",
        "tagline": "AI-Powered Recruiting for Robotics & Autonomous Systems",
        "company": "VanguardLab",
        "version": "2.0.0",
        "architecture": "multi-agent-recruiting",
        "status": "operational",
        "capabilities": [
            "AI Candidate Sourcing",
            "Skills Matching & Scoring",
            "Automated Screening",
            "Human-in-the-Loop Review",
            "Pipeline Management",
            "Predictive Analytics"
        ],
        "agents": {
            "core": ["orchestrator", "gateway", "data", "integration"],
            "recruiting": ["sourcer", "matcher", "screener", "pipeline"]
        },
        "target_industries": [
            "Physical AI",
            "Robotics",
            "Humanoids",
            "Autonomous Systems",
            "Computer Vision",
            "Machine Learning"
        ],
        "endpoints": {
            "health": "/api/health",
            "agents": "/api/agents",
            "candidates": "/api/candidates",
            "jobs": "/api/jobs",
            "pipeline": "/api/pipeline",
            "screening": "/api/screening",
            "demo": "/api/demo"
        },
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "PhysicalAI Talent",
        "uptime": "operational",
        "agents_ready": True,
        "timestamp": datetime.utcnow().isoformat()
    })


# ============== AGENT ROUTES ==============

@app.route('/api/agents', methods=['GET'])
@run_async
async def get_agents_status():
    """Get status of all agents."""
    await orchestrator.start()
    status = orchestrator.get_all_agents_status()
    return jsonify(status)


@app.route('/api/agents/<agent_name>/action', methods=['POST'])
@run_async
async def agent_action(agent_name):
    """Execute an action on a specific agent."""
    await orchestrator.start()

    data = request.get_json() or {}
    action = data.get('action')
    payload = data.get('payload', {})

    if not action:
        return jsonify({"error": "Action is required"}), 400

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api",
        target=agent_name,
        action=action,
        payload=payload
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify({"success": True, "data": response.data})
    else:
        return jsonify({"success": False, "error": response.error}), 400


# ============== CANDIDATE SOURCING ROUTES ==============

@app.route('/api/candidates/search', methods=['POST'])
@run_async
async def search_candidates():
    """AI-powered candidate search."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="sourcer", action="search_candidates",
        payload={
            "role": data.get("role", "Robotics Engineer"),
            "skills": data.get("skills", ["ROS", "Python", "Computer Vision"]),
            "location": data.get("location", "Remote"),
            "experience_min": data.get("experience_min", 3)
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/candidates/<candidate_id>/enrich', methods=['POST'])
@run_async
async def enrich_candidate(candidate_id):
    """Enrich candidate profile with additional data."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="sourcer", action="enrich_profile",
        payload={"candidate_id": candidate_id}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/candidates/recommendations', methods=['GET'])
@run_async
async def get_recommendations():
    """Get AI-recommended candidates."""
    await orchestrator.start()
    job_id = request.args.get('job_id', 'JOB001')

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="sourcer", action="get_recommendations",
        payload={"job_id": job_id}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


# ============== MATCHING ROUTES ==============

@app.route('/api/match', methods=['POST'])
@run_async
async def match_candidate():
    """Match candidate to job."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="matcher", action="match_candidate",
        payload={
            "candidate": data.get("candidate", {}),
            "job": data.get("job", {})
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/match/batch', methods=['POST'])
@run_async
async def batch_match():
    """Match multiple candidates to a job."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="matcher", action="batch_match",
        payload={
            "candidates": data.get("candidates", []),
            "job": data.get("job", {})
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/candidates/<candidate_id>/gaps', methods=['GET'])
@run_async
async def analyze_skill_gaps(candidate_id):
    """Analyze skill gaps for a candidate."""
    await orchestrator.start()
    target_role = request.args.get('role', 'Senior Robotics Engineer')

    # First get candidate info (simulated)
    candidate = {
        "id": candidate_id,
        "skills": request.args.getlist('skills') or ["Python", "ROS/ROS2", "Computer Vision"]
    }

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="matcher", action="analyze_gaps",
        payload={
            "candidate": candidate,
            "target_role": target_role
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


# ============== SCREENING ROUTES ==============

@app.route('/api/screening/screen', methods=['POST'])
@run_async
async def screen_candidate():
    """AI screening of a candidate."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="screener", action="screen_candidate",
        payload={
            "candidate": data.get("candidate", {}),
            "job": data.get("job", {})
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/screening/bulk', methods=['POST'])
@run_async
async def bulk_screen():
    """Bulk screen multiple candidates."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="screener", action="bulk_screen",
        payload={
            "candidates": data.get("candidates", []),
            "job": data.get("job", {})
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/screening/queue', methods=['GET'])
@run_async
async def get_screening_queue():
    """Get candidates pending human review."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="screener", action="get_screening_queue", payload={}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/screening/<candidate_id>/approve', methods=['POST'])
@run_async
async def approve_candidate(candidate_id):
    """Human approves a candidate."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="screener", action="approve_candidate",
        payload={
            "candidate_id": candidate_id,
            "reviewer": data.get("reviewer", "recruiter"),
            "notes": data.get("notes", "")
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/screening/<candidate_id>/reject', methods=['POST'])
@run_async
async def reject_candidate(candidate_id):
    """Human rejects a candidate."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="screener", action="reject_candidate",
        payload={
            "candidate_id": candidate_id,
            "reviewer": data.get("reviewer", "recruiter"),
            "reason": data.get("reason", ""),
            "notes": data.get("notes", "")
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


# ============== PIPELINE ROUTES ==============

@app.route('/api/pipeline', methods=['GET'])
@run_async
async def get_pipeline():
    """Get full recruiting pipeline."""
    await orchestrator.start()
    job_id = request.args.get('job_id')

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="get_pipeline",
        payload={"job_id": job_id}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/pipeline/funnel', methods=['GET'])
@run_async
async def get_funnel():
    """Get funnel visualization data."""
    await orchestrator.start()
    job_id = request.args.get('job_id')

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="get_funnel",
        payload={"job_id": job_id}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/pipeline/metrics', methods=['GET'])
@run_async
async def get_pipeline_metrics():
    """Get pipeline metrics and conversion rates."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="get_metrics", payload={}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/pipeline/predict', methods=['GET'])
@run_async
async def predict_outcomes():
    """AI prediction of pipeline outcomes."""
    await orchestrator.start()
    job_id = request.args.get('job_id')

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="predict_outcomes",
        payload={"job_id": job_id}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/pipeline/candidate', methods=['POST'])
@run_async
async def add_to_pipeline():
    """Add candidate to pipeline."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="add_candidate",
        payload={
            "candidate": data.get("candidate", {}),
            "job_id": data.get("job_id", "JOB001"),
            "stage": data.get("stage", "sourced")
        }
    )
    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    return jsonify({"error": response.error}), 400


@app.route('/api/pipeline/move', methods=['POST'])
@run_async
async def move_stage():
    """Move candidate to new stage."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="move_stage",
        payload={
            "candidate_id": data.get("candidate_id"),
            "new_stage": data.get("new_stage"),
            "notes": data.get("notes", ""),
            "reviewer": data.get("reviewer", "recruiter")
        }
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


# ============== JOB ROUTES ==============

@app.route('/api/jobs', methods=['GET'])
@run_async
async def get_jobs():
    """Get all job openings."""
    await orchestrator.start()
    status = request.args.get('status')

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="get_jobs",
        payload={"status": status}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/jobs', methods=['POST'])
@run_async
async def create_job():
    """Create a new job opening."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="pipeline", action="create_job",
        payload=data
    )
    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    return jsonify({"error": response.error}), 400


# ============== DASHBOARD STATS ==============

@app.route('/api/dashboard/stats', methods=['GET'])
@run_async
async def get_dashboard_stats():
    """Get dashboard statistics from all agents."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage

    # Get stats from all recruiting agents
    sourcer_msg = AgentMessage(source="api", target="sourcer", action="get_stats", payload={})
    matcher_msg = AgentMessage(source="api", target="matcher", action="get_stats", payload={})
    screener_msg = AgentMessage(source="api", target="screener", action="get_stats", payload={})
    pipeline_msg = AgentMessage(source="api", target="pipeline", action="get_stats", payload={})

    sourcer_resp = await orchestrator.route_message(sourcer_msg)
    matcher_resp = await orchestrator.route_message(matcher_msg)
    screener_resp = await orchestrator.route_message(screener_msg)
    pipeline_resp = await orchestrator.route_message(pipeline_msg)

    return jsonify({
        "sourcing": sourcer_resp.data if sourcer_resp.success else {},
        "matching": matcher_resp.data if matcher_resp.success else {},
        "screening": screener_resp.data if screener_resp.success else {},
        "pipeline": pipeline_resp.data if pipeline_resp.success else {},
        "timestamp": datetime.utcnow().isoformat()
    })


# ============== LIVE DEMO ROUTES ==============
import random

# Demo state for recruiting workflow
demo_state = {
    "demo_running": False,
    "demo_step": 0,
    "candidates_sourced": [],
    "candidates_screened": [],
    "candidates_in_pipeline": [],
    "activity_feed": []
}

@app.route('/api/demo/start', methods=['POST'])
@run_async
async def start_demo():
    """Start recruiting demo - shows the full AI-powered workflow."""
    await orchestrator.start()

    demo_state["demo_running"] = True
    demo_state["demo_step"] = 0
    demo_state["activity_feed"] = []

    # Step 1: Source candidates
    from agents.base_agent import AgentMessage

    # Search for candidates
    search_msg = AgentMessage(
        source="demo", target="sourcer", action="search_candidates",
        payload={
            "role": "Senior Robotics Engineer",
            "skills": ["ROS/ROS2", "Python", "C++", "Computer Vision", "SLAM"],
            "experience_min": 5
        }
    )
    search_resp = await orchestrator.route_message(search_msg)

    if search_resp.success:
        candidates = search_resp.data.get("candidates", [])
        demo_state["candidates_sourced"] = candidates
        demo_state["activity_feed"].append({
            "type": "sourcing",
            "message": f"AI Sourcer found {len(candidates)} candidates matching criteria",
            "timestamp": datetime.utcnow().isoformat()
        })

    return jsonify({
        "status": "demo_started",
        "message": "AI Recruiting Demo activated - sourcing Physical AI talent",
        "candidates_found": len(demo_state["candidates_sourced"]),
        "workflow_steps": [
            "1. AI Sourcing - Find candidates",
            "2. AI Screening - Evaluate fit",
            "3. Human Review - Approve/Reject",
            "4. Pipeline Management - Track progress"
        ]
    })


@app.route('/api/demo/stop', methods=['POST'])
def stop_demo():
    """Stop demo mode."""
    demo_state["demo_running"] = False
    demo_state["demo_step"] = 0
    return jsonify({"status": "demo_stopped"})


@app.route('/api/demo/state', methods=['GET'])
@run_async
async def get_demo_state():
    """Get current demo state with live recruiting data."""
    await orchestrator.start()

    if not demo_state["demo_running"]:
        return jsonify({
            "demo_running": False,
            "message": "Start demo to see AI recruiting in action"
        })

    # Advance demo step
    demo_state["demo_step"] += 1
    step = demo_state["demo_step"]

    from agents.base_agent import AgentMessage

    # Simulate workflow progression
    if step == 3 and demo_state["candidates_sourced"]:
        # Screen candidates
        screen_msg = AgentMessage(
            source="demo", target="screener", action="bulk_screen",
            payload={
                "candidates": demo_state["candidates_sourced"][:5],
                "job": {
                    "id": "JOB001",
                    "title": "Senior Robotics Engineer",
                    "experience_min": 5
                }
            }
        )
        screen_resp = await orchestrator.route_message(screen_msg)

        if screen_resp.success:
            demo_state["candidates_screened"] = screen_resp.data
            demo_state["activity_feed"].append({
                "type": "screening",
                "message": f"AI Screener evaluated {screen_resp.data.get('total_screened', 0)} candidates",
                "approved": screen_resp.data.get("approved_count", 0),
                "pending_review": screen_resp.data.get("pending_review_count", 0),
                "timestamp": datetime.utcnow().isoformat()
            })

    # Get current stats
    stats_msg = AgentMessage(source="demo", target="pipeline", action="get_metrics", payload={})
    stats_resp = await orchestrator.route_message(stats_msg)

    # Build response
    return jsonify({
        "demo_running": demo_state["demo_running"],
        "workflow_step": min(step, 4),
        "total_steps": 4,
        "sourcing": {
            "candidates_found": len(demo_state["candidates_sourced"]),
            "top_candidates": demo_state["candidates_sourced"][:3] if demo_state["candidates_sourced"] else [],
            "sources": ["LinkedIn", "GitHub", "ArXiv", "RoboticsJobs"],
            "ai_status": "active" if step >= 1 else "idle"
        },
        "screening": {
            "total_screened": demo_state["candidates_screened"].get("total_screened", 0) if demo_state["candidates_screened"] else 0,
            "approved": demo_state["candidates_screened"].get("approved_count", 0) if demo_state["candidates_screened"] else 0,
            "pending_review": demo_state["candidates_screened"].get("pending_review_count", 0) if demo_state["candidates_screened"] else 0,
            "rejected": demo_state["candidates_screened"].get("rejected_count", 0) if demo_state["candidates_screened"] else 0,
            "ai_status": "active" if step >= 3 else "waiting"
        },
        "human_review": {
            "queue_length": demo_state["candidates_screened"].get("pending_review_count", 0) if demo_state["candidates_screened"] else 0,
            "status": "ready_for_review" if step >= 3 else "waiting"
        },
        "pipeline": stats_resp.data if stats_resp.success else {},
        "activity_feed": demo_state["activity_feed"][-5:],
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/demo/scenarios', methods=['GET'])
def get_demo_scenarios():
    """Get available demo scenarios for the recruiting platform."""
    return jsonify({
        "scenarios": [
            {
                "id": "full_workflow",
                "name": "Full Recruiting Workflow",
                "description": "Watch AI source, screen, and pipeline Physical AI candidates",
                "duration": "Interactive"
            },
            {
                "id": "urgent_hire",
                "name": "Urgent Robotics Hire",
                "description": "Fast-track sourcing for critical robotics position",
                "duration": "2 min"
            },
            {
                "id": "passive_sourcing",
                "name": "Passive Candidate Outreach",
                "description": "AI identifies and enriches passive candidate profiles",
                "duration": "1 min"
            },
            {
                "id": "skills_gap",
                "name": "Skills Gap Analysis",
                "description": "AI analyzes candidate skills vs job requirements",
                "duration": "30 sec"
            }
        ],
        "target_roles": [
            "Senior Robotics Engineer",
            "ML Engineer - Physical AI",
            "Autonomy Software Engineer",
            "Computer Vision Engineer",
            "Motion Planning Engineer",
            "Research Scientist - Robotics"
        ]
    })


@app.route('/api/demo/workflow', methods=['GET'])
@run_async
async def run_demo_workflow():
    """Run a complete demo workflow showing the agentic recruiting system."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage

    workflow_results = {
        "steps": [],
        "summary": {}
    }

    # Step 1: Source candidates
    search_msg = AgentMessage(
        source="demo", target="sourcer", action="search_candidates",
        payload={
            "role": "Senior Robotics Engineer",
            "skills": ["ROS/ROS2", "Python", "C++", "SLAM", "Motion Planning"],
            "experience_min": 5
        }
    )
    search_resp = await orchestrator.route_message(search_msg)

    candidates = search_resp.data.get("candidates", []) if search_resp.success else []
    workflow_results["steps"].append({
        "step": 1,
        "agent": "Sourcer",
        "action": "Search Candidates",
        "result": f"Found {len(candidates)} candidates",
        "data": {
            "candidates_found": len(candidates),
            "top_3": candidates[:3]
        }
    })

    # Step 2: Match candidates to job
    job = {
        "id": "JOB001",
        "title": "Senior Robotics Engineer",
        "required_skills": ["ROS/ROS2", "Python", "C++", "Motion Planning"],
        "preferred_skills": ["SLAM", "Computer Vision", "TensorFlow"],
        "experience_min": 5,
        "experience_max": 12
    }

    match_msg = AgentMessage(
        source="demo", target="matcher", action="batch_match",
        payload={"candidates": candidates[:5], "job": job}
    )
    match_resp = await orchestrator.route_message(match_msg)

    workflow_results["steps"].append({
        "step": 2,
        "agent": "Matcher",
        "action": "Skills Matching",
        "result": f"Analyzed {match_resp.data.get('total_candidates', 0)} candidates" if match_resp.success else "Error",
        "data": match_resp.data if match_resp.success else {}
    })

    # Step 3: Screen candidates
    screen_msg = AgentMessage(
        source="demo", target="screener", action="bulk_screen",
        payload={"candidates": candidates[:5], "job": job}
    )
    screen_resp = await orchestrator.route_message(screen_msg)

    workflow_results["steps"].append({
        "step": 3,
        "agent": "Screener",
        "action": "AI Screening",
        "result": f"Screened {screen_resp.data.get('total_screened', 0)} candidates" if screen_resp.success else "Error",
        "data": {
            "approved": screen_resp.data.get("approved_count", 0),
            "pending_human_review": screen_resp.data.get("pending_review_count", 0),
            "rejected": screen_resp.data.get("rejected_count", 0)
        } if screen_resp.success else {}
    })

    # Step 4: Pipeline metrics
    metrics_msg = AgentMessage(
        source="demo", target="pipeline", action="get_metrics", payload={}
    )
    metrics_resp = await orchestrator.route_message(metrics_msg)

    workflow_results["steps"].append({
        "step": 4,
        "agent": "Pipeline",
        "action": "Pipeline Analytics",
        "result": "Generated pipeline metrics",
        "data": metrics_resp.data if metrics_resp.success else {}
    })

    # Summary
    workflow_results["summary"] = {
        "total_candidates_sourced": len(candidates),
        "approved_by_ai": screen_resp.data.get("approved_count", 0) if screen_resp.success else 0,
        "pending_human_review": screen_resp.data.get("pending_review_count", 0) if screen_resp.success else 0,
        "human_in_the_loop_required": True,
        "message": "AI has pre-filtered candidates. Human recruiters review the 'pending_review' queue to make final decisions.",
        "next_action": "Review candidates in the Human Review Queue"
    }

    return jsonify(workflow_results)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
