function Panel({ children, title, className = "", onClick }: { children: React.ReactNode; title?: string; className?: string; onClick?: () => void }) {
  return (
    <div className={`relative ${className} ${onClick ? "cursor-pointer" : ""}`} style={{ border: "1px solid rgba(201,169,110,0.12)", background: "#0a0a0a" }} onClick={onClick}>
      {title && <div className="absolute -top-3 left-4 px-2 bg-[#070707] text-[9px] font-mono text-[#c9a96e]/70 tracking-[0.22em] uppercase">{title}</div>}
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#c9a96e]/50" />
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#c9a96e]/50" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#c9a96e]/50" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#c9a96e]/50" />
      {children}
    </div>
  );
}

export default Panel;
