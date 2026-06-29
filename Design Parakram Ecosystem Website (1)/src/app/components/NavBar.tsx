import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import GoldButton from "./GoldButton";

import type { Page } from "../types";

function navTo(setPage: (p: Page) => void, p: Page) { setPage(p); window.scrollTo({ top: 0, behavior: "instant" }); }

const NAV_LINKS: { label: string; page: Page }[] = [
  { label: "Services", page: "services" },
  { label: "Work", page: "work" },
  { label: "Products", page: "products" },
  { label: "Store", page: "store" },
  { label: "About", page: "about" },
  { label: "Contact", page: "contact" },
];

export function NavBar({ current, setPage }: { current: Page; setPage: (p: Page) => void }) {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => { const h = () => setScrolled(window.scrollY > 30); window.addEventListener("scroll", h); return () => window.removeEventListener("scroll", h); }, []);
  const go = (p: Page) => { navTo(setPage, p); setOpen(false); };

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${scrolled ? "bg-[#070707]/94 backdrop-blur-2xl border-b border-white/[0.06]" : "bg-transparent"}`}>
      <div className="max-w-7xl mx-auto px-6 h-[60px] flex items-center justify-between">
        <button onClick={() => go("home")} className="flex items-center gap-3">
          <img src="/parakram_logo.png" alt="Parakram" className="w-7 h-7 object-contain" />
          <span className="text-[11px] font-semibold tracking-[0.22em] text-[#e8e6e3] uppercase" style={{ fontFamily: "Sora, sans-serif" }}>Parakram</span>
        </button>
        <div className="hidden md:flex items-center gap-7">
          {NAV_LINKS.map(({ label, page }) => (
            <button key={page} onClick={() => go(page)} className={`text-[13px] tracking-wide transition-colors ${current === page ? "text-[#c9a96e]" : "text-[#6a6a6a] hover:text-[#e8e6e3]"}`}>{label}</button>
          ))}
          <button onClick={() => go("play")} className="text-[12px] px-3 py-1.5 font-mono tracking-[0.08em] transition-all" style={{ border: "1px solid rgba(201,169,110,0.35)", color: "#c9a96e", background: current === "play" ? "rgba(201,169,110,0.08)" : "transparent" }}>
            ▶ PLAY
          </button>
        </div>
        <div className="hidden md:flex items-center gap-3">
          <GoldButton onClick={() => go("contact")} className="text-[12px] px-5 py-2.5 tracking-[0.08em]">
            TRUST US
          </GoldButton>
        </div>
        <button onClick={() => setOpen(v => !v)} className="md:hidden text-[#6a6a6a] hover:text-[#e8e6e3]">{open ? <X size={18} /> : <Menu size={18} />}</button>
      </div>
      {open && (
        <div className="md:hidden bg-[#0a0a0a] border-b border-white/[0.06] px-6 py-5 flex flex-col gap-3">
          {[...NAV_LINKS, { label: "▶ PLAY", page: "play" as Page }].map(({ label, page }) => (
            <button key={page} onClick={() => go(page)} className={`text-left text-[13px] py-1 ${current === page ? "text-[#c9a96e]" : "text-[#6a6a6a]"}`}>{label}</button>
          ))}
          <button onClick={() => go("contact")} className="self-start text-[12px] px-5 py-2 font-semibold mt-1" style={{ background: "linear-gradient(135deg,#c9a96e,#f5e4a8)", color: "#1a0f00" }}>TRUST US</button>
        </div>
      )}
    </header>
  );
}
