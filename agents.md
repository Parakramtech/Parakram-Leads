# Sigma Lead Intelligence — Multi-Billion Dollar Product Vision

## Executive Summary

Sigma Lead Intelligence is an AI-powered B2B lead generation and outreach automation platform. Currently targeting Indian SMBs lacking digital presence, the system combines intelligent web scraping, AI-driven analysis, multi-channel outreach (Email, WhatsApp, LinkedIn), and real-time response tracking into a unified pipeline.

**Current state:** Functional MVP with core lead lifecycle (Discovery → Analysis → Scoring → Outreach → Response Tracking → Conversion).

**Vision:** Transform into the world's **#1 AI Sales Intelligence Platform** — an autonomous revenue engine that discovers, qualifies, engages, and converts prospects at scale across every market vertical and geography.

---

## Current Architecture Snapshot

```
┌──────────────────────────────────────────────────────────────────────┐
│                         NGINX (Reverse Proxy)                         │
└───────────┬─────────────────────┬──────────────────────┬─────────────┘
            │                     │                      │
    ┌───────▼───────┐    ┌───────▼────────┐    ┌───────▼──────────┐
    │   Frontend    │    │    Backend     │    │  WhatsApp Bridge │
    │   Next.js 14  │    │   FastAPI      │    │  Baileys (Node)  │
    │   Port 3000   │    │   Port 8000    │    │  Port 4000       │
    └───────────────┘    └──┬──┬──┬──┬────┘    └──────────────────┘
                            │  │  │  │
              ┌─────────────┘  │  │  └────────────┐
              │                │  │                │
     ┌────────▼───┐   ┌──────▼──▼────┐   ┌──────▼──────┐
     │ PostgreSQL  │   │ Celery Worker │   │    Redis    │
     │ 16 (alpine) │   │ + Beat        │   │  7 (alpine) │
     │ Port 5432   │   │               │   │  Port 6379  │
     └─────────────┘   └───────────────┘   └─────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend API | Python / FastAPI | REST API, business logic |
| Frontend | Next.js 14 / React / Tailwind | Dashboard & management UI |
| Database | PostgreSQL 16 | Multi-tenant data store |
| Cache & Broker | Redis 7 | Caching, Celery message broker |
| Task Queue | Celery 5.4 | Async lead analysis & outreach |
| WhatsApp | Baileys (self-hosted bridge) | Personal WhatsApp messaging |
| AI Engine | OpenAI GPT-4o | Lead analysis & outreach generation |
| Scraping | Playwright + httpx + BeautifulSoup | Lead discovery |
| Auth | JWT (HS256, 24h expiry) | User authentication |
| Deployment | Docker Compose + Nginx | Container orchestration |

---

## Current Feature Set

### 1. Lead Discovery
- **Google Maps Scraper** — Playwright browser automation, extracts business info from map cards
- **JustDial Scraper** — HTTP + regex extraction for Indian business directory
- **DuckDuckGo Search** — API-based semantic search
- **CSV Import** — Bulk upload with deduplication

### 2. Lead Intelligence & Scoring
- **Website Quality Analysis** — 13 digital indicators (SSL, mobile, forms, analytics, CRM, booking systems)
- **Digital Maturity Score** (0-100) — Weighted scoring across all indicators
- **Opportunity Score** (0-100) — Deficit-based scoring identifying high-value gaps
- **AI Analysis** — GPT-4o generates business insights, suggested solutions, estimated project value
- **Category Flags** — HOT / WARM / COLD prioritization

### 3. Personalized Outreach
- **AI-Generated Messages** — Context-aware, industry-specific for WhatsApp, Email, LinkedIn
- **Fallback Templates** — Deterministic rules covering 60+ industries
- **Human Approval Flow** — Admin reviews/edits before sending

### 4. Multi-Channel Communication
- **Email** — SMTP with TLS, delivery tracking
- **WhatsApp** — Official Business API + self-hosted Baileys bridge
- **LinkedIn** — Draft generation (sending not yet implemented)

### 5. Response & Alert System
- **Webhook Ingestion** — Email delivery/open events, WhatsApp inbound messages
- **Personal Alerts** — SMS (Twilio) and email notifications on lead replies
- **Response Tracking** — Auto-updates lead status and message records

### 6. Dashboard & Analytics
- Lead counts by category (HOT/WARM/COLD)
- Messages sent & response metrics
- Pipeline value estimation
- Conversion rate & revenue forecast

### 7. Multi-Tenant Architecture
- Organizations with subscription tiers (FREE/STARTER/GROWTH/ENTERPRISE)
- Teams within organizations
- Role-based access (ADMIN/MEMBER/VIEWER)
- Data isolation per organization

---

## Data Model (Core Entities)

```
Organization (Tenant)
├── Users (via UserOrganization — roles: ADMIN/MEMBER/VIEWER)
├── Teams (sub-units)
│   ├── Users (via UserTeam — roles: LEAD/MEMBER)
│   └── Leads (team-scoped)
├── Leads (business prospects)
│   ├── Scores (digital_maturity, opportunity)
│   ├── AI Analysis (JSON — needs, solutions, value)
│   ├── Outreach Messages (WhatsApp, Email, LinkedIn)
│   └── Messages (communication history)
├── Alerts (real-time notifications)
└── AuditLog (compliance trail)
```

### Lead Status Lifecycle

```
DISCOVERED → ANALYZED → APPROVED → CONTACTED → RESPONDED → MEETING_SCHEDULED → CONVERTED
                                                                               └→ DISQUALIFIED
