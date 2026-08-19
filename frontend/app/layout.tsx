import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Outfit } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const outfit = Outfit({
  variable: "--font-heading",
  subsets: ["latin"],
  display: "swap",
});

const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "FLYYY.AI — AI Asset Discovery",
  description:
    "Automatically discover, inventory, and govern AI usage across your codebase. Evidence-backed AI asset discovery for security and governance teams.",
  keywords: ["AI governance", "AI discovery", "LLM inventory", "AI security"],
  openGraph: {
    title: "FLYYY.AI — AI Asset Discovery Platform",
    description: "Automatically discover AI usage across your codebase.",
    type: "website",
  },
};

import { ToastProvider } from "@/components/Toast";

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} ${mono.variable}`}>
      <body>
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
      </body>
    </html>
  );
}
