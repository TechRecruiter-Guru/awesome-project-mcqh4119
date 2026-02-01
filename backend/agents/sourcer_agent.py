"""Sourcer Agent - AI-powered candidate sourcing for Physical AI talent."""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import random


class SourcerAgent(BaseAgent):
    """
    Candidate sourcing specialist that:
    - Searches talent pools for Physical AI/Robotics candidates
    - Identifies passive candidates
    - Enriches candidate profiles
    - Scores candidate relevance
    """

    def __init__(self):
        config = AgentConfig(
            name="sourcer",
            description="AI-powered candidate sourcing for Physical AI, Robotics & Autonomous Systems talent"
        )
        super().__init__(config)
        self._sourced_candidates: List[Dict] = []
        self._sources = ["LinkedIn", "GitHub", "ArXiv", "RoboticsJobs", "IEEE", "Company Websites"]
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("search_candidates", self._handle_search)
        self.register_handler("enrich_profile", self._handle_enrich)
        self.register_handler("get_recommendations", self._handle_recommendations)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Sourcer agent initialized - ready to find Physical AI talent")

    async def on_stop(self) -> None:
        self.logger.info("Sourcer agent stopped")

    async def _handle_search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search for candidates matching criteria."""
        role = payload.get("role", "Robotics Engineer")
        skills = payload.get("skills", ["ROS", "Python", "Computer Vision"])
        location = payload.get("location", "Remote")
        experience_min = payload.get("experience_min", 3)

        # Simulated candidate generation (in production, integrate with LinkedIn API, etc.)
        candidates = self._generate_candidates(role, skills, experience_min)
        self._sourced_candidates.extend(candidates)

        return {
            "search_criteria": {
                "role": role,
                "skills": skills,
                "location": location,
                "experience_min": experience_min
            },
            "candidates_found": len(candidates),
            "candidates": candidates,
            "sources_searched": self._sources,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_enrich(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich candidate profile with additional data."""
        candidate_id = payload.get("candidate_id")

        # Simulated enrichment
        return {
            "candidate_id": candidate_id,
            "enriched_data": {
                "github_repos": random.randint(5, 50),
                "publications": random.randint(0, 15),
                "patents": random.randint(0, 5),
                "certifications": random.sample([
                    "ROS Certified Developer",
                    "AWS Machine Learning",
                    "NVIDIA Deep Learning",
                    "Google Cloud AI",
                    "PMP"
                ], random.randint(1, 3)),
                "open_source_contributions": random.randint(0, 200),
                "conference_talks": random.randint(0, 10)
            },
            "social_presence": {
                "linkedin_connections": random.randint(200, 2000),
                "twitter_followers": random.randint(50, 5000),
                "github_followers": random.randint(10, 1000)
            },
            "enrichment_score": round(random.uniform(0.7, 0.98), 2)
        }

    async def _handle_recommendations(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-recommended candidates for a role."""
        job_id = payload.get("job_id", "JOB001")

        top_candidates = self._sourced_candidates[:10] if self._sourced_candidates else self._generate_candidates("Robotics Engineer", ["ROS", "Python"], 3)

        return {
            "job_id": job_id,
            "ai_recommendations": top_candidates[:5],
            "recommendation_reason": "Based on skills match, experience, and cultural fit analysis",
            "confidence": round(random.uniform(0.85, 0.95), 2)
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "total_sourced": len(self._sourced_candidates),
            "sources_active": len(self._sources),
            "avg_match_score": round(random.uniform(0.75, 0.90), 2)
        }

    def _generate_candidates(self, role: str, skills: List[str], exp_min: int) -> List[Dict]:
        """Generate simulated candidates."""
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery", "Reese", "Dakota"]
        last_names = ["Chen", "Patel", "Rodriguez", "Kim", "Johnson", "Williams", "Garcia", "Martinez", "Lee", "Brown"]
        companies = ["Boston Dynamics", "Tesla", "Waymo", "NVIDIA", "Amazon Robotics", "ABB", "FANUC", "Universal Robots", "Agility Robotics", "Figure AI"]
        universities = ["MIT", "Stanford", "CMU", "Georgia Tech", "UC Berkeley", "ETH Zurich", "TUM", "Imperial College", "Caltech", "University of Michigan"]

        robotics_skills = [
            "ROS/ROS2", "Python", "C++", "Computer Vision", "SLAM", "Motion Planning",
            "PyTorch", "TensorFlow", "Reinforcement Learning", "Sensor Fusion",
            "Gazebo", "Isaac Sim", "Control Systems", "Embedded Systems", "PCB Design",
            "Mechanical Design", "CAD/SolidWorks", "3D Printing", "Linux", "Docker"
        ]

        candidates = []
        for i in range(random.randint(8, 15)):
            exp_years = random.randint(exp_min, exp_min + 10)
            candidate = {
                "id": f"CAND{random.randint(10000, 99999)}",
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "title": random.choice([
                    "Senior Robotics Engineer",
                    "ML Engineer - Robotics",
                    "Autonomy Software Engineer",
                    "Computer Vision Engineer",
                    "Motion Planning Engineer",
                    "Robotics Research Scientist",
                    "Principal Engineer - Physical AI",
                    "Staff Software Engineer - Perception"
                ]),
                "current_company": random.choice(companies),
                "experience_years": exp_years,
                "education": f"MS/PhD - {random.choice(universities)}",
                "skills": random.sample(robotics_skills, random.randint(6, 12)),
                "location": random.choice(["San Francisco, CA", "Boston, MA", "Austin, TX", "Seattle, WA", "Remote", "Pittsburgh, PA", "Los Angeles, CA"]),
                "match_score": round(random.uniform(0.72, 0.98), 2),
                "availability": random.choice(["Actively Looking", "Open to Opportunities", "Passive"]),
                "salary_expectation": f"${random.randint(150, 350)}K",
                "source": random.choice(self._sources),
                "sourced_at": datetime.utcnow().isoformat()
            }
            candidates.append(candidate)

        # Sort by match score
        candidates.sort(key=lambda x: x["match_score"], reverse=True)
        return candidates