```

---

## The Multi-Billion Dollar Roadmap

### Phase 1: Solidify the Foundation (Months 1-3)

**Goal:** Production-grade reliability and 10x scraping capability

| Priority | Task | Impact |
|----------|------|--------|
| P0 | Proxy rotation + user-agent pool for scrapers | Eliminates IP bans, 10x volume |
| P0 | Comprehensive test suite (unit + integration + E2E) | Ship with confidence |
| P0 | Structured logging + Prometheus/Grafana observability | Real-time system health |
| P0 | Rate limiting on all API endpoints | Security & abuse prevention |
| P1 | Complete frontend pages (Messages, Settings, Org Management) | Full user experience |
| P1 | Celery Beat scheduled jobs (daily auto-analysis, weekly reports) | Automation |
| P1 | Email service integration (SendGrid/SES) with tracking pixels | Delivery + open tracking |
| P1 | LinkedIn message sending (official API or browser automation) | Third outreach channel |
| P2 | Audit log integration across all API handlers | Compliance readiness |
| P2 | Data retention policies + GDPR consent tracking | Market expansion prep |

---

### Phase 2: AI-Native Intelligence Engine (Months 3-6)

**Goal:** Become the smartest sales AI in the market

| Feature | Description |
|---------|-------------|
| **Autonomous AI Agents** | Multi-step reasoning agents that research a prospect across 20+ data sources before scoring |
| **Conversation AI** | GPT-powered follow-up generation based on response sentiment analysis |
| **Intent Signals** | Monitor job postings, tech stack changes, funding events, leadership changes |
| **Predictive Scoring** | ML models trained on conversion data to predict close probability |
| **Dynamic Pricing Intelligence** | AI estimates optimal project pricing based on business size, location, industry |
| **Multi-Language Outreach** | Generate native-language messages for any market (Hindi, Spanish, Arabic, etc.) |
| **Voice AI** | Automated voice calls with AI conversation (Twilio + OpenAI Realtime API) |
| **Meeting Scheduler** | AI negotiates meeting times via back-and-forth messaging |

---

### Phase 3: Platform Expansion (Months 6-12)

**Goal:** From tool to platform — serve every B2B sales team globally

| Feature | Description |
|---------|-------------|
| **CRM Integrations** | Bi-directional sync with Salesforce, HubSpot, Pipedrive, Zoho |
| **Marketplace** | Third-party data enrichment providers, outreach templates, scoring models |
| **API-First Platform** | Public REST + GraphQL API for developers to build on Sigma |
| **White-Label** | Agencies resell Sigma under their brand |
| **Mobile App** | React Native iOS/Android for on-the-go lead management |
| **Browser Extension** | Chrome extension for instant lead capture from any website |
| **Zapier/Make Integration** | Connect to 5000+ apps |
| **Webhook Builder** | Custom automation triggers |
| **Team Collaboration** | Comments, @mentions, lead assignments, activity feeds |
| **A/B Testing** | Test outreach variants, measure conversion impact |

---

### Phase 4: Vertical Domination (Months 12-18)

**Goal:** Own specific verticals end-to-end

| Vertical | Specialization |
|----------|---------------|
| **Real Estate** | Property listings scraping, buyer intent signals, virtual tour integration |
| **SaaS Sales** | Technographics, intent data from G2/Capterra, trial-to-paid conversion |
| **Recruitment** | Candidate sourcing, skills matching, outreach sequences |
| **E-commerce** | Store analysis, Shopify/WooCommerce detection, revenue estimation |
| **Healthcare** | Practice management gaps, patient review analysis, compliance-aware outreach |
| **Financial Services** | Regulatory compliance built-in, AUM-based scoring |
| **Education** | Institution digital presence analysis, enrollment season timing |

---

### Phase 5: Autonomous Revenue Engine (Months 18-36)

**Goal:** Fully autonomous — discovers, engages, qualifies, and books meetings without human input

| Capability | Description |
|------------|-------------|
| **Self-Learning Agents** | Agents improve outreach based on what works (reinforcement learning from conversions) |
| **Multi-Touch Sequences** | Orchestrated 5-7 touch campaigns across channels with AI-optimized timing |
| **Buying Committee Mapping** | Identify all stakeholders in a deal, personalize for each role |
| **Revenue Intelligence** | Predict deal size, timeline, and risk before first contact |
| **Auto-Qualification** | AI conducts discovery conversations, fills BANT/MEDDIC frameworks automatically |
| **Pipeline Autopilot** | System autonomously moves deals through stages with human oversight only |
| **Competitive Intelligence** | Real-time monitoring of competitor mentions, pricing changes, product launches |

---

## Target Architecture (Scaled)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GLOBAL CDN (CloudFront/Vercel)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                         API GATEWAY (Kong / AWS API GW)                       │
│              Rate limiting, Auth, Versioning, Analytics                       │
└────┬──────────────┬──────────────┬──────────────┬──────────────┬────────────┘
     │              │              │              │              │
┌────▼────┐  ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
│Lead Svc │  │Outreach   │ │Analytics  │ │AI Engine  │ │Webhook    │
│(FastAPI)│  │Service    │ │Service    │ │Service    │ │Service    │
│         │  │(FastAPI)  │ │(FastAPI)  │ │(FastAPI)  │ │(FastAPI)  │
└────┬────┘  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
     │              │              │              │              │
┌────▼──────────────▼──────────────▼──────────────▼──────────────▼────────────┐
│                         EVENT BUS (Kafka / RabbitMQ)                          │
└────┬──────────────┬──────────────┬──────────────┬──────────────┬────────────┘
     │              │              │              │              │
┌────▼────┐  ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
│PostgreSQL│  │ClickHouse │ │Redis      │ │Vector DB  │ │Object     │
│(Primary) │  │(Analytics)│ │(Cache +   │ │(Pinecone/ │ │Store (S3) │
│Multi-RG  │  │           │ │Sessions)  │ │Weaviate)  │ │           │
└──────────┘  └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### Microservices Breakdown

| Service | Responsibility |
|---------|---------------|
| **Lead Service** | CRUD, scoring, categorization, lifecycle management |
| **Outreach Service** | Message generation, channel routing, sequence orchestration |
| **Analytics Service** | Dashboards, reports, forecasting, funnel analysis |
| **AI Engine** | GPT orchestration, agent workflows, ML model serving |
| **Webhook Service** | Inbound event processing, delivery tracking |
| **Scraper Fleet** | Distributed scraping workers, proxy management, anti-bot evasion |
| **Notification Service** | Real-time alerts, push notifications, in-app messaging |
| **Integration Service** | CRM sync, Zapier, third-party data providers |
| **Auth & Billing** | SSO, RBAC, subscription management, usage metering |

---

## Revenue Model

### Pricing Tiers

| Tier | Price/mo | Leads | Channels | AI Credits | Target |
|------|----------|-------|----------|-----------|--------|
| **Free** | $0 | 50 | Email only | 10 analyses | Solo freelancers |
| **Starter** | $49 | 500 | Email + WhatsApp | 100 analyses | Small agencies |
| **Growth** | $149 | 2,500 | All channels | 500 analyses | Growing teams |
| **Business** | $399 | 10,000 | All + API | 2,000 analyses | Mid-market |
| **Enterprise** | Custom | Unlimited | All + white-label | Unlimited | Large orgs |

### Revenue Multipliers

| Stream | Description |
|--------|-------------|
| **Usage-Based AI** | $0.05 per AI analysis beyond plan limits |
| **Data Credits** | $0.10 per enriched lead from premium sources |
| **Marketplace** | 30% revenue share on third-party integrations |
| **Professional Services** | Implementation, custom integrations, training |
| **White-Label Licensing** | Annual license fee for resellers |

### Path to $1B ARR

```
Year 1:  1,000 customers × $150 avg/mo = $1.8M ARR (Product-market fit)
Year 2:  10,000 customers × $200 avg/mo = $24M ARR (Geographic expansion)
Year 3:  50,000 customers × $250 avg/mo = $150M ARR (Platform + marketplace)
Year 4:  150,000 customers × $300 avg/mo = $540M ARR (Enterprise + verticals)
Year 5:  250,000 customers × $400 avg/mo = $1.2B ARR (Autonomous AI dominance)
```

---

## Competitive Moats

| Moat | Description |
|------|-------------|
| **AI Flywheel** | More customers → more conversion data → better scoring models → higher conversion → more customers |
| **Data Network Effect** | Aggregated lead intelligence across all customers improves quality for everyone |
| **Channel Lock-in** | WhatsApp Business API verification, email domain reputation, LinkedIn connections |
| **Vertical Depth** | Industry-specific scoring models and templates that improve with usage |
| **Self-Hosted Bridge** | WhatsApp outreach without expensive official API — cost advantage |
| **Multi-Tenant Scale** | Shared infrastructure reduces per-customer cost as platform grows |

---

## Key Metrics to Track

| Category | Metrics |
|----------|---------|
| **Growth** | MRR, customer count, lead volume processed, DAU/MAU |
| **Engagement** | Messages sent/day, response rate, sequences completed |
| **AI Quality** | Scoring accuracy (predicted vs actual conversion), outreach reply rate |
| **Efficiency** | Cost per lead analyzed, cost per message sent, infrastructure cost per customer |
| **Revenue** | ARPU, LTV, CAC, LTV:CAC ratio, net revenue retention |
| **Platform** | API calls/day, integrations activated, marketplace GMV |

---

## Immediate Next Steps (Sprint 1)

1. **Fix scraper reliability** — Add proxy rotation, implement retry logic with exponential backoff
2. **Complete test coverage** — Unit tests for all services, integration tests for API endpoints
3. **Production observability** — Prometheus metrics, Grafana dashboards, structured JSON logging
4. **Frontend completion** — Messages page with conversation view, Settings with integration config
5. **LinkedIn integration** — Browser automation for message sending
6. **Celery Beat schedules** — Auto-analyze new leads every 6 hours, weekly pipeline reports
7. **Rate limiting** — Redis-based rate limiting on all public endpoints
8. **Email tracking** — SendGrid/SES integration with open/click tracking pixels
9. **Provision VPS** — Set up Oracle Cloud Free Tier VM, add GitHub secrets for auto-deploy

---

## CI/CD Pipeline (Proven & Automated)

### Architecture

```
GitHub Push (main)
    ↓
