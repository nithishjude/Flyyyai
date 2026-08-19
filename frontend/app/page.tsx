import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "FLYYY.AI — AI Asset Discovery Platform",
  description:
    "Automatically discover, inventory, and govern every AI integration across your codebase. Evidence-backed. Line-level traceability. Zero false positives.",
};

const features = [
  {
    icon: "🔬",
    title: "AST-Level Precision",
    desc: "Python files are parsed using the built-in ast module — syntactically precise, zero false positives from commented-out code.",
    color: "var(--emerald)",
    glow: "rgba(16,185,129,0.12)",
  },
  {
    icon: "🌿",
    title: "Terraform IaC Scanning",
    desc: "Detects Azure OpenAI, AWS Bedrock, and GCP Vertex AI resource declarations directly from your .tf files.",
    color: "var(--accent-light)",
    glow: "rgba(99,102,241,0.12)",
  },
  {
    icon: "🤖",
    title: "Agent Framework Detection",
    desc: "Identifies LangGraph, LangChain, CrewAI and other agent orchestration frameworks — not just raw LLM calls.",
    color: "var(--rose)",
    glow: "rgba(244,63,94,0.12)",
  },
  {
    icon: "📋",
    title: "Manifest Intelligence",
    desc: "Scans requirements.txt, package.json, pyproject.toml, and .env files for AI package dependencies and API keys.",
    color: "var(--amber)",
    glow: "rgba(245,158,11,0.12)",
  },
  {
    icon: "🏷️",
    title: "Discovered vs Inferred",
    desc: "Every asset gets a confidence-weighted status. Discovered = import + model name. Inferred = partial evidence only.",
    color: "var(--emerald)",
    glow: "rgba(16,185,129,0.12)",
  },
  {
    icon: "🔗",
    title: "Full Traceability",
    desc: "Every asset links back to the exact file, line number, and code snippet that triggered discovery. No black boxes.",
    color: "var(--accent-light)",
    glow: "rgba(99,102,241,0.12)",
  },
];

const pipeline = [
  { n: "01", icon: "📂", title: "File Walker", desc: "Traverses the repo, pruning noise directories like venv, node_modules, .git, .terraform" },
  { n: "02", icon: "⚙️", title: "Per-file Parsers", desc: "AST for Python · Regex for JS/TS · Regex for Terraform HCL" },
  { n: "03", icon: "🔍", title: "Evidence Extractor", desc: "Emits typed signals: LIBRARY_IMPORT · MODEL_NAME_STRING · ENV_VAR_KEY · MANIFEST_DEPENDENCY" },
  { n: "04", icon: "🧩", title: "Evidence Aggregator", desc: "Groups signals by application boundary detected from manifest files" },
  { n: "05", icon: "✨", title: "Asset Synthesizer", desc: "Merges evidence into structured AIAsset records with confidence scoring and status" },
];

const supported = [
  { lang: "Python", icon: "🐍", note: "AST parser" },
  { lang: "JavaScript", icon: "🟨", note: "Regex parser" },
  { lang: "TypeScript", icon: "🔷", note: "Regex parser" },
  { lang: "Terraform", icon: "🌿", note: "HCL regex" },
  { lang: "requirements.txt", icon: "📦", note: "Manifest" },
  { lang: "package.json", icon: "📦", note: "Manifest" },
  { lang: ".env files", icon: "🔑", note: "Env keys" },
  { lang: "pyproject.toml", icon: "📦", note: "Manifest" },
];

const providers = ["OpenAI", "Anthropic", "Hugging Face", "Azure OpenAI", "AWS Bedrock", "Google Vertex AI", "LangChain", "LangGraph", "Mistral AI", "Cohere", "Groq", "Ollama"];

