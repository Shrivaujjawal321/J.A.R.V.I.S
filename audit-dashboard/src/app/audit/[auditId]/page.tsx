import { Suspense } from "react";
import { AuditResultsClient } from "../results-client";

interface Props {
  params: Promise<{ auditId: string }>;
}

export default async function AuditResultsPage({ params }: Props) {
  const { auditId } = await params;
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
      <AuditResultsClient auditId={auditId} />
    </Suspense>
  );
}
