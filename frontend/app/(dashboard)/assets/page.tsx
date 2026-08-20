"use client";

import { Suspense } from "react";
import { useEffect, useState, useMemo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import AssetCard from "@/components/AssetCard";
import SkeletonCard from "@/components/SkeletonCard";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

interface AssetsResponse {
  assets: Asset[];
  total: number;
  scan_id: string | null;
}

function AssetsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const scanId = searchParams.get("scan_id") || undefined;
  
  const [data, setData] = useState<AssetsResponse>({ assets: [], total: 0, scan_id: null });
  const [isLoading, setIsLoading] = useState(true);
  
  // Client-side filtering state for quick interactions
  const [filterStatus, setFilterStatus] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 24;

  useEffect(() => {
    let url = `${API_BASE}/assets?limit=500`;
    if (scanId) {
      url = `${API_BASE}/assets?scan_id=${scanId}&limit=500`;
    }
    
    setIsLoading(true);
    fetch(url)
      .then(res => res.ok ? res.json() : { assets: [], total: 0, scan_id: null })
      .then(data => {
        setData(data);
        setIsLoading(false);
      })
      .catch(() => {
        setData({ assets: [], total: 0, scan_id: null });
        setIsLoading(false);
      });
  }, [scanId]);

  const counts = useMemo(() => {
    return {
      discovered: data.assets.filter((a) => a.status === "Discovered").length,
      inferred: data.assets.filter((a) => a.status === "Inferred").length,
      pending: data.assets.filter((a) => a.status === "Pending Review").length,
    };
  }, [data.assets]);

  const filteredAssets = useMemo(() => {
    return data.assets.filter(a => {
      if (filterStatus !== "All" && a.status !== filterStatus) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (
          a.name.toLowerCase().includes(q) ||
          a.provider.toLowerCase().includes(q) ||
          (a.llm_or_model && a.llm_or_model.toLowerCase().includes(q))
        );
      }
      return true;
    });
  }, [data.assets, filterStatus, searchQuery]);

  const totalPages = Math.ceil(filteredAssets.length / itemsPerPage);
  const paginatedAssets = filteredAssets.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filterStatus, searchQuery]);

  return (
    <div className="page-fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="page-eyebrow">
          <span aria-hidden="true">◈</span> AI Asset Inventory
        </div>
        <h1 className="page-title">
          Discovered <span className="gradient-text">AI Assets</span>
        </h1>
        <p className="page-subtitle">
          {data.total > 0
            ? `${data.total} asset${data.total !== 1 ? "s" : ""} found${scanId ? " in this scan" : ""}. Click an asset to see the full evidence chain.`
            : "No assets found yet. Run a scan from the home page."}
        </p>
      </div>

      {/* Filter & Stats bar */}
      <div className="stats-bar flex-wrap gap-4" role="group" aria-label="Asset filters and statistics">
        <div className="flex gap-2">
          <button 
            className={`filter-chip ${filterStatus === "All" ? "filter-chip-active" : ""}`}
            onClick={() => setFilterStatus("All")}
          >
            All <span className="stat-value">&nbsp;{data.total}</span>
          </button>
          <button 
            className={`filter-chip ${filterStatus === "Discovered" ? "filter-chip-active" : ""}`}
            onClick={() => setFilterStatus("Discovered")}
          >
            <span style={{ color: "var(--emerald)" }}>●</span> Discovered <span className="stat-value">&nbsp;{counts.discovered}</span>
          </button>
          <button 
            className={`filter-chip ${filterStatus === "Inferred" ? "filter-chip-active" : ""}`}
            onClick={() => setFilterStatus("Inferred")}
          >
            <span style={{ color: "var(--amber)" }}>●</span> Inferred <span className="stat-value">&nbsp;{counts.inferred}</span>
          </button>
        </div>

        <div className="flex-1 min-w-[200px]">
          <input 
            type="text" 
            className="form-input w-full" 
            placeholder="Search provider, model, or app name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ padding: "0.4rem 0.8rem" }}
          />
        </div>
      </div>

      {/* Asset grid or empty state */}
      {isLoading ? (
        <section aria-label="Loading assets">
          <div className="asset-grid">
            {Array.from({ length: 8 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </section>
      ) : filteredAssets.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon" aria-hidden="true">◈</div>
          <p className="empty-title">No assets match your filters</p>
          {data.assets.length === 0 && (
            <p className="empty-subtitle text-muted">
              Run a scan from the{" "}
              <Link href="/" style={{ color: "var(--accent-light)" }}>
                home page
              </Link>{" "}
              to populate this inventory.
            </p>
          )}
        </div>
      ) : (
        <>
          <section aria-label="AI asset cards">
            <div className="asset-grid">
              {paginatedAssets.map((asset) => (
                <AssetCard key={asset.id} asset={asset} />
              ))}
            </div>
          </section>

          {totalPages > 1 && (
            <div className="pagination flex justify-center items-center gap-4 mt-8">
              <button 
                className="btn btn-secondary" 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              <span className="text-muted" style={{ fontSize: "0.9rem" }}>
                Page {currentPage} of {totalPages}
              </span>
              <button 
                className="btn btn-secondary" 
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default function AssetsPage() {
  return (
    <Suspense fallback={
      <div className="asset-grid">
        {Array.from({ length: 8 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    }>
      <AssetsContent />
    </Suspense>
  );
}
