"""Unit tests for app.services.scorer — digital maturity & opportunity scoring."""

import os
import sys
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.scorer import (
    calculate_digital_maturity,
    calculate_opportunity_score,
    compute_scores,
    DIGITAL_MATURITY_WEIGHTS,
    OPPORTUNITY_WEIGHTS,
)


def _make_lead(**overrides):
    """Create a mock Lead with sensible defaults for scoring tests."""
    defaults = {
        "website_exists": False,
        "website_quality_score": 0.0,
        "mobile_responsive": False,
        "ssl_present": False,
        "gbp_complete": False,
        "social_media_active": False,
        "has_booking_system": False,
        "has_lead_form": False,
        "has_crm_indicators": False,
        "has_analytics": False,
        "has_whatsapp": False,
        "email_domain_quality": 0.0,
        "review_count": 0,
        "rating": 0.0,
        "business_size_estimate": None,
        "website_url": None,
        "opportunity_score": 0.0,
        "digital_maturity_score": 0.0,
        "predictive_quality_score": 0.0,
        "conversion_probability": 0.0,
        "buying_urgency": 0.0,
        "optimal_channel": None,
        "recommended_sequence_length": 3,
        "last_intelligence_update": None,
    }
    defaults.update(overrides)
    lead = MagicMock()
    for k, v in defaults.items():
        setattr(lead, k, v)
    return lead


class TestCalculateDigitalMaturity(unittest.TestCase):

    def test_zero_score_for_empty_lead(self):
        lead = _make_lead()
        result = asyncio.run(calculate_digital_maturity(lead))
        self.assertEqual(result, 0.0)

    def test_max_score_for_fully_digital_lead(self):
        lead = _make_lead(
            website_exists=True,
            website_quality_score=100.0,
            mobile_responsive=True,
            ssl_present=True,
            gbp_complete=True,
            social_media_active=True,
            has_booking_system=True,
            has_lead_form=True,
            has_crm_indicators=True,
            has_analytics=True,
            has_whatsapp=True,
            email_domain_quality=1.0,
        )
        result = asyncio.run(calculate_digital_maturity(lead))
        expected = sum(DIGITAL_MATURITY_WEIGHTS.values())
        self.assertEqual(result, min(expected, 100.0))

    def test_website_exists_adds_20(self):
        lead = _make_lead(website_exists=True)
        result = asyncio.run(calculate_digital_maturity(lead))
        self.assertEqual(result, DIGITAL_MATURITY_WEIGHTS["website_exists"])

    def test_website_quality_score_scaled(self):
        lead = _make_lead(website_quality_score=50.0)
        result = asyncio.run(calculate_digital_maturity(lead))
        expected = (50.0 / 100) * DIGITAL_MATURITY_WEIGHTS["website_quality_score"]
        self.assertAlmostEqual(result, expected)

    def test_ssl_adds_5(self):
        lead = _make_lead(ssl_present=True)
        result = asyncio.run(calculate_digital_maturity(lead))
        self.assertEqual(result, DIGITAL_MATURITY_WEIGHTS["ssl_present"])

    def test_email_domain_quality_scaled(self):
        lead = _make_lead(email_domain_quality=0.5)
        result = asyncio.run(calculate_digital_maturity(lead))
        expected = 0.5 * DIGITAL_MATURITY_WEIGHTS["email_domain_quality"]
        self.assertAlmostEqual(result, expected)

    def test_score_capped_at_100(self):
        lead = _make_lead(
            website_exists=True,
            website_quality_score=100.0,
            mobile_responsive=True,
            ssl_present=True,
            gbp_complete=True,
            social_media_active=True,
            has_booking_system=True,
            has_lead_form=True,
            has_crm_indicators=True,
            has_analytics=True,
            has_whatsapp=True,
            email_domain_quality=1.0,
        )
        result = asyncio.run(calculate_digital_maturity(lead))
        self.assertLessEqual(result, 100.0)

    def test_partial_score_combination(self):
        lead = _make_lead(
            website_exists=True,
            mobile_responsive=True,
            ssl_present=True,
        )
        result = asyncio.run(calculate_digital_maturity(lead))
        expected = (
            DIGITAL_MATURITY_WEIGHTS["website_exists"]
            + DIGITAL_MATURITY_WEIGHTS["mobile_responsive"]
            + DIGITAL_MATURITY_WEIGHTS["ssl_present"]
        )
        self.assertEqual(result, expected)


