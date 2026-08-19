interface Evidence {
  id: string;
  file_path: string;
  line_number: number;
  signal_type: string;
  matched_value: string;
  snippet: string;
  confidence_weight: number;
}

function formatPath(filePath: string): string {
  // Show last 3 path segments for readability
  const parts = filePath.replace(/\\/g, "/").split("/");
  return parts.slice(-3).join("/");
}

function SignalChip({ type }: { type: string }) {
  const label: Record<string, string> = {
    LIBRARY_IMPORT: "Library Import",
    MODEL_NAME_STRING: "Model Name",
    ENV_VAR_KEY: "Env Key",
    MANIFEST_DEPENDENCY: "Manifest Dep",
    API_ENDPOINT: "API Endpoint",
  };
  return (
    <span className={`signal-chip signal-${type}`} title={type}>
      {label[type] ?? type}
    </span>
  );
}

export default function EvidenceList({ evidence }: { evidence: Evidence[] }) {
  if (!evidence || evidence.length === 0) {
    return (
      <div className="empty-state" style={{ padding: "2rem 0" }}>
        <p className="text-muted">No evidence records linked to this asset.</p>
      </div>
    );
  }

  return (
    <ol
      style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0.75rem" }}
      aria-label="Evidence records"
    >
      {evidence.map((ev) => (
        <li key={ev.id} className="evidence-item" id={`evidence-${ev.id}`}>
          {/* Header */}
          <div className="evidence-header">
            <SignalChip type={ev.signal_type} />
            <span className="evidence-path" title={ev.file_path}>
              {formatPath(ev.file_path)}
            </span>
            {ev.line_number > 0 && (
              <span className="evidence-line">line {ev.line_number}</span>
            )}
            <span
              style={{
                marginLeft: "auto",
                fontSize: "0.68rem",
                color: "var(--text-muted)",
                fontFamily: "var(--font-mono)",
              }}
              title="Confidence weight of this signal"
            >
              w={ev.confidence_weight.toFixed(2)}
            </span>
          </div>

          {/* Matched value */}
          <div style={{ padding: "0.5rem 1rem 0" }}>
            <span
              style={{
                fontSize: "0.72rem",
                color: "var(--text-muted)",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.06em",
              }}
            >
              Matched value:
            </span>{" "}
            <code
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "0.82rem",
                color: "var(--accent-light)",
                fontWeight: 600,
              }}
            >
              {ev.matched_value}
            </code>
          </div>

          {/* Code snippet */}
          <div style={{ padding: "0.5rem 1rem 0.75rem" }}>
            <pre className="code-block" aria-label="Code snippet">
              {ev.snippet}
            </pre>
          </div>
        </li>
      ))}
    </ol>
  );
}
