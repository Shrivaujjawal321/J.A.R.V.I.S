import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Nav } from "@/components/ui/nav";
import { SwKiller } from "@/components/sw-killer";
import { QueryProvider } from "@/providers/query-provider";
import { AuditStoreProvider } from "@/providers/audit-store-provider";
import { AuthProvider } from "@/providers/auth-provider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
  adjustFontFallback: true,
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
  adjustFontFallback: true,
});

export const metadata: Metadata = {
  title: "E.D.I.T.H — Dataset Quality Scoring for Tata Steel",
  description:
    "E.D.I.T.H grades your industrial dataset and shows you exactly how to make it better. Upload a CSV, XLSX, or JSON file to get a composite quality score, dimension breakdown, and actionable improvement coaching.",
  keywords: ["dataset quality", "data scoring", "industrial data", "steel", "ML readiness", "EDITH"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[var(--color-bg)] text-[var(--color-fg)]`}
      >
        <SwKiller />
        {/* Skip to main content — WCAG 2.4.1 */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[9999] focus:px-4 focus:py-2 focus:rounded-lg focus:text-sm focus:font-medium"
          style={{ backgroundColor: "var(--color-accent-400)", color: "var(--color-fg-on-accent)" }}
        >
          Skip to main content
        </a>
        <QueryProvider>
          <AuthProvider>
            <AuditStoreProvider>
              <Nav />
              <main id="main-content">{children}</main>
            </AuditStoreProvider>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
