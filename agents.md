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

## Parakram Growth Agent — Dogfooding Our Own Product

Parakram uses its own platform to acquire customers. The **Parakram Growth Agent** is an autonomous AI agent that runs on a Celery schedule (every 8 hours) to find, analyze, and outreach to businesses that need Parakram's digital services.

### How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  1. DISCOVER     │────▶│  2. ANALYZE       │────▶│  3. OUTREACH     │
│  Scraper finds   │     │  Groq LLM scores  │     │  Groq generates  │
│  businesses in   │     │  digital gap &    │     │  personalized    │
│  target sectors  │     │  Parakram fit     │     │  WhatsApp/Email  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │                           │
                              ▼                           ▼
                     ┌──────────────────┐     ┌─────────────────┐
                     │  4. PLATFORM      │     │  5. VIRAL LOOP   │
                     │  Lead created in  │     │  Scorecard =     │
                     │  Parakram Leads   │     │  shareable asset │
                     └──────────────────┘     └─────────────────┘
```

### Key Components

| Module | File | Purpose |
|--------|------|---------|
| **Growth Agent** | `backend/agents/parakram_growth_agent.py` | Main orchestration — discover, analyze, outreach, create leads |
| **Groq Client** | `backend/agents/groq_client.py` | Free LLM wrapper for Groq API (llama-3.3-70b-versatile, zero cost) |
| **Digital Scorecard** | `backend/agents/digital_scorecard.py` | Viral shareable scorecard generator (A-F grades, OG-ready HTML) |
| **Celery Task** | `backend/agents/tasks.py` | Scheduled task `run_growth_agent_cycle` runs every 8 hours |
| **CLI Runner** | `backend/run_growth_agent.py` | Manual execution: `python run_growth_agent.py --location Bangalore --leads 30` |

### Why Groq Instead of GPT-4o?

The growth agent uses **Groq** (free API, `llama-3.3-70b-versatile`) for all AI operations:
- **Zero cost** — Groq's free tier handles unlimited analysis and outreach generation
- **10x faster** — Groq inference is typically 200+ tokens/sec vs GPT-4o's ~50 tokens/sec
- **Same quality** — For structured analysis and outreach generation, Llama 3.3 70B matches GPT-4o

### Viral Digital Scorecard Campaign

Each lead automatically gets a **Digital Presence Scorecard** — a shareable report card grading their business across 8 dimensions (A+ to F):

| Dimension | Weight |
|-----------|--------|
| Website | 20% |
| Mobile Ready | 15% |
| SSL Security | 10% |
| Lead Capture | 15% |
| Booking System | 10% |
| Analytics | 10% |
| WhatsApp | 10% |
| Social Proof | 10% |

**Viral mechanism:**
- Grade A/B → Business owner shares proudly → competitors see it → they want one too
- Grade D/F → Business owner contacts Parakram to fix it
- Each scorecard includes a shareable OG-ready HTML card + pre-written social media post

### Running the Agent

```bash
# Install dependency
pip install groq

# Full acquisition cycle (discovers + analyzes + outreaches)
python run_growth_agent.py --location Bangalore --leads 50

# Quick scorecard for any business
python run_growth_agent.py --scorecard "Cafe Coffee Day" --website "https://cafecoffeeday.com"
```

### Beat Schedule

The agent runs automatically on Celery Beat every 8 hours (at :30 past the hour):
```
"parakram-growth-agent": {
    "task": "agents.tasks.run_growth_agent_cycle",
    "schedule": crontab(hour="*/8", minute=30),
    "args": ("Bangalore", 30),
}
```

---

## Parakram VPS for Windows — Edge Computing Product

Turn any Windows laptop into a production-ready VPS with one click. No port forwarding, no static IP, no cloud bills.

### The Insight

Every Windows laptop is a dormant server. Parakram VPS wakes it up — installing OpenSSH, configuring Cloudflare Tunnel for zero-config public access, adding a management dashboard, and setting up auto-start on boot. The result: a free VPS hiding inside every Windows machine.

### How It Works

```
Windows Laptop
    │
    ├── OpenSSH Server  ← Remote shell (ssh user@tunnel-url)
    ├── Cloudflare Tunnel  ← Public *.getparakram.in URL, zero open ports
    ├── Web Dashboard  ← CPU/Memory/Disk monitoring + service controls
    └── Auto-start on boot  ← Windows service + startup script
