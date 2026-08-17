"use client";

import React, { useId, useRef, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, ChevronRight, Cpu, Clock } from "lucide-react";
import { cn, API_BASE } from "@/lib/utils";
import { OutputCard } from "@/components/ui/output-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { useEdithStore, type ChatMessage } from "@/store/edith-store";
import { useFocus } from "@/hooks/use-focus";
import type { AskResponse, ReasoningTrace, TraceStep, StatusBand, FocusChip } from "@/lib/types";

function toStatusBandSafe(rb: string | undefined): StatusBand {
  if (!rb) return "unknown";
  const map: Record<string, StatusBand> = {
    low: "healthy", medium: "warning", high: "alarm", critical: "critical",
    healthy: "healthy", warning: "warning", alarm: "alarm",
  };
  return map[rb.toLowerCase()] ?? "unknown";
}

async function askEdith(
  query: string,
  sessionId: string,
  assetId: string
): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, session_id: sessionId, asset_id: assetId }),
  });
  if (!res.ok) throw new Error(`Ask failed: ${res.status}`);
  return res.json();
}

// ─── Reasoning trace expandable (J4 / DIFF-04 / G7) ─────────────────────────

const KIND_LABEL: Record<string, string> = {
  plan:      "Plan",
  tool:      "Tool",
  ml:        "ML Model",
  rag:       "RAG Retrieval",
  synthesis: "Synthesis",
  llm:       "LLM",
};

function kindLabel(kind: string): string {
  return KIND_LABEL[kind] ?? kind.charAt(0).toUpperCase() + kind.slice(1);
}

function kindColor(kind: string): string {
  switch (kind) {
    case "plan":      return "var(--color-accent-400)";
    case "tool":      return "oklch(75% 0.13 213)";
    case "ml":        return "var(--color-status-healthy-fg)";
    case "rag":       return "var(--color-status-warning-fg)";
    case "synthesis": return "oklch(72% 0.16 300)";
    case "llm":       return "var(--color-fg-secondary)";
    default:          return "var(--color-fg-tertiary)";
  }
}

interface TraceStepRowProps { step: TraceStep; }

