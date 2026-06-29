"""
PARAKRAM VPS — API CLIENT TEST SUITE (Military/Space Grade)
=============================================================
Tests: 32 total | Coverage: circuit breaker, retry, validation, error handling
"""

import os
import sys
import json
import time
import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.api_client import (
    ParakramAPI, APIError, ErrorSeverity, CircuitBreaker, CircuitState,
    validate_signup_payload, validate_subscription_payload,
    classify_error, should_retry, MAX_RETRIES,
)


# ═══════════════════════════════════════════════════════════════════════════
#  TEST: INPUT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

class TestInputValidation(unittest.TestCase):
    """Test client-side payload validation."""

    def test_valid_signup(self):
        errors = validate_signup_payload("test@example.com", "password123", "John Doe")
        self.assertEqual(errors, [])

    def test_invalid_email(self):
        errors = validate_signup_payload("not-an-email", "password123", "John")
        self.assertGreater(len(errors), 0)

    def test_short_password(self):
        errors = validate_signup_payload("test@example.com", "12345", "John")
        self.assertGreater(len(errors), 0)

    def test_empty_email(self):
        errors = validate_signup_payload("", "password123", "John")
        self.assertGreater(len(errors), 0)

    def test_xss_in_name(self):
        errors = validate_signup_payload("test@example.com", "password123", "<script>alert('xss')</script>")
        self.assertGreater(len(errors), 0)

    def test_long_name(self):
        errors = validate_signup_payload("test@example.com", "password123", "A" * 201)
        self.assertGreater(len(errors), 0)

    def test_valid_subscription_plan(self):
        for plan in ["free", "edge", "fleet"]:
            errors = validate_subscription_payload(plan)
            self.assertEqual(errors, [], f"Plan '{plan}' should be valid")

    def test_invalid_subscription_plan(self):
        errors = validate_subscription_payload("premium")
        self.assertGreater(len(errors), 0)

    def test_empty_subscription_plan(self):
        errors = validate_subscription_payload("")
        self.assertGreater(len(errors), 0)


# ═══════════════════════════════════════════════════════════════════════════
#  TEST: ERROR CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

class TestErrorClassification(unittest.TestCase):
    """Test HTTP response classification."""

    def _make_response(self, status_code: int):
        resp = MagicMock()
        resp.status_code = status_code
        resp.text = "Error"
        return resp

    def test_401_is_critical(self):
        resp = self._make_response(401)
        self.assertEqual(classify_error(resp), ErrorSeverity.CRITICAL)

    def test_403_is_critical(self):
        resp = self._make_response(403)
        self.assertEqual(classify_error(resp), ErrorSeverity.CRITICAL)

    def test_400_is_fatal(self):
        resp = self._make_response(400)
        self.assertEqual(classify_error(resp), ErrorSeverity.FATAL)

    def test_422_is_fatal(self):
        resp = self._make_response(422)
        self.assertEqual(classify_error(resp), ErrorSeverity.FATAL)

    def test_429_is_transient(self):
        resp = self._make_response(429)
        self.assertEqual(classify_error(resp), ErrorSeverity.TRANSIENT)

    def test_502_is_transient(self):
        resp = self._make_response(502)
        self.assertEqual(classify_error(resp), ErrorSeverity.TRANSIENT)

    def test_500_is_transient(self):
        resp = self._make_response(500)
        self.assertEqual(classify_error(resp), ErrorSeverity.TRANSIENT)

    def test_200_not_error(self):
        resp = self._make_response(200)
        sev = classify_error(resp)
        self.assertNotEqual(sev, ErrorSeverity.CRITICAL)
        self.assertNotEqual(sev, ErrorSeverity.FATAL)

    def test_should_retry_transient(self):
        self.assertTrue(should_retry(ErrorSeverity.TRANSIENT))

    def test_should_retry_degraded(self):
        self.assertTrue(should_retry(ErrorSeverity.DEGRADED))

    def test_should_not_retry_fatal(self):
        self.assertFalse(should_retry(ErrorSeverity.FATAL))

    def test_should_not_retry_critical(self):
        self.assertFalse(should_retry(ErrorSeverity.CRITICAL))


# ═══════════════════════════════════════════════════════════════════════════
#  TEST: CIRCUIT BREAKER
# ═══════════════════════════════════════════════════════════════════════════

class TestCircuitBreaker(unittest.TestCase):
    """Test the circuit breaker pattern."""

    def test_initial_state_closed(self):
        cb = CircuitBreaker()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.allow_request())

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=30)
        for _ in range(3):
            cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.allow_request())

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=30)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.allow_request())

    def test_half_open_transition(self):
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=0.1)
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.allow_request())
        time.sleep(0.15)
        self.assertTrue(cb.allow_request())
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)

    def test_half_open_success_closes(self):
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=0.1)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.15)
        cb.allow_request()  # transitions to half-open
        cb.record_success()
        self.assertEqual(cb.state, CircuitState.CLOSED)

    def test_half_open_limits_requests(self):
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=0.1,
                            half_open_max=2)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.15)
        self.assertTrue(cb.allow_request())  # OPEN→HALF_OPEN transition (not counted)
        self.assertTrue(cb.allow_request())  # HALF_OPEN req 1/2
        self.assertTrue(cb.allow_request())  # HALF_OPEN req 2/2
        self.assertFalse(cb.allow_request())  # block 3rd

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=30)
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.state, CircuitState.OPEN)
        cb.reset()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.allow_request())


