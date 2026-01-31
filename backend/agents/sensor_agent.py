"""Sensor Agent - Robot sensor data processing and fusion."""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentConfig
from datetime import datetime
import random
import math


class SensorAgent(BaseAgent):
    """
    Sensor processing specialist that:
    - Aggregates multi-sensor data
    - Performs sensor fusion
    - Detects anomalies
    - Provides environmental awareness
    """

    def __init__(self):
        config = AgentConfig(
            name="sensor",
            description="Multi-sensor data fusion and environmental awareness"
        )
        super().__init__(config)
        self._sensors: Dict[str, Dict] = {}
        self._readings: List[Dict] = []
        self._alerts: List[Dict] = []
        self._init_default_sensors()
        self._register_handlers()

    def _init_default_sensors(self):
        """Initialize default sensor configuration."""
        self._sensors = {
            "lidar_front": {"type": "lidar", "range": 30.0, "fov": 180, "status": "active"},
            "lidar_rear": {"type": "lidar", "range": 30.0, "fov": 180, "status": "active"},
            "camera_rgb": {"type": "camera", "resolution": "1920x1080", "fps": 30, "status": "active"},
            "camera_depth": {"type": "depth_camera", "resolution": "640x480", "fps": 30, "status": "active"},
            "imu": {"type": "imu", "axes": 9, "rate": 100, "status": "active"},
            "gps": {"type": "gps", "accuracy": 0.01, "status": "active"},
            "force_torque": {"type": "force_torque", "axes": 6, "status": "active"},
            "proximity": {"type": "proximity", "range": 2.0, "count": 8, "status": "active"}
        }

    def _register_handlers(self) -> None:
        self.register_handler("get_reading", self._handle_get_reading)
        self.register_handler("get_all_readings", self._handle_get_all_readings)
        self.register_handler("fuse_sensors", self._handle_fuse_sensors)
        self.register_handler("detect_obstacles", self._handle_detect_obstacles)
        self.register_handler("get_environment", self._handle_get_environment)
        self.register_handler("calibrate", self._handle_calibrate)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        self.logger.info(f"Sensor agent initialized with {len(self._sensors)} sensors")

    async def on_stop(self) -> None:
        self.logger.info("Sensor agent stopped")

    async def _handle_get_reading(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get reading from specific sensor."""
        sensor_id = payload.get("sensor_id", "lidar_front")

        if sensor_id not in self._sensors:
            raise ValueError(f"Unknown sensor: {sensor_id}")

        sensor = self._sensors[sensor_id]
        reading = self._generate_sensor_reading(sensor_id, sensor)

        self._readings.append(reading)
        return reading

    async def _handle_get_all_readings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get readings from all sensors."""
        readings = {}
        for sensor_id, sensor in self._sensors.items():
            readings[sensor_id] = self._generate_sensor_reading(sensor_id, sensor)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_count": len(readings),
            "readings": readings
        }

    async def _handle_fuse_sensors(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform sensor fusion for localization."""
        # Simulated sensor fusion result
        return {
            "fused_position": {
                "x": random.uniform(-0.01, 0.01),
                "y": random.uniform(-0.01, 0.01),
                "z": 0.0,
                "confidence": random.uniform(0.95, 0.99)
            },
            "fused_orientation": {
                "roll": random.uniform(-0.5, 0.5),
                "pitch": random.uniform(-0.5, 0.5),
                "yaw": random.uniform(-180, 180),
                "confidence": random.uniform(0.95, 0.99)
            },
            "velocity": {
                "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
            },
            "fusion_method": "extended_kalman_filter",
            "sensors_used": list(self._sensors.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_detect_obstacles(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Detect obstacles in environment."""
        num_obstacles = random.randint(0, 5)
        obstacles = []

        for i in range(num_obstacles):
            obstacles.append({
                "id": f"obstacle_{i}",
                "type": random.choice(["static", "dynamic", "human", "vehicle"]),
                "position": {
                    "x": random.uniform(0.5, 10),
                    "y": random.uniform(-5, 5),
                    "z": random.uniform(0, 2)
                },
                "size": {
                    "width": random.uniform(0.1, 2),
                    "height": random.uniform(0.1, 2),
                    "depth": random.uniform(0.1, 2)
                },
                "velocity": {
                    "x": random.uniform(-1, 1),
                    "y": random.uniform(-1, 1)
                },
                "confidence": random.uniform(0.8, 0.99)
            })

        return {
            "obstacle_count": num_obstacles,
            "obstacles": obstacles,
            "scan_time_ms": random.uniform(10, 50),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_environment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get environmental conditions."""
        return {
            "temperature": random.uniform(18, 28),
            "humidity": random.uniform(30, 70),
            "light_level": random.uniform(100, 1000),
            "air_quality_index": random.randint(0, 100),
            "noise_level_db": random.uniform(30, 80),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_calibrate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calibrate sensors."""
        sensor_id = payload.get("sensor_id", "all")

        if sensor_id == "all":
            calibrated = list(self._sensors.keys())
        else:
            calibrated = [sensor_id]

        return {
            "calibrated_sensors": calibrated,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "total_sensors": len(self._sensors),
            "active_sensors": sum(1 for s in self._sensors.values() if s["status"] == "active"),
            "total_readings": len(self._readings),
            "alerts": len(self._alerts),
            "sensors": list(self._sensors.keys())
        }

    def _generate_sensor_reading(self, sensor_id: str, sensor: Dict) -> Dict[str, Any]:
        """Generate simulated sensor reading."""
        sensor_type = sensor["type"]

        if sensor_type == "lidar":
            return {
                "sensor_id": sensor_id,
                "type": sensor_type,
                "points": random.randint(10000, 50000),
                "min_distance": random.uniform(0.1, 1),
                "max_distance": random.uniform(20, 30),
                "timestamp": datetime.utcnow().isoformat()
            }
        elif sensor_type in ["camera", "depth_camera"]:
            return {
                "sensor_id": sensor_id,
                "type": sensor_type,
                "frame_id": random.randint(1, 10000),
                "resolution": sensor.get("resolution"),
                "timestamp": datetime.utcnow().isoformat()
            }
        elif sensor_type == "imu":
            return {
                "sensor_id": sensor_id,
                "type": sensor_type,
                "acceleration": {"x": random.uniform(-0.1, 0.1), "y": random.uniform(-0.1, 0.1), "z": 9.81},
                "gyroscope": {"x": random.uniform(-0.01, 0.01), "y": random.uniform(-0.01, 0.01), "z": random.uniform(-0.01, 0.01)},
                "magnetometer": {"x": random.uniform(-50, 50), "y": random.uniform(-50, 50), "z": random.uniform(-50, 50)},
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "sensor_id": sensor_id,
                "type": sensor_type,
                "value": random.uniform(0, 100),
                "timestamp": datetime.utcnow().isoformat()
            }
