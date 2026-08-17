import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "THE EDITH — Industrial Maintenance Cockpit",
  description: "Agentic maintenance wizard for steel plant operations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full" style={{ colorScheme: "dark" }}>
      <body className="h-full overflow-hidden" style={{ background: "oklch(8% 0.018 250)" }}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
