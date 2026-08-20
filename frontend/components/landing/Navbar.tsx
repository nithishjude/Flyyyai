"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const links = [
  { label: "FEATURES",      section: "features"      },
  { label: "HOW IT WORKS",  section: "how-it-works"  },
];

function scrollTo(id: string) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive]     = useState("");

  /* ── scroll detection ── */
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /* ── active section via IntersectionObserver ── */
  useEffect(() => {
    const ids = links.map((l) => l.section).filter(Boolean);
    const obs: IntersectionObserver[] = [];

    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      const o = new IntersectionObserver(
        ([entry]) => { if (entry.isIntersecting) setActive(id); },
        { rootMargin: "-35% 0px -60% 0px" }
      );
      o.observe(el);
      obs.push(o);
    });

    return () => obs.forEach((o) => o.disconnect());
  }, []);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={{
        background:       scrolled ? "rgba(10,10,10,0.88)" : "transparent",
        backdropFilter:   scrolled ? "blur(14px)"          : "none",
        WebkitBackdropFilter: scrolled ? "blur(14px)"      : "none",
        borderBottom:     scrolled ? "1px solid #1E1E1E"   : "1px solid transparent",
      }}
    >
      <div className="flex items-center justify-between h-[60px] px-6 md:px-[48px] max-w-[1400px] mx-auto">

        {/* ── Logo ── */}
        <a href="#" className="flex items-center gap-[10px] shrink-0 group">
          <span className="w-[10px] h-[10px] bg-[#FFD600] group-hover:scale-110 transition-transform" />
          <span className="font-grotesk text-[13px] font-bold text-[#F5F5F0] tracking-[2.5px]">
            FLYYY<span style={{ color: "#FFD600" }}>.AI</span>
          </span>
        </a>

        {/* ── Nav links ── */}
        <nav className="hidden sm:flex items-center gap-[24px] md:gap-[36px]">
          {links.map(({ label, section }) => {
            const isActive = active === section;
            return (
              <button
                key={label}
                onClick={() => scrollTo(section)}
                className="relative font-ibm-mono text-[10px] tracking-[1.5px] transition-colors duration-150 bg-transparent border-none cursor-pointer"
                style={{ color: isActive ? "#FFD600" : "#555" }}
                onMouseEnter={(e) => {
                  if (!isActive) (e.currentTarget as HTMLButtonElement).style.color = "#F5F5F0";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.color = isActive ? "#FFD600" : "#555";
                }}
              >
                {label}
                <span
                  className="absolute left-0 -bottom-[3px] h-[1.5px] bg-[#FFD600] transition-all duration-300"
                  style={{ width: isActive ? "100%" : "0%" }}
                />
              </button>
            );
          })}
        </nav>

        {/* ── CTA ── */}
        <Link
          href="/scan"
          className="font-grotesk text-[11px] font-bold text-[#0A0A0A] bg-[#FFD600] tracking-[1.5px] px-[18px] py-[9px] hover:bg-[#F5F5F0] transition-colors shrink-0"
        >
          START SCANNING
        </Link>
      </div>
    </header>
  );
}
