"""
Response Intelligence Engine — analyzes lead replies for sentiment, intent, and buying signals.

The trick: we don't need GPT for basic analysis. We use deterministic pattern matching
that's faster, cheaper, and works offline. Only escalate to AI for complex replies.
"""

import re
from datetime import datetime, timezone
from typing import Optional


# === SENTIMENT PATTERNS ===
POSITIVE_SIGNALS = [
    r"\b(interested|great|awesome|perfect|yes|sure|ok|okay|let'?s do it|tell me more|show me|demo|call me|book|schedule|available)\b",
    r"\b(how much|pricing|cost|price|package)\b",
    r"\b(when|available|timing|schedule|tomorrow|today|next week)\b",
    r"\b(send|share|email|forward|link|website)\b",
    r"\b(thanks|thank you|appreciate)\b",
    r"👍|✅|🙏|🙂|😊|👌|🔥",
]

NEGATIVE_SIGNALS = [
    r"\b(not interested|no thanks|stop|unsubscribe|don'?t contact|remove|spam)\b",
    r"\b(busy|not now|later|maybe some other time|no time)\b",
    r"\b(already|have one|existing|current provider|already using)\b",
    r"\b(waste|scam|fraud|fake|not good|terrible|bad)\b",
    r"\b(too high|don'?t see.*help|not.*helpful|not.*useful)\b",
    r"😠|😡|👎|🚫|❌",
]

NEUTRAL_SIGNALS = [
    r"\b(maybe|perhaps|possibly|let me think|need to check|discuss with|talk to)\b",
    r"\b(send more info|brochure|details|catalogue|website)\b",
    r"\b(who|what|how|why|which)\b.*\b(you|this|company|service)\b",
]

# === INTENT CLASSIFICATION ===
INTENT_PATTERNS = {
    "meeting_request": [
        r"\b(call|meeting|demo|book|schedule|visit|discuss|talk)\b",
        r"\b(when|available|free|timing|time|day)\b.*\b(tomorrow|today|monday|tuesday|wednesday|thursday|friday)\b",
    ],
    "pricing_inquiry": [
        r"\b(how much|cost|price|pricing|package|plan|subscription|fee|rate|charges)\b",
        r"\b(payment|pay|billing|monthly|annual|subscription)\b",
    ],
    "positive_interest": [
        r"\b(interested|great|awesome|love it|perfect|yes|sure|let'?s do it)\b",
        r"\b(when can we|let'?s schedule|i'?m in|count me in|sign me up)\b",
    ],
    "information_request": [
        r"\b(send|share|email|forward|link|more info|details|brochure|catalogue|website|portfolio|example)\b",
        r"\b(how does it work|how it works|tell me more|explain|what.*offer|what.*do.*for)\b",
    ],
    "objection": [
        r"\b(expensive|too much|too high|budget|can'?t afford|not now|already|existing|happy with)\b",
        r"\b(not interested|no thanks|stop|busy|not for me|don'?t see.*help|not.*useful|waste of time)\b",
    ],
}


class ResponseAnalysis:
    def __init__(self, reply_text: str, lead_name: str = ""):
        self.text = reply_text.lower().strip()
        self.lead_name = lead_name
        self.sentiment_score = 0  # -1 to 1
        self.intent = "unknown"
        self.urgency = 0  # 0-100
        self.should_alert = False
        self.suggested_reply_type = "none"
        self.analyzed_at = datetime.now(timezone.utc)

    def analyze(self) -> dict:
        self._analyze_sentiment()
        self._analyze_intent()
        self._calc_urgency()
        self._suggest_reply_type()
        return self.to_dict()

    def _analyze_sentiment(self):
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for pattern in POSITIVE_SIGNALS:
            if re.search(pattern, self.text, re.IGNORECASE):
                positive_count += 1

        for pattern in NEGATIVE_SIGNALS:
            if re.search(pattern, self.text, re.IGNORECASE):
                negative_count += 1

        for pattern in NEUTRAL_SIGNALS:
            if re.search(pattern, self.text, re.IGNORECASE):
                neutral_count += 1

        total = positive_count + negative_count + neutral_count
        if total == 0:
            self.sentiment_score = 0
        else:
            self.sentiment_score = (positive_count - negative_count) / max(total, 1)
        self.sentiment_score = max(-1.0, min(1.0, self.sentiment_score))

    def _analyze_intent(self):
        scores = {}
        for intent, patterns in INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, self.text, re.IGNORECASE):
                    score += 1
            scores[intent] = score

        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                best_intents = [k for k, v in scores.items() if v == max_score]
                self.intent = best_intents[0]

        # Override for very short replies
        words = self.text.split()
        if len(words) <= 3:
            if any(w in self.text for w in ["yes", "sure", "ok", "okay", "interested", "👍", "✅"]):
                self.intent = "positive_interest"
            elif any(w in self.text for w in ["no", "not", "stop", "unsubscribe"]):
                self.intent = "objection"

        # Default to information_request when no intent detected
        if self.intent == "unknown":
            self.intent = "information_request"

    def _calc_urgency(self):
        """How urgently should we respond? Higher = faster needed."""
        # Empty text gets zero urgency
        if not self.text.strip():
            self.urgency = 0
            self.should_alert = False
            return

        if self.intent == "meeting_request":
            self.urgency = 90
        elif self.intent == "pricing_inquiry":
            self.urgency = 80
        elif self.intent == "positive_interest":
            self.urgency = 85
        elif self.sentiment_score > 0.5:
            self.urgency = 70
        elif self.intent == "information_request":
            self.urgency = 60
        elif self.intent == "objection":
            self.urgency = 50
        else:
            self.urgency = 30

        # Alert if high urgency
        self.should_alert = self.urgency >= 70

    def _suggest_reply_type(self):
        if not self.text.strip():
            self.suggested_reply_type = "follow_up"
            return
        mapping = {
            "meeting_request": "schedule_meeting",
            "pricing_inquiry": "send_pricing",
            "information_request": "send_info",
            "objection": "handle_objection",
            "positive_interest": "schedule_call",
        }
        self.suggested_reply_type = mapping.get(self.intent, "follow_up")

    def sentiment_label(self) -> str:
        if self.sentiment_score > 0.3:
            return "positive"
        elif self.sentiment_score < -0.3:
            return "negative"
        return "neutral"

    def to_dict(self) -> dict:
        return {
            "sentiment_score": round(self.sentiment_score, 2),
            "sentiment_label": self.sentiment_label(),
            "intent": self.intent,
            "urgency": self.urgency,
            "should_alert": self.should_alert,
            "suggested_reply_type": self.suggested_reply_type,
            "analyzed_at": self.analyzed_at.isoformat(),
            "lead_name": self.lead_name,
        }


async def analyze_response(reply_text: str, lead_name: str = "") -> dict:
    """Analyze a lead's reply and return intelligence insights."""
    analyzer = ResponseAnalysis(reply_text, lead_name)
    return analyzer.analyze()


async def should_send_alert(analysis: dict) -> bool:
    """Should we send a real-time alert to the user?"""
    return analysis["urgency"] >= 70 or analysis["intent"] in (
        "meeting_request", "positive_interest"
    )
