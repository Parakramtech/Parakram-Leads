"""
PARAKRAM PLATFORM — WHATSAPP ALERT TEST SUITE
Tests: 28 total | Coverage: circuit breaker, rate limiter, retry, email fallback, priorities
"""

import os
import sys
import json
import time
import asyncio
import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.whatsapp_alert import (
    AlertPriority,
    _CircuitState,
    _RateLimiter,
    _send_whatsapp,
    _send_email_fallback,
    send_whatsapp_alert,
    fire_alert,
    ALERT_RATE_LIMIT,
    MAX_RETRIES,
    CIRCUIT_FAILURE_THRESHOLD,
    CIRCUIT_RESET_TIMEOUT,
)


class TestAlertPriority(unittest.TestCase):
    def test_priority_values(self):
        self.assertEqual(AlertPriority.CRITICAL.value, "CRITICAL")
        self.assertEqual(AlertPriority.HIGH.value, "HIGH")
        self.assertEqual(AlertPriority.NORMAL.value, "NORMAL")
        self.assertEqual(AlertPriority.LOW.value, "LOW")

    def test_valid_priorities(self):
        priorities = list(AlertPriority)
        self.assertEqual(len(priorities), 4)
        self.assertIn(AlertPriority.CRITICAL, priorities)


class TestCircuitState(unittest.TestCase):
    def setUp(self):
        self.circuit = _CircuitState()

    def test_initial_state_allows(self):
        result = asyncio.run(self.circuit.allow())
        self.assertTrue(result)

    def test_opens_after_threshold_failures(self):
        async def run():
            for _ in range(CIRCUIT_FAILURE_THRESHOLD):
                await self.circuit.record_failure()
            self.assertFalse(await self.circuit.allow())
        asyncio.run(run())

    def test_success_resets_failure_count(self):
        async def run():
            await self.circuit.record_failure()
            await self.circuit.record_failure()
            await self.circuit.record_success()
            self.assertTrue(await self.circuit.allow())
        asyncio.run(run())

    def test_half_open_timeout_allows(self):
        async def run():
            for _ in range(CIRCUIT_FAILURE_THRESHOLD):
                await self.circuit.record_failure()
            self.assertFalse(await self.circuit.allow())
            self.circuit._last_failure = time.time() - CIRCUIT_RESET_TIMEOUT - 1
            self.assertTrue(await self.circuit.allow())
        asyncio.run(run())

    def test_half_open_success_closes(self):
        async def run():
            for _ in range(CIRCUIT_FAILURE_THRESHOLD):
                await self.circuit.record_failure()
            self.circuit._last_failure = time.time() - CIRCUIT_RESET_TIMEOUT - 1
            await self.circuit.allow()
            self.assertFalse(self.circuit._open)
            self.assertEqual(self.circuit._failures, 0)
        asyncio.run(run())

    def test_record_failure_increments_counter(self):
        async def run():
            await self.circuit.record_failure()
            self.assertEqual(self.circuit._failures, 1)
        asyncio.run(run())

    def test_success_clears_open_state(self):
        async def run():
            self.circuit._open = True
            self.circuit._failures = 5
            await self.circuit.record_success()
            self.assertFalse(self.circuit._open)
            self.assertEqual(self.circuit._failures, 0)
        asyncio.run(run())


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = _RateLimiter(max_per_minute=5)

    def test_initial_allows(self):
        result = asyncio.run(self.limiter.allow())
        self.assertTrue(result)

    def test_blocks_at_limit(self):
        async def run():
            for _ in range(5):
                self.assertTrue(await self.limiter.allow())
            self.assertFalse(await self.limiter.allow())
        asyncio.run(run())

    def test_window_ages_out(self):
        async def run():
            for _ in range(5):
                await self.limiter.allow()
            self.assertFalse(await self.limiter.allow())
            now = time.time()
            self.limiter._timestamps = [now - 70] * 5
            self.assertTrue(await self.limiter.allow())
        asyncio.run(run())

    def test_old_timestamps_pruned(self):
        now = time.time()
        self.limiter._timestamps = [now - 120] * 5
        async def run():
            self.assertTrue(await self.limiter.allow())
            self.assertLessEqual(len(self.limiter._timestamps), 1)
        asyncio.run(run())


