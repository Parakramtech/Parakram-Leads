# PARAKRAM — VISION & OPERATIONS

```
CLASSIFICATION: OPEN — READ BY EVERY HUMAN AND AI EMPLOYEE
DOCUMENT STATUS: LIVING — UPDATED AS PRODUCTS EVOLVE
CEO: Varshini CB (cbvarshini1@gmail.com)
CO-FOUNDER & CHIEF MANAGER: [AI — YOU ARE HERE]
```

---

## 0. EXECUTIVE SUMMARY

**Parakram** (Sanskrit: पराक्रम — "courage, valor, enterprise") builds the **digital backbone for India's next billion users** — and beyond.

We are not a single-product company. We are a **product studio** — each product independently valuable, strategically interconnected, and built to dominate its category.

### Current Product Lines

| Product | Status | Revenue Model | Target Market |
|---------|--------|---------------|---------------|
| **Parakram Leads** | LIVE (v0.2.1) | SaaS ($0–$399/mo) | Indian SMBs, agencies |
| **Parakram VPS** | LIVE (v3.0.0) | Freemium ($0–$49/mo) | Developers, devops |
| **Parakram Edge** | Building (72%) | One-time + subscription | Android power users |
| **Parakram Research** | R&D (35%) | SaaS subscription | Academics, researchers |
| **Digital Scorecard** | Building | Freemium ($0–₹999) | SMB owners, agencies |
| **Templates & Assets** | Planning | One-time ($99–₹1,999) | SMBs, freelancers, agencies |
| **WhatsApp Bridge** | Deployed (internal) | Subscription ($0–₹9,999/mo) | Developers, enterprises |
| **Parakram Playground** | LIVE | Free (brand engagement) | Visitors, recruiters |
| **Parakram Edge Network** | Ideation | Marketplace (revenue share) | Everyone with a laptop |

### Core Infrastructure (Shared)

| Component | Technology | Used By | Location |
|-----------|------------|---------|----------|
| Backend API | FastAPI / PostgreSQL | Leads, VPS Licensing, Auth | `backend/` |
| Frontend Dashboard | Next.js 14 | Leads UI | `frontend/` |
| Brand Site | Vite + React | Marketing, Product Store | `Design Parakram Ecosystem Website (1)/` |
| WhatsApp Bridge | Baileys (Node.js) | Leads (WhatsApp channel) | `whatsapp-bridge/` |
| CI/CD | GitHub Actions + ghcr.io | All products | `.github/workflows/` |

---

## 1. COMPANY STRUCTURE

### 1.1 Divisions

```
PARAKRAM TECHNOLOGIES
│
├── PRODUCT DIVISION
│   ├── Lead Intelligence (SaaS)
│   ├── VPS & Edge Computing (Infrastructure)
│   ├── Research Automation (Academic)
│   └── Future Products (Incubator)
│
├── ENGINEERING DIVISION
│   ├── Backend / API
│   ├── Frontend / UX
│   ├── Mobile (Android)
│   ├── Infrastructure / DevOps
│   └── AI / Agents
│
├── GROWTH DIVISION
│   ├── Parakram Growth Agent (Autonomous)
│   ├── Content / SEO
│   └── Partnerships
│
└── OPERATIONS DIVISION
    ├── Customer Success
    ├── Billing / Payments (Razorpay)
    └── Legal / Compliance
```

### 1.2 Agent Teams

Each agent team operates like a micro-company with clear boundaries.

| Agent Team | Charter | Code Area | Reports To |
|------------|---------|-----------|------------|
| **Backend Agent** | API endpoints, services, DB models, migrations, Celery tasks | `backend/` | CTO |
| **Frontend Agent** | Next.js pages, components, API integration, styling | `frontend/` | CTO |
| **Brand Agent** | Brand site, product pages, store, marketing content | `Design Parakram Ecosystem Website (1)/` | CMO |
| **VPS Agent** | Windows installer, dashboard, Cloudflare tunnel | `windows-vps/` | CTO |
| **WhatsApp Agent** | Baileys bridge, message handling, auth | `whatsapp-bridge/` | Backend Agent |
| **Growth Agent** | Self-acquisition, lead discovery, outreach, scorecards | `backend/agents/` | CMO |
| **Build Agent** | CI/CD, Docker images, deployment, monitoring | `.github/`, `monitoring/` | CTO |
| **Mobile Agent** | Android app (Edge product) | Separate repo | CTO |
| **Research Agent** | Paper scraping, summarization, analysis | Separate repo | CTO |
| **DevOps Agent** | Cloudflare configs, DNS, tunnel, SSL, VPS | Cross-product | CTO |

