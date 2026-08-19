export default function SkeletonCard() {
  return (
    <div className="asset-card skeleton-card" aria-hidden="true">
      <div className="asset-card-badges flex gap-2 mb-3">
        <div className="skeleton-pill" style={{ width: "80px", height: "24px" }} />
        <div className="skeleton-pill" style={{ width: "100px", height: "24px" }} />
      </div>
      
      <div className="skeleton-text mb-4" style={{ width: "70%", height: "20px" }} />
      
      <div className="asset-meta" style={{ display: "grid", gap: "8px" }}>
        <div className="skeleton-text" style={{ width: "100%", height: "16px" }} />
        <div className="skeleton-text" style={{ width: "90%", height: "16px" }} />
        <div className="skeleton-text" style={{ width: "95%", height: "16px" }} />
      </div>
      
      <div className="mt-4 pt-3" style={{ borderTop: "1px solid var(--border)" }}>
        <div className="skeleton-text" style={{ width: "40%", height: "14px" }} />
      </div>
    </div>
  );
}
