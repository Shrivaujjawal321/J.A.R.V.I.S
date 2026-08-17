"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Shield, Folder, ArrowRight, Clock, AlertTriangle } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { checkDaemonHealth, startAudit } from "@/lib/api";
import { SettingsSheet } from "@/components/layout/settings-sheet";
import { Sparkline } from "@/components/ui/sparkline";
import { timeAgo } from "@/lib/utils";
import { DemoBanner } from "@/components/layout/demo-banner";

export function HomeClient() {
  const router = useRouter();
  const { recentScans, isDemoMode, setDemoMode, enabledScanners, llmBudget } = useAppStore();
  const [path, setPath] = useState("");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Probe daemon on mount
  useEffect(() => {
    checkDaemonHealth().then((alive) => {
      setDemoMode(!alive);
    });
  }, [setDemoMode]);

  async function handleScan(e: React.FormEvent) {
    e.preventDefault();
    if (!path.trim()) return;

    if (isDemoMode) {
      // In demo mode, go directly to demo results
      router.push("/audit/demo");
      return;
    }

    setScanning(true);
    setError(null);
    try {
      const run = await startAudit({
        target_uri: path.trim(),
        allowed_scanners: enabledScanners,
        max_budget_usd: llmBudget,
      });
      router.push(`/audit/${run.audit_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start scan");
      setScanning(false);
    }
  }

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{ background: "var(--bg)" }}
    >
      {isDemoMode && <DemoBanner />}

      {/* Nav */}
      <header
        className="flex items-center justify-between border-b px-5 py-3"
        style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      >
        <div className="flex items-center gap-2">
          <div
            className="flex h-6 w-6 items-center justify-center rounded"
            style={{ background: "var(--accent-muted)" }}
          >
            <Shield className="h-3.5 w-3.5" style={{ color: "var(--accent)" }} aria-hidden />
          </div>
          <span className="text-sm font-semibold" style={{ color: "var(--text)" }}>
            AuditAgent
          </span>
        </div>
        <SettingsSheet />
      </header>

      {/* Main content */}
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-12">
        <motion.div
          className="w-full max-w-xl space-y-8"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: "easeOut" }}
        >
          {/* Hero */}
          <div className="text-center space-y-3">
            <div
              className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border"
              style={{
                background: "var(--accent-muted)",
                borderColor: "var(--accent)",
              }}
            >
              <Shield
                className="h-7 w-7"
                style={{ color: "var(--accent)" }}
                aria-hidden
              />
            </div>
            <h1
              className="text-2xl font-semibold tracking-tight"
              style={{ color: "var(--text)" }}
            >
              Scan a local repository
            </h1>
            <p className="text-sm" style={{ color: "var(--text-muted)" }}>
              SAST · SCA · Secrets · AI-verified findings · Zero false-positive noise
            </p>
          </div>

          {/* Scan form */}
          <form
            onSubmit={handleScan}
            className="space-y-3"
            aria-label="Start a security scan"
          >
            <div
              className="flex items-center gap-2 rounded-lg border px-3 py-2.5"
              style={{
                background: "var(--surface)",
                borderColor: error ? "var(--critical)" : "var(--border)",
              }}
            >
              <Folder
                className="h-4 w-4 shrink-0"
                style={{ color: "var(--text-muted)" }}
                aria-hidden
              />
              <input
                type="text"
                value={path}
                onChange={(e) => setPath(e.target.value)}
                placeholder={
                  isDemoMode
                    ? "/path/to/your/repo  (demo mode — any path works)"
                    : "/path/to/your/repo"
                }
                className="flex-1 bg-transparent text-sm outline-none placeholder:text-[var(--text-subtle)]"
                style={{ color: "var(--text)" }}
                aria-label="Repository path"
                aria-describedby={error ? "scan-error" : undefined}
              />
            </div>

            {error && (
              <p
                id="scan-error"
                className="flex items-center gap-1.5 text-xs"
                style={{ color: "var(--critical)" }}
                role="alert"
              >
                <AlertTriangle className="h-3.5 w-3.5 shrink-0" aria-hidden />
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={scanning || !path.trim()}
              className="flex w-full items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-semibold transition-opacity disabled:opacity-50"
              style={{
                background: "var(--accent)",
                color: "oklch(1 0 0)",
              }}
              aria-busy={scanning}
            >
              {scanning ? (
                "Starting scan…"
              ) : isDemoMode ? (
                <>
                  View Demo Results
                  <ArrowRight className="h-4 w-4" aria-hidden />
                </>
              ) : (
                <>
                  Start Scan
                  <ArrowRight className="h-4 w-4" aria-hidden />
                </>
              )}
            </button>
          </form>

          {/* Scanner info */}
          <div
            className="rounded-lg border p-3"
            style={{ background: "var(--surface)", borderColor: "var(--border)" }}
          >
            <div className="mb-2 text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
              Enabled scanners
            </div>
            <div className="flex flex-wrap gap-1.5">
              {enabledScanners.map((s) => (
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
          </div>

          {/* Recent scans */}
          {recentScans.length > 0 && (
            <section aria-label="Recent scans">
              <h2
                className="mb-3 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wider"
                style={{ color: "var(--text-muted)" }}
              >
                <Clock className="h-3.5 w-3.5" aria-hidden />
                Recent Scans
              </h2>
              <div className="space-y-1">
                {recentScans.map((scan) => (
                  <a
                    key={scan.audit_id}
                    href={`/audit/${scan.audit_id === "2d919643-fbfa-4b2a-a1fd-e70b91905939" ? "demo" : scan.audit_id}`}
                    className="flex items-center gap-3 rounded-lg border px-3 py-2 text-xs transition-colors hover:bg-[var(--surface-raised)]"
                    style={{
                      background: "var(--surface)",
                      borderColor: "var(--border)",
                    }}
                  >
                    <Folder
                      className="h-3.5 w-3.5 shrink-0"
                      style={{ color: "var(--text-muted)" }}
                      aria-hidden
                    />
                    <div className="flex flex-1 flex-col gap-0.5 min-w-0">
                      <span
                        className="truncate font-mono font-medium"
                        style={{ color: "var(--text)" }}
                      >
                        {scan.target_uri}
                      </span>
                      <span style={{ color: "var(--text-muted)" }}>
                        {timeAgo(scan.scanned_at)} · {scan.total_findings} raw ·{" "}
                        <span style={{ color: "var(--accent)" }}>
                          {scan.actionable_count} actionable
                        </span>
                      </span>
                    </div>
                    <Sparkline data={scan.history} />
                  </a>
                ))}
              </div>
            </section>
          )}
        </motion.div>
      </main>
    </div>
  );
}
