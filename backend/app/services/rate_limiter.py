"""
Redis-based sliding window rate limiter for FastAPI.
Tracks request counts per client per endpoint using sorted sets.
"""

from app.config import settings
from datetime import datetime, timezone
import hashlib


class RateLimiter:
    """Sliding window rate limiter backed by Redis sorted sets."""

    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._default_limits = {
            "authenticated": {"requests": 200, "window": 60},
            "anonymous": {"requests": 20, "window": 60},
            "scraper": {"requests": 10, "window": 60},
            "intelligence": {"requests": 50, "window": 60},
            "auth": {"requests": 5, "window": 60},
        }

    async def _get_redis(self):
        if self._redis is None:
            from redis.asyncio import from_url
            self._redis = await from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    def _key(self, client_id: str, route_group: str) -> str:
        return f"ratelimit:{route_group}:{hashlib.sha256(client_id.encode()).hexdigest()[:16]}"

    def _get_limit(self, route_group: str, is_authenticated: bool) -> tuple[int, int]:
        if route_group in self._default_limits:
            return (
                self._default_limits[route_group]["requests"],
                self._default_limits[route_group]["window"],
            )
        base = self._default_limits["authenticated" if is_authenticated else "anonymous"]
        return (base["requests"], base["window"])

    async def check(self, client_id: str, route_group: str = "default", is_authenticated: bool = True) -> dict:
        """
        Check if request is within rate limit.
        Returns dict with `allowed`, `remaining`, `reset_at`, `limit`.
        """
        r = await self._get_redis()
        key = self._key(client_id, route_group)
        max_requests, window = self._get_limit(route_group, is_authenticated)
        now = int(datetime.now(timezone.utc).timestamp())
        window_start = now - window

        pipeline = r.pipeline()
        pipeline.zremrangebyscore(key, 0, window_start)
        pipeline.zcard(key)
        pipeline.zadd(key, {str(now): now})
        pipeline.expire(key, window * 2)
        _, count, _, _ = await pipeline.execute()

        if count >= max_requests:
            oldest = await r.zrange(key, 0, 0, withscores=True)
            reset_at = int(oldest[0][1]) + window if oldest else now + window
            return {
                "allowed": False,
                "remaining": 0,
                "reset_at": reset_at,
                "limit": max_requests,
            }

        return {
            "allowed": True,
            "remaining": max_requests - count - 1,
            "reset_at": now + window,
            "limit": max_requests,
        }

    def route_group(self, path: str) -> str:
        """Map request path to a rate limit group."""
        path_lower = path.lower()
        if path_lower.startswith("/api/v1/scraper"):
            return "scraper"
        if path_lower.startswith("/api/v1/intelligence"):
            return "intelligence"
        if path_lower.startswith("/api/v1/auth"):
            return "auth"
        return "default"


rate_limiter = RateLimiter()
