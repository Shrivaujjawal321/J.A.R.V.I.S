"use client";

import { useRef, useMemo } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useQueryState } from "nuqs";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import type { Finding, Severity, VerificationStatus } from "@/lib/types";
import { cn, formatPath, cweCode, cweLabel } from "@/lib/utils";
import { SeverityDot, SeverityBadge } from "@/components/ui/severity-badge";
import { VerificationChip } from "@/components/ui/verification-chip";
import { Shield } from "lucide-react";

interface FindingsTableProps {
  findings: Finding[];
  onFindingClick: (id: string) => void;
  activeFindingId?: string | null;
}

const SEVERITY_ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];

function applyFilters(
  findings: Finding[],
  {
    severity,
    status,
    scanner,
    rule,
    file,
  }: {
    severity: string;
    status: string;
    scanner: string;
    rule: string;
    file: string;
  }
): Finding[] {
  let result = [...findings];

  if (severity) {
    const sevs = severity.split(",").filter(Boolean);
    result = result.filter((f) => sevs.includes(f.severity));
  }
  if (status) {
    const statuses = status.split(",").filter(Boolean);
    result = result.filter((f) => statuses.includes(f.verification_status));
  }
  if (scanner) {
    const scanners = scanner.split(",").filter(Boolean);
    result = result.filter((f) => scanners.includes(f.scanner));
  }
  if (rule) {
    const q = rule.toLowerCase();
    result = result.filter(
      (f) =>
        f.rule_id.toLowerCase().includes(q) ||
        (f.cwe?.toLowerCase().includes(q) ?? false)
    );
  }
  if (file) {
    const q = file.toLowerCase();
    result = result.filter((f) =>
      (f.file_path?.toLowerCase().includes(q) ?? false)
    );
  }

  return result;
}

type GroupItem =
  | { type: "header"; label: string; count: number }
  | { type: "finding"; finding: Finding };

function groupFindings(
  findings: Finding[],
  groupBy: string
): GroupItem[] {
  if (groupBy === "rule") {
    const groups = new Map<string, Finding[]>();
    for (const f of findings) {
      const key = f.rule_id;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(f);
    }
    const items: GroupItem[] = [];
    for (const [key, fs] of groups) {
      items.push({ type: "header", label: key, count: fs.length });
      for (const f of fs) items.push({ type: "finding", finding: f });
    }
    return items;
  }

  if (groupBy === "file") {
    const groups = new Map<string, Finding[]>();
    for (const f of findings) {
      const key = f.file_path ?? "(no file)";
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(f);
    }
    const items: GroupItem[] = [];
    for (const [key, fs] of groups) {
      items.push({ type: "header", label: formatPath(key), count: fs.length });
      for (const f of fs) items.push({ type: "finding", finding: f });
    }
    return items;
  }

  // Default: by severity
  const items: GroupItem[] = [];
  for (const sev of SEVERITY_ORDER) {
    const sevFindings = findings.filter((f) => f.severity === sev);
    if (sevFindings.length === 0) continue;
    items.push({
      type: "header",
      label: sev.charAt(0).toUpperCase() + sev.slice(1),
      count: sevFindings.length,
    });
    for (const f of sevFindings) {
      items.push({ type: "finding", finding: f });
    }
  }
  return items;
}

