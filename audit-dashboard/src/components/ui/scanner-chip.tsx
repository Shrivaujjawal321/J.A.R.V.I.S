"use client";

import { cn } from "@/lib/utils";
import { SCANNER_LABELS } from "@/lib/types";
import { CheckCircle2, Loader2, Clock } from "lucide-react";

type ScannerState = "queued" | "running" | "done";

interface ScannerChipProps {
  scanner: string;
  state: ScannerState;
  count?: number;
  className?: string;
}

export function ScannerChip({
  scanner,
  state,
  count,
  className,
}: ScannerChipProps) {
  const label = SCANNER_LABELS[scanner] ?? scanner;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-xs font-medium transition-colors",
        state === "queued" &&
          "border-[var(--border)] bg-[var(--surface)] text-[var(--text-muted)]",
        state === "running" &&
          "border-[var(--accent)] bg-[var(--accent-muted)] text-[var(--accent)]",
        state === "done" &&
          "border-[var(--border)] bg-[var(--surface-raised)] text-[var(--text)]",
        className
      )}
      aria-label={`${label}: ${state}${count !== undefined ? `, ${count} findings` : ""}`}
    >
      {state === "queued" && <Clock className="h-3 w-3" aria-hidden />}
      {state === "running" && (
        <Loader2 className="h-3 w-3 animate-spin" aria-hidden />
      )}
      {state === "done" && (
        <CheckCircle2 className="h-3 w-3 text-[var(--accent)]" aria-hidden />
      )}
      <span>{label}</span>
      {state === "done" && count !== undefined && (
        <span className="ml-0.5 text-[var(--text-muted)]">{count}</span>
      )}
    </span>
  );
}
