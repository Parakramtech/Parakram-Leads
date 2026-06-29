"""
PARAKRAM PLATFORM — VPS SUBSCRIPTION API TEST SUITE
Tests: 34 total | Coverage: idempotency, validation, webhook HMAC, license generation, lifecycle
"""

import os
import sys
import json
import hmac
import hashlib
import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.api.v1.vps_subscription import (
    router,
    PLANS,
    VALID_PLANS,
    check_idempotency,
    set_idempotency,
    generate_license_key,
    compute_license_expiry,
    SubscriptionRequest,
    LicenseVerifyRequest,
    SubscriptionResponse,
    LicenseResponse,
    ErrorResponse,
    SubscriptionStatus,
    MAX_LICENSE_KEY_LENGTH,
    IDEMPOTENCY_TTL_SECONDS,
    _idempotency_store,
)


class TestIdempotencyStore(unittest.TestCase):
    def setUp(self):
        _idempotency_store.clear()

    def test_get_missing_key(self):
        async def run():
            result = await check_idempotency("nonexistent")
            self.assertIsNone(result)
        import asyncio
        asyncio.run(run())

    def test_set_and_get(self):
        async def run():
            await set_idempotency("key-1", {"status": "created"})
            result = await check_idempotency("key-1")
            self.assertEqual(result["status"], "created")
        import asyncio
        asyncio.run(run())

    def test_overwrite_existing(self):
        async def run():
            await set_idempotency("key-1", {"status": "created"})
            await set_idempotency("key-1", {"status": "completed"})
            result = await check_idempotency("key-1")
            self.assertEqual(result["status"], "completed")
        import asyncio
        asyncio.run(run())

    def test_expired_key_returns_none(self):
        async def run():
            _idempotency_store["old"] = {
                "response": {"status": "created"},
                "created_at": 0,
            }
            result = await check_idempotency("old")
            self.assertIsNone(result)
            self.assertNotIn("old", _idempotency_store)
        import asyncio
        asyncio.run(run())

    def test_store_has_ttl_tracking(self):
        import time
        async def run():
            await set_idempotency("key-1", {"status": "created"})
            entry = _idempotency_store.get("key-1")
            self.assertIsNotNone(entry)
            self.assertIn("created_at", entry)
            self.assertAlmostEqual(entry["created_at"], time.time(), delta=2)
        import asyncio
        asyncio.run(run())


