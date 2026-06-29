"""Unit tests for app.services.email_service — SendGrid & SMTP providers + tracking pixel."""

import os
import sys
import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.email_service import (
    _inject_tracking_pixel,
    SendGridProvider,
    SMTPProvider,
    get_email_provider,
)


class TestInjectTrackingPixel(unittest.TestCase):

    @patch("app.services.email_service.settings")
    def test_injects_pixel_before_body_tag(self, mock_settings):
        mock_settings.EMAIL_TRACKING_BASE_URL = "http://localhost:8000"
        html = "<html><body><p>Hello</p></body></html>"
        result = _inject_tracking_pixel(html, "track-123")
        self.assertIn('src="http://localhost:8000/api/v1/webhooks/email/track/track-123"', result)
        self.assertIn("</body>", result)
        self.assertTrue(result.index("track-123") < result.index("</body>"))

    @patch("app.services.email_service.settings")
    def test_appends_pixel_if_no_body_tag(self, mock_settings):
        mock_settings.EMAIL_TRACKING_BASE_URL = "http://localhost:8000"
        html = "<p>Hello World</p>"
        result = _inject_tracking_pixel(html, "track-456")
        self.assertIn("track-456", result)
        self.assertTrue(result.endswith('/>'))

    def test_no_tracking_id_returns_unchanged(self):
        html = "<html><body><p>Hello</p></body></html>"
        result = _inject_tracking_pixel(html, None)
        self.assertEqual(result, html)

    def test_empty_tracking_id_returns_unchanged(self):
        html = "<html><body><p>Hello</p></body></html>"
        result = _inject_tracking_pixel(html, "")
        self.assertEqual(result, html)

    @patch("app.services.email_service.settings")
    def test_strips_trailing_slash_from_base_url(self, mock_settings):
        mock_settings.EMAIL_TRACKING_BASE_URL = "http://example.com/"
        html = "<html><body></body></html>"
        result = _inject_tracking_pixel(html, "id-789")
        self.assertIn("http://example.com/api/v1/webhooks/email/track/id-789", result)
        self.assertNotIn("http://example.com//", result)


class TestSendGridProvider(unittest.TestCase):

    @patch("app.services.email_service.settings")
    @patch("app.services.email_service._inject_tracking_pixel")
    def test_send_success(self, mock_pixel, mock_settings):
        mock_settings.SMTP_FROM = "noreply@example.com"
        mock_settings.SENDGRID_API_KEY = "SG.test-key"
        mock_pixel.return_value = "<p>tracked</p>"

        with patch("sendgrid.SendGridAPIClient") as mock_sg_class:
            mock_sg = MagicMock()
            mock_sg_class.return_value = mock_sg
            mock_response = MagicMock()
            mock_response.status_code = 202
            mock_response.headers = {"X-Message-Id": "msg-abc"}
            mock_sg.send.return_value = mock_response

            provider = SendGridProvider()
            result = asyncio.run(provider.send("to@example.com", "Test Subject", "<p>Body</p>", "track-1"))
            self.assertEqual(result, "msg-abc")
            mock_sg.send.assert_called_once()

    @patch("app.services.email_service.settings")
    @patch("app.services.email_service._inject_tracking_pixel")
    def test_send_failure_status(self, mock_pixel, mock_settings):
        mock_settings.SMTP_FROM = "noreply@example.com"
        mock_settings.SENDGRID_API_KEY = "SG.test-key"
        mock_pixel.return_value = "<p>tracked</p>"

        with patch("sendgrid.SendGridAPIClient") as mock_sg_class:
            mock_sg = MagicMock()
            mock_sg_class.return_value = mock_sg
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.body = "Bad request"
            mock_sg.send.return_value = mock_response

            provider = SendGridProvider()
            result = asyncio.run(provider.send("to@example.com", "Subject", "<p>Body</p>"))
            self.assertIsNone(result)

    @patch("app.services.email_service.settings")
    @patch("app.services.email_service._inject_tracking_pixel")
    def test_send_exception_returns_none(self, mock_pixel, mock_settings):
        mock_settings.SMTP_FROM = "noreply@example.com"
        mock_settings.SENDGRID_API_KEY = "SG.test-key"
        mock_pixel.return_value = "<p>tracked</p>"

        with patch("sendgrid.SendGridAPIClient") as mock_sg_class:
            mock_sg_class.side_effect = Exception("API error")

            provider = SendGridProvider()
            result = asyncio.run(provider.send("to@example.com", "Subject", "<p>Body</p>"))
            self.assertIsNone(result)


class TestSMTPProvider(unittest.TestCase):

    @patch("app.services.email_service.settings")
    @patch("app.services.email_service._inject_tracking_pixel")
    @patch("smtplib.SMTP")
    def test_send_success(self, mock_smtp_class, mock_pixel, mock_settings):
        mock_settings.SMTP_FROM = "noreply@example.com"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_pixel.return_value = "<p>tracked</p>"

        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        provider = SMTPProvider()
        result = asyncio.run(provider.send("to@example.com", "Test Subject", "<p>Body</p>", "track-1"))
        self.assertIsNone(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "password")
        mock_server.sendmail.assert_called_once()

    @patch("app.services.email_service.settings")
    @patch("app.services.email_service._inject_tracking_pixel")
    @patch("smtplib.SMTP")
    def test_send_exception_returns_none(self, mock_smtp_class, mock_pixel, mock_settings):
        mock_settings.SMTP_FROM = "noreply@example.com"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user"
        mock_settings.SMTP_PASSWORD = "pass"
        mock_pixel.return_value = "<p>tracked</p>"

        mock_smtp_class.side_effect = ConnectionRefusedError("Connection refused")

        provider = SMTPProvider()
        result = asyncio.run(provider.send("to@example.com", "Subject", "<p>Body</p>"))
        self.assertIsNone(result)


class TestGetEmailProvider(unittest.TestCase):

    @patch("app.services.email_service.settings")
    def test_returns_sendgrid_when_configured(self, mock_settings):
        mock_settings.SENDGRID_API_KEY = "SG.valid-key"
        provider = get_email_provider()
        self.assertIsInstance(provider, SendGridProvider)

    @patch("app.services.email_service.settings")
    def test_returns_smtp_when_no_sendgrid(self, mock_settings):
        mock_settings.SENDGRID_API_KEY = ""
        provider = get_email_provider()
        self.assertIsInstance(provider, SMTPProvider)

    @patch("app.services.email_service.settings")
    def test_returns_smtp_when_sendgrid_none(self, mock_settings):
        mock_settings.SENDGRID_API_KEY = None
        provider = get_email_provider()
        self.assertIsInstance(provider, SMTPProvider)


if __name__ == "__main__":
    unittest.main(verbosity=2)
