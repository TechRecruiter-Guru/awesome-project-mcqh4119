"""
PhysicalAI Command Center - Agentic System for Robotics & Autonomous Systems
Enterprise-grade multi-agent platform for Physical AI, Humanoids, and Robotics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import asyncio
from functools import wraps
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS - allow all origins
CORS(app)

# Initialize database
from core.database import db, init_db
init_db(app)

# Initialize ALL agents including robotics agents
from agents import (
    OrchestratorAgent, GatewayAgent, DataAgent, IntegrationAgent,
    MotionAgent, SensorAgent, VisionAgent, AutonomyAgent
)

orchestrator = OrchestratorAgent()
gateway = GatewayAgent()
data_agent = DataAgent()
integration_agent = IntegrationAgent()
motion_agent = MotionAgent()
sensor_agent = SensorAgent()
vision_agent = VisionAgent()
autonomy_agent = AutonomyAgent()

# Register ALL agents with orchestrator
orchestrator.register_agent(gateway)
orchestrator.register_agent(data_agent)
orchestrator.register_agent(integration_agent)
orchestrator.register_agent(motion_agent)
orchestrator.register_agent(sensor_agent)
orchestrator.register_agent(vision_agent)
orchestrator.register_agent(autonomy_agent)


def run_async(func):
    """Decorator to run async functions in Flask."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper


# ============== ROOT & HEALTH ==============

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "PhysicalAI Command Center",
        "company": "VanguardLab",
        "version": "2.0.0",
        "architecture": "multi-agent-robotics",
        "status": "operational",
        "capabilities": [
            "Motion Planning",
            "Sensor Fusion",
            "Computer Vision",
            "Autonomous Navigation",
            "Human-Robot Interaction"
        ],
        "agents": {
            "core": ["orchestrator", "gateway", "data", "integration"],
            "robotics": ["motion", "sensor", "vision", "autonomy"]
        },
        "endpoints": {
            "health": "/api/health",
            "agents": "/api/agents",
            "robot": "/api/robot",
            "mission": "/api/mission",
            "sensors": "/api/sensors",
            "vision": "/api/vision"
        },
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "PhysicalAI Command Center",
        "uptime": "operational",
        "agents_ready": True,
        "timestamp": datetime.utcnow().isoformat()
    })


# ============== AGENT ROUTES ==============

@app.route('/api/agents', methods=['GET'])
@run_async
async def get_agents_status():
    """Get status of all agents."""
    await orchestrator.start()
    status = orchestrator.get_all_agents_status()
    return jsonify(status)


@app.route('/api/agents/<agent_name>/action', methods=['POST'])
@run_async
async def agent_action(agent_name):
    """Execute an action on a specific agent."""
    await orchestrator.start()

    data = request.get_json() or {}
    action = data.get('action')
    payload = data.get('payload', {})

    if not action:
        return jsonify({"error": "Action is required"}), 400

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api",
        target=agent_name,
        action=action,
        payload=payload
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify({"success": True, "data": response.data})
    else:
        return jsonify({"success": False, "error": response.error}), 400


# ============== ROBOT CONTROL ROUTES ==============

@app.route('/api/robot/position', methods=['GET'])
@run_async
async def get_robot_position():
    """Get current robot position."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="motion", action="get_position", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/robot/move', methods=['POST'])
@run_async
async def move_robot():
    """Plan and execute robot movement."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage

    # First plan trajectory
    plan_message = AgentMessage(
        source="api", target="motion", action="plan_trajectory",
        payload={"target": data.get("target", {}), "speed": data.get("speed", 0.5)}
    )
    plan_response = await orchestrator.route_message(plan_message)

    if not plan_response.success:
        return jsonify({"error": plan_response.error}), 400

    # Execute if auto_execute is true
    if data.get("auto_execute", False):
        exec_message = AgentMessage(
            source="api", target="motion", action="execute_motion",
            payload={"target": data.get("target", {})}
        )
        exec_response = await orchestrator.route_message(exec_message)
        return jsonify({
            "trajectory": plan_response.data,
            "execution": exec_response.data if exec_response.success else {"error": exec_response.error}
        })

    return jsonify({"trajectory": plan_response.data, "status": "planned"})


@app.route('/api/robot/status', methods=['GET'])
@run_async
async def get_robot_status():
    """Get comprehensive robot status."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage

    # Get status from multiple agents
    motion_msg = AgentMessage(source="api", target="motion", action="get_stats", payload={})
    sensor_msg = AgentMessage(source="api", target="sensor", action="get_stats", payload={})
    autonomy_msg = AgentMessage(source="api", target="autonomy", action="get_stats", payload={})

    motion_resp = await orchestrator.route_message(motion_msg)
    sensor_resp = await orchestrator.route_message(sensor_msg)
    autonomy_resp = await orchestrator.route_message(autonomy_msg)

    return jsonify({
        "motion": motion_resp.data if motion_resp.success else {},
        "sensors": sensor_resp.data if sensor_resp.success else {},
        "autonomy": autonomy_resp.data if autonomy_resp.success else {},
        "timestamp": datetime.utcnow().isoformat()
    })


# ============== SENSOR ROUTES ==============

@app.route('/api/sensors', methods=['GET'])
@run_async
async def get_all_sensor_readings():
    """Get readings from all sensors."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="sensor", action="get_all_readings", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/sensors/<sensor_id>', methods=['GET'])
