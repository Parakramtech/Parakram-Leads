"""Unit tests for app.services.communicator — multi-channel message sending."""

import os
import sys
import asyncio
import uuid
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.communicator import (
    send_email,
    send_whatsapp_bridge,
    send_whatsapp,
    send_message,
)
from app.models.message import MessageChannel, MessageStatus


def _make_lead(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "phone": "+919876543210",
        "business_name": "Test Corp",
    }
    defaults.update(overrides)
    lead = MagicMock()
    for k, v in defaults.items():
        setattr(lead, k, v)
    return lead


def _make_message(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "content": "Subject: Test\n\nHello, this is a test message.",
        "status": MessageStatus.DRAFT,
        "sent_at": None,
        "external_id": None,
    }
    defaults.update(overrides)
    msg = MagicMock()
    for k, v in defaults.items():
        setattr(msg, k, v)
    return msg


def _make_db():
    db = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    db.refresh = AsyncMock()
    return db


class TestSendEmail(unittest.TestCase):

    @patch("app.services.communicator.settings")
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp_class, mock_settings):
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.SMTP_FROM = "noreply@example.com"

        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_email(lead, message, db))
        self.assertTrue(result)
        self.assertEqual(message.status, MessageStatus.SENT)
        self.assertIsNotNone(message.sent_at)

    @patch("app.services.communicator.settings")
    def test_send_email_missing_config(self, mock_settings):
        mock_settings.SMTP_HOST = ""
        mock_settings.SMTP_USER = ""
        mock_settings.SMTP_PASSWORD = ""

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_email(lead, message, db))
        self.assertFalse(result)

    @patch("app.services.communicator.settings")
    @patch("smtplib.SMTP")
    def test_send_email_smtp_failure(self, mock_smtp_class, mock_settings):
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user"
        mock_settings.SMTP_PASSWORD = "pass"
        mock_settings.SMTP_FROM = "from@example.com"

        mock_smtp_class.side_effect = ConnectionRefusedError("SMTP down")

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_email(lead, message, db))
        self.assertFalse(result)
        self.assertEqual(message.status, MessageStatus.FAILED)

    @patch("app.services.communicator.settings")
    @patch("smtplib.SMTP")
    def test_send_email_parses_subject_line(self, mock_smtp_class, mock_settings):
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user"
        mock_settings.SMTP_PASSWORD = "pass"
        mock_settings.SMTP_FROM = "from@example.com"

        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        lead = _make_lead()
        message = _make_message(content="Subject: Important\n\nBody here")
        db = _make_db()

        asyncio.run(send_email(lead, message, db))
        call_args = mock_server.sendmail.call_args
        sent_msg = call_args[0][2]
        self.assertIn("Important", sent_msg)


class TestSendWhatsAppBridge(unittest.TestCase):

    @patch("app.services.communicator.settings")
    def test_no_bridge_url_returns_false(self, mock_settings):
        mock_settings.WHATSAPP_BRIDGE_URL = ""

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_whatsapp_bridge(lead, message, db))
        self.assertFalse(result)

    @patch("app.services.communicator.settings")
    def test_no_phone_returns_false(self, mock_settings):
        mock_settings.WHATSAPP_BRIDGE_URL = "http://localhost:4000"

        lead = _make_lead(phone=None)
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_whatsapp_bridge(lead, message, db))
        self.assertFalse(result)

    @patch("httpx.AsyncClient")
    @patch("app.services.communicator.settings")
    def test_bridge_send_success(self, mock_settings, mock_client_class):
        mock_settings.WHATSAPP_BRIDGE_URL = "http://localhost:4000"

        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "msg-bridge-123"}
        mock_client.post = AsyncMock(return_value=mock_response)

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_whatsapp_bridge(lead, message, db))
        self.assertTrue(result)
        self.assertEqual(message.status, MessageStatus.SENT)
        self.assertEqual(message.external_id, "msg-bridge-123")

    @patch("httpx.AsyncClient")
    @patch("app.services.communicator.settings")
    def test_bridge_send_failure_status(self, mock_settings, mock_client_class):
        mock_settings.WHATSAPP_BRIDGE_URL = "http://localhost:4000"

        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.post = AsyncMock(return_value=mock_response)

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_whatsapp_bridge(lead, message, db))
        self.assertFalse(result)
        self.assertEqual(message.status, MessageStatus.FAILED)


class TestSendWhatsApp(unittest.TestCase):

    @patch("app.services.communicator.send_whatsapp_bridge")
    @patch("app.services.communicator.settings")
    def test_falls_back_to_bridge_when_no_api_key(self, mock_settings, mock_bridge):
        mock_settings.WHATSAPP_API_KEY = ""
        mock_settings.WHATSAPP_PHONE_NUMBER_ID = ""
        mock_bridge.return_value = True

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_whatsapp(lead, message, db))
        self.assertTrue(result)
        mock_bridge.assert_called_once_with(lead, message, db)

    @patch("httpx.AsyncClient")
    @patch("app.services.communicator.settings")
    def test_whatsapp_api_success(self, mock_settings, mock_client_class):
        mock_settings.WHATSAPP_API_KEY = "wa-key"
        mock_settings.WHATSAPP_PHONE_NUMBER_ID = "123456"

        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": [{"id": "wamid-abc"}]}
        mock_client.post = AsyncMock(return_value=mock_response)

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_whatsapp(lead, message, db))
        self.assertTrue(result)
        self.assertEqual(message.status, MessageStatus.SENT)
        self.assertEqual(message.external_id, "wamid-abc")

    @patch("httpx.AsyncClient")
    @patch("app.services.communicator.settings")
    def test_whatsapp_api_failure(self, mock_settings, mock_client_class):
        mock_settings.WHATSAPP_API_KEY = "wa-key"
        mock_settings.WHATSAPP_PHONE_NUMBER_ID = "123456"

        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_client.post = AsyncMock(return_value=mock_response)

        lead = _make_lead()
        message = _make_message()
        db = _make_db()

        result = asyncio.run(send_whatsapp(lead, message, db))
        self.assertFalse(result)
        self.assertEqual(message.status, MessageStatus.FAILED)


class TestSendMessage(unittest.TestCase):

    @patch("app.services.communicator.send_email")
    def test_send_message_email_channel(self, mock_send_email):
        mock_send_email.return_value = True

        lead = _make_lead()
        db = _make_db()
        db.refresh = AsyncMock()

        result = asyncio.run(send_message(lead, MessageChannel.EMAIL, "Hello", db))
        mock_send_email.assert_called_once()
        db.add.assert_called_once()

    @patch("app.services.communicator.send_whatsapp")
    def test_send_message_whatsapp_channel(self, mock_send_wa):
        mock_send_wa.return_value = True

        lead = _make_lead()
        db = _make_db()
        db.refresh = AsyncMock()

        result = asyncio.run(send_message(lead, MessageChannel.WHATSAPP, "Hi", db))
        mock_send_wa.assert_called_once()

    def test_send_message_linkedin_stays_draft(self):
        lead = _make_lead()
        db = _make_db()
        db.refresh = AsyncMock()

        result = asyncio.run(send_message(lead, MessageChannel.LINKEDIN, "Connect", db))
        db.add.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
