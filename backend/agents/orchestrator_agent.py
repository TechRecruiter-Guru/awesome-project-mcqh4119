"""Orchestrator Agent - Central coordinator for all agents."""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig, AgentMessage, AgentResponse, AgentStatus
import logging


class OrchestratorAgent(BaseAgent):
    """
    Central coordinator that:
    - Receives requests from Gateway
    - Determines which agents to invoke
    - Manages multi-step workflows
    - Aggregates responses
    """

    def __init__(self):
        config = AgentConfig(
            name="orchestrator",
            description="Central task coordinator and router"
        )
        super().__init__(config)
        self._agents: Dict[str, BaseAgent] = {}
        self._workflows: Dict[str, List[str]] = {}

    async def on_start(self) -> None:
        """Initialize orchestrator."""
        self.logger.info("Orchestrator starting...")
        # Start all registered agents
        for agent in self._agents.values():
            if agent.config.enabled:
                await agent.start()

    async def on_stop(self) -> None:
        """Shutdown orchestrator."""
        self.logger.info("Orchestrator stopping...")
        # Stop all registered agents
        for agent in self._agents.values():
            await agent.stop()

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self._agents[agent.name] = agent
        agent.set_orchestrator(self)
        self.logger.info(f"Registered agent: {agent.name}")

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent."""
        if agent_name in self._agents:
            del self._agents[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)

    async def route_message(self, message: AgentMessage) -> AgentResponse:
        """Route a message to the appropriate agent."""
        target_agent = self._agents.get(message.target)

        if not target_agent:
            return AgentResponse(
                success=False,
                error=f"Agent not found: {message.target}"
            )

        if target_agent.status != AgentStatus.RUNNING:
            return AgentResponse(
                success=False,
                error=f"Agent not running: {message.target}"
            )

        return await target_agent.handle_message(message)

    async def execute_workflow(
        self,
        workflow_name: str,
        initial_payload: Dict[str, Any]
    ) -> AgentResponse:
        """Execute a multi-step workflow."""
        if workflow_name not in self._workflows:
            return AgentResponse(
                success=False,
                error=f"Workflow not found: {workflow_name}"
            )

        steps = self._workflows[workflow_name]
        current_payload = initial_payload
        results = []

        for step in steps:
            agent_name, action = step.split(":")
            response = await self.route_message(AgentMessage(
                source="orchestrator",
                target=agent_name,
                action=action,
                payload=current_payload
            ))

            if not response.success:
                return AgentResponse(
                    success=False,
                    error=f"Workflow failed at step {step}: {response.error}",
                    metadata={"completed_steps": results}
                )

            results.append({"step": step, "result": response.data})
            # Pass result to next step
            if isinstance(response.data, dict):
                current_payload = {**current_payload, **response.data}

        return AgentResponse(
            success=True,
            data=results,
            metadata={"workflow": workflow_name}
        )

    def register_workflow(self, name: str, steps: List[str]) -> None:
        """Register a workflow with ordered steps."""
        self._workflows[name] = steps
        self.logger.info(f"Registered workflow: {name} with {len(steps)} steps")

    def get_all_agents_status(self) -> Dict[str, Any]:
        """Get status of all registered agents."""
        return {
            "orchestrator": self.get_status(),
            "agents": {
                name: agent.get_status()
                for name, agent in self._agents.items()
            },
            "workflows": list(self._workflows.keys())
        }

    async def broadcast(self, action: str, payload: Dict[str, Any]) -> Dict[str, AgentResponse]:
        """Broadcast a message to all agents."""
        responses = {}
        for name, agent in self._agents.items():
            if agent.status == AgentStatus.RUNNING:
                message = AgentMessage(
                    source="orchestrator",
                    target=name,
                    action=action,
                    payload=payload
                )
                responses[name] = await agent.handle_message(message)
        return responses
