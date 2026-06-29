"use client";

import { motion } from "motion/react";
import SectionLabel from "../components/SectionLabel";
import Panel from "../components/Panel";
import Scanlines from "../components/Scanlines";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import { type Page } from "../types";
import { Linkedin, Github, MessageCircle, Zap, Code, Star, Rocket, ArrowRight } from "lucide-react";
import varshiniImg from "../../imports/varshini.png";

function navTo(setPage: (p: Page) => void, p: Page) { setPage(p); window.scrollTo({ top: 0, behavior: "instant" }); }

function AboutPage({ setPage }: { setPage: (p: Page) => void }) {
  const skills = [
    { label: "Full-Stack Web Development", val: 97 },
    { label: "Mobile & Cross-Platform Apps", val: 93 },
    { label: "AI / LLM Integration & Agents", val: 88 },
    { label: "IoT & Embedded Systems", val: 82 },
    { label: "UI/UX Design", val: 91 },
    { label: "Systems Architecture", val: 94 },
    { label: "Research Automation", val: 85 },
    { label: "Hardware Prototyping", val: 75 },
  ];

  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16">
          <SectionLabel>About</SectionLabel>
          <h1 className="text-[40px] md:text-[52px] font-semibold text-[#e8e6e3] tracking-[-0.025em] mb-4" style={{ fontFamily: "Sora, sans-serif" }}>Meet the Founder.</h1>
        </div>

        <div className="grid md:grid-cols-[380px_1fr] gap-10 mb-20">
          <Panel title="meet.the.founder" className="p-8">
            <Scanlines />
            <div className="relative z-10">
              <div className="relative mb-6">
                <div className="w-full overflow-hidden" style={{ border: "1px solid rgba(201,169,110,0.25)", aspectRatio: "3/4" }}>
                  <ImageWithFallback src={varshiniImg} alt="Varshini CB — Founder of Parakram" className="w-full h-full object-cover object-center" />
                </div>
                <div className="absolute top-3 right-3 px-2 py-1 bg-[#070707]/90 backdrop-blur-sm" style={{ border: "1px solid rgba(201,169,110,0.4)" }}>
                  <span className="text-[9px] font-mono text-[#c9a96e]">FOUNDER</span>
                </div>
                <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-[#0a0a0a] to-transparent" />
              </div>
              <h2 className="text-[22px] font-semibold text-[#e8e6e3] mb-1" style={{ fontFamily: "Sora, sans-serif" }}>Varshini CB</h2>
              <p className="text-[12px] text-[#5a5a5a] mb-5">Full-Stack Developer · Systems Designer · Builder</p>
              <div className="flex flex-col gap-2">
                <a href="https://www.linkedin.com/in/varshini-cb-821176360/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 text-[12px] font-mono transition-all hover:bg-[#c9a96e]/[0.06]" style={{ border: "1px solid rgba(201,169,110,0.2)", color: "#c9a96e" }}>
                  <Linkedin size={13} /> Connect on LinkedIn
                </a>
                <a href="https://github.com/varshinicb1" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 text-[12px] font-mono transition-all hover:bg-white/[0.03]" style={{ border: "1px solid rgba(255,255,255,0.07)", color: "#7a7a7a" }}>
                  <Github size={13} /> github.com/varshinicb1
                </a>
                <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-4 py-2.5 text-[12px] font-mono transition-all hover:bg-[#25D366]/[0.05]" style={{ border: "1px solid rgba(37,211,102,0.2)", color: "#25D366" }}>
                  <MessageCircle size={13} /> WhatsApp
                </a>
              </div>
            </div>
          </Panel>

          <div className="flex flex-col gap-5">
            <Panel title="skill.tree" className="p-7">
              <div className="flex flex-col gap-3">
                {skills.map(({ label, val }) => (
                  <div key={label} className="flex items-center gap-3">
                    <span className="text-[11px] text-[#5a5a5a] w-56 flex-shrink-0">{label}</span>
                    <div className="flex-1 h-[4px] bg-white/[0.04]">
                      <motion.div className="h-full" style={{ background: "linear-gradient(90deg,#7a5020,#c9a96e,#f5e4a8)" }} initial={{ width: 0 }} animate={{ width: `${val}%` }} transition={{ duration: 1.2, delay: 0.2, ease: [0.4, 0, 0.2, 1] }} />
                    </div>
                    <span className="text-[10px] font-mono text-[#c9a96e] w-8 text-right">{val}</span>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel title="lore.txt" className="p-7">
              <div className="space-y-3">
                {[
                  "Varshini CB is a full-stack developer and systems architect who started building websites at 16 and never stopped.",
                  "She founded Parakram with one mission: deliver bespoke digital products at a quality level usually reserved for large teams — leaner, faster, more personal.",
                  "Every project at Parakram clears one bar: would we be proud to put our name on this? Yes = ship. No = iterate.",
                  "Parakram is growing into a full digital ecosystem — custom client work alongside independent products. Everything digital. One studio.",
                ].map((p, i) => <p key={i} className="text-[13px] text-[#5a5a5a] leading-relaxed">{p}</p>)}
                <div className="pt-3 border-t border-white/[0.05]">
                  <button onClick={() => navTo(setPage, "contact")} className="flex items-center gap-2 text-[12px] font-mono text-[#c9a96e] hover:gap-3 transition-all">Start a conversation <ArrowRight size={12} /></button>
                </div>
              </div>
            </Panel>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-white/[0.04]">
          {[
            { icon: Zap, t: "Ship Fast", d: "Bias for getting things into the world." },
            { icon: Code, t: "Clean Code", d: "Readable, maintainable, built to last." },
            { icon: Star, t: "Craft First", d: "Design and engineering matter equally." },
            { icon: Rocket, t: "Own Outcomes", d: "We treat your project like our own." },
          ].map(({ icon: Icon, t, d }) => (
            <div key={t} className="bg-[#070707] p-7"><Icon size={16} className="text-[#c9a96e] mb-4" /><h3 className="text-[14px] font-semibold text-[#c8c6c3] mb-2">{t}</h3><p className="text-[12px] text-[#3a3a3a] leading-relaxed">{d}</p></div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AboutPage;
