"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import type { Finding } from "@/lib/types";
import { cn, cweCode, cweLabel, formatPath } from "@/lib/utils";
import { SeverityBadge } from "@/components/ui/severity-badge";
import { VerificationChip } from "@/components/ui/verification-chip";
import { CvssGauge } from "@/components/ui/cvss-gauge";
import {
  X,
  ExternalLink,
  Copy,
  CheckCircle2,
  FileCode2,
  ShieldAlert,
  Star,
} from "lucide-react";
import { useState } from "react";

interface FindingDrawerProps {
  finding: Finding | null;
  onClose: () => void;
}

export function FindingDrawer({ finding, onClose }: FindingDrawerProps) {
  const shouldReduce = useReducedMotion();
  const closeRef = useRef<HTMLButtonElement>(null);
  const [copied, setCopied] = useState(false);

  // Focus the close button when drawer opens
  useEffect(() => {
    if (finding) {
      setTimeout(() => closeRef.current?.focus(), 100);
    }
  }, [finding?.id]);

  // Trap focus + Esc
  useEffect(() => {
    if (!finding) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [finding, onClose]);

  function copyId() {
    if (!finding) return;
    navigator.clipboard.writeText(finding.id).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <AnimatePresence>
      {finding && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            className="fixed inset-0 z-40 bg-black/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: shouldReduce ? 0 : 0.15 }}
            onClick={onClose}
            aria-hidden
          />

          {/* Drawer */}
          <motion.aside
            key="drawer"
            role="dialog"
            aria-modal="true"
            aria-label={`Finding detail: ${finding.rule_id}`}
            className="fixed right-0 top-0 bottom-0 z-50 flex flex-col overflow-hidden shadow-2xl"
            style={{
              width: "min(520px, 92vw)",
              background: "var(--surface)",
              borderLeft: "1px solid var(--border)",
            }}
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: shouldReduce ? 0 : 0.25, ease: "easeOut" }}
          >
            {/* Header */}
            <div
              className="flex items-start gap-3 p-4 shrink-0"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              <div className="flex flex-col gap-2 flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <SeverityBadge severity={finding.severity} />
                  <VerificationChip status={finding.verification_status} />
                  {finding.scanners_agreeing.length > 1 && (
                    <span
                      className="inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-xs font-medium"
                      style={{
                        background: "var(--gold-bg)",
                        borderColor: "var(--gold)",
                        color: "var(--gold)",
                      }}
                    >
                      <Star className="h-3 w-3" aria-hidden />
                      {finding.scanners_agreeing.length} scanners agree
                    </span>
                  )}
                </div>
                <h2
                  className="text-sm font-semibold leading-snug"
                  style={{ color: "var(--text)" }}
                >
                  {finding.cwe ? cweLabel(finding.cwe) : finding.rule_id.split(".").pop()}
                </h2>
                {finding.cwe && (
                  <div className="flex items-center gap-2 text-xs font-mono" style={{ color: "var(--text-muted)" }}>
                    <span>{cweCode(finding.cwe)}</span>
                    <span style={{ color: "var(--border)" }}>·</span>
                    <span>{finding.rule_id}</span>
                  </div>
                )}
              </div>

              {/* Close */}
              <button
                ref={closeRef}
                type="button"
                onClick={onClose}
                className="shrink-0 rounded p-1.5 transition-colors hover:bg-[var(--surface-raised)]"
                style={{ color: "var(--text-muted)" }}
                aria-label="Close finding detail"
              >
                <X className="h-4 w-4" aria-hidden />
              </button>
            </div>

            {/* Scrollable body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-5">
              {/* Scanner + file meta */}
              <section aria-label="Finding location">
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <div className="mb-1 font-medium uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                      Scanner
                    </div>
                    <span
                      className="inline-block rounded border px-2 py-0.5 font-mono"
                      style={{
                        background: "var(--surface-raised)",
                        borderColor: "var(--border)",
                        color: "var(--text)",
                      }}
                    >
                      {finding.scanner}
                    </span>
                  </div>
                  {finding.owasp_category && (
                    <div>
                      <div className="mb-1 font-medium uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                        OWASP
                      </div>
                      <span className="font-mono" style={{ color: "var(--text)" }}>
                        {finding.owasp_category}
                      </span>
                    </div>
                  )}
                  {finding.confidence !== undefined && (
                    <div>
                      <div className="mb-1 font-medium uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                        Confidence
                      </div>
                      <span className="font-mono" style={{ color: "var(--text)" }}>
                        {Math.round(finding.confidence * 100)}%
                      </span>
                    </div>
                  )}
                </div>

                {finding.file_path && (
                  <div className="mt-3 flex items-start gap-2 rounded-lg p-2.5" style={{ background: "var(--surface-raised)" }}>
                    <FileCode2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--text-muted)]" aria-hidden />
                    <div className="min-w-0">
                      <div
                        className="break-all font-mono text-xs"
                        style={{ color: "var(--text)" }}
                      >
                        {finding.file_path}
                      </div>
                      {finding.line_start && (
                        <div className="mt-0.5 text-xs" style={{ color: "var(--text-muted)" }}>
                          Lines {finding.line_start}
                          {finding.line_end && finding.line_end !== finding.line_start
                            ? `–${finding.line_end}`
                            : ""}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </section>

              {/* Evidence */}
              <section aria-label="Evidence">
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                  Evidence
                </h3>
                <pre
                  className="rounded-lg p-3 text-xs font-mono leading-relaxed overflow-x-auto whitespace-pre-wrap"
                  style={{
                    background: "oklch(0.08 0.005 255)",
                    color: "var(--text)",
                    border: "1px solid var(--border)",
                  }}
                >
                  {finding.evidence}
                </pre>
              </section>

              {/* Verification reason */}
              {finding.verification_reason && (
                <section aria-label="Verification rationale">
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                    Verification Rationale
                  </h3>
                  <div
                    className="rounded-lg p-3 text-xs leading-relaxed"
                    style={{
                      background: "var(--surface-raised)",
                      color: "var(--text)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    {finding.verification_reason}
                  </div>
                </section>
              )}

              {/* Remediation */}
              {finding.remediation && (
                <section aria-label="Remediation guidance">
                  <h3 className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                    <ShieldAlert className="h-3.5 w-3.5" aria-hidden />
                    Remediation
                  </h3>
                  <div
                    className="rounded-lg p-3 text-xs leading-relaxed whitespace-pre-wrap"
                    style={{
                      background: "var(--surface-raised)",
                      color: "var(--text)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    {finding.remediation}
                  </div>
                </section>
              )}

              {/* CVSS Gauge (SCA findings) */}
              {finding.cvss_score !== null && finding.cvss_vector && (
                <section aria-label="CVSS score">
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                    CVSS 4.0
                  </h3>
                  <div
                    className="rounded-lg p-3"
                    style={{
                      background: "var(--surface-raised)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    <CvssGauge
                      score={finding.cvss_score}
                      vector={finding.cvss_vector}
                    />
                  </div>
                </section>
              )}

              {/* Scanner agreement */}
              {finding.scanners_agreeing.length > 0 && (
                <section aria-label="Scanner agreement">
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide" style={{ color: "var(--text-muted)" }}>
                    Scanners
                  </h3>
                  <div className="flex flex-wrap gap-1.5">
                    {finding.scanners_agreeing.map((s) => (
                      <span
                        key={s}
                        className="rounded border px-2 py-0.5 text-xs font-mono"
                        style={{
                          background: "var(--surface-raised)",
                          borderColor: "var(--border)",
                          color: "var(--text)",
                        }}
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </section>
              )}
            </div>

            {/* Footer */}
            <div
              className="flex items-center justify-between px-4 py-3 text-xs shrink-0"
              style={{
                borderTop: "1px solid var(--border)",
                color: "var(--text-muted)",
              }}
            >
              <button
                type="button"
                onClick={copyId}
                className="flex items-center gap-1.5 font-mono transition-colors hover:text-[var(--text)]"
                aria-label="Copy finding ID to clipboard"
              >
                {copied ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-500" aria-hidden />
                ) : (
                  <Copy className="h-3.5 w-3.5" aria-hidden />
                )}
                {finding.id.slice(0, 8)}…
              </button>
              {finding.rule_id.includes("GHSA") && (
                <a
                  href={`https://github.com/advisories/${finding.rule_id.split(".").pop()}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 transition-colors hover:text-[var(--text)]"
                  aria-label={`View ${finding.rule_id} on GitHub Advisory Database`}
                >
                  <ExternalLink className="h-3 w-3" aria-hidden />
                  GitHub Advisory
                </a>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
