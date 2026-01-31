"""Base Agent class for all agents in the system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import logging
import uuid
import asyncio


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    description: str = ""
    max_retries: int = 3
    timeout: float = 30.0
    enabled: bool = True


@dataclass
class AgentMessage:
    """Message passed between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""
    target: str = ""
    action: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "action": self.action,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "retry_count": self.retry_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class AgentResponse:
    """Response from an agent action."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(f"agent.{config.name}")
        self._status = AgentStatus.IDLE
        self._handlers: Dict[str, Callable] = {}
        self._message_queue: List[AgentMessage] = []
        self._orchestrator = None

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def status(self) -> AgentStatus:
        return self._status

    def register_handler(self, action: str, handler: Callable) -> None:
        """Register a handler for a specific action."""
        self._handlers[action] = handler
        self.logger.debug(f"Registered handler for action: {action}")

    def set_orchestrator(self, orchestrator: 'BaseAgent') -> None:
        """Set the orchestrator for this agent."""
        self._orchestrator = orchestrator

    async def start(self) -> None:
        """Start the agent."""
        self.logger.info(f"Starting agent: {self.config.name}")
        self._status = AgentStatus.RUNNING
        await self.on_start()

    async def stop(self) -> None:
        """Stop the agent gracefully."""
        self.logger.info(f"Stopping agent: {self.config.name}")
        self._status = AgentStatus.STOPPED
        await self.on_stop()

    @abstractmethod
    async def on_start(self) -> None:
        """Called when agent starts. Override in subclass."""
        pass

    @abstractmethod
    async def on_stop(self) -> None:
        """Called when agent stops. Override in subclass."""
        pass

    async def handle_message(self, message: AgentMessage) -> AgentResponse:
        """Handle incoming message by routing to appropriate handler."""
        self.logger.debug(f"Handling message: {message.action}")

        handler = self._handlers.get(message.action)
        if not handler:
            return AgentResponse(
                success=False,
                error=f"No handler for action: {message.action}"
            )

        try:
            result = await handler(message.payload)
            return AgentResponse(success=True, data=result)
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            return AgentResponse(success=False, error=str(e))

    async def send_message(
        self,
        target: str,
        action: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> AgentResponse:
        """Send message to another agent via orchestrator."""
        if not self._orchestrator:
            return AgentResponse(
                success=False,
                error="No orchestrator configured"
            )

        message = AgentMessage(
            source=self.name,
            target=target,
            action=action,
            payload=payload,
            correlation_id=correlation_id or str(uuid.uuid4())
        )

        return await self._orchestrator.route_message(message)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "status": self._status.value,
            "enabled": self.config.enabled,
            "handlers": list(self._handlers.keys())
        }
