export default function Footer() {
  return (
    <footer className="flex flex-col w-full bg-[#050505]">
      {/* Top */}
      <div className="flex flex-col px-6 md:px-[120px] py-12 md:py-[64px]">
        {/* Brand */}
        <div className="flex flex-col gap-6">
          <div className="flex items-center gap-[12px]">
            <div className="w-[32px] h-[32px] bg-[#FFD600] shrink-0" />
            <span className="font-grotesk text-[16px] font-bold text-[#FFD600] tracking-[3px]">
              FLYYY.AI
            </span>
          </div>
          <p className="font-ibm-mono text-[11px] text-[#888888] tracking-[1px] leading-[1.6] max-w-[260px]">
            AUTOMATED AI ASSET DISCOVERY. BUILT FOR SECURITY AND GOVERNANCE
            TEAMS.
          </p>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between w-full px-6 md:px-[120px] py-4 md:h-[56px] border-t border-t-[#1D1D1D] gap-3 sm:gap-0">
        <span className="font-ibm-mono text-[11px] text-[#666666] tracking-[1px]">
          © 2026 FLYYY.AI. ALL RIGHTS RESERVED.
        </span>
        <div className="flex items-center gap-6 md:gap-[32px]">
          <a href="#" className="font-ibm-mono text-[11px] text-[#666666] tracking-[1px] hover:text-[#AAAAAA] transition-colors">
            PRIVACY
          </a>
          <a href="#" className="font-ibm-mono text-[11px] text-[#666666] tracking-[1px] hover:text-[#AAAAAA] transition-colors">
            TERMS
          </a>
          <span className="font-ibm-mono text-[11px] font-bold text-[#FFD600] tracking-[1px]">
            V1.0.0
          </span>
        </div>
      </div>
    </footer>
  );
}
