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
    </>
  );
}
