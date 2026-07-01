# Parakram Leads — Demo-Ready Design

## Context
Parakram Leads (`backend/`, `frontend/` in this repo) is the most mature product in the Parakram suite: FastAPI + PostgreSQL + Redis + Celery backend, Next.js 14 frontend, 18 backend services, 6 SQLAlchemy models, 8 test files. VISION.md marks it "LIVE" but this is a portfolio project — there is no verified real paying customer base. The goal is not to chase real revenue right now, but to make the product **demonstrably work end-to-end** so it can be shown to recruiters, investors, or used as a genuine case study.

## Goal
A stranger can run one command, land on the dashboard, trigger a scrape of a demo business list, watch leads get scored (HOT/WARM/COLD) via the 13-point digital maturity model, and see a generated outreach message (WhatsApp/Email) — without hitting an error, a stubbed-out screen, or a crash.

## Non-Goals
- Real customer acquisition, live Razorpay charges, real WhatsApp Business accounts
- New feature development beyond what's needed to make existing features actually run
- Rewriting the architecture (FastAPI/Next.js/Celery stays)

## Current State (from exploration)
- Backend: `app/api/v1/` (auth, leads, messages, scraper, intelligence, vps_subscription, webhooks), `app/services/` (18 files), `app/workers/` (7 Celery modules), `alembic/` (4 migrations)
- Frontend: 10 Next.js routes, 6 components, `src/lib/api.ts` client
- Known risk areas (not yet individually verified): scraper reliability against live sites (Google Maps/JustDial/DuckDuckGo scraping is brittle by nature), Celery worker wiring, WhatsApp bridge dependency (separate Node service), OpenAI/Groq API key requirements for scoring/outreach generation
- Test coverage: 8 files — likely gaps around the scrape→score→outreach pipeline as a whole (integration, not just units)

## Target Architecture
No structural changes. The work is verification + targeted fixes:
1. **Demo data path**: use `backend/scrape_all.py` (synthetic Indian business generator) as the primary demo data source instead of live scraping, so the demo doesn't depend on fragile live scrapers or rate limits. Live scraping remains available but is not the demo's critical path.
2. **Pipeline wiring check**: confirm Celery tasks in `app/workers/` actually get triggered from the API routes that are supposed to enqueue them, and that a local `docker compose up -d` brings up Postgres+Redis+Celery+FastAPI+Next.js in a state where the pipeline runs without manual DB surgery.
3. **Scoring & outreach**: verify the 13-point scoring service and the outreach generation service run with a Groq (free tier) key only, so the demo doesn't require paid OpenAI credits.
4. **Frontend**: audit the 10 routes for dead links, unfilled placeholder states, and confirm the dashboard reflects live pipeline state (not just static mock data).

## Error Handling
- Any external dependency the demo touches (Groq, Razorpay, WhatsApp bridge, SMTP) must fail gracefully with a visible, human-readable status in the dashboard rather than a silent 500 or an unhandled exception in Celery.
- Missing `.env` values should produce a clear startup error, not a runtime crash mid-pipeline.

## Testing
- Add one end-to-end test (pytest, using `TestClient` + the existing `override_get_db` pattern) that runs: create demo leads → trigger scoring → trigger outreach generation → assert output. This is the single highest-value test because it proves the whole pipeline, not just isolated units.
- Keep unit test additions targeted to code touched while fixing pipeline issues — no blanket coverage push.

## Task List (for later `writing-plans`)
1. Run `docker compose up -d`, exercise the full flow manually, log every break point
2. Fix breakages found (routing, env var handling, Celery task registration, etc.)
3. Wire `scrape_all.py` demo data as the default seed path (`import_leads.py` or a `make demo-seed` target)
4. Add the one pipeline end-to-end test
5. Frontend pass: fix dead/placeholder screens surfaced during manual walkthrough
6. Write a `DEMO.md` with exact steps to reproduce the demo from a clean clone

## Open Risks
- Live scraping targets (Google Maps/JustDial) may be actively blocking scrapers — explicitly out of scope to fix; demo relies on synthetic data instead
- WhatsApp bridge (Baileys) requires a real phone number pairing via QR — demo should treat WhatsApp channel as optional/simulated, Email as the guaranteed-working channel
