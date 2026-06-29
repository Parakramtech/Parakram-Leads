"use client";

import { useState } from "react";
import { motion } from "motion/react";

function WarriorMark({ size = 120, float = true, idSuffix = "0", onClick }: {
  size?: number; float?: boolean; idSuffix?: string; onClick?: () => void;
}) {
  const [pulse, setPulse] = useState(false);
  const handle = () => { if (!onClick) return; onClick(); setPulse(true); setTimeout(() => setPulse(false), 700); };
  const g = (n: string) => `wm${idSuffix}_${n}`;

  const svgEl = (
    <svg viewBox="0 0 110 120" fill="none" xmlns="http://www.w3.org/2000/svg"
      style={{ width: "100%", height: "100%", cursor: onClick ? "pointer" : "default",
        filter: pulse
          ? "drop-shadow(0 0 50px rgba(245,228,168,0.95)) drop-shadow(0 0 80px rgba(201,169,110,0.7))"
          : "drop-shadow(0 6px 36px rgba(201,169,110,0.55)) drop-shadow(0 2px 14px rgba(201,169,110,0.25))",
        transition: "filter 0.4s ease" }}
      onClick={handle}>
      <defs>
        {/* Primary gold gradient */}
        <linearGradient id={g("gold")} x1="15%" y1="0%" x2="85%" y2="100%">
          <stop offset="0%" stopColor="#120c04" />
          <stop offset="8%" stopColor="#3a2410" />
          <stop offset="22%" stopColor="#7a5828" />
          <stop offset="38%" stopColor="#c9a96e" />
          <stop offset="50%" stopColor="#f5e4a8" />
          <stop offset="64%" stopColor="#d4b870" />
          <stop offset="80%" stopColor="#9a7240" />
          <stop offset="100%" stopColor="#1a0e04" />
        </linearGradient>
        {/* Sheen */}
        <linearGradient id={g("sheen")} x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="rgba(255,245,200,0.3)" />
          <stop offset="40%" stopColor="rgba(255,245,200,0)" />
          <stop offset="100%" stopColor="rgba(255,200,100,0.06)" />
        </linearGradient>
        {/* Edge gradient */}
        <linearGradient id={g("edge")} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#7a4a18" />
          <stop offset="50%" stopColor="#f5e4a8" />
          <stop offset="100%" stopColor="#7a4a18" />
        </linearGradient>
        {/* Plume gradient */}
        <linearGradient id={g("plume")} x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#f5e4a8" />
          <stop offset="40%" stopColor="#c9a96e" />
          <stop offset="100%" stopColor="#5a3810" />
        </linearGradient>
        {/* Brushed texture */}
        <pattern id={g("brush")} width="110" height="1.3" patternUnits="userSpaceOnUse">
          <line x1="0" y1="0.65" x2="110" y2="0.65" stroke="rgba(255,255,255,0.05)" strokeWidth="0.65" />
        </pattern>
        {/* Glow filter */}
        <filter id={g("glow")} x="-30%" y="-20%" width="160%" height="140%">
          <feGaussianBlur stdDeviation="2.5" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {/* Shadow / ground plane */}
      <ellipse cx="55" cy="116" rx="35" ry="4" fill="black" opacity="0.4" />

      {/* ── PLUME — extends up and left from back of crown ── */}
      <path d="M 42 16 Q 34 5 24 0 Q 14 -4 8 2 Q 4 8 8 16 Q 14 22 24 22 L 36 20 Z"
        fill={`url(#${g("plume")})`} filter={`url(#${g("glow")})`} />
      <path d="M 42 16 Q 34 5 24 0 Q 14 -4 8 2 Q 4 8 8 16 Q 14 22 24 22 L 36 20 Z"
        fill={`url(#${g("brush")})`} opacity="0.6" />
      {/* Plume quill / spine line */}
      <path d="M 42 18 Q 25 8 10 10" stroke="rgba(245,228,168,0.5)" strokeWidth="1" fill="none" />

      {/* ── MAIN HELMET BODY ── */}
      {/* The helmet faces right (open face on the right side) */}
      <path d="
        M 38 110
        L 72 110
        Q 80 110 84 102
        L 84 88
        Q 90 86 92 78
        L 92 65
        Q 95 55 92 44
        Q 88 28 78 18
        Q 66 8 52 10
        Q 38 10 28 20
        L 28 32
        L 42 18
        L 50 16
        Q 68 14 76 28
        Q 84 42 80 58
        Q 78 68 76 78
        L 76 102
        L 38 102
        Z
      " fill={`url(#${g("gold")})`} filter={`url(#${g("glow")})`} />

      {/* Brushed texture overlay on helmet */}
      <path d="
        M 38 110 L 72 110 Q 80 110 84 102 L 84 88 Q 90 86 92 78 L 92 65 Q 95 55 92 44
        Q 88 28 78 18 Q 66 8 52 10 Q 38 10 28 20 L 28 32 L 42 18 L 50 16
        Q 68 14 76 28 Q 84 42 80 58 Q 78 68 76 78 L 76 102 L 38 102 Z
      " fill={`url(#${g("brush")})`} opacity="0.85" />

      {/* Sheen */}
      <path d="
        M 38 110 L 72 110 Q 80 110 84 102 L 84 88 Q 90 86 92 78 L 92 65 Q 95 55 92 44
        Q 88 28 78 18 Q 66 8 52 10 Q 38 10 28 20 L 28 32 L 42 18 L 50 16
        Q 68 14 76 28 Q 84 42 80 58 Q 78 68 76 78 L 76 102 L 38 102 Z
      " fill={`url(#${g("sheen")})`} />

      {/* ── VISOR / EYE SLIT — open right side of face ── */}
      {/* The left face guard has an eye slit */}
      <path d="M 28 38 L 56 34 L 56 48 L 28 52 Z" fill="#060606" />
      <path d="M 28 38 L 56 34 L 56 48 L 28 52 Z" fill="none" stroke="rgba(201,169,110,0.2)" strokeWidth="0.8" />

      {/* ── NASAL / NOSE GUARD ── */}
      <path d="M 28 52 L 22 60 L 22 72 L 28 70 Z" fill={`url(#${g("gold")})`} />
      <path d="M 28 52 L 22 60 L 22 72 L 28 70 Z" fill={`url(#${g("brush")})`} opacity="0.6" />

      {/* ── NECK / CHEEK GUARD plate (right side extension) ── */}
      <path d="M 84 80 L 96 76 L 96 94 L 84 94 Z" fill={`url(#${g("gold")})`} />
      <path d="M 84 80 L 96 76 L 96 94 L 84 94 Z" fill={`url(#${g("brush")})`} opacity="0.7" />

      {/* ── Edge highlights ── */}
      {/* Front vertical edge */}
      <path d="M 28 20 L 28 105" stroke="rgba(201,169,110,0.4)" strokeWidth="1.5" />
      {/* Top brow edge */}
      <path d="M 28 20 Q 50 12 76 20" stroke="rgba(245,228,168,0.5)" strokeWidth="1" fill="none" />
      {/* Bottom edge */}
      <path d="M 38 110 L 76 110" stroke={`url(#${g("edge")})`} strokeWidth="1" opacity="0.5" />

      {/* Specular dots (forged rivets look) */}
      <circle cx="28" cy="20" r="1.5" fill="#f5e4a8" opacity="0.8" />
      <circle cx="84" cy="80" r="1.2" fill="#f5e4a8" opacity="0.6" />
      <circle cx="28" cy="70" r="1" fill="#f5e4a8" opacity="0.5" />

      {/* ── Decorative crest line across crown ── */}
      <path d="M 42 18 Q 60 14 76 24" stroke="rgba(245,228,168,0.35)" strokeWidth="2" fill="none" />
    </svg>
  );

  const wrapped = float ? (
    <motion.div style={{ width: "100%", height: "100%" }}
      animate={{ y: [-8, 8, -8], rotate: [-0.4, 0.4, -0.4] }}
      transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}>
      {svgEl}
    </motion.div>
  ) : svgEl;

  return (
    <div style={{ width: size, height: size * 1.1 }} className="relative">
      {wrapped}
      {pulse && (
        <motion.div initial={{ scale: 0.6, opacity: 0.9 }} animate={{ scale: 3, opacity: 0 }}
          transition={{ duration: 0.7 }} className="absolute inset-0 rounded-full pointer-events-none"
          style={{ border: "1px solid rgba(201,169,110,0.8)" }} />
      )}
    </div>
  );
}

