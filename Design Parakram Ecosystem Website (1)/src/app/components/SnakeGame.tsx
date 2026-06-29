"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import { motion } from "motion/react";
import Panel from "./Panel";
import Scanlines from "./Scanlines";

const COLS = 22; const ROWS = 22; const CELL = 16;
const CW = COLS * CELL; const CH = ROWS * CELL;
type Pos = { x: number; y: number }; type Dir = { x: number; y: number };

function randFood(snake: Pos[]): Pos { let p: Pos; do { p = { x: Math.floor(Math.random() * COLS), y: Math.floor(Math.random() * ROWS) }; } while (snake.some(s => s.x === p.x && s.y === p.y)); return p; }

function SnakeGame() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gs = useRef({ snake: [{ x: 11, y: 11 }] as Pos[], dir: { x: 1, y: 0 } as Dir, nextDir: { x: 1, y: 0 } as Dir, food: { x: 5, y: 5 } as Pos, score: 0, alive: true });
  const intervalRef = useRef<ReturnType<typeof setInterval>>();
  const [score, setScore] = useState(0);
  const [phase, setPhase] = useState<"idle" | "playing" | "dead">("idle");
  const touchStart = useRef<{ x: number; y: number } | null>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current; if (!canvas) return;
    const ctx = canvas.getContext("2d"); if (!ctx) return;
    const { snake, food } = gs.current;
    ctx.fillStyle = "#070707"; ctx.fillRect(0, 0, CW, CH);
    ctx.strokeStyle = "rgba(255,255,255,0.025)"; ctx.lineWidth = 0.5;
    for (let x = 0; x <= COLS; x++) { ctx.beginPath(); ctx.moveTo(x * CELL, 0); ctx.lineTo(x * CELL, CH); ctx.stroke(); }
    for (let y = 0; y <= ROWS; y++) { ctx.beginPath(); ctx.moveTo(0, y * CELL); ctx.lineTo(CW, y * CELL); ctx.stroke(); }
    const fx = food.x * CELL + CELL / 2, fy = food.y * CELL + CELL / 2;
    const grd = ctx.createRadialGradient(fx, fy, 1, fx, fy, CELL / 2 + 4);
    grd.addColorStop(0, "#f5e4a8"); grd.addColorStop(0.5, "#c9a96e"); grd.addColorStop(1, "rgba(201,169,110,0)");
    ctx.fillStyle = grd; ctx.fillRect(food.x * CELL + 2, food.y * CELL + 2, CELL - 4, CELL - 4);
    snake.forEach((seg, i) => {
      const isHead = i === 0;
      ctx.globalAlpha = isHead ? 1 : Math.max(0.3, 1 - (i / snake.length) * 0.7);
      ctx.fillStyle = isHead ? "#f5e4a8" : "#c9a96e";
      const p = isHead ? 1 : 2;
      if (isHead) { ctx.shadowBlur = 12; ctx.shadowColor = "#c9a96e"; }
      ctx.fillRect(seg.x * CELL + p, seg.y * CELL + p, CELL - p * 2, CELL - p * 2);
      ctx.shadowBlur = 0;
    });
    ctx.globalAlpha = 1;
  }, []);

  const step = useCallback(() => {
    const st = gs.current; if (!st.alive) return;
    st.dir = st.nextDir;
    const head = st.snake[0];
    const next = { x: head.x + st.dir.x, y: head.y + st.dir.y };
    if (next.x < 0 || next.x >= COLS || next.y < 0 || next.y >= ROWS || st.snake.some(s => s.x === next.x && s.y === next.y)) {
      st.alive = false; setPhase("dead"); if (intervalRef.current) clearInterval(intervalRef.current); return;
    }
    st.snake.unshift(next);
    if (next.x === st.food.x && next.y === st.food.y) { st.score++; setScore(st.score); st.food = randFood(st.snake); }
    else { st.snake.pop(); }
    draw();
  }, [draw]);

  const start = useCallback(() => {
    const st = gs.current;
    st.snake = [{ x: 11, y: 11 }, { x: 10, y: 11 }, { x: 9, y: 11 }];
    st.dir = { x: 1, y: 0 }; st.nextDir = { x: 1, y: 0 }; st.food = randFood(st.snake); st.score = 0; st.alive = true;
    setScore(0); setPhase("playing");
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(step, 110); draw();
  }, [step, draw]);

  useEffect(() => { draw(); return () => { if (intervalRef.current) clearInterval(intervalRef.current); }; }, [draw]);

  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if (phase !== "playing") return;
      const st = gs.current;
      const map: Record<string, Dir> = { ArrowUp: { x: 0, y: -1 }, ArrowDown: { x: 0, y: 1 }, ArrowLeft: { x: -1, y: 0 }, ArrowRight: { x: 1, y: 0 }, w: { x: 0, y: -1 }, s: { x: 0, y: 1 }, a: { x: -1, y: 0 }, d: { x: 1, y: 0 } };
      const d = map[e.key]; if (!d) return;
      if (d.x === -st.dir.x && d.y === -st.dir.y) return;
      st.nextDir = d; e.preventDefault();
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [phase]);

  const setDir = (d: Dir) => { const st = gs.current; if (phase !== "playing") return; if (d.x === -st.dir.x && d.y === -st.dir.y) return; st.nextDir = d; };
  const onTouchStart = (e: React.TouchEvent) => { touchStart.current = { x: e.touches[0].clientX, y: e.touches[0].clientY }; };
  const onTouchEnd = (e: React.TouchEvent) => {
    if (!touchStart.current || phase !== "playing") return;
    const dx = e.changedTouches[0].clientX - touchStart.current.x, dy = e.changedTouches[0].clientY - touchStart.current.y;
    if (Math.abs(dx) > Math.abs(dy)) setDir(dx > 0 ? { x: 1, y: 0 } : { x: -1, y: 0 });
    else setDir(dy > 0 ? { x: 0, y: 1 } : { x: 0, y: -1 });
    touchStart.current = null;
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <Panel title="SNAKE.EXE" className="p-2">
        <div className="relative">
          <canvas ref={canvasRef} width={CW} height={CH} className="block" style={{ imageRendering: "pixelated" }} onTouchStart={onTouchStart} onTouchEnd={onTouchEnd} />
          {phase !== "playing" && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm">
              <Scanlines />
              <div className="relative z-10 text-center px-6">
                {phase === "dead" && (
                  <><p style={{ fontFamily: "'Press Start 2P', monospace" }} className="text-[#c9a96e] text-sm mb-3 leading-relaxed">GAME OVER</p>
                  <p className="text-[#5a5a5a] text-xs font-mono mb-6">Score: {score}</p></>
                )}
                {phase === "idle" && (
                  <><p style={{ fontFamily: "'Press Start 2P', monospace" }} className="text-[#c9a96e] text-sm mb-4 leading-loose">SNAKE</p>
                  <p className="text-[#5a5a5a] text-xs font-mono mb-1">Eat the gold orbs. Avoid walls.</p>
                  <p className="text-[#3a3a3a] text-xs font-mono mb-6">WASD / Arrows / Swipe</p></>
                )}
                <button onClick={start}
                  className="px-5 py-3 text-[9px] text-[#c9a96e] tracking-[0.15em] hover:bg-[#c9a96e]/10 transition-colors leading-relaxed"
                  style={{ fontFamily: "'Press Start 2P', monospace", border: "1px solid rgba(201,169,110,0.4)" }}>
                  {phase === "dead" ? "RETRY" : "START"}
                </button>
              </div>
            </div>
          )}
        </div>
      </Panel>
      <div className="flex items-center justify-between w-full px-1">
        <span className="text-[11px] font-mono text-[#c9a96e]">SCORE: <span className="text-[#f5e4a8]">{score}</span></span>
        <span className="text-[11px] font-mono text-[#2a2a2a]">WASD to move</span>
      </div>
      <div className="grid grid-cols-3 gap-1 w-28">
        <div />
        <button onClick={() => setDir({ x: 0, y: -1 })} className="h-8 flex items-center justify-center text-[#c9a96e] font-mono text-xs" style={{ border: "1px solid rgba(201,169,110,0.2)" }}>▲</button>
        <div />
        <button onClick={() => setDir({ x: -1, y: 0 })} className="h-8 flex items-center justify-center text-[#c9a96e] font-mono text-xs" style={{ border: "1px solid rgba(201,169,110,0.2)" }}>◀</button>
        <div className="h-8 flex items-center justify-center"><div className="w-1.5 h-1.5 bg-[#c9a96e]/30" /></div>
        <button onClick={() => setDir({ x: 1, y: 0 })} className="h-8 flex items-center justify-center text-[#c9a96e] font-mono text-xs" style={{ border: "1px solid rgba(201,169,110,0.2)" }}>▶</button>
        <div />
        <button onClick={() => setDir({ x: 0, y: 1 })} className="h-8 flex items-center justify-center text-[#c9a96e] font-mono text-xs" style={{ border: "1px solid rgba(201,169,110,0.2)" }}>▼</button>
        <div />
      </div>
    </div>
  );
}

export default SnakeGame;
