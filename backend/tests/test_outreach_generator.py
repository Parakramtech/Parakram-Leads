"""Unit tests for app.services.outreach_generator — AI and fallback outreach message generation."""

import os
import sys
import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.outreach_generator import generate_outreach, _generate_outreach_fallback


def _make_lead(**overrides):
    defaults = {
        "business_name": "Test Corp",
        "owner_name": "John",
        "industry": "Technology",
        "category": "IT Services",
        "location": "Bangalore",
        "website_url": "https://testcorp.com",
        "business_description": "A tech company",
        "estimated_needs": ["Website", "SEO"],
        "suggested_solution": "professional website with SEO optimization",
    }
    defaults.update(overrides)
    lead = MagicMock()
    for k, v in defaults.items():
        setattr(lead, k, v)
    return lead


class TestGenerateOutreachFallback(unittest.TestCase):

    def test_fallback_returns_all_channels(self):
        lead = _make_lead()
        result = _generate_outreach_fallback(lead, "John", "Website, SEO")
        self.assertIn("whatsapp", result)
        self.assertIn("email", result)
        self.assertIn("linkedin", result)

    def test_fallback_includes_business_name(self):
        lead = _make_lead(business_name="Acme Inc")
        result = _generate_outreach_fallback(lead, "John", "Website")
        self.assertIn("Acme Inc", result["whatsapp"])
        self.assertIn("Acme Inc", result["email"])

    def test_fallback_includes_owner_name(self):
        lead = _make_lead()
        result = _generate_outreach_fallback(lead, "Sarah", "Website")
        self.assertIn("Sarah", result["whatsapp"])
        self.assertIn("Sarah", result["email"])
        self.assertIn("Sarah", result["linkedin"])

    def test_fallback_legal_industry(self):
        lead = _make_lead(industry="Lawyer")
        result = _generate_outreach_fallback(lead, "John", "Website")
        self.assertIn("client", result["whatsapp"].lower())
        self.assertIn("Subject:", result["email"])

    def test_fallback_advocate_industry(self):
        lead = _make_lead(industry="Advocate Firm")
        result = _generate_outreach_fallback(lead, "Jane", "Digital presence")
        self.assertIn("Jane", result["whatsapp"])

    def test_fallback_architect_industry(self):
        lead = _make_lead(industry="Architecture Studio")
        result = _generate_outreach_fallback(lead, "Mike", "Portfolio website")
        self.assertIn("portfolio", result["whatsapp"].lower())

    def test_fallback_interior_design(self):
        lead = _make_lead(industry="Interior Design")
        result = _generate_outreach_fallback(lead, "Anna", "Website")
        self.assertIn("portfolio", result["whatsapp"].lower())

    def test_fallback_photographer_industry(self):
        lead = _make_lead(industry="Photography Studio")
        result = _generate_outreach_fallback(lead, "Sam", "Portfolio")
        self.assertIn("portfolio", result["whatsapp"].lower())

    def test_fallback_doctor_industry(self):
        lead = _make_lead(industry="Doctor Clinic")
        result = _generate_outreach_fallback(lead, "Dr. Patel", "Online booking")
        self.assertIn("booking", result["whatsapp"].lower())

    def test_fallback_hospital_industry(self):
        lead = _make_lead(industry="Hospital")
        result = _generate_outreach_fallback(lead, "Admin", "Appointments")
        self.assertIn("appointment", result["email"].lower())

    def test_fallback_restaurant_industry(self):
        lead = _make_lead(industry="Restaurant")
        result = _generate_outreach_fallback(lead, "Chef Kumar", "Online ordering")
        self.assertIn("order", result["whatsapp"].lower())

    def test_fallback_cafe_industry(self):
        lead = _make_lead(industry="Cafe & Bakery")
        result = _generate_outreach_fallback(lead, "Owner", "Digital menu")
        self.assertIn("order", result["whatsapp"].lower())

    def test_fallback_accountant_industry(self):
        lead = _make_lead(industry="CA Firm / Accountant")
        result = _generate_outreach_fallback(lead, "CA Sharma", "Client portal")
        self.assertIn("client", result["whatsapp"].lower())

    def test_fallback_financial_industry(self):
        lead = _make_lead(industry="Financial Advisor")
        result = _generate_outreach_fallback(lead, "Raj", "Portfolio")
        self.assertIn("financial", result["email"].lower())

    def test_fallback_generic_industry(self):
        lead = _make_lead(industry="Plumbing Services")
        result = _generate_outreach_fallback(lead, "Bob", "Website")
        self.assertIn("online presence", result["whatsapp"].lower())

    def test_fallback_empty_industry(self):
        lead = _make_lead(industry=None)
        result = _generate_outreach_fallback(lead, "Owner", "Digital tools")
        self.assertIn("whatsapp", result)
        self.assertIn("email", result)
        self.assertIn("linkedin", result)


