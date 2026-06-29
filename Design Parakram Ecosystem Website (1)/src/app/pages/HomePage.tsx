"use client";

import { motion } from "motion/react";

import SectionLabel from "../components/SectionLabel";
import GridBg from "../components/GridBg";
import Panel from "../components/Panel";
import Scanlines from "../components/Scanlines";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import {
  ArrowRight, ChevronRight, ExternalLink,
  Globe, Star, Smartphone, Bot, Cpu, Microscope,
  BarChart3, MessageCircle, Github, Linkedin, Mail,
} from "lucide-react";
import varshiniImg from "../../imports/varshini.png";
import { type Page } from "../types";

function navTo(setPage: (p: Page) => void, p: Page) { setPage(p); window.scrollTo({ top: 0, behavior: "instant" }); }

const SERVICES_PREVIEW = [
  { name: "Custom Websites", icon: Globe, desc: "Blazing-fast, beautifully crafted web experiences for businesses, agencies, and creators.", diff: "★★☆☆☆" },
  { name: "Portfolio Sites", icon: Star, desc: "Standout personal portfolios that get you noticed, hired, and remembered.", diff: "★☆☆☆☆" },
  { name: "Cross-Platform Apps", icon: Smartphone, desc: "Android, iOS, Windows — one codebase. ESC/POS, CRM, IoT integrations built in.", diff: "★★★★☆" },
  { name: "AI Agents & Workflows", icon: Bot, desc: "Intelligent automation, AI pipelines, WhatsApp triggers, and custom CRM workflows.", diff: "★★★★★" },
  { name: "IoT & Hardware", icon: Cpu, desc: "Full-stack IoT: sensor firmware, cloud dashboards, edge AI. Custom hardware design.", diff: "★★★★☆" },
  { name: "Research Automation", icon: Microscope, desc: "Automate systematic review, data scraping, PDF parsing, and publication-ready reports.", diff: "★★★☆☆" },
];

const CLIENT_SITES = [
  { domain: "cokakaalan.in", name: "Coka Kaalan", desc: "Full-featured business website with CMS, SEO optimization, and mobile-first design.", tag: "Web" },
  { domain: "vidyuthlabs.co.in", name: "Vidyuth Labs", desc: "Corporate site for a technology lab — clean, fast, and professional.", tag: "Web" },
  { domain: "pubrealty.in", name: "PubRealty", desc: "Real estate platform with property listings, search filters, and lead capture.", tag: "Web + App" },
  { domain: "leads.getparakram.in", name: "Parakram Leads", desc: "AI-powered B2B lead intelligence platform — live in production with 34K+ leads.", tag: "SaaS" },
];