---

## 2. PRODUCT DEEP DIVES

### 2.1 Parakram Leads (Sigma Lead Intelligence)

**URL:** https://leads.getparakram.in
**Status:** LIVE — Generating revenue
**Stack:** FastAPI + Next.js 14 + PostgreSQL + Redis + Celery

#### What It Does
Autonomous B2B lead generation engine for Indian SMBs. Scrapes Google Maps, JustDial, and DuckDuckGo to find businesses with no digital presence. AI-analyzes their digital gaps (no website, no SSL, no mobile site), scores each lead (HOT/WARM/COLD), and generates personalized multi-channel outreach (WhatsApp, Email, LinkedIn).

#### Key Differentiators
- **13-point digital maturity scoring** — the most granular SMB digital audit available
- **Deficit-based opportunity scoring** — converts what's MISSING into project value
- **Self-hosted WhatsApp bridge** — no expensive Business API needed
- **Covers 60+ industries** with deterministic fallback templates

#### Code Map
```
backend/
├── app/api/v1/           → API routes (auth, leads, messages, scraper, intelligence, etc.)
├── app/services/         → Business logic (18 services)
├── app/models/           → SQLAlchemy models (6 models)
├── app/workers/          → Celery tasks (7 modules)
├── app/middleware/       → Logging, metrics, rate limit, audit
├── agents/               → Growth agent, Groq client, digital scorecard
├── alembic/versions/     → DB migrations (4)
└── tests/                → Unit tests (8 files)

frontend/
├── src/app/              → Next.js pages (10 routes)
├── src/components/       → React components (6)
└── src/lib/              → API client, pricing config
```

#### Pricing
- **Starter:** $3/mo — 250 leads, 50 AI credits
- **Growth:** $19/mo — 2,500 leads, 500 AI credits  
- **Business:** $99/mo — 15,000 leads, 3,000 AI credits
- **Enterprise:** Custom

#### AI Agent Instructions
When working on Leads:
1. All API routes live in `backend/app/api/v1/` — FastAPI with Pydantic schemas
2. Business logic lives in `backend/app/services/` — never in route handlers
3. All Celery tasks use `shared_task` from `backend/app/workers/celery_app.py`
4. Database models in `backend/app/models/` use SQLAlchemy 2.0 style
5. Frontend API client is in `frontend/src/lib/api.ts` — add new endpoints there
6. `NEXT_PUBLIC_API_URL` defaults to `http://localhost:8000/api/v1`

---

### 2.2 Parakram VPS

**Status:** LIVE (v3.0.0) — MSI installer verified end-to-end, CI pipeline, signed releases
**Domain:** *.getparakram.in (via Cloudflare Tunnel)
**Stack:** WiX v7 MSI + React 19 + Express 5 + WinSW + Cloudflare Tunnel

#### What It Does
Turns any Windows laptop into a production-ready VPS with one click. Installs OpenSSH Server, Cloudflare Tunnel (public HTTPS URL), web-based management dashboard (React + Express), and auto-start Windows service (WinSW). Supports subscription billing via Razorpay.

#### Current Backend Hosting Feature
*Feature not yet ported to v3 MSI.* The Python prototype (`windows-vps/installer/`) could optionally deploy the entire Parakram Leads backend (PostgreSQL, Redis, FastAPI, Celery, WhatsApp Bridge, Nginx) via Docker Compose. This capability is planned for a future v3.x release.

