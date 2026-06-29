"use client";

import { motion } from "motion/react";
import Panel from "../components/Panel";
import SectionLabel from "../components/SectionLabel";
import { Smartphone, ShoppingCart, Building2, Users, Cpu, Bot, Zap, ExternalLink } from "lucide-react";

function WorkPage() {
  const websites = [
    { domain: "cokakaalan.in", name: "Coka Kaalan", category: "Business Website", desc: "Complete business website with custom CMS, mobile-first layout, SEO optimization, and contact lead capture.", tech: ["Next.js", "Tailwind"] },
    { domain: "vidyuthlabs.co.in", name: "Vidyuth Labs", category: "Corporate Site", desc: "Clean, high-performance corporate site for a technology lab. Optimized for speed, accessibility, and professional credibility.", tech: ["React", "Vercel"] },
    { domain: "pubrealty.in", name: "PubRealty", category: "Real Estate Platform", desc: "Property listing platform with search filters, geo-location maps, photo galleries, and seller lead management.", tech: ["React", "Node.js", "Maps API"] },
  ];

  const apps = [
    { name: "Smart Billing + POS", category: "Mobile App", desc: "Easy-to-use billing application with ESC/POS thermal printer integration, inventory tracking, GST invoicing, and CRM customer history. Built for a retail client.", icons: [Smartphone, ShoppingCart], tags: ["ESC/POS", "CRM", "Flutter", "Bluetooth"] },
    { name: "Property Listing App", category: "Mobile App", desc: "Full-featured real estate app for a startup — property listings with rich media, buyer/seller matching, saved searches, and WhatsApp inquiry integration.", icons: [Smartphone, Building2], tags: ["React Native", "Maps", "WhatsApp API"] },
    { name: "Geo + Face Attendance", category: "Enterprise App", desc: "Employee attendance system with GPS geo-fencing, face recognition verification, real-time status dashboards, leave workflows, and automated reporting.", icons: [Users, Cpu], tags: ["Face AI", "GPS", "React Native", "Firebase"] },
    { name: "AI Agent Automations", category: "AI Workflow", desc: "Custom AI agents for document processing, automated email/WhatsApp response pipelines, lead qualification, and multi-step business workflow automation.", icons: [Bot, Zap], tags: ["LangChain", "n8n", "OpenAI", "WhatsApp API"] },
  ];

  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16">
          <SectionLabel>Portfolio</SectionLabel>
          <h1 className="text-[40px] md:text-[52px] font-semibold text-[#e8e6e3] tracking-[-0.025em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>Shipped and live.</h1>
          <p className="text-[15px] text-[#5a5a5a] max-w-lg">Real products delivered for real clients. Every project is in production.</p>
        </div>

        {/* Live websites */}
        <h2 className="text-[18px] font-semibold text-[#e8e6e3] mb-5" style={{ fontFamily: "Sora, sans-serif" }}>Client Websites</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-14">
          {websites.map(({ domain, name, category, desc, tech }) => (
            <motion.a key={domain} href={`https://${domain}`} target="_blank" rel="noopener noreferrer"
              className="relative p-7 group block" style={{ border: "1px solid rgba(255,255,255,0.06)", background: "#0a0a0a" }}
              whileHover={{ y: -3, borderColor: "rgba(201,169,110,0.28)" }}>
              <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#c9a96e]/30 group-hover:border-[#c9a96e]/60 transition-colors" />
              <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#c9a96e]/30 group-hover:border-[#c9a96e]/60 transition-colors" />
              <div className="flex items-center justify-between mb-4">
                <span className="text-[9px] font-mono text-[#c9a96e]/50 uppercase tracking-[0.2em] border border-[#c9a96e]/15 px-2 py-0.5">{category}</span>
                <ExternalLink size={12} className="text-[#2a2a2a] group-hover:text-[#c9a96e] transition-colors" />
              </div>
              <h3 className="text-[16px] font-semibold text-[#c8c6c3] mb-1 group-hover:text-[#e8e6e3] transition-colors">{name}</h3>
              <p className="text-[11px] font-mono text-[#c9a96e]/40 mb-3">{domain}</p>
              <p className="text-[12px] text-[#4a4a4a] leading-relaxed mb-4">{desc}</p>
              <div className="flex gap-2 flex-wrap">{tech.map(t => <span key={t} className="text-[9px] font-mono px-2 py-0.5 text-[#2a2a2a] border border-white/[0.05]">{t}</span>)}</div>
            </motion.a>
          ))}
        </div>

        {/* Apps */}
        <h2 className="text-[18px] font-semibold text-[#e8e6e3] mb-5" style={{ fontFamily: "Sora, sans-serif" }}>Custom Applications</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {apps.map(({ name, category, desc, icons, tags }) => (
            <Panel key={name} className="p-7">
              <div className="flex items-start gap-3 mb-4">
                <div className="flex gap-1">
                  {icons.map((Icon, i) => <div key={i} className="w-8 h-8 flex items-center justify-center border border-white/[0.07] bg-white/[0.02]"><Icon size={14} className="text-[#c9a96e]" /></div>)}
                </div>
                <div>
                  <p className="text-[9px] font-mono text-[#c9a96e]/50 uppercase tracking-[0.18em]">{category}</p>
                  <h3 className="text-[15px] font-semibold text-[#e8e6e3]">{name}</h3>
                </div>
              </div>
              <p className="text-[13px] text-[#5a5a5a] leading-relaxed mb-5">{desc}</p>
              <div className="flex gap-2 flex-wrap">{tags.map(t => <span key={t} className="text-[9px] font-mono px-2 py-0.5 text-[#3a3a3a] border border-[#c9a96e]/10">{t}</span>)}</div>
            </Panel>
          ))}
        </div>
      </div>
    </div>
  );
}

export default WorkPage;
