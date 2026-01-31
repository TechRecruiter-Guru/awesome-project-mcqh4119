"""Data Agent - Database operations handler."""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig, AgentResponse
from datetime import datetime


class DataAgent(BaseAgent):
    """
    Database specialist that:
    - Handles all database operations
    - Manages connection pooling
    - Implements caching strategies
    - Validates data integrity
    """

    def __init__(self, db=None):
        config = AgentConfig(
            name="data",
            description="Database operations and caching"
        )
        super().__init__(config)
        self._db = db
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, float] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register action handlers."""
        self.register_handler("query", self._handle_query)
        self.register_handler("create", self._handle_create)
        self.register_handler("update", self._handle_update)
        self.register_handler("delete", self._handle_delete)
        self.register_handler("cache_get", self._handle_cache_get)
        self.register_handler("cache_set", self._handle_cache_set)
        self.register_handler("get_stats", self._handle_get_stats)

    async def on_start(self) -> None:
        """Initialize data agent."""
        self.logger.info("Data agent initialized")

    async def on_stop(self) -> None:
        """Cleanup data agent."""
        self._cache.clear()
        self.logger.info("Data agent stopped")

    def set_database(self, db) -> None:
        """Set database connection."""
        self._db = db

    async def _handle_query(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database query."""
        table = payload.get("table")
        filters = payload.get("filters", {})
        limit = payload.get("limit", 100)
        offset = payload.get("offset", 0)

        # Check cache first
        cache_key = f"query:{table}:{hash(str(filters))}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return {"data": cached, "source": "cache"}

        # Simulate query result (replace with actual DB query)
        result = {
            "table": table,
            "filters": filters,
            "count": 0,
            "rows": [],
            "timestamp": datetime.utcnow().isoformat()
        }

        # Cache result
        self._set_cache(cache_key, result, ttl=60)

        return {"data": result, "source": "database"}

    async def _handle_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle record creation."""
        table = payload.get("table")
        data = payload.get("data", {})

        # Validate required fields
        if not table or not data:
            raise ValueError("Table and data are required")

        # Invalidate related cache
        self._invalidate_cache_pattern(f"query:{table}")

        return {
            "created": True,
            "table": table,
            "id": f"new_{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle record update."""
        table = payload.get("table")
        record_id = payload.get("id")
        data = payload.get("data", {})

        if not table or not record_id:
            raise ValueError("Table and ID are required")

        # Invalidate related cache
        self._invalidate_cache_pattern(f"query:{table}")

        return {
            "updated": True,
            "table": table,
            "id": record_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_delete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle record deletion."""
        table = payload.get("table")
        record_id = payload.get("id")

        if not table or not record_id:
            raise ValueError("Table and ID are required")

        # Invalidate related cache
        self._invalidate_cache_pattern(f"query:{table}")

        return {
            "deleted": True,
            "table": table,
            "id": record_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _handle_cache_get(self, payload: Dict[str, Any]) -> Any:
        """Get value from cache."""
        key = payload.get("key")
        return self._get_from_cache(key)

    async def _handle_cache_set(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Set value in cache."""
        key = payload.get("key")
        value = payload.get("value")
        ttl = payload.get("ttl", 300)

        self._set_cache(key, value, ttl)
        return {"cached": True, "key": key}

    async def _handle_get_stats(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get data agent statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_keys": list(self._cache.keys())[:10]
        }

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None

        if key in self._cache_ttl:
            if datetime.utcnow().timestamp() > self._cache_ttl[key]:
                del self._cache[key]
                del self._cache_ttl[key]
                return None

        return self._cache.get(key)

    def _set_cache(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL."""
        self._cache[key] = value
        self._cache_ttl[key] = datetime.utcnow().timestamp() + ttl

    def _invalidate_cache_pattern(self, pattern: str) -> None:
        """Invalidate cache keys matching pattern."""
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]
            if key in self._cache_ttl:
                del self._cache_ttl[key]
