"use client";

import { useQueryState } from "nuqs";
import { X, Search, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Severity, VerificationStatus } from "@/lib/types";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { VerificationChip } from "@/components/ui/verification-chip";

const SEVERITIES: Severity[] = ["critical", "high", "medium", "low", "info"];
const STATUSES: VerificationStatus[] = [
  "confirmed",
  "needs_manual",
  "false_positive",
  "unverified",
];
const SCANNERS = ["semgrep", "trivy", "osv", "gitleaks", "trufflehog"];
const SCANNER_LABELS: Record<string, string> = {
  semgrep: "Semgrep",
  trivy: "Trivy",
  osv: "OSV",
  gitleaks: "Gitleaks",
  trufflehog: "TruffleHog",
};
const GROUP_BY_OPTIONS = [
  { value: "severity", label: "By Severity" },
  { value: "rule", label: "By Rule" },
  { value: "file", label: "By File" },
];

export function FilterBar() {
  const [severity, setSeverity] = useQueryState("severity", {
    defaultValue: "",
    shallow: true,
  });
  const [status, setStatus] = useQueryState("status", {
    defaultValue: "",
    shallow: true,
  });
  const [scanner, setScanner] = useQueryState("scanner", {
    defaultValue: "",
    shallow: true,
  });
  const [ruleSearch, setRuleSearch] = useQueryState("rule", {
    defaultValue: "",
    shallow: true,
  });
  const [fileSearch, setFileSearch] = useQueryState("file", {
    defaultValue: "",
    shallow: true,
  });
  const [groupBy, setGroupBy] = useQueryState("groupBy", {
    defaultValue: "severity",
    shallow: true,
  });

  const activeSevs = severity ? severity.split(",").filter(Boolean) : [];
  const activeStatuses = status ? status.split(",").filter(Boolean) : [];
  const activeScanners = scanner ? scanner.split(",").filter(Boolean) : [];

  function toggleSeverity(s: string) {
    const next = activeSevs.includes(s)
      ? activeSevs.filter((x) => x !== s)
      : [...activeSevs, s];
    setSeverity(next.join(",") || null);
  }

  function toggleStatus(s: string) {
    const next = activeStatuses.includes(s)
      ? activeStatuses.filter((x) => x !== s)
      : [...activeStatuses, s];
    setStatus(next.join(",") || null);
  }

  function toggleScanner(s: string) {
    const next = activeScanners.includes(s)
      ? activeScanners.filter((x) => x !== s)
      : [...activeScanners, s];
    setScanner(next.join(",") || null);
  }

  function clearAll() {
    setSeverity(null);
    setStatus(null);
    setScanner(null);
    setRuleSearch(null);
    setFileSearch(null);
  }

  const hasFilters =
    activeSevs.length > 0 ||
    activeStatuses.length > 0 ||
    activeScanners.length > 0 ||
    ruleSearch ||
    fileSearch;

  return (
    <div className="space-y-2">
      {/* Filter controls row */}
      <div
        className="flex flex-wrap items-center gap-2 rounded-lg border p-2"
        style={{
          background: "var(--surface)",
          borderColor: "var(--border)",
        }}
        role="toolbar"
        aria-label="Findings filters"
      >
        <SlidersHorizontal
          className="h-4 w-4 shrink-0 text-[var(--text-muted)]"
          aria-hidden
        />

        {/* Severity toggles */}
        <div className="flex items-center gap-1" role="group" aria-label="Filter by severity">
          {SEVERITIES.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => toggleSeverity(s)}
              className={cn(
                "transition-opacity",
                !activeSevs.includes(s) && activeSevs.length > 0 && "opacity-40"
              )}
              aria-pressed={activeSevs.includes(s)}
              aria-label={`Filter by ${s} severity`}
            >
              <SeverityBadge severity={s as Severity} compact />
            </button>
          ))}
        </div>

        <div className="h-4 w-px bg-[var(--border)]" aria-hidden />

        {/* Status toggles */}
        <div className="flex items-center gap-1" role="group" aria-label="Filter by status">
          {STATUSES.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => toggleStatus(s)}
              className={cn(
                "transition-opacity",
                !activeStatuses.includes(s) && activeStatuses.length > 0 && "opacity-40"
              )}
              aria-pressed={activeStatuses.includes(s)}
              aria-label={`Filter by ${s} status`}
            >
              <VerificationChip status={s as VerificationStatus} />
            </button>
          ))}
        </div>

        <div className="h-4 w-px bg-[var(--border)]" aria-hidden />

        {/* Scanner toggles */}
        <div className="flex items-center gap-1" role="group" aria-label="Filter by scanner">
          {SCANNERS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => toggleScanner(s)}
              className={cn(
                "rounded border px-2 py-0.5 text-xs font-medium transition-all",
                activeScanners.includes(s)
                  ? "border-[var(--accent)] bg-[var(--accent-muted)] text-[var(--accent)]"
                  : "border-[var(--border)] bg-transparent text-[var(--text-muted)]",
                !activeScanners.includes(s) && activeScanners.length > 0 && "opacity-40"
              )}
              aria-pressed={activeScanners.includes(s)}
            >
              {SCANNER_LABELS[s]}
            </button>
          ))}
        </div>

        <div className="h-4 w-px bg-[var(--border)]" aria-hidden />

        {/* Rule search */}
        <label className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
          <Search className="h-3.5 w-3.5 shrink-0" aria-hidden />
          <input
            type="search"
            value={ruleSearch ?? ""}
            onChange={(e) => setRuleSearch(e.target.value || null)}
            placeholder="Rule / CWE"
            className="w-28 bg-transparent text-[var(--text)] placeholder:text-[var(--text-subtle)] outline-none focus:ring-0"
            aria-label="Search by rule or CWE"
          />
        </label>

        {/* File search */}
        <label className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
          <Search className="h-3.5 w-3.5 shrink-0" aria-hidden />
          <input
            type="search"
            value={fileSearch ?? ""}
            onChange={(e) => setFileSearch(e.target.value || null)}
            placeholder="File path"
            className="w-32 bg-transparent text-[var(--text)] placeholder:text-[var(--text-subtle)] outline-none focus:ring-0"
            aria-label="Search by file path"
          />
        </label>

        {/* Group by */}
        <div className="ml-auto flex items-center gap-1">
          {GROUP_BY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setGroupBy(opt.value)}
              className={cn(
                "rounded px-2 py-0.5 text-xs font-medium transition-colors",
                groupBy === opt.value
                  ? "bg-[var(--surface-raised)] text-[var(--text)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text)]"
              )}
              aria-pressed={groupBy === opt.value}
            >
              {opt.label}
            </button>
          ))}
        </div>

        {/* Clear all */}
        {hasFilters && (
          <button
            type="button"
            onClick={clearAll}
            className="flex items-center gap-1 rounded px-1.5 py-0.5 text-xs text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
            aria-label="Clear all filters"
          >
            <X className="h-3 w-3" aria-hidden />
            Clear
          </button>
        )}
      </div>

      {/* Active filter chips */}
      {hasFilters && (
        <div
          className="flex flex-wrap items-center gap-1.5"
          aria-label="Active filters"
        >
          {activeSevs.map((s) => (
            <ActiveChip
              key={s}
              label={s}
              onRemove={() => toggleSeverity(s)}
            />
          ))}
          {activeStatuses.map((s) => (
            <ActiveChip
              key={s}
              label={s.replace("_", " ")}
              onRemove={() => toggleStatus(s)}
            />
          ))}
          {activeScanners.map((s) => (
            <ActiveChip
              key={s}
              label={SCANNER_LABELS[s] ?? s}
              onRemove={() => toggleScanner(s)}
            />
          ))}
          {ruleSearch && (
            <ActiveChip
              label={`rule: ${ruleSearch}`}
              onRemove={() => setRuleSearch(null)}
            />
          )}
          {fileSearch && (
            <ActiveChip
              label={`file: ${fileSearch}`}
              onRemove={() => setFileSearch(null)}
            />
          )}
        </div>
      )}
    </div>
  );
}

function ActiveChip({
  label,
  onRemove,
}: {
  label: string;
  onRemove: () => void;
}) {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium"
      style={{
        borderColor: "var(--accent)",
        background: "var(--accent-muted)",
        color: "var(--accent)",
      }}
    >
      {label}
      <button
        type="button"
        onClick={onRemove}
        className="rounded-full p-0.5 transition-opacity hover:opacity-70"
        aria-label={`Remove ${label} filter`}
      >
        <X className="h-2.5 w-2.5" aria-hidden />
      </button>
    </span>
  );
}
