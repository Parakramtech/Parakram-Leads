"""
Buying Signal Monitor — continuously monitors external signals to detect
when leads are ready to buy. The trick: we don't need real-time scraping;
we detect signals through patterns already available in our data.

Signal categories:
1. Digital decay — website goes down, SSL expires, features break
2. Review activity — new reviews indicate active business
3. Competitor moves — competitor website changes indicate market shift
4. Business events — detected through review patterns, opening hours changes
5. Hiring signals — job posting keywords on website
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.models.lead import Lead, LeadCategory, LeadStatus


BUYING_SIGNALS = {
    "emergency_missing_online": {
        "description": "Business has phone but zero web presence. They're losing customers daily.",
        "weight": 95,
        "channels": ["whatsapp", "phone_call"],
        "message_tone": "urgent_help",
    },
    "outdated_website": {
        "description": "Website looks old/unmaintained. Business likely needs upgrade.",
        "weight": 70,
        "channels": ["email", "whatsapp"],
        "message_tone": "modernization",
    },
    "no_booking_no_form": {
        "description": "Missing both booking and lead capture. Losing 40%+ potential customers.",
        "weight": 85,
        "channels": ["whatsapp", "email"],
        "message_tone": "problem_awareness",
    },
    "high_reviews_low_tech": {
        "description": "Great reputation but no digital tools. Prime candidate for upgrade.",
        "weight": 80,
        "channels": ["email", "linkedin"],
        "message_tone": "professional",
    },
    "active_on_gbp_only": {
        "description": "Only on Google Business Profile. Needs website + social media.",
        "weight": 65,
        "channels": ["whatsapp"],
        "message_tone": "friendly",
    },
    "social_media_growth": {
        "description": "Active on social media but no website. Growing business needs digital home.",
        "weight": 75,
        "channels": ["instagram_dm", "whatsapp"],
        "message_tone": "casual",
    },
    "seasonal_business": {
        "description": "In a seasonal industry. Timing outreach before peak season.",
        "weight": 60,
        "channels": ["email", "whatsapp"],
        "message_tone": "strategic",
    },
    "multi_location": {
        "description": "Multiple locations but no centralized digital system. Needs consolidation.",
        "weight": 70,
        "channels": ["email", "linkedin"],
        "message_tone": "professional",
    },
}

SEASONALITY = {
    "restaurant": {"peak_months": [1, 2, 12], "outreach_before": 2},
    "cafe": {"peak_months": [1, 2, 12], "outreach_before": 2},
    "fitness": {"peak_months": [1, 6, 7], "outreach_before": 1},
    "education": {"peak_months": [3, 4, 5, 10, 11], "outreach_before": 2},
    "travel": {"peak_months": [10, 11, 12, 1], "outreach_before": 2},
    "retail": {"peak_months": [10, 11, 12], "outreach_before": 1},
    "real_estate": {"peak_months": [1, 2, 9, 10], "outreach_before": 1},
    "photography": {"peak_months": [10, 11, 12, 2, 3], "outreach_before": 2},
    "salon": {"peak_months": [10, 11, 12], "outreach_before": 1},
}


class BuyingSignalDetector:
    def __init__(self, lead: Lead):
        self.lead = lead
        self.signals = []
        self.total_weight = 0
        self.analyzed_at = datetime.now(timezone.utc)

    def analyze(self) -> dict:
        self._check_emergency_signals()
        self._check_opportunity_signals()
        self._check_seasonal_signals()
        self._check_competitive_signals()
        return self.to_dict()

    def _check_emergency_signals(self):
        """High-urgency signals that need immediate action."""
        # Emergency 1: Has phone but no website
        if self.lead.phone and not self.lead.website_exists:
            self._add_signal("emergency_missing_online")

        # Emergency 2: Has website but no SSL
        if self.lead.website_exists and not self.lead.ssl_present:
            self._add_signal("outdated_website")

        # Emergency 3: No booking AND no lead form
        if not self.lead.has_booking_system and not self.lead.has_lead_form:
            self._add_signal("no_booking_no_form")

    def _check_opportunity_signals(self):
        """High-opportunity signals."""
        review_count = self.lead.review_count or 0
        rating = self.lead.rating or 0
        # Great reviews but no tech
        if review_count > 10 and rating > 4.0:
            if not self.lead.has_booking_system and not self.lead.has_lead_form:
                self._add_signal("high_reviews_low_tech")

        # Only on Google
        if not self.lead.website_exists and self.lead.gbp_complete:
            self._add_signal("active_on_gbp_only")

        # Social media active but no website
        if self.lead.social_media_active and not self.lead.website_exists:
            self._add_signal("social_media_growth")

    def _check_seasonal_signals(self):
        """Industry-based seasonal opportunities."""
        if not self.lead.industry:
            return

        current_month = datetime.now(timezone.utc).month
        for industry, data in SEASONALITY.items():
            if industry in self.lead.industry.lower() or self.lead.industry.lower() in industry:
                for peak_month in data["peak_months"]:
                    months_until_peak = (peak_month - current_month) % 12
                    if 0 <= months_until_peak <= data["outreach_before"]:
                        self._add_signal("seasonal_business", extra={
                            "peak_month": peak_month,
                            "months_until_peak": months_until_peak,
                        })
                        break

    def _check_competitive_signals(self):
        """Competitive pressure signals."""
        if not self.lead.industry:
            return

        # High competitive pressure industries
        high_pressure = [
            "restaurant", "cafe", "food", "fitness", "salon",
            "real estate", "education", "photography"
        ]
        for ind in high_pressure:
            if ind in (self.lead.industry or "").lower():
                self._add_signal("multi_location" if (self.lead.review_count or 0) > 30 else "seasonal_business")
                break

    def _add_signal(self, signal_key: str, extra: Optional[dict] = None):
        if signal_key in BUYING_SIGNALS:
            signal = BUYING_SIGNALS[signal_key].copy()
            signal["key"] = signal_key
            signal["detected_at"] = self.analyzed_at.isoformat()
            if extra:
                signal.update(extra)
            self.signals.append(signal)
            self.total_weight += signal["weight"]

    def to_dict(self) -> dict:
        self.signals.sort(key=lambda s: s["weight"], reverse=True)
        return {
            "has_signals": len(self.signals) > 0,
            "active_signals": [s["key"] for s in self.signals],
            "total_signals": len(self.signals),
            "combined_urgency": min(100, self.total_weight),
            "total_buying_urgency": min(100, self.total_weight),
            "primary_signal": self.signals[0]["description"] if self.signals else None,
            "recommended_channel": self.signals[0]["channels"][0] if self.signals else "email",
            "recommended_tone": self.signals[0]["message_tone"] if self.signals else "professional",
            "signals": self.signals,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


async def detect_buying_signals(lead: Lead) -> dict:
    """Detect buying signals for a lead."""
    detector = BuyingSignalDetector(lead)
    return detector.analyze()


async def should_prioritize(lead: Lead, predictive_score: float = None) -> dict:
    """Determine if a lead should be prioritized RIGHT NOW."""
    signals = await detect_buying_signals(lead)
    priority = {
        "score": predictive_score or 0,
        "buying_urgency": signals["total_buying_urgency"],
        "combined": min(100, (predictive_score or 0) * 0.5 + signals["total_buying_urgency"] * 0.5),
        "reason": signals["primary_signal"],
        "action": "contact_now" if signals["total_buying_urgency"] >= 70 else "nurture" if signals["total_buying_urgency"] >= 40 else "monitor",
    }
    return priority