┌─────────────────┐
│  CI (ci.yml)    │  ← Every push/PR — tests backend, builds frontend + brand site
│  Test & Build   │
└────────┬────────┘
         ↓ (on push to main)
┌─────────────────┐
│ Deploy (deploy.yml) │
│                    │
│  Job 1: Docker     │  → Build & push images to ghcr.io/github_org/repo
│  Job 2: Brand Site │  → `wrangler pages deploy` → getparakram.in (Cloudflare Pages)
│  Job 3: VPS (opt)  │  → SSH into Oracle Cloud VM → docker compose pull && up -d
└────────────────────┘
```

### Workflows

| File | Trigger | What it does | Status |
|------|---------|-------------|--------|
| `.github/workflows/ci.yml` | push/PR to main, push to develop | Backend tests (pytest, 33/33 pass), Frontend build (Next.js), Brand site build (Vite) | ✅ Proven |
| `.github/workflows/deploy.yml` | push to main | Docker images → ghcr.io, Brand site → Cloudflare Pages, VPS deploy (if VPS_ENABLED=true) | ✅ Proven |

### Required GitHub Secrets

| Secret | Used By | Description |
|--------|---------|-------------|
| `CLOUDFLARE_API_TOKEN` | CI (brand-site job) | Cloudflare API token with Workers/Pages write access for deploying brand site |
| `VPS_HOST` | Deploy (deploy-vps job) | Oracle Cloud VPS public IP (e.g., `146.56.xxx.xxx`) |
| `VPS_USER` | Deploy (deploy-vps job) | SSH username (e.g., `ubuntu`, `opc`) |
| `VPS_SSH_KEY` | Deploy (deploy-vps job) | SSH private key for VPS access |
| `VPS_PORT` (optional) | Deploy (deploy-vps job) | SSH port (default `22`) |

### Required GitHub Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `VPS_ENABLED` | Deploy (deploy-vps job) | Set to `true` to enable VPS auto-deploy after VPS is provisioned |
| `PUBLIC_API_URL` | Deploy (docker job) | Public API URL for frontend build arg (default: `https://leads.getparakram.in/api/v1`) |