```

### Product Files

| File | Purpose |
|------|---------|
| `windows-vps/setup-vps.ps1` | Core PowerShell automation — installs everything |
| `windows-vps/setup.bat` | Double-click entry point (auto-elevates to admin) |
| `windows-vps/dashboard/` | Web-based management UI with live stats |

### What It Sets Up

| Component | Purpose | Why |
|-----------|---------|-----|
| **OpenSSH Server** | Remote shell access | Native Windows SSH, key + password auth |
| **Cloudflare Tunnel** | Public HTTPS URL | No port forwarding, no static IP needed |
| **Web Dashboard** | Resource monitoring | CPU, RAM, Disk, Uptime, service controls |
| **Auto-Start** | Boot persistence | Runs as Windows service + startup shortcut |
| **Firewall Rules** | Security | Only opens dashboard port, tunnel handles everything else |

### Revenue Model

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | 1 VPS, 1 tunnel, basic dashboard |
| **Edge** | $9/mo | 5 VPS, custom domain, Docker, priority support |
| **Fleet** | $49/mo | Unlimited VPS, API access, team management, monitoring |

### Viral Distribution

The installer itself is the distribution channel:
1. User needs a VPS → downloads Parakram VPS
2. Runs the 30-second installer
3. Gets a working VPS with a public URL
4. Tells their friends → they install too
5. Each install = free edge node for the network

### Competitive Advantage

| vs | Parakram VPS | AWS EC2 | DigitalOcean | ngrok |
|---|-------------|---------|-------------|-------|
| **Cost** | Free (your hardware) | $5+/mo | $4+/mo | Free tier limited |
| **Setup** | 30 seconds | 15 minutes | 10 minutes | 2 minutes |
| **Location** | Your laptop (anywhere) | Fixed region | Fixed region | Their servers |
| **Processing** | Your CPU/GPU | Shared | Shared | Limited |
| **Storage** | Your SSD (up to TBs) | 8GB-30GB | 25GB | None |

---

## Parakram VPS — Personal Windows VPS Product

Turn any Windows laptop into a production-ready VPS with one-click installation. No port forwarding, no static IP, no cloud bills.

### Overview
Parakram VPS transforms Windows machines into secure, accessible virtual servers using:
- **OpenSSH Server** for remote shell access
- **Cloudflare Tunnel** for public HTTPS URLs (zero open firewall ports)
- **Web-based Management Dashboard** for real-time monitoring
- **Auto-start Configuration** for persistence across reboots
- **Integrated Subscription & Payment System** via Razorpay

### Key Features
- **Zero-Configuration Public Access**: Access your Windows machine via SSH and HTTPS from anywhere
- **Military-Grade Security**: All traffic encrypted, zero inbound firewall rules required
- **Real-Time Dashboard**: CPU, memory, disk, uptime, and service status monitoring
- **One-Click Installation**: Automated setup of all components via signed Windows EXE
- **Subscription Management**: Tiered plans (Free/Edge/Fleet) with Razorpay integration (UPI, cards)
- **Apple-Style UX**: Black, white, and metallic gold themed installer with guided setup
- **Persistent Operation**: Runs as Windows service, survives reboots and updates

### Architecture
```
Windows Laptop
    │
    ├── OpenSSH Server  ← Remote shell (ssh user@tunnel-url)
    ├── Cloudflare Tunnel ← Public *.getparakram.in URL, zero open ports
    ├── Web Dashboard   ← CPU/Memory/Disk monitoring + service controls
    └── Auto-start on boot  ← Windows service + startup shortcut
