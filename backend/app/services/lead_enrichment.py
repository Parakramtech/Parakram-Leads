"""Lead enrichment service for gathering additional data about leads."""

import re
from datetime import datetime, timezone
from typing import Optional
from app.models.lead import Lead

SOCIAL_PLATFORMS = {
    "facebook": r"facebook",
    "instagram": r"instagram", 
    "twitter": r"twitter|x\.com",
    "linkedin": r"linkedin",
    "youtube": r"youtube",
    "google_business": r"google.*business|google.*maps",
    "justdial": r"justdial",
    "indiamart": r"indiamart",
}

TECH_INDICATORS = {
    "analytics": r"gtag|analytics|ga\.js|gtag\.js",
    "crm": r"salesforce|hubspot|zoho|pipedrive",
    "booking_system": r"calendly|acuity|squareappointments|bookitlive",
    "payment_gateway": r"stripe|paypal|razorpay|paytm",
    "live_chat": r"tawk|livechat|intercom|zendesk|freshchat",
    "review_widget": r"yotpo|judgeme|loox|stamped",
}

REVIEW_PLATFORMS = [
    "google", "justdial", "indiamart", "yellow_pages", "facebook",
    "youtube", "sulekha", "urbanpro", "practo", "zomato", "swiggy",
]


async def enrich_lead(lead: Lead) -> dict:
    """
    Enrich a lead with data from multiple sources in parallel.
    Returns enriched data that can be merged into the lead record.
    """
    enrichment = {
        "social_profiles": {},
        "tech_stack": [],
        "review_summary": {},
        "business_details": {},
        "enrichment_quality": 0,
        "sources_checked": [],
        "enriched_at": datetime.now(timezone.utc).isoformat(),
    }

    # Source 1: Extract social profiles from business name + location
    if lead.business_name and lead.location:
        for platform in SOCIAL_PLATFORMS:
            url = _guess_social_url(lead.business_name, lead.location, platform)
            if url:
                enrichment["social_profiles"][platform] = url
                enrichment["sources_checked"].append(f"social_{platform}")

    # Source 2: Detect technology stack from website
    if getattr(lead, 'website_domain', None):
        website_url = f"https://{lead.website_domain}"
        tech_stack = await _detect_tech_stack(website_url)
        enrichment["tech_stack"] = tech_stack
        if tech_stack:
            enrichment["sources_checked"].append("tech_detection")

    # Source 3: Analyze review presence and sentiment
    if lead.review_count is not None or lead.rating is not None:
        enrichment["review_summary"] = {
            "review_count": lead.review_count or 0,
            "average_rating": lead.rating or 0.0,
            "review_trend": "stable"  # simplified - would need historical data
        }
        enrichment["sources_checked"].append("review_analysis")

    # Source 4: Estimate business details
    enrichment["business_details"] = _estimate_business_details(lead)
    if enrichment["business_details"]:
        enrichment["sources_checked"].append("business_estimation")

    # Source 5: Identify likely competitors
    enrichment["competitors"] = _identify_competitors(lead)
    if enrichment["competitors"]:
        enrichment["sources_checked"].append("competitor_analysis")

    # Calculate enrichment quality score (0-100)
    total_signals = (
        len(enrichment["social_profiles"]) * 15 +
        len(enrichment["tech_stack"]) * 10 +
        len(enrichment["review_summary"]) * 10 +
        len(enrichment["business_details"]) * 5 +
        len(enrichment.get("competitors", [])) * 5
    )
    enrichment["enrichment_quality"] = min(total_signals, 100)

    return enrichment


def _guess_social_url(business_name: str, location: str, platform: str) -> Optional[str]:
    """Guess the likely social media URL for a business."""
    if not business_name:
        return None
        
    name_slug = business_name.lower().strip()
    name_slug = re.sub(r'[^a-z0-9]', '', name_slug)
    if len(name_slug) < 3:
        return None

    # Clean location for URL
    loc_part = ""
    if location:
        loc_clean = location.lower().split(",")[0].strip()
        loc_clean = re.sub(r'[^a-z0-9]', '', loc_clean)
        if loc_clean:
            loc_part = f"-{loc_clean}"

    base_urls = {
        "facebook": f"https://facebook.com/{name_slug}{loc_part}",
        "instagram": f"https://instagram.com/{name_slug}{loc_part}",
        "twitter": f"https://twitter.com/{name_slug}{loc_part}",
        "linkedin": f"https://linkedin.com/company/{name_slug}{loc_part}",
        "youtube": f"https://youtube.com/@{name_slug}{loc_part}",
        "google_business": f"https://maps.google.com/?q={business_name.replace(' ', '+')}+{location.replace(' ', '+') if location else ''}",
        "justdial": f"https://justdial.com/{location.replace(' ', '-') if location else ''}/{name_slug}",
        "indiamart": f"https://indiamart.com/{name_slug}",
    }
    return base_urls.get(platform)


