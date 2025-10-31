"""
Caching Utilities for API Responses

This module provides Redis-based caching for API responses with fallback to in-memory caching.
Includes proper error handling and backward compatibility.
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional

import redis

from .utils import CONFIG


class APICache:
    """API response caching with Redis and in-memory fallback."""

    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self._init_redis()

    def _init_redis(self):
        """Initialize Redis client if enabled and available."""
        if not CONFIG["performance"]["enable_redis_caching"]:
            return

        try:
            self.redis_client = redis.Redis(
                host=CONFIG["caching"]["redis_host"],
                port=CONFIG["caching"]["redis_port"],
                db=CONFIG["caching"]["redis_db"],
                decode_responses=True,
            )
            # Test connection
            self.redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError) as e:
            print(f"Redis connection failed: {e}. Falling back to in-memory caching.")
            self.redis_client = None
        except Exception as e:
            print(
                f"Unexpected error initializing Redis: {e}. Falling back to in-memory caching."
            )
            self.redis_client = None

    def _generate_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate a unique cache key from URL and parameters."""
        key_data = {"url": url, "params": params or {}}
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Retrieve cached response if available."""
        if not CONFIG["performance"]["enable_redis_caching"] and not self.memory_cache:
            return None

        key = self._generate_key(url, params)

        # Try Redis first
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                print(f"Redis get error: {e}")

        # Fallback to memory cache
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() < entry["expires"]:
                return entry["data"]
            else:
                # Expired, remove it
                del self.memory_cache[key]

        return None

    def set(
        self,
        url: str,
        data: Any,
        params: Optional[Dict] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """Cache the response data."""
        if not CONFIG["performance"]["enable_redis_caching"] and not self.memory_cache:
            return False

        key = self._generate_key(url, params)
        ttl = ttl or CONFIG["caching"]["cache_ttl"]
        expires = time.time() + ttl

        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(data))
                return True
            except Exception as e:
                print(f"Redis set error: {e}")

        # Fallback to memory cache
        try:
            self.memory_cache[key] = {"data": data, "expires": expires}
            return True
        except Exception as e:
            print(f"Memory cache set error: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cached data."""
        success = True

        # Clear Redis
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                print(f"Redis clear error: {e}")
                success = False

        # Clear memory cache
        try:
            self.memory_cache.clear()
        except Exception as e:
            print(f"Memory cache clear error: {e}")
            success = False

        return success

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "redis_enabled": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache),
            "config_enabled": CONFIG["performance"]["enable_redis_caching"],
        }

        if self.redis_client:
            try:
                stats["redis_keys"] = self.redis_client.dbsize()
            except Exception as e:
                stats["redis_error"] = str(e)

        return stats


# Global cache instance
api_cache = APICache()


def cache_api_response(func):
    """Decorator to cache API function responses."""

    def wrapper(*args, **kwargs):
        if not CONFIG["performance"]["enable_redis_caching"]:
            return func(*args, **kwargs)

        # Generate cache key from function name and arguments
        key_data = {
            "func": func.__name__,
            "args": args,
            "kwargs": {
                k: v for k, v in kwargs.items() if k != "use_cache"
            },  # Exclude use_cache param
        }
        key = hashlib.md5(
            json.dumps(key_data, sort_keys=True, default=str).encode()
        ).hexdigest()

        # Check cache
        cached = api_cache.get(key)
        if cached is not None:
            return cached

        # Call function
        result = func(*args, **kwargs)

        # Cache result if successful
        if result is not None:
            api_cache.set(key, data=result)

        return result

    return wrapper


def get_cached_api_response(url: str, params: Optional[Dict] = None) -> Optional[Any]:
    """Convenience function to get cached API response."""
    return api_cache.get(url, params)


def set_cached_api_response(
    url: str, data: Any, params: Optional[Dict] = None, ttl: Optional[int] = None
) -> bool:
    """Convenience function to cache API response."""
    return api_cache.set(url, params, data, ttl)
