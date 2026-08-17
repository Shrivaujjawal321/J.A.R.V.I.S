"use client";

import * as Dialog from "@radix-ui/react-dialog";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { X, Copy, CheckCircle2, Download, FileText } from "lucide-react";
import type { AuditReport } from "@/lib/types";

interface ReportViewerProps {
  report: AuditReport | null;
  loading?: boolean;
  onRequestReport?: () => void;
}

export function ReportViewer({
  report,
  loading,
  onRequestReport,
}: ReportViewerProps) {
  const [copied, setCopied] = useState(false);
  const [open, setOpen] = useState(false);

  function copyMarkdown() {
    if (!report) return;
    navigator.clipboard.writeText(report.markdown_body).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  function handleOpen() {
    if (!report && onRequestReport) {
      onRequestReport();
    }
    setOpen(true);
  }

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <button
          type="button"
          onClick={handleOpen}
          className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors hover:bg-[var(--surface-raised)]"
          style={{
            borderColor: "var(--border)",
            background: "var(--surface)",
            color: "var(--text-muted)",
          }}
        >
          <FileText className="h-3.5 w-3.5" aria-hidden />
          {report ? "View Report" : "Generate Report"}
        </button>
      </Dialog.Trigger>

      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
        <Dialog.Content
          className="fixed inset-4 z-50 flex flex-col overflow-hidden rounded-xl shadow-2xl outline-none sm:inset-8"
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
          }}
          aria-label="Audit report"
        >
          {/* Header */}
          <div
            className="flex items-center justify-between px-5 py-3 shrink-0"
            style={{ borderBottom: "1px solid var(--border)" }}
          >
            <Dialog.Title
              className="text-sm font-semibold"
              style={{ color: "var(--text)" }}
            >
              Security Audit Report
              {report && (
                <span
                  className="ml-2 font-mono text-xs font-normal"
                  style={{ color: "var(--text-muted)" }}
                >
                  {report.audit_id.slice(0, 8)}
                </span>
              )}
            </Dialog.Title>

            <div className="flex items-center gap-2">
              {report && (
                <>
                  <button
                    type="button"
                    onClick={copyMarkdown}
                    className="flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors hover:bg-[var(--surface-raised)]"
                    style={{
                      borderColor: "var(--border)",
                      color: "var(--text-muted)",
                    }}
                    aria-label="Copy markdown to clipboard"
                  >
                    {copied ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-green-500" aria-hidden />
                    ) : (
                      <Copy className="h-3.5 w-3.5" aria-hidden />
                    )}
                    {copied ? "Copied!" : "Copy Markdown"}
                  </button>
                  <button
                    type="button"
                    className="flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-colors hover:bg-[var(--surface-raised)]"
                    style={{
                      borderColor: "var(--border)",
                      color: "var(--text-muted)",
                    }}
                    title="Export (coming soon)"
                    aria-label="Export report (coming soon)"
                  >
                    <Download className="h-3.5 w-3.5" aria-hidden />
                    Export
                  </button>
                </>
              )}
              <Dialog.Close asChild>
                <button
                  type="button"
                  className="rounded p-1.5 transition-colors hover:bg-[var(--surface-raised)]"
                  style={{ color: "var(--text-muted)" }}
                  aria-label="Close report"
                >
                  <X className="h-4 w-4" aria-hidden />
                </button>
              </Dialog.Close>
            </div>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto px-6 py-5">
            {loading && (
              <div className="flex items-center justify-center py-16">
                <div
                  className="text-sm"
                  style={{ color: "var(--text-muted)" }}
                  aria-live="polite"
                >
                  Generating report…
                </div>
              </div>
            )}
            {!loading && !report && (
              <div className="flex items-center justify-center py-16">
                <div
                  className="text-sm"
                  style={{ color: "var(--text-muted)" }}
                >
                  No report available yet. Complete a scan first.
                </div>
              </div>
            )}
            {!loading && report && (
              <div
                className="prose prose-sm max-w-none"
                style={{
                  "--tw-prose-body": "var(--text)",
                  "--tw-prose-headings": "var(--text)",
                  "--tw-prose-code": "var(--accent)",
                  "--tw-prose-pre-bg": "oklch(0.08 0.005 255)",
                  "--tw-prose-pre-code": "var(--text)",
                  "--tw-prose-td-borders": "var(--border)",
                  "--tw-prose-th-borders": "var(--border)",
                  "--tw-prose-hr": "var(--border)",
                  "--tw-prose-links": "var(--accent)",
                  "--tw-prose-bold": "var(--text)",
                  "--tw-prose-bullets": "var(--text-muted)",
                  "--tw-prose-counters": "var(--text-muted)",
                  "--tw-prose-captions": "var(--text-muted)",
                  "--tw-prose-quote-borders": "var(--border)",
                  "--tw-prose-quotes": "var(--text-muted)",
                } as React.CSSProperties}
              >
                <ReactMarkdown>{report.markdown_body}</ReactMarkdown>
              </div>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
