"use client";

import { Info } from "lucide-react";

export function DemoBanner() {
  return (
    <div
      className="flex items-center gap-2 px-4 py-2 text-xs"
      style={{
        background: "var(--accent-muted)",
        borderBottom: "1px solid var(--accent)",
        color: "var(--accent)",
      }}
      role="status"
      aria-label="Demo mode active"
    >
      <Info className="h-3.5 w-3.5 shrink-0" aria-hidden />
      <span>
        Demo data — showing real EngiNerd scan (52 findings, 15 actionable).
        Start the AuditAgent daemon for live scans.
      </span>
      <code
        className="ml-1 rounded px-1.5 py-0.5 font-mono text-xs"
        style={{ background: "var(--accent-muted)" }}
      >
        python -m jarvis_core.daemon
      </code>
    </div>
  );
}
