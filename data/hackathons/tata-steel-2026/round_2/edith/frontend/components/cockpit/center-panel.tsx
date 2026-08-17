"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Activity, Zap, BookOpen, ChevronDown, ChevronRight, FileText, Bell, ClipboardList, MessageSquare } from "lucide-react";
import { cn, API_BASE, formatTs } from "@/lib/utils";
import { toStatusBand, stateToStatusBand, type AssetDetail, type LogbookEntry, type LogbookEntryType } from "@/lib/types";
import { StatusBadge } from "@/components/ui/status-badge";
import { VerdictCard, VerdictCardSkeleton } from "./verdict-card";
import { SensorChart } from "./sensor-chart";
import { useEdithStore } from "@/store/edith-store";
import { useSseStream } from "@/hooks/use-sse-stream";
import { useFocus } from "@/hooks/use-focus";

async function fetchAssetDetail(id: string): Promise<AssetDetail> {
  const res = await fetch(`${API_BASE}/api/asset/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`Asset detail fetch failed: ${res.status}`);
  return res.json();
}

async function postReport(body: {
  asset_id: string;
  kind: "incident" | "decision";
}) {
  const res = await fetch(`${API_BASE}/api/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Report generation failed");
  return res.json() as Promise<{ report_id: string }>;
}

async function fetchLogbook(assetId: string): Promise<LogbookEntry[]> {
  const res = await fetch(
    `${API_BASE}/api/logbook?asset_id=${encodeURIComponent(assetId)}&limit=20`
  );
  if (!res.ok) throw new Error(`Logbook fetch failed: ${res.status}`);
  const data: unknown = await res.json();
  // Defensive: backend may return { entries: [...] } or just [...]
  if (Array.isArray(data)) return data as LogbookEntry[];
  if (data && typeof data === "object" && "entries" in data && Array.isArray((data as Record<string, unknown>).entries)) {
    return (data as { entries: LogbookEntry[] }).entries;
  }
  return [];
}

// ─── Logbook section (G9-frontend) ──────────────────────────────────────────

function entryTypeIcon(t: LogbookEntryType) {
  switch (t) {
    case "alert":     return <Bell size={11} aria-hidden="true" style={{ color: "var(--color-status-alarm-fg)" }} />;
    case "diagnosis": return <ClipboardList size={11} aria-hidden="true" style={{ color: "var(--color-accent-400)" }} />;
    case "report":    return <FileText size={11} aria-hidden="true" style={{ color: "var(--color-status-healthy-fg)" }} />;
    case "feedback":  return <MessageSquare size={11} aria-hidden="true" style={{ color: "var(--color-fg-tertiary)" }} />;
    default:          return <FileText size={11} aria-hidden="true" style={{ color: "var(--color-fg-faint)" }} />;
  }
}

const LOGBOOK_EMPTY_MSG =
  "Logbook entries are recorded automatically as EDITH monitors, diagnoses and reports on this machine.";

function LogbookSection({ assetId }: { assetId: string }) {
  const [open, setOpen] = useState(false);

  const { data, isError } = useQuery<LogbookEntry[]>({
    queryKey: ["logbook", assetId],
    queryFn: () => fetchLogbook(assetId),
    staleTime: 30_000,
    retry: false,
    enabled: open, // only fetch when expanded
  });

  const entries: LogbookEntry[] = data ?? [];
  const isEmpty = isError || entries.length === 0;

  return (
    <div
      className="rounded"
      style={{
        background: "var(--color-bg-card)",
        border: "1px solid var(--color-border)",
        borderRadius: "var(--radius-lg)",
        overflow: "hidden",
      }}
    >
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-2 px-4 py-3 text-left hover:opacity-80 transition-opacity"
        aria-expanded={open}
        aria-controls="logbook-entries"
        style={{ background: "transparent", border: "none", cursor: "pointer" }}
      >
        <BookOpen
          size={13}
          aria-hidden="true"
          style={{ color: "var(--color-accent-400)", flexShrink: 0 }}
        />
        <span
          className="label-caps"
          style={{ color: "var(--color-fg-tertiary)", margin: 0 }}
        >
          Digital Logbook
        </span>
        <span
          className="ml-auto"
          style={{ color: "var(--color-fg-faint)" }}
          aria-hidden="true"
        >
          {open
            ? <ChevronDown size={13} />
            : <ChevronRight size={13} />
          }
        </span>
      </button>

      {open && (
        <div
          id="logbook-entries"
          style={{ borderTop: "1px solid var(--color-border-subtle)" }}
        >
          {isEmpty ? (
            <p
              className="px-4 py-4 text-center"
              style={{
                fontSize: "var(--text-xs)",
                color: "var(--color-fg-faint)",
                lineHeight: 1.6,
              }}
            >
              {LOGBOOK_EMPTY_MSG}
            </p>
          ) : (
            <ul className="divide-y" style={{ borderColor: "var(--color-border-subtle)" }} aria-label="Logbook entries">
              {entries.map((entry, i) => (
                <li
                  key={entry.ref_id ?? `${entry.ts}-${i}`}
                  className="flex items-start gap-2 px-4 py-2.5"
                >
                  <span className="mt-0.5 flex-shrink-0">
                    {entryTypeIcon(entry.entry_type)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 justify-between">
                      <p
                        className="text-xs font-medium truncate"
                        style={{ color: "var(--color-fg-primary)" }}
                      >
                        {entry.title}
                      </p>
                      <time
                        dateTime={String(entry.ts)}
                        className="label-caps flex-shrink-0"
                        style={{ color: "var(--color-fg-faint)", fontSize: "10px" }}
                      >
                        {formatTs(entry.ts)}
                      </time>
                    </div>
                    {entry.summary && (
                      <p
                        className="text-[11px] mt-0.5 leading-snug"
                        style={{ color: "var(--color-fg-tertiary)" }}
                      >
                        {entry.summary}
                      </p>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function AssetHeaderSkeleton() {
  return (
    <div
      className="px-4 pt-4 pb-3 border-b"
      style={{ borderColor: "var(--color-border)" }}
    >
      <div className="skeleton h-4 w-48 mb-2 rounded" />
      <div className="skeleton h-3 w-32 rounded" />
    </div>
  );
}

export function CenterPanel() {
  const router = useRouter();
  const {
    selectedAssetId,
    replaySpeed,
    setReplaySpeed,
    sensorBuffers,
    sensorMetas,
    streamConnected,
    streamStale,
    streamEnded,
    assetStatus,
    userRole,
  } = useEdithStore();

  // SSE stream for live sensor data — pass role for server-side routing (G5)
  useSseStream(selectedAssetId, replaySpeed, userRole);

  // Focus data for the guided verdict card (polls /api/focus every 5s)
  const {
    data: focusData,
    isLoading: focusLoading,
    isError: focusError,
  } = useFocus(selectedAssetId);

  const { data: detail, isLoading: detailLoading } = useQuery<AssetDetail>({
    queryKey: ["asset-detail", selectedAssetId],
    queryFn: () => fetchAssetDetail(selectedAssetId),
    staleTime: 60_000,
  });

  const reportMutation = useMutation({
    mutationFn: postReport,
    onSuccess: (data) => {
      router.push(`/report/${data.report_id}`);
    },
    onError: () => toast.error("Failed to generate report"),
  });

  // Use focus state as the authoritative badge status when available;
  // fall back to SSE assetStatus while focus loads
  const statusBand = focusData
    ? stateToStatusBand(focusData.state)
    : toStatusBand(assetStatus as "normal" | "warning" | "alarm");

  const bufferList = sensorMetas
    .map((m) => sensorBuffers[m.tag])
    .filter(Boolean);

  const [speed, setSpeed] = useState(replaySpeed);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* ── Asset header ──────────────────────────────── */}
      {detailLoading ? (
        <AssetHeaderSkeleton />
      ) : (
        <div
          className="px-4 pt-4 pb-3 border-b flex-shrink-0"
          style={{ borderColor: "var(--color-border)" }}
        >
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div className="min-w-0">
              <div className="flex items-center gap-3 mb-1 flex-wrap">
                <span className="sensor-id text-lg">{selectedAssetId}</span>
                <StatusBadge status={statusBand} />

                {/* Live / stale / ended stream indicator */}
                {streamConnected && !streamStale && (
                  <span className="flex items-center gap-1">
                    <span
                      className="status-dot status-dot--healthy"
                      aria-label="Live data streaming"
                    />
                    <span
                      className="label-caps"
                      style={{ color: "var(--color-fg-faint)" }}
                    >
                      Live
                    </span>
                  </span>
                )}
                {streamStale && (
                  <span
                    className="label-caps"
                    style={{ color: "var(--color-status-warning-fg)" }}
                    aria-label="Stream data stale"
                  >
                    Stale
                  </span>
                )}
                {streamEnded && (
                  <span
                    className="label-caps"
                    style={{ color: "var(--color-fg-tertiary)" }}
                    aria-label="Stream replay ended"
                  >
                    Replay ended
                  </span>
                )}
              </div>

              {/* Use focus name (descriptive) if available; otherwise detail.description */}
              {(focusData?.name ?? detail?.description) && (
                <p
                  className="text-sm leading-snug"
                  style={{ color: "var(--color-fg-secondary)" }}
                >
                  {focusData?.name ?? detail?.description}
                  {detail?.process_stage && (
                    <span
                      className="ml-2 label-caps"
                      style={{ color: "var(--color-fg-faint)" }}
                    >
                      · {detail.process_stage}
                    </span>
                  )}
                </p>
              )}
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              {/* Replay speed */}
              <label
                className="flex items-center gap-2"
                htmlFor="replay-speed"
                aria-label="Replay speed"
              >
                <Activity
                  size={13}
                  aria-hidden="true"
                  style={{ color: "var(--color-fg-tertiary)" }}
                />
                <span className="label-caps">Speed</span>
                <select
                  id="replay-speed"
                  value={speed}
                  onChange={(e) => {
                    const v = Number(e.target.value);
                    setSpeed(v);
                    setReplaySpeed(v);
                  }}
                  className="text-xs rounded px-2 py-1 border"
                  style={{
                    background: "var(--color-bg-elevated)",
                    color: "var(--color-fg-primary)",
                    borderColor: "var(--color-border)",
                    fontFamily: "var(--font-mono)",
                  }}
                  aria-label="Replay speed multiplier"
                >
                  {[1, 2, 4, 8, 16, 32].map((s) => (
                    <option key={s} value={s}>
                      {s}x
                    </option>
                  ))}
                </select>
              </label>

              {/* Generate report button */}
              <button
                type="button"
                className={cn(
                  "btn-secondary py-1.5 px-3 text-xs",
                  reportMutation.isPending && "opacity-60"
                )}
                disabled={reportMutation.isPending}
                aria-label="Generate maintenance report"
                onClick={() =>
                  reportMutation.mutate({
                    asset_id: selectedAssetId,
                    kind: "incident",
                  })
                }
              >
                <Zap size={12} aria-hidden="true" />
                {reportMutation.isPending ? "Generating…" : "Report"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Scrollable content ─────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        {/* 1. VERDICT CARD — highest eye priority, always first */}
        {focusLoading ? (
          <VerdictCardSkeleton />
        ) : focusError || !focusData ? (
          <div
            className="p-4 text-center rounded"
            style={{
              background: "var(--color-bg-card)",
              border: "1px solid var(--color-border)",
              borderRadius: "var(--radius-lg)",
            }}
          >
            <p className="text-xs" style={{ color: "var(--color-fg-tertiary)" }}>
              When a sensor crosses a threshold, EDITH&apos;s diagnosis appears here
              automatically. You can also ask EDITH anything about this machine.
            </p>
          </div>
        ) : (
          <VerdictCard data={focusData} assetId={selectedAssetId} />
        )}

        {/* 2. SENSOR GRAPHS — supporting evidence below verdict */}
        {bufferList.length > 0 && (
          <div>
            {/* Section header + ROB-07 historian-replay chip */}
            <div className="flex items-center gap-2 mb-3 flex-wrap">
              <div
                className="hud-heading mb-0 border-0 pb-0 flex-shrink-0"
                style={{ color: "var(--color-fg-faint)" }}
              >
                Live sensor readings
              </div>
              {/* ROB-07: historian replay label — always shown since stream plays back historical data */}
              <span
                className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium flex-shrink-0"
                style={{
                  background: "oklch(78% 0.17 78 / 0.08)",
                  border: "1px solid oklch(78% 0.17 78 / 0.30)",
                  color: "var(--color-status-warning-fg)",
                  fontFamily: "var(--font-mono)",
                  letterSpacing: "0.03em",
                }}
                aria-label="Historian replay: these graphs replay a past degradation episode"
                title="These graphs are replaying a historical degradation episode, not live real-time data"
              >
                HISTORIAN REPLAY — playing back a past degradation episode (timestamps from 2025)
              </span>
            </div>

            {/* Graph hint — only when stream hasn't started yet */}
            {!streamConnected && bufferList.every((b) => b.timestamps.length === 0) && (
              <p className="panel-hint text-center mb-3">
                The shaded band is the safe operating range. A reading touching
                or crossing the edge means investigate now.
              </p>
            )}

            <div className="space-y-3">
              {bufferList.map((buf) => (
                <SensorChart key={buf.tag} buffer={buf} height={100} />
              ))}
            </div>

            {/* ROB-07: contextual note when stream shows warning/alarm but verdict is healthy */}
            {(assetStatus === "warning" || assetStatus === "alarm") && (
              <p
                className="mt-2 text-[11px] leading-relaxed"
                style={{ color: "var(--color-fg-faint)" }}
                aria-live="polite"
              >
                The replay below is showing a PAST episode — the machine&apos;s current baseline is healthy.
              </p>
            )}
          </div>
        )}

        {/* Connecting state — no buffers yet */}
        {!streamConnected && bufferList.length === 0 && (
          <div className="flex items-center justify-center h-20">
            <p
              className="text-xs"
              style={{ color: "var(--color-fg-tertiary)" }}
            >
              Connecting to live sensor stream…
            </p>
          </div>
        )}

        {/* 3. DIGITAL LOGBOOK — G9-frontend */}
        <LogbookSection assetId={selectedAssetId} />
      </div>
    </div>
  );
}