@run_async
async def get_sensor_reading(sensor_id):
    """Get reading from specific sensor."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="sensor", action="get_reading",
        payload={"sensor_id": sensor_id}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/sensors/obstacles', methods=['GET'])
@run_async
async def detect_obstacles():
    """Detect obstacles in environment."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="sensor", action="detect_obstacles", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/sensors/fusion', methods=['GET'])
@run_async
async def sensor_fusion():
    """Get fused sensor data for localization."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="sensor", action="fuse_sensors", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


# ============== VISION ROUTES ==============

@app.route('/api/vision/detect', methods=['GET'])
@run_async
async def detect_objects():
    """Detect objects in camera view."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="vision", action="detect_objects", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/vision/pose', methods=['GET'])
@run_async
async def estimate_pose():
    """Estimate human pose for HRI."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="vision", action="estimate_pose", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/vision/gesture', methods=['GET'])
@run_async
async def recognize_gesture():
    """Recognize hand gestures."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="vision", action="recognize_gesture", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/vision/slam', methods=['GET'])
@run_async
async def visual_slam():
    """Get Visual SLAM data."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="vision", action="visual_slam", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


# ============== MISSION / AUTONOMY ROUTES ==============

@app.route('/api/mission', methods=['GET'])
@run_async
async def get_mission_status():
    """Get current mission status."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="autonomy", action="get_mission_status", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/mission', methods=['POST'])
@run_async
async def plan_mission():
    """Plan a new autonomous mission."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="autonomy", action="plan_mission",
        payload=data
    )
    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    return jsonify({"error": response.error}), 400


@app.route('/api/mission/execute', methods=['POST'])
@run_async
async def execute_mission():
    """Execute planned mission."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="autonomy", action="execute_mission", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/mission/abort', methods=['POST'])
@run_async
async def abort_mission():
    """Abort current mission."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="autonomy", action="abort_mission",
        payload={"reason": data.get("reason", "user_requested")}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/autonomy/level', methods=['GET', 'POST'])
@run_async
async def autonomy_level():
    """Get or set autonomy level."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage

    if request.method == 'POST':
        data = request.get_json() or {}
        message = AgentMessage(
            source="api", target="autonomy", action="set_autonomy_level",
            payload={"level": data.get("level", 4)}
        )
    else:
        message = AgentMessage(source="api", target="autonomy", action="get_stats", payload={})

    response = await orchestrator.route_message(message)
    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/autonomy/safety', methods=['GET'])
@run_async
async def safety_check():
    """Perform safety check."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(source="api", target="autonomy", action="safety_check", payload={})
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/autonomy/override', methods=['POST'])
@run_async
async def human_override():
    """Human override of autonomous behavior."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="autonomy", action="human_override",
        payload={"type": data.get("type", "pause")}
    )
    response = await orchestrator.route_message(message)

    return jsonify(response.data if response.success else {"error": response.error})


# ============== TASK ROUTES (via Data Agent) ==============

@app.route('/api/tasks', methods=['GET'])
@run_async
async def get_tasks():
    """Get all tasks."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="data", action="query",
        payload={"table": "tasks", "filters": {}}
    )
    response = await orchestrator.route_message(message)
    return jsonify(response.data if response.success else {"error": response.error})


@app.route('/api/tasks', methods=['POST'])
@run_async
async def create_task():
    """Create a new task."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="data", action="create",
        payload={"table": "tasks", "data": data}
    )
    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    return jsonify({"error": response.error}), 400


# ============== INTEGRATION ROUTES ==============

@app.route('/api/integrate/service', methods=['POST'])
@run_async
async def register_service():
    """Register an external service."""
    await orchestrator.start()
    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api", target="integration", action="register_service",
        payload=data
    )
    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    return jsonify({"error": response.error}), 400


# ============== LIVE DEMO ROUTES ==============
import random
import math

# Demo state (in production, use Redis or database)
demo_state = {
    "robot_position": {"x": 0, "y": 0, "z": 0, "yaw": 0},
    "demo_running": False,
    "waypoint_index": 0,
    "detected_objects": [],
    "sensor_history": []
}

DEMO_WAYPOINTS = [
    {"x": 0, "y": 0, "z": 0},
    {"x": 2, "y": 0, "z": 0},
    {"x": 2, "y": 2, "z": 0},
    {"x": 0, "y": 2, "z": 0},
    {"x": 0, "y": 0, "z": 0},
]

