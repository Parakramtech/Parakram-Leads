"use client";

import { motion } from "motion/react";
import SectionLabel from "../components/SectionLabel";
import { type Page } from "../types";
import {
  ArrowRight, Globe, Star, Smartphone, Bot, Cpu, Microscope,
  ShoppingCart, Users, Building2, Rocket, MessageCircle, ChevronRight,
} from "lucide-react";

function navTo(setPage: (p: Page) => void, p: Page) { setPage(p); window.scrollTo({ top: 0, behavior: "instant" }); }

function ServicesPage({ setPage }: { setPage: (p: Page) => void }) {
  const go = (p: Page) => navTo(setPage, p);
  const fullServices = [
    { name: "Custom Websites", icon: Globe, desc: "SEO-optimised, beautifully designed web experiences. Landing pages, corporate sites, eCommerce, portals — fast, accessible, and memorable.", time: "1–4 weeks", tech: ["Next.js", "React", "Tailwind", "Vercel"] },
    { name: "Portfolio Sites", icon: Star, desc: "Interactive, animated, custom portfolios crafted to make you unforgettable online. Developers, designers, creators, and professionals.", time: "3–7 days", tech: ["React", "Framer Motion", "Three.js"] },
    { name: "Cross-Platform Apps", icon: Smartphone, desc: "Android, iOS, Windows — one codebase. ESC/POS thermal receipt printing, CRM integrations, BLE/WiFi hardware bridges, offline-first design.", time: "4–12 weeks", tech: ["React Native", "Flutter", "Electron", "ESC/POS"] },
    { name: "AI Agents & Workflows", icon: Bot, desc: "Intelligent automation: AI-driven pipelines, lead scoring, WhatsApp/email triggers, document processing, and custom LLM-powered tools.", time: "4–16 weeks", tech: ["LangChain", "OpenAI", "n8n", "PostgreSQL"] },
    { name: "IoT & Hardware", icon: Cpu, desc: "Sensor firmware, real-time cloud dashboards, edge-to-cloud MQTT stacks, BLE communication, and PCB design coordination for custom hardware.", time: "6–20 weeks", tech: ["ESP32", "Raspberry Pi", "MQTT", "InfluxDB"] },
    { name: "Research Automation", icon: Microscope, desc: "Automate systematic review, web scraping, statistical pipelines, PDF parsing, and generate publication-ready reports with AI assistance.", time: "2–8 weeks", tech: ["Python", "Playwright", "pandas", "LangChain"] },
    { name: "ERP / Billing / POS", icon: ShoppingCart, desc: "Custom ERP, inventory management, GST billing, and POS systems with ESC/POS thermal printing and WhatsApp order notifications.", time: "4–10 weeks", tech: ["React", "Node.js", "PostgreSQL", "ESC/POS"] },
    { name: "Attendance & HR Tools", icon: Users, desc: "Employee attendance with GPS geo-fencing, face verification, real-time status reports, leave management, and automated payroll calculations.", time: "4–12 weeks", tech: ["React Native", "Face AI", "GPS APIs", "Firebase"] },
    { name: "Property & Real Estate Apps", icon: Building2, desc: "Property listing platforms, virtual tours, buyer/seller matching, lead pipelines, and CRM integrations for real estate startups.", time: "6–14 weeks", tech: ["React", "Maps API", "Node.js", "PostgreSQL"] },
    { name: "Any Custom Challenge", icon: Rocket, desc: "Do not see your project? Describe it to us. We have yet to find something we cannot build. WhatsApp us or fill in the form.", time: "TBD", tech: ["Anything"] },
  ];

  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16">
          <SectionLabel>Services</SectionLabel>
          <h1 className="text-[40px] md:text-[52px] font-semibold text-[#e8e6e3] tracking-[-0.025em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>What we build.</h1>
          <p className="text-[15px] text-[#5a5a5a] max-w-lg leading-relaxed">Every project is delivered on time, on spec, with obsessive attention to quality. For pricing, reach us on WhatsApp.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {fullServices.map(({ name, icon: Icon, desc, time, tech }, i) => (
            <motion.div key={name} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }} className="relative p-7 group" style={{ border: "1px solid rgba(201,169,110,0.1)", background: "#0a0a0a" }} whileHover={{ borderColor: "rgba(201,169,110,0.3)", y: -2 }}>
              <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#c9a96e]/40" /><div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#c9a96e]/40" /><div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#c9a96e]/40" /><div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#c9a96e]/40" />
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 flex items-center justify-center border border-white/[0.07] group-hover:border-[#c9a96e]/30 transition-colors bg-white/[0.02]"><Icon size={16} className="text-[#3a3a3a] group-hover:text-[#c9a96e] transition-colors" /></div>
                <h3 className="text-[15px] font-semibold text-[#d0cec9] group-hover:text-[#e8e6e3] transition-colors">{name}</h3>
              </div>
              <p className="text-[13px] text-[#4a4a4a] leading-relaxed mb-5">{desc}</p>
              <div className="flex items-center justify-between border-t border-white/[0.05] pt-4 mb-3">
                <div><p className="text-[9px] font-mono text-[#2a2a2a] uppercase mb-1">Typical Timeline</p><p className="text-[11px] font-mono text-[#5a5a5a]">{time}</p></div>
                <div className="text-right"><p className="text-[9px] font-mono text-[#2a2a2a] uppercase mb-1">Pricing</p><a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer" className="text-[11px] font-mono text-[#25D366]/70 hover:text-[#25D366] transition-colors">WhatsApp us</a></div>
              </div>
              <div className="flex items-center gap-2 flex-wrap mb-4">{tech.map(t => <span key={t} className="text-[9px] font-mono px-2 py-0.5 text-[#3a3a3a] border border-white/[0.05]">{t}</span>)}</div>
              <button onClick={() => go("contact")} className="w-full py-2.5 text-[12px] font-mono text-[#c9a96e] border border-[#c9a96e]/20 hover:border-[#c9a96e]/50 hover:bg-[#c9a96e]/[0.04] transition-colors tracking-[0.08em]">[ GET STARTED ]</button>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ServicesPage;
