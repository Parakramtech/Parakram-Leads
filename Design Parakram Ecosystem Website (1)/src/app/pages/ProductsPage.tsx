"use client";

import SectionLabel from "../components/SectionLabel";
import Panel from "../components/Panel";
import Scanlines from "../components/Scanlines";
import { type Page } from "../types";
import { Cpu, BarChart3, Microscope, Check, MessageCircle, ArrowRight } from "lucide-react";

function navTo(setPage: (p: Page) => void, p: Page) { setPage(p); window.scrollTo({ top: 0, behavior: "instant" }); }

function ProductsPage({ setPage }: { setPage: (p: Page) => void }) {
  const go = (p: Page) => navTo(setPage, p);

  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16">
          <SectionLabel>Parakram Products</SectionLabel>
          <h1 className="text-[40px] md:text-[52px] font-semibold text-[#e8e6e3] tracking-[-0.025em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>Our own software.</h1>
          <p className="text-[15px] text-[#5a5a5a] max-w-lg leading-relaxed">Beyond client work, we build independent products. <span className="text-[#c9a96e]">Parakram Leads is LIVE.</span> Try it now at <a href="https://leads.getparakram.in" target="_blank" rel="noopener noreferrer" className="text-[#c9a96e] underline hover:text-[#f5e4a8]">leads.getparakram.in</a>.</p>
        </div>

        <div className="font-mono text-[11px] text-[#c9a96e]/30 mb-8 border-b border-white/[0.04] pb-4">
          PARAKRAM_ECOSYSTEM_BOOTLOADER v1.0.0 — INITIALIZING...
        </div>

        {/* Parakram Edge */}
        <Panel title="product.edge" className="p-10 mb-6">
          <Scanlines />
          <div className="relative z-10 grid md:grid-cols-[1fr_200px] gap-10 items-start">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <Cpu size={22} className="text-[#c9a96e]" />
                <div>
                  <p className="text-[9px] font-mono text-[#c9a96e]/50 uppercase tracking-[0.2em]">Mobile Edge Computing</p>
                  <h2 className="text-[24px] font-semibold text-[#e8e6e3]" style={{ fontFamily: "Sora, sans-serif" }}>Parakram Edge</h2>
                </div>
              </div>
              <p className="text-[14px] text-[#6a6a6a] leading-relaxed mb-6 max-w-2xl">
                A high-performance, localized edge-computing server running natively on Android. Parakram Edge transforms your mobile phone into an asynchronous hardware extension and secure telemetry proxy for desktop AI agents, developers, and remote orchestration workflows.
              </p>
              <p className="text-[13px] text-[#5a5a5a] leading-relaxed mb-6 max-w-2xl">
                By exposing a secure local REST API, Parakram Edge enables desktop agents to interact with on-device hardware sensors, local filesystems, real-time terminals, and mobile battery states — without sacrificing privacy or relying on heavy cloud infrastructure.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                {[
                  { label: "Secure REST API", desc: "Local network, authenticated" },
                  { label: "Sensor Access", desc: "GPS, camera, accelerometer" },
                  { label: "AI Agent Bridge", desc: "Works with any desktop agent" },
                  { label: "Privacy-First", desc: "Zero cloud dependency" },
                ].map(({ label, desc }) => (
                  <div key={label} className="border border-white/[0.05] p-3">
                    <p className="text-[11px] font-semibold text-[#c9a96e]/80 mb-1">{label}</p>
                    <p className="text-[10px] text-[#3a3a3a]">{desc}</p>
                  </div>
                ))}
              </div>
              <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer">
                <button className="flex items-center gap-2 px-6 py-2.5 text-[12px] font-mono text-[#25D366] border border-[#25D366]/30 hover:bg-[#25D366]/[0.05] transition-colors"><MessageCircle size={13} /> Get Early Access</button>
              </a>
            </div>
            <div className="flex flex-col gap-3">
              <div className="border border-white/[0.05] p-4 text-center">
                <p className="text-[9px] font-mono text-[#2a2a2a] uppercase mb-1">Status</p>
                <div className="flex items-center justify-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-[#c9a96e]" style={{ boxShadow: "0 0 6px rgba(201,169,110,0.8)" }} /><span className="text-[12px] font-mono text-[#c9a96e]">Building</span></div>
              </div>
              <div className="border border-white/[0.05] p-4">
                <p className="text-[9px] font-mono text-[#2a2a2a] uppercase mb-2">Progress</p>
                <div className="h-[4px] bg-white/[0.04]"><div className="h-full" style={{ width: "72%", background: "linear-gradient(90deg,#7a5020,#c9a96e)" }} /></div>
                <p className="text-[10px] font-mono text-[#c9a96e] mt-1">72%</p>
              </div>
              <div className="border border-white/[0.05] p-4">
                <p className="text-[9px] font-mono text-[#2a2a2a] uppercase mb-2">Platform</p>
                <p className="text-[12px] text-[#5a5a5a]">Android 10+</p>
              </div>
            </div>
          </div>
        </Panel>

        {/* Parakram Leads */}
        <Panel title="product.leads" className="p-10 mb-6">
          <Scanlines />
          <div className="relative z-10 grid md:grid-cols-[1fr_200px] gap-10 items-start">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <BarChart3 size={22} className="text-[#c9a96e]" />
                <div>
                  <p className="text-[9px] font-mono text-[#c9a96e]/50 uppercase tracking-[0.2em]">AI Lead Intelligence</p>
                  <h2 className="text-[24px] font-semibold text-[#e8e6e3]" style={{ fontFamily: "Sora, sans-serif" }}>Parakram Leads</h2>
                </div>
              </div>
              <p className="text-[14px] text-[#6a6a6a] leading-relaxed mb-4 max-w-2xl">
                7 out of 10 Indian SMBs have no digital presence. No website. No SSL. No Google Business Profile. They exist on JustDial and Google Maps — invisible, unreachable, losing customers daily. Parakram Leads finds them, scores their gaps, and lets you sell them the solution automatically.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-6">
                {[
                  { f: "Lead Discovery", d: "Scrapes Google Maps, JustDial, DuckDuckGo — finds every local business without a website" },
                  { f: "Digital Gap Analysis", d: "13-point audit (SSL, mobile, forms, analytics, CRM, booking) → Digital Maturity Score 0–100" },
                  { f: "Opportunity Scoring", d: "Converts digital gaps into project value — 'needs website + SSL = ₹15,000 project'" },
                  { f: "AI Outreach", d: "Personalized WhatsApp, Email, LinkedIn messages per industry — AI or deterministic templates" },
                  { f: "Multi-Channel Sending", d: "WhatsApp (official API + Baileys), Email (SMTP), LinkedIn (Playwright)" },
                  { f: "Predictive Intelligence", d: "5-dimension scoring: identifies HOT / WARM / COLD leads automatically" },
                ].map(({ f, d }) => (
                  <div key={f} className="border border-white/[0.05] p-3">
                    <p className="text-[11px] font-semibold text-[#c9a96e]/80 mb-1">{f}</p>
                    <p className="text-[10px] text-[#3a3a3a] leading-relaxed">{d}</p>
                  </div>
                ))}
              </div>
              <p className="text-[12px] font-mono text-[#c9a96e]/50 mb-4">Free tier available. Upgrade for more leads and channels.</p>
              <div className="flex items-center gap-3 flex-wrap">
                <a href="https://leads.getparakram.in" target="_blank" rel="noopener noreferrer">
                  <button className="flex items-center gap-2 px-6 py-2.5 text-[12px] font-semibold tracking-[0.04em]" style={{ background: "linear-gradient(135deg,#b8903a,#d4b060,#f5e4a8,#c9a96e)", color: "#1a0f00" }}><BarChart3 size={13} /> Launch App</button>
                </a>
                <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer">
                  <button className="flex items-center gap-2 px-6 py-2.5 text-[12px] font-mono text-[#25D366] border border-[#25D366]/30 hover:bg-[#25D366]/[0.05] transition-colors"><MessageCircle size={13} /> WhatsApp Us</button>
                </a>
              </div>
            </div>
            <div className="flex flex-col gap-3">
              <div className="border border-white/[0.05] p-4 text-center">
                <div className="flex items-center justify-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-[#22c55e]" style={{ boxShadow: "0 0 6px rgba(34,197,94,0.8)" }} /><span className="text-[12px] font-mono text-[#22c55e]">LIVE</span></div>
              </div>
              <div className="border border-white/[0.05] p-4">
                <div className="h-[4px] bg-white/[0.04]"><div className="h-full" style={{ width: "100%", background: "linear-gradient(90deg,#7a5020,#c9a96e)" }} /></div>
                <p className="text-[10px] font-mono text-[#c9a96e] mt-1">100% — v0.2.1</p>
              </div>
              <div className="border border-white/[0.05] p-4">
                <p className="text-[9px] font-mono text-[#2a2a2a] uppercase mb-1">Target</p>
                <p className="text-[12px] text-[#5a5a5a]">Indian SMBs</p>
              </div>
              <a href="https://leads.getparakram.in" target="_blank" rel="noopener noreferrer">
                <div className="border border-[#22c55e]/30 p-3 text-center hover:bg-[#22c55e]/[0.04] transition-colors cursor-pointer">
                  <p className="text-[9px] font-mono text-[#22c55e]/70 uppercase tracking-[0.15em]">Visit →</p>
                  <p className="text-[10px] font-mono text-[#22c55e]">leads.getparakram.in</p>
                </div>
              </a>
            </div>
          </div>
        </Panel>

        {/* Parakram Research */}
        <Panel title="product.research" className="p-10">
          <Scanlines />
          <div className="relative z-10 grid md:grid-cols-[1fr_200px] gap-10 items-start">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <Microscope size={22} className="text-[#c9a96e]" />
                <div>
                  <p className="text-[9px] font-mono text-[#c9a96e]/50 uppercase tracking-[0.2em]">Research Automation</p>
                  <h2 className="text-[24px] font-semibold text-[#e8e6e3]" style={{ fontFamily: "Sora, sans-serif" }}>Parakram Research</h2>
                </div>
              </div>
              <p className="text-[14px] text-[#6a6a6a] leading-relaxed mb-6 max-w-2xl">
                A tool for academic and professional research automation. Parakram Research scrapes hundreds of papers from arXiv, PubMed, Semantic Scholar, and other sources, builds a structured searchable database, and uses AI to extract summaries, identify trends, compare findings, and generate literature review drafts.
              </p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-6">
                {["Multi-source paper scraping", "AI-powered summarization", "Citation network mapping", "Searchable database", "Trend detection", "Literature review generation"].map(f => (
                  <div key={f} className="flex items-center gap-2 border border-white/[0.05] p-3">
                    <Check size={10} className="text-[#c9a96e] flex-shrink-0" />
                    <span className="text-[11px] text-[#5a5a5a]">{f}</span>
                  </div>
                ))}
              </div>
              <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer">
                <button className="flex items-center gap-2 px-6 py-2.5 text-[12px] font-mono text-[#25D366] border border-[#25D366]/30 hover:bg-[#25D366]/[0.05] transition-colors"><MessageCircle size={13} /> Get Early Access</button>
              </a>
            </div>
            <div className="flex flex-col gap-3">
              <div className="border border-white/[0.05] p-4 text-center">
                <div className="flex items-center justify-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-[#3a3a3a]" /><span className="text-[12px] font-mono text-[#3a3a3a]">R&D</span></div>
              </div>
              <div className="border border-white/[0.05] p-4">
                <div className="h-[4px] bg-white/[0.04]"><div className="h-full" style={{ width: "35%", background: "linear-gradient(90deg,#7a5020,#c9a96e)" }} /></div>
                <p className="text-[10px] font-mono text-[#c9a96e] mt-1">35%</p>
              </div>
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}

export default ProductsPage;
