"use client";

import { useState } from "react";
import { motion } from "motion/react";
import SectionLabel from "../components/SectionLabel";
import Panel from "../components/Panel";
import Scanlines from "../components/Scanlines";
import { Check, MessageCircle, Mail, Linkedin, Github } from "lucide-react";

function ContactPage() {
  const [sent, setSent] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", project: "Custom Website", message: "" });

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); setSent(true); };

  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16">
          <SectionLabel>Contact</SectionLabel>
          <h1 className="text-[40px] md:text-[52px] font-semibold text-[#e8e6e3] tracking-[-0.025em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>Let us build together.</h1>
          <p className="text-[15px] text-[#5a5a5a] max-w-lg">Tell us what you want to build. We respond within 24 hours. For quick answers, WhatsApp us directly.</p>
        </div>

        <div className="grid md:grid-cols-[1fr_360px] gap-12">
          <div>
            {sent ? (
              <Panel className="p-12 text-center">
                <Scanlines />
                <div className="relative z-10">
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 200 }}>
                    <div className="w-14 h-14 border border-[#c9a96e]/30 flex items-center justify-center mx-auto mb-5"><Check size={22} className="text-[#c9a96e]" /></div>
                  </motion.div>
                  <h3 className="text-[20px] font-semibold text-[#e8e6e3] mb-2" style={{ fontFamily: "Sora, sans-serif" }}>Message received.</h3>
                  <p className="text-[13px] text-[#5a5a5a] mb-6">We will respond within 24 hours.<br />Or reach us on WhatsApp for a faster reply.</p>
                  <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-5 py-2.5 text-[12px] font-mono text-[#25D366] border border-[#25D366]/30 hover:bg-[#25D366]/[0.05] transition-colors"><MessageCircle size={13} /> Open WhatsApp</a>
                </div>
              </Panel>
            ) : (
              <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="text-[10px] font-mono tracking-[0.18em] text-[#3a3a3a] uppercase block mb-2">Your Name</label><input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Varshini CB" required className="w-full bg-transparent border border-white/[0.07] px-4 py-3 text-[13px] text-[#e8e6e3] placeholder-[#2a2a2a] focus:border-[#c9a96e]/40 outline-none transition-colors" /></div>
                  <div><label className="text-[10px] font-mono tracking-[0.18em] text-[#3a3a3a] uppercase block mb-2">Email</label><input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="you@company.com" required className="w-full bg-transparent border border-white/[0.07] px-4 py-3 text-[13px] text-[#e8e6e3] placeholder-[#2a2a2a] focus:border-[#c9a96e]/40 outline-none transition-colors" /></div>
                </div>
                <div><label className="text-[10px] font-mono tracking-[0.18em] text-[#3a3a3a] uppercase block mb-2">Project Type</label><select value={form.project} onChange={e => setForm({ ...form, project: e.target.value })} className="w-full bg-[#0f0f0f] border border-white/[0.07] px-4 py-3 text-[13px] text-[#e8e6e3] focus:border-[#c9a96e]/40 outline-none transition-colors">{["Custom Website", "Portfolio Site", "Mobile App", "AI Workflow / Agent", "IoT Solution", "Research Tool", "ERP / Billing / POS", "Attendance System", "Real Estate App", "Parakram Edge", "Parakram Leads", "Parakram Research", "Other"].map(s => <option key={s}>{s}</option>)}</select></div>
                <div><label className="text-[10px] font-mono tracking-[0.18em] text-[#3a3a3a] uppercase block mb-2">Tell us about your project</label><textarea value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} rows={6} required placeholder="Describe what you want to build, the problem it solves, and any specific integrations or features you need..." className="w-full bg-transparent border border-white/[0.07] px-4 py-3 text-[13px] text-[#e8e6e3] placeholder-[#2a2a2a] focus:border-[#c9a96e]/40 outline-none transition-colors resize-none" /></div>
                <div className="flex items-center gap-3 flex-wrap">
                  <motion.button type="submit" className="px-8 py-[13px] text-[13px] font-semibold text-[#1a0f00] tracking-[0.04em]" style={{ background: "linear-gradient(135deg,#b8903a,#d4b060,#f5e4a8,#c9a96e)" }} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>Send Message</motion.button>
                  <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer"><motion.button type="button" className="flex items-center gap-2 px-6 py-[13px] text-[13px] font-mono border border-[#25D366]/30 text-[#25D366] hover:border-[#25D366]/60 hover:bg-[#25D366]/[0.04] transition-all" whileHover={{ scale: 1.02 }}><MessageCircle size={14} /> WhatsApp Instead</motion.button></a>
                </div>
              </form>
            )}
          </div>

          <div className="flex flex-col gap-4">
            <Panel title="direct.contact" className="p-6">
              <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 p-3 hover:bg-[#25D366]/[0.05] transition-colors mb-3 border border-[#25D366]/15"><MessageCircle size={16} className="text-[#25D366]" /><div><p className="text-[12px] font-semibold text-[#e8e6e3]">WhatsApp</p><p className="text-[11px] text-[#3a3a3a]">+91 7259426670</p></div></a>
              <a href="mailto:hello@getparakram.in" className="flex items-center gap-3 p-3 hover:bg-white/[0.02] transition-colors border border-white/[0.06]"><Mail size={16} className="text-[#c9a96e]" /><div><p className="text-[12px] font-semibold text-[#e8e6e3]">Email</p><p className="text-[11px] text-[#3a3a3a]">hello@getparakram.in</p></div></a>
            </Panel>
            <Panel title="connect" className="p-6">
              <div className="flex flex-col gap-3">
                <a href="https://www.linkedin.com/in/varshini-cb-821176360/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-[13px] text-[#5a5a5a] hover:text-[#c9a96e] transition-colors"><Linkedin size={14} /> LinkedIn — Varshini CB</a>
                <a href="https://github.com/varshinicb1" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-[13px] text-[#5a5a5a] hover:text-[#c9a96e] transition-colors"><Github size={14} /> github.com/varshinicb1</a>
              </div>
            </Panel>
            <Panel className="p-6">
              <p className="text-[11px] font-mono text-[#c9a96e]/50 uppercase tracking-[0.15em] mb-3">Response Time</p>
              <p className="text-[13px] text-[#c8c6c3] mb-1">Email: within 24 hours</p>
              <p className="text-[13px] text-[#c8c6c3]">WhatsApp: within 2 hours</p>
            </Panel>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContactPage;
