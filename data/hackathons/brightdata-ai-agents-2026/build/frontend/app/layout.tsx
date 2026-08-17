import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
  preload: true,
});

export const metadata: Metadata = {
  title: {
    default: "AltBrief — AI-Powered Investment Brief",
    template: "%s | AltBrief",
  },
  description:
    "Bloomberg charges $24K/year and won't show its sources. AltBrief is free, conversational, and every signal links to the peer-reviewed paper behind it.",
  keywords: [
    "investment research",
    "alternative data",
    "stock analysis",
    "AI finance",
    "BrightData",
    "SEC EDGAR",
    "insider trading",
    "Glassdoor signals",
  ],
  openGraph: {
    type: "website",
    siteName: "AltBrief",
    title: "AltBrief — AI Investment Brief",
    description:
      "Free AI-powered investment brief with alt-data signals, cross-source contradiction detection, and peer-reviewed citations.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: "#0A0E1A",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable}`}
      suppressHydrationWarning
    >
      <body className="antialiased font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
