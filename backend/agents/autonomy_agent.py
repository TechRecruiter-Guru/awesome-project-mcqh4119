"""Autonomy Agent - Autonomous decision making and behavior control."""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import random


class AutonomyAgent(BaseAgent):
    """
    Autonomous decision-making specialist that:
    - Mission planning and execution
    - Behavior tree management
    - Safety monitoring
    - Human-Robot collaboration
    """

    def __init__(self):
        config = AgentConfig(
            name="autonomy",
            description="Autonomous decision making, mission planning, and safety"
        )
        super().__init__(config)
        self._autonomy_level = 4  # SAE levels 0-5
        self._current_mission: Optional[Dict] = None
        self._mission_history: List[Dict] = []
        self._safety_status = "nominal"
        self._behavior_state = "idle"
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("plan_mission", self._handle_plan_mission)
        self.register_handler("execute_mission", self._handle_execute_mission)
        self.register_handler("abort_mission", self._handle_abort_mission)
        self.register_handler("get_mission_status", self._handle_get_mission_status)
        self.register_handler("safety_check", self._handle_safety_check)
        self.register_handler("set_autonomy_level", self._handle_set_autonomy_level)
        self.register_handler("get_behavior_tree", self._handle_get_behavior_tree)
        self.register_handler("human_override", self._handle_human_override)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info(f"Autonomy agent initialized at Level {self._autonomy_level}")

    async def on_stop(self) -> None:
        if self._current_mission:
            self._current_mission["status"] = "suspended"
        self.logger.info("Autonomy agent stopped")

    async def _handle_plan_mission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Plan a new autonomous mission."""
        mission_type = payload.get("type", "navigation")
        target = payload.get("target", {})
        constraints = payload.get("constraints", {})

        mission = {
            "id": f"mission_{datetime.utcnow().timestamp()}",
            "type": mission_type,
            "target": target,
            "constraints": constraints,
            "status": "planned",
            "created_at": datetime.utcnow().isoformat(),
            "steps": self._generate_mission_steps(mission_type),
            "estimated_duration_s": random.randint(30, 600),
            "risk_assessment": {
                "level": random.choice(["low", "medium", "high"]),
                "factors": ["obstacle_density", "human_presence", "terrain_complexity"]
            },
            "safety_requirements": {
                "max_speed": 1.0,
                "min_obstacle_distance": 0.5,
                "human_safety_zone": 2.0
            }
        }

        self._current_mission = mission
        return mission

    async def _handle_execute_mission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the current mission."""
        if not self._current_mission:
            raise ValueError("No mission planned")

        self._current_mission["status"] = "executing"
        self._current_mission["started_at"] = datetime.utcnow().isoformat()
        self._behavior_state = "executing_mission"

        return {
            "mission_id": self._current_mission["id"],
            "status": "executing",
            "current_step": 1,
            "total_steps": len(self._current_mission["steps"]),
            "estimated_completion": datetime.utcnow().isoformat()
        }

    async def _handle_abort_mission(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Abort current mission."""
        reason = payload.get("reason", "user_requested")

        if self._current_mission:
            self._current_mission["status"] = "aborted"
            self._current_mission["abort_reason"] = reason
            self._mission_history.append(self._current_mission)
            mission_id = self._current_mission["id"]
            self._current_mission = None
            self._behavior_state = "idle"

            return {
                "mission_id": mission_id,
                "status": "aborted",
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }

        return {"status": "no_active_mission"}

    async def _handle_get_mission_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get current mission status."""
        if not self._current_mission:
            return {"status": "no_active_mission"}

        return {
            "mission": self._current_mission,
            "progress_percent": random.randint(0, 100),
            "current_step": random.randint(1, len(self._current_mission["steps"])),
            "obstacles_encountered": random.randint(0, 5),
            "replanning_count": random.randint(0, 3)
        }

    async def _handle_safety_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive safety check."""
        checks = {
            "emergency_stop_ready": True,
            "collision_avoidance_active": True,
            "human_detection_active": True,
            "speed_within_limits": True,
            "battery_level_ok": random.uniform(20, 100) > 15,
            "communication_stable": True,
            "sensors_operational": random.uniform(0.9, 1.0) > 0.8,
            "motor_temperatures_ok": True,
            "payload_within_limits": True
        }

        all_passed = all(checks.values())
        self._safety_status = "nominal" if all_passed else "warning"

        return {
            "overall_status": self._safety_status,
            "all_checks_passed": all_passed,
            "checks": checks,
            "autonomy_level": self._autonomy_level,
            "can_operate": all_passed,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_set_autonomy_level(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Set robot autonomy level (0-5 like SAE driving levels)."""
        level = payload.get("level", self._autonomy_level)
        level = max(0, min(5, level))

        old_level = self._autonomy_level
        self._autonomy_level = level

        level_descriptions = {
            0: "No Automation - Full human control",
            1: "Assistance - Robot assists human operator",
            2: "Partial Automation - Robot handles some tasks",
            3: "Conditional Automation - Robot operates with human supervision",
            4: "High Automation - Robot operates independently, human backup",
            5: "Full Automation - Complete autonomous operation"
        }

        return {
            "previous_level": old_level,
            "new_level": level,
            "description": level_descriptions[level],
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_behavior_tree(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get current behavior tree state."""
        return {
            "current_behavior": self._behavior_state,
            "behavior_tree": {
                "root": "Selector",
                "children": [
                    {
                        "name": "SafetyCheck",
                        "type": "Sequence",
                        "status": "success"
                    },
                    {
                        "name": "ExecuteMission",
                        "type": "Sequence",
                        "status": "running" if self._behavior_state == "executing_mission" else "idle",
                        "children": [
                            {"name": "Navigate", "type": "Action", "status": "running"},
                            {"name": "AvoidObstacles", "type": "Action", "status": "success"},
                            {"name": "MonitorHumans", "type": "Action", "status": "success"}
                        ]
                    },
                    {
                        "name": "Idle",
                        "type": "Action",
                        "status": "success" if self._behavior_state == "idle" else "idle"
                    }
                ]
            },
            "tick_rate_hz": 10,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_human_override(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle human override of autonomous behavior."""
        override_type = payload.get("type", "pause")

        if override_type == "pause":
            self._behavior_state = "paused_human_override"
        elif override_type == "stop":
            self._behavior_state = "stopped"
            if self._current_mission:
                self._current_mission["status"] = "paused"
        elif override_type == "resume":
            self._behavior_state = "executing_mission" if self._current_mission else "idle"

        return {
            "override_type": override_type,
            "behavior_state": self._behavior_state,
            "autonomy_level": self._autonomy_level,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "autonomy_level": self._autonomy_level,
            "safety_status": self._safety_status,
            "behavior_state": self._behavior_state,
            "missions_completed": len(self._mission_history),
            "has_active_mission": self._current_mission is not None
        }

    def _generate_mission_steps(self, mission_type: str) -> List[Dict]:
        """Generate mission steps based on type."""
        if mission_type == "navigation":
            return [
                {"step": 1, "action": "plan_path", "status": "pending"},
                {"step": 2, "action": "safety_check", "status": "pending"},
                {"step": 3, "action": "navigate", "status": "pending"},
                {"step": 4, "action": "arrive", "status": "pending"}
            ]
        elif mission_type == "manipulation":
            return [
                {"step": 1, "action": "approach_target", "status": "pending"},
                {"step": 2, "action": "identify_object", "status": "pending"},
                {"step": 3, "action": "plan_grasp", "status": "pending"},
                {"step": 4, "action": "execute_grasp", "status": "pending"},
                {"step": 5, "action": "verify_grasp", "status": "pending"}
            ]
        elif mission_type == "inspection":
            return [
                {"step": 1, "action": "navigate_to_area", "status": "pending"},
                {"step": 2, "action": "scan_environment", "status": "pending"},
                {"step": 3, "action": "analyze_data", "status": "pending"},
                {"step": 4, "action": "generate_report", "status": "pending"}
            ]
        else:
            return [{"step": 1, "action": "execute", "status": "pending"}]
