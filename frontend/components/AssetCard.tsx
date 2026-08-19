import Link from "next/link";
import StatusBadge from "./StatusBadge";

interface Asset {
  id: string;
  name: string;
  asset_type: string;
  llm_or_model: string | null;
  provider: string;
  application: string;
  status: string;
  confidence_score: number;
  discovery_source: string;
}

export default function AssetCard({ asset }: { asset: Asset }) {
  const typeCls =
    asset.asset_type === "AI Agent"
      ? "type-ai-agent"
      : asset.asset_type === "AI Application"
      ? "type-ai-application"
      : "type-model-integration";

  const confPct = Math.round(asset.confidence_score * 100);

  return (
    <Link
      href={`/assets/${asset.id}`}
      className="asset-card"
      id={`asset-card-${asset.id}`}
      aria-label={`View details for ${asset.name}`}
    >
      {/* Badges row */}
      <div className="asset-card-badges">
        <StatusBadge status={asset.status} />
        <span className={`type-badge ${typeCls}`}>{asset.asset_type}</span>
      </div>

      {/* Name */}
      <div className="asset-name">{asset.name}</div>

      {/* Meta grid */}
      <div className="asset-meta">
        <span className="asset-meta-key">Provider</span>
        <span className="asset-meta-value">{asset.provider}</span>

        <span className="asset-meta-key">Application</span>
        <span className="asset-meta-value">{asset.application}</span>

        <span className="asset-meta-key">Model</span>
        <span className="asset-meta-value">
          {asset.llm_or_model ?? <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>Not resolved</span>}
        </span>

        <span className="asset-meta-key">Source</span>
        <span className="asset-meta-value">{asset.discovery_source}</span>
      </div>

      {/* Confidence bar */}
      <div className="confidence-bar" role="progressbar" aria-valuenow={confPct} aria-valuemin={0} aria-valuemax={100} aria-label={`Confidence: ${confPct}%`}>
        <div className="confidence-fill" style={{ width: `${confPct}%` }} />
      </div>
      <div className="flex items-center mt-2 gap-2" style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
        <span>Confidence</span>
        <span style={{ color: confPct >= 70 ? "var(--emerald)" : confPct >= 45 ? "var(--amber)" : "var(--slate)", fontWeight: 700 }}>
          {confPct}%
        </span>
      </div>
    </Link>
  );
}
