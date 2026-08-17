"use client";

import { useState, useMemo, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useQueryState } from "nuqs";
import Link from "next/link";
import { ArrowLeft, Shield } from "lucide-react";
import type { AuditRunView, AuditReport, Finding, Severity } from "@/lib/types";
import { TERMINAL_STATES } from "@/lib/types";
import { getAuditStatus, getReport } from "@/lib/api";
import {
  demoAuditRunView,
  demoReport,
  demoFindings,
  DEMO_FP_COUNT,
  DEMO_ACTIONABLE_COUNT,
  DEMO_RAW_COUNT,
} from "@/lib/demo";
import { FpFunnel } from "@/components/findings/fp-funnel";
import { SeverityDonut } from "@/components/findings/severity-donut";
import { FilterBar } from "@/components/findings/filter-bar";
import { FindingsTable } from "@/components/findings/findings-table";
import { FindingDrawer } from "@/components/findings/finding-drawer";
import { ScanProgress } from "@/components/layout/scan-progress";
import { ReportViewer } from "@/components/layout/report-viewer";
import { SettingsSheet } from "@/components/layout/settings-sheet";
import { DemoBanner } from "@/components/layout/demo-banner";
import { timeAgo } from "@/lib/utils";

interface AuditResultsClientProps {
  auditId: string;
}

