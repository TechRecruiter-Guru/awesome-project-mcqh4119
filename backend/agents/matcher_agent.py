"""Matcher Agent - AI-powered candidate-to-job matching for Physical AI talent.

DIFFERENTIATOR: Includes research scoring + independent researcher boost.
- H-index, citations, publications weighted in matching
- Independent researchers ranked higher (not tied to company benchmarks)
- Platform presence (GitHub, Kaggle, HuggingFace) factored in
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import random


class MatcherAgent(BaseAgent):
    """
    Elite skills matching specialist that:
    - Matches candidates to job requirements
    - Weights research impact (H-index, citations, publications)
    - Boosts independent researchers (unbiased by corporate benchmarks)
    - Factors platform presence (GitHub, Kaggle, HuggingFace)
    - Identifies skill gaps and upskilling paths
    """

    # Scoring weights - research heavy for Physical AI
    SCORING_WEIGHTS = {
        "skills_required": 0.30,
        "skills_preferred": 0.10,
        "experience": 0.15,
        "research_impact": 0.25,  # H-index, citations, publications
        "platform_presence": 0.10,  # GitHub, Kaggle, HuggingFace
        "independent_boost": 0.10   # Bonus for independent researchers
    }

    def __init__(self):
        config = AgentConfig(
            name="matcher",
            description="Elite matching with research scoring, H-index weighting, and independent researcher boost"
        )
        super().__init__(config)
        self._match_history: List[Dict] = []
        self._skill_weights = {
            # Core Robotics
            "ROS/ROS2": 1.5,
            "Python": 1.2,
            "C++": 1.4,
            "Computer Vision": 1.4,
            "SLAM": 1.5,
            "Motion Planning": 1.5,
            "Sensor Fusion": 1.4,
            "Control Systems": 1.4,
            "Embedded Systems": 1.3,
            # ML/AI
            "PyTorch": 1.3,
            "TensorFlow": 1.2,
            "JAX": 1.4,
            "Reinforcement Learning": 1.5,
            # Cutting Edge
            "Transformer Models": 1.5,
            "Diffusion Models": 1.6,
            "Foundation Models": 1.6,
            "LLMs for Robotics": 1.6,
            "Sim-to-Real": 1.5,
            "Imitation Learning": 1.5
        }
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("match_candidate", self._handle_match_candidate)
        self.register_handler("batch_match", self._handle_batch_match)
        self.register_handler("analyze_gaps", self._handle_analyze_gaps)
        self.register_handler("get_top_matches", self._handle_get_top_matches)
        self.register_handler("rank_by_research", self._handle_rank_by_research)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Matcher agent initialized - Research-weighted matching for Physical AI talent")

    async def on_stop(self) -> None:
        self.logger.info("Matcher agent stopped")

    async def _handle_match_candidate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Match a single candidate to a job with research scoring."""
        candidate = payload.get("candidate", {})
        job = payload.get("job", {})

        # Extract candidate data
        candidate_skills = set(candidate.get("skills", []))
        required_skills = set(job.get("required_skills", []))
        preferred_skills = set(job.get("preferred_skills", []))
        research_profile = candidate.get("research_profile", {})

        # === SKILLS SCORING ===
        required_match = len(candidate_skills & required_skills) / max(len(required_skills), 1)
        preferred_match = len(candidate_skills & preferred_skills) / max(len(preferred_skills), 1)

        # Apply skill weights for matched skills
        weighted_skill_bonus = 0
        for skill in candidate_skills & (required_skills | preferred_skills):
            weighted_skill_bonus += (self._skill_weights.get(skill, 1.0) - 1.0) * 0.05
        weighted_skill_bonus = min(weighted_skill_bonus, 0.15)

        # === EXPERIENCE SCORING ===
        candidate_exp = candidate.get("experience_years", 0)
        job_min_exp = job.get("experience_min", 0)
        job_max_exp = job.get("experience_max", 15)
        if job_min_exp <= candidate_exp <= job_max_exp:
            exp_match = 1.0
        elif candidate_exp < job_min_exp:
            exp_match = max(0, 1 - (job_min_exp - candidate_exp) * 0.15)
        else:
            exp_match = max(0.7, 1 - (candidate_exp - job_max_exp) * 0.05)  # Slight penalty for overqualified

        # === RESEARCH IMPACT SCORING ===
        h_index = research_profile.get("h_index", 0)
        citations = research_profile.get("total_citations", 0)
        publications = research_profile.get("publications_count", 0)
        research_impact_score = research_profile.get("research_impact_score", 0)

        # Calculate research score if not provided
        if research_impact_score == 0 and (h_index > 0 or citations > 0 or publications > 0):
            research_impact_score = (
                min(h_index / 25, 1.0) * 0.4 +
                min(citations / 500, 1.0) * 0.35 +
                min(publications / 15, 1.0) * 0.25
            )

        # === PLATFORM PRESENCE SCORING ===
        platform_score = self._calculate_platform_score(candidate)

        # === INDEPENDENT RESEARCHER BOOST ===
        is_independent = research_profile.get("is_independent_researcher", candidate.get("is_independent", False))
        independent_score = 1.0 if is_independent else 0.0

        # === FINAL WEIGHTED SCORE ===
        final_score = (
            required_match * self.SCORING_WEIGHTS["skills_required"] +
            preferred_match * self.SCORING_WEIGHTS["skills_preferred"] +
            exp_match * self.SCORING_WEIGHTS["experience"] +
            research_impact_score * self.SCORING_WEIGHTS["research_impact"] +
            platform_score * self.SCORING_WEIGHTS["platform_presence"] +
            independent_score * self.SCORING_WEIGHTS["independent_boost"] +
            weighted_skill_bonus
        )

        # Normalize to 0-1 range
        final_score = min(final_score, 0.99)

        match_result = {
            "candidate_id": candidate.get("id"),
            "candidate_name": candidate.get("name"),
            "job_id": job.get("id"),
            "scores": {
                "overall": round(final_score, 3),
                "skills_required": round(required_match, 3),
                "skills_preferred": round(preferred_match, 3),
                "experience": round(exp_match, 3),
                "research_impact": round(research_impact_score, 3),
                "platform_presence": round(platform_score, 3),
                "independent_boost": round(independent_score * self.SCORING_WEIGHTS["independent_boost"], 3)
            },
            "research_metrics": {
                "h_index": h_index,
                "total_citations": citations,
                "publications_count": publications,
                "is_independent": is_independent,
                "research_areas": research_profile.get("research_areas", [])
            },
            "matched_skills": list(candidate_skills & (required_skills | preferred_skills)),
            "missing_required": list(required_skills - candidate_skills),
            "missing_preferred": list(preferred_skills - candidate_skills),
            "high_value_skills": [s for s in candidate_skills if self._skill_weights.get(s, 1.0) >= 1.4],
            "recommendation": self._get_recommendation(final_score, is_independent, h_index),
            "scoring_breakdown": self.SCORING_WEIGHTS,
            "timestamp": datetime.utcnow().isoformat()
        }

        self._match_history.append(match_result)
        return match_result

    async def _handle_batch_match(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Match multiple candidates to a job with research scoring."""
        candidates = payload.get("candidates", [])
        job = payload.get("job", {})
        prioritize_independent = payload.get("prioritize_independent", True)

        matches = []
        for candidate in candidates:
            match_result = await self._handle_match_candidate({
                "candidate": candidate,
                "job": job
            })
            matches.append(match_result)

        # Sort by overall score
        matches.sort(key=lambda x: x["scores"]["overall"], reverse=True)

        # Count research-qualified candidates
        research_qualified = len([m for m in matches if m["research_metrics"]["h_index"] >= 5])
        independent_count = len([m for m in matches if m["research_metrics"]["is_independent"]])

        return {
            "job_id": job.get("id"),
            "total_candidates": len(candidates),
            "matches": matches,
            "top_3": matches[:3],
            "average_score": round(sum(m["scores"]["overall"] for m in matches) / max(len(matches), 1), 3),
            "research_qualified_count": research_qualified,
            "independent_researchers_count": independent_count,
            "scoring_weights_used": self.SCORING_WEIGHTS,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_rank_by_research(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Rank candidates purely by research metrics."""
        candidates = payload.get("candidates", [])
        min_h_index = payload.get("min_h_index", 0)
        independent_only = payload.get("independent_only", False)

        ranked = []
        for candidate in candidates:
            research = candidate.get("research_profile", {})
            h_index = research.get("h_index", 0)
            citations = research.get("total_citations", 0)
            is_independent = research.get("is_independent_researcher", False)

            if h_index >= min_h_index:
                if not independent_only or is_independent:
                    research_score = (
                        h_index * 0.4 +
                        (citations / 100) * 0.35 +
                        research.get("publications_count", 0) * 0.25
                    )
                    if is_independent:
                        research_score *= 1.15  # 15% boost

                    ranked.append({
                        "candidate_id": candidate.get("id"),
                        "name": candidate.get("name"),
                        "h_index": h_index,
                        "citations": citations,
                        "publications": research.get("publications_count", 0),
                        "is_independent": is_independent,
                        "research_areas": research.get("research_areas", []),
                        "research_rank_score": round(research_score, 2)
                    })

        ranked.sort(key=lambda x: x["research_rank_score"], reverse=True)

        return {
            "ranked_by_research": ranked[:20],
            "total_qualified": len(ranked),
            "filters_applied": {
                "min_h_index": min_h_index,
                "independent_only": independent_only
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_analyze_gaps(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill gaps including research gaps."""
        candidate = payload.get("candidate", {})
        target_role = payload.get("target_role", "Senior Robotics Engineer")

        candidate_skills = set(candidate.get("skills", []))
        research_profile = candidate.get("research_profile", {})

        # Define target skills for common Physical AI roles
        role_requirements = {
            "Senior Robotics Engineer": {
                "skills": ["ROS/ROS2", "Python", "C++", "Motion Planning", "Control Systems", "Linux"],
                "min_h_index": 3,
                "min_publications": 2
            },
            "Research Scientist": {
                "skills": ["Python", "PyTorch", "Reinforcement Learning", "Computer Vision", "SLAM"],
                "min_h_index": 10,
                "min_publications": 8
            },
            "ML Engineer - Robotics": {
                "skills": ["Python", "PyTorch", "TensorFlow", "Reinforcement Learning", "Computer Vision", "ROS/ROS2"],
                "min_h_index": 3,
                "min_publications": 2
            },
            "Autonomy Engineer": {
                "skills": ["SLAM", "Sensor Fusion", "Motion Planning", "C++", "ROS/ROS2", "Computer Vision"],
                "min_h_index": 5,
                "min_publications": 3
            },
            "Principal Research Engineer": {
                "skills": ["Python", "C++", "PyTorch", "Foundation Models", "Reinforcement Learning", "Diffusion Models"],
                "min_h_index": 15,
                "min_publications": 12
            }
        }

        requirements = role_requirements.get(target_role, role_requirements["Senior Robotics Engineer"])
        target_skills = set(requirements["skills"])
        gaps = target_skills - candidate_skills
        strengths = candidate_skills & target_skills

        # Research gaps
        h_index = research_profile.get("h_index", 0)
        publications = research_profile.get("publications_count", 0)
        research_gaps = []

        if h_index < requirements["min_h_index"]:
            research_gaps.append({
                "gap": "H-index",
                "current": h_index,
                "required": requirements["min_h_index"],
                "recommendation": "Publish more papers in top venues (ICRA, IROS, CoRL)"
            })

        if publications < requirements["min_publications"]:
            research_gaps.append({
                "gap": "Publications",
                "current": publications,
                "required": requirements["min_publications"],
                "recommendation": "Submit to ArXiv, IEEE RAL, or robotics conferences"
            })

        # Generate upskilling recommendations
        skill_recommendations = []
        for gap in gaps:
            skill_recommendations.append({
                "skill": gap,
                "priority": "high" if self._skill_weights.get(gap, 1.0) >= 1.4 else "medium",
                "resources": self._get_learning_resources(gap),
                "estimated_time": f"{random.randint(2, 12)} weeks"
            })

        # Calculate overall readiness
        skills_readiness = len(strengths) / max(len(target_skills), 1)
        research_readiness = min(h_index / requirements["min_h_index"], 1.0) if requirements["min_h_index"] > 0 else 1.0
        overall_readiness = (skills_readiness * 0.6) + (research_readiness * 0.4)

        return {
            "candidate_id": candidate.get("id"),
            "target_role": target_role,
            "current_skills": list(candidate_skills),
            "target_skills": list(target_skills),
            "skill_gaps": list(gaps),
            "skill_strengths": list(strengths),
            "research_gaps": research_gaps,
            "current_research": {
                "h_index": h_index,
                "publications": publications,
                "is_independent": research_profile.get("is_independent_researcher", False)
            },
            "readiness_scores": {
                "skills": round(skills_readiness, 3),
                "research": round(research_readiness, 3),
                "overall": round(overall_readiness, 3)
            },
            "skill_recommendations": skill_recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_top_matches(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get top matches from history."""
        limit = payload.get("limit", 10)
        job_id = payload.get("job_id")
        independent_only = payload.get("independent_only", False)

        matches = self._match_history
        if job_id:
            matches = [m for m in matches if m.get("job_id") == job_id]
        if independent_only:
            matches = [m for m in matches if m.get("research_metrics", {}).get("is_independent")]

        matches.sort(key=lambda x: x["scores"]["overall"], reverse=True)

        return {
            "top_matches": matches[:limit],
            "total_matches": len(matches),
            "filters": {"job_id": job_id, "independent_only": independent_only},
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        total = len(self._match_history)
        if total == 0:
            return {
                "total_matches": 0,
                "avg_score": 0,
                "strong_matches": 0,
                "research_qualified": 0,
                "independent_researchers": 0,
                "skills_tracked": len(self._skill_weights)
            }

        return {
            "total_matches": total,
            "avg_score": round(sum(m["scores"]["overall"] for m in self._match_history) / total, 3),
            "strong_matches": len([m for m in self._match_history if m["scores"]["overall"] > 0.75]),
            "research_qualified": len([m for m in self._match_history if m.get("research_metrics", {}).get("h_index", 0) >= 5]),
            "independent_researchers": len([m for m in self._match_history if m.get("research_metrics", {}).get("is_independent")]),
            "avg_research_score": round(sum(m["scores"].get("research_impact", 0) for m in self._match_history) / total, 3),
            "skills_tracked": len(self._skill_weights),
            "scoring_weights": self.SCORING_WEIGHTS
        }

    def _calculate_platform_score(self, candidate: Dict) -> float:
        """Calculate platform presence score from GitHub, Kaggle, HuggingFace, etc."""
        # This would integrate with enrichment data in production
        # For now, simulate based on candidate data
        base_score = random.uniform(0.3, 0.8)

        # Boost for certain indicators
        if candidate.get("research_profile", {}).get("publications_count", 0) > 5:
            base_score += 0.1
        if candidate.get("is_independent"):
            base_score += 0.05

        return min(base_score, 1.0)

    def _get_recommendation(self, score: float, is_independent: bool, h_index: int) -> str:
        """Get hiring recommendation based on score and research profile."""
        indie_tag = " [INDEPENDENT RESEARCHER]" if is_independent else ""
        research_tag = f" [H-INDEX: {h_index}]" if h_index >= 10 else ""

        if score >= 0.80:
            return f"STRONG_MATCH - Fast track for interview{indie_tag}{research_tag}"
        elif score >= 0.65:
            return f"GOOD_MATCH - Recommend for screening{indie_tag}{research_tag}"
        elif score >= 0.50:
            return f"POTENTIAL_MATCH - Consider for pipeline{indie_tag}{research_tag}"
        else:
            return f"WEAK_MATCH - Not recommended at this time{research_tag}"

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
            "Foundation Models": ["Hugging Face Course", "Stanford CS324", "LLM Papers"],
            "Diffusion Models": ["Lil'Log Blog", "CVPR Tutorials", "Score-Based Papers"],
            "Control Systems": ["Brian Douglas YouTube", "MIT OCW 2.004", "Modern Control Engineering"]
        }
        return resources.get(skill, ["Online Courses", "Official Documentation", "YouTube Tutorials"])
