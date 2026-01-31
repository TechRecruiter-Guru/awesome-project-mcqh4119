"""Integration Agent - External services handler."""

from typing import Dict, Any, Optional, Callable
from .base_agent import BaseAgent, AgentConfig, AgentResponse
from datetime import datetime
import asyncio


class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(self, failure_threshold: int = 5, recovery_time: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open

    def can_execute(self) -> bool:
        """Check if circuit allows execution."""
        if self.state == "closed":
            return True

        if self.state == "open":
            if datetime.utcnow().timestamp() - self.last_failure_time > self.recovery_time:
                self.state = "half-open"
                return True
            return False

        return True  # half-open allows one attempt

    def record_success(self) -> None:
        """Record successful call."""
        self.failures = 0
        self.state = "closed"

    def record_failure(self) -> None:
        """Record failed call."""
        self.failures += 1
        self.last_failure_time = datetime.utcnow().timestamp()

        if self.failures >= self.failure_threshold:
            self.state = "open"


class IntegrationAgent(BaseAgent):
    """
    External communication specialist that:
    - Manages API connections to external services
    - Handles retries and circuit breaking
    - Processes webhooks
    - Manages API rate limits
    """

    def __init__(self):
        config = AgentConfig(
            name="integration",
            description="External API integrations and webhooks"
        )
        super().__init__(config)
        self._services: Dict[str, Dict[str, Any]] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._webhooks: Dict[str, Callable] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register action handlers."""
        self.register_handler("fetch", self._handle_fetch)
        self.register_handler("register_service", self._handle_register_service)
        self.register_handler("call_service", self._handle_call_service)
        self.register_handler("register_webhook", self._handle_register_webhook)
        self.register_handler("trigger_webhook", self._handle_trigger_webhook)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        """Initialize integration agent."""
        self.logger.info("Integration agent initialized")

    async def on_stop(self) -> None:
        """Cleanup integration agent."""
        self.logger.info("Integration agent stopped")

    async def _handle_fetch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from external URL."""
        url = payload.get("url")
        method = payload.get("method", "GET")
        headers = payload.get("headers", {})
        data = payload.get("data")

        if not url:
            raise ValueError("URL is required")

        # Simulate external API call
        return {
            "url": url,
            "method": method,
            "status": 200,
            "response": {"message": "Simulated response"},
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_register_service(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register an external service."""
        name = payload.get("name")
        base_url = payload.get("base_url")
        api_key = payload.get("api_key")
        headers = payload.get("headers", {})

        if not name or not base_url:
            raise ValueError("Name and base_url are required")

        self._services[name] = {
            "base_url": base_url,
            "api_key": api_key,
            "headers": headers,
            "registered_at": datetime.utcnow().isoformat()
        }

        self._circuit_breakers[name] = CircuitBreaker()

        return {"registered": True, "service": name}

    async def _handle_call_service(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered external service."""
        service_name = payload.get("service")
        endpoint = payload.get("endpoint", "")
        method = payload.get("method", "GET")
        data = payload.get("data")

        if service_name not in self._services:
            raise ValueError(f"Service not registered: {service_name}")

        circuit = self._circuit_breakers[service_name]
        if not circuit.can_execute():
            raise Exception(f"Circuit breaker open for service: {service_name}")

        try:
            service = self._services[service_name]
            # Simulate service call with retry
            result = await self._call_with_retry(
                url=f"{service['base_url']}{endpoint}",
                method=method,
                headers=service['headers'],
                data=data
            )
            circuit.record_success()
            return result

        except Exception as e:
            circuit.record_failure()
            raise

    async def _call_with_retry(
        self,
        url: str,
        method: str,
        headers: Dict[str, str],
        data: Any,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Call external service with retry logic."""
        last_error = None

        for attempt in range(max_retries):
            try:
                # Simulate API call
                await asyncio.sleep(0.1)  # Simulate network latency

                return {
                    "url": url,
                    "method": method,
                    "status": 200,
                    "response": {"data": "simulated response"},
                    "attempt": attempt + 1,
                    "timestamp": datetime.utcnow().isoformat()
                }

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise last_error or Exception("Max retries exceeded")

    async def _handle_register_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a webhook handler."""
        event = payload.get("event")
        callback_url = payload.get("callback_url")

        if not event:
            raise ValueError("Event name is required")

        webhook_id = f"webhook_{event}_{datetime.utcnow().timestamp()}"
        self._webhooks[webhook_id] = {
            "event": event,
            "callback_url": callback_url,
            "registered_at": datetime.utcnow().isoformat()
        }

        return {"webhook_id": webhook_id, "event": event}

    async def _handle_trigger_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger webhooks for an event."""
        event = payload.get("event")
        data = payload.get("data", {})

        triggered = []
        for webhook_id, webhook in self._webhooks.items():
            if webhook["event"] == event:
                # Simulate webhook call
                triggered.append(webhook_id)

        return {
            "event": event,
            "triggered_webhooks": triggered,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get integration agent statistics."""
        return {
            "registered_services": list(self._services.keys()),
            "webhooks_count": len(self._webhooks),
            "circuit_breaker_states": {
                name: cb.state
                for name, cb in self._circuit_breakers.items()
            }
        }
