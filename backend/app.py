"""Main Flask application with Agentic System."""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import asyncio
from functools import wraps

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

# Initialize agents
from agents import OrchestratorAgent, GatewayAgent, DataAgent, IntegrationAgent

orchestrator = OrchestratorAgent()
gateway = GatewayAgent()
data_agent = DataAgent()
integration_agent = IntegrationAgent()

# Register agents with orchestrator
orchestrator.register_agent(gateway)
orchestrator.register_agent(data_agent)
orchestrator.register_agent(integration_agent)


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


# ============== BASIC ROUTES ==============

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "awesome-project-api",
        "status": "running",
        "version": "1.0.0",
        "architecture": "agentic",
        "endpoints": {
            "health": "/api/health",
            "hello": "/api/hello",
            "agents": "/api/agents",
            "tasks": "/api/tasks"
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})


@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from awesome-project-mcqh4119!"})


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


# ============== TASK ROUTES (via Data Agent) ==============

@app.route('/api/tasks', methods=['GET'])
@run_async
async def get_tasks():
    """Get all tasks."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api",
        target="data",
        action="query",
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
        source="api",
        target="data",
        action="create",
        payload={"table": "tasks", "data": data}
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    else:
        return jsonify({"error": response.error}), 400


@app.route('/api/tasks/<task_id>', methods=['PUT'])
@run_async
async def update_task(task_id):
    """Update a task."""
    await orchestrator.start()

    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api",
        target="data",
        action="update",
        payload={"table": "tasks", "id": task_id, "data": data}
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data)
    else:
        return jsonify({"error": response.error}), 400


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@run_async
async def delete_task(task_id):
    """Delete a task."""
    await orchestrator.start()

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api",
        target="data",
        action="delete",
        payload={"table": "tasks", "id": task_id}
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data)
    else:
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
        source="api",
        target="integration",
        action="register_service",
        payload=data
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    else:
        return jsonify({"error": response.error}), 400


@app.route('/api/integrate/call', methods=['POST'])
@run_async
async def call_service():
    """Call an external service."""
    await orchestrator.start()

    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api",
        target="integration",
        action="call_service",
        payload=data
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data)
    else:
        return jsonify({"error": response.error}), 400


@app.route('/api/integrate/webhook', methods=['POST'])
@run_async
async def register_webhook():
    """Register a webhook."""
    await orchestrator.start()

    data = request.get_json() or {}

    from agents.base_agent import AgentMessage
    message = AgentMessage(
        source="api",
        target="integration",
        action="register_webhook",
        payload=data
    )

    response = await orchestrator.route_message(message)

    if response.success:
        return jsonify(response.data), 201
    else:
        return jsonify({"error": response.error}), 400


# ============== WORKFLOW ROUTES ==============

@app.route('/api/workflow/<workflow_name>', methods=['POST'])
@run_async
async def execute_workflow(workflow_name):
    """Execute a registered workflow."""
    await orchestrator.start()

    data = request.get_json() or {}
    response = await orchestrator.execute_workflow(workflow_name, data)

    if response.success:
        return jsonify({"workflow": workflow_name, "results": response.data})
    else:
        return jsonify({"error": response.error}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
