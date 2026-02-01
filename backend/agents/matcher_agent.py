"""Matcher Agent - AI-powered candidate-to-job matching for Physical AI talent."""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import random


class MatcherAgent(BaseAgent):
    """
    Skills matching specialist that:
    - Matches candidates to job requirements
    - Calculates compatibility scores
    - Identifies skill gaps
    - Recommends training/upskilling paths
    """

    def __init__(self):
        config = AgentConfig(
            name="matcher",
            description="AI-powered candidate-to-job matching and skills analysis"
        )
        super().__init__(config)
        self._match_history: List[Dict] = []
        self._skill_weights = {
            "ROS/ROS2": 1.5,
            "Python": 1.2,
            "C++": 1.3,
            "Computer Vision": 1.4,
            "SLAM": 1.5,
            "Motion Planning": 1.4,
            "PyTorch": 1.3,
            "TensorFlow": 1.2,
            "Reinforcement Learning": 1.5,
            "Sensor Fusion": 1.4,
            "Embedded Systems": 1.3,
            "Control Systems": 1.4
        }
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("match_candidate", self._handle_match_candidate)
        self.register_handler("batch_match", self._handle_batch_match)
        self.register_handler("analyze_gaps", self._handle_analyze_gaps)
        self.register_handler("get_top_matches", self._handle_get_top_matches)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Matcher agent initialized - ready to match Physical AI talent")

    async def on_stop(self) -> None:
        self.logger.info("Matcher agent stopped")

    async def _handle_match_candidate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Match a single candidate to a job."""
        candidate = payload.get("candidate", {})
        job = payload.get("job", {})

        candidate_skills = set(candidate.get("skills", []))
        required_skills = set(job.get("required_skills", []))
        preferred_skills = set(job.get("preferred_skills", []))

        # Calculate match scores
        required_match = len(candidate_skills & required_skills) / max(len(required_skills), 1)
        preferred_match = len(candidate_skills & preferred_skills) / max(len(preferred_skills), 1)

        # Weighted overall score
        overall_score = (required_match * 0.7) + (preferred_match * 0.3)

        # Experience match
        candidate_exp = candidate.get("experience_years", 0)
        job_min_exp = job.get("experience_min", 0)
        job_max_exp = job.get("experience_max", 15)
        exp_match = 1.0 if job_min_exp <= candidate_exp <= job_max_exp else max(0, 1 - abs(candidate_exp - job_min_exp) * 0.1)

        # Culture fit simulation (in production, would use NLP on candidate responses)
        culture_fit = random.uniform(0.65, 0.95)

        final_score = (overall_score * 0.5) + (exp_match * 0.3) + (culture_fit * 0.2)

        match_result = {
            "candidate_id": candidate.get("id"),
            "job_id": job.get("id"),
            "scores": {
                "overall": round(final_score, 3),
                "skills_required": round(required_match, 3),
                "skills_preferred": round(preferred_match, 3),
                "experience": round(exp_match, 3),
                "culture_fit": round(culture_fit, 3)
            },
            "matched_skills": list(candidate_skills & (required_skills | preferred_skills)),
            "missing_required": list(required_skills - candidate_skills),
            "missing_preferred": list(preferred_skills - candidate_skills),
            "recommendation": self._get_recommendation(final_score),
            "timestamp": datetime.utcnow().isoformat()
        }

        self._match_history.append(match_result)
        return match_result

    async def _handle_batch_match(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Match multiple candidates to a job."""
        candidates = payload.get("candidates", [])
        job = payload.get("job", {})

        matches = []
        for candidate in candidates:
            match_result = await self._handle_match_candidate({
                "candidate": candidate,
                "job": job
            })
            matches.append(match_result)

        # Sort by overall score
        matches.sort(key=lambda x: x["scores"]["overall"], reverse=True)

        return {
            "job_id": job.get("id"),
            "total_candidates": len(candidates),
            "matches": matches,
            "top_3": matches[:3],
            "average_score": round(sum(m["scores"]["overall"] for m in matches) / max(len(matches), 1), 3),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_analyze_gaps(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill gaps for a candidate."""
        candidate = payload.get("candidate", {})
        target_role = payload.get("target_role", "Senior Robotics Engineer")

        candidate_skills = set(candidate.get("skills", []))

        # Define target skills for common Physical AI roles
        role_skills = {
            "Senior Robotics Engineer": ["ROS/ROS2", "Python", "C++", "Motion Planning", "Control Systems", "Linux"],
            "ML Engineer - Robotics": ["Python", "PyTorch", "TensorFlow", "Reinforcement Learning", "Computer Vision", "ROS/ROS2"],
            "Autonomy Engineer": ["SLAM", "Sensor Fusion", "Motion Planning", "C++", "ROS/ROS2", "Computer Vision"],
            "Computer Vision Engineer": ["Computer Vision", "Python", "PyTorch", "TensorFlow", "C++", "CUDA"],
            "Research Scientist": ["Python", "PyTorch", "Reinforcement Learning", "Research", "Publications", "SLAM"]
        }

        target_skills = set(role_skills.get(target_role, role_skills["Senior Robotics Engineer"]))
        gaps = target_skills - candidate_skills
        strengths = candidate_skills & target_skills

        # Generate upskilling recommendations
        recommendations = []
        for gap in gaps:
            recommendations.append({
                "skill": gap,
                "priority": "high" if gap in ["ROS/ROS2", "Python", "C++"] else "medium",
                "resources": self._get_learning_resources(gap),
                "estimated_time": f"{random.randint(2, 12)} weeks"
            })

        return {
            "candidate_id": candidate.get("id"),
            "target_role": target_role,
            "current_skills": list(candidate_skills),
            "target_skills": list(target_skills),
            "skill_gaps": list(gaps),
            "strengths": list(strengths),
            "gap_count": len(gaps),
            "readiness_score": round(len(strengths) / max(len(target_skills), 1), 3),
            "upskilling_recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_top_matches(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get top matches from history."""
        limit = payload.get("limit", 10)
        job_id = payload.get("job_id")

        matches = self._match_history
        if job_id:
            matches = [m for m in matches if m.get("job_id") == job_id]

        matches.sort(key=lambda x: x["scores"]["overall"], reverse=True)

        return {
            "top_matches": matches[:limit],
            "total_matches": len(matches),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "total_matches": len(self._match_history),
            "avg_score": round(sum(m["scores"]["overall"] for m in self._match_history) / max(len(self._match_history), 1), 3) if self._match_history else 0,
            "strong_matches": len([m for m in self._match_history if m["scores"]["overall"] > 0.8]),
            "skills_tracked": len(self._skill_weights)
        }

    def _get_recommendation(self, score: float) -> str:
        """Get hiring recommendation based on score."""
        if score >= 0.85:
            return "STRONG_MATCH - Fast track for interview"
        elif score >= 0.70:
            return "GOOD_MATCH - Recommend for screening"
        elif score >= 0.55:
            return "POTENTIAL_MATCH - Consider for pipeline"
        else:
            return "WEAK_MATCH - Not recommended at this time"

    def _get_learning_resources(self, skill: str) -> List[str]:
        """Get learning resources for a skill."""
        resources = {
            "ROS/ROS2": ["ROS2 Official Tutorials", "The Construct", "Udacity Robotics Nanodegree"],
            "Python": ["Python.org Tutorial", "Real Python", "Codecademy Python"],
            "C++": ["LearnCpp.com", "C++ Primer", "Udemy C++ for Robotics"],
            "Computer Vision": ["OpenCV Tutorials", "PyImageSearch", "CS231n Stanford"],
            "SLAM": ["Cyrill Stachniss Lectures", "ORB-SLAM Papers", "GTSAM Tutorials"],
            "Motion Planning": ["MoveIt Tutorials", "Steven LaValle Book", "Coursera Robotics"],
            "PyTorch": ["PyTorch Official Tutorials", "Fast.ai", "Deep Learning with PyTorch"],
            "TensorFlow": ["TensorFlow Official Guide", "Coursera TF Specialization"],
            "Reinforcement Learning": ["Sutton & Barto Book", "DeepMind x UCL Lectures", "Spinning Up"],
            "Sensor Fusion": ["Kalman Filter Tutorials", "Sensor Fusion Udacity", "ROS Localization"],
        }
        return resources.get(skill, ["Online Courses", "Official Documentation", "YouTube Tutorials"])
