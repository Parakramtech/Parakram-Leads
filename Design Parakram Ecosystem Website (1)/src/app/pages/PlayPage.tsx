"use client";

import SnakeGame from "../components/SnakeGame";
import Panel from "../components/Panel";
import { Lock } from "lucide-react";

function PlayPage() {
  return (
    <div className="min-h-screen pt-24 pb-32">
      <div className="max-w-5xl mx-auto px-6">
        <div className="mb-12 text-center">
          <p className="text-[10px] tracking-[0.32em] text-[#c9a96e] uppercase font-mono mb-4">ARCADE</p>
          <h1 style={{ fontFamily: "'Press Start 2P', monospace" }} className="text-[18px] md:text-[26px] text-[#e8e6e3] mb-5 leading-loose">
            PLAY A GAME
          </h1>
          <p className="text-[14px] text-[#5a5a5a] max-w-md mx-auto">We built an actual game into the website. Eat the gold orbs. Avoid walls. That is it.</p>
        </div>

        <div className="grid md:grid-cols-[auto_1fr] gap-10 items-start justify-center">
          <SnakeGame />
          <div className="flex flex-col gap-5">
            <Panel title="how.to.play" className="p-6">
              <p className="text-[10px] font-mono text-[#c9a96e]/50 mb-4 uppercase tracking-[0.15em]">Controls</p>
              <div className="flex flex-col gap-2 font-mono">
                <p className="text-[12px] text-[#5a5a5a]">◆ WASD or Arrow keys</p>
                <p className="text-[12px] text-[#5a5a5a]">◆ Swipe on mobile</p>
                <p className="text-[12px] text-[#5a5a5a]">◆ D-pad buttons below</p>
                <p className="text-[12px] text-[#5a5a5a]">◆ Eat gold orbs to grow</p>
                <p className="text-[12px] text-[#5a5a5a]">◆ Hit wall or self = over</p>
              </div>
            </Panel>
            <Panel title="coming.games" className="p-6">
              <p className="text-[10px] font-mono text-[#2a2a2a] uppercase tracking-[0.15em] mb-3">More Games Planned</p>
              {["Memory Card Game", "Typing Speed Challenge", "Code Debug Puzzle"].map(g => (
                <div key={g} className="flex items-center gap-2 py-2 border-b border-white/[0.03] last:border-0">
                  <Lock size={10} className="text-[#2a2a2a]" /><span className="text-[12px] text-[#2a2a2a]">{g}</span>
                </div>
              ))}
            </Panel>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PlayPage;