### How to provision Oracle Cloud VPS for auto-deploy

```bash
# 1. Launch Oracle Cloud Free Tier VM (Ubuntu 22.04, 4 OCPU, 24GB RAM)
# 2. Install Docker + deps
ssh ubuntu@<VPS_IP>
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER

# 3. Clone repo
git clone https://github.com/<org>/sigma-lead-intelligence.git /opt/sigma-lead-intelligence

# 4. Create .env file, set DB_PASSWORD, SECRET_KEY, etc.
nano /opt/sigma-lead-intelligence/.env

# 5. Set GitHub secrets in repo Settings → Secrets and variables → Actions
# VPS_HOST, VPS_USER (ubuntu), VPS_SSH_KEY (private key)
# Set VPS_ENABLED = true in Variables

# 6. Push to main → deploy.yml runs → images pull → containers start
```

### How to build and deploy locally (for testing)

```bash
# Full stack (Docker Compose)
docker compose -f docker-compose.prod.yml up -d --build

# Frontend only (dev mode)
cd frontend && npm run dev

# Backend only (dev mode)
cd backend && uvicorn app.main:app --reload --port 8000

# Brand site (dev mode)
cd "Design Parakram Ecosystem Website (1)" && pnpm dev

# Brand site build check (same as CI)
pnpm build

# Frontend build check (same as CI)
npm run build

# Backend tests (same as CI)
pytest -v --tb=short --ignore=tests/test_intelligence_api.py
```