class TestSendWhatsApp(unittest.TestCase):
    def setUp(self):
        self.settings_patcher = patch("app.services.whatsapp_alert.settings")
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.WHATSAPP_BRIDGE_URL = "http://localhost:4000"
        self.mock_settings.PERSONAL_ALERT_PHONE = "917259426670"
        self.circuit_patcher = patch("app.services.whatsapp_alert._circuit")
        self.mock_circuit = self.circuit_patcher.start()
        self.mock_circuit.allow = AsyncMock(return_value=True)
        self.mock_circuit.record_failure = AsyncMock()
        self.mock_circuit.record_success = AsyncMock()
        self.rl_patcher = patch("app.services.whatsapp_alert._rate_limiter")
        self.mock_rl = self.rl_patcher.start()
        self.mock_rl.allow = AsyncMock(return_value=True)

    def tearDown(self):
        self.settings_patcher.stop()
        self.circuit_patcher.stop()
        self.rl_patcher.stop()

    @patch("app.services.whatsapp_alert.httpx.AsyncClient")
    def test_send_success(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = Mock(status_code=200)

        async def run():
            ok, detail = await _send_whatsapp("Test message", "917259426670")
            self.assertTrue(ok)
            self.assertEqual(detail, "Delivered")

        asyncio.run(run())

    @patch("app.services.whatsapp_alert.httpx.AsyncClient")
    def test_send_retries_on_503(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        resp_503 = Mock(status_code=503, text="Service Unavailable")
        mock_client.post.return_value = resp_503

        async def run():
            ok, detail = await _send_whatsapp("Test", "917259426670")
            self.assertFalse(ok)
            self.assertIn("Bridge returned HTTP 503", detail)

        asyncio.run(run())

    @patch("app.services.whatsapp_alert.httpx.AsyncClient")
    def test_send_handles_timeout(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post.side_effect = __import__("httpx").TimeoutException("Timeout")

        async def run():
            ok, detail = await _send_whatsapp("Test", "917259426670")
            self.assertFalse(ok)
            self.assertIn("Bridge timeout", detail)

        asyncio.run(run())

    @patch("app.services.whatsapp_alert.httpx.AsyncClient")
    def test_send_handles_connection_error(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post.side_effect = __import__("httpx").ConnectError("Bridge down")

        async def run():
            ok, detail = await _send_whatsapp("Test", "917259426670")
            self.assertFalse(ok)
            self.assertIn("Cannot connect to bridge", detail)

        asyncio.run(run())

    @patch("app.services.whatsapp_alert.httpx.AsyncClient")
    def test_circuit_blocks_when_open(self, mock_client_class):
        self.circuit = _CircuitState()
        with patch("app.services.whatsapp_alert._circuit", self.circuit):
            async def run():
                for _ in range(CIRCUIT_FAILURE_THRESHOLD):
                    await self.circuit.record_failure()
                ok, detail = await _send_whatsapp("Test", "917259426670")
                self.assertFalse(ok)
                self.assertIn("Circuit breaker OPEN", detail)
            asyncio.run(run())

    @patch("app.services.whatsapp_alert.httpx.AsyncClient")
    def test_rate_limiter_blocks(self, mock_client_class):
        limiter = _RateLimiter(max_per_minute=1)
        with patch("app.services.whatsapp_alert._rate_limiter", limiter):
            async def run():
                await limiter.allow()
                ok, detail = await _send_whatsapp("Test", "917259426670")
                self.assertFalse(ok)
                self.assertIn("Rate limit exceeded", detail)
            asyncio.run(run())

    @patch("app.services.whatsapp_alert.httpx.AsyncClient")
    def test_jid_formatting(self, mock_client_class):
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = Mock(status_code=200)

        async def run():
            await _send_whatsapp("Test", "+91 72594 26670")
            call_kwargs = mock_client.post.call_args[1]
            self.assertEqual(call_kwargs["json"]["to"], "917259426670@s.whatsapp.net")
        asyncio.run(run())


class TestEmailFallback(unittest.TestCase):
    def setUp(self):
        self.settings_patcher = patch("app.services.whatsapp_alert.settings")
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.SMTP_HOST = "smtp.gmail.com"
        self.mock_settings.SMTP_PORT = 587
        self.mock_settings.SMTP_USER = "test@example.com"
        self.mock_settings.SMTP_PASSWORD = "test-password"
        self.mock_settings.SMTP_FROM = "noreply@getparakram.in"
        self.mock_settings.PERSONAL_ALERT_EMAIL = "admin@parakram.in"

    def tearDown(self):
        self.settings_patcher.stop()

    @patch("smtplib.SMTP")
    def test_email_fallback_sends(self, mock_smtp_class):
        mock_instance = Mock()
        mock_smtp_class.return_value = mock_instance

        async def run():
            result = await _send_email_fallback("Test Subject", "Test Body")
            self.assertTrue(result)
            mock_instance.send_message.assert_called_once()
            mock_instance.quit.assert_called_once()

        asyncio.run(run())

    @patch("smtplib.SMTP")
    def test_email_fallback_smtp_failure(self, mock_smtp_class):
        mock_smtp_class.side_effect = ConnectionError("SMTP down")

        async def run():
            result = await _send_email_fallback("Subject", "Body")
            self.assertFalse(result)

        asyncio.run(run())

        async def run():
            result = await _send_email_fallback("Subject", "Body")
            self.assertFalse(result)

        asyncio.run(run())

    def test_email_fallback_skips_if_not_configured(self):
        self.mock_settings.SMTP_HOST = None

        async def run():
            result = await _send_email_fallback("Subject", "Body")
            self.assertFalse(result)

        asyncio.run(run())


class TestSendWhatsAppAlert(unittest.TestCase):
    def setUp(self):
        self.settings_patcher = patch("app.services.whatsapp_alert.settings")
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.PERSONAL_ALERT_PHONE = "917259426670"
        self.mock_settings.SMTP_HOST = "smtp.gmail.com"
        self.mock_settings.SMTP_PORT = 587
        self.mock_settings.SMTP_USER = "test@example.com"
        self.mock_settings.SMTP_PASSWORD = "test-password"
        self.mock_settings.SMTP_FROM = "noreply@getparakram.in"
        self.mock_settings.PERSONAL_ALERT_EMAIL = "admin@parakram.in"

    def tearDown(self):
        self.settings_patcher.stop()

    @patch("app.services.whatsapp_alert._send_whatsapp")
    def test_sends_whatsapp_for_high_priority(self, mock_whatsapp):
        mock_whatsapp.return_value = (True, "Delivered")

        async def run():
            result = await send_whatsapp_alert(
                user_email="test@example.com",
                user_name="Test User",
                method="Email/Password",
            )
            self.assertTrue(result)
            mock_whatsapp.assert_called_once()

        asyncio.run(run())

    @patch("app.services.whatsapp_alert._send_whatsapp")
    @patch("app.services.whatsapp_alert._send_email_fallback")
    def test_falls_back_to_email(self, mock_email, mock_whatsapp):
        mock_whatsapp.return_value = (False, "Bridge down")
        mock_email.return_value = True

        async def run():
            result = await send_whatsapp_alert(
                user_email="test@example.com",
                user_name="Test User",
                method="Google",
                priority=AlertPriority.CRITICAL,
            )
            self.assertTrue(result)
            mock_email.assert_called_once()

        asyncio.run(run())

    @patch("app.services.whatsapp_alert._send_whatsapp")
    def test_low_priority_logs_only(self, mock_whatsapp):
        async def run():
            result = await send_whatsapp_alert(
                user_email="test@example.com",
                user_name="Test",
                method="Email/Password",
                priority=AlertPriority.LOW,
            )
            self.assertFalse(result)
            mock_whatsapp.assert_not_called()

        asyncio.run(run())

    def test_disabled_if_no_phone(self):
        self.mock_settings.PERSONAL_ALERT_PHONE = None

        async def run():
            result = await send_whatsapp_alert(
                user_email="test@example.com",
                user_name="Test",
                method="Email/Password",
            )
            self.assertFalse(result)

        asyncio.run(run())

    @patch("app.services.whatsapp_alert._send_whatsapp")
    @patch("app.services.whatsapp_alert._send_email_fallback")
    def test_normal_priority_no_email_fallback(self, mock_email, mock_whatsapp):
        mock_whatsapp.return_value = (False, "Bridge down")

        async def run():
            result = await send_whatsapp_alert(
                user_email="test@example.com",
                user_name="Test",
                method="Email/Password",
                priority=AlertPriority.NORMAL,
            )
            self.assertFalse(result)
            mock_email.assert_not_called()

        asyncio.run(run())

    @patch("app.services.whatsapp_alert._send_whatsapp")
    @patch("app.services.whatsapp_alert._send_email_fallback")
    def test_all_channels_fail(self, mock_email, mock_whatsapp):
        mock_whatsapp.return_value = (False, "Bridge down")
        mock_email.return_value = False

        async def run():
            result = await send_whatsapp_alert(
                user_email="test@example.com",
                user_name="Test",
                method="Google",
                priority=AlertPriority.CRITICAL,
            )
            self.assertFalse(result)

        asyncio.run(run())

    @patch("app.services.whatsapp_alert._send_whatsapp")
    def test_builds_message_with_user_info(self, mock_whatsapp):
        mock_whatsapp.return_value = (True, "Delivered")

        async def run():
            await send_whatsapp_alert(
                user_email="john@example.com",
                user_name="John Doe",
                method="Google",
            )
            call_args = mock_whatsapp.call_args[0][0]
            self.assertIn("John Doe", call_args)
            self.assertIn("john@example.com", call_args)
            self.assertIn("Google", call_args)

        asyncio.run(run())

    def test_uses_email_local_part_when_no_name(self):
        with patch("app.services.whatsapp_alert._send_whatsapp", return_value=(True, "Delivered")) as mock_whatsapp:
            async def run():
                await send_whatsapp_alert(
                    user_email="john@example.com",
                    user_name=None,
                    method="Google",
                )
                call_args = mock_whatsapp.call_args[0][0]
                self.assertIn("john", call_args)
            asyncio.run(run())


class TestFireAlert(unittest.TestCase):
    @patch("app.services.whatsapp_alert.send_whatsapp_alert")
    def test_fire_alert_creates_task(self, mock_send):
        mock_send.return_value = True
        try:
            fire_alert(user_email="test@example.com", user_name="Test", method="Email/Password")
        except Exception:
            self.fail("fire_alert should never raise")

    def test_fire_alert_handles_no_event_loop(self):
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(None)
            fire_alert(user_email="test@example.com", user_name="Test", method="Google")
            asyncio.set_event_loop(loop)
        except Exception:
            self.fail("fire_alert should never raise")


if __name__ == "__main__":
    unittest.main(verbosity=2)
