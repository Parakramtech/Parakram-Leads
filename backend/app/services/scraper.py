import asyncio
import random
import uuid
import re
import json
import os
import csv
from typing import Optional
from urllib.parse import quote_plus, unquote
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.lead import Lead, LeadStatus, LeadCategory
from app.services.collector import analyze_website_async


JUSTDIAL_CATEGORIES = [
    "Restaurants", "Beauty Parlours", "Salons", "Gyms", "Yoga Centers",
    "Bakers", "Caterers", "Tiffin Services", "Cloud Kitchens",
    "General Physicians", "Dentists", "Skin Clinics", "Eye Hospitals",
    "Diagnostic Centers", "Path Labs", "Medical Stores", "Ayurvedic",
    "Physiotherapists", "Veterinary Hospitals",
    "Architects", "Interior Designers", "Civil Contractors",
    "Painters", "Plumbers", "Electricians", "Carpenters",
    "Pest Control", "Packers Movers", "Security Services",
    "Housekeeping", "Deep Cleaning",
    "CAs", "Tax Consultants", "Company Registration",
    "Lawyers", "Advocates", "Legal Consultants",
    "Property Agents", "Real Estate", "Property Consultants",
    "Builders", "Developers",
    "Photographers", "Event Planners", "DJs", "Wedding Planners",
    "Tent Houses", "Caterers",
    "Tutors", "Coaching Centers", "Computer Training",
    "Dance Classes", "Music Classes",
    "Pizza Outlets", "Juice Centers", "Ice Cream Parlours",
    "Cafes", "Food Trucks",
    "Chemists", "Opticians", "Fitness Centers",
    "BPO", "IT Services", "Digital Marketing",
    "Travel Agents", "Cab Services", "Car Rentals",
    "Laundry", "Dry Cleaners", "Tailors",
    "Boutiques", "Jewelers", "Watch Repairs",
    "Furniture Stores", "Home Decor", "Kitchen Appliances",
    "Hardware Stores", "Paint Stores", "Flooring Dealers",
    "Tiles Dealers", "Bathroom Fittings",
    "Automobile Repair", "Car Wash", "Bike Rentals",
    "Tyre Dealers", "Auto Spares",
    "Courier Services", "Cargo Services", "Logistics",
    "Manpower Consultants", "Placement Agencies",
    "Counsellors", "Psychologists", "Child Care",
    "Old Age Homes", "Orphanages", "NGOs",
    "Banks", "ATMs", "Finance Companies",
    "Insurance Agents", "Stock Brokers", "Mutual Funds",
    "DTP Operators", "Printing Shops", "Xerox Centers",
    "Stationery Shops", "Book Shops", "Libraries",
    "Pet Shops", "Pet Grooming", "Dog Training",
    "Swimming Pools", "Sports Clubs", "Badminton Courts",
    "Golf Courses", "Tennis Courts",
    "Pest Control", "Water Purifiers", "Solar Panels",
    "Security Systems", "CCTV Dealers", "Fire Safety",
    "Cable TV", "Internet Providers", "Broadband Services",
    "Mobile Repairs", "Computer Repairs", "Laptop Repairs",
    "AC Repair", "Refrigerator Repair", "Washing Machine Repair",
    "Microwave Repair", "Water Heater Repair", "Chimney Repair",
]

BANGALORE_LOCATIONS = [
    "Koramangala", "Indiranagar", "Whitefield", "Marathahalli",
    "HSR Layout", "BTM Layout", "Jayanagar", "JP Nagar",
    "Malleshwaram", "Rajajinagar", "Basavanagudi", "Vijayanagar",
    "Yelahanka", "Hebbal", "RT Nagar", "Banashankari",
    "Electronic City", "MG Road", "Brigade Road",
    "Sadashivanagar", "Ulsoor", "Domlur", "HAL",
    "Vasanth Nagar", "Yeshwanthpur", "Peenya",
    "Kengeri", "Nagarabhavi", "Padmanabhanagar",
    "Bannerghatta Road", "Kanakapura Road", "Mysore Road",
    "Sarjapur Road", "Kanakapura", "Anekal",
]


def normalize_phone(raw: str) -> str:
    cleaned = re.sub(r'[\s\-\(\)\+\#\*\.]', '', raw)
    if cleaned.startswith('91') and len(cleaned) >= 12:
        return cleaned
    if cleaned.startswith('0') and len(cleaned) >= 11:
        return '91' + cleaned[1:]
    if len(cleaned) == 10 and cleaned[0] in '6789':
        return '91' + cleaned
    return cleaned


