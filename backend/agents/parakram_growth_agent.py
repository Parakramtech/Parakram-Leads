"""
Parakram Growth Agent — Autonomous customer acquisition for Parakram itself.

This agent dogfoods the Parakram Leads platform to find businesses that
need Parakram's digital services (websites, apps, AI, IoT, etc.).

Uses Groq (free LLM) instead of GPT-4o to keep costs at zero while
generating personalized analysis, scoring, and outreach at scale.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from agents.groq_client import llm, llm_json, system_msg, user_msg

logger = logging.getLogger(__name__)

LEADS_API = os.getenv("PARAKRAM_LEADS_API", "https://leads.getparakram.in/api/v1")
AUTH_TOKEN = os.getenv("PARAKRAM_AUTH_TOKEN", "")

SERVICES = [
    "Custom Websites",
    "Portfolio Sites",
    "Cross-Platform Mobile Apps",
    "AI Agents & Workflows",
    "IoT & Hardware Integration",
    "Research Automation Tools",
    "ERP / Billing / POS Systems",
    "Real Estate Platforms",
    "Attendance & HR Systems",
]

TARGET_INDUSTRIES = [
    "real estate", "healthcare", "education", "restaurant", "retail",
    "salon", "fitness", "automotive", "legal", "accounting",
    "construction", "logistics", "manufacturing", "hotel", "pharmacy",
]

SELF_ANALYSIS_PROMPT = """You are Parakram's internal AI analyst. Your job is to analyze a potential client and determine if they are a good fit for Parakram's services.

Business: {business_name}
Industry: {industry}
Location: {location}
Rating: {rating}/5
Reviews: {review_count}
Website: {website}

Digital Indicators:
- Has Website: {has_website}
- Has SSL: {has_ssl}
- Mobile Friendly: {has_mobile}
- Has Booking System: {has_booking}
- Has Lead Form: {has_lead_form}
- Has CRM: {has_crm}
- Has Analytics: {has_analytics}
- WhatsApp Active: {has_whatsapp}

Respond with JSON:
{{
  "analysis": "2-3 sentence analysis of their digital gap",
  "parakram_fit_score": 0-100,
  "recommended_services": ["service1", "service2"],
  "estimated_value_inr": numeric,
  "pain_points": ["pain1", "pain2"],
  "viral_hook": "one-liner hook for outreach that references their industry",
  "outreach_angle": "consultative|educational|direct|value_proposition"
}}"""

OUTREACH_SELF_PROMPT = """You are Parakram's lead generator. Draft a personalized outreach message for a prospect.

Business: {business_name}
Owner: {owner_name}
Industry: {industry}
Location: {location}
Key Gaps: {gaps}
Recommended Service: {service}
Pain Points: {pain_points}

Create 3 messages in JSON:
{{
  "whatsapp": "Short WhatsApp message (max 3 sentences, casual, references their business)",
  "email": {{"subject": "Email subject line", "body": "Email body (max 5 sentences)"}},
  "linkedin": "LinkedIn message (max 3 sentences, professional)"
}}

