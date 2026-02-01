"""Screener Agent - AI-powered candidate screening for Physical AI talent."""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import random


class ScreenerAgent(BaseAgent):
    """
    AI screening specialist that:
    - Conducts initial candidate screening
    - Evaluates technical competency signals
    - Assesses communication and cultural indicators
    - Flags candidates for human review
    """

    def __init__(self):
        config = AgentConfig(
            name="screener",
            description="AI-powered candidate screening and evaluation"
        )
        super().__init__(config)
        self._screened_candidates: List[Dict] = []
        self._screening_criteria = {
            "technical": 0.4,
            "experience": 0.25,
            "education": 0.15,
            "cultural": 0.2
        }
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("screen_candidate", self._handle_screen_candidate)
        self.register_handler("bulk_screen", self._handle_bulk_screen)
        self.register_handler("get_screening_queue", self._handle_get_queue)
        self.register_handler("approve_candidate", self._handle_approve)
        self.register_handler("reject_candidate", self._handle_reject)
        self.register_handler("request_human_review", self._handle_request_review)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Screener agent initialized - ready to screen Physical AI candidates")

    async def on_stop(self) -> None:
        self.logger.info("Screener agent stopped")

    async def _handle_screen_candidate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Screen a single candidate with AI analysis."""
        candidate = payload.get("candidate", {})
        job = payload.get("job", {})

        # Technical screening
        technical_signals = self._evaluate_technical(candidate)

        # Experience screening
        experience_signals = self._evaluate_experience(candidate, job)

        # Education screening
        education_signals = self._evaluate_education(candidate)

        # Cultural/soft skills screening (simulated NLP analysis)
        cultural_signals = self._evaluate_cultural(candidate)

        # Calculate weighted score
        weighted_score = (
            technical_signals["score"] * self._screening_criteria["technical"] +
            experience_signals["score"] * self._screening_criteria["experience"] +
            education_signals["score"] * self._screening_criteria["education"] +
            cultural_signals["score"] * self._screening_criteria["cultural"]
        )

        # Determine action
        if weighted_score >= 0.75:
            action = "AUTO_APPROVE"
            status = "approved"
        elif weighted_score >= 0.55:
            action = "HUMAN_REVIEW"
            status = "pending_review"
        else:
            action = "AUTO_REJECT"
            status = "rejected"

        # Check for red flags that require human review
        red_flags = self._check_red_flags(candidate)
        if red_flags and action == "AUTO_APPROVE":
            action = "HUMAN_REVIEW"
            status = "pending_review"

        screening_result = {
            "candidate_id": candidate.get("id"),
            "candidate_name": candidate.get("name"),
            "job_id": job.get("id", "general"),
            "scores": {
                "overall": round(weighted_score, 3),
                "technical": round(technical_signals["score"], 3),
                "experience": round(experience_signals["score"], 3),
                "education": round(education_signals["score"], 3),
                "cultural": round(cultural_signals["score"], 3)
            },
            "signals": {
                "technical": technical_signals["signals"],
                "experience": experience_signals["signals"],
                "education": education_signals["signals"],
                "cultural": cultural_signals["signals"]
            },
            "red_flags": red_flags,
            "action": action,
            "status": status,
            "ai_notes": self._generate_screening_notes(candidate, weighted_score, red_flags),
            "human_review_required": action == "HUMAN_REVIEW",
            "screened_at": datetime.utcnow().isoformat()
        }

        self._screened_candidates.append(screening_result)
        return screening_result

    async def _handle_bulk_screen(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Screen multiple candidates."""
        candidates = payload.get("candidates", [])
        job = payload.get("job", {})

        results = {
            "approved": [],
            "pending_review": [],
            "rejected": []
        }

        for candidate in candidates:
            result = await self._handle_screen_candidate({
                "candidate": candidate,
                "job": job
            })

            if result["status"] == "approved":
                results["approved"].append(result)
            elif result["status"] == "pending_review":
                results["pending_review"].append(result)
            else:
                results["rejected"].append(result)

        return {
            "job_id": job.get("id"),
            "total_screened": len(candidates),
            "approved_count": len(results["approved"]),
            "pending_review_count": len(results["pending_review"]),
            "rejected_count": len(results["rejected"]),
            "results": results,
            "screening_efficiency": round(len(results["approved"]) / max(len(candidates), 1), 3),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_queue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get candidates pending human review."""
        pending = [c for c in self._screened_candidates if c["status"] == "pending_review"]

        # Sort by score (highest first for priority review)
        pending.sort(key=lambda x: x["scores"]["overall"], reverse=True)

        return {
            "queue_length": len(pending),
            "candidates": pending,
            "avg_score": round(sum(c["scores"]["overall"] for c in pending) / max(len(pending), 1), 3) if pending else 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_approve(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Human approves a candidate after review."""
        candidate_id = payload.get("candidate_id")
        reviewer = payload.get("reviewer", "recruiter")
        notes = payload.get("notes", "")

        for candidate in self._screened_candidates:
            if candidate["candidate_id"] == candidate_id:
                candidate["status"] = "approved"
                candidate["human_decision"] = {
                    "action": "approved",
                    "reviewer": reviewer,
                    "notes": notes,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return {
                    "candidate_id": candidate_id,
                    "status": "approved",
                    "message": "Candidate approved and moved to interview pipeline"
                }

        return {"error": "Candidate not found"}

    async def _handle_reject(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Human rejects a candidate after review."""
        candidate_id = payload.get("candidate_id")
        reviewer = payload.get("reviewer", "recruiter")
        reason = payload.get("reason", "")
        notes = payload.get("notes", "")

        for candidate in self._screened_candidates:
            if candidate["candidate_id"] == candidate_id:
                candidate["status"] = "rejected"
                candidate["human_decision"] = {
                    "action": "rejected",
                    "reviewer": reviewer,
                    "reason": reason,
                    "notes": notes,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return {
                    "candidate_id": candidate_id,
                    "status": "rejected",
                    "message": "Candidate rejected"
                }

        return {"error": "Candidate not found"}

    async def _handle_request_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Request human review for a candidate."""
        candidate_id = payload.get("candidate_id")
        reason = payload.get("reason", "Additional review needed")

        for candidate in self._screened_candidates:
            if candidate["candidate_id"] == candidate_id:
                candidate["status"] = "pending_review"
                candidate["review_request"] = {
                    "reason": reason,
                    "requested_at": datetime.utcnow().isoformat()
                }
                return {
                    "candidate_id": candidate_id,
                    "status": "pending_review",
                    "message": "Human review requested"
                }

        return {"error": "Candidate not found"}

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        total = len(self._screened_candidates)
        approved = len([c for c in self._screened_candidates if c["status"] == "approved"])
        rejected = len([c for c in self._screened_candidates if c["status"] == "rejected"])
        pending = len([c for c in self._screened_candidates if c["status"] == "pending_review"])

        return {
            "total_screened": total,
            "approved": approved,
            "rejected": rejected,
            "pending_review": pending,
            "approval_rate": round(approved / max(total, 1), 3),
            "human_review_rate": round(pending / max(total, 1), 3)
        }

    def _evaluate_technical(self, candidate: Dict) -> Dict:
        """Evaluate technical competency."""
        skills = candidate.get("skills", [])

        # Core Physical AI skills
        core_skills = ["ROS/ROS2", "Python", "C++", "Computer Vision", "SLAM", "Motion Planning"]
        core_match = len(set(skills) & set(core_skills)) / len(core_skills)

        signals = []
        if "ROS/ROS2" in skills:
            signals.append("Has ROS experience - essential for robotics")
        if "Python" in skills and "C++" in skills:
            signals.append("Strong programming foundation")
        if len(skills) >= 8:
            signals.append("Broad technical skillset")

        github_repos = candidate.get("github_repos", random.randint(5, 30))
        if github_repos > 20:
            signals.append(f"Active on GitHub ({github_repos} repos)")

        score = core_match * 0.6 + min(len(skills) / 12, 1) * 0.3 + min(github_repos / 30, 1) * 0.1

        return {"score": score, "signals": signals}

    def _evaluate_experience(self, candidate: Dict, job: Dict) -> Dict:
        """Evaluate experience fit."""
        years = candidate.get("experience_years", 0)
        min_years = job.get("experience_min", 3)
        max_years = job.get("experience_max", 15)

        signals = []

        if years >= min_years:
            signals.append(f"Meets minimum experience ({years} years)")
        if years > max_years:
            signals.append("May be overqualified")

        # Check for relevant companies
        top_companies = ["Boston Dynamics", "Tesla", "Waymo", "NVIDIA", "Amazon Robotics", "Figure AI", "Agility Robotics"]
        current_company = candidate.get("current_company", "")
        if current_company in top_companies:
            signals.append(f"Currently at top-tier company: {current_company}")

        score = min(years / max(min_years, 3), 1.0) if years >= min_years else years / max(min_years, 3)

        return {"score": score, "signals": signals}

    def _evaluate_education(self, candidate: Dict) -> Dict:
        """Evaluate educational background."""
        education = candidate.get("education", "")

        signals = []
        score = 0.5  # Base score

        top_schools = ["MIT", "Stanford", "CMU", "Georgia Tech", "UC Berkeley", "ETH Zurich", "Caltech"]
        for school in top_schools:
            if school in education:
                signals.append(f"Attended top institution: {school}")
                score = 0.9
                break

        if "PhD" in education:
            signals.append("Has PhD - strong research background")
            score = min(score + 0.2, 1.0)
        elif "MS" in education:
            signals.append("Has Master's degree")
            score = min(score + 0.1, 1.0)

        return {"score": score, "signals": signals}

    def _evaluate_cultural(self, candidate: Dict) -> Dict:
        """Evaluate cultural fit indicators (simulated NLP analysis)."""
        signals = []

        # Simulated analysis - in production, would analyze communication style
        availability = candidate.get("availability", "")
        if availability == "Actively Looking":
            signals.append("Actively seeking opportunities - high engagement")
            engagement_score = 0.9
        elif availability == "Open to Opportunities":
            signals.append("Open to opportunities")
            engagement_score = 0.7
        else:
            signals.append("Passive candidate - may need more outreach")
            engagement_score = 0.5

        # Simulated culture indicators
        culture_match = random.uniform(0.6, 0.95)
        if culture_match > 0.8:
            signals.append("Strong culture alignment indicators")

        score = (engagement_score * 0.4) + (culture_match * 0.6)
        return {"score": score, "signals": signals}

    def _check_red_flags(self, candidate: Dict) -> List[str]:
        """Check for red flags requiring human review."""
        flags = []

        years = candidate.get("experience_years", 0)
        if years > 15:
            flags.append("Very senior - verify role fit and expectations")

        salary = candidate.get("salary_expectation", "")
        if salary and "350" in salary:
            flags.append("High salary expectation - verify budget alignment")

        return flags

    def _generate_screening_notes(self, candidate: Dict, score: float, red_flags: List[str]) -> str:
        """Generate AI screening notes."""
        name = candidate.get("name", "Candidate")
        title = candidate.get("title", "Engineer")

        if score >= 0.75:
            note = f"{name} is a strong candidate for Physical AI roles. "
            note += f"Current role as {title} at {candidate.get('current_company', 'their company')} shows relevant experience. "
            note += "Recommend fast-tracking to technical interview."
        elif score >= 0.55:
            note = f"{name} shows potential for Physical AI roles. "
            note += "Recommend human review to assess specific fit. "
            if red_flags:
                note += f"Note: {'; '.join(red_flags)}"
        else:
            note = f"{name} may not be the best fit for current requirements. "
            note += "Consider for future opportunities or different role."

        return note
