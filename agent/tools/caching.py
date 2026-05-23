"""Caching and rate limiting tools."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class Cache:
    """Simple file-based cache with TTL."""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, key: str) -> Path:
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        path = self._key_path(key)
        if not path.exists():
            return None

        try:
            with open(path) as f:
                data = json.load(f)

            # Check TTL
            if data.get("expires") and time.time() > data["expires"]:
                path.unlink()
                return None

            return data["value"]
        except:
            return None

    def set(self, key: str, value: str, ttl: int = 3600):
        """Set value in cache with TTL (seconds)."""
        path = self._key_path(key)
        data = {
            "key": key,
            "value": value,
            "created": time.time(),
            "expires": time.time() + ttl if ttl > 0 else None,
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def delete(self, key: str):
        """Delete from cache."""
        path = self._key_path(key)
        if path.exists():
            path.unlink()

    def clear(self):
        """Clear all cache."""
        for f in self.cache_dir.glob("*.json"):
            f.unlink()

    def stats(self) -> dict:
        """Get cache statistics."""
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            "entries": len(files),
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2),
        }


# Global cache instance
_cache = None


def get_cache() -> Cache:
    global _cache
    if _cache is None:
        _cache = Cache()
    return _cache


class RateLimiter:
    """Simple rate limiter."""

    def __init__(self):
        self.requests: dict[str, list[float]] = {}

    def check(self, key: str, max_requests: int = 10, window: int = 60) -> dict:
        """Check if request is allowed."""
        now = time.time()

        if key not in self.requests:
            self.requests[key] = []

        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < window]

        allowed = len(self.requests[key]) < max_requests
        remaining = max_requests - len(self.requests[key])

        if allowed:
            self.requests[key].append(now)

        return {
            "allowed": allowed,
            "remaining": max(0, remaining),
            "reset_in": window,
        }


_rate_limiter = RateLimiter()


def cache_get(key: str) -> str:
    """Get value from cache."""
    value = get_cache().get(key)
    return value if value else f"Cache miss for key: {key}"


def cache_set(key: str, value: str, ttl: int = 3600) -> str:
    """Set value in cache."""
    get_cache().set(key, value, ttl)
    return f"Cached: {key} (TTL: {ttl}s)"


def cache_clear() -> str:
    """Clear all cache."""
    get_cache().clear()
    return "Cache cleared"


def rate_limit_check(key: str, max_requests: int = 10, window: int = 60) -> str:
    """Check rate limit for a key."""
    result = _rate_limiter.check(key, max_requests, window)
    return json.dumps(result)


CACHING_TOOLS = {
    "cache_get": {
        "func": cache_get,
        "schema": {
            "type": "function",
            "function": {
                "name": "cache_get",
                "description": "Get value from cache.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Cache key"},
                    },
                    "required": ["key"],
                },
            },
        },
    },
    "cache_set": {
        "func": cache_set,
        "schema": {
            "type": "function",
            "function": {
                "name": "cache_set",
                "description": "Set value in cache with TTL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Cache key"},
                        "value": {"type": "string", "description": "Value to cache"},
                        "ttl": {"type": "integer", "description": "Time to live in seconds (default: 3600)"},
                    },
                    "required": ["key", "value"],
                },
            },
        },
    },
    "cache_clear": {
        "func": cache_clear,
        "schema": {
            "type": "function",
            "function": {
                "name": "cache_clear",
                "description": "Clear all cache entries.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
    "rate_limit_check": {
        "func": rate_limit_check,
        "schema": {
            "type": "function",
            "function": {
                "name": "rate_limit_check",
                "description": "Check rate limit for a key.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Rate limit key"},
                        "max_requests": {"type": "integer", "description": "Max requests in window (default: 10)"},
                        "window": {"type": "integer", "description": "Time window in seconds (default: 60)"},
                    },
                    "required": ["key"],
                },
            },
        },
    },
}
