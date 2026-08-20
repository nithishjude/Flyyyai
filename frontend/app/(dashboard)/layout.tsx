import Link from "next/link";
import { ToastProvider } from "@/components/Toast";

export default function DashboardLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="app-shell">
      {/* Top navigation bar */}
      <nav className="navbar" role="navigation" aria-label="Main navigation">
        <div className="navbar-inner">
          <Link href="/" className="brand" aria-label="FLYYY.AI home">
            <span className="brand-icon" aria-hidden="true">⬡</span>
            <span className="brand-name">FLYYY<span className="brand-dot">.AI</span></span>
            <span className="brand-tag">Asset Discovery</span>
          </Link>

          <div className="navbar-links">
            <Link href="/scan" className="nav-link">
              <span className="nav-icon">⊕</span> New Scan
            </Link>
            <Link href="/assets" className="nav-link">
              <span className="nav-icon">◈</span> Inventory
            </Link>
            <Link href="/scans" className="nav-link">
              <span className="nav-icon">⊙</span> Scans History
            </Link>
          </div>
        </div>
      </nav>

      {/* Main content area */}
      <main className="main-content">
        <ToastProvider>
          {children}
        </ToastProvider>
      </main>

      {/* Footer */}
      <footer className="footer" role="contentinfo">
        <p>FLYYY.AI Asset Discovery &nbsp;·&nbsp; v1.0.0 &nbsp;·&nbsp; Built for governance teams</p>
      </footer>
    </div>
  );
}
