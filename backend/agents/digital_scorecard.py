"""
Digital Presence Scorecard — Viral lead generation engine.

Generates beautiful, shareable "Digital Health Scorecards" for businesses.
Each scorecard grades a business across 8 digital dimensions (A-F format like
classic school report cards), making them highly shareable on social media.

When a business owner sees their scorecard, they either:
  A) Share it proudly → their competitors see it → they want one too (viral)
  B) Get embarrassed by a low grade → reach out to fix it (lead conversion)

Mechanism: Grade inflation hook. Everyone who gets an A shares it.
Everyone who gets an F wants to fix it. Both outcomes generate leads.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from agents.groq_client import llm_json, system_msg, user_msg

logger = logging.getLogger(__name__)

SCORE_LABELS = {
    90: "A+", 80: "A", 70: "B+", 60: "B", 50: "C+",
    40: "C", 30: "D+", 20: "D", 10: "F", 0: "F",
}

CATEGORIES = [
    ("Website", "has_website", 20),
    ("Mobile Ready", "mobile_responsive", 15),
    ("SSL Security", "ssl_present", 10),
    ("Lead Capture", "has_lead_form", 15),
    ("Booking System", "has_booking", 10),
    ("Analytics", "has_analytics", 10),
    ("WhatsApp", "has_whatsapp", 10),
    ("Social Proof", "has_crm", 10),
]

VIRAL_SOCIAL_POST_PROMPT = """You are a social media copywriter. Create a Twitter/LinkedIn post for a business owner sharing their Digital Presence Scorecard.

Business: {business_name}
Industry: {industry}
Overall Grade: {grade}
Score: {score}/100

The post should:
- Be proud and shareable (if grade is good) OR self-aware and funny (if grade is bad)
- Include the grade as a headline
- Tag @getparakram or mention "Parakram"
- Be max 280 chars (Twitter-style)
- Use emojis naturally

Respond with JSON:
{{
  "post": "the social media post text",
  "hashtags": ["tag1", "tag2", "tag3"],
  "hook": "the hook line"
}}"""


def grade_for_score(score: int) -> str:
    for threshold, label in sorted(SCORE_LABELS.items(), reverse=True):
        if score >= threshold:
            return label
    return "F"


def compute_scorecard(lead: dict) -> dict:
    categories = []
    total = 0

    for name, key, weight in CATEGORIES:
        val = lead.get(key, False)
        if isinstance(val, str):
            val = val.lower() in ("true", "yes", "1")
        score = 100 if val else 0
        weighted = score * weight // 100
        total += weighted
        categories.append({
            "name": name,
            "present": val,
            "score": score,
            "weight": weight,
            "grade": grade_for_score(score),
        })

    overall_score = total
    overall_grade = grade_for_score(overall_score)

    return {
        "overall_score": overall_score,
        "overall_grade": overall_grade,
        "categories": categories,
        "generated_at": datetime.utcnow().isoformat(),
    }


def generate_share_card_html(scorecard: dict, business_name: str) -> str:
    """Generate a visually stunning share card as HTML/CSS."""
    grade = scorecard["overall_grade"]
    score = scorecard["overall_score"]
    color = "#22c55e" if score >= 70 else "#eab308" if score >= 40 else "#ef4444"
    emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"

    cats_html = "".join(
        f"""<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.06);font-size:13px;">
          <span style="color:#a0a0a0;">{c['name']}</span>
          <span style="color:{'#22c55e' if c['present'] else '#ef4444'};font-weight:600;">{c['grade']}</span>
        </div>"""
        for c in scorecard["categories"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{business_name} — Digital Scorecard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;600;700&family=Sora:wght@600;700&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#070707; display:flex; justify-content:center; align-items:center; min-height:100vh; font-family:'Instrument Sans',sans-serif; }}
  .card {{ background:#0a0a0a; border:1px solid rgba(201,169,110,0.2); border-radius:8px; padding:32px; max-width:420px; width:100%; position:relative; overflow:hidden; }}
  .card::before {{ content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%; background:radial-gradient(circle at 50% 50%,rgba(201,169,110,0.03),transparent 60%); pointer-events:none; }}
  .header {{ display:flex; align-items:center; gap:12px; margin-bottom:24px; }}
  .logo {{ width:28px; height:28px; }}
  .brand {{ font-size:10px; letter-spacing:0.15em; color:#c9a96e; text-transform:uppercase; font-weight:600; }}
  .grade-circle {{ width:80px; height:80px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 16px; font-size:32px; font-weight:700; font-family:'Sora',sans-serif; border:3px solid {color}; color:{color}; background:rgba({','.join(str(int(color[i:i+2],16)) for i in (1,3,5))},0.08); }}
  .biz-name {{ text-align:center; font-size:18px; font-weight:600; color:#e8e6e3; margin-bottom:4px; font-family:'Sora',sans-serif; }}
  .score-text {{ text-align:center; font-size:13px; color:#5a5a5a; margin-bottom:24px; }}
  .cats {{ margin-bottom:24px; }}
  .footer {{ text-align:center; font-size:10px; color:#3a3a3a; border-top:1px solid rgba(255,255,255,0.06); padding-top:16px; }}
  .cta {{ display:inline-block; margin-top:12px; padding:8px 20px; background:linear-gradient(135deg,#c9a96e,#a88740); color:#070707; text-decoration:none; font-weight:600; font-size:11px; border-radius:4px; }}
</style>
</head>
<body>
<div class="card">
  <div class="header"><img class="logo" src="https://getparakram.in/parakram_logo.png" alt="P"/><span class="brand">Digital Scorecard</span></div>
  <div class="grade-circle">{grade}</div>
  <div class="biz-name">{business_name}</div>
  <div class="score-text">{emoji} Digital Health: {score}/100 — {grade}</div>
  <div class="cats">{cats_html}</div>
  <div class="footer">
    <div style="margin-bottom:8px;">Generated by Parakram — getparakram.in</div>
    <a class="cta" href="https://getparakram.in/contact">Get Your Free Scorecard →</a>
  </div>
</div>
</body>
</html>"""


def generate_viral_post(business_name: str, industry: str, grade: str, score: int) -> dict:
    try:
        return llm_json([
            system_msg("You are a viral social media copywriter."),
            user_msg(VIRAL_SOCIAL_POST_PROMPT.format(
                business_name=business_name,
                industry=industry or "local business",
                grade=grade,
                score=score,
            )),
        ])
    except Exception as e:
        logger.error(f"Viral post generation failed: {e}")
        return {
            "post": f"My business got a {grade} on the Digital Scorecard! How does yours stack up? 🏆 Check yours at getparakram.in",
            "hashtags": ["DigitalScorecard", "Parakram"],
            "hook": f"My business scored {grade}!",
        }


async def process_lead_scorecard(lead_data: dict) -> dict:
    business_name = lead_data.get("business_name", "Your Business")
    industry = lead_data.get("industry", "")
    scorecard = compute_scorecard(lead_data)
    og = generate_share_card_html(scorecard, business_name)
    viral = generate_viral_post(business_name, industry, scorecard["overall_grade"], scorecard["overall_score"])

    return {
        "scorecard": scorecard,
        "og_image_html": og,
        "viral_post": viral,
        "share_url": None,
    }
