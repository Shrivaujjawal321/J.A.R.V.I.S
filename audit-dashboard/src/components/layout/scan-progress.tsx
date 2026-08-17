"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { useQueryClient } from "@tanstack/react-query";
import type { AuditRunView } from "@/lib/types";
import { ScannerChip } from "@/components/ui/scanner-chip";
import { cancelAudit } from "@/lib/api";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

const SCANNERS = ["semgrep", "trivy", "osv", "gitleaks", "trufflehog"];

function getScannerStates(
  run: AuditRunView
): Record<string, "queued" | "running" | "done"> {
  const pct = run.progress_pct;
  const states: Record<string, "queued" | "running" | "done"> = {};

  // Simulate which scanners are done based on progress
  const doneCount = Math.floor((pct / 100) * SCANNERS.length);
  const isRunning = pct > 0 && pct < 100;

  SCANNERS.forEach((s, i) => {
    if (i < doneCount) {
      states[s] = "done";
    } else if (isRunning && i === doneCount) {
      states[s] = "running";
    } else {
      states[s] = "queued";
    }
  });

  return states;
}

interface ScanProgressProps {
  run: AuditRunView;
  findingCount: number;
  fpCount: number;
  onCancel?: () => void;
}

export function ScanProgress({
  run,
  findingCount,
  fpCount,
  onCancel,
}: ScanProgressProps) {
  const shouldReduce = useReducedMotion();
  const scannerStates = getScannerStates(run);

  return (
    <div
      className="rounded-xl border p-5 space-y-4"
      style={{
        background: "var(--surface)",
        borderColor: "var(--border)",
      }}
      role="status"
      aria-label={`Scan in progress: ${run.progress_pct}% complete`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className="inline-flex h-2 w-2 rounded-full"
              style={{ background: "var(--accent)" }}
              aria-hidden
            />
            <span className="text-sm font-semibold" style={{ color: "var(--text)" }}>
              Scanning…
            </span>
          </div>
          <span
            className="truncate text-xs font-mono"
            style={{ color: "var(--text-muted)" }}
          >
            {run.target_uri}
          </span>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-sm font-bold tabular-nums" style={{ color: "var(--text)" }}>
            {run.progress_pct}%
          </span>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="rounded p-1 transition-colors hover:bg-[var(--surface-raised)]"
              style={{ color: "var(--text-muted)" }}
              aria-label="Cancel scan"
            >
              <X className="h-4 w-4" aria-hidden />
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div
        className="relative h-1.5 w-full overflow-hidden rounded-full"
        style={{ background: "var(--surface-overlay)" }}
        role="progressbar"
        aria-valuenow={run.progress_pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ background: "var(--accent)" }}
          initial={{ width: 0 }}
          animate={{ width: `${run.progress_pct}%` }}
          transition={{ duration: shouldReduce ? 0 : 0.5, ease: "easeOut" }}
        />
      </div>

      {/* Scanner chips */}
      <div className="flex flex-wrap gap-2" role="list" aria-label="Scanner status">
        {SCANNERS.map((s) => (
          <div key={s} role="listitem">
            <ScannerChip
              scanner={s}
              state={scannerStates[s] ?? "queued"}
            />
          </div>
        ))}
      </div>

      {/* Live finding counter */}
      <div
        className="text-sm"
        style={{ color: "var(--text-muted)" }}
        aria-live="polite"
        aria-atomic="true"
      >
        <span className="font-semibold tabular-nums" style={{ color: "var(--text)" }}>
          {findingCount}
        </span>{" "}
        findings
        {fpCount > 0 && (
          <>
            {" · "}
            <span
              className="tabular-nums"
              style={{ color: "var(--critical)" }}
            >
              {fpCount}
            </span>{" "}
            filtered as FP
          </>
        )}
      </div>

      {/* State label */}
      <div className="text-xs" style={{ color: "var(--text-subtle)" }}>
        State:{" "}
        <span className="font-mono" style={{ color: "var(--text-muted)" }}>
          {run.audit_state}
        </span>
      </div>
    </div>
  );
}
