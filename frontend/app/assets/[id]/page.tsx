import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import StatusBadge from "@/components/StatusBadge";
import EvidenceList from "@/components/EvidenceList";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Evidence {
  id: string;
  file_path: string;
  line_number: number;
  signal_type: string;
  matched_value: string;
  snippet: string;
  confidence_weight: number;
}

interface AssetDetail {
  id: string;
  scan_id: string;
  name: string;
  asset_type: string;
  llm_or_model: string | null;
  provider: string;
  location: string;
  application: string;
  purpose: string;
  discovery_source: string;
  status: string;
  confidence_score: number;
  evidence: Evidence[];
}

async function fetchAsset(id: string): Promise<AssetDetail | null> {
  try {
    const res = await fetch(`${API_BASE}/assets/${id}`, { cache: "no-store" });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const asset = await fetchAsset(id);
  if (!asset) return { title: "Asset Not Found — FLYYY.AI" };
  return {
    title: `${asset.name} — FLYYY.AI Asset Detail`,
    description: `AI asset detail: ${asset.purpose}. Provider: ${asset.provider}. Status: ${asset.status}.`,
  };
}

function ConfidenceExplainer({ status, score }: { status: string; score: number }) {
  const pct = Math.round(score * 100);
  const isDiscovered = status === "Discovered";

  return (
    <div
      className="card"
      style={{
        background: isDiscovered
          ? "rgba(16,185,129,0.05)"
          : "rgba(245,158,11,0.05)",
        borderColor: isDiscovered
          ? "rgba(16,185,129,0.2)"
          : "rgba(245,158,11,0.2)",
      }}
      role="region"
      aria-label="Confidence explanation"
    >
      <div className="flex items-center gap-3 mb-3">
        <StatusBadge status={status} />
        <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>
          Confidence: {pct}%
        </span>
      </div>
      <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
        {isDiscovered ? (
          <>
            <strong style={{ color: "var(--emerald)" }}>Discovered</strong> — This asset
            has both a direct library import <em>and</em> an explicit model name string
            in the source code, making the AI integration unambiguously identified.
          </>
        ) : (
          <>
            <strong style={{ color: "var(--amber)" }}>Inferred</strong> — Evidence is
            partial or indirect (e.g., only an environment variable key or a manifest
            dependency was found, without a direct import or explicit model name). The
            integration is likely but not confirmed from source code alone.
          </>
        )}
      </p>
      <div className="confidence-bar mt-3" style={{ height: 5 }}>
        <div className="confidence-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default async function AssetDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const asset = await fetchAsset(id);

  if (!asset) notFound();

  const typeCls =
    asset.asset_type === "AI Agent"
      ? "type-ai-agent"
      : asset.asset_type === "AI Application"
      ? "type-ai-application"
      : "type-model-integration";

  const fields = [
    { label: "Type", value: <span className={`type-badge ${typeCls}`}>{asset.asset_type}</span> },
    { label: "Provider", value: asset.provider },
    { label: "Model / LLM", value: asset.llm_or_model ?? "Not resolved" },
    { label: "Application", value: asset.application },
    { label: "Location", value: asset.location },
    { label: "Discovery Source", value: asset.discovery_source },
  ];

  return (
    <>
      {/* Back link */}
      <Link href="/assets" className="back-link" aria-label="Back to asset inventory">
        ← Back to Inventory
      </Link>

      {/* Page header */}
      <div className="page-header">
        <div className="page-eyebrow">
          <span aria-hidden="true">◈</span> Asset Detail
        </div>
        <h1 className="page-title" style={{ fontSize: "1.75rem" }}>
          {asset.name}
        </h1>
        <p className="page-subtitle">{asset.purpose}</p>
      </div>

      {/* Confidence / status card */}
      <ConfidenceExplainer status={asset.status} score={asset.confidence_score} />

      <hr className="divider" />

      {/* Field grid */}
      <section aria-labelledby="fields-heading">
        <h2 id="fields-heading" className="section-heading">Asset Fields</h2>
        <div className="field-grid">
          {fields.map(({ label, value }) => (
            <div key={label} className="field-item">
              <div className="field-label">{label}</div>
              <div className="field-value">{value}</div>
            </div>
          ))}
        </div>
      </section>

      <hr className="divider" />

      {/* Evidence section */}
      <section aria-labelledby="evidence-heading">
        <h2 id="evidence-heading" className="section-heading">
          Evidence ({asset.evidence.length} signal{asset.evidence.length !== 1 ? "s" : ""})
        </h2>
        <p
          style={{
            fontSize: "0.8rem",
            color: "var(--text-muted)",
            marginBottom: "1rem",
          }}
        >
          Each evidence record is a raw signal extracted directly from source code or
          dependency manifests. These are the traceable facts that produced this asset.
        </p>
        <EvidenceList evidence={asset.evidence} />
      </section>

      {/* Scan link */}
      <hr className="divider" />
      <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
        Scan ID:{" "}
        <span className="mono" style={{ color: "var(--text-secondary)" }}>
          {asset.scan_id}
        </span>
      </div>
    </>
  );
}
