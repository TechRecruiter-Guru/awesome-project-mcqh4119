"""Gateway Agent - API entry point and request handler."""

from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentConfig, AgentResponse
from datetime import datetime
import hashlib


class GatewayAgent(BaseAgent):
    """
    Entry point that:
    - Validates incoming requests
    - Handles authentication/authorization
    - Rate limits requests
    - Routes to Orchestrator
    """

    def __init__(self):
        config = AgentConfig(
            name="gateway",
            description="API gateway and request validator"
        )
        super().__init__(config)
        self._rate_limits: Dict[str, list] = {}
        self._request_count = 0
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register action handlers."""
        self.register_handler("validate_request", self._handle_validate)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        """Initialize gateway."""
        self.logger.info("Gateway agent initialized")

    async def on_stop(self) -> None:
        """Cleanup gateway."""
        self.logger.info("Gateway agent stopped")

    async def _handle_validate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an incoming request."""
        self._request_count += 1

        # Basic validation
        required_fields = payload.get("required_fields", [])
        data = payload.get("data", {})

        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return {
            "valid": True,
            "request_id": self._generate_request_id(),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get gateway statistics."""
        return {
            "total_requests": self._request_count,
            "rate_limited_ips": len(self._rate_limits)
        }

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(f"{timestamp}-{self._request_count}".encode()).hexdigest()[:16]

    def check_rate_limit(self, client_ip: str, limit: int = 100, window: int = 60) -> bool:
        """Check if client is rate limited."""
        now = datetime.utcnow().timestamp()

        if client_ip not in self._rate_limits:
            self._rate_limits[client_ip] = []

        # Remove old entries outside window
        self._rate_limits[client_ip] = [
            t for t in self._rate_limits[client_ip]
            if now - t < window
        ]

        if len(self._rate_limits[client_ip]) >= limit:
            return False

        self._rate_limits[client_ip].append(now)
        return True

    async def process_request(
        self,
        endpoint: str,
        method: str,
        data: Dict[str, Any],
        client_ip: str = "unknown"
    ) -> AgentResponse:
        """Process an incoming API request."""
        self._request_count += 1

        # Check rate limit
        if not self.check_rate_limit(client_ip):
            return AgentResponse(
                success=False,
                error="Rate limit exceeded",
                metadata={"status_code": 429}
            )

        # Route to appropriate agent via orchestrator
        if not self._orchestrator:
            return AgentResponse(
                success=False,
                error="Gateway not connected to orchestrator"
            )

        # Determine target agent based on endpoint
        agent_mapping = {
            "/data": ("data", "query"),
            "/integrate": ("integration", "fetch"),
            "/status": ("orchestrator", "status")
        }

        for prefix, (agent, action) in agent_mapping.items():
            if endpoint.startswith(prefix):
                return await self.send_message(agent, action, data)

        return AgentResponse(
            success=False,
            error=f"Unknown endpoint: {endpoint}",
            metadata={"status_code": 404}
        )