function WarriorSmall({ size = 28 }: { size?: number }) {
  return (
    <svg viewBox="0 0 110 120" fill="none" style={{ width: size, height: size * 1.1, filter: "drop-shadow(0 0 8px rgba(201,169,110,0.55))", flexShrink: 0 }}>
      <defs>
        <linearGradient id="wsm_g" x1="15%" y1="0%" x2="85%" y2="100%">
          <stop offset="10%" stopColor="#3a2410" />
          <stop offset="45%" stopColor="#c9a96e" />
          <stop offset="52%" stopColor="#f5e4a8" />
          <stop offset="85%" stopColor="#5a3810" />
        </linearGradient>
        <linearGradient id="wsm_p" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#c9a96e" />
          <stop offset="100%" stopColor="#3a2410" />
        </linearGradient>
      </defs>
      {/* Simplified plume */}
      <path d="M 42 16 Q 28 4 14 2 Q 6 4 8 14 Q 14 22 26 20 L 38 18 Z" fill="url(#wsm_p)" />
      {/* Simplified helmet */}
      <path d="M 38 110 L 72 110 L 80 100 L 80 86 Q 88 82 88 68 L 88 48 Q 84 28 72 18 Q 60 10 48 12 Q 34 14 28 26 L 28 38 L 44 18 L 52 16 Q 72 16 78 36 Q 82 52 78 70 L 76 100 L 38 100 Z" fill="url(#wsm_g)" />
      {/* Eye slit */}
      <path d="M 28 38 L 54 34 L 54 46 L 28 50 Z" fill="#070707" />
      {/* Nose guard */}
      <path d="M 28 50 L 22 58 L 22 70 L 28 68 Z" fill="url(#wsm_g)" />
      {/* Neck plate */}
      <path d="M 80 80 L 92 76 L 92 90 L 80 90 Z" fill="url(#wsm_g)" />
      {/* Front edge */}
      <path d="M 28 26 L 28 102" stroke="#c9a96e" strokeWidth="1.5" opacity="0.6" />
    </svg>
  );
}

export { WarriorMark, WarriorSmall };
export default WarriorMark;