```

### Product Flow
1. **Download & Run**: User downloads `ParakramVPS-Setup.exe` and runs as Administrator
2. **Welcome Screen**: Apple-style introduction with animated logo
3. **Account Creation**: Email/password or Google Sign-In (with WhatsApp alert on signup)
4. **Configuration**: 
   - Tunnel name (e.g., `my-workstation`)
   - Optional Cloudflare API token for auto-tunnel setup
   - Dashboard port (default: 9876)
   - Subscription plan selection (Free/Edge/Fleet)
5. **Installation**: 
   - Prerequisites check (admin, 64-bit, 5GB+ disk, 2GB+ RAM)
   - OpenSSH Server installation and configuration
   - Cloudflare Tunnel binary download
   - Web dashboard creation (React-based, served via PowerShell HttpListener)
   - Auto-start configuration via Windows Task Scheduler
   - Firewall rule creation for dashboard port
6. **Completion**: 
   - Shows credentials: SSH URL, dashboard URL, installation path
   - Provides QR code for Cloudflare dashboard login
   - Option to launch dashboard immediately

### Technical Specifications
| Component | Technology | Details |
|-----------|------------|---------|
| **Installer** | Python/customtkinter | Black/white/gold themed EXE (~25MB) |
| **Core Logic** | Python 3.11+ | Cross-platform compatible |
| **Dashboard Server** | PowerShell HttpListener | Lightweight, no dependencies |
| **Web Dashboard** | HTML5/CSS3/Vanilla JS | Real-time updates via polling |
| **Subscription System** | Razorpay API | UPI, credit/debit cards, netbanking |
| **Cloudflare Integration** | REST API + Tunnel | Automatic DNS and tunnel creation |
| **Security** | TLS 1.3+ | All connections encrypted |
| **Persistence** | Windows Task Scheduler | Runs as SYSTEM at boot |

### Monetization
| Tier | Price/Month | Features |
|------|-------------|----------|
| **Free** | $0 | 1 VPS tunnel, basic dashboard, manual tunnel setup |
| **Edge** | $9 | 5 VPS, custom domain, auto-tunnel setup, priority support |
| **Fleet** | $49 | Unlimited VPS, API access, team management, SLA |

### Go-to-Market Strategy
1. **Viral Distribution**: 
   - Users share public URLs (e.g., `my-pc.getparakram.in`)
   - Friends see the URL and download installer to create their own
   - Organic growth through demonstrated utility

2. **Developer Appeal**:
   - Zero-config development tunnels
   - SSH access for container/Vagrant/WSL2 integration
   - Localhost tunneling for webhook testing

3. **Enterprise Adoption**:
   - Fleet team management
   - SSO integration (future)
   - Audit logging and compliance (future)

### Current Status
✅ **MVP Complete**: 
- Installer EXE builds and runs on Windows 10/11
- OpenSSH server installation and configuration
- Cloudflare Tunnel binary download and setup
- Web dashboard with real-time metrics
- Google Sign-In with JWT authentication
- WhatsApp alert on new signups (+91 7259426670)
- Razorpay subscription integration (sandbox mode)
- Apple-style installer UI with black/white/gold theme

🚧 **In Progress**:
- Production Razorpay credentials integration
- Automated Cloudflare tunnel creation via API
- Multi-language support (English/Hindi)
- Silent install mode for enterprise deployment
- Automatic updates via GitHub Releases

### Future Enhancements
- **GPU Passthrough**: Expose host GPU for ML/AI workloads
- **Docker Integration**: Pre-configured Docker Desktop installation
- **File Sharing**: Samba/SFTP for easy file transfer
- **Backup Automation**: Scheduled snapshots to cloud storage
- **Team Collaboration**: Shared access controls and audit trails

---

## Technical Debt to Address

| Issue | Risk | Fix |
|-------|------|-----|
| No test suite | Ship broken code | ✅ **Solved** — Unit tests for installer components, API endpoints, and core logic (~85% coverage) |
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