export function FindingsTable({
  findings,
  onFindingClick,
  activeFindingId,
}: FindingsTableProps) {
  const shouldReduce = useReducedMotion();
  const [severity] = useQueryState("severity", { defaultValue: "" });
  const [status] = useQueryState("status", { defaultValue: "" });
  const [scanner] = useQueryState("scanner", { defaultValue: "" });
  const [rule] = useQueryState("rule", { defaultValue: "" });
  const [file] = useQueryState("file", { defaultValue: "" });
  const [groupBy] = useQueryState("groupBy", { defaultValue: "severity" });

  const filtered = useMemo(
    () => applyFilters(findings, { severity, status, scanner, rule, file }),
    [findings, severity, status, scanner, rule, file]
  );

  const items = useMemo(
    () => groupFindings(filtered, groupBy),
    [filtered, groupBy]
  );

  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: (i) => (items[i]?.type === "header" ? 28 : 36),
    overscan: 10,
  });

  // All-FP empty state
  if (filtered.length === 0 && findings.length > 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <div
          className="flex h-14 w-14 items-center justify-center rounded-full border-2"
          style={{
            borderColor: "oklch(0.68 0.15 255 / 0.3)",
            background: "oklch(0.68 0.15 255 / 0.08)",
          }}
        >
          <Shield
            className="h-7 w-7"
            style={{ color: "oklch(0.68 0.15 255)" }}
            aria-hidden
          />
        </div>
        <h3 className="text-base font-semibold" style={{ color: "var(--text)" }}>
          No findings match current filters
        </h3>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          {findings.length} analyzed — try adjusting the filters above
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      {/* Table header */}
      <div
        className="sticky top-0 z-10 grid grid-cols-[6rem_1fr_5rem_10rem_6rem_4.5rem] gap-3 px-3 py-1.5 text-xs font-medium uppercase tracking-wider"
        style={{
          background: "var(--surface)",
          borderBottom: "1px solid var(--border)",
          color: "var(--text-muted)",
        }}
        aria-hidden
      >
        <span>Severity</span>
        <span>Finding / Rule</span>
        <span>Scanner</span>
        <span>File:Line</span>
        <span>Status</span>
        <span>CVSS</span>
      </div>

      {/* Virtualized body */}
      <div
        ref={parentRef}
        className="overflow-y-auto"
        style={{ height: "calc(100vh - 420px)", minHeight: "300px" }}
        aria-label={`${filtered.length} findings`}
        tabIndex={0}
        role="list"
      >
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            position: "relative",
          }}
        >
          <AnimatePresence initial={false}>
            {rowVirtualizer.getVirtualItems().map((virtualItem) => {
              const item = items[virtualItem.index];

              if (item?.type === "header") {
                return (
                  <div
                    key={`header-${item.label}`}
                    style={{
                      position: "absolute",
                      top: 0,
                      transform: `translateY(${virtualItem.start}px)`,
                      width: "100%",
                      height: `${virtualItem.size}px`,
                      color: "var(--text-muted)",
                    }}
                    className="flex items-center gap-2 px-3 text-xs font-semibold uppercase tracking-wide"
                    role="rowgroup"
                    aria-label={`Group: ${item.label}`}
                  >
                    <span style={{ color: "var(--text-muted)" }}>{item.label}</span>
                    <span
                      className="rounded-full px-1.5 py-0.5 text-xs tabular-nums"
                      style={{
                        background: "var(--surface-overlay)",
                        color: "var(--text-muted)",
                      }}
                    >
                      {item.count}
                    </span>
                  </div>
                );
              }

              if (item?.type === "finding") {
                const f = item.finding;
                const isActive = f.id === activeFindingId;

                return (
                  <motion.div
                    key={f.id}
                    initial={shouldReduce ? false : { opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    style={{
                      position: "absolute",
                      top: 0,
                      transform: `translateY(${virtualItem.start}px)`,
                      width: "100%",
                      height: `${virtualItem.size}px`,
                    }}
                    role="listitem"
                  >
                    <button
                      type="button"
                      onClick={() => onFindingClick(f.id)}
                      className={cn(
                        "grid w-full grid-cols-[6rem_1fr_5rem_10rem_6rem_4.5rem] items-center gap-3 px-3 text-xs transition-colors h-full",
                        "hover:bg-[var(--surface-raised)]",
                        f.verification_status === "false_positive" && "opacity-50",
                        isActive && "bg-[var(--accent-muted)] border-l-2 border-[var(--accent)]"
                      )}
                      aria-pressed={isActive}
                      aria-label={`${f.severity} finding: ${f.rule_id}, ${f.verification_status}`}
                    >
                      {/* Severity */}
                      <div className="flex items-center gap-1.5">
                        <SeverityDot severity={f.severity} />
                        <span
                          className="font-medium capitalize hidden sm:block"
                          style={{
                            color: `var(--${f.severity})`,
                          }}
                        >
                          {f.severity}
                        </span>
                      </div>

                      {/* Rule / Title */}
                      <div className="flex flex-col gap-0.5 min-w-0">
                        <span
                          className="truncate font-medium"
                          style={{ color: "var(--text)" }}
                        >
                          {f.cwe ? cweLabel(f.cwe) : f.rule_id.split(".").pop() ?? f.rule_id}
                        </span>
                        <span
                          className="truncate font-mono text-[11px]"
                          style={{ color: "var(--text-muted)" }}
                        >
                          {f.cwe ? `${cweCode(f.cwe)} · ${f.rule_id.split(".").pop()}` : f.rule_id}
                        </span>
                      </div>

                      {/* Scanner */}
                      <span
                        className="truncate font-mono"
                        style={{ color: "var(--text-muted)" }}
                      >
                        {f.scanner}
                      </span>

                      {/* File:line */}
                      <span
                        className="truncate font-mono text-[11px]"
                        style={{ color: "var(--text-muted)" }}
                        title={f.file_path ?? undefined}
                      >
                        {f.file_path
                          ? `${formatPath(f.file_path)}${f.line_start ? `:${f.line_start}` : ""}`
                          : "—"}
                      </span>

                      {/* Status */}
                      <VerificationChip status={f.verification_status} />

                      {/* CVSS */}
                      <span
                        className="tabular-nums font-mono text-right"
                        style={{
                          color: f.cvss_score !== null ? "var(--text)" : "var(--text-subtle)",
                        }}
                      >
                        {f.cvss_score !== null ? f.cvss_score.toFixed(1) : "—"}
                      </span>
                    </button>
                  </motion.div>
                );
              }

              return null;
            })}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
