import { Suspense } from "react";
import { AuditResultsClient } from "../results-client";

export const metadata = {
  title: "AuditAgent — EngiNerd Scan Results",
};

export default function DemoResultsPage() {
  return (
    <Suspense
      fallback={
        <div
          className="flex h-screen items-center justify-center"
          style={{ background: "var(--bg)", color: "var(--text-muted)" }}
          aria-live="polite"
        >
          Loading scan results…
        </div>
      }
    >
      <AuditResultsClient auditId="demo" />
    </Suspense>
  );
}