export function AuditResultsClient({ auditId }: AuditResultsClientProps) {
  const isDemo = auditId === "demo";
  const [findingId, setFindingId] = useQueryState("finding", {
    defaultValue: "",
    shallow: true,
  });

  // Poll audit status if live
  const statusQuery = useQuery({
    queryKey: ["audit", auditId],
    queryFn: () => getAuditStatus(auditId),
    enabled: !isDemo,
    refetchInterval: (query) => {
      if (!query.state.data) return 1000;
      return TERMINAL_STATES.includes(query.state.data.audit_state) ? false : 1000;
    },
  });

  const run: AuditRunView | null = isDemo
    ? demoAuditRunView
    : statusQuery.data ?? null;

  const isDone = run
    ? TERMINAL_STATES.includes(run.audit_state) || isDemo
    : false;

  // Get report when done
  const reportQuery = useQuery({
    queryKey: ["report", auditId],
    queryFn: () => getReport(auditId),
    enabled: !isDemo && isDone && run?.audit_state === "done",
  });

  const report: AuditReport | null = isDemo ? demoReport : reportQuery.data ?? null;

  // Findings (all loaded for demo, fetched live)
  const [liveFindings, setLiveFindings] = useState<Finding[]>([]);

  // For live mode, use all findings from the report
  const findings: Finding[] = isDemo
    ? demoFindings
    : report?.json_findings ?? liveFindings;

  // Stats
  const fpCount = useMemo(
    () => findings.filter((f) => f.verification_status === "false_positive").length,
    [findings]
  );
  const actionable = useMemo(
    () => findings.filter((f) => f.is_actionable).length,
    [findings]
  );

  const bySeverity = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const f of findings) {
      counts[f.severity] = (counts[f.severity] ?? 0) + 1;
    }
    return counts;
  }, [findings]);

  // Filter by donut click
  const [donutSeverity, setDonutSeverity] = useState<Severity | null>(null);
  const [, setSeverityFilter] = useQueryState("severity", {
    defaultValue: "",
    shallow: true,
  });

  function handleDonutClick(sev: Severity | null) {
    setDonutSeverity(sev);
    setSeverityFilter(sev ?? null);
  }

  // Active finding
  const activeFinding = useMemo(
    () => (findingId ? findings.find((f) => f.id === findingId) ?? null : null),
    [findingId, findings]
  );

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{ background: "var(--bg)" }}
    >
      {isDemo && <DemoBanner />}

      {/* Nav */}
      <header
        className="flex items-center justify-between border-b px-5 py-3"
        style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      >
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex items-center gap-1.5 text-xs transition-colors hover:text-[var(--text)]"
            style={{ color: "var(--text-muted)" }}
            aria-label="Back to home"
          >
            <ArrowLeft className="h-3.5 w-3.5" aria-hidden />
            Back
          </Link>
          <div className="h-4 w-px bg-[var(--border)]" aria-hidden />
          <div className="flex items-center gap-2">
            <div
              className="flex h-6 w-6 items-center justify-center rounded"
              style={{ background: "var(--accent-muted)" }}
            >
              <Shield
                className="h-3.5 w-3.5"
                style={{ color: "var(--accent)" }}
                aria-hidden
              />
            </div>
            <span className="text-sm font-semibold" style={{ color: "var(--text)" }}>
              AuditAgent
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isDone && report && (
            <ReportViewer report={report} />
          )}
          <SettingsSheet />
        </div>
      </header>

      <main className="flex flex-1 flex-col">
        {/* Scan in progress */}
        {!isDone && run && (
          <div className="border-b p-5" style={{ borderColor: "var(--border)" }}>
            <ScanProgress
              run={run}
              findingCount={findings.length}
              fpCount={fpCount}
            />
          </div>
        )}

        {/* Results header */}
        {isDone && (
          <div
            className="border-b px-5 py-4 space-y-4"
            style={{ borderColor: "var(--border)", background: "var(--surface)" }}
          >
            {/* Target + meta */}
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="space-y-1">
                <h1
                  className="text-base font-semibold font-mono"
                  style={{ color: "var(--text)" }}
                >
                  {run?.target_uri ?? "Scan Results"}
                </h1>
                <div
                  className="flex flex-wrap items-center gap-3 text-xs"
                  style={{ color: "var(--text-muted)" }}
                >
                  <span>
                    {run?.updated_at
                      ? timeAgo(run.updated_at)
                      : "Just now"}
                  </span>
                  <span>·</span>
                  <span>{findings.length} raw findings</span>
                  {run?.cost_usd_total !== undefined && run.cost_usd_total > 0 && (
                    <>
                      <span>·</span>
                      <span>${run.cost_usd_total.toFixed(2)} LLM cost</span>
                    </>
                  )}
                  {run?.audit_id && (
                    <>
                      <span>·</span>
                      <span className="font-mono">{run.audit_id.slice(0, 8)}</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Summary row: FP funnel + donut */}
            <div
              className="flex flex-wrap items-start gap-6 rounded-xl border p-4"
              style={{
                background: "var(--surface-raised)",
                borderColor: "var(--border)",
              }}
            >
              <div className="flex-1 min-w-[280px]">
                <FpFunnel
                  raw={findings.length > 0 ? findings.length : DEMO_RAW_COUNT}
                  fpFiltered={findings.length > 0 ? fpCount : DEMO_FP_COUNT}
                  actionable={findings.length > 0 ? actionable : DEMO_ACTIONABLE_COUNT}
                  animate
                />
              </div>
              <div
                className="w-px self-stretch"
                style={{ background: "var(--border)" }}
                aria-hidden
              />
              <SeverityDonut
                data={bySeverity}
                onSeverityClick={handleDonutClick}
                activeSeverity={donutSeverity}
              />
            </div>
          </div>
        )}

        {/* Findings section */}
        <div className="flex flex-1 flex-col gap-3 px-5 py-4">
          {isDone && (
            <>
              <FilterBar />
              <div
                className="flex-1 rounded-xl border overflow-hidden"
                style={{ background: "var(--surface)", borderColor: "var(--border)" }}
              >
                <FindingsTable
                  findings={findings}
                  onFindingClick={(id) => setFindingId(id === findingId ? null : id)}
                  activeFindingId={findingId || null}
                />
              </div>
            </>
          )}

          {!run && !isDemo && (
            <div
              className="flex flex-1 items-center justify-center"
              style={{ color: "var(--text-muted)" }}
            >
              <span className="text-sm" aria-live="polite">
                Loading scan…
              </span>
            </div>
          )}
        </div>
      </main>

      {/* Finding detail drawer */}
      <FindingDrawer
        finding={activeFinding}
        onClose={() => setFindingId(null)}
      />
    </div>
  );
}