### Container Registry

All Docker images are stored in **GitHub Container Registry (ghcr.io)** — no separate Docker Hub account needed. The `GITHUB_TOKEN` secret is automatically available in workflows.

Images are tagged with:
- `latest` — most recent push to main
- `<commit-sha>` — specific commit (for rollback)

### Brand Site Deployment

The brand site (`getparakram.in`) is a Vite/vanilla-js site under `Design Parakram Ecosystem Website (1)/`. It is deployed to Cloudflare Pages via the `deploy.yml` workflow on push to main. The live site is at `https://getparakram.in`.

CI/CD is handled via:
- `wrangler pages deploy ./dist --project-name parakram --branch main`

The domain `getparakram.in` was added to Cloudflare Pages via:
```bash
npx wrangler pages domain add parakram getparakram.in
```

### Known Working Commands (from local testing)

```bash
# All verified on Windows 11 + Docker Desktop
docker compose build         # Builds all 8 containers
docker compose up -d         # Starts full stack at localhost:8080
npm run build                # Frontend builds in ~35s
pnpm build                   # Brand site builds in ~19s
pytest -v --tb=short         # 33/33 unit tests pass
```

---

## Technical Debt to Address

| Issue | Risk | Fix |
|-------|------|-----|
| No test suite | Ship broken code | pytest + coverage > 80% |
| Brittle Google Maps selectors | Scraper breaks on DOM change | Abstract selectors, add fallbacks |
| No rate limiting | API abuse | Redis sliding window limiter |
| Prometheus not integrated | Blind to issues | Add middleware metrics |
| AuditLog not wired | Compliance gaps | Middleware decorator for all mutations |
| LinkedIn channel incomplete | Lost revenue opportunity | Official API or Playwright automation |
| ~No CI/CD pipeline~ | ~Manual deploys~ | ✅ **Solved** — GitHub Actions → ghcr.io + Cloudflare Pages + VPS |
| No backup strategy | Data loss risk | pg_dump cron + S3 upload |
| JWT 24h expiry, no refresh | Poor UX | Add refresh token rotation |
| CORS localhost only | Can't deploy frontend separately | Environment-based CORS origins |

---

*This document is a living roadmap. Updated as the product evolves toward market dominance.*
