"""Unit tests for app.services.prioritizer — lead categorization logic."""

import os
import sys
import asyncio
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.lead import LeadCategory
from app.services.prioritizer import categorize_lead, get_category_flags


def _make_lead(digital_maturity_score: float = 0.0, opportunity_score: float = 0.0):
    lead = MagicMock()
    lead.digital_maturity_score = digital_maturity_score
    lead.opportunity_score = opportunity_score
    return lead


class TestCategorizeLead(unittest.TestCase):

    def test_hot_lead_high_opportunity_low_maturity(self):
        lead = _make_lead(digital_maturity_score=20.0, opportunity_score=70.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.HOT)

    def test_hot_lead_boundary_opp_60_dm_39(self):
        lead = _make_lead(digital_maturity_score=39.0, opportunity_score=60.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.HOT)

    def test_warm_lead_moderate_opportunity(self):
        lead = _make_lead(digital_maturity_score=50.0, opportunity_score=50.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.WARM)

    def test_warm_lead_opp_40_dm_55(self):
        lead = _make_lead(digital_maturity_score=55.0, opportunity_score=40.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.WARM)

    def test_cold_lead_low_opportunity(self):
        lead = _make_lead(digital_maturity_score=80.0, opportunity_score=20.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.COLD)

    def test_cold_lead_zero_scores(self):
        lead = _make_lead(digital_maturity_score=0.0, opportunity_score=0.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.COLD)

    def test_hot_not_triggered_when_maturity_too_high(self):
        lead = _make_lead(digital_maturity_score=50.0, opportunity_score=70.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertNotEqual(result, LeadCategory.HOT)

    def test_warm_boundary_opp_50_dm_65(self):
        # opp >= 40 and (opp >= 50 or dm < 60) → True and (True or False) → WARM
        lead = _make_lead(digital_maturity_score=65.0, opportunity_score=50.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.WARM)

    def test_cold_when_opp_40_but_dm_high(self):
        # opp >= 40 and (opp >= 50 or dm < 60) → True and (False or False) → COLD
        lead = _make_lead(digital_maturity_score=70.0, opportunity_score=40.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.COLD)

    def test_cold_boundary_opp_39(self):
        lead = _make_lead(digital_maturity_score=70.0, opportunity_score=39.0)
        result = asyncio.run(categorize_lead(lead))
        self.assertEqual(result, LeadCategory.COLD)


class TestGetCategoryFlags(unittest.TestCase):

    def test_hot_flags(self):
        flags = get_category_flags(LeadCategory.HOT)
        self.assertEqual(len(flags), 4)
        self.assertIn("High opportunity", flags)
        self.assertIn("Low digital maturity", flags)
        self.assertIn("Active business", flags)
        self.assertIn("Ready to buy", flags)

    def test_warm_flags(self):
        flags = get_category_flags(LeadCategory.WARM)
        self.assertEqual(len(flags), 3)
        self.assertIn("Moderate opportunity", flags)
        self.assertIn("Some digital presence", flags)
        self.assertIn("Nurture required", flags)

    def test_cold_flags(self):
        flags = get_category_flags(LeadCategory.COLD)
        self.assertEqual(len(flags), 3)
        self.assertIn("Low priority", flags)
        self.assertIn("Limited data", flags)
        self.assertIn("Revisit later", flags)

    def test_flags_return_list(self):
        for category in LeadCategory:
            flags = get_category_flags(category)
            self.assertIsInstance(flags, list)
            self.assertTrue(len(flags) > 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
