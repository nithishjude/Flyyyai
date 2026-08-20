"use client";

const CURSOR = {
  name: "ALEX_K",
  color: "#FFD600",
  textColor: "#0A0A0A",
  animName: "cursor-alex",
  duration: "18s",
  keyframes: `@keyframes cursor-alex {
    0%   { transform: translate(12vw, 8vh); }
    15%  { transform: translate(40vw, 18vh); }
    30%  { transform: translate(55vw, 30vh); }
    50%  { transform: translate(30vw, 42vh); }
    65%  { transform: translate(15vw, 25vh); }
    80%  { transform: translate(48vw, 12vh); }
    100% { transform: translate(12vw, 8vh); }
  }`,
};

export default function CollabCursors() {
  return (
    <div
      className="absolute inset-0 overflow-hidden pointer-events-none hidden md:block"
      style={{ zIndex: 20 }}
    >
      <style>{CURSOR.keyframes}</style>

      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          animation: `${CURSOR.animName} ${CURSOR.duration} cubic-bezier(0.4, 0, 0.2, 1) infinite`,
          willChange: "transform",
        }}
      >
        {/* Cursor arrow */}
        <svg
          width="16"
          height="18"
          viewBox="0 0 20 22"
          fill="none"
          style={{ filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.7))" }}
        >
          <path
            d="M2 2L18 10L10 12L6 20L2 2Z"
            fill={CURSOR.color}
            stroke="#0A0A0A"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
        </svg>

        {/* Name tag */}
        <div
          style={{
            position: "absolute",
            left: "14px",
            top: "14px",
            backgroundColor: CURSOR.color,
            padding: "2px 8px",
            fontFamily: "monospace",
            fontSize: "10px",
            fontWeight: 700,
            color: CURSOR.textColor,
            letterSpacing: "0.08em",
            whiteSpace: "nowrap",
            boxShadow: "0 2px 8px rgba(0,0,0,0.5)",
          }}
        >
          {CURSOR.name}
        </div>
      </div>
    </div>
  );
}