function HomePage({ setPage }: { setPage: (p: Page) => void }) {
  const go = (p: Page) => navTo(setPage, p);

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
        <GridBg />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_40%_at_50%_46%,rgba(201,169,110,0.07),transparent_70%)]" />
        <div className="relative z-10 flex flex-col items-center text-center px-6 pt-20">
          <img src="/parakram_logo.png" alt="Parakram" className="w-40 h-40 object-contain" />
          <div className="flex items-center gap-3 mt-8 mb-6">
            <div className="w-10 h-px" style={{ background: "linear-gradient(90deg,transparent,rgba(201,169,110,0.5))" }} />
            <span className="text-[10px] tracking-[0.38em] text-[#c9a96e] uppercase font-mono">Digital Ecosystem</span>
            <div className="w-10 h-px" style={{ background: "linear-gradient(90deg,rgba(201,169,110,0.5),transparent)" }} />
          </div>
          <h1 className="text-[40px] md:text-[68px] font-semibold tracking-[-0.03em] text-[#e8e6e3] mb-5 leading-[1.04] max-w-[860px]" style={{ fontFamily: "Sora, sans-serif" }}>
            We Build{" "}
            <span className="text-transparent bg-clip-text" style={{ backgroundImage: "linear-gradient(125deg,#8a6030 0%,#c9a96e 30%,#f5e4a8 52%,#c9a96e 70%,#7a5020 100%)" }}>
              Everything Digital
            </span>
          </h1>
          <p className="text-[15px] md:text-[17px] text-[#5a5a5a] max-w-[540px] mb-4 leading-relaxed">
            Custom websites · Cross-platform apps · AI workflows · IoT solutions · Research tools · And whatever you imagine — tell us, we will build it.
          </p>
          <p className="text-[11px] font-mono text-[#c9a96e]/50 mb-8"><span className="text-[#22c55e]">Parakram Leads is LIVE.</span> Try it at <a href="https://leads.getparakram.in" target="_blank" rel="noopener noreferrer" className="hover:text-[#c9a96e] transition-colors underline">leads.getparakram.in</a></p>
          <div className="flex items-center gap-3 flex-wrap justify-center">
            <motion.button onClick={() => go("services")} className="flex items-center gap-2 px-7 py-[13px] text-[13px] font-semibold tracking-[0.04em]" style={{ background: "linear-gradient(135deg,#b8903a,#d4b060,#f5e4a8,#c9a96e)", color: "#1a0f00" }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>View Services <ArrowRight size={13} /></motion.button>
            <motion.button onClick={() => go("work")} className="flex items-center gap-2 px-7 py-[13px] text-[13px] border border-[#c9a96e]/25 text-[#c9a96e] hover:border-[#c9a96e]/50 hover:bg-[#c9a96e]/[0.04] transition-all tracking-[0.04em]" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>See Our Work <ArrowRight size={13} /></motion.button>
          </div>
        </div>
      </section>

      {/* Services preview */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <div className="flex items-end justify-between mb-12">
          <div>
            <SectionLabel>Services</SectionLabel>
            <h2 className="text-[30px] md:text-[40px] font-semibold text-[#e8e6e3] tracking-[-0.02em]" style={{ fontFamily: "Sora, sans-serif" }}>What we build for you.</h2>
          </div>
          <button onClick={() => go("services")} className="hidden md:flex items-center gap-2 text-[12px] font-mono text-[#5a5a5a] hover:text-[#c9a96e] transition-colors">All Services <ArrowRight size={12} /></button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {SERVICES_PREVIEW.map(({ name, icon: Icon, desc, diff }) => (
            <motion.div key={name} onClick={() => go("services")} className="relative p-6 cursor-pointer group" style={{ border: "1px solid rgba(201,169,110,0.1)", background: "#0a0a0a" }} whileHover={{ y: -3, borderColor: "rgba(201,169,110,0.3)" }} transition={{ duration: 0.2 }}>
              <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-[#c9a96e]/40" /><div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-[#c9a96e]/40" /><div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-[#c9a96e]/40" /><div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-[#c9a96e]/40" />
              <div className="flex items-start justify-between mb-5">
                <div className="w-9 h-9 flex items-center justify-center border border-white/[0.07] group-hover:border-[#c9a96e]/30 transition-colors bg-white/[0.02]"><Icon size={16} className="text-[#3a3a3a] group-hover:text-[#c9a96e] transition-colors" /></div>
                <span className="text-[9px] font-mono text-[#2a2a2a] group-hover:text-[#c9a96e]/50">{diff}</span>
              </div>
              <h3 className="text-[14px] font-semibold text-[#c8c6c3] mb-2 group-hover:text-[#e8e6e3] transition-colors">{name}</h3>
              <p className="text-[12px] text-[#3a3a3a] leading-relaxed mb-5">{desc}</p>
              <div className="flex items-center gap-1 text-[11px] font-mono text-[#2a2a2a] group-hover:text-[#c9a96e] transition-colors">Get Started <ChevronRight size={10} /></div>
            </motion.div>
          ))}
        </div>
        <div className="mt-6 border border-dashed border-[#c9a96e]/10 p-6 text-center">
          <p className="text-[12px] text-[#5a5a5a] mb-2">Need something not listed?</p>
          <p className="text-[11px] font-mono text-[#c9a96e]">Tell us — no request is too ambitious.</p>
          <button onClick={() => go("contact")} className="mt-4 text-[12px] px-5 py-2 border border-[#c9a96e]/25 text-[#c9a96e] hover:bg-[#c9a96e]/[0.05] transition-colors font-mono">[ REACH OUT ]</button>
        </div>
      </section>

      {/* Client websites */}
      <section className="border-y border-white/[0.06] bg-[#0a0a0a] py-20">
        <div className="max-w-7xl mx-auto px-6">
          <SectionLabel>Live Deployments</SectionLabel>
          <h2 className="text-[28px] md:text-[38px] font-semibold text-[#e8e6e3] tracking-[-0.02em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>Shipped and live.</h2>
          <p className="text-[14px] text-[#5a5a5a] mb-10 max-w-lg">Real products, real clients, live in production.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            {CLIENT_SITES.map(({ domain, name, desc, tag }) => (
              <motion.a key={domain} href={`https://${domain}`} target="_blank" rel="noopener noreferrer"
                className="relative p-6 group block" style={{ border: "1px solid rgba(255,255,255,0.06)", background: "#070707" }}
                whileHover={{ y: -3, borderColor: "rgba(201,169,110,0.25)" }} transition={{ duration: 0.2 }}>
                <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-[#c9a96e]/30 group-hover:border-[#c9a96e]/60 transition-colors" />
                <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-[#c9a96e]/30 group-hover:border-[#c9a96e]/60 transition-colors" />
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[9px] font-mono text-[#c9a96e]/40 uppercase tracking-[0.2em] border border-[#c9a96e]/15 px-2 py-0.5">{tag}</span>
                  <ExternalLink size={11} className="text-[#2a2a2a] group-hover:text-[#c9a96e] transition-colors" />
                </div>
                <h3 className="text-[14px] font-semibold text-[#c8c6c3] mb-1 group-hover:text-[#e8e6e3] transition-colors">{name}</h3>
                <p className="text-[11px] font-mono text-[#c9a96e]/50 mb-3">{domain}</p>
                <p className="text-[12px] text-[#3a3a3a] leading-relaxed">{desc}</p>
              </motion.a>
            ))}
          </div>
          <button onClick={() => navTo(setPage, "work")} className="flex items-center gap-2 text-[13px] font-mono text-[#c9a96e] hover:gap-3 transition-all">See all client work <ArrowRight size={13} /></button>
        </div>
      </section>

      {/* Products preview */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <SectionLabel>Parakram Products</SectionLabel>
        <h2 className="text-[28px] md:text-[38px] font-semibold text-[#e8e6e3] tracking-[-0.02em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>Our own software, now shipping.</h2>
        <p className="text-[14px] text-[#5a5a5a] mb-10 max-w-xl leading-relaxed">Beyond client work, we build independent products. <span className="text-[#22c55e]">Parakram Leads is LIVE.</span> Try it now.</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {[
            { name: "Parakram Edge", tag: "Mobile Computing", desc: "Turn your Android phone into a high-performance edge server with a secure REST API for desktop AI agents and IoT orchestration.", pct: 72, icon: Cpu, live: false },
            { name: "Parakram Leads", tag: "AI Lead Intelligence", desc: "Find every Indian SMB without a website, audit their digital gaps, score opportunities, and send personalized outreach automatically.", pct: 100, icon: BarChart3, live: true },
            { name: "Parakram Research", tag: "Research Automation", desc: "Scrape hundreds of academic papers, build a searchable database, and extract insights with AI-powered analysis.", pct: 35, icon: Microscope, live: false },
          ].map(({ name, tag, desc, pct, icon: Icon }) => (
            <Panel key={name} className="p-6" onClick={() => go("products")}>
              <div className="flex items-center gap-3 mb-4"><Icon size={16} className="text-[#c9a96e]" /><div><p className="text-[9px] font-mono text-[#c9a96e]/50 uppercase tracking-[0.15em]">{tag}</p><h3 className="text-[14px] font-semibold text-[#e8e6e3]" style={{ fontFamily: "Sora, sans-serif" }}>{name}</h3></div></div>
              <p className="text-[12px] text-[#5a5a5a] leading-relaxed mb-5">{desc}</p>
              <div className="h-[3px] bg-white/[0.04]"><div className="h-full" style={{ width: `${pct}%`, background: pct >= 100 ? "linear-gradient(90deg,#22c55e,#16a34a)" : "linear-gradient(90deg,#7a5020,#c9a96e)" }} /></div>
              <p className="text-[10px] font-mono mt-2" style={{ color: pct >= 100 ? "#22c55e" : "#2a2a2a" }}>{pct >= 100 ? "LIVE — v0.2.1" : `BUILDING: ${pct}%`}</p>
            </Panel>
          ))}
        </div>
        <button onClick={() => go("products")} className="flex items-center gap-2 text-[13px] font-mono text-[#c9a96e] hover:gap-3 transition-all">Explore all products <ArrowRight size={13} /></button>
      </section>

      {/* Founder teaser */}
      <section className="border-y border-white/[0.06] bg-[#0a0a0a] py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <SectionLabel>Founder</SectionLabel>
              <h2 className="text-[28px] md:text-[38px] font-semibold text-[#e8e6e3] tracking-[-0.02em] mb-5" style={{ fontFamily: "Sora, sans-serif" }}>Built by a builder,<br />for builders.</h2>
              <p className="text-[14px] text-[#5a5a5a] leading-relaxed mb-8 max-w-md">Parakram is founded by Varshini CB — developer, designer, and systems thinker. Every product carries the same obsessive attention to craft.</p>
              <button onClick={() => go("about")} className="flex items-center gap-2 text-[13px] font-mono text-[#c9a96e] hover:gap-3 transition-all">Meet the Founder <ArrowRight size={13} /></button>
            </div>
            <Panel title="character.profile" className="p-8" onClick={() => go("about")}>
              <div className="flex items-start gap-5">
                <div className="w-16 h-16 overflow-hidden border-2 border-[#c9a96e]/30 flex-shrink-0" style={{ borderRadius: "4px" }}>
                  <ImageWithFallback src={varshiniImg} alt="Varshini CB" className="w-full h-full object-cover" />
                </div>
                <div>
                  <p className="text-[9px] font-mono text-[#c9a96e]/60 uppercase tracking-[0.2em] mb-1">[FOUNDER]</p>
                  <h3 className="text-[17px] font-semibold text-[#e8e6e3] mb-0.5" style={{ fontFamily: "Sora, sans-serif" }}>Varshini CB</h3>
                  <p className="text-[11px] text-[#5a5a5a]">Full-Stack Developer & Systems Architect</p>
                  <div className="flex items-center gap-3 mt-3">
                    <a href="https://www.linkedin.com/in/varshini-cb-821176360/" target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()} className="text-[#3a3a3a] hover:text-[#c9a96e] transition-colors"><Linkedin size={14} /></a>
                    <a href="https://github.com/varshinicb1" target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()} className="text-[#3a3a3a] hover:text-[#c9a96e] transition-colors"><Github size={14} /></a>
                  </div>
                </div>
              </div>
              <div className="mt-5 pt-4 border-t border-white/[0.05]">
                {[["DEV", 98], ["DESIGN", 92], ["AI / ML", 88], ["SYSTEMS", 95]].map(([k, v]) => (
                  <div key={String(k)} className="flex items-center gap-3 mb-2">
                    <span className="text-[9px] font-mono text-[#3a3a3a] w-16">{k}</span>
                    <div className="flex-1 h-[3px] bg-white/[0.04]"><div className="h-full" style={{ width: `${v}%`, background: "linear-gradient(90deg,#7a5020,#c9a96e)" }} /></div>
                    <span className="text-[9px] font-mono text-[#c9a96e]/60">{v}</span>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <Panel className="p-16 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_70%_at_50%_50%,rgba(201,169,110,0.05),transparent_70%)]" /><Scanlines />
          <div className="relative z-10">
            <SectionLabel>Ready?</SectionLabel>
            <h2 className="text-[34px] md:text-[50px] font-semibold text-[#e8e6e3] tracking-[-0.025em] mb-5 leading-tight" style={{ fontFamily: "Sora, sans-serif" }}>Have a project in mind?</h2>
            <p className="text-[14px] text-[#5a5a5a] mb-10 max-w-md mx-auto leading-relaxed">Tell us what you want to build. We will figure out the rest together — from concept to shipped product.</p>
            <div className="flex items-center gap-3 justify-center flex-wrap">
              <motion.button onClick={() => go("contact")} className="px-8 py-[13px] text-[13px] font-semibold text-[#1a0f00] tracking-[0.04em]" style={{ background: "linear-gradient(135deg,#b8903a,#d4b060,#f5e4a8,#c9a96e)" }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>Start a Conversation</motion.button>
              <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer">
                <motion.button className="flex items-center gap-2 px-8 py-[13px] text-[13px] border border-[#25D366]/30 text-[#25D366] hover:border-[#25D366]/60 hover:bg-[#25D366]/[0.04] transition-all" whileHover={{ scale: 1.02 }}><MessageCircle size={14} /> Chat on WhatsApp</motion.button>
              </a>
            </div>
          </div>
        </Panel>
      </section>
    </div>
  );
}

export default HomePage;
