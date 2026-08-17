"use client";

import React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Download, Share2, ArrowLeft, FileText } from "lucide-react";
import { toast } from "sonner";
import { API_BASE } from "@/lib/utils";
import { OutputCard } from "@/components/ui/output-card";
import { StatusBadge } from "@/components/ui/status-badge";
import type { ReportData, StatusBand } from "@/lib/types";

async function fetchReport(id: string): Promise<ReportData> {
  const res = await fetch(`${API_BASE}/api/report/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`Report fetch failed: ${res.status}`);
  return res.json();
}

function toStatusBandSafe(rb: string | undefined): StatusBand {
  if (!rb) return "unknown";
  const map: Record<string, StatusBand> = {
    low: "healthy", medium: "warning", high: "alarm", critical: "critical",
    healthy: "healthy", warning: "warning", alarm: "alarm",
  };
  return map[rb.toLowerCase()] ?? "unknown";
}

function getFindingEntry(
  data: ReportData,
  key: string
): { title: string; brief: string; detail: string; sources: string[] } | null {
  // Try findings map first
  if (data.findings && data.findings[key]) return data.findings[key];
  // Try top-level key
  const v = data[key];
  if (typeof v === "string") return { title: key, brief: v, detail: "", sources: [] };
  if (v && typeof v === "object") {
    const entry = v as { title?: string; brief?: string; detail?: string; sources?: string[] };
    return {
      title: entry.title ?? key,
      brief: entry.brief ?? "",
      detail: entry.detail ?? "",
      sources: entry.sources ?? [],
    };
  }
  return null;
}

const FINDING_KEYS = ["diagnosis", "rca", "predictor", "prioritizer", "recommender"];
const FINDING_LABELS: Record<string, string> = {
  diagnosis: "Diagnosis",
  rca: "Root Cause Analysis",
  predictor: "RUL Prediction",
  prioritizer: "Prioritized Actions",
  recommender: "Recommendations",
};

interface ReportViewProps {
  reportId: string;
  printMode?: boolean;
}

export function ReportView({ reportId, printMode }: ReportViewProps) {
  const { data, isLoading, isError } = useQuery<ReportData>({
    queryKey: ["report", reportId],
    queryFn: () => fetchReport(reportId),
    staleTime: Infinity,
  });

  function handleDownload() {
    // Try backend PDF endpoint first, fall back to print
    const pdfUrl = `${API_BASE}/api/report/${reportId}/pdf`;
    fetch(pdfUrl, { method: "HEAD" })
      .then((r) => {
        if (r.ok) {
          window.open(pdfUrl, "_blank");
        } else {
          window.print();
        }
      })
      .catch(() => window.print());
  }

  function handleDownloadJSON() {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `edith-report-${reportId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleCopyLink() {
    navigator.clipboard
      .writeText(`${window.location.origin}/report/${reportId}`)
      .then(() => toast.success("Share link copied"))
      .catch(() => toast.error("Copy failed"));
  }

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: "var(--color-bg-base)" }}
      >
        <div className="text-center">
          <div
            className="skeleton h-4 w-48 mx-auto mb-3 rounded"
            aria-hidden="true"
          />
          <p
            className="text-sm"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            Loading report…
          </p>
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: "var(--color-bg-base)" }}
      >
        <div
          className="hud-panel p-8 max-w-md text-center"
          role="alert"
        >
          <FileText
            size={32}
            style={{ color: "var(--color-status-alarm-fg)" }}
            className="mx-auto mb-3"
            aria-hidden="true"
          />
          <h1
            className="text-lg font-semibold mb-2"
            style={{ color: "var(--color-fg-primary)" }}
          >
            Report not found
          </h1>
          <p
            className="text-sm mb-4"
            style={{ color: "var(--color-fg-secondary)" }}
          >
            Report ID <code className="mono-data">{reportId}</code> could not be
            loaded. Check the backend is running at 127.0.0.1:8077.
          </p>
          <Link href="/" className="btn-secondary">
            <ArrowLeft size={14} aria-hidden="true" />
            Back to cockpit
          </Link>
        </div>
      </div>
    );
  }

  const riskBand = toStatusBandSafe(data.risk_band);
  const findings = FINDING_KEYS.map((k) => ({
    key: k,
    label: FINDING_LABELS[k],
    entry: getFindingEntry(data, k),
  })).filter((f) => f.entry != null);

  return (
    <div
      className="min-h-screen"
      style={{ background: "var(--color-bg-base)" }}
    >
      {/* Header / nav (hidden in print mode) */}
      {!printMode && (
        <header
          className="sticky top-0 z-20 flex items-center gap-3 px-6 py-4 border-b print:hidden"
          style={{
            background: "var(--color-glass-base)",
            backdropFilter: "blur(16px)",
            borderColor: "var(--color-glass-border)",
          }}
        >
          <Link
            href="/"
            className="btn-ghost py-1.5 px-3 text-xs"
            aria-label="Back to cockpit"
          >
            <ArrowLeft size={13} aria-hidden="true" />
            Cockpit
          </Link>

          <div
            className="h-4 w-px"
            style={{ background: "var(--color-border)" }}
            aria-hidden="true"
          />

          <span
            className="font-bold text-sm"
            style={{
              color: "var(--color-accent-400)",
              fontFamily: "var(--font-mono)",
              letterSpacing: "0.18em",
            }}
          >
            EDITH
          </span>
          <span
            className="text-sm"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            Maintenance Report
          </span>

          <div className="ml-auto flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopyLink}
              className="btn-ghost py-1.5 px-3 text-xs"
              aria-label="Copy share link"
            >
              <Share2 size={13} aria-hidden="true" />
              Share
            </button>
            <button
              type="button"
              onClick={handleDownloadJSON}
              className="btn-ghost py-1.5 px-3 text-xs"
              aria-label="Download report as JSON"
            >
              JSON
            </button>
            <button
              type="button"
              onClick={handleDownload}
              className="btn-primary py-1.5 px-3 text-xs"
              aria-label="Download report as PDF"
            >
              <Download size={13} aria-hidden="true" />
              PDF
            </button>
          </div>
        </header>
      )}

      {/* Report body */}
      <main
        className="max-w-3xl mx-auto px-6 py-8"
        aria-label="Maintenance report"
      >
        {/* Report header */}
        <div
          className="hud-panel p-6 mb-6"
          role="region"
          aria-label="Report summary"
        >
          <div className="flex items-start justify-between gap-4 mb-4 flex-wrap">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span
                  className="font-bold text-xs tracking-widest"
                  style={{
                    color: "var(--color-accent-400)",
                    fontFamily: "var(--font-mono)",
                  }}
                >
                  EDITH
                </span>
                <span
                  className="label-caps"
                  style={{ color: "var(--color-fg-faint)" }}
                >
                  Maintenance Report
                </span>
              </div>
              <h1
                className="text-xl font-semibold mb-1"
                style={{ color: "var(--color-fg-primary)" }}
              >
                {data.asset_id ?? "Asset Report"}
              </h1>
              {data.generated_at && (
                <time
                  dateTime={data.generated_at}
                  className="label-caps"
                  style={{ color: "var(--color-fg-faint)" }}
                >
                  Generated{" "}
                  {new Date(data.generated_at).toLocaleString("en-IN", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  })}
                </time>
              )}
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              {data.risk_band && <StatusBadge status={riskBand} />}
              {data.rul != null && (
                <div className="kpi-card py-2 px-4">
                  <div className="kpi-label">RUL</div>
                  <div
                    className="kpi-value"
                    style={{
                      fontSize: "1.25rem",
                      color:
                        (data.rul ?? 0) < 50
                          ? "var(--color-status-critical-fg)"
                          : (data.rul ?? 0) < 200
                          ? "var(--color-status-warning-fg)"
                          : "var(--color-fg-primary)",
                    }}
                  >
                    {data.rul}{" "}
                    <span
                      className="text-xs font-normal"
                      style={{ color: "var(--color-fg-tertiary)" }}
                    >
                      cycles
                    </span>
                  </div>
                </div>
              )}
              {data.confidence != null && (
                <div className="kpi-card py-2 px-4">
                  <div className="kpi-label">Confidence</div>
                  <div
                    className="kpi-value"
                    style={{ fontSize: "1.25rem", color: "var(--color-accent-400)" }}
                  >
                    {Math.round((data.confidence ?? 0) * 100)}%
                  </div>
                </div>
              )}
            </div>
          </div>

          {data.summary && (
            <p
              className="text-sm leading-relaxed"
              style={{ color: "var(--color-fg-secondary)" }}
            >
              {data.summary}
            </p>
          )}
        </div>

        {/* Finding cards */}
        {findings.length > 0 && (
          <div className="space-y-3 mb-6" aria-label="Detailed findings">
            <h2 className="hud-heading">Detailed Findings</h2>
            {findings.map(({ key, entry }) => (
              <OutputCard
                key={key}
                heading={entry!.title}
                brief={entry!.brief}
                enhancedBrief={
                  entry!.detail ? (
                    <p className="whitespace-pre-line">{entry!.detail}</p>
                  ) : undefined
                }
                citations={entry!.sources}
                riskBand={data.risk_band}
                rul={data.rul ?? undefined}
                defaultExpanded
              />
            ))}
          </div>
        )}

        {/* Sources */}
        {data.sources && data.sources.length > 0 && (
          <div
            className="hud-panel p-4 mb-6"
            role="region"
            aria-label="Source references"
          >
            <h2 className="hud-heading">References</h2>
            <div className="flex flex-wrap gap-1.5">
              {data.sources.map((s, i) => (
                <span key={i} className="cite-pill">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Report ID */}
        <div
          className="text-xs border-t pt-4"
          style={{
            color: "var(--color-fg-faint)",
            borderColor: "var(--color-border-subtle)",
            fontFamily: "var(--font-mono)",
          }}
        >
          Report ID: {reportId} · EDITH Maintenance Intelligence
        </div>
      </main>
    </div>
  );
}