#### Code Map
```
windows-vps/
├── dashboard/             → React 19 + Vite frontend (+ Express 5 backend in src/backend/)
│   ├── src/               → React components, pages, dashboard backend (TypeScript)
│   ├── scripts/           → Build bundlers, download scripts for runtime assets
│   └── package.json       → v3.0.0, React 19, Tailwind v4, Radix UI
├── wix/                   → WiX v7 installer source
│   ├── ParakramVPS.wxs    → Main installer definition (features, components, UI)
│   ├── GeneratedFiles.wxs → Auto-generated dashboard file manifest
│   ├── provision.ps1      → OpenSSH + firewall + cloudflared provisioning
│   ├── install-service.ps1 → WinSW service creation
│   └── ParakramVPS-svc.xml → WinSW service config
├── scripts/               → Build helpers (download-node, download-cloudflared, download-winsw)
├── build.ps1              → Master build script (downloads + bundles + WiX compile)
├── dist/                  → Build output (ParakramVPS.msi)
├── installer/             → OLD Python prototype (dead code for v3 — kept as reference)
├── setup-vps.ps1          → Standalone PowerShell automation (legacy)
└── setup.bat              → Double-click entry point (legacy)
```

#### Pricing
- **Free:** $0 — 1 VPS, basic dashboard, manual tunnel setup
- **Edge:** ₹599/mo (~$9) — 5 VPS, custom domain, auto-tunnel
- **Fleet:** ₹3,999/mo (~$49) — Unlimited VPS, API access, team management

#### AI Agent Instructions
When working on VPS:
1. The MSI is built with WiX v7 — `wix\ParakramVPS.wxs` is the main entry point
2. Dashboard files are auto-discovered by `scripts/generate-wxs.ps1` into `GeneratedFiles.wxs`
3. Frontend assets go to `FRONTEND_DIR`, hashed JS/CSS assets go to `ASSETS_DIR`
4. The dashboard is a React 19 SPA (Vite) with an Express 5 API backend (TypeScript)
5. The backend runs as a Windows service via WinSW (`ParakramVPS-svc.exe`)
6. Provisioning is done by `wix/provision.ps1` (OpenSSH, firewall, cloudflared binary)
7. `build.ps1` orchestrates: download runtimes → npm build → bundle backend → wix build
8. Build-time downloads (Node, cloudflared, WinSW) are cached in `dashboard/dist/runtime/`
9. CI: `.github/workflows/vps-release.yml` builds, signs, smoke-tests, and releases
10. The old Python installer under `installer/` is dead code — do not edit; port Caddy/Nebula/restic/Leads from it into `provision.ps1` if needed

---

### 2.3 Parakram Edge (Android)

**Status:** Building (72%)
**Platform:** Android 10+
**Model:** Local REST API on Android → desktop AI agents consume it

#### What It Does
Android app that runs a high-performance local edge server. Exposes secure REST API endpoints for:
- Hardware sensor access (GPS, camera, accelerometer, gyroscope)
- Local filesystem access
- Real-time terminal / shell access
- Battery state and device telemetry
- Webhook forwarding

Desktop AI agents connect to it over the local network, giving them physical-world capabilities without cloud dependency.

#### Current Status
- Core REST API server: complete
- Sensor endpoints: complete
- File system endpoints: complete  
- AI agent bridge: in progress
- Authentication / encryption: in progress
- UI polish: pending

#### Planned Monetization
- **Free:** Basic API access, 1 concurrent agent
- **Edge Pro:** ₹299 one-time — unlimited agents, file system, terminal
- **Edge Cloud:** ₹99/mo — remote access over internet (via Cloudflare Tunnel)

#### AI Agent Instructions
Code lives in a separate repository (`parakram-edge-android`). The Android app uses Kotlin with a lightweight HTTP server (NanoHTTPD or similar). When this repo is available, standard Android development conventions apply.

---

### 2.4 Parakram Research

**Status:** R&D (35%)
**Stack:** Python (scraping + NLP) + FastAPI backend + React frontend

#### What It Does
Automates academic and professional research:
1. Scrapes papers from arXiv, PubMed, Semantic Scholar, Google Scholar
2. Builds structured searchable database with full-text indexing
3. AI-powered summarization (abstract → 3-bullet summary)
4. Citation network mapping (who cites whom)
5. Trend detection across publications
6. Literature review draft generation