def is_valid_phone(phone: str) -> bool:
    cleaned = re.sub(r'\D', '', phone)
    if cleaned.startswith('91'):
        cleaned = cleaned[2:]
    return len(cleaned) == 10 and cleaned[0] in '6789'


async def scrape_google_maps_browser(
    category: str,
    location: str = "Bangalore",
    max_results: int = 30,
) -> list[dict]:
    from playwright.async_api import async_playwright

    results = []
    seen_phones: set = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu"],
        )
        page = await browser.new_page()

        query = quote_plus(f"{category} in {location}")
        url = f"https://www.google.com/maps/search/{query}/"
        print(f"  Opening Maps: {url}")
        try:
            await page.goto(url, timeout=45000)
        except Exception:
            pass
        await asyncio.sleep(8)

        title = await page.title()
        print(f"    Page title: {title}")

        locator = page.locator('a[href*="maps/place/"]')
        total = await locator.count()
        print(f"    Found {total} listing links")

        for i in range(min(total, max_results)):
            try:
                link = locator.nth(i)
                href = await asyncio.wait_for(link.get_attribute("href"), timeout=5) or ""
                if not href:
                    continue

                card_name = await asyncio.wait_for(link.evaluate("""el => {
                    const c = el.closest('[class*="Nv2PK"], div[jsaction], div > div');
                    const ne = c?.querySelector('[class*="fontHeadline"]') || c?.querySelector('h3');
                    return ne ? ne.innerText.trim() : '';
                }"""), timeout=5)

                await asyncio.wait_for(link.click(force=True), timeout=15)
                await asyncio.sleep(1.5)

                try:
                    await asyncio.wait_for(page.wait_for_load_state("networkidle"), timeout=8)
                except Exception:
                    pass

                name = ""
                try:
                    for sel in ['[class*="DUwDvf"]', "h1.DUwDvf", "h1"]:
                        el = await page.query_selector(sel)
                        if el:
                            name = (await el.inner_text()).strip()
                            skip = ["results", "sign in", "get the most", "updates from", "this area"]
                            if name and len(name) > 2 and not any(s in name.lower() for s in skip):
                                break
                except Exception:
                    pass

                if not name and card_name:
                    name = card_name
                if not name or len(name) < 3:
                    print(f"    [{i+1}] Skipping (bad name)")
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.3)
                    continue

                phone = ""
                try:
                    tel_links = await page.query_selector_all('a[href^="tel:"]')
                    if tel_links:
                        h = await tel_links[0].get_attribute("href") or ""
                        phone = normalize_phone(h.replace("tel:", ""))
                    if not phone:
                        for sel in ['button[data-item-id*="phone"]', 'button[aria-label*="phone"]']:
                            btn = await page.query_selector(sel)
                            if btn:
                                txt = (await btn.inner_text()).strip()
                                for n in re.findall(r"[\d\s\-\(\)\+]{10,}", txt):
                                    c = normalize_phone(n)
                                    if is_valid_phone(c):
                                        phone = c
                                        break
                                if phone:
                                    break
                except Exception:
                    pass

                website = ""
                try:
                    auth = await page.query_selector('a[data-item-id*="authority"]')
                    if auth:
                        h = await auth.get_attribute("href") or ""
                        if "http" in h:
                            website = h
                    if not website:
                        for a in await page.query_selector_all("a"):
                            h = await a.get_attribute("href") or ""
                            if h.startswith("http") and "google.com" not in h and "maps" not in h:
                                website = h
                                break
                except Exception:
                    pass

                address = ""
                try:
                    addr_btn = await page.query_selector('button[data-item-id*="address"]')
                    if addr_btn:
                        address = (await addr_btn.inner_text()).strip()[:200]
                except Exception:
                    pass

                if phone and phone not in seen_phones and is_valid_phone(phone):
                    seen_phones.add(phone)
                    results.append({
                        "business_name": name[:255],
                        "phone": phone,
                        "website": website,
                        "address": address,
                        "category": category,
                        "description": f"{category} in {location}",
                        "source": "google_maps_playwright",
                        "location": location,
                        "has_website": bool(website),
                    })
                    print(f"    [{i+1}] {name[:35]} | Phone: {phone}")
                else:
                    print(f"    [{i+1}] {name[:35]} | No phone")

                await page.keyboard.press("Escape")
                await asyncio.sleep(0.3)

            except asyncio.TimeoutError:
                print(f"    [{i+1}] Timeout")
                try:
                    await page.keyboard.press("Escape")
                except Exception:
                    pass
                continue
            except Exception as e:
                print(f"    [{i+1}] Error: {e}")
                try:
                    await page.keyboard.press("Escape")
                except Exception:
                    pass
                continue

        await browser.close()

    return results


