import type { Metadata } from "next";
import Link from "next/link";
import DeleteScanButton from "./DeleteScanButton"; // Client component for delete action

export const metadata: Metadata = {
  title: "Scan History — FLYYY.AI",
  description: "View history of all AI asset discovery scans.",
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Scan {
  id: string;
  repo_url: string;
  status: string;
  asset_count: number;
  started_at: string;
  completed_at: string | null;
}

interface ScanListResponse {
  scans: Scan[];
  total: number;
}

async function fetchScans(): Promise<ScanListResponse> {
  try {
    const res = await fetch(`${API_BASE}/scans`, { cache: "no-store" });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  } catch {
    return { scans: [], total: 0 };
  }
}

export default async function ScansPage() {
  const data = await fetchScans();

  return (
    <>
      <div className="page-header">
        <div className="page-eyebrow">
          <span aria-hidden="true">⊙</span> Scan History
        </div>
        <h1 className="page-title">
          Discovery <span className="gradient-text">Scans</span>
        </h1>
        <p className="page-subtitle">
          {data.total > 0
            ? `Showing ${data.total} scan${data.total !== 1 ? "s" : ""} across all repositories.`
            : "No scans have been run yet."}
        </p>
      </div>

      {data.scans.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon" aria-hidden="true">⊙</div>
          <p className="empty-title">No scan history</p>
          <p className="empty-subtitle text-muted">
            Run a scan from the{" "}
            <Link href="/" style={{ color: "var(--accent-light)" }}>
              home page
            </Link>{" "}
            to get started.
          </p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="scan-table">
            <thead>
              <tr>
                <th>Scan ID</th>
                <th>Repository</th>
                <th>Status</th>
                <th>Assets</th>
                <th>Time</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.scans.map((scan) => (
                <tr key={scan.id}>
                  <td className="mono" style={{ fontSize: "0.85rem" }}>
                    <Link href={`/assets?scan_id=${scan.id}`} style={{ color: "var(--accent-light)", textDecoration: "none" }}>
                      {scan.id.split("-")[0]}
                    </Link>
                  </td>
                  <td>{scan.repo_url}</td>
                  <td>
                    <span className={`status-badge status-${scan.status.toLowerCase()}`}>
                      {scan.status}
                    </span>
                  </td>
                  <td>
                    <strong>{scan.asset_count}</strong>
                  </td>
                  <td className="text-muted" style={{ fontSize: "0.85rem" }}>
                    {new Date(scan.started_at).toLocaleString()}
                  </td>
                  <td>
                    <div className="flex gap-2">
                      <Link href={`/assets?scan_id=${scan.id}`} className="btn btn-secondary" style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}>
                        View
                      </Link>
                      <DeleteScanButton scanId={scan.id} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