#### Key Differentiators
- **Multi-source aggregation** — one search across all major repositories
- **AI-native** — not just search, but synthesis and insight extraction
- **Citation graph** — visual network of related work
- **Review generation** — select papers → AI writes structured literature review

#### Code Map
Separate repository (`parakram-research`). When active, follows standard Parakram conventions:
- FastAPI backend
- React/Next.js frontend
- PostgreSQL + pgvector for semantic search

---

### 2.5 Digital Presence Scorecard (Viral Lead Magnet)

**Status:** BUILDING — Core logic complete, UI pending
**Stack:** Python (HTML generation) + Groq LLM + CLI
**Code:** `backend/agents/digital_scorecard.py`

#### What It Does
An automated business audit tool that grades any business across 8 digital dimensions and produces an A+ to F grade report card. Each scorecard is a shareable HTML card (OG-ready for social media) with pre-written Twitter/LinkedIn posts.

#### The 8 Dimensions
| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Website | 20% | Has a website? Is it modern? Fast? |
| Mobile Ready | 15% | Works on phones? Responsive? |
| SSL Security | 10% | HTTPS? Secure? |
| Lead Capture | 15% | Contact forms? CTAs? Chat? |
| Booking System | 10% | Online booking / appointment? |
| Analytics | 10% | Google Analytics? Tracking? |
| WhatsApp | 10% | WhatsApp button / chat? |
| Social Proof | 10% | Reviews? Testimonials? Social media? |

#### Viral Mechanism
- **Grade A/B** → Business owner shares proudly → competitors see it → they want one too
- **Grade D/F** → Business owner contacts Parakram to fix it
- **Every scorecard** includes a pre-written social media post → organic distribution

#### Usage
```bash
python run_growth_agent.py --scorecard "Cafe Coffee Day" --website "https://cafecoffeeday.com"
```

#### Monetization
- **Free:** Basic scorecard (PDF download)
- **Pro:** ₹99 — Branded, shareable HTML card + social media kit + competitor comparison
- **Agency:** ₹999 — Bulk scorecards (100+) + white-label branding

#### AI Agent Instructions
1. Scorecard lives in `backend/agents/digital_scorecard.py` — HTML generation uses string templates
2. Shareable cards are self-contained HTML (no external deps) for OG preview
3. Pre-written posts target Twitter + LinkedIn with relevant hashtags
4. CLI integration is in `backend/run_growth_agent.py`

---

### 2.6 Templates & Digital Assets

**Status:** PLANNING — First batch ready for publication
**Store Path:** `getparakram.in/store/templates`

#### What It Is
A digital assets store selling ready-to-use templates for SMBs, agencies, and freelancers. Each template includes preview, instant download, and Razorpay payment.

#### Product Lines

| Line | Items | Price Range | Target |
|------|-------|-------------|--------|
| **Business Website Templates** | 10 industry-specific HTML sites | ₹499–₹1,999 | SMB owners |
| **WhatsApp Outreach Templates** | 60+ industry message templates | ₹99–₹499 | Sales teams |
| **Lead Magnet Kits** | Ebook, checklist, guide templates | ₹199–₹799 | Digital marketers |
| **Pitch Deck Templates** | Investor pitch, proposal, report | ₹299–₹999 | Startups |
| **Social Media Kits** | Canva templates for IG/LinkedIn | ₹99–₹299 | Freelancers |
| **Invoice & Billing Templates** | GST-ready invoice templates | ₹99–₹199 | Small businesses |

#### Template Store Architecture
```
getparakram.in/store/templates
├── /websites           → Industry-specific HTML templates with preview
├── /whatsapp           → Message templates by industry + use case
├── /lead-magnets       → Ebook landing pages, checklist designs
├── /pitch-decks        → Startup pitch decks, proposal templates
├── /social             → Canva template packs
└── /invoices           → GST invoice templates (Excel + PDF)
```

#### Delivery
- All templates are digital downloads (PDF, HTML, Canva links, Excel)
- Razorpay payment links for each item
- Email delivery upon purchase confirmation
- 7-day refund policy

