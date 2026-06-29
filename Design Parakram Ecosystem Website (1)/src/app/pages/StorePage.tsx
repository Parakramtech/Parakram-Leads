"use client";

import SectionLabel from "../components/SectionLabel";
import Panel from "../components/Panel";
import Scanlines from "../components/Scanlines";
import GoldButton from "../components/GoldButton";
import { type Page } from "../types";
import { Cpu, BarChart3, Microscope, Laptop, Check, ArrowRight, MessageCircle, Shield, FileText, Gamepad2, LayoutTemplate } from "lucide-react";

function navTo(setPage: (p: Page) => void, p: Page) { setPage(p); window.scrollTo({ top: 0, behavior: "instant" }); }

const CATEGORIES = [
  { id: "saas", label: "SaaS Products" },
  { id: "infra", label: "Infrastructure" },
  { id: "mobile", label: "Mobile Apps" },
  { id: "tools", label: "Tools & Templates" },
  { id: "fun", label: "Fun Stuff" },
];

const PRODUCTS = [
  // === SAAS ===
  {
    category: "saas",
    id: "leads",
    name: "Parakram Leads",
    tagline: "AI Lead Intelligence Platform",
    icon: BarChart3,
    status: "LIVE",
    statusColor: "#22c55e",
    statusGlow: "rgba(34,197,94,0.8)",
    description: "Find Indian SMBs without digital presence. AI-scans their gaps (no website, no SSL, no mobile site), scores each lead HOT/WARM/COLD, and sends personalized WhatsApp/Email/LinkedIn outreach automatically.",
    href: "https://leads.getparakram.in",
    features: ["Google Maps + JustDial scraping", "13-point digital maturity audit", "AI outreach generation", "Multi-channel sending", "Response tracking"],
    tiers: [
      { name: "Free", price: "$0", features: { Leads: "50/mo", Channels: "Email only", AI: "10 analyses" }, target: "Solo freelancers" },
      { name: "Starter", price: "$49", features: { Leads: "500/mo", Channels: "Email + WhatsApp", AI: "100 analyses" }, target: "Small agencies" },
      { name: "Growth", price: "$149", features: { Leads: "2,500/mo", Channels: "All channels", AI: "500 analyses" }, target: "Growing teams" },
      { name: "Business", price: "$399", features: { Leads: "10,000/mo", Channels: "All + API", AI: "2,000 analyses" }, target: "Mid-market" },
    ],
  },
  {
    category: "saas",
    id: "research",
    name: "Parakram Research",
    tagline: "Research Automation",
    icon: Microscope,
    status: "R&D",
    statusColor: "#3a3a3a",
    statusGlow: "transparent",
    description: "Automates academic research across arXiv, PubMed, Semantic Scholar. AI extracts summaries, identifies trends, maps citation networks, and generates literature review drafts.",
    href: "#",
    features: ["Multi-source paper scraping", "AI-powered summarization", "Citation network mapping", "Trend detection", "Lit review generation"],
    tiers: [
      { name: "Early Access", price: "$0", features: { Papers: "100/mo", Sources: "3 repositories", AI: "50 summaries" }, target: "Researchers" },
      { name: "Scholar", price: "$19", features: { Papers: "1,000/mo", Sources: "All + custom", AI: "500 summaries" }, target: "PhD students" },
      { name: "Institution", price: "$99", features: { Papers: "Unlimited", Sources: "All + API", AI: "Unlimited" }, target: "Universities" },
    ],
  },

  // === INFRASTRUCTURE ===
  {
    category: "infra",
    id: "vps",
    name: "Parakram VPS",
    tagline: "Windows → VPS in 30 Seconds",
    icon: Laptop,
    status: "BETA",
    statusColor: "#c9a96e",
    statusGlow: "rgba(201,169,110,0.8)",
    description: "Turn any Windows laptop into a production-ready VPS with one click. Installs OpenSSH, Cloudflare Tunnel (public URL), web dashboard, and auto-start on boot. Zero cloud bills, zero port forwarding.",
    href: "#",
    features: ["One-click installer", "Cloudflare Tunnel (public URL)", "Web dashboard (CPU/RAM/Disk)", "OpenSSH remote shell", "Auto-start on boot"],
    tiers: [
      { name: "Free", price: "$0", features: { VPS: "1 node", Tunnel: "Manual setup", Dashboard: "Basic" }, target: "Solo devs" },
      { name: "Edge", price: "$9", features: { VPS: "5 nodes", Tunnel: "Auto setup", Dashboard: "Full + Docker" }, target: "Power users" },
      { name: "Fleet", price: "$49", features: { VPS: "Unlimited", Tunnel: "Custom domains", Dashboard: "Team + API" }, target: "Enterprises" },
    ],
  },
  {
    category: "infra",
    id: "whatsapp-bridge",
    name: "WhatsApp Bridge",
    tagline: "Self-Hosted WhatsApp API",
    icon: MessageCircle,
    status: "BETA",
    statusColor: "#25D366",
    statusGlow: "rgba(37,211,102,0.8)",
    description: "A self-hosted WhatsApp Web bridge powered by Baileys. No expensive Business API. Run unlimited WhatsApp sessions, send/receive messages, handle media — all from your own server.",
    href: "#",
    features: ["No WhatsApp Business API fees", "Multi-device protocol support", "Express REST API", "Media send/receive", "Dockerized (node:22-alpine)"],
    tiers: [
      { name: "Embedded", price: "$0", features: { Sessions: "Included with Leads", API: "REST + Webhook", Support: "Community" }, target: "Leads users" },
      { name: "Standalone", price: "$9", features: { Sessions: "1 session", API: "REST + Webhook", Support: "Email" }, target: "Developers" },
      { name: "Enterprise", price: "$99", features: { Sessions: "Unlimited", API: "Full + Dashboard", Support: "Priority + SLA" }, target: "Businesses" },
    ],
  },

  // === MOBILE ===
  {
    category: "mobile",
    id: "edge",
    name: "Parakram Edge",
    tagline: "Mobile Edge Computing for AI Agents",
    icon: Cpu,
    status: "BUILDING",
    statusColor: "#c9a96e",
    statusGlow: "rgba(201,169,110,0.8)",
    description: "Android app that turns your phone into a local edge server. Desktop AI agents connect over WiFi to access sensors (GPS, camera), filesystem, terminal — no cloud dependency, full privacy.",
    href: "#",
    features: ["Secure REST API on Android", "Sensor access (GPS, camera, accel)", "Local filesystem bridge", "Real-time terminal", "Zero cloud dependency"],
    tiers: [
      { name: "Beta", price: "$0", features: { Agents: "1 concurrent", Sensors: "GPS + accel", Terminal: "Read-only" }, target: "Early adopters" },
      { name: "Edge Pro", price: "$3", features: { Agents: "Unlimited", Sensors: "All", Terminal: "Full shell" }, target: "Power users" },
      { name: "Edge Cloud", price: "$9", features: { Access: "Remote over internet", Tunnel: "Cloudflare", Team: "Multi-device" }, target: "Teams" },
    ],
  },

  // === TOOLS & TEMPLATES ===
  {
    category: "tools",
    id: "scorecard",
    name: "Digital Scorecard",
    tagline: "Instant Business Audit Tool",
    icon: FileText,
    status: "BETA",
    statusColor: "#c9a96e",
    statusGlow: "rgba(201,169,110,0.8)",
    description: "Grade any business across 8 digital dimensions (Website, Mobile, SSL, Forms, Booking, Analytics, WhatsApp, Social) → A+ to F score. Generates shareable HTML cards with pre-written social media posts.",
    href: "#",
    features: ["8-dimension digital audit", "A+ to F grading", "Shareable OG-ready HTML card", "Pre-written social posts", "Competitor comparison"],
    tiers: [
      { name: "Free", price: "$0", features: { Audits: "5/mo", Reports: "Basic PDF", Branding: "Parakram logo" }, target: "SMB owners" },
      { name: "Pro", price: "$9", features: { Audits: "Unlimited", Reports: "HTML card + PDF", Branding: "White-label" }, target: "Agencies" },
      { name: "Bulk", price: "$99", features: { Audits: "1,000+", Reports: "Bulk export", API: "REST endpoint" }, target: "Enterprises" },
    ],
  },
  {
    category: "tools",
    id: "templates",
    name: "Template Store",
    tagline: "Website, WhatsApp & Marketing Templates",
    icon: LayoutTemplate,
    status: "BUILDING",
    statusColor: "#c9a96e",
    statusGlow: "rgba(201,169,110,0.8)",
    description: "Ready-to-use digital templates for SMBs and freelancers. Business websites, WhatsApp outreach scripts, lead magnets, pitch decks, social media kits, and GST invoice templates.",
    href: "#",
    features: ["Industry website templates", "WhatsApp message scripts (60+ industries)", "Lead magnet kits", "Pitch deck templates", "Social media Canva kits"],
    tiers: [
      { name: "Website", price: "$9", features: { Templates: "10 industry sites", Format: "HTML/CSS", Use: "Personal/commercial" }, target: "SMB owners" },
      { name: "WhatsApp Kit", price: "$3", features: { Scripts: "60+ industries", Format: "Copy-paste", Use: "Sales outreach" }, target: "Sales teams" },
      { name: "Full Bundle", price: "$29", features: { Includes: "All templates", Updates: "1 year", Support: "Email" }, target: "Agencies" },
    ],
  },

  // === FUN ===
  {
    category: "fun",
    id: "playground",
    name: "Parakram's Quest",
    tagline: "Retro Treasure-Hunting Snake Game",
    icon: Gamepad2,
    status: "LIVE",
    statusColor: "#22c55e",
    statusGlow: "rgba(34,197,94,0.8)",
    description: "An Easter egg on our brand site — explore the island, follow the hot/cold detector, dig for treasure. Built with React + Canvas. WASD to move, Space to dig. Watch out for snakes!",
    href: "#",
    features: ["Retro pixel-art aesthetic", "Hot/Cold proximity detector", "Treasure digging mechanic", "Snake collision = game over", "Built with React + Canvas"],
    tiers: [
      { name: "Free", price: "$0", features: { Access: "getparakram.in/play", HighScore: "Local only", Ads: "None" }, target: "Everyone" },
      { name: "Sponsor", price: "$99", features: { Access: "Custom branding", HighScore: "Weekly leaderboard", Ads: "Your logo in game" }, target: "Brands" },
    ],
  },
];

