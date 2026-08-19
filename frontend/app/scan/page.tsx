import type { Metadata } from "next";
import ScanForm from "@/components/ScanForm";

export const metadata: Metadata = {
  title: "New Scan — FLYYY.AI Asset Discovery",
  description:
    "Trigger an AI asset discovery scan against a local repository. Automatically detect LLM integrations, embedding models, and AI frameworks.",
};

export default function ScanPage() {
  return (
    <>
      <section className="scan-hero slide-up" aria-labelledby="scan-heading">
        <div className="page-eyebrow">
          <span aria-hidden="true">⬡</span> AI Governance Platform
        </div>

        <h1 id="scan-heading" className="page-title" style={{ fontSize: "2.4rem" }}>
          Discover every <span className="gradient-text">AI asset</span>
          <br />in your codebase
        </h1>

        <p className="page-subtitle" style={{ margin: "0.75rem auto 0" }}>
          Point the scanner at any local repository. It walks your source code,
          extracts evidence, and builds a structured inventory of every AI
          integration — with full traceability back to the line of code.
        </p>

        <ScanForm />


      </section>

      {/* How it works */}
      <section
        className="mt-8 slide-up delay-300"
        aria-labelledby="how-it-works-heading"
        style={{ maxWidth: 860, margin: "3rem auto 0" }}
      >
        <h2
          id="how-it-works-heading"
          style={{
            fontSize: "1rem",
            fontWeight: 700,
            letterSpacing: "-0.01em",
            marginBottom: "1.25rem",
            color: "var(--text-secondary)",
          }}
        >
          How the pipeline works
        </h2>

        <ol
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
            gap: "1rem",
            listStyle: "none",
          }}
        >
          {[
            { n: "01", title: "File Walker", desc: "Walks repo, skips noise dirs (venv, node_modules, .git)" },
            { n: "02", title: "Parsers", desc: "AST for Python, regex for JS/TS & Terraform — extracts raw signals" },
            { n: "03", title: "Evidence", desc: "Signals tagged: import, model name, env key, endpoint" },
            { n: "04", title: "Aggregation", desc: "Groups evidence by application boundary (manifest files)" },
            { n: "05", title: "Synthesis", desc: "Merges into AI assets with Discovered / Inferred status" },
          ].map(({ n, title, desc }) => (
            <li key={n} className="card" style={{ padding: "1.1rem 1.25rem" }}>
              <div
                style={{
                  fontSize: "0.65rem",
                  fontWeight: 800,
                  letterSpacing: "0.12em",
                  color: "var(--accent)",
                  marginBottom: "0.4rem",
                }}
              >
                STEP {n}
              </div>
              <div style={{ fontWeight: 700, fontSize: "0.875rem", marginBottom: "0.3rem" }}>
                {title}
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", lineHeight: 1.5 }}>
                {desc}
              </div>
            </li>
          ))}
        </ol>
      </section>
    </>
  );
}