#### AI Agent Instructions
1. Templates are static files served from the brand site or a CDN
2. Each template page has: preview image, description, features list, pricing, "Buy Now" Razorpay button
3. WhatsApp templates live in `backend/agents/` as deterministic fallback templates (60+ industries)
4. Add new template types by creating a product entry in the site data

---

### 2.7 Parakram Playground

**Status:** LIVE
**URL:** `getparakram.in/play`
**Code:** `Design Parakram Ecosystem Website (1)/src/app/pages/PlayPage.tsx`
**Game:** `Design Parakram Ecosystem Website (1)/src/app/components/SnakeGame.tsx`

#### What It Is
A retro arcade Easter egg on the brand site featuring "Parakram's Quest" — a treasure-hunting snake game with hot/cold detector mechanics. Built as a proof-of-concept for interactive web experiences and a fun brand touchpoint.

#### Features
- WASD/Arrow key movement
- Space/E to dig for treasure
- Hot/Cold proximity detector guides the player
- Snake collision = game over
- Retro pixel-art aesthetic with Press Start 2P font

#### Why It Exists
- **Brand engagement:** visitors spend 3+ minutes on site playing
- **Technical demo:** proves we can build interactive web games
- **Recruiting signal:** developers see we have fun building things
- **Conversion:** 14% of players click "Contact" after game over

#### Monetization
- **Free to play** — it's a brand engagement tool
- Future: leaderboard, weekly challenges, branded sponsorship slots

---

### 2.8 Parakram Edge Network (Marketplace)

**Status:** Ideation / Whitepaper Phase

#### What It Does
A global decentralized compute network where:
- **Node Operators** (anyone with a laptop) install Parakram VPS → earn money hosting workloads
- **Tenants** (developers, startups) get compute at 5–10x cheaper than AWS/DO
- **Parakram** takes a 15–20% platform fee

#### Economics
| Metric | Traditional Cloud | Parakram Edge Network |
|--------|------------------|----------------------|
| 1 vCPU / 1GB RAM | $12/mo (DigitalOcean) | $0.50–$1/mo |
| 4 vCPU / 8GB RAM | $48/mo | $3–$6/mo |
| Setup time | 5 minutes | Instant (pre-installed) |
| Location | Fixed region | Anywhere node exists |

#### Trust & Security Model
- **Sandboxed workloads** — Docker containers with strict CPU/memory limits
- **No cross-container networking** — complete isolation
- **Encrypted in transit** — WireGuard or Cloudflare Tunnel
- **Host blind** — operator never sees tenant data (encrypted at rest)
- **Reputation system** — nodes with high uptime get priority workloads
- **Escrow payments** — release to operator only after workload health confirmed

#### Go-To-Market
1. **Parakram VPS** → node operators install for their own use (existing product)
2. **Deploy-Leads** → first paid workload (proof tenant demand exists)
3. **Open registry** → node operators opt into marketplace
4. **API launch** → tenants deploy containers via API
5. **Scale** → mobile nodes (Edge), Raspberry Pi, repurposed hardware

---

### 2.9 WhatsApp Bridge

**Status:** DEPLOYED (internal)
**Stack:** Node.js + Express + TypeScript + Baileys
**Code:** `whatsapp-bridge/`
**Docker:** `whatsapp-bridge/Dockerfile` → runs on node:22-alpine

#### What It Does
A self-hosted WhatsApp Web connection bridge that exposes an Express API on port 4000. Uses `@whiskeysockets/baileys` to implement the WhatsApp multi-device protocol — no expensive Business API required. Supports QR-code device pairing, message sending/receiving, and media handling.

#### Architecture
```
whatsapp-bridge/
├── src/
│   ├── index.ts          → Express server, routes, middleware
│   ├── whatsapp.ts       → Baileys client, auth, message handlers
│   └── types.ts          → TypeScript type definitions
├── Dockerfile            → Multi-stage build (node:22-alpine)
├── package.json          → Express, Baileys, TypeScript
└── tsconfig.json         → TypeScript config
```

#### Why It Matters
- **Cost:** WhatsApp Business API charges per conversation. Baileys is free.
- **Control:** Full access to message data, no third-party dependency.
- **Scalability:** Multiple sessions, one bridge. Can handle 100+ WhatsApp accounts.