async def scrape_justdial_httpx(
    category: str,
    location: str = "Bangalore",
    max_pages: int = 2,
) -> list[dict]:
    import httpx
    results = []
    seen_phones: set = set()

    location_slug = location.lower().replace(" ", "-")
    cat_slug = category.lower().replace(" ", "-")

    for page in range(max_pages):
        url = f"https://www.justdial.com/{location_slug}/{cat_slug}?page={page + 1}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        }
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200 or len(resp.text) < 100:
                    continue

                phones = re.findall(r"[6-9]\d{9}", resp.text)
                names = re.findall(r'<h2[^>]*class="[^"]*lng_cont_name[^"]*"[^>]*>(.*?)</h2>', resp.text, re.DOTALL)
                if not names:
                    names = re.findall(r'<h2[^>]*>(.*?)</h2>', resp.text)
                if not names:
                    names = re.findall(r'"storeName":"([^"]+)"', resp.text)
                if not names:
                    names = re.findall(r'"businessName":"([^"]+)"', resp.text)

                for name in names:
                    name = BeautifulSoup(name, "html.parser").get_text(strip=True) if name else ""
                    if len(name) < 3:
                        continue
                    for p in phones:
                        cleaned = normalize_phone(p)
                        if cleaned and is_valid_phone(cleaned) and cleaned not in seen_phones:
                            seen_phones.add(cleaned)
                            results.append({
                                "business_name": name[:255],
                                "phone": cleaned,
                                "website": "",
                                "description": category,
                                "address": "",
                                "category": category,
                                "source": "justdial",
                                "location": location,
                                "has_website": False,
                            })
                            break

                print(f"    Page {page+1}: {len(names)} names, {len(phones)} phones, {len(results)} results")
        except Exception as e:
            print(f"    Error: {e}")
            continue

    return results


async def scrape_duckduckgo(
    category: str,
    location: str = "Bangalore",
    max_results: int = 10,
) -> list[dict]:
    """API-based lead sourcing via DuckDuckGo search"""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("  DDGS not installed, skipping")
        return []

    results = []
    seen_phones: set = set()
    query = f"{category} in {location} Bangalore phone"
    print(f"  Searching DDG: {query}")

    await asyncio.sleep(random.uniform(3, 6))
    try:
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=max_results)):
                title = r.get("title", "")
                href = r.get("href", "")
                snippet = r.get("body", "")

                if not title or len(title) < 3:
                    continue

                phones_title = re.findall(r"[6-9]\d{9}", title)
                phones_snippet = re.findall(r"[6-9]\d{9}", snippet)
                all_phones = phones_title + phones_snippet

                for p in all_phones:
                    cleaned = normalize_phone(p)
                    if cleaned and is_valid_phone(cleaned) and cleaned not in seen_phones:
                        seen_phones.add(cleaned)
                        has_website = "http" in href and "justdial" not in href and "sulekha" not in href
                        results.append({
                            "business_name": title[:255],
                            "phone": cleaned,
                            "website": href if has_website else "",
                            "description": snippet[:300],
                            "address": location,
                            "category": category,
                            "source": "duckduckgo",
                            "location": location,
                            "has_website": has_website,
                        })
                        break

            print(f"    DDG: {len(results)} leads")
    except Exception as e:
        print(f"    DDG Error: {e}")

    return results


async def verify_no_website(lead_data: dict) -> dict:
    if lead_data.get("website"):
        known_no_site = [
            "facebook.com", "instagram.com", "twitter.com", "linkedin.com",
            "youtube.com", "justdial.com", "sulekha.com", "indiamart.com",
            "google.com/maps", "maps.google.com",
        ]
        site = lead_data["website"].lower()
        for no_site in known_no_site:
            if no_site in site:
                lead_data["has_website"] = False
                lead_data["website"] = ""
                return lead_data
        try:
            analysis = await analyze_website_async(lead_data["website"])
            lead_data["has_website"] = analysis.get("website_exists", False)
            if not analysis.get("website_exists", False):
                lead_data["website"] = ""
        except Exception:
            lead_data["has_website"] = True
    return lead_data