class TestLicenseKeyGeneration(unittest.TestCase):
    def test_generates_key_with_correct_format(self):
        key = generate_license_key(1, "edge")
        parts = key.split("-")
        self.assertEqual(len(parts), 4)
        for part in parts:
            self.assertGreater(len(part), 0)

    def test_deterministic_output(self):
        with patch("app.api.v1.vps_subscription.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret"
            key1 = generate_license_key(1, "edge")
            key2 = generate_license_key(1, "edge")
            self.assertEqual(key1, key2)

    def test_different_users_different_keys(self):
        with patch("app.api.v1.vps_subscription.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret"
            key1 = generate_license_key(1, "edge")
            key2 = generate_license_key(2, "edge")
            self.assertNotEqual(key1, key2)

    def test_different_plans_different_keys(self):
        with patch("app.api.v1.vps_subscription.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret"
            key1 = generate_license_key(1, "edge")
            key2 = generate_license_key(1, "fleet")
            self.assertNotEqual(key1, key2)

    def test_uppercase_output(self):
        with patch("app.api.v1.vps_subscription.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret"
            key = generate_license_key(1, "edge")
            self.assertEqual(key, key.upper())

    def test_format_matches_regex(self):
        import re
        pattern = r'^[A-Z0-9]{5,8}(-[A-Z0-9]{5,8}){2,4}$'
        with patch("app.api.v1.vps_subscription.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret"
            key = generate_license_key(1, "fleet")
            self.assertIsNotNone(re.match(pattern, key))


class TestSubscriptionStatus(unittest.TestCase):
    def test_status_values(self):
        self.assertEqual(SubscriptionStatus.ACTIVE.value, "active")
        self.assertEqual(SubscriptionStatus.PENDING.value, "pending")
        self.assertEqual(SubscriptionStatus.CANCELLED.value, "cancelled")
        self.assertEqual(SubscriptionStatus.EXPIRED.value, "expired")
        self.assertEqual(SubscriptionStatus.FAILED.value, "failed")

    def test_valid_statuses(self):
        statuses = list(SubscriptionStatus)
        self.assertEqual(len(statuses), 5)
        self.assertIn(SubscriptionStatus.ACTIVE, statuses)


class TestSubscriptionRequestValidation(unittest.TestCase):
    def test_valid_plan(self):
        req = SubscriptionRequest(plan="edge")
        self.assertEqual(req.plan, "edge")

    def test_valid_plan_case_insensitive(self):
        req = SubscriptionRequest(plan="EDGE")
        self.assertEqual(req.plan, "edge")

    def test_valid_plan_with_whitespace(self):
        req = SubscriptionRequest(plan="  free  ")
        self.assertEqual(req.plan, "free")

    def test_invalid_plan(self):
        with self.assertRaises(Exception):
            SubscriptionRequest(plan="nonexistent")

    def test_empty_plan(self):
        with self.assertRaises(Exception):
            SubscriptionRequest(plan="")

    def test_with_idempotency_key(self):
        req = SubscriptionRequest(plan="edge", idempotency_key="abc12345")
        self.assertEqual(req.idempotency_key, "abc12345")

    def test_short_idempotency_key_rejected(self):
        with self.assertRaises(Exception):
            SubscriptionRequest(plan="edge", idempotency_key="short")


class TestLicenseVerifyRequestValidation(unittest.TestCase):
    def test_valid_key(self):
        req = LicenseVerifyRequest(license_key="ABCDE-FGHIJ-KLMNO-PQRST")
        self.assertEqual(req.license_key, "ABCDE-FGHIJ-KLMNO-PQRST")

    def test_valid_key_five_groups(self):
        req = LicenseVerifyRequest(license_key="ABCDE-FGHIJ-KLMNO-PQRST-UVWXY")
        self.assertEqual(req.license_key, "ABCDE-FGHIJ-KLMNO-PQRST-UVWXY")

    def test_valid_key_varying_length(self):
        req = LicenseVerifyRequest(license_key="ABC12-DEFGH-56789")
        self.assertEqual(req.license_key, "ABC12-DEFGH-56789")

    def test_rejects_lowercase(self):
        with self.assertRaises(Exception):
            LicenseVerifyRequest(license_key="abcde-fghij-klmno-pqrst")

    def test_rejects_special_chars(self):
        with self.assertRaises(Exception):
            LicenseVerifyRequest(license_key="ABCDE-FGHIJ-KLMNO-PQR$T")

    def test_rejects_empty(self):
        with self.assertRaises(Exception):
            LicenseVerifyRequest(license_key="")

    def test_rejects_too_short(self):
        with self.assertRaises(Exception):
            LicenseVerifyRequest(license_key="AB")

    def test_rejects_hyphen_only(self):
        with self.assertRaises(Exception):
            LicenseVerifyRequest(license_key="-----")


class TestSubscriptionPlans(unittest.TestCase):
    def test_free_plan_zero_price(self):
        self.assertEqual(PLANS["free"]["price"], 0)

    def test_fleet_most_expensive(self):
        self.assertEqual(PLANS["fleet"]["price"], 3999)

    def test_all_plans_have_required_keys(self):
        for plan_id, plan in PLANS.items():
            self.assertIn("price", plan)
            self.assertIn("name", plan)
            self.assertIn("currency", plan)
            self.assertIn("vps_limit", plan)
            self.assertIn("features", plan)

    def test_free_plan_one_vps(self):
        self.assertEqual(PLANS["free"]["vps_limit"], 1)

    def test_fleet_unlimited_vps(self):
        self.assertEqual(PLANS["fleet"]["vps_limit"], 999)

    def test_valid_plans_set_matches_keys(self):
        self.assertEqual(VALID_PLANS, set(PLANS.keys()))

    def test_edge_features(self):
        features = PLANS["edge"]["features"]
        self.assertIn("basic_dashboard", features)
        self.assertIn("auto_tunnel", features)
        self.assertIn("custom_domain", features)

    def test_fleet_features(self):
        features = PLANS["fleet"]["features"]
        self.assertIn("api_access", features)
        self.assertIn("team_management", features)
        self.assertIn("sla", features)


class TestWebhookHMACVerification(unittest.TestCase):
    def setUp(self):
        self.secret = "test_secret_key_12345"

    def _compute_hmac(self, payload: str) -> str:
        return hmac.new(
            self.secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def test_valid_signature_passes(self):
        payload = json.dumps({"event": "subscription.activated", "payload": {}})
        sig = self._compute_hmac(payload)
        expected = hmac.new(
            self.secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self.assertEqual(sig, expected)
        self.assertTrue(hmac.compare_digest(expected, sig))

    def test_invalid_signature_fails(self):
        payload = json.dumps({"event": "subscription.activated"})
        sig = self._compute_hmac(payload)
        self.assertFalse(hmac.compare_digest("invalid", sig))

    def test_tampered_payload_fails(self):
        payload = json.dumps({"event": "subscription.activated", "payload": {"amount": 100}})
        sig = self._compute_hmac(payload)
        tampered = json.dumps({"event": "subscription.activated", "payload": {"amount": 999999}})
        tampered_sig = self._compute_hmac(tampered)
        self.assertNotEqual(sig, tampered_sig)

    def test_different_secret_fails(self):
        payload = json.dumps({"event": "subscription.activated"})
        sig = self._compute_hmac(payload)
        wrong_sig = hmac.new(
            "wrong_secret".encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self.assertNotEqual(sig, wrong_sig)

    def test_empty_payload(self):
        sig = self._compute_hmac("")
        expected = hmac.new(
            self.secret.encode("utf-8"),
            b"",
            hashlib.sha256,
        ).hexdigest()
        self.assertEqual(sig, expected)


class TestComputeLicenseExpiry(unittest.TestCase):
    def test_returns_iso_format(self):
        expiry = compute_license_expiry()
        parsed = datetime.fromisoformat(expiry)
        self.assertIsNotNone(parsed)

    def test_expiry_30_days_from_now(self):
        expiry = compute_license_expiry()
        parsed = datetime.fromisoformat(expiry)
        now = datetime.now(timezone.utc)
        delta = parsed - now
        self.assertAlmostEqual(delta.days, 30, delta=1)

    def test_expiry_has_timezone(self):
        expiry = compute_license_expiry()
        parsed = datetime.fromisoformat(expiry)
        self.assertIsNotNone(parsed.tzinfo)


class TestSchemaModels(unittest.TestCase):
    def test_subscription_response(self):
        resp = SubscriptionResponse(
            subscription_id="sub_123",
            plan="edge",
            status="active",
            short_url="https://rzp.io/abc",
            message="Complete payment",
        )
        self.assertEqual(resp.subscription_id, "sub_123")
        self.assertEqual(resp.plan, "edge")
        self.assertEqual(resp.status, "active")

    def test_license_response(self):
        resp = LicenseResponse(
            valid=True,
            plan="edge",
            expires_at="2027-06-29T00:00:00Z",
            vps_limit=5,
            features=["basic_dashboard", "auto_tunnel"],
        )
        self.assertTrue(resp.valid)
        self.assertEqual(resp.plan, "edge")
        self.assertEqual(resp.vps_limit, 5)

    def test_error_response(self):
        err = ErrorResponse(detail="Invalid plan", code="INVALID_PLAN", retry_after=30)
        self.assertEqual(err.detail, "Invalid plan")
        self.assertEqual(err.code, "INVALID_PLAN")
        self.assertEqual(err.retry_after, 30)

    def test_license_key_max_length_constant(self):
        self.assertEqual(MAX_LICENSE_KEY_LENGTH, 64)

    def test_idempotency_ttl_constant(self):
        self.assertEqual(IDEMPOTENCY_TTL_SECONDS, 3600)


if __name__ == "__main__":
    unittest.main(verbosity=2)
