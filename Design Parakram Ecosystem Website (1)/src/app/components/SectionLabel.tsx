function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <div className="w-5 h-px" style={{ background: "linear-gradient(90deg,#c9a96e,transparent)" }} />
      <span className="text-[10px] tracking-[0.32em] text-[#c9a96e] uppercase font-mono">{children}</span>
    </div>
  );
}

export default SectionLabel;
