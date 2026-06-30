import { MessageCircle, Github, Linkedin, Mail } from "lucide-react";

import type { Page } from "../types";

function navTo(setPage: (p: Page) => void, p: Page) { setPage(p); window.scrollTo({ top: 0, behavior: "instant" }); }

export function Footer({ setPage }: { setPage: (p: Page) => void }) {
  const go = (p: Page) => navTo(setPage, p);
  return (
    <footer className="border-t border-white/[0.06] bg-[#070707] mt-32">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-10">
          <div className="col-span-2">
            <div className="flex items-center gap-3 mb-4"><img src="/parakram_logo.png" alt="Parakram" className="w-6 h-6 object-contain" /><span className="text-[11px] font-semibold tracking-[0.22em] text-[#e8e6e3] uppercase" style={{ fontFamily: "Sora, sans-serif" }}>Parakram</span></div>
            <p className="text-[12px] text-[#333] leading-relaxed max-w-xs mb-5">We build everything digital — websites, apps, AI workflows, IoT, and whatever you imagine. Tell us your vision.</p>
            <div className="flex items-center gap-4">
              <a href="https://wa.me/917259426670" target="_blank" rel="noopener noreferrer" className="text-[#252525] hover:text-[#25D366] transition-colors"><MessageCircle size={15} /></a>
              <a href="https://github.com/varshinicb1" target="_blank" rel="noopener noreferrer" className="text-[#252525] hover:text-[#c9a96e] transition-colors"><Github size={15} /></a>
              <a href="https://www.linkedin.com/in/varshini-cb-821176360/" target="_blank" rel="noopener noreferrer" className="text-[#252525] hover:text-[#c9a96e] transition-colors"><Linkedin size={15} /></a>
              <a href="mailto:hello@getparakram.in" className="text-[#252525] hover:text-[#c9a96e] transition-colors"><Mail size={15} /></a>
            </div>
          </div>
          {([
            { heading: "Build", links: [["Websites", "services"], ["Mobile Apps", "services"], ["AI Workflows", "services"], ["IoT", "services"]] },
            { heading: "Company", links: [["Work", "work"], ["Products", "products"], ["About", "about"], ["Contact", "contact"], ["Privacy", "privacy"]] },
          ] as { heading: string; links: [string, Page][] }[]).map(({ heading, links }) => (
            <div key={heading}>
              <h4 className="text-[10px] font-mono tracking-[0.2em] text-[#2a2a2a] uppercase mb-4">{heading}</h4>
              <div className="flex flex-col gap-2">{links.map(([l, p]) => <button key={l} onClick={() => go(p)} className="text-[12px] text-[#2e2e2e] hover:text-[#7a7a7a] text-left transition-colors">{l}</button>)}</div>
            </div>
          ))}
        </div>
        <div className="border-t border-white/[0.05] pt-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <p className="text-[11px] text-[#1e1e1e]">© 2024 Parakram. Built with valor.</p>
          <div className="flex items-center gap-4">
            {["cokakaalan.in", "vidyuthlabs.co.in", "pubrealty.in"].map(site => (
              <a key={site} href={`https://${site}`} target="_blank" rel="noopener noreferrer" className="text-[10px] font-mono text-[#1e1e1e] hover:text-[#c9a96e]/60 transition-colors">{site}</a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
