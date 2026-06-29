"""Unit tests for app.services.rate_limiter — Redis sliding window rate limiter."""

import os
import sys
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.rate_limiter import RateLimiter


class TestRateLimiterRouteGroup(unittest.TestCase):

    def setUp(self):
        self.limiter = RateLimiter()

    def test_scraper_route(self):
        self.assertEqual(self.limiter.route_group("/api/v1/scraper/start"), "scraper")

    def test_scraper_route_case_insensitive(self):
        self.assertEqual(self.limiter.route_group("/API/V1/Scraper/start"), "scraper")

    def test_intelligence_route(self):
        self.assertEqual(self.limiter.route_group("/api/v1/intelligence/analyze"), "intelligence")

    def test_auth_route(self):
        self.assertEqual(self.limiter.route_group("/api/v1/auth/login"), "auth")

    def test_default_route(self):
        self.assertEqual(self.limiter.route_group("/api/v1/leads"), "default")

    def test_unknown_route_returns_default(self):
        self.assertEqual(self.limiter.route_group("/api/v1/store/products"), "default")


class TestRateLimiterGetLimit(unittest.TestCase):

    def setUp(self):
        self.limiter = RateLimiter()

    def test_scraper_limit(self):
        requests, window = self.limiter._get_limit("scraper", True)
        self.assertEqual(requests, 10)
        self.assertEqual(window, 60)

    def test_intelligence_limit(self):
        requests, window = self.limiter._get_limit("intelligence", True)
        self.assertEqual(requests, 50)
        self.assertEqual(window, 60)

    def test_auth_limit(self):
        requests, window = self.limiter._get_limit("auth", True)
        self.assertEqual(requests, 5)
        self.assertEqual(window, 60)

    def test_authenticated_default(self):
        requests, window = self.limiter._get_limit("unknown_group", True)
        self.assertEqual(requests, 200)
        self.assertEqual(window, 60)

    def test_anonymous_default(self):
        requests, window = self.limiter._get_limit("unknown_group", False)
        self.assertEqual(requests, 20)
        self.assertEqual(window, 60)


class TestRateLimiterKey(unittest.TestCase):

    def setUp(self):
        self.limiter = RateLimiter()

    def test_key_format(self):
        key = self.limiter._key("client-123", "auth")
        self.assertTrue(key.startswith("ratelimit:auth:"))
        self.assertEqual(len(key.split(":")[2]), 16)

    def test_same_client_same_key(self):
        key1 = self.limiter._key("user@example.com", "default")
        key2 = self.limiter._key("user@example.com", "default")
        self.assertEqual(key1, key2)

    def test_different_clients_different_keys(self):
        key1 = self.limiter._key("client-1", "default")
        key2 = self.limiter._key("client-2", "default")
        self.assertNotEqual(key1, key2)

    def test_different_groups_different_keys(self):
        key1 = self.limiter._key("client-1", "auth")
        key2 = self.limiter._key("client-1", "scraper")
        self.assertNotEqual(key1, key2)


class TestRateLimiterCheck(unittest.TestCase):

    def _make_mock_redis(self, count=5):
        """Create a mock Redis that properly simulates pipeline behavior."""
        mock_redis = MagicMock()
        mock_pipeline = MagicMock()
        mock_redis.pipeline.return_value = mock_pipeline
        # Pipeline methods return self for chaining (sync)
        mock_pipeline.zremrangebyscore.return_value = mock_pipeline
        mock_pipeline.zcard.return_value = mock_pipeline
        mock_pipeline.zadd.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        # execute() is async
        mock_pipeline.execute = AsyncMock(return_value=[None, count, None, None])
        # zrange on the redis object is async
        mock_redis.zrange = AsyncMock(return_value=[("1234567890", 1234567890)])
        return mock_redis

    def test_allowed_when_under_limit(self):
        mock_redis = self._make_mock_redis(count=5)
        self.limiter = RateLimiter(redis_client=mock_redis)

        result = asyncio.run(self.limiter.check("client-1", "default", True))
        self.assertTrue(result["allowed"])
        self.assertEqual(result["limit"], 200)
        self.assertEqual(result["remaining"], 200 - 5 - 1)

    def test_blocked_when_at_limit(self):
        mock_redis = self._make_mock_redis(count=200)
        self.limiter = RateLimiter(redis_client=mock_redis)

        result = asyncio.run(self.limiter.check("client-1", "default", True))
        self.assertFalse(result["allowed"])
        self.assertEqual(result["remaining"], 0)
        self.assertEqual(result["limit"], 200)

    def test_blocked_auth_route_at_5(self):
        mock_redis = self._make_mock_redis(count=5)
        self.limiter = RateLimiter(redis_client=mock_redis)

        result = asyncio.run(self.limiter.check("client-1", "auth", True))
        self.assertFalse(result["allowed"])
        self.assertEqual(result["limit"], 5)

    def test_reset_at_returned(self):
        mock_redis = self._make_mock_redis(count=3)
        self.limiter = RateLimiter(redis_client=mock_redis)

        result = asyncio.run(self.limiter.check("client-1", "default", True))
        self.assertIn("reset_at", result)
        self.assertIsInstance(result["reset_at"], int)

    @patch("redis.asyncio.from_url")
    def test_lazy_redis_initialization(self, mock_from_url):
        mock_redis = MagicMock()
        mock_pipeline = MagicMock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.zremrangebyscore.return_value = mock_pipeline
        mock_pipeline.zcard.return_value = mock_pipeline
        mock_pipeline.zadd.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute = AsyncMock(return_value=[None, 0, None, None])

        async def _mock_from_url(*args, **kwargs):
            return mock_redis
        mock_from_url.side_effect = _mock_from_url

        limiter = RateLimiter()
        self.assertIsNone(limiter._redis)
        asyncio.run(limiter.check("client-1", "default", True))
        mock_from_url.assert_called_once()


class TestRateLimiterInit(unittest.TestCase):

    def test_default_limits_defined(self):
        limiter = RateLimiter()
        self.assertIn("authenticated", limiter._default_limits)
        self.assertIn("anonymous", limiter._default_limits)
        self.assertIn("scraper", limiter._default_limits)
        self.assertIn("intelligence", limiter._default_limits)
        self.assertIn("auth", limiter._default_limits)

    def test_custom_redis_client(self):
        mock_redis = AsyncMock()
        limiter = RateLimiter(redis_client=mock_redis)
        self.assertEqual(limiter._redis, mock_redis)

    def test_no_redis_client_by_default(self):
        limiter = RateLimiter()
        self.assertIsNone(limiter._redis)


if __name__ == "__main__":
    unittest.main(verbosity=2)