export default function LandingPage() {
  return (
    <div className="landing-page">
      {/* ── HERO ─────────────────────────────────────────────────────── */}
      <section className="landing-hero" aria-labelledby="hero-heading">
        <div className="hero-glow-orb hero-glow-1" aria-hidden="true" />
        <div className="hero-glow-orb hero-glow-2" aria-hidden="true" />
        <div className="hero-glow-orb hero-glow-3" aria-hidden="true" />

        <div className="hero-inner">
          <div className="hero-eyebrow slide-up">
            <span className="eyebrow-dot" aria-hidden="true" />
            AI Governance · Evidence-Backed Discovery
          </div>

          <h1 id="hero-heading" className="hero-title slide-up delay-100">
            Every AI asset in your codebase,{" "}
            <span className="hero-gradient">automatically surfaced</span>
          </h1>

          <p className="hero-subtitle slide-up delay-200">
            FLYYY.AI walks your source code — Python, JS/TS, Terraform — and builds
            a structured, evidence-backed inventory of every LLM integration,
            embedding model, and AI agent framework. Full traceability to the exact
            file and line.
          </p>

          <div className="hero-cta slide-up delay-300">
            <Link href="/scan" className="btn-hero-primary" id="hero-cta-scan">
              <span aria-hidden="true">▶</span> Run a Scan
            </Link>
            <Link href="/assets" className="btn-hero-secondary" id="hero-cta-inventory">
              <span aria-hidden="true">◈</span> View Inventory
            </Link>
          </div>

          <div className="hero-stats slide-up delay-400" aria-label="Platform statistics">
            {[
              { value: "4", label: "File Types" },
              { value: "12+", label: "AI Providers" },
              { value: "5", label: "Signal Types" },
              { value: "100%", label: "Traceable" },
            ].map(({ value, label }) => (
              <div key={label} className="hero-stat">
                <span className="hero-stat-value">{value}</span>
                <span className="hero-stat-label">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Floating code preview */}
        <div className="hero-code-preview slide-up delay-500" aria-hidden="true">
          <div className="code-preview-header">
            <span className="dot dot-red" />
            <span className="dot dot-amber" />
            <span className="dot dot-green" />
            <span className="code-preview-title">scan result · support-portal</span>
          </div>
          <pre className="code-preview-body">{`{
  "asset_name": "support-portal",
  "provider":   "OpenAI",
  "asset_type": "AI Agent",
  "model":      "gpt-4o-mini",
  "status":     "Discovered",
  "confidence": 0.91,
  "evidence": [
    { "signal_type": "LIBRARY_IMPORT",
      "matched_value": "langgraph",
      "file": "agent.py", "line": 23 },
    { "signal_type": "MODEL_NAME_STRING",
      "matched_value": "gpt-4o-mini",
      "file": "agent.py", "line": 47 }
  ]
}`}</pre>
        </div>
      </section>

      {/* ── PROVIDERS TICKER ─────────────────────────────────────────── */}
      <div className="providers-ticker" aria-label="Supported AI providers">
        <div className="ticker-track">
          {[...providers, ...providers].map((p, i) => (
            <span key={i} className="ticker-item">{p}</span>
          ))}
        </div>
      </div>

      {/* ── FEATURES ─────────────────────────────────────────────────── */}
      <section className="landing-section" aria-labelledby="features-heading">
        <div className="section-eyebrow">
          <span aria-hidden="true">◈</span> Capabilities
        </div>
        <h2 id="features-heading" className="section-title">
          Built for precision, not guesswork
        </h2>
        <p className="section-subtitle">
          Every signal is typed, weighted, and traced. No LLM required to find LLMs.
        </p>

        <div className="features-grid">
          {features.map(({ icon, title, desc, color, glow }) => (
            <div key={title} className="feature-card" style={{ "--feature-glow": glow, "--feature-color": color } as React.CSSProperties}>
              <div className="feature-icon" aria-hidden="true">{icon}</div>
              <h3 className="feature-title">{title}</h3>
              <p className="feature-desc">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── PIPELINE ─────────────────────────────────────────────────── */}
      <section className="landing-section pipeline-section" aria-labelledby="pipeline-heading">
        <div className="section-eyebrow">
          <span aria-hidden="true">⬡</span> Architecture
        </div>
        <h2 id="pipeline-heading" className="section-title">
          A five-stage discovery pipeline
        </h2>
        <p className="section-subtitle">
          From raw repository path to structured AI asset inventory in seconds.
        </p>

        <div className="pipeline-track">
          {pipeline.map(({ n, icon, title, desc }, idx) => (
            <div key={n} className="pipeline-step">
              <div className="pipeline-connector" aria-hidden="true">
                <div className="pipeline-node">
                  <span className="pipeline-icon" aria-hidden="true">{icon}</span>
                </div>
                {idx < pipeline.length - 1 && <div className="pipeline-line" aria-hidden="true" />}
              </div>
              <div className="pipeline-content">
                <div className="pipeline-num">{n}</div>
                <div className="pipeline-title">{title}</div>
                <p className="pipeline-desc">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── SUPPORTED LANGUAGES ──────────────────────────────────────── */}
      <section className="landing-section" aria-labelledby="languages-heading">
        <div className="section-eyebrow">
          <span aria-hidden="true">⊕</span> Language Support
        </div>
        <h2 id="languages-heading" className="section-title">
          Scans where AI actually lives
        </h2>
        <div className="lang-grid">
          {supported.map(({ lang, icon, note }) => (
            <div key={lang} className="lang-card">
              <span className="lang-icon" aria-hidden="true">{icon}</span>
              <span className="lang-name">{lang}</span>
              <span className="lang-note">{note}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────── */}
      <section className="landing-cta-section" aria-labelledby="cta-heading">
        <div className="cta-glow" aria-hidden="true" />
        <div className="cta-inner">
          <h2 id="cta-heading" className="cta-title">
            Ready to map your AI surface area?
          </h2>
          <p className="cta-subtitle">
            Point the scanner at any local repository and get a structured,
            evidence-backed AI asset inventory in seconds.
          </p>
          <Link href="/scan" className="btn-hero-primary" id="bottom-cta-scan">
            <span aria-hidden="true">▶</span> Start Scanning
          </Link>
        </div>
      </section>
    </div>
  );
}