class TestGenerateOutreach(unittest.TestCase):

    @patch("app.services.outreach_generator.settings")
    def test_no_api_key_uses_fallback(self, mock_settings):
        mock_settings.OPENAI_API_KEY = ""
        lead = _make_lead()
        result = asyncio.run(generate_outreach(lead))
        self.assertIn("whatsapp", result)
        self.assertIn("email", result)
        self.assertIn("linkedin", result)

    @patch("app.services.outreach_generator.settings")
    def test_fallback_handles_none_owner(self, mock_settings):
        mock_settings.OPENAI_API_KEY = ""
        lead = _make_lead(owner_name=None)
        result = asyncio.run(generate_outreach(lead))
        self.assertIn("there", result["whatsapp"])

    @patch("app.services.outreach_generator.settings")
    def test_fallback_handles_none_needs(self, mock_settings):
        mock_settings.OPENAI_API_KEY = ""
        lead = _make_lead(estimated_needs=None)
        result = asyncio.run(generate_outreach(lead))
        self.assertIn("whatsapp", result)

    @patch("app.services.outreach_generator.settings")
    def test_fallback_handles_empty_needs_list(self, mock_settings):
        mock_settings.OPENAI_API_KEY = ""
        lead = _make_lead(estimated_needs=[])
        result = asyncio.run(generate_outreach(lead))
        self.assertIn("whatsapp", result)

    @patch("httpx.AsyncClient")
    @patch("app.services.outreach_generator.settings")
    def test_openai_success(self, mock_settings, mock_client_class):
        mock_settings.OPENAI_API_KEY = "sk-test-key"
        mock_settings.OPENAI_MODEL = "gpt-4o"

        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"whatsapp": "Hi!", "email": "Subject: Hi", "linkedin": "Connect?"}'
                    }
                }
            ]
        }
        mock_client.post = AsyncMock(return_value=mock_response)

        lead = _make_lead()
        result = asyncio.run(generate_outreach(lead))
        self.assertEqual(result["whatsapp"], "Hi!")
        self.assertEqual(result["linkedin"], "Connect?")

    @patch("httpx.AsyncClient")
    @patch("app.services.outreach_generator.settings")
    def test_openai_failure_falls_back(self, mock_settings, mock_client_class):
        mock_settings.OPENAI_API_KEY = "sk-test-key"
        mock_settings.OPENAI_MODEL = "gpt-4o"

        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.post = AsyncMock(return_value=mock_response)

        lead = _make_lead()
        result = asyncio.run(generate_outreach(lead))
        self.assertIn("whatsapp", result)
        self.assertIn("email", result)
        self.assertIn("linkedin", result)

    @patch("httpx.AsyncClient")
    @patch("app.services.outreach_generator.settings")
    def test_openai_exception_falls_back(self, mock_settings, mock_client_class):
        mock_settings.OPENAI_API_KEY = "sk-test-key"
        mock_settings.OPENAI_MODEL = "gpt-4o"

        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=Exception("Network error"))

        lead = _make_lead()
        result = asyncio.run(generate_outreach(lead))
        self.assertIn("whatsapp", result)
        self.assertIn("email", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
