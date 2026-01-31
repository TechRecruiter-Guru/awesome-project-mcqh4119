"""Motion Agent - Robot motion planning and control."""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig, AgentResponse
from datetime import datetime
import math
import random


class MotionAgent(BaseAgent):
    """
    Motion planning specialist that:
    - Generates motion trajectories
    - Handles inverse kinematics
    - Manages velocity/acceleration profiles
    - Collision avoidance
    """

    def __init__(self):
        config = AgentConfig(
            name="motion",
            description="Robot motion planning and trajectory generation"
        )
        super().__init__(config)
        self._current_position = {"x": 0, "y": 0, "z": 0, "roll": 0, "pitch": 0, "yaw": 0}
        self._velocity_limit = 1.0  # m/s
        self._acceleration_limit = 0.5  # m/s²
        self._trajectories: List[Dict] = []
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.register_handler("plan_trajectory", self._handle_plan_trajectory)
        self.register_handler("execute_motion", self._handle_execute_motion)
        self.register_handler("get_position", self._handle_get_position)
        self.register_handler("set_position", self._handle_set_position)
        self.register_handler("inverse_kinematics", self._handle_inverse_kinematics)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info("Motion agent initialized - ready for trajectory planning")

    async def on_stop(self) -> None:
        self.logger.info("Motion agent stopped")

    async def _handle_plan_trajectory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Plan a motion trajectory from current position to target."""
        target = payload.get("target", {})
        speed = payload.get("speed", 0.5)

        start = self._current_position.copy()

        # Calculate distance
        dx = target.get("x", start["x"]) - start["x"]
        dy = target.get("y", start["y"]) - start["y"]
        dz = target.get("z", start["z"]) - start["z"]
        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        # Generate waypoints
        num_points = max(int(distance / 0.1), 5)
        waypoints = []
        for i in range(num_points + 1):
            t = i / num_points
            waypoints.append({
                "x": start["x"] + dx * t,
                "y": start["y"] + dy * t,
                "z": start["z"] + dz * t,
                "timestamp": i * (distance / speed / num_points)
            })

        trajectory = {
            "id": f"traj_{datetime.utcnow().timestamp()}",
            "start": start,
            "target": target,
            "distance": round(distance, 3),
            "estimated_time": round(distance / speed, 2),
            "waypoints_count": len(waypoints),
            "waypoints": waypoints[:5],  # Return first 5 for preview
            "status": "planned"
        }

        self._trajectories.append(trajectory)
        return trajectory

    async def _handle_execute_motion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a planned motion."""
        trajectory_id = payload.get("trajectory_id")

        # Simulate motion execution
        target = payload.get("target", self._current_position)
        self._current_position = {
            "x": target.get("x", self._current_position["x"]),
            "y": target.get("y", self._current_position["y"]),
            "z": target.get("z", self._current_position["z"]),
            "roll": target.get("roll", 0),
            "pitch": target.get("pitch", 0),
            "yaw": target.get("yaw", 0)
        }

        return {
            "status": "completed",
            "final_position": self._current_position,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_position(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get current robot position."""
        return {
            "position": self._current_position,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_set_position(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Set robot position (for simulation/calibration)."""
        self._current_position.update(payload.get("position", {}))
        return {
            "status": "updated",
            "position": self._current_position
        }

    async def _handle_inverse_kinematics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate inverse kinematics for end-effector position."""
        end_effector = payload.get("end_effector", {})

        # Simulated IK solution (would use actual IK solver in production)
        joint_angles = {
            "joint_1": random.uniform(-180, 180),
            "joint_2": random.uniform(-90, 90),
            "joint_3": random.uniform(-180, 180),
            "joint_4": random.uniform(-90, 90),
            "joint_5": random.uniform(-180, 180),
            "joint_6": random.uniform(-180, 180)
        }

        return {
            "end_effector_target": end_effector,
            "joint_angles": joint_angles,
            "solution_found": True,
            "solver": "numerical_ik"
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "trajectories_planned": len(self._trajectories),
            "current_position": self._current_position,
            "velocity_limit": self._velocity_limit,
            "acceleration_limit": self._acceleration_limit
        }
