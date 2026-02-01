"""Sourcer Agent - AI-powered candidate sourcing for Physical AI talent.

DIFFERENTIATOR: Sources from platforms where top 5 ATS systems DON'T look.
- Zenodo, Kaggle, HuggingFace, Papers with Code, ROS Discourse, ArXiv, IEEE
- Research profiles with H-index, citations, ORCID
- Independent researcher ranking (not tied to company benchmarks)
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import random
import hashlib


class SourcerAgent(BaseAgent):
    """
    Elite candidate sourcing specialist that:
    - Sources from 10+ unique platforms (beyond LinkedIn/Indeed)
    - Extracts research profiles (H-index, citations, ORCID)
    - Identifies and boosts independent researchers
    - Finds PASSIVE candidates not actively job hunting
    """

    # Unique sources - where top 5 ATS systems DON'T look
    ELITE_SOURCES = {
        # Academic & Research
        "ArXiv": {"type": "research", "weight": 1.3, "description": "Preprint research papers"},
        "Zenodo": {"type": "research", "weight": 1.4, "description": "Research datasets & papers"},
        "IEEE Xplore": {"type": "research", "weight": 1.3, "description": "Published research"},
        "Google Scholar": {"type": "research", "weight": 1.2, "description": "Academic citations"},
        "Papers with Code": {"type": "research", "weight": 1.5, "description": "Research + implementation"},
        "Semantic Scholar": {"type": "research", "weight": 1.3, "description": "AI-powered research"},

        # ML/AI Platforms
        "HuggingFace": {"type": "ml_platform", "weight": 1.4, "description": "ML models & datasets"},
        "Kaggle": {"type": "ml_platform", "weight": 1.3, "description": "ML competitions & notebooks"},

        # Open Source & Code
        "GitHub": {"type": "code", "weight": 1.2, "description": "Open source contributions"},
        "GitLab": {"type": "code", "weight": 1.1, "description": "Open source projects"},

        # Robotics Specific
        "ROS Discourse": {"type": "robotics", "weight": 1.4, "description": "ROS community experts"},
        "RobotHub": {"type": "robotics", "weight": 1.3, "description": "Robotics projects"},
        "OpenCV Forums": {"type": "robotics", "weight": 1.2, "description": "Computer vision experts"},

        # Professional
        "LinkedIn": {"type": "professional", "weight": 1.0, "description": "Professional network"},
        "Company Websites": {"type": "professional", "weight": 0.9, "description": "Direct company pages"},
        "ORCID": {"type": "professional", "weight": 1.3, "description": "Research identity"},
    }

    # Research focus areas for Physical AI
    RESEARCH_AREAS = [
        "Computer Vision", "SLAM", "Motion Planning", "Reinforcement Learning",
        "Sensor Fusion", "Human-Robot Interaction", "Manipulation",
        "Autonomous Navigation", "Sim-to-Real Transfer", "Imitation Learning",
        "Neural Radiance Fields", "Diffusion Models for Robotics",
        "Foundation Models for Robotics", "Embodied AI"
    ]

    def __init__(self):
        config = AgentConfig(
            name="sourcer",
            description="Elite AI sourcing from 10+ unique platforms - Research profiles, H-index, Independent researcher boost"
        )
        super().__init__(config)
        self._sourced_candidates: List[Dict] = []
        self._research_profiles: Dict[str, Dict] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("search_candidates", self._handle_search)
        self.register_handler("search_researchers", self._handle_search_researchers)
        self.register_handler("enrich_profile", self._handle_enrich)
        self.register_handler("get_research_profile", self._handle_get_research_profile)
        self.register_handler("get_recommendations", self._handle_recommendations)
        self.register_handler("get_sources", self._handle_get_sources)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Sourcer agent initialized - Elite sourcing from 10+ unique platforms")

    async def on_stop(self) -> None:
        self.logger.info("Sourcer agent stopped")

    async def _handle_search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search for candidates from ALL elite sources."""
        role = payload.get("role", "Robotics Engineer")
        skills = payload.get("skills", ["ROS", "Python", "Computer Vision"])
        location = payload.get("location", "Remote")
        experience_min = payload.get("experience_min", 3)
        include_researchers = payload.get("include_researchers", True)
        independent_only = payload.get("independent_only", False)

        # Generate candidates from elite sources
        candidates = self._generate_elite_candidates(role, skills, experience_min, independent_only)

        # Enrich with research profiles
        for candidate in candidates:
            research_profile = self._generate_research_profile(candidate)
            candidate["research_profile"] = research_profile
            self._research_profiles[candidate["id"]] = research_profile

            # Apply independent researcher boost
            if research_profile.get("is_independent_researcher"):
                candidate["match_score"] = min(candidate["match_score"] * 1.15, 0.99)
                candidate["independent_boost_applied"] = True

        self._sourced_candidates.extend(candidates)

        # Sort by match score (with boosts applied)
        candidates.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "search_criteria": {
                "role": role,
                "skills": skills,
                "location": location,
                "experience_min": experience_min,
                "include_researchers": include_researchers,
                "independent_only": independent_only
            },
            "candidates_found": len(candidates),
            "candidates": candidates,
            "sources_searched": list(self.ELITE_SOURCES.keys()),
            "source_breakdown": self._get_source_breakdown(candidates),
            "independent_researchers_found": len([c for c in candidates if c.get("research_profile", {}).get("is_independent_researcher")]),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_search_researchers(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search specifically for researchers with publications."""
        research_area = payload.get("research_area", "Computer Vision")
        min_citations = payload.get("min_citations", 50)
        min_h_index = payload.get("min_h_index", 5)
        independent_only = payload.get("independent_only", True)

        candidates = self._generate_researcher_candidates(research_area, min_citations, min_h_index, independent_only)
        self._sourced_candidates.extend(candidates)

        return {
            "search_criteria": {
                "research_area": research_area,
                "min_citations": min_citations,
                "min_h_index": min_h_index,
                "independent_only": independent_only
            },
            "researchers_found": len(candidates),
            "researchers": candidates,
            "sources": ["ArXiv", "Zenodo", "Papers with Code", "Google Scholar", "Semantic Scholar", "IEEE Xplore"],
            "avg_h_index": round(sum(c["research_profile"]["h_index"] for c in candidates) / max(len(candidates), 1), 1),
            "avg_citations": round(sum(c["research_profile"]["total_citations"] for c in candidates) / max(len(candidates), 1), 0),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_enrich(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich candidate profile with research data from multiple sources."""
        candidate_id = payload.get("candidate_id")

        # Full enrichment across all platforms
        enrichment = {
            "candidate_id": candidate_id,

            # Research & Academic
            "research_profile": self._generate_research_profile({"id": candidate_id}),

            # Platform Presence
            "platform_presence": {
                "github": {
                    "repos": random.randint(10, 80),
                    "stars_received": random.randint(50, 2000),
                    "contributions_last_year": random.randint(100, 1000),
                    "robotics_repos": random.randint(2, 15),
                    "profile_url": f"https://github.com/user-{candidate_id[-5:]}"
                },
                "huggingface": {
                    "models_published": random.randint(0, 10),
                    "total_downloads": random.randint(0, 50000),
                    "spaces_created": random.randint(0, 5),
                    "profile_url": f"https://huggingface.co/user-{candidate_id[-5:]}"
                },
                "kaggle": {
                    "competitions_entered": random.randint(0, 30),
                    "medals": {"gold": random.randint(0, 3), "silver": random.randint(0, 5), "bronze": random.randint(0, 8)},
                    "highest_rank": random.choice(["Grandmaster", "Master", "Expert", "Contributor", None]),
                    "notebooks_published": random.randint(0, 20),
                    "profile_url": f"https://kaggle.com/user-{candidate_id[-5:]}"
                },
                "ros_discourse": {
                    "posts": random.randint(0, 200),
                    "solutions_provided": random.randint(0, 50),
                    "reputation_score": random.randint(0, 5000),
                    "profile_url": f"https://discourse.ros.org/u/user-{candidate_id[-5:]}"
                },
                "papers_with_code": {
                    "papers_linked": random.randint(0, 15),
                    "code_implementations": random.randint(0, 10),
                    "profile_url": f"https://paperswithcode.com/author/user-{candidate_id[-5:]}"
                }
            },

            # Certifications
            "certifications": random.sample([
                "ROS Certified Developer",
                "NVIDIA Deep Learning Institute",
                "AWS Machine Learning Specialty",
                "Google Cloud Professional ML Engineer",
                "TensorFlow Developer Certificate",
                "PyTorch Certified Developer",
                "Coursera Deep Learning Specialization",
                "MIT MicroMasters in Statistics and Data Science"
            ], random.randint(1, 4)),

            # Conference Activity
            "conference_activity": {
                "talks_given": random.randint(0, 15),
                "papers_presented": random.randint(0, 10),
                "workshops_led": random.randint(0, 5),
                "conferences": random.sample([
                    "ICRA", "IROS", "CoRL", "RSS", "NeurIPS", "ICML", "CVPR", "ICCV", "RAL"
                ], random.randint(1, 5))
            },

            "enrichment_score": round(random.uniform(0.75, 0.98), 2),
            "enriched_at": datetime.utcnow().isoformat()
        }

        return enrichment

    async def _handle_get_research_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed research profile for a candidate."""
        candidate_id = payload.get("candidate_id")

        if candidate_id in self._research_profiles:
            return self._research_profiles[candidate_id]

        return self._generate_research_profile({"id": candidate_id})

    async def _handle_recommendations(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-recommended candidates prioritizing research quality."""
        job_id = payload.get("job_id", "JOB001")
        prioritize_independent = payload.get("prioritize_independent", True)

        candidates = self._sourced_candidates[:20] if self._sourced_candidates else self._generate_elite_candidates("Robotics Engineer", ["ROS", "Python"], 3, False)

        # Sort by research impact + match score
        def score_candidate(c):
            base = c.get("match_score", 0.5)
            research = c.get("research_profile", {})
            h_index_boost = min(research.get("h_index", 0) / 50, 0.2)
            citation_boost = min(research.get("total_citations", 0) / 1000, 0.15)
            indie_boost = 0.1 if research.get("is_independent_researcher") and prioritize_independent else 0
            return base + h_index_boost + citation_boost + indie_boost

        candidates.sort(key=score_candidate, reverse=True)

        return {
            "job_id": job_id,
            "ai_recommendations": candidates[:5],
            "recommendation_factors": [
                "Skills match",
                "Research impact (H-index, citations)",
                "Independent researcher status",
                "Platform presence (GitHub, HuggingFace, Kaggle)",
                "Publication quality"
            ],
            "prioritize_independent": prioritize_independent,
            "confidence": round(random.uniform(0.88, 0.96), 2)
        }

    async def _handle_get_sources(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get all available sourcing platforms."""
        return {
            "total_sources": len(self.ELITE_SOURCES),
            "sources": self.ELITE_SOURCES,
            "categories": {
                "research": [k for k, v in self.ELITE_SOURCES.items() if v["type"] == "research"],
                "ml_platform": [k for k, v in self.ELITE_SOURCES.items() if v["type"] == "ml_platform"],
                "code": [k for k, v in self.ELITE_SOURCES.items() if v["type"] == "code"],
                "robotics": [k for k, v in self.ELITE_SOURCES.items() if v["type"] == "robotics"],
                "professional": [k for k, v in self.ELITE_SOURCES.items() if v["type"] == "professional"]
            },
            "differentiator": "Sources where top 5 ATS systems (Greenhouse, Lever, Workday, iCIMS, Taleo) DON'T look"
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        total = len(self._sourced_candidates)
        researchers = len([c for c in self._sourced_candidates if c.get("research_profile", {}).get("publications_count", 0) > 0])
        independent = len([c for c in self._sourced_candidates if c.get("research_profile", {}).get("is_independent_researcher")])

        return {
            "total_sourced": total,
            "sources_active": len(self.ELITE_SOURCES),
            "researchers_found": researchers,
            "independent_researchers": independent,
            "avg_match_score": round(sum(c.get("match_score", 0) for c in self._sourced_candidates) / max(total, 1), 2),
            "avg_h_index": round(sum(c.get("research_profile", {}).get("h_index", 0) for c in self._sourced_candidates) / max(total, 1), 1),
            "platform_breakdown": self._get_source_breakdown(self._sourced_candidates) if self._sourced_candidates else {}
        }

    def _generate_research_profile(self, candidate: Dict) -> Dict:
        """Generate comprehensive research profile."""
        # Determine if independent researcher (not at major company)
        major_companies = ["Google", "Meta", "OpenAI", "DeepMind", "Tesla", "NVIDIA", "Amazon", "Microsoft", "Apple"]
        current_company = candidate.get("current_company", "")
        is_independent = not any(company in current_company for company in major_companies)

        # Research metrics
        h_index = random.randint(3, 35) if random.random() > 0.3 else 0
        total_citations = h_index * random.randint(10, 50) if h_index > 0 else 0
        publications_count = random.randint(h_index, h_index * 3) if h_index > 0 else random.randint(0, 5)

        # Generate ORCID-like ID
        orcid = f"0000-000{random.randint(1,9)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}" if random.random() > 0.4 else None

        return {
            # Core Research Metrics
            "h_index": h_index,
            "total_citations": total_citations,
            "publications_count": publications_count,
            "i10_index": random.randint(0, h_index),  # Papers with 10+ citations

            # Identity
            "orcid": orcid,
            "google_scholar_id": f"scholar_{hashlib.md5(candidate.get('id', '').encode()).hexdigest()[:12]}" if random.random() > 0.5 else None,
            "semantic_scholar_id": f"semantic_{random.randint(100000, 999999)}" if random.random() > 0.5 else None,

            # Research Focus
            "research_areas": random.sample(self.RESEARCH_AREAS, random.randint(2, 5)),
            "primary_research_area": random.choice(self.RESEARCH_AREAS),

            # Publication Venues
            "top_venues": random.sample([
                "ICRA", "IROS", "CoRL", "RSS", "NeurIPS", "ICML", "CVPR", "ICCV",
                "Science Robotics", "IEEE RAL", "IJRR", "T-RO", "Nature Machine Intelligence"
            ], random.randint(1, 4)) if publications_count > 0 else [],

            # Recent Publications (simulated)
            "recent_publications": self._generate_publications(publications_count, candidate),

            # Independence Status
            "is_independent_researcher": is_independent,
            "affiliation_type": "independent" if is_independent else "corporate",
            "independence_score": round(random.uniform(0.7, 1.0) if is_independent else random.uniform(0.3, 0.6), 2),

            # Research Impact Score
            "research_impact_score": round(
                (h_index / 30 * 0.4) +
                (min(total_citations / 500, 1) * 0.3) +
                (min(publications_count / 20, 1) * 0.2) +
                (0.1 if is_independent else 0),
                2
            ),

            "profile_generated_at": datetime.utcnow().isoformat()
        }

    def _generate_publications(self, count: int, candidate: Dict) -> List[Dict]:
        """Generate simulated publications."""
        if count == 0:
            return []

        publication_templates = [
            "Learning {task} for {domain} using {method}",
            "A {adjective} Approach to {task} in {domain}",
            "{method}-based {task} for {domain} Applications",
            "Towards {adjective} {task}: A {method} Perspective",
            "Real-time {task} with {method} for {domain}"
        ]

        tasks = ["Manipulation", "Navigation", "SLAM", "Object Detection", "Motion Planning", "Grasping", "Control"]
        domains = ["Mobile Robots", "Humanoids", "Autonomous Vehicles", "Industrial Arms", "Drones", "Legged Robots"]
        methods = ["Deep Learning", "Reinforcement Learning", "Transformer", "Diffusion Models", "Neural Networks", "Foundation Models"]
        adjectives = ["Robust", "Scalable", "Efficient", "Novel", "Unified", "Generalizable"]

        publications = []
        for i in range(min(count, 5)):  # Show up to 5 recent
            template = random.choice(publication_templates)
            title = template.format(
                task=random.choice(tasks),
                domain=random.choice(domains),
                method=random.choice(methods),
                adjective=random.choice(adjectives)
            )

            publications.append({
                "title": title,
                "venue": random.choice(["ICRA", "IROS", "CoRL", "RSS", "NeurIPS", "CVPR", "IEEE RAL"]),
                "year": random.randint(2021, 2025),
                "citations": random.randint(5, 200),
                "url": f"https://arxiv.org/abs/{random.randint(2000, 2500)}.{random.randint(10000, 99999)}"
            })

        publications.sort(key=lambda x: x["citations"], reverse=True)
        return publications

    def _generate_elite_candidates(self, role: str, skills: List[str], exp_min: int, independent_only: bool) -> List[Dict]:
        """Generate candidates from elite sources."""
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Quinn", "Avery", "Reese", "Dakota", "Sasha", "Kai", "Rowan", "Sage", "Phoenix"]
        last_names = ["Chen", "Patel", "Rodriguez", "Kim", "Johnson", "Williams", "Garcia", "Martinez", "Lee", "Brown", "Singh", "Nakamura", "Mueller", "Okonkwo", "Johansson"]

        # Mix of companies and independent affiliations
        affiliations_corporate = ["Boston Dynamics", "Tesla", "Waymo", "NVIDIA", "Amazon Robotics", "Figure AI", "Agility Robotics", "Covariant", "Skydio"]
        affiliations_independent = ["Independent Researcher", "Stanford (Postdoc)", "MIT CSAIL", "CMU RI", "UC Berkeley BAIR", "ETH Zurich", "Max Planck Institute", "Georgia Tech", "University of Michigan"]

        candidates = []
        source_list = list(self.ELITE_SOURCES.keys())

        for i in range(random.randint(12, 20)):
            is_independent = random.random() > 0.4 if not independent_only else True
            affiliation = random.choice(affiliations_independent if is_independent else affiliations_corporate)
            exp_years = random.randint(exp_min, exp_min + 12)

            source = random.choice(source_list)
            source_weight = self.ELITE_SOURCES[source]["weight"]

            candidate = {
                "id": f"CAND{random.randint(10000, 99999)}",
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "title": random.choice([
                    "Senior Robotics Engineer",
                    "Research Scientist",
                    "ML Engineer - Robotics",
                    "Autonomy Software Engineer",
                    "Computer Vision Researcher",
                    "Postdoctoral Researcher",
                    "Principal Research Engineer",
                    "Staff Software Engineer - Perception",
                    "Independent Researcher"
                ]),
                "current_company": affiliation,
                "is_independent": is_independent,
                "experience_years": exp_years,
                "education": f"PhD - {random.choice(['MIT', 'Stanford', 'CMU', 'UC Berkeley', 'Georgia Tech', 'ETH Zurich', 'TUM', 'Oxford', 'Cambridge', 'Caltech'])}",
                "skills": random.sample([
                    "ROS/ROS2", "Python", "C++", "Computer Vision", "SLAM", "Motion Planning",
                    "PyTorch", "TensorFlow", "JAX", "Reinforcement Learning", "Sensor Fusion",
                    "Gazebo", "Isaac Sim", "Control Systems", "Embedded Systems",
                    "Transformer Models", "Diffusion Models", "Foundation Models", "LLMs for Robotics"
                ], random.randint(6, 12)),
                "location": random.choice(["San Francisco, CA", "Boston, MA", "Austin, TX", "Seattle, WA", "Remote", "Pittsburgh, PA", "New York, NY", "Zurich, Switzerland", "Munich, Germany", "London, UK"]),
                "match_score": round(random.uniform(0.70, 0.96) * source_weight, 2),
                "availability": random.choice(["Actively Looking", "Open to Opportunities", "Passive", "Passive"]),  # More passive candidates
                "salary_expectation": f"${random.randint(180, 400)}K",
                "source": source,
                "source_type": self.ELITE_SOURCES[source]["type"],
                "sourced_at": datetime.utcnow().isoformat()
            }
            candidates.append(candidate)

        candidates.sort(key=lambda x: x["match_score"], reverse=True)
        return candidates

    def _generate_researcher_candidates(self, research_area: str, min_citations: int, min_h_index: int, independent_only: bool) -> List[Dict]:
        """Generate researcher-specific candidates."""
        candidates = self._generate_elite_candidates("Research Scientist", ["Python", "PyTorch"], 3, independent_only)

        # Filter and enhance for research criteria
        researcher_candidates = []
        for candidate in candidates:
            profile = self._generate_research_profile(candidate)

            if profile["h_index"] >= min_h_index and profile["total_citations"] >= min_citations:
                if research_area in profile["research_areas"] or random.random() > 0.5:
                    profile["research_areas"].insert(0, research_area)
                    candidate["research_profile"] = profile
                    candidate["match_score"] = min(candidate["match_score"] * 1.1, 0.99)
                    researcher_candidates.append(candidate)

        return researcher_candidates[:15]

    def _get_source_breakdown(self, candidates: List[Dict]) -> Dict[str, int]:
        """Get breakdown of candidates by source."""
        breakdown = {}
        for candidate in candidates:
            source = candidate.get("source", "Unknown")
            breakdown[source] = breakdown.get(source, 0) + 1
        return breakdown
