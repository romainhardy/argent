"""Caching layer for reducing redundant API calls."""

import hashlib
import json
import os
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, TypeVar

# TTL Configuration in seconds
TTL_CONFIG = {
    "current_price": 60,  # 1 minute
    "price_history": 3600,  # 60 minutes
    "company_info": 86400,  # 24 hours
    "crypto_price": 60,  # 1 minute
    "crypto_history": 3600,  # 60 minutes
    "crypto_info": 3600,  # 60 minutes
    "economic_indicator": 43200,  # 12 hours
    "macro_snapshot": 43200,  # 12 hours
    "news": 900,  # 15 minutes
    "financials": 86400,  # 24 hours
    "recommendations": 3600,  # 60 minutes
}

# Default cache directory
CACHE_DIR = Path(__file__).parent.parent.parent.parent / "data" / "cache"

T = TypeVar("T")


def _ensure_cache_dir() -> Path:
    """Ensure the cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def _generate_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate a unique cache key from function arguments."""
    key_parts = [prefix]

    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif isinstance(arg, (list, tuple)):
            key_parts.append(json.dumps(sorted(arg) if all(isinstance(x, str) for x in arg) else arg))
        elif isinstance(arg, dict):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")

    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def _serialize_value(value: Any) -> Any:
    """Serialize a value for JSON storage."""
    if is_dataclass(value) and not isinstance(value, type):
        return {"__dataclass__": type(value).__name__, "data": asdict(value)}
    elif isinstance(value, datetime):
        return {"__datetime__": value.isoformat()}
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    return value


def _deserialize_value(value: Any, dataclass_registry: dict[str, type] | None = None) -> Any:
    """Deserialize a value from JSON storage."""
    if isinstance(value, dict):
        if "__datetime__" in value:
            return datetime.fromisoformat(value["__datetime__"])
        elif "__dataclass__" in value and dataclass_registry:
            cls_name = value["__dataclass__"]
            if cls_name in dataclass_registry:
                cls = dataclass_registry[cls_name]
                data = value["data"]
                # Recursively deserialize nested values
                for k, v in data.items():
                    data[k] = _deserialize_value(v, dataclass_registry)
                return cls(**data)
        return {k: _deserialize_value(v, dataclass_registry) for k, v in value.items()}
    elif isinstance(value, list):
        return [_deserialize_value(item, dataclass_registry) for item in value]
    return value


class Cache:
    """File-based cache with TTL support."""

    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or CACHE_DIR
        self._ensure_dir()
        self._dataclass_registry: dict[str, type] = {}

    def _ensure_dir(self) -> None:
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def register_dataclass(self, cls: type) -> None:
        """Register a dataclass for deserialization."""
        self._dataclass_registry[cls.__name__] = cls

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{key}.json"

    def get(self, key: str, ttl: int | None = None) -> Any | None:
        """
        Get a value from cache if it exists and hasn't expired.

        Args:
            key: Cache key
            ttl: Time-to-live in seconds (None = no expiry check)

        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r") as f:
                cached = json.load(f)

            timestamp = cached.get("timestamp", 0)

            # Check TTL
            if ttl is not None:
                age = time.time() - timestamp
                if age > ttl:
                    # Expired, remove cache file
                    cache_path.unlink(missing_ok=True)
                    return None

            return _deserialize_value(cached.get("value"), self._dataclass_registry)

        except (json.JSONDecodeError, KeyError, OSError):
            # Invalid cache file, remove it
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Store a value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)

        try:
            cached = {
                "timestamp": time.time(),
                "value": _serialize_value(value),
            }
            with open(cache_path, "w") as f:
                json.dump(cached, f)
        except (OSError, TypeError) as e:
            # Failed to write cache, log and continue
            pass

    def delete(self, key: str) -> None:
        """Delete a cache entry."""
        cache_path = self._get_cache_path(key)
        cache_path.unlink(missing_ok=True)

    def clear(self) -> None:
        """Clear all cache entries."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)

    def cleanup_expired(self, ttl_map: dict[str, int] | None = None) -> int:
        """
        Remove expired cache entries.

        Args:
            ttl_map: Map of prefix to TTL (uses default TTL_CONFIG if not provided)

        Returns:
            Number of entries removed
        """
        ttl_map = ttl_map or TTL_CONFIG
        default_ttl = max(ttl_map.values()) if ttl_map else 86400
        removed = 0

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    cached = json.load(f)

                timestamp = cached.get("timestamp", 0)
                age = time.time() - timestamp

                # Use default TTL for cleanup
                if age > default_ttl:
                    cache_file.unlink()
                    removed += 1

            except (json.JSONDecodeError, OSError):
                # Invalid cache file, remove it
                cache_file.unlink(missing_ok=True)
                removed += 1

        return removed


# Global cache instance
_cache_instance: Cache | None = None


def get_cache() -> Cache:
    """Get the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache()
    return _cache_instance


def cached(
    cache_type: str,
    ttl: int | None = None,
    key_prefix: str | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for caching function results.

    Args:
        cache_type: Type of data being cached (used for TTL lookup)
        ttl: Override TTL in seconds (uses TTL_CONFIG if not provided)
        key_prefix: Custom prefix for cache key (uses function name if not provided)

    Usage:
        @cached("current_price")
        def get_current_price(self, symbol: str) -> dict:
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            cache = get_cache()

            # Get TTL from config or override
            actual_ttl = ttl if ttl is not None else TTL_CONFIG.get(cache_type, 3600)

            # Generate cache key (skip 'self' argument)
            func_args = args[1:] if args and hasattr(args[0], "__class__") else args
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = _generate_cache_key(prefix, *func_args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key, actual_ttl)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)

            # Only cache non-None and non-empty results
            if result is not None and result != [] and result != {}:
                cache.set(cache_key, result)

            return result

        return wrapper
    return decorator


def invalidate_cache(pattern: str | None = None) -> int:
    """
    Invalidate cache entries matching a pattern.

    Args:
        pattern: Glob pattern for cache keys (None = clear all)

    Returns:
        Number of entries invalidated
    """
    cache = get_cache()

    if pattern is None:
        cache.clear()
        return -1  # Unknown count

    count = 0
    for cache_file in cache.cache_dir.glob(f"*{pattern}*.json"):
        cache_file.unlink(missing_ok=True)
        count += 1

    return count