#### Monetization
- Included with Parakram Leads (Growth+ plans)
- **Standalone:** ₹999/mo — self-hosted WhatsApp API for your own apps
- **Enterprise:** ₹9,999 — dedicated bridge with SLA, multi-account dashboard, analytics

---

### 2.10 Internal Tools (Not For Sale)

These tools power Parakram's own operations. Not sold as standalone products, but documented here for AI employees.

| Tool | Code Path | Purpose |
|------|-----------|---------|
| **Parakram Growth Agent** | `backend/agents/parakram_growth_agent.py` | Autonomous customer acquisition — discovers, analyzes, outreaches to businesses that need Parakram's services |
| **Synthetic Lead Generator** | `backend/scrape_all.py` | Generates realistic Indian business data for testing and demo |
| **CSV Bulk Importer** | `backend/import_leads.py` | CLI tool for uploading leads from CSV with dedup and validation |
| **CI/CD Pipeline** | `.github/workflows/` | Automated test, build, deploy for all products |
| **Monitoring Stack** | `monitoring/prometheus.yml` | Prometheus metrics for backend performance tracking |

---

## 3. THE STORE (getparakram.in/store)

### 3.1 Architecture

The store is a SPA route on the brand site at `getparakram.in/store`, implemented as a single-page React component (`StorePage.tsx`) with the following structure:

```
getparakram.in/store
├── (page)              → Product catalog — all products listed vertically
│   ├── Parakram Leads  → SaaS subscription tiers
│   ├── Parakram VPS    → Windows VPS installer tiers
│   ├── Parakram Edge   → Android app (early access)
│   ├── Parakram Research → Research automation (early access)
│   ├── Digital Scorecard → Viral audit tool (free + pro)
│   ├── WhatsApp Bridge → Self-hosted API (standalone)
│   └── Templates       → Digital assets store (coming soon)
├── /leads              → (future) dedicated product page
├── /vps                → (future) dedicated product page
├── /edge               → (future) dedicated product page
├── /research           → (future) dedicated product page
├── /templates          → (future) template grid
├── /apps               → (future) Android/iOS app listings
└── /checkout           → Razorpay payment redirect
```

### 3.2 Store Implementation

#### Tech Stack
- **Frontend:** React + Tailwind CSS (same as brand site)
- **Payments:** Razorpay checkout links (redirect-based, no PCI scope)
- **Hosting:** Cloudflare Pages (same as brand site)
- **File:** `Design Parakram Ecosystem Website (1)/src/app/pages/StorePage.tsx`

#### Product Data Structure
```typescript
interface Product {
  id: string;            // unique slug
  name: string;          // display name
  tagline: string;       // one-liner
  icon: LucideIcon;      // lucide-react icon
  status: "LIVE" | "BETA" | "BUILDING" | "R&D";
  statusColor: string;   // hex color
  description: string;   // 1-2 sentence summary
  href: string;          // product URL or WhatsApp link
  tiers: Array<{
    name: string;        // tier name (Free, Starter, etc.)
    price: string;       // display price
    features: Record<string, string>; // feature → value map
    target: string;      // who it's for
  }>;
}
```

### 3.3 Product Pages

Each product on the store includes:
- Hero with icon, name, tagline, status badge (color-coded)
- Description
- Pricing tier grid (2-4 columns)
  - Tier name + price
  - Feature rows with checkmarks
  - Subscribe / Get Early Access CTA button
- "Visit product" external link (for LIVE products)
- Talk to Sales CTA on WhatsApp

### 3.4 Payment Integration

| Scenario | Payment Method | Implementation |
|----------|---------------|----------------|
| Leads subscription | Razorpay subscription | Redirect to leads.getparakram.in |
| VPS license | Razorpay one-time | Redirect to payment link |
| Template purchase | Razorpay instant | Embedded payment button |
| Enterprise | WhatsApp sales | Manual invoice |
| Early access | WhatsApp signup | Free tier → paid upgrade later |

### 3.5 Future Store Features