Rules:
- Sound 100% human, never automated
- Reference their actual business and location
- Be concise and value-focused
- Include a low-friction CTA ("Shall I share a quick audit?" / "Free 2-min website check")
- Never mention scores, metrics, or automated analysis
- Talk about helping them get more customers
"""


async def api_get(path: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{LEADS_API}{path}",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
        )
        resp.raise_for_status()
        return resp.json()


async def api_post(path: str, data: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{LEADS_API}{path}",
            json=data or {},
            headers={"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()


async def discover_leads(location: str = "Bangalore", max_pages: int = 3) -> list[dict]:
    results = []
    for industry in TARGET_INDUSTRIES[:5]:
        try:
            logger.info(f"Scraping {industry} in {location}...")
            data = await api_post("/scraper/single/", {
                "category": industry,
                "location": location,
                "pages": max_pages,
                "use_maps": True,
                "use_justdial": True,
                "use_ddg": True,
            })
            if isinstance(data, dict) and "leads" in data:
                results.extend(data["leads"])
            elif isinstance(data, list):
                results.extend(data)
        except Exception as e:
            logger.warning(f"Scrape failed for {industry}: {e}")
        await asyncio.sleep(2)
    return results


async def analyze_lead(business: dict) -> Optional[dict]:
    try:
        result = llm_json([
            system_msg("You are a precise business analyst. Return only valid JSON."),
            user_msg(SELF_ANALYSIS_PROMPT.format(
                business_name=business.get("business_name", "Unknown"),
                industry=business.get("industry", "Unknown"),
                location=business.get("location", "Unknown"),
                rating=business.get("rating", 0),
                review_count=business.get("review_count", 0),
                website=business.get("website_url", "None"),
                has_website=str(business.get("website_url") not in (None, "", "None")),
                has_ssl=str(business.get("ssl_present", False)),
                has_mobile=str(business.get("mobile_responsive", False)),
                has_booking=str(business.get("has_booking", False)),
                has_lead_form=str(business.get("has_lead_form", False)),
                has_crm=str(business.get("has_crm", False)),
                has_analytics=str(business.get("has_analytics", False)),
                has_whatsapp=str(business.get("has_whatsapp", False)),
            )),
        ])
        result["business_name"] = business.get("business_name")
        result["phone"] = business.get("phone")
        return result
    except Exception as e:
        logger.error(f"Analysis failed for {business.get('business_name')}: {e}")
        return None


async def generate_outreach(lead_data: dict, analysis: dict) -> Optional[dict]:
    try:
        gaps = ", ".join(analysis.get("pain_points", [])) or "Digital presence gaps"
        service = analysis.get("recommended_services", [Services.SERVICES[0]])[0]

        messages = llm_json([
            system_msg("You are a professional sales copywriter. Return valid JSON."),
            user_msg(OUTREACH_SELF_PROMPT.format(
                business_name=lead_data.get("business_name", "there"),
                owner_name=lead_data.get("owner_name", "there"),
                industry=lead_data.get("industry", "your industry"),
                location=lead_data.get("location", ""),
                gaps=gaps,
                service=service,
                pain_points=", ".join(analysis.get("pain_points", [])),
            )),
        ])
        return messages
    except Exception as e:
        logger.error(f"Outreach generation failed: {e}")
        return None


async def create_lead_in_platform(business: dict, analysis: dict, outreach: dict) -> Optional[str]:
    try:
        score = analysis.get("parakram_fit_score", 50)
        category_flag = "HOT" if score >= 70 else "WARM" if score >= 40 else "COLD"

        payload = {
            "business_name": business.get("business_name"),
            "owner_name": business.get("owner_name"),
            "industry": business.get("industry"),
            "phone": business.get("phone"),
            "website_url": business.get("website_url"),
            "location": business.get("location"),
            "rating": business.get("rating"),
            "review_count": business.get("review_count"),
            "source": "Parakram Growth Agent",
            "category_flag": category_flag,
            "status": "ANALYZED",
            "ai_analysis": {
                "analysis": analysis.get("analysis"),
                "pain_points": analysis.get("pain_points"),
                "recommended_services": analysis.get("recommended_services"),
                "estimated_value_inr": analysis.get("estimated_value_inr"),
            },
            "digital_maturity_score": max(0, 100 - score),
            "opportunity_score": score,
            "outreach_message_whatsapp": outreach.get("whatsapp", ""),
            "outreach_message_email": outreach.get("email", {}).get("body", ""),
            "outreach_message_linkedin": outreach.get("linkedin", ""),
        }

        result = await api_post("/leads", payload)
        return result.get("id")
    except Exception as e:
        logger.error(f"Failed to create lead: {e}")
        return None


async def run_acquisition_cycle(location: str = "Bangalore", max_leads: int = 50):
    logger.info(f"=== Parakram Growth Agent: Starting acquisition cycle in {location} ===")

    discovered = await discover_leads(location)
    logger.info(f"Discovered {len(discovered)} leads")

    created = 0
    for business in discovered[:max_leads]:
        analysis = await analyze_lead(business)
        if not analysis or analysis.get("parakram_fit_score", 0) < 30:
            continue

        outreach = await generate_outreach(business, analysis)
        if not outreach:
            continue

        lead_id = await create_lead_in_platform(business, analysis, outreach)
        if lead_id:
            created += 1
            logger.info(f"Created lead #{created}: {business.get('business_name')} (score: {analysis.get('parakram_fit_score')})")

        await asyncio.sleep(3)

    logger.info(f"=== Cycle complete: {created} leads created ===")
    return {"discovered": len(discovered), "created": created}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_acquisition_cycle())