async def save_leads_to_db(leads: list[dict], db: AsyncSession, organization_id: uuid.UUID) -> int:
    saved = 0
    for ld in leads:
        phone = ld.get("phone", "")
        if not phone:
            continue
        existing = await db.execute(
            select(Lead).where(Lead.phone == phone, Lead.organization_id == organization_id)
        )
        if existing.scalar_one_or_none():
            continue
        try:
            lead = Lead(
                organization_id=organization_id,
                business_name=ld.get("business_name", "Unknown")[:255],
                phone=phone,
                industry=ld.get("category", "General")[:128],
                category=LeadCategory.COLD,
                status=LeadStatus.DISCOVERED,
                location=ld.get("address", ld.get("location", ""))[:255],
                business_description=ld.get("description", "")[:1000],
                source=ld.get("source", "scraper"),
                website_url=ld.get("website", ""),
                website_exists=ld.get("has_website", False),
                social_profiles={},
            )
            db.add(lead)
            saved += 1
        except Exception:
            continue
    if saved > 0:
        await db.flush()
    return saved


async def run_crawl(
    categories: list[str] | None = None,
    locations: list[str] | None = None,
    max_pages: int = 2,
    use_maps: bool = True,
    use_justdial: bool = True,
    use_ddg: bool = True,
    db: AsyncSession | None = None,
    progress_callback: callable = None,
    organization_id: uuid.UUID | None = None,
) -> dict:
    if categories is None:
        categories = JUSTDIAL_CATEGORIES[:5]
    if locations is None:
        locations = BANGALORE_LOCATIONS[:3]

    all_leads = []
    stats = {"categories_done": 0, "total_leads": 0, "no_website": 0, "saved": 0}

    for i, category in enumerate(categories):
        for location in locations:
            msg = f"[{i+1}/{len(categories)}] {category} in {location}"
            print(f"\n{msg}")
            if progress_callback:
                progress_callback(msg)

            batch = []
            if use_maps:
                leads = await scrape_google_maps_browser(category, location, max_pages * 15)
                batch.extend(leads)
                print(f"  Maps: {len(leads)} leads")

            if use_justdial:
                leads = await scrape_justdial_httpx(category, location, max_pages)
                batch.extend(leads)
                print(f"  JD: {len(leads)} leads")

            if use_ddg:
                leads = await scrape_duckduckgo(category, location)
                batch.extend(leads)

            seen = set()
            unique = []
            for ld in batch:
                p = ld.get("phone", "")
                if p and p not in seen:
                    seen.add(p)
                    ld = await verify_no_website(ld)
                    unique.append(ld)

            no_site = [ld for ld in unique if not ld.get("has_website", False)]
            all_leads.extend(unique)  # Save ALL leads, not just no-website ones
            print(f"  Total: {len(unique)}, no-website: {len(no_site)}")

        stats["categories_done"] = i + 1

    stats["total_leads"] = len(all_leads)
    stats["no_website"] = len([ld for ld in all_leads if not ld.get("has_website")])

    if db:
        saved = await save_leads_to_db(all_leads, db, organization_id=organization_id)
        stats["saved"] = saved
        print(f"\nSaved {saved} leads to database")

    return stats


async def export_leads_to_json(leads: list[dict], filepath: str = "scraped_leads.json"):
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(leads)} leads to {filepath}")


async def import_from_csv(filepath: str, db: AsyncSession) -> int:
    saved = 0
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            phone = normalize_phone(row.get("phone", ""))
            if not phone or not is_valid_phone(phone):
                continue
            existing = await db.execute(select(Lead).where(Lead.phone == phone))
            if existing.scalar_one_or_none():
                continue
            try:
                lead = Lead(
                    business_name=row.get("business_name", "Unknown")[:255],
                    phone=phone,
                    industry=row.get("industry", row.get("category", "General"))[:128],
                    category=LeadCategory.COLD,
                    status=LeadStatus.DISCOVERED,
                    location=row.get("location", row.get("address", ""))[:255],
                    business_description=row.get("description", "")[:1000],
                    source="csv_import",
                    social_profiles={},
                )
                db.add(lead)
                saved += 1
            except Exception:
                continue
    if saved > 0:
        await db.flush()
    return saved


async def scrape_single_category(
    category: str,
    location: str = "Bangalore",
    max_results: int = 30,
    db: AsyncSession | None = None,
    organization_id: uuid.UUID | None = None,
) -> list[dict]:
    all_leads = []
    maps_leads = await scrape_google_maps_browser(category, location, max_results)
    jd_leads = await scrape_justdial_httpx(category, location)

    seen = set()
    for ld in maps_leads + jd_leads:
        p = ld.get("phone", "")
        if p and p not in seen:
            seen.add(p)
            ld = await verify_no_website(ld)
            if not ld.get("has_website", False):
                all_leads.append(ld)

    if db:
        saved = await save_leads_to_db(all_leads, db, organization_id=organization_id)
        print(f"  Saved {saved} to DB")

    return all_leads

