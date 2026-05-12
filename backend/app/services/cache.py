"""
Metrics caching service for performance optimization.

Provides in-memory caching of computed metrics with TTL (time-to-live) and
invalidation support for sync events.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable, TypeVar
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""
    value: Any
    timestamp: float
    ttl_seconds: int

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl_seconds


class MetricsCache:
    """
    In-memory cache for commit analytics metrics.
    
    Supports:
    - Automatic expiration (TTL)
    - Cache invalidation by repository
    - Metrics pre-computation via callbacks
    """

    def __init__(self, default_ttl_seconds: int = 300):
        """
        Initialize the metrics cache.
        
        Args:
            default_ttl_seconds: Default time-to-live for cache entries (default: 5 minutes)
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl_seconds = default_ttl_seconds
        self.lock_free = True  # Simple implementation without locks

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            logger.debug(f"Cache expired for key: {key}")
            return None

        logger.debug(f"Cache hit for key: {key}")
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Store a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl_seconds or self.default_ttl_seconds
        self.cache[key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl_seconds=ttl
        )
        logger.debug(f"Cache set for key: {key} with TTL {ttl}s")

    def invalidate(self, pattern: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            pattern: If provided, invalidates keys starting with this pattern.
                    If None, clears entire cache.
        """
        if pattern is None:
            self.cache.clear()
            logger.info("Cache cleared")
        else:
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(pattern)]
            for key in keys_to_delete:
                del self.cache[key]
            logger.info(f"Cache invalidated for pattern: {pattern} ({len(keys_to_delete)} entries)")

    def invalidate_repository(self, repository_id: int) -> None:
        """
        Invalidate all cache entries for a specific repository.
        
        Useful when commits are synced for a repository.
        
        Args:
            repository_id: GitLabRepository ID
        """
        pattern = f"repo_{repository_id}_"
        self.invalidate(pattern)

    @staticmethod
    def make_key(metric_type: str, repository_id: int, **params) -> str:
        """
        Generate a cache key from metric parameters.
        
        Args:
            metric_type: Type of metric (e.g., 'frequency', 'velocity')
            repository_id: GitLabRepository ID
            **params: Additional parameters (e.g., days=30)
            
        Returns:
            Cache key string
        """
        param_str = "_".join(f"{k}_{v}" for k, v in sorted(params.items()))
        return f"repo_{repository_id}_{metric_type}_{param_str}"

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl_seconds: Optional[int] = None
    ) -> T:
        """
        Get cached value or compute and cache if not available.
        
        Args:
            key: Cache key
            compute_fn: Callable that computes the value if not cached
            ttl_seconds: Cache TTL (uses default if not specified)
            
        Returns:
            Cached or computed value
        """
        # Try to get from cache
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value

        # Compute and cache
        logger.debug(f"Computing value for key: {key}")
        value = compute_fn()
        self.set(key, value, ttl_seconds)
        return value

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        expired_count = sum(1 for e in self.cache.values() if e.is_expired())
        return {
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "active_entries": len(self.cache) - expired_count,
            "ttl_seconds": self.default_ttl_seconds,
        }


# Global cache instance
_metrics_cache = MetricsCache(default_ttl_seconds=300)


def get_metrics_cache() -> MetricsCache:
    """Get the global metrics cache instance."""
    return _metrics_cache


def cache_metric(ttl_seconds: Optional[int] = None):
    """
    Decorator for caching async metric computation methods.
    
    Usage:
        @cache_metric(ttl_seconds=300)
        async def some_metric_method(self, repo_id, days=30):
            # computation here
            return result
    
    Args:
        ttl_seconds: Cache TTL in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Build cache key from function name and arguments
            metric_type = func.__name__
            if args:
                repository_id = args[0]
            else:
                raise ValueError("repository_id must be first argument")

            # Extract remaining kwargs for key generation
            key_params = {}
            for i, arg in enumerate(args[1:], 1):
                key_params[f"arg{i}"] = arg
            key_params.update(kwargs)

            cache_key = MetricsCache.make_key(metric_type, repository_id, **key_params)

            # Check cache and compute if needed
            cache = get_metrics_cache()
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Returning cached result for {metric_type} (repo={repository_id})")
                return cached

            # Compute and cache
            logger.debug(f"Computing {metric_type} (repo={repository_id})")
            result = await func(self, *args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result

        return wrapper
    return decorator
