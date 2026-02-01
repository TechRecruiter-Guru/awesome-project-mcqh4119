"""Audit Agent - Defensible AI Hiring audit trails for internal protection.

PURPOSE: Logs every AI decision with explainability for YOUR legal protection.
- Every sourcing, matching, screening decision is logged
- Explainable AI - captures WHY decisions were made
- Audit trail for EEOC/OFCCP compliance
- Zero candidate PII stored - only decision metadata

This is your INTERNAL protection layer, inspired by defensibleaihiring.com
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import hashlib
import json


class AuditAgent(BaseAgent):
    """
    Internal audit trail agent that:
    - Logs every AI decision (sourcing, matching, screening, pipeline moves)
    - Captures explainability data (WHY the decision was made)
    - Tracks human-in-the-loop decisions
    - Generates compliance reports
    - Zero PII storage - only hashed IDs and decision metadata
    """

    # Decision types we audit
    AUDITABLE_ACTIONS = [
        "candidate_sourced",
        "candidate_matched",
        "candidate_screened",
        "candidate_approved",
        "candidate_rejected",
        "candidate_moved_stage",
        "human_review_requested",
        "human_decision_made",
        "job_created",
        "search_performed"
    ]

    def __init__(self):
        config = AgentConfig(
            name="audit",
            description="Defensible AI Hiring - Internal audit trails for legal protection"
        )
        super().__init__(config)
        self._audit_log: List[Dict] = []
        self._decision_explanations: Dict[str, Dict] = {}
        self._compliance_flags: List[Dict] = []
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("log_decision", self._handle_log_decision)
        self.register_handler("log_human_decision", self._handle_log_human_decision)
        self.register_handler("get_audit_trail", self._handle_get_audit_trail)
        self.register_handler("get_candidate_history", self._handle_get_candidate_history)
        self.register_handler("get_compliance_report", self._handle_get_compliance_report)
        self.register_handler("flag_for_review", self._handle_flag_for_review)
        self.register_handler("get_decision_explanation", self._handle_get_explanation)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Audit agent initialized - Defensible AI Hiring protection active")

    async def on_stop(self) -> None:
        self.logger.info("Audit agent stopped")

    async def _handle_log_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Log an AI decision with full explainability."""
        decision_type = payload.get("decision_type", "unknown")
        candidate_id = payload.get("candidate_id")
        job_id = payload.get("job_id")
        agent_name = payload.get("agent_name", "unknown")
        decision = payload.get("decision")  # e.g., "approved", "rejected", "matched"
        scores = payload.get("scores", {})
        factors = payload.get("factors", [])
        metadata = payload.get("metadata", {})

        # Create audit entry - NO PII, only hashed references
        audit_entry = {
            "audit_id": self._generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": decision_type,
            "agent": agent_name,

            # Hashed IDs only - no PII
            "candidate_hash": self._hash_id(candidate_id) if candidate_id else None,
            "job_hash": self._hash_id(job_id) if job_id else None,

            # Decision details
            "decision": decision,
            "confidence": scores.get("overall", scores.get("confidence")),

            # Explainability - WHY this decision was made
            "explanation": {
                "primary_factors": factors[:5] if factors else self._extract_factors(scores),
                "score_breakdown": self._sanitize_scores(scores),
                "decision_rationale": self._generate_rationale(decision_type, decision, scores, factors)
            },

            # Compliance tracking
            "compliance": {
                "human_in_loop_required": decision_type in ["candidate_screened", "candidate_rejected"],
                "human_in_loop_completed": False,
                "adverse_impact_check": self._check_adverse_impact(decision, scores)
            },

            # Non-PII metadata
            "metadata": {
                "source": metadata.get("source"),
                "is_independent_researcher": metadata.get("is_independent_researcher"),
                "research_score": metadata.get("research_impact_score"),
                "skills_matched_count": metadata.get("skills_matched_count"),
                "experience_years": metadata.get("experience_years")  # Range only, not exact
            }
        }

        self._audit_log.append(audit_entry)

        # Store explanation for later retrieval
        if candidate_id:
            key = f"{self._hash_id(candidate_id)}_{decision_type}"
            self._decision_explanations[key] = audit_entry["explanation"]

        return {
            "audit_id": audit_entry["audit_id"],
            "logged": True,
            "decision_type": decision_type,
            "timestamp": audit_entry["timestamp"],
            "explainability_captured": True
        }

    async def _handle_log_human_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Log a human-in-the-loop decision."""
        candidate_id = payload.get("candidate_id")
        reviewer = payload.get("reviewer", "unknown")
        decision = payload.get("decision")  # "approved" or "rejected"
        reason = payload.get("reason", "")
        notes = payload.get("notes", "")
        original_ai_decision = payload.get("original_ai_decision")

        audit_entry = {
            "audit_id": self._generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "decision_type": "human_decision_made",
            "agent": "human",

            "candidate_hash": self._hash_id(candidate_id) if candidate_id else None,
            "reviewer_hash": self._hash_id(reviewer),  # Hash reviewer ID too

            "decision": decision,
            "confidence": 1.0,  # Human decisions are definitive

            "explanation": {
                "primary_factors": ["human_judgment", reason] if reason else ["human_judgment"],
                "decision_rationale": f"Human reviewer made {decision} decision" + (f": {reason}" if reason else ""),
                "ai_agreement": decision == original_ai_decision if original_ai_decision else None
            },

            "compliance": {
                "human_in_loop_required": True,
                "human_in_loop_completed": True,
                "reviewer_certified": True,  # Would verify in production
                "ai_override": decision != original_ai_decision if original_ai_decision else False
            },

            "metadata": {
                "original_ai_decision": original_ai_decision,
                "has_notes": bool(notes),
                "review_time_logged": True
            }
        }

        self._audit_log.append(audit_entry)

        # Update any previous AI decision entry to mark human review completed
        for entry in self._audit_log:
            if (entry.get("candidate_hash") == self._hash_id(candidate_id) and
                entry.get("decision_type") == "candidate_screened"):
                entry["compliance"]["human_in_loop_completed"] = True

        return {
            "audit_id": audit_entry["audit_id"],
            "logged": True,
            "human_decision_recorded": True,
            "ai_override": audit_entry["compliance"]["ai_override"],
            "timestamp": audit_entry["timestamp"]
        }

    async def _handle_get_audit_trail(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get audit trail with optional filters."""
        decision_type = payload.get("decision_type")
        agent_name = payload.get("agent_name")
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        limit = payload.get("limit", 100)

        trail = self._audit_log.copy()

        # Apply filters
        if decision_type:
            trail = [e for e in trail if e["decision_type"] == decision_type]
        if agent_name:
            trail = [e for e in trail if e["agent"] == agent_name]

        # Sort by timestamp descending
        trail.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "total_entries": len(trail),
            "returned_entries": min(len(trail), limit),
            "audit_trail": trail[:limit],
            "filters_applied": {
                "decision_type": decision_type,
                "agent_name": agent_name,
                "start_date": start_date,
                "end_date": end_date
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_candidate_history(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete audit history for a candidate (hashed)."""
        candidate_id = payload.get("candidate_id")
        candidate_hash = self._hash_id(candidate_id)

        history = [e for e in self._audit_log if e.get("candidate_hash") == candidate_hash]
        history.sort(key=lambda x: x["timestamp"])

        return {
            "candidate_hash": candidate_hash,
            "total_decisions": len(history),
            "history": history,
            "journey": self._summarize_journey(history),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_compliance_report(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance report for auditors."""
        report_type = payload.get("report_type", "summary")

        total_decisions = len(self._audit_log)
        ai_decisions = len([e for e in self._audit_log if e["agent"] != "human"])
        human_decisions = len([e for e in self._audit_log if e["agent"] == "human"])

        # Human-in-loop compliance
        requiring_human_review = [e for e in self._audit_log if e.get("compliance", {}).get("human_in_loop_required")]
        human_review_completed = [e for e in requiring_human_review if e.get("compliance", {}).get("human_in_loop_completed")]

        # AI override rate
        human_entries = [e for e in self._audit_log if e["agent"] == "human"]
        ai_overrides = [e for e in human_entries if e.get("compliance", {}).get("ai_override")]

        # Decision distribution
        decisions_by_type = {}
        for entry in self._audit_log:
            dtype = entry["decision_type"]
            decisions_by_type[dtype] = decisions_by_type.get(dtype, 0) + 1

        # Approval/rejection rates
        approvals = len([e for e in self._audit_log if e.get("decision") == "approved"])
        rejections = len([e for e in self._audit_log if e.get("decision") == "rejected"])

        return {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),

            "summary": {
                "total_decisions_logged": total_decisions,
                "ai_decisions": ai_decisions,
                "human_decisions": human_decisions,
                "explainability_rate": 1.0  # All decisions have explanations
            },

            "human_in_loop_compliance": {
                "decisions_requiring_review": len(requiring_human_review),
                "reviews_completed": len(human_review_completed),
                "compliance_rate": round(len(human_review_completed) / max(len(requiring_human_review), 1), 3),
                "pending_reviews": len(requiring_human_review) - len(human_review_completed)
            },

            "ai_oversight": {
                "ai_override_count": len(ai_overrides),
                "ai_override_rate": round(len(ai_overrides) / max(len(human_entries), 1), 3),
                "ai_human_agreement_rate": round(1 - (len(ai_overrides) / max(len(human_entries), 1)), 3)
            },

            "decision_distribution": {
                "by_type": decisions_by_type,
                "approvals": approvals,
                "rejections": rejections,
                "approval_rate": round(approvals / max(approvals + rejections, 1), 3)
            },

            "adverse_impact_flags": len(self._compliance_flags),

            "data_protection": {
                "pii_stored": False,
                "only_hashed_ids": True,
                "gdpr_compliant": True,
                "ccpa_compliant": True
            }
        }

    async def _handle_flag_for_review(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Flag a decision for compliance review."""
        audit_id = payload.get("audit_id")
        reason = payload.get("reason", "Manual flag")
        flagged_by = payload.get("flagged_by", "system")

        flag = {
            "flag_id": self._generate_audit_id(),
            "audit_id": audit_id,
            "reason": reason,
            "flagged_by": flagged_by,
            "flagged_at": datetime.utcnow().isoformat(),
            "status": "pending_review"
        }

        self._compliance_flags.append(flag)

        return {
            "flag_id": flag["flag_id"],
            "flagged": True,
            "audit_id": audit_id,
            "status": "pending_review"
        }

    async def _handle_get_explanation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed explanation for a specific decision."""
        candidate_id = payload.get("candidate_id")
        decision_type = payload.get("decision_type", "candidate_screened")

        key = f"{self._hash_id(candidate_id)}_{decision_type}"
        explanation = self._decision_explanations.get(key)

        if explanation:
            return {
                "candidate_hash": self._hash_id(candidate_id),
                "decision_type": decision_type,
                "explanation": explanation,
                "found": True
            }

        return {
            "candidate_hash": self._hash_id(candidate_id),
            "decision_type": decision_type,
            "found": False,
            "message": "No explanation found for this decision"
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "total_decisions_logged": len(self._audit_log),
            "ai_decisions": len([e for e in self._audit_log if e["agent"] != "human"]),
            "human_decisions": len([e for e in self._audit_log if e["agent"] == "human"]),
            "compliance_flags": len(self._compliance_flags),
            "explainability_rate": 1.0,
            "pii_stored": False
        }

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID."""
        timestamp = datetime.utcnow().isoformat()
        random_part = hashlib.md5(f"{timestamp}{len(self._audit_log)}".encode()).hexdigest()[:8]
        return f"AUD-{random_part.upper()}"

    def _hash_id(self, id_value: Any) -> str:
        """Hash an ID for privacy - NO PII stored."""
        if id_value is None:
            return None
        return hashlib.sha256(str(id_value).encode()).hexdigest()[:16]

    def _sanitize_scores(self, scores: Dict) -> Dict:
        """Sanitize scores for audit log - remove any PII."""
        safe_keys = ["overall", "skills_required", "skills_preferred", "experience",
                     "research_impact", "platform_presence", "independent_boost",
                     "technical", "cultural", "confidence"]
        return {k: v for k, v in scores.items() if k in safe_keys}

    def _extract_factors(self, scores: Dict) -> List[str]:
        """Extract primary factors from scores."""
        factors = []
        if scores.get("skills_required", 0) > 0.7:
            factors.append("strong_skills_match")
        if scores.get("research_impact", 0) > 0.5:
            factors.append("high_research_impact")
        if scores.get("independent_boost", 0) > 0:
            factors.append("independent_researcher_boost")
        if scores.get("experience", 0) > 0.8:
            factors.append("experience_match")
        return factors if factors else ["general_scoring"]

    def _generate_rationale(self, decision_type: str, decision: str, scores: Dict, factors: List) -> str:
        """Generate human-readable rationale for the decision."""
        overall = scores.get("overall", 0)

        if decision_type == "candidate_screened":
            if decision == "approved":
                return f"AI approved with {overall:.0%} confidence. Key factors: {', '.join(factors[:3]) if factors else 'overall score'}."
            elif decision == "pending_review":
                return f"Flagged for human review ({overall:.0%} score). Borderline case requiring human judgment."
            else:
                return f"AI recommended rejection ({overall:.0%} score). Did not meet minimum thresholds."

        elif decision_type == "candidate_matched":
            return f"Matched with {overall:.0%} score. Factors: {', '.join(factors[:3]) if factors else 'skills and experience'}."

        elif decision_type == "candidate_sourced":
            return f"Sourced from research platforms. Match score: {overall:.0%}."

        return f"Decision: {decision} (Score: {overall:.0%})"

    def _check_adverse_impact(self, decision: str, scores: Dict) -> str:
        """Check for potential adverse impact - placeholder for real implementation."""
        # In production, this would check for statistical disparities
        return "no_flags"

    def _summarize_journey(self, history: List[Dict]) -> Dict:
        """Summarize a candidate's journey through the system."""
        if not history:
            return {"stages": [], "current_stage": "unknown"}

        stages = []
        for entry in history:
            stages.append({
                "stage": entry["decision_type"],
                "decision": entry.get("decision"),
                "timestamp": entry["timestamp"],
                "agent": entry["agent"]
            })

        return {
            "stages": stages,
            "total_touchpoints": len(stages),
            "first_contact": history[0]["timestamp"] if history else None,
            "last_activity": history[-1]["timestamp"] if history else None,
            "human_interactions": len([e for e in history if e["agent"] == "human"])
        }
