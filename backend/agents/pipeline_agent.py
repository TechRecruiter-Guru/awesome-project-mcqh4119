"""Pipeline Agent - Recruiting funnel and pipeline management for Physical AI talent."""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime, timedelta
import random


class PipelineAgent(BaseAgent):
    """
    Recruiting pipeline manager that:
    - Manages candidate funnel stages
    - Tracks pipeline metrics
    - Predicts pipeline health
    - Automates stage transitions
    """

    STAGES = [
        "sourced",
        "screened",
        "phone_screen",
        "technical_interview",
        "onsite_interview",
        "offer",
        "hired",
        "rejected"
    ]

    def __init__(self):
        config = AgentConfig(
            name="pipeline",
            description="Recruiting pipeline and funnel management"
        )
        super().__init__(config)
        self._pipeline: Dict[str, List[Dict]] = {stage: [] for stage in self.STAGES}
        self._stage_history: List[Dict] = []
        self._jobs: Dict[str, Dict] = {}
        self._initialize_demo_data()
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("add_candidate", self._handle_add_candidate)
        self.register_handler("move_stage", self._handle_move_stage)
        self.register_handler("get_pipeline", self._handle_get_pipeline)
        self.register_handler("get_stage", self._handle_get_stage)
        self.register_handler("get_metrics", self._handle_get_metrics)
        self.register_handler("get_funnel", self._handle_get_funnel)
        self.register_handler("predict_outcomes", self._handle_predict_outcomes)
        self.register_handler("create_job", self._handle_create_job)
        self.register_handler("get_jobs", self._handle_get_jobs)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Pipeline agent initialized - managing Physical AI talent funnel")

    async def on_stop(self) -> None:
        self.logger.info("Pipeline agent stopped")

    def _initialize_demo_data(self) -> None:
        """Initialize with demo job openings and candidates."""
        # Demo jobs
        self._jobs = {
            "JOB001": {
                "id": "JOB001",
                "title": "Senior Robotics Engineer",
                "department": "Robotics",
                "location": "San Francisco, CA",
                "required_skills": ["ROS/ROS2", "Python", "C++", "Motion Planning"],
                "preferred_skills": ["SLAM", "Computer Vision", "TensorFlow"],
                "experience_min": 5,
                "experience_max": 12,
                "salary_range": "$180K - $280K",
                "status": "open",
                "priority": "high",
                "created_at": datetime.utcnow().isoformat()
            },
            "JOB002": {
                "id": "JOB002",
                "title": "ML Engineer - Physical AI",
                "department": "AI/ML",
                "location": "Remote",
                "required_skills": ["Python", "PyTorch", "Reinforcement Learning"],
                "preferred_skills": ["ROS/ROS2", "Simulation", "Isaac Sim"],
                "experience_min": 3,
                "experience_max": 10,
                "salary_range": "$160K - $250K",
                "status": "open",
                "priority": "high",
                "created_at": datetime.utcnow().isoformat()
            },
            "JOB003": {
                "id": "JOB003",
                "title": "Autonomy Software Engineer",
                "department": "Autonomy",
                "location": "Austin, TX",
                "required_skills": ["C++", "SLAM", "Sensor Fusion", "Motion Planning"],
                "preferred_skills": ["ROS/ROS2", "Computer Vision"],
                "experience_min": 4,
                "experience_max": 15,
                "salary_range": "$170K - $290K",
                "status": "open",
                "priority": "medium",
                "created_at": datetime.utcnow().isoformat()
            }
        }

    async def _handle_add_candidate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add a candidate to the pipeline."""
        candidate = payload.get("candidate", {})
        job_id = payload.get("job_id", "JOB001")
        stage = payload.get("stage", "sourced")

        pipeline_entry = {
            "id": candidate.get("id", f"CAND{random.randint(10000, 99999)}"),
            "candidate": candidate,
            "job_id": job_id,
            "current_stage": stage,
            "stage_history": [{
                "stage": stage,
                "entered_at": datetime.utcnow().isoformat(),
                "notes": "Added to pipeline"
            }],
            "added_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }

        self._pipeline[stage].append(pipeline_entry)

        return {
            "success": True,
            "candidate_id": pipeline_entry["id"],
            "stage": stage,
            "job_id": job_id,
            "message": f"Candidate added to {stage} stage"
        }

    async def _handle_move_stage(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Move a candidate to a new stage."""
        candidate_id = payload.get("candidate_id")
        new_stage = payload.get("new_stage")
        notes = payload.get("notes", "")
        reviewer = payload.get("reviewer", "system")

        if new_stage not in self.STAGES:
            return {"error": f"Invalid stage. Valid stages: {self.STAGES}"}

        # Find candidate in current stage
        for stage, candidates in self._pipeline.items():
            for i, entry in enumerate(candidates):
                if entry["id"] == candidate_id:
                    old_stage = entry["current_stage"]

                    # Update entry
                    entry["current_stage"] = new_stage
                    entry["stage_history"].append({
                        "stage": new_stage,
                        "from_stage": old_stage,
                        "entered_at": datetime.utcnow().isoformat(),
                        "notes": notes,
                        "reviewer": reviewer
                    })
                    entry["last_activity"] = datetime.utcnow().isoformat()

                    # Move to new stage
                    self._pipeline[stage].pop(i)
                    self._pipeline[new_stage].append(entry)

                    # Record in history
                    self._stage_history.append({
                        "candidate_id": candidate_id,
                        "from_stage": old_stage,
                        "to_stage": new_stage,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    return {
                        "success": True,
                        "candidate_id": candidate_id,
                        "from_stage": old_stage,
                        "to_stage": new_stage,
                        "message": f"Candidate moved from {old_stage} to {new_stage}"
                    }

        return {"error": "Candidate not found in pipeline"}

    async def _handle_get_pipeline(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get full pipeline view."""
        job_id = payload.get("job_id")

        pipeline_view = {}
        for stage in self.STAGES:
            if stage == "rejected":
                continue  # Don't include rejected in main view

            candidates = self._pipeline[stage]
            if job_id:
                candidates = [c for c in candidates if c.get("job_id") == job_id]

            pipeline_view[stage] = {
                "count": len(candidates),
                "candidates": [{
                    "id": c["id"],
                    "name": c["candidate"].get("name"),
                    "title": c["candidate"].get("title"),
                    "company": c["candidate"].get("current_company"),
                    "score": c["candidate"].get("match_score"),
                    "days_in_stage": self._days_in_stage(c),
                    "last_activity": c["last_activity"]
                } for c in candidates]
            }

        total = sum(len(self._pipeline[s]) for s in self.STAGES if s != "rejected")

        return {
            "pipeline": pipeline_view,
            "total_candidates": total,
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_stage(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get candidates in a specific stage."""
        stage = payload.get("stage", "sourced")
        job_id = payload.get("job_id")

        candidates = self._pipeline.get(stage, [])
        if job_id:
            candidates = [c for c in candidates if c.get("job_id") == job_id]

        return {
            "stage": stage,
            "count": len(candidates),
            "candidates": candidates,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get pipeline metrics and conversion rates."""
        timeframe = payload.get("timeframe", "all")

        stage_counts = {stage: len(self._pipeline[stage]) for stage in self.STAGES}
        total_active = sum(stage_counts[s] for s in self.STAGES if s not in ["rejected", "hired"])

        # Calculate conversion rates
        conversions = {}
        for i in range(len(self.STAGES) - 2):  # Exclude hired and rejected
            from_stage = self.STAGES[i]
            to_stage = self.STAGES[i + 1]
            from_count = stage_counts[from_stage]
            to_count = stage_counts[to_stage]

            if from_count > 0:
                conversions[f"{from_stage}_to_{to_stage}"] = round(to_count / from_count, 3)
            else:
                conversions[f"{from_stage}_to_{to_stage}"] = 0

        # Overall funnel efficiency
        sourced = stage_counts["sourced"] + sum(stage_counts[s] for s in self.STAGES[1:])
        hired = stage_counts["hired"]
        overall_conversion = round(hired / max(sourced, 1), 3)

        return {
            "stage_counts": stage_counts,
            "total_active": total_active,
            "total_hired": hired,
            "total_rejected": stage_counts["rejected"],
            "conversion_rates": conversions,
            "overall_conversion": overall_conversion,
            "avg_time_to_hire_days": random.randint(21, 45),
            "pipeline_velocity": round(random.uniform(0.7, 1.3), 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_funnel(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get funnel visualization data."""
        job_id = payload.get("job_id")

        funnel_data = []
        running_total = 0

        # Build funnel (excluding rejected)
        display_stages = [s for s in self.STAGES if s != "rejected"]

        for stage in display_stages:
            candidates = self._pipeline[stage]
            if job_id:
                candidates = [c for c in candidates if c.get("job_id") == job_id]

            count = len(candidates)
            running_total += count

            funnel_data.append({
                "stage": stage,
                "stage_display": stage.replace("_", " ").title(),
                "count": count,
                "percentage": 100 if stage == "sourced" else round(count / max(funnel_data[0]["count"], 1) * 100, 1)
            })

        return {
            "funnel": funnel_data,
            "total_in_funnel": running_total,
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_predict_outcomes(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """AI prediction of pipeline outcomes."""
        job_id = payload.get("job_id")

        # Get current pipeline state
        pipeline_state = {}
        for stage in self.STAGES:
            candidates = self._pipeline[stage]
            if job_id:
                candidates = [c for c in candidates if c.get("job_id") == job_id]
            pipeline_state[stage] = len(candidates)

        # Simulated predictions based on historical conversion rates
        predicted_hires = int(
            pipeline_state["sourced"] * 0.05 +
            pipeline_state["screened"] * 0.10 +
            pipeline_state["phone_screen"] * 0.25 +
            pipeline_state["technical_interview"] * 0.40 +
            pipeline_state["onsite_interview"] * 0.60 +
            pipeline_state["offer"] * 0.85
        )

        weeks_to_fill = max(1, 4 - predicted_hires)

        return {
            "current_state": pipeline_state,
            "predicted_hires_30_days": predicted_hires,
            "confidence": round(random.uniform(0.72, 0.88), 2),
            "estimated_weeks_to_fill": weeks_to_fill,
            "recommendations": self._generate_recommendations(pipeline_state),
            "risk_factors": self._identify_risks(pipeline_state),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_create_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job opening."""
        job_id = f"JOB{len(self._jobs) + 1:03d}"

        job = {
            "id": job_id,
            "title": payload.get("title", "Robotics Engineer"),
            "department": payload.get("department", "Engineering"),
            "location": payload.get("location", "Remote"),
            "required_skills": payload.get("required_skills", []),
            "preferred_skills": payload.get("preferred_skills", []),
            "experience_min": payload.get("experience_min", 3),
            "experience_max": payload.get("experience_max", 10),
            "salary_range": payload.get("salary_range", "Competitive"),
            "status": "open",
            "priority": payload.get("priority", "medium"),
            "created_at": datetime.utcnow().isoformat()
        }

        self._jobs[job_id] = job

        return {
            "success": True,
            "job": job
        }

    async def _handle_get_jobs(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get all job openings."""
        status = payload.get("status")

        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j["status"] == status]

        # Add pipeline counts per job
        for job in jobs:
            job_id = job["id"]
            job["pipeline_count"] = sum(
                len([c for c in self._pipeline[stage] if c.get("job_id") == job_id])
                for stage in self.STAGES
            )

        return {
            "jobs": jobs,
            "total": len(jobs),
            "open_count": len([j for j in jobs if j["status"] == "open"])
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        total = sum(len(self._pipeline[s]) for s in self.STAGES)
        return {
            "total_in_pipeline": total,
            "active_jobs": len([j for j in self._jobs.values() if j["status"] == "open"]),
            "hired_this_month": len(self._pipeline["hired"]),
            "avg_conversion": round(random.uniform(0.08, 0.15), 3)
        }

    def _days_in_stage(self, entry: Dict) -> int:
        """Calculate days in current stage."""
        if entry["stage_history"]:
            last_entry = entry["stage_history"][-1]
            entered = datetime.fromisoformat(last_entry["entered_at"].replace("Z", ""))
            return (datetime.utcnow() - entered).days
        return 0

    def _generate_recommendations(self, state: Dict) -> List[str]:
        """Generate pipeline recommendations."""
        recommendations = []

        if state["sourced"] < 10:
            recommendations.append("Pipeline is thin - increase sourcing efforts")
        if state["screened"] > state["phone_screen"] * 3:
            recommendations.append("Bottleneck at screening - expedite phone screens")
        if state["offer"] > 0 and state["hired"] == 0:
            recommendations.append("Offers pending - follow up on candidate decisions")
        if state["technical_interview"] < 3:
            recommendations.append("Low interview pipeline - source more qualified candidates")

        if not recommendations:
            recommendations.append("Pipeline is healthy - maintain current velocity")

        return recommendations

    def _identify_risks(self, state: Dict) -> List[str]:
        """Identify pipeline risks."""
        risks = []

        total_active = sum(state[s] for s in ["sourced", "screened", "phone_screen", "technical_interview", "onsite_interview", "offer"])

        if total_active < 5:
            risks.append("Low pipeline volume - risk of missing hiring targets")
        if state["offer"] == 0 and state["onsite_interview"] < 2:
            risks.append("No near-term hires expected")
        if state["rejected"] > state["hired"] * 5:
            risks.append("High rejection rate - review sourcing quality")

        return risks