function TraceStepRow({ step }: TraceStepRowProps) {
  const [open, setOpen] = useState(false);
  const hasDetail = step.detail && Object.keys(step.detail).length > 0;

  return (
    <div className="flex gap-2 text-[11px]">
      {/* Timeline spine */}
      <div className="flex flex-col items-center flex-shrink-0" style={{ width: 16 }}>
        <div
          className="w-2 h-2 rounded-full flex-shrink-0 mt-0.5"
          style={{ background: kindColor(step.kind) }}
          aria-hidden="true"
        />
        <div
          className="flex-1 w-px mt-0.5"
          style={{ background: "var(--color-border-subtle)", minHeight: 8 }}
          aria-hidden="true"
        />
      </div>

      {/* Step content */}
      <div className="flex-1 min-w-0 pb-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span
            className="font-semibold"
            style={{ color: kindColor(step.kind), fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.04em" }}
          >
            {kindLabel(step.kind).toUpperCase()}
          </span>
          <span style={{ color: "var(--color-fg-faint)" }}>·</span>
          <span style={{ color: "var(--color-fg-secondary)" }}>{step.action}</span>
          {step.latency_ms > 0 && (
            <span
              className="flex items-center gap-0.5 ml-auto flex-shrink-0"
              style={{ color: "var(--color-fg-faint)", fontFamily: "var(--font-mono)" }}
            >
              <Clock size={9} aria-hidden="true" />
              {step.latency_ms}ms
            </span>
          )}
        </div>

        <p style={{ color: "var(--color-fg-tertiary)", marginTop: 2, lineHeight: 1.5 }}>
          {step.result_summary}
        </p>

        {hasDetail && (
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="flex items-center gap-0.5 mt-1 hover:opacity-80 transition-opacity"
            style={{ color: "var(--color-fg-faint)", fontFamily: "var(--font-mono)", fontSize: 10 }}
            aria-expanded={open}
          >
            {open ? <ChevronDown size={10} aria-hidden="true" /> : <ChevronRight size={10} aria-hidden="true" />}
            detail
          </button>
        )}

        {open && hasDetail && (
          <pre
            className="mt-1 p-2 rounded text-[10px] overflow-x-auto"
            style={{
              background: "var(--color-bg-raised)",
              color: "var(--color-fg-secondary)",
              fontFamily: "var(--font-mono)",
              border: "1px solid var(--color-border-subtle)",
              whiteSpace: "pre-wrap",
              wordBreak: "break-all",
            }}
          >
            {JSON.stringify(step.detail, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}

interface TraceExpandableProps { trace: ReasoningTrace; }

function TraceExpandable({ trace }: TraceExpandableProps) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="mt-2.5 rounded"
      style={{
        background: "var(--color-bg-raised)",
        border: "1px solid var(--color-border-subtle)",
        overflow: "hidden",
      }}
    >
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left hover:opacity-80 transition-opacity"
        aria-expanded={open}
        aria-controls="trace-timeline"
        style={{ background: "transparent", border: "none", cursor: "pointer" }}
      >
        <Cpu size={11} aria-hidden="true" style={{ color: "var(--color-accent-400)", flexShrink: 0 }} />
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            color: "var(--color-fg-tertiary)",
            fontWeight: 600,
          }}
        >
          How EDITH decided
        </span>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            color: "var(--color-fg-faint)",
            marginLeft: 4,
          }}
        >
          {trace.step_count} steps · {trace.total_latency_ms}ms
        </span>
        <span className="ml-auto" style={{ color: "var(--color-fg-faint)" }} aria-hidden="true">
          {open ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
        </span>
      </button>

      {open && (
        <div
          id="trace-timeline"
          className="px-3 pb-3 pt-1"
          style={{ borderTop: "1px solid var(--color-border-subtle)" }}
        >
          {trace.steps.map((step) => (
            <TraceStepRow key={step.step} step={step} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Reasoning-mode + confidence pills (J11 / DIFF-08) ───────────────────────

interface ReasoningPillsProps {
  reasoningMode?: string | null;
  confidenceLabel?: string | null;
}

function ReasoningPills({ reasoningMode, confidenceLabel }: ReasoningPillsProps) {
  if (!reasoningMode && !confidenceLabel) return null;
  return (
    <div className="flex flex-wrap gap-1 mt-2" aria-label="Reasoning metadata">
      {reasoningMode && (
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium"
          style={{
            background: "oklch(22% 0.075 213 / 0.25)",
            border: "1px solid oklch(72% 0.16 213 / 0.20)",
            color: "var(--color-accent-400)",
            fontFamily: "var(--font-mono)",
            letterSpacing: "0.02em",
          }}
          aria-label={`Reasoning mode: ${reasoningMode}`}
        >
          <Cpu size={9} aria-hidden="true" />
          {reasoningMode}
        </span>
      )}
      {confidenceLabel && (
        <span
          className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium"
          style={{
            background: "var(--color-bg-elevated)",
            border: "1px solid var(--color-border)",
            color: "var(--color-fg-tertiary)",
            fontFamily: "var(--font-mono)",
            letterSpacing: "0.02em",
          }}
          aria-label={`Confidence: ${confidenceLabel}`}
        >
          {confidenceLabel}
        </span>
      )}
    </div>
  );
}

// ─── Proactive chip list ──────────────────────────────────────────────────────

interface ChipListProps {
  chips: FocusChip[];
  onChipClick: (label: string) => void;
  disabled: boolean;
}

function ChipList({ chips, onChipClick, disabled }: ChipListProps) {
  if (chips.length === 0) {
    return (
      <p className="panel-hint text-xs py-2">
        Ask EDITH anything about this machine — history, procedures, spare parts.
        Use the suggestions above to get started.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-1.5" aria-label="EDITH suggested questions">
      {chips.map((chip, i) => (
        <button
          key={`${chip.label}-${i}`}
          type="button"
          className="proactive-chip"
          onClick={() => onChipClick(chip.label)}
          disabled={disabled}
          aria-label={`Ask EDITH: ${chip.label}`}
        >
          <span
            className="text-sm font-medium leading-snug"
            style={{ color: "var(--color-fg-primary)" }}
          >
            {chip.label}
          </span>
          {chip.why && (
            <span
              className="text-xs leading-snug"
              style={{ color: "var(--color-fg-faint)" }}
            >
              {chip.why}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}

// ─── Main copilot panel ───────────────────────────────────────────────────────

export function CopilotPanel() {
  const {
    chatMessages,
    chatProcessing,
    addChatMessage,
    setChatProcessing,
    selectedAssetId,
  } = useEdithStore();

  const { data: focusData } = useFocus(selectedAssetId);
  const chips: FocusChip[] = focusData?.chips ?? [];

  const [draft, setDraft] = useState("");
  const sessionId = useRef(`session-${Date.now()}`);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputId = useId();

  // Reset session when asset changes
  const prevAssetRef = useRef(selectedAssetId);
  useEffect(() => {
    if (prevAssetRef.current !== selectedAssetId) {
      prevAssetRef.current = selectedAssetId;
      sessionId.current = `session-${Date.now()}`;
    }
  }, [selectedAssetId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  async function handleSubmit(query: string) {
    const q = query.trim();
    if (!q || chatProcessing) return;
    setDraft("");

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: q,
    };
    addChatMessage(userMsg);
    setChatProcessing(true);

    try {
      const resp = await askEdith(q, sessionId.current, selectedAssetId);
      const assistantMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: resp.answer,
        citations: resp.sources,
        riskBand: resp.risk_band,
        rul: resp.rul,
        sections: resp.sections,
        trace: resp.trace ?? null,
        reasoningMode: resp.reasoning_mode ?? null,
        confidenceLabel: resp.confidence_label ?? null,
      };
      addChatMessage(assistantMsg);
    } catch {
      addChatMessage({
        id: `err-${Date.now()}`,
        role: "assistant",
        content: "I could not process that request right now. Please try again.",
      });
    } finally {
      setChatProcessing(false);
    }
  }

  function onChipClick(label: string) {
    if (chatProcessing) return;
    handleSubmit(label);
  }

  function onFormSubmit(e: React.FormEvent) {
    e.preventDefault();
    handleSubmit(draft);
  }

  return (
    <section
      className="hud-panel flex flex-col h-full overflow-hidden"
      aria-label="EDITH copilot"
    >
      {/* ── EDITH SUGGESTS section — always visible ─── */}
      <div
        className="px-4 py-3 border-b flex-shrink-0"
        style={{ borderColor: "var(--color-border)" }}
      >
        <p
          className="label-caps mb-2"
          style={{ color: "var(--color-fg-faint)" }}
          aria-label="EDITH proactive suggestions"
        >
          EDITH suggests
        </p>
        <ChipList
          chips={chips}
          onChipClick={onChipClick}
          disabled={chatProcessing}
        />
      </div>

      {/* ── Chat messages ────────────────────────────── */}
      <div
        className="flex-1 overflow-y-auto px-4 py-3 flex flex-col gap-3"
        role="log"
        aria-live="polite"
        aria-label="Conversation history"
      >
        {/* Empty state hint */}
        {chatMessages.length === 0 && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="panel-hint text-center py-4"
          >
            Ask EDITH anything about this machine — history, procedures, spare
            parts. Use the suggestions above to get started.
          </motion.p>
        )}

        <AnimatePresence initial={false} mode="popLayout">
          {chatMessages.map((msg) => (
            <motion.div
              key={msg.id}
              layout
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ type: "spring", stiffness: 320, damping: 28 }}
              className={cn(
                "flex flex-col",
                msg.role === "user" ? "items-end" : "items-start"
              )}
            >
              {msg.role === "user" ? (
                <div className="chat-bubble--user">
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>
              ) : (
                <div className="chat-bubble--edith w-full">
                  <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                    <p className="label-caps" style={{ margin: 0 }}>EDITH</p>
                    {/* J11/DIFF-08: inline reasoning mode pill next to label */}
                    {msg.reasoningMode && (
                      <span
                        className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full"
                        style={{
                          background: "oklch(22% 0.075 213 / 0.25)",
                          border: "1px solid oklch(72% 0.16 213 / 0.20)",
                          color: "var(--color-accent-400)",
                          fontFamily: "var(--font-mono)",
                          fontSize: 9,
                          letterSpacing: "0.03em",
                        }}
                        aria-label={`Reasoning mode: ${msg.reasoningMode}`}
                      >
                        <Cpu size={8} aria-hidden="true" />
                        {msg.reasoningMode}
                      </span>
                    )}
                  </div>
                  {msg.sections && msg.sections.length > 0 ? (
                    <div className="flex flex-col gap-2">
                      {msg.sections.map((s) => (
                        <OutputCard
                          key={s.key}
                          heading={s.title}
                          brief={s.brief}
                          enhancedBrief={
                            s.detail ? (
                              <div
                                className="text-sm leading-relaxed whitespace-pre-line"
                                style={{ color: "var(--color-fg-secondary)" }}
                              >
                                {s.detail}
                              </div>
                            ) : undefined
                          }
                          citations={s.sources}
                          riskBand={s.key === "prioritizer" ? msg.riskBand : undefined}
                          rul={s.key === "predictor" ? msg.rul : undefined}
                          defaultExpanded={s.key === "recommender"}
                        />
                      ))}
                    </div>
                  ) : (
                    <div
                      className="text-sm leading-relaxed whitespace-pre-line"
                      style={{ color: "var(--color-fg-primary)" }}
                    >
                      {msg.content}
                    </div>
                  )}
                  {!msg.sections?.length &&
                    msg.citations &&
                    msg.citations.length > 0 && (
                      <div
                        className="flex flex-wrap gap-1 mt-2"
                        aria-label="Sources"
                      >
                        {msg.citations.slice(0, 5).map((c, i) => (
                          <span key={i} className="cite-pill">
                            {c}
                          </span>
                        ))}
                      </div>
                    )}
                  {/* J11/DIFF-08: reasoning mode + confidence pills */}
                  <ReasoningPills
                    reasoningMode={msg.reasoningMode}
                    confidenceLabel={msg.confidenceLabel}
                  />

                  {(msg.riskBand || msg.rul != null) && (
                    <div
                      className="flex items-center gap-2 mt-2.5 pt-2 border-t"
                      style={{ borderColor: "var(--color-border-subtle)" }}
                    >
                      {msg.riskBand && (
                        <StatusBadge status={toStatusBandSafe(msg.riskBand)} />
                      )}
                      {msg.rul != null && (
                        <span
                          className="mono-data text-xs"
                          style={{ color: "var(--color-fg-tertiary)" }}
                        >
                          RUL{" "}
                          <span className="font-semibold">{msg.rul}</span> cy
                        </span>
                      )}
                    </div>
                  )}

                  {/* J4/DIFF-04/G7: multi-agent reasoning trace expandable */}
                  {msg.trace && msg.trace.steps && msg.trace.steps.length > 0 && (
                    <TraceExpandable trace={msg.trace} />
                  )}
                </div>
              )}
            </motion.div>
          ))}

          {/* Thinking indicator */}
          {chatProcessing && (
            <motion.div
              key="thinking"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex items-start"
              aria-label="EDITH is processing your question"
              aria-live="polite"
            >
              <div className="chat-bubble--edith">
                <p className="label-caps mb-1.5">EDITH</p>
                <div
                  className="edith-thinking"
                  aria-hidden="true"
                  role="presentation"
                >
                  <span className="edith-thinking-dot" />
                  <span className="edith-thinking-dot" />
                  <span className="edith-thinking-dot" />
                </div>
                <p
                  className="text-xs mt-1"
                  style={{ color: "var(--color-fg-tertiary)" }}
                >
                  Analysing sensor data and maintenance records…
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={bottomRef} aria-hidden="true" />
      </div>

      {/* ── Input bar ─────────────────────────────────── */}
      <form
        onSubmit={onFormSubmit}
        className="px-4 py-3 border-t flex-shrink-0"
        style={{ borderColor: "var(--color-border)" }}
        aria-label="Ask EDITH a maintenance question"
      >
        <div className="flex gap-2 items-end">
          <label htmlFor={inputId} className="sr-only">
            Ask EDITH about plant maintenance
          </label>
          <textarea
            id={inputId}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(draft);
              }
            }}
            placeholder="Ask about this machine…"
            className="flex-1 resize-none rounded-[var(--radius-md)] px-3 py-2.5 text-sm leading-relaxed border transition-colors"
            style={{
              background: "var(--color-bg-elevated)",
              color: "var(--color-fg-primary)",
              borderColor: "var(--color-border)",
              fontFamily: "var(--font-sans)",
              minHeight: "44px",
              maxHeight: "120px",
            }}
            rows={1}
            disabled={chatProcessing}
            aria-multiline="true"
            aria-disabled={chatProcessing}
          />
          <button
            type="submit"
            disabled={!draft.trim() || chatProcessing}
            aria-disabled={!draft.trim() || chatProcessing}
            aria-label="Send question to EDITH"
            className="btn-primary flex-shrink-0 self-end"
          >
            Send
          </button>
        </div>
        <p
          className="text-xs mt-1.5"
          style={{ color: "var(--color-fg-faint)" }}
        >
          Enter to send · Shift+Enter for new line
        </p>
      </form>
    </section>
  );
}