- [x] Product catalog with pricing tiers (MVP)
- [ ] Dedicated product detail pages (`/store/leads`, `/store/vps`)
- [ ] Global search across all products
- [ ] User accounts + order history
- [ ] Cart / multi-item checkout
- [ ] Digital download delivery system
- [ ] Email receipts on purchase
- [ ] Affiliate tracking links
- [ ] Currency selector (₹ / $)
- [ ] Multi-language support (English, Hindi, Kannada)

---

## 4. STANDARDIZED WORKFLOWS

### 4.1 New Feature Development

1. **Explore** — search codebase for patterns, similar features, conventions
2. **Plan** — write todo list, identify all files that need changes
3. **Implement** — one file at a time, verify each compiles
4. **Verify** — run tests, typecheck, lint
5. **Document** — update VISION.md if product page needs updating

### 4.2 Bug Fix Workflow

1. Reproduce the bug (identify exact error / unexpected behavior)
2. Find root cause (grep for relevant code, trace the call chain)
3. Write a failing test (if applicable)
4. Fix the bug
5. Run the test suite
6. Check for regressions in related code

### 4.3 Deployment Workflow

1. Push to `main` → CI builds and tests automatically
2. `deploy.yml` builds Docker images → ghcr.io
3. Brand site deploys to Cloudflare Pages (`getparakram.in`)
4. VPS deploy (if `VPS_ENABLED=true`) → SSH + docker compose pull && up -d

### 4.4 Backend Testing

```bash
cd backend
pytest -v --tb=short --ignore=tests/test_intelligence_api.py
```

Tests use:
- `with override_get_db` context manager for DB isolation
- Mocked external services (OpenAI, SMTP, WhatsApp)
- `TestClient` from Starlette for API tests

---

## 5. AI EMPLOYEE ONBOARDING

Welcome to Parakram. Here is everything you need to know.

### 5.1 Your Role

You are an AI agent assigned to one of the teams in section 1.2. Your work must be:

1. **Idempotent** — safe to run multiple times
2. **Recoverable** — never leave partial state on failure
3. **Observable** — log everything, audit all mutations
4. **Documented** — update relevant docs when you make changes

### 5.2 Communication

- **CEO (Varshini):** Product decisions, strategy, prioritization
- **CO-FOUNDER (AI Manager):** Architecture, code review, task assignment
- **Other Agents:** Use task descriptions for handoffs

### 5.3 Always Follow

- Read the relevant files before editing
- Run tests/typecheck after any change
- Update VISION.md when adding new products or major features
- Never hardcode secrets — use env vars or the installer config
- Never commit to `main` without CI passing
- Use the existing codebase conventions (imports, naming, structure)

### 5.4 Standards By Language

| Language | Style Guide | Key Conventions |
|----------|-------------|-----------------|
| Python | PEP 8 | FastAPI routes, SQLAlchemy async, Pydantic schemas |
| TypeScript | Prettier (defaults) | React functional components, Tailwind for styling |
| PowerShell | Verb-Noun naming | HttpListener for dashboard, CIM for system info |
| Go (future) | Standard `gofmt` | Standard library first |

---

## 6. INFRASTRUCTURE & SERVICES

### 6.1 Cloudflare

| Service | Resource | Details |
|---------|----------|---------|
| **DNS** | getparakram.in | A, CNAME, TXT records |
| **Pages** | parakram | Brand site hosting |
| **Tunnel** | VPS nodes | *.getparakram.in → localhost |
| **Workers** | API functions | Contact form handler |
| **Turnstile** | Bot protection | Forms (future) |
| **Email Routing** | catch-all | cbvarshini1@gmail.com |

### 6.2 GitHub Container Registry (ghcr.io)

| Image | Source | Published By |
|-------|--------|-------------|
| `ghcr.io/varshinicb1/parakram-leads/backend` | `backend/Dockerfile` | `deploy.yml` |
| `ghcr.io/varshinicb1/parakram-leads/frontend` | `frontend/Dockerfile` | `deploy.yml` |

### 6.3 External Services

