import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Outfit } from "next/font/google";
import "./globals.css";

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

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} ${mono.variable}`}>
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