@app.route('/api/demo/start', methods=['POST'])
def start_demo():
    """Start live demo mode."""
    demo_state["demo_running"] = True
    demo_state["waypoint_index"] = 0
    demo_state["robot_position"] = {"x": 0, "y": 0, "z": 0, "yaw": 0}
    return jsonify({
        "status": "demo_started",
        "message": "Live demo mode activated",
        "waypoints": len(DEMO_WAYPOINTS)
    })

@app.route('/api/demo/stop', methods=['POST'])
def stop_demo():
    """Stop live demo mode."""
    demo_state["demo_running"] = False
    return jsonify({"status": "demo_stopped"})

@app.route('/api/demo/state', methods=['GET'])
def get_demo_state():
    """Get current demo state with simulated real-time data."""
    # Simulate robot movement if demo is running
    if demo_state["demo_running"]:
        target = DEMO_WAYPOINTS[demo_state["waypoint_index"]]
        pos = demo_state["robot_position"]

        # Move towards target
        dx = target["x"] - pos["x"]
        dy = target["y"] - pos["y"]
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < 0.1:
            # Reached waypoint, go to next
            demo_state["waypoint_index"] = (demo_state["waypoint_index"] + 1) % len(DEMO_WAYPOINTS)
        else:
            # Move towards target
            speed = 0.15
            pos["x"] += (dx / dist) * speed
            pos["y"] += (dy / dist) * speed
            pos["yaw"] = math.degrees(math.atan2(dy, dx))

    # Generate simulated sensor data
    lidar_points = []
    for i in range(36):
        angle = i * 10
        distance = random.uniform(1.5, 8.0)
        # Add some obstacles
        if 30 < angle < 60 and random.random() > 0.7:
            distance = random.uniform(0.5, 2.0)
        lidar_points.append({"angle": angle, "distance": round(distance, 2)})

    # Simulate detected objects
    objects = []
    if random.random() > 0.5:
        obj_types = ["person", "box", "pallet", "forklift", "robot"]
        for i in range(random.randint(1, 4)):
            objects.append({
                "id": i,
                "type": random.choice(obj_types),
                "x": round(random.uniform(-3, 3), 2),
                "y": round(random.uniform(0.5, 5), 2),
                "confidence": round(random.uniform(0.85, 0.99), 2)
            })

    return jsonify({
        "demo_running": demo_state["demo_running"],
        "robot": {
            "position": {
                "x": round(demo_state["robot_position"]["x"], 3),
                "y": round(demo_state["robot_position"]["y"], 3),
                "z": round(demo_state["robot_position"]["z"], 3)
            },
            "yaw": round(demo_state["robot_position"]["yaw"], 1),
            "velocity": round(random.uniform(0.3, 0.8), 2) if demo_state["demo_running"] else 0,
            "battery": round(random.uniform(75, 95), 1),
            "status": "moving" if demo_state["demo_running"] else "idle"
        },
        "sensors": {
            "lidar": lidar_points,
            "imu": {
                "accel": {"x": round(random.uniform(-0.1, 0.1), 3), "y": round(random.uniform(-0.1, 0.1), 3), "z": round(9.81 + random.uniform(-0.05, 0.05), 3)},
                "gyro": {"x": round(random.uniform(-0.02, 0.02), 3), "y": round(random.uniform(-0.02, 0.02), 3), "z": round(random.uniform(-0.02, 0.02), 3)}
            },
            "temperature": round(random.uniform(22, 28), 1),
            "humidity": round(random.uniform(40, 60), 1)
        },
        "vision": {
            "objects": objects,
            "fps": round(random.uniform(28, 32), 1)
        },
        "mission": {
            "current_waypoint": demo_state["waypoint_index"],
            "total_waypoints": len(DEMO_WAYPOINTS),
            "progress": round((demo_state["waypoint_index"] / len(DEMO_WAYPOINTS)) * 100, 1)
        },
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/demo/scenarios', methods=['GET'])
def get_demo_scenarios():
    """Get available demo scenarios."""
    return jsonify({
        "scenarios": [
            {
                "id": "warehouse_patrol",
                "name": "Warehouse Patrol",
                "description": "Robot patrols warehouse, detecting obstacles and inventory",
                "duration": "60s"
            },
            {
                "id": "pick_and_place",
                "name": "Pick & Place",
                "description": "Robot identifies objects and performs manipulation tasks",
                "duration": "45s"
            },
            {
                "id": "human_following",
                "name": "Human Following",
                "description": "Robot tracks and follows human using vision",
                "duration": "30s"
            },
            {
                "id": "autonomous_nav",
                "name": "Autonomous Navigation",
                "description": "Robot navigates through obstacles to reach goal",
                "duration": "90s"
            }
        ]
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