class TestCalculateOpportunityScore(unittest.TestCase):

    def test_max_opportunity_for_no_digital_presence(self):
        lead = _make_lead(
            website_exists=False,
            has_booking_system=False,
            has_lead_form=False,
            social_media_active=False,
            has_analytics=False,
            review_count=0,
            has_whatsapp=False,
            ssl_present=False,
            rating=0.0,
        )
        result = asyncio.run(calculate_opportunity_score(lead))
        # no_website and low_quality_website are mutually exclusive (elif)
        # so max base = 30 + 10 + 10 + 10 + 5 + 5 + 5 + 5 = 80
        expected = (
            OPPORTUNITY_WEIGHTS["no_website"]
            + OPPORTUNITY_WEIGHTS["no_booking"]
            + OPPORTUNITY_WEIGHTS["no_lead_form"]
            + OPPORTUNITY_WEIGHTS["no_social_media"]
            + OPPORTUNITY_WEIGHTS["no_analytics"]
            + OPPORTUNITY_WEIGHTS["low_reviews"]
            + OPPORTUNITY_WEIGHTS["no_whatsapp"]
            + OPPORTUNITY_WEIGHTS["no_ssl"]
        )
        self.assertAlmostEqual(result, expected)

    def test_zero_opportunity_for_full_digital_presence(self):
        lead = _make_lead(
            website_exists=True,
            website_quality_score=80.0,
            has_booking_system=True,
            has_lead_form=True,
            social_media_active=True,
            has_analytics=True,
            review_count=50,
            has_whatsapp=True,
            ssl_present=True,
            rating=3.0,
        )
        result = asyncio.run(calculate_opportunity_score(lead))
        self.assertEqual(result, 0.0)

    def test_low_quality_website_triggers_score(self):
        lead = _make_lead(
            website_exists=True,
            website_quality_score=30.0,
            has_booking_system=True,
            has_lead_form=True,
            social_media_active=True,
            has_analytics=True,
            review_count=50,
            has_whatsapp=True,
            ssl_present=True,
            rating=3.0,
        )
        result = asyncio.run(calculate_opportunity_score(lead))
        self.assertEqual(result, OPPORTUNITY_WEIGHTS["low_quality_website"])

    def test_high_rating_multiplier(self):
        lead = _make_lead(
            website_exists=False,
            has_booking_system=True,
            has_lead_form=True,
            social_media_active=True,
            has_analytics=True,
            review_count=5,
            has_whatsapp=True,
            ssl_present=True,
            rating=4.5,
        )
        base_score = OPPORTUNITY_WEIGHTS["no_website"] + OPPORTUNITY_WEIGHTS["low_reviews"]
        result = asyncio.run(calculate_opportunity_score(lead))
        self.assertAlmostEqual(result, base_score * 1.2)

    def test_high_review_count_multiplier(self):
        lead = _make_lead(
            website_exists=False,
            has_booking_system=True,
            has_lead_form=True,
            social_media_active=True,
            has_analytics=True,
            review_count=100,
            has_whatsapp=True,
            ssl_present=True,
            rating=3.5,
        )
        base_score = OPPORTUNITY_WEIGHTS["no_website"]
        result = asyncio.run(calculate_opportunity_score(lead))
        self.assertAlmostEqual(result, base_score * 1.15)

    def test_medium_business_size_multiplier(self):
        lead = _make_lead(
            website_exists=False,
            has_booking_system=True,
            has_lead_form=True,
            social_media_active=True,
            has_analytics=True,
            review_count=5,
            has_whatsapp=True,
            ssl_present=True,
            rating=3.0,
            business_size_estimate="medium",
        )
        base_score = OPPORTUNITY_WEIGHTS["no_website"] + OPPORTUNITY_WEIGHTS["low_reviews"]
        result = asyncio.run(calculate_opportunity_score(lead))
        self.assertAlmostEqual(result, base_score * 1.1)

    def test_combined_multipliers(self):
        lead = _make_lead(
            website_exists=False,
            has_booking_system=True,
            has_lead_form=True,
            social_media_active=True,
            has_analytics=True,
            review_count=100,
            has_whatsapp=True,
            ssl_present=True,
            rating=4.5,
            business_size_estimate="large",
        )
        base_score = OPPORTUNITY_WEIGHTS["no_website"]
        result = asyncio.run(calculate_opportunity_score(lead))
        expected = base_score * 1.2 * 1.15 * 1.1
        self.assertAlmostEqual(result, min(expected, 100.0))

    def test_score_capped_at_100(self):
        lead = _make_lead(
            website_exists=False,
            has_booking_system=False,
            has_lead_form=False,
            social_media_active=False,
            has_analytics=False,
            review_count=0,
            has_whatsapp=False,
            ssl_present=False,
            rating=5.0,
            business_size_estimate="large",
        )
        result = asyncio.run(calculate_opportunity_score(lead))
        self.assertLessEqual(result, 100.0)


class TestComputeScores(unittest.TestCase):

    @patch("app.services.scorer.compute_predictive_score")
    @patch("app.services.scorer.analyze_website_async")
    def test_compute_scores_with_website(self, mock_analyze, mock_predictive):
        mock_analyze.return_value = {
            "website_exists": True,
            "website_quality_score": 60.0,
            "mobile_responsive": True,
            "ssl_present": True,
            "has_booking_system": False,
            "has_lead_form": True,
            "has_analytics": True,
            "has_whatsapp": False,
        }
        mock_predictive.return_value = {
            "overall_quality": 75.0,
            "conversion_probability": 0.6,
            "urgency": 0.8,
            "optimal_channel": "email",
            "recommended_sequence_length": 4,
        }
        lead = _make_lead(website_url="https://example.com")
        dm, opp = asyncio.run(compute_scores(lead))
        self.assertIsInstance(dm, float)
        self.assertIsInstance(opp, float)
        self.assertTrue(lead.website_exists)
        self.assertEqual(lead.predictive_quality_score, 75.0)
        self.assertEqual(lead.optimal_channel, "email")
        mock_analyze.assert_called_once_with("https://example.com")

    @patch("app.services.scorer.compute_predictive_score")
    @patch("app.services.scorer.analyze_website_async")
    def test_compute_scores_without_website(self, mock_analyze, mock_predictive):
        mock_predictive.return_value = {
            "overall_quality": 30.0,
            "conversion_probability": 0.2,
            "urgency": 0.3,
            "optimal_channel": "whatsapp",
            "recommended_sequence_length": 2,
        }
        lead = _make_lead(website_url=None)
        dm, opp = asyncio.run(compute_scores(lead))
        mock_analyze.assert_not_called()
        self.assertIsInstance(dm, float)
        self.assertIsInstance(opp, float)


if __name__ == "__main__":
    unittest.main(verbosity=2)