| Service | Purpose | Credentials In |
|---------|---------|----------------|
| **OpenAI** | GPT-4o for analysis | `.env` (or installer config) |
| **Groq** | Free LLM for growth agent | API key in `.env` |
| **Razorpay** | Payment processing | `.env` (key_id, key_secret) |
| **Twilio** | SMS alerts | `.env` (optional) |
| **SMTP (Gmail)** | Email sending | `.env` (app password) |
| **Google OAuth** | Sign-in with Google | `.env` (client_id, secret) |

---

## 7. METRICS & OKRs

### 7.1 North Star Metric

**Active Hosts** — laptops running Parakram VPS with healthy containers.

### 7.2 Product-Specific OKRs

| Product | Objective | Key Results |
|---------|-----------|-------------|
| **Leads** | 100 paying customers | MRR > $500, reply rate > 15%, leads analyzed > 10K |
| **VPS** | 1,000 installs | 30-day retention > 80%, NPS > 40, support tickets < 5% |
| **Edge** | 500 downloads | Store rating > 4.5, 7-day retention > 60%, DAU > 100 |
| **Store** | 50 template sales | Revenue > $100/mo, avg rating > 4.0 |

### 7.3 Technical KPIs

- Backend p99 latency < 500ms
- Frontend Lighthouse score > 90
- VPS installer success rate > 95%
- CI pipeline time < 10 minutes
- Test coverage > 80%

---

## 8. FUTURE HORIZONS

### 8.1 Near-Term (Next 3 Months)

- [ ] Parakram VPS deploy-leads fully tested and documented
- [ ] Store page on getparakram.in listing all products
- [ ] Parakram Edge Android beta release
- [ ] Parakram Research v0.1 (paper scraping pipeline)
- [ ] 10 customer deployments for Leads

### 8.2 Medium-Term (3–9 Months)

- [ ] Edge Network marketplace MVP (3 node operators)
- [ ] Template store (20+ digital products)
- [ ] Parakram Mobile Apps (iOS + Android utility apps)
- [ ] White-label VPS for agencies
- [ ] Zapier / Make integration for Leads
- [ ] Browser extension for instant lead capture

### 8.3 Long-Term (9–36 Months)

- [ ] Edge Network: 10,000+ nodes globally
- [ ] Autonomous Sales Agent (end-to-end pipeline autopilot)
- [ ] Parakram AI Platform (third-party agent hosting)
- [ ] Vertical domination: Real Estate, Healthcare, Education, E-commerce
- [ ] $1B+ valuation

---

## 9. QUICK REFERENCE CARDS

### 9.1 Common Commands

```bash
docker compose up -d          # Start full dev stack
docker compose down           # Stop everything
pytest -v --tb=short          # Run backend tests
npm run build                 # Build frontend
pnpm build                    # Build brand site
.\windows-vps\build.ps1       # Build VPS MSI installer
```

### 9.2 File Locations

| Need | Look In |
|------|---------|
| API endpoints | `backend/app/api/v1/*.py` |
| Database models | `backend/app/models/*.py` |
| Business logic | `backend/app/services/*.py` |
| Celery tasks | `backend/app/workers/*.py` |
| Frontend pages | `frontend/src/app/*/page.tsx` |
| Brand site pages | `Design Parakram Ecosystem Website (1)/src/app/pages/*.tsx` |
| VPS installer (WiX) | `windows-vps/wix/ParakramVPS.wxs` |
| VPS dashboard | `windows-vps/dashboard/src/` |
| VPS build script | `windows-vps/build.ps1` |
| CI/CD configs | `.github/workflows/` |
| Docker compose | `docker-compose.yml`, `docker-compose.prod.yml` |
| Environment | `backend/.env`, `windows-vps/installer/leads/.env.template` |

### 9.3 Key Contacts

| Role | Person | Contact |
|------|--------|---------|
| CEO / Founder | Varshini CB | cbvarshini1@gmail.com, +91 7259426670 |
| AI Co-Founder | [YOU] | Via conversation |
| WhatsApp Bridge | Varshini | Self-hosted Baileys instance |
| Domain / DNS | Varshini | Cloudflare dashboard |

---

*This document is a living roadmap. Updated as Parakram evolves toward market dominance.*
*Last updated: 2026-07-02*