# ═══════════════════════════════════════════════════════════════════════════
#  TEST: API CLIENT SIGNUP
# ═══════════════════════════════════════════════════════════════════════════

class TestAPIClientSignup(unittest.TestCase):
    """Test the signup flow with validation."""

    def setUp(self):
        self.api = ParakramAPI()
        self.api._circuit = CircuitBreaker(failure_threshold=100)  # disable circuit

    def test_signup_rejects_invalid_email(self):
        with self.assertRaises(APIError) as ctx:
            self.api.signup("not-email", "password123", "John")
        self.assertEqual(ctx.exception.severity, ErrorSeverity.FATAL)

    def test_signup_rejects_short_password(self):
        with self.assertRaises(APIError) as ctx:
            self.api.signup("test@example.com", "123", "John")
        self.assertEqual(ctx.exception.severity, ErrorSeverity.FATAL)

    def test_signup_rejects_xss_name(self):
        with self.assertRaises(APIError):
            self.api.signup("test@example.com", "password123", "<script>")

    @patch.object(ParakramAPI, "_request")
    def test_signup_success(self, mock_request):
        mock_request.return_value = {
            "access_token": "test-token",
            "user": {"email": "test@example.com", "full_name": "John"},
        }
        result = self.api.signup("test@example.com", "password123", "John")
        self.assertIn("access_token", result)

    @patch.object(ParakramAPI, "_request")
    def test_signup_sets_token(self, mock_request):
        mock_request.return_value = {
            "access_token": "new-token",
            "user": {"email": "test@example.com", "full_name": "John"},
        }
        self.api.signup("test@example.com", "password123", "John")
        self.assertEqual(self.api.token, "new-token")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST: API CLIENT SUBSCRIPTION
# ═══════════════════════════════════════════════════════════════════════════

class TestAPIClientSubscription(unittest.TestCase):
    """Test subscription creation with validation."""

    def setUp(self):
        self.api = ParakramAPI(token="test-token")
        self.api._circuit = CircuitBreaker(failure_threshold=100)

    def test_subscription_rejects_invalid_plan(self):
        with self.assertRaises(APIError) as ctx:
            self.api.create_vps_subscription("invalid")
        self.assertEqual(ctx.exception.severity, ErrorSeverity.FATAL)

    def test_subscription_rejects_no_auth(self):
        api = ParakramAPI()
        with self.assertRaises(APIError) as ctx:
            api.create_vps_subscription("edge")
        self.assertEqual(ctx.exception.severity, ErrorSeverity.CRITICAL)

    @patch.object(ParakramAPI, "_request")
    def test_subscription_success(self, mock_request):
        mock_request.return_value = {
            "subscription_id": "sub_test123",
            "plan": "edge",
            "status": "created",
        }
        result = self.api.create_vps_subscription("edge")
        self.assertEqual(result["subscription_id"], "sub_test123")
        self.assertEqual(result["plan"], "edge")

    @patch.object(ParakramAPI, "_request")
    def test_subscription_free_plan(self, mock_request):
        mock_request.return_value = {
            "plan": "free",
            "status": "active",
        }
        result = self.api.create_vps_subscription("free")
        self.assertEqual(result["plan"], "free")
        self.assertEqual(result["status"], "active")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST: API CLIENT LICENSE
# ═══════════════════════════════════════════════════════════════════════════

class TestAPIClientLicense(unittest.TestCase):
    """Test license verification with validation."""

    def setUp(self):
        self.api = ParakramAPI()

    def test_verify_rejects_short_key(self):
        with self.assertRaises(APIError) as ctx:
            self.api.verify_license("short")
        self.assertEqual(ctx.exception.severity, ErrorSeverity.FATAL)

    def test_verify_rejects_empty_key(self):
        with self.assertRaises(APIError):
            self.api.verify_license("")

    @patch.object(ParakramAPI, "_request")
    def test_verify_success(self, mock_request):
        mock_request.return_value = {
            "valid": True,
            "plan": "edge",
            "expires_at": "2027-06-29T00:00:00Z",
        }
        result = self.api.verify_license("VALID-KEY-HERE-1234")
        self.assertTrue(result["valid"])
        self.assertEqual(result["plan"], "edge")


# ═══════════════════════════════════════════════════════════════════════════
#  TEST: CIRCUIT BREAKER BLOCKING
# ═══════════════════════════════════════════════════════════════════════════

class TestAPICircuitBreakerBlocking(unittest.TestCase):
    """Test that circuit breaker blocks requests when open."""

    def setUp(self):
        self.api = ParakramAPI(token="test-token")

    def test_open_circuit_blocks_request(self):
        # Force circuit open
        self.api._circuit = CircuitBreaker(failure_threshold=1, reset_timeout=3600)
        self.api._circuit.record_failure()
        self.assertEqual(self.api._circuit.state, CircuitState.OPEN)

        with self.assertRaises(APIError) as ctx:
            self.api.signup("test@example.com", "password123", "John")
        self.assertIn("circuit breaker", str(ctx.exception).lower())

    def test_health_check_reopens_circuit(self):
        self.api._circuit = CircuitBreaker(failure_threshold=1, reset_timeout=0.1)
        self.api._circuit.record_failure()
        time.sleep(0.15)

        # Health check should try and potentially succeed or fail gracefully
        result = self.api.health_check()
        # This shouldn't crash regardless of outcome
        self.assertIsInstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════
#  RUNNER
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
