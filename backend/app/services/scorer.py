from app.models.lead import Lead
from app.services.collector import analyze_website_async
from app.services.predictive_scorer import compute_predictive_score


DIGITAL_MATURITY_WEIGHTS = {
    "website_exists": 20,
    "website_quality_score": 15,
    "mobile_responsive": 10,
    "ssl_present": 5,
    "gbp_complete": 10,
    "social_media_active": 10,
    "has_booking_system": 8,
    "has_lead_form": 8,
    "has_crm_indicators": 5,
    "has_analytics": 3,
    "has_whatsapp": 3,
    "email_domain_quality": 3,
}


OPPORTUNITY_WEIGHTS = {
    "no_website": 30,
    "low_quality_website": 20,
    "no_booking": 10,
    "no_lead_form": 10,
    "no_social_media": 10,
    "no_analytics": 5,
    "low_reviews": 5,
    "no_whatsapp": 5,
    "no_ssl": 5,
}


async def calculate_digital_maturity(lead: Lead) -> float:
    score = 0.0
    if lead.website_exists:
        score += DIGITAL_MATURITY_WEIGHTS["website_exists"]
    score += (lead.website_quality_score / 100) * DIGITAL_MATURITY_WEIGHTS["website_quality_score"]
    if lead.mobile_responsive:
        score += DIGITAL_MATURITY_WEIGHTS["mobile_responsive"]
    if lead.ssl_present:
        score += DIGITAL_MATURITY_WEIGHTS["ssl_present"]
    if lead.gbp_complete:
        score += DIGITAL_MATURITY_WEIGHTS["gbp_complete"]
    if lead.social_media_active:
        score += DIGITAL_MATURITY_WEIGHTS["social_media_active"]
    if lead.has_booking_system:
        score += DIGITAL_MATURITY_WEIGHTS["has_booking_system"]
    if lead.has_lead_form:
        score += DIGITAL_MATURITY_WEIGHTS["has_lead_form"]
    if lead.has_crm_indicators:
        score += DIGITAL_MATURITY_WEIGHTS["has_crm_indicators"]
    if lead.has_analytics:
        score += DIGITAL_MATURITY_WEIGHTS["has_analytics"]
    if lead.has_whatsapp:
        score += DIGITAL_MATURITY_WEIGHTS["has_whatsapp"]
    score += lead.email_domain_quality * DIGITAL_MATURITY_WEIGHTS["email_domain_quality"]
    return min(score, 100.0)


async def calculate_opportunity_score(lead: Lead) -> float:
    score = 0.0
    if not lead.website_exists:
        score += OPPORTUNITY_WEIGHTS["no_website"]
    elif lead.website_quality_score < 40:
        score += OPPORTUNITY_WEIGHTS["low_quality_website"]
    if not lead.has_booking_system:
        score += OPPORTUNITY_WEIGHTS["no_booking"]
    if not lead.has_lead_form:
        score += OPPORTUNITY_WEIGHTS["no_lead_form"]
    if not lead.social_media_active:
        score += OPPORTUNITY_WEIGHTS["no_social_media"]
    if not lead.has_analytics:
        score += OPPORTUNITY_WEIGHTS["no_analytics"]
    if lead.review_count < 10:
        score += OPPORTUNITY_WEIGHTS["low_reviews"]
    if not lead.has_whatsapp:
        score += OPPORTUNITY_WEIGHTS["no_whatsapp"]
    if not lead.ssl_present:
        score += OPPORTUNITY_WEIGHTS["no_ssl"]

    if lead.rating > 4.0:
        score *= 1.2
    if lead.review_count > 50:
        score *= 1.15
    if lead.business_size_estimate and lead.business_size_estimate.lower() in ("medium", "large"):
        score *= 1.1

    return min(score, 100.0)


async def compute_scores(lead: Lead) -> tuple[float, float]:
    if lead.website_url:
        ws = await analyze_website_async(lead.website_url)
        lead.website_exists = ws.get("website_exists", False)
        lead.website_quality_score = ws.get("website_quality_score", 0.0)
        lead.mobile_responsive = ws.get("mobile_responsive", False)
        lead.ssl_present = ws.get("ssl_present", False)
        lead.has_booking_system = ws.get("has_booking_system", False)
        lead.has_lead_form = ws.get("has_lead_form", False)
        lead.has_analytics = ws.get("has_analytics", False)
        lead.has_whatsapp = ws.get("has_whatsapp", False)

    dm = await calculate_digital_maturity(lead)
    opp = await calculate_opportunity_score(lead)
    pred = await compute_predictive_score(lead)
    lead.opportunity_score = round(opp, 2)
    lead.digital_maturity_score = round(dm, 2)
    lead.predictive_quality_score = pred.get("overall_quality", 0)
    lead.conversion_probability = pred.get("conversion_probability", 0)
    lead.buying_urgency = pred.get("urgency", 0)
    lead.optimal_channel = pred.get("optimal_channel")
    lead.recommended_sequence_length = pred.get("recommended_sequence_length", 3)
    from datetime import datetime, timezone
    lead.last_intelligence_update = datetime.now(timezone.utc)
    return round(dm, 2), round(opp, 2)