async def _detect_tech_stack(website_url: str) -> list[str]:
    """Detect technologies used on a website from its URL."""
    import httpx
    if not website_url:
        return []
    tech_found = []
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            # Ensure URL has protocol
            url_to_check = website_url if website_url.startswith(('http://', 'https://')) else f"https://{website_url}"
            resp = await client.get(url_to_check)
            html = resp.text.lower() if resp.status_code == 200 else ""
            body = resp.text if resp.status_code == 200 else ""

        for tech, pattern in TECH_INDICATORS.items():
            if re.search(pattern, html, re.IGNORECASE):
                tech_found.append(tech)

    except Exception:
        pass  # Silently continue if website unreachable
    return tech_found


def _estimate_business_details(lead: Lead) -> dict:
    """Estimate additional business details."""
    details = {}
    industry = (lead.industry or "").lower()

    # Employee count estimation
    if lead.business_size_estimate:
        size_map = {
            "small": {"employees": "1-10", "revenue_range": "$50K-$500K"},
            "medium": {"employees": "11-50", "revenue_range": "$500K-$5M"},
            "large": {"employees": "51-200", "revenue_range": "$5M-$50M"},
            "enterprise": {"employees": "200+", "revenue_range": "$50M+"},
        }
        size = lead.business_size_estimate.lower()
        if size in size_map:
            details.update(size_map[size])

    # Location and market
    if lead.location:
        details["service_area"] = lead.location
        if "india" in lead.location.lower():
            details["market"] = "Indian SMB"
        else:
            details["market"] = "Global"

    # Weekly customer volume estimation
    if lead.review_count is not None:
        if lead.review_count > 50:
            details["estimated_weekly_customers"] = "100+"
        elif lead.review_count > 20:
            details["estimated_weekly_customers"] = "30-100"
        elif lead.review_count > 5:
            details["estimated_weekly_customers"] = "10-30"
        else:
            details["estimated_weekly_customers"] = "0-10"

    # Years in business estimation (rudimentary)
    if hasattr(lead, 'years_in_business') and lead.years_in_business:
        details["estimated_years_in_business"] = min(lead.years_in_business, 50)
    elif lead.gbp_complete:
        # If they have a complete GBP, they've been around at least 6 months
        details["estimated_years_in_business"] = 1
    else:
        # Default assumption for unknown businesses
        details["estimated_years_in_business"] = 1

    return details


def _identify_competitors(lead: Lead) -> list[dict]:
    """Identify likely competitors based on industry and location."""
    competitors = []
    if not lead.industry or not lead.location:
        return competitors

    # In production, this would query a competitor database
    # For now, return likely competitor types
    industry = lead.industry.lower()
    location = lead.location.split(",")[0].strip() if lead.location else ""

    competitor_types = {
        "restaurant": ["Zomato-listed restaurants", "Swiggy partners", "Cloud kitchens"],
        "cafe": ["Starbucks", "local cafes", "Dabba services"],
        "fitness": ["Cult.fit", "local gyms", "Yoga studios"],
        "education": ["Byju's", "Unacademy", "local coaching centers"],
        "healthcare": ["Practo", "1mg", "local clinics", "Apollo"],
        "legal": ["Local law firms", "LegalRaasta", "VakilSearch"],
        "real estate": ["MagicBricks", "99acres", "Housing.com", "local agents"],
        "retail": ["Amazon sellers", "Flipkart", "local shops", "D2C brands"],
        "manufacturing": ["IndiaMART suppliers", "TradeIndia", "local manufacturers"],
        "photography": ["Local photographers", "Instagram photographers", "Snapixel"],
    }

    for key, comp_list in competitor_types.items():
        if key in industry or industry in key:
            candidates = [{"name": c, "type": "direct", "risk_level": "high" if i < 2 else "medium"}
                          for i, c in enumerate(comp_list[:4])]
            # Sort by name for consistent ordering
            candidates.sort(key=lambda x: x["name"])
            return candidates[:4]

    return []