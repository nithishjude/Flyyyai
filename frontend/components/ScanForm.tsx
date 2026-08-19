"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type ScanState = "idle" | "scanning" | "success" | "error";

interface ScanResult {
  id: string;
  status: string;
  asset_count: number;
  repo_url: string;
  error_message?: string;
}

export default function ScanForm() {
  const [repoPath, setRepoPath] = useState("");
  const [scanState, setScanState] = useState<ScanState>("idle");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  async function handleScan(e: React.FormEvent) {
    e.preventDefault();
    if (!repoPath.trim()) return;

    setScanState("scanning");
    setResult(null);
    setErrorMsg("");

    try {
      const res = await fetch(`${API_BASE}/scans`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoPath.trim() }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `Server error: ${res.status}`);
      }

      let data: ScanResult = await res.json();

      // Poll until background scan is completed or failed
      while (data.status === "pending" || data.status === "running") {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const pollRes = await fetch(`${API_BASE}/scans/${data.id}`);
        if (!pollRes.ok) throw new Error(`Polling failed: ${pollRes.status}`);
        data = await pollRes.json();
      }

      if (data.status === "failed") {
        throw new Error(data.error_message || "Scan failed during execution.");
      }

      setResult(data);
      setScanState("success");
    } catch (err: unknown) {
      setScanState("error");
      setErrorMsg(err instanceof Error ? err.message : "An unexpected error occurred");
    }
  }

  function handleViewAssets() {
    if (result) {
      router.push(`/assets?scan_id=${result.id}`);
    }
  }

  function handleReset() {
    setScanState("idle");
    setResult(null);
    setErrorMsg("");
    setTimeout(() => inputRef.current?.focus(), 100);
  }

  return (
    <div className="scan-form-card slide-up delay-100">
      {/* Path input */}
      <form onSubmit={handleScan} id="scan-form" aria-label="Repository scan form">
        <div className="form-group">
          <label htmlFor="repo-path-input" className="form-label">
            Repository Path
          </label>
          <div className="flex gap-3">
            <input
              ref={inputRef}
              id="repo-path-input"
              className="form-input"
              type="text"
              placeholder="d:/fly/testbed  or  /home/user/myproject"
              value={repoPath}
              onChange={(e) => setRepoPath(e.target.value)}
              disabled={scanState === "scanning"}
              autoComplete="off"
              spellCheck={false}
              aria-describedby="path-hint"
              suppressHydrationWarning={true}
            />
            <button
              id="start-scan-btn"
              type="submit"
              className="btn btn-primary"
              disabled={scanState === "scanning" || !repoPath.trim()}
              aria-busy={scanState === "scanning"}
            >
              {scanState === "scanning" ? (
                <>
                  <span className="spinner" aria-hidden="true" />
                  Scanning…
                </>
              ) : (
                <>
                  <span aria-hidden="true">▶</span> Run Scan
                </>
              )}
            </button>
          </div>
          <p id="path-hint" className="text-muted mt-1" style={{ fontSize: "0.78rem" }}>
            Provide an absolute local path to a repository. The scanner will discover AI usage across all Python and JS/TS files.
          </p>
        </div>
      </form>

      {/* Scanning progress */}
      {scanState === "scanning" && (
        <div className="alert alert-info mt-4 fade-in" role="status" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          <div>
            <strong>Scanning in progress…</strong>
            <p className="mt-1" style={{ fontSize: "0.8rem", opacity: 0.8 }}>
              Walking files, extracting evidence, and synthesising AI assets. This may take a few seconds.
            </p>
          </div>
        </div>
      )}

      {/* Success result */}
      {scanState === "success" && result && (
        <div className="mt-4 slide-up" role="region" aria-label="Scan results">
          <div className="alert alert-success">
            <span aria-hidden="true">✓</span>
            <div>
              <strong>Scan complete!</strong> Found{" "}
              <strong>{result.asset_count}</strong> AI asset
              {result.asset_count !== 1 ? "s" : ""} in{" "}
              <code className="mono" style={{ fontSize: "0.8em", opacity: 0.85 }}>{result.repo_url}</code>
            </div>
          </div>

          <div className="flex gap-3 mt-4">
            <button
              id="view-assets-btn"
              className="btn btn-primary"
              onClick={handleViewAssets}
              aria-label={`View ${result.asset_count} discovered assets`}
            >
              <span aria-hidden="true">◈</span> View Assets
            </button>
            <button
              id="new-scan-btn"
              className="btn btn-secondary"
              onClick={handleReset}
              aria-label="Start a new scan"
            >
              New Scan
            </button>
          </div>
        </div>
      )}

      {/* Error result */}
      {scanState === "error" && (
        <div className="mt-4" role="alert" aria-live="assertive">
          <div className="alert alert-error">
            <span aria-hidden="true">✕</span>
            <div>
              <strong>Scan failed</strong>
              <p className="mt-1" style={{ fontSize: "0.82rem", opacity: 0.85 }}>{errorMsg}</p>
            </div>
          </div>
          <button
            id="retry-scan-btn"
            className="btn btn-secondary mt-3"
            onClick={handleReset}
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}