function StorePage({ setPage }: { setPage: (p: Page) => void }) {
  const go = (p: Page) => navTo(setPage, p);

  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16">
          <SectionLabel>Parakram Store</SectionLabel>
          <h1 className="text-[40px] md:text-[52px] font-semibold text-[#e8e6e3] tracking-[-0.025em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>Everything we build.</h1>
          <p className="text-[15px] text-[#5a5a5a] max-w-lg leading-relaxed">SaaS, infrastructure, mobile apps, templates, games — all from one studio. Buy once, deploy anywhere.</p>
        </div>

        <div className="font-mono text-[11px] text-[#c9a96e]/30 mb-8 border-b border-white/[0.04] pb-4">
          PARAKRAM_STORE v2.0.0 — PRODUCT_COUNT := {PRODUCTS.length}
        </div>

        {CATEGORIES.map((cat) => {
          const catProducts = PRODUCTS.filter((p) => p.category === cat.id);
          if (catProducts.length === 0) return null;
          return (
            <div key={cat.id} className="mb-12">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-px flex-1 bg-white/[0.04]" />
                <span className="text-[10px] font-mono text-[#c9a96e]/40 uppercase tracking-[0.25em]">{cat.label}</span>
                <div className="h-px flex-1 bg-white/[0.04]" />
              </div>

              {catProducts.map((product) => (
                <div key={product.id} className="mb-8">
                  <Panel title={`store.${product.id}`} className="p-8">
                    <Scanlines />
                    <div className="relative z-10">
                      <div className="flex items-start gap-4 mb-5">
                        <product.icon size={22} className="text-[#c9a96e] mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 flex-wrap mb-1">
                            <h2 className="text-[20px] font-semibold text-[#e8e6e3]" style={{ fontFamily: "Sora, sans-serif" }}>{product.name}</h2>
                            <div className="flex items-center gap-1.5 px-2.5 py-0.5 border" style={{ borderColor: `${product.statusColor}30`, color: product.statusColor }}>
                              <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: product.statusColor, boxShadow: `0 0 6px ${product.statusGlow}` }} />
                              <span className="text-[10px] font-mono">{product.status}</span>
                            </div>
                          </div>
                          <p className="text-[11px] text-[#c9a96e]/50 font-mono mb-2">{product.tagline}</p>
                          <p className="text-[13px] text-[#6a6a6a] leading-relaxed max-w-2xl">{product.description}</p>
                          <div className="flex flex-wrap gap-2 mt-3">
                            {product.features.map((f) => (
                              <span key={f} className="flex items-center gap-1 text-[10px] font-mono text-[#4a4a4a] border border-white/[0.05] px-2 py-0.5">
                                <Check size={8} className="text-[#c9a96e]" /> {f}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Pricing Tiers */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                        {product.tiers.map((tier) => (
                          <div key={tier.name} className="border border-white/[0.06] p-4 flex flex-col">
                            <p className="text-[10px] font-semibold text-[#c9a96e]/80 mb-1">{tier.name}</p>
                            <p className="text-[26px] font-semibold text-[#e8e6e3] mb-3" style={{ fontFamily: "Sora, sans-serif" }}>
                              {tier.price}<span className="text-[11px] text-[#5a5a5a] font-normal">{tier.price !== "$0" ? "/mo" : ""}</span>
                            </p>
                            <div className="flex flex-col gap-1.5 mb-4 flex-1">
                              {Object.entries(tier.features).map(([label, value]) => (
                                <div key={label} className="flex items-start gap-2">
                                  <Check size={9} className="text-[#c9a96e] mt-0.5 flex-shrink-0" />
                                  <div>
                                    <p className="text-[8px] text-[#2a2a2a] uppercase font-mono">{label}</p>
                                    <p className="text-[10px] text-[#5a5a5a]">{value}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                            <p className="text-[8px] font-mono text-[#3a3a3a] mb-3">{tier.target}</p>
                            <a href={product.status === "LIVE" && product.href !== "#" ? product.href : "https://wa.me/917259426670"} target="_blank" rel="noopener noreferrer">
                              <GoldButton className="w-full text-[10px] py-2">
                                {product.status === "LIVE" ? "Subscribe" : "Get Early Access"}
                              </GoldButton>
                            </a>
                          </div>
                        ))}
                      </div>

                      {product.href !== "#" && (
                        <a href={product.href} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 text-[10px] font-mono text-[#c9a96e]/50 hover:text-[#c9a96e] transition-colors">
                          Visit {product.name} <ArrowRight size={10} />
                        </a>
                      )}
                    </div>
                  </Panel>
                </div>
              ))}
            </div>
          );
        })}

        {/* Enterprise CTA */}
        <Panel title="store.enterprise" className="p-10 text-center">
          <Scanlines />
          <div className="relative z-10">
            <Shield size={28} className="text-[#c9a96e] mx-auto mb-3" />
            <h2 className="text-[18px] font-semibold text-[#e8e6e3] mb-2" style={{ fontFamily: "Sora, sans-serif" }}>Need a custom plan?</h2>
            <p className="text-[13px] text-[#5a5a5a] max-w-md mx-auto mb-4">Enterprise pricing, white-label licensing, custom integrations, dedicated support, SLA guarantees.</p>
            <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer">
              <button className="flex items-center gap-2 mx-auto px-6 py-2.5 text-[12px] font-mono text-[#25D366] border border-[#25D366]/30 hover:bg-[#25D366]/[0.05] transition-colors"><MessageCircle size={13} /> Talk to Sales</button>
            </a>
          </div>
        </Panel>
      </div>
    </div>
  );
}

export default StorePage;
