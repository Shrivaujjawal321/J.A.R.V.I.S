/**
 * EDITH Design System — Reference Component Implementations
 * Stack: React 19 + Tailwind 4 (CSS vars) + Framer Motion 12 + shadcn/ui v4
 * A11y: WCAG 2.2 AA, keyboard-complete, prefers-reduced-motion aware
 *
 * These are REFERENCE implementations for the frontend engineer.
 * Import the hud-*.css classes from edith-theme.css.
 *
 * Framer Motion spring presets — use these constants, don't guess:
 */

"use client";

import { AnimatePresence, motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { ChevronDown, ChevronRight, Download, FileText, AlertTriangle } from "lucide-react";
import React, { useId, useRef, useState, useEffect, useReducer } from "react";
import { cn } from "@/lib/utils";

// ─── Motion presets ────────────────────────────────────────────────────────
export const SPRING = {
  TILE:    { type: "spring" as const, stiffness: 320, damping: 28, mass: 1 },
  NUMBER:  { type: "spring" as const, stiffness: 280, damping: 32, mass: 0.8 },
  PANEL:   { type: "spring" as const, stiffness: 260, damping: 30, mass: 1 },
  ALERT:   { type: "spring" as const, stiffness: 380, damping: 24, mass: 0.9 },
};

// prefers-reduced-motion — read once at module load, recheck on mount
const prefersReducedMotion = () =>
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ─── Status types ──────────────────────────────────────────────────────────
export type StatusBand = "healthy" | "warning" | "alarm" | "critical" | "unknown" | "offline";

const STATUS_LABEL: Record<StatusBand, string> = {
  healthy: "Healthy",
  warning: "Warning",
  alarm:   "Alarm",
  critical:"Critical",
  unknown: "Unknown",
  offline: "Offline",
};

// ═══════════════════════════════════════════════════════════════════════════
// 1. STATUS TILE  — one of the 15-asset health-strip tiles
// ═══════════════════════════════════════════════════════════════════════════
interface StatusTileProps {
  assetId:     string;
  description: string;
  status:      StatusBand;
  rul?:        number | null;  // remaining useful life in cycles
  breaches?:   number;
  selected?:   boolean;
  loading?:    boolean;
  onClick?:    () => void;
}

export function StatusTile({
  assetId, description, status, rul, breaches = 0, selected, loading, onClick,
}: StatusTileProps) {
  const reduced = prefersReducedMotion();
  const id = useId();
  const descId = `${id}-desc`;

  if (loading) {
    return (
      <div
        className="status-tile"
        aria-busy="true"
        aria-label={`Loading asset ${assetId}`}
        role="status"
      >
        <div className="skeleton h-3 w-16 mb-2" />
        <div className="skeleton h-2.5 w-24 mb-3" />
        <div className="skeleton h-2 w-12" />
      </div>
    );
  }

  const tileVariants = {
    hidden:  { opacity: 0, y: reduced ? 0 : 8 },
    visible: { opacity: 1, y: 0 },
    exit:    { opacity: 0, scale: 0.97 },
  };

  return (
    <motion.button
      type="button"
      role="button"
      aria-pressed={selected}
      aria-describedby={descId}
      aria-label={`${assetId} — ${STATUS_LABEL[status]}${rul != null ? `, RUL ${rul} cycles` : ""}`}
      variants={tileVariants}
      initial="hidden"
      animate="visible"
      transition={reduced ? { duration: 0.05 } : SPRING.TILE}
      onClick={onClick}
      className={cn(
        "status-tile w-full text-left",
        `status-tile--${status}`,
        selected && "status-tile--selected",
        status === "offline" && "status-tile--offline",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--color-accent-400)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--color-bg-base)]"
      )}
    >
      {/* Header row */}
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <span className="sensor-id truncate">{assetId}</span>
        <StatusBadge status={status} compact />
      </div>

      {/* Description */}
      <p
        id={descId}
        className="text-xs text-[var(--color-fg-secondary)] truncate mb-2 leading-tight"
      >
        {description}
      </p>

      {/* Data row */}
      <div className="flex items-center gap-3">
        {rul != null && (
          <span className="mono-data text-xs text-[var(--color-fg-tertiary)]">
            RUL{" "}
            <span className={cn(
              "font-semibold",
              rul < 50  ? "text-[var(--color-status-critical-fg)]" :
              rul < 150 ? "text-[var(--color-status-warning-fg)]" :
              "text-[var(--color-fg-primary)]"
            )}>
              {rul}
            </span>{" "}cy
          </span>
        )}
        {breaches > 0 && (
          <span
            className="mono-data text-xs text-[var(--color-status-warning-fg)]"
            aria-label={`${breaches} sensor breaches`}
          >
            {breaches} ⚡
          </span>
        )}
      </div>
    </motion.button>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 2. STATUS BADGE  — pill with dot + label
// ═══════════════════════════════════════════════════════════════════════════
interface StatusBadgeProps {
  status:   StatusBand;
  compact?: boolean;
  className?: string;
}

export function StatusBadge({ status, compact, className }: StatusBadgeProps) {
  return (
    <span
      className={cn("status-badge", `status-badge--${status}`, className)}
      aria-label={`Status: ${STATUS_LABEL[status]}`}
    >
      <span className={cn("status-dot", `status-dot--${status}`)} aria-hidden="true" />
      {!compact && STATUS_LABEL[status]}
    </span>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 3. ANIMATED KPI VALUE  — spring number ticker
// ═══════════════════════════════════════════════════════════════════════════
interface KpiValueProps {
  label:     string;
  value:     number;
  unit?:     string;
  variant?:  "default" | "accent" | "critical" | "warning" | "healthy";
  precision?: number;
}

export function KpiCard({ label, value, unit, variant = "default", precision = 0 }: KpiValueProps) {
  const reduced = prefersReducedMotion();
  const mv = useMotionValue(value);
  const spring = useSpring(mv, reduced ? { duration: 0 } : SPRING.NUMBER);
  const display = useTransform(spring, (v) => v.toFixed(precision));

  useEffect(() => { mv.set(value); }, [value, mv]);

  return (
    <div className="kpi-card">
      <div className="kpi-label">{label}</div>
      <div className={cn("kpi-value", variant !== "default" && `kpi-value--${variant}`)}>
        <motion.span>{display}</motion.span>
        {unit && (
          <span className="text-[var(--color-fg-tertiary)] font-normal ml-1 text-sm tracking-normal">
            {unit}
          </span>
        )}
      </div>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 4. ALERT CARD  — proactive EDITH alert with RUL, RCA header, expand
// ═══════════════════════════════════════════════════════════════════════════
interface AlertCardProps {
  assetId:   string;
  severity:  "warning" | "alarm" | "critical";
  title:     string;
  brief:     string;
  timestamp: string;
  rul?:      number;
  onDismiss?: () => void;
  onDrillDown?: () => void;
}

export function AlertCard({
  assetId, severity, title, brief, timestamp, rul, onDismiss, onDrillDown,
}: AlertCardProps) {
  const reduced = prefersReducedMotion();
  const headingId = useId();

  const cardVariants = {
    hidden:  { opacity: 0, x: reduced ? 0 : -16, scale: reduced ? 1 : 0.98 },
    visible: { opacity: 1, x: 0, scale: 1 },
    exit:    { opacity: 0, x: reduced ? 0 : 16, scale: 0.97 },
  };

  return (
    <motion.div
      role="alert"
      aria-labelledby={headingId}
      aria-live={severity === "critical" ? "assertive" : "polite"}
      aria-atomic="true"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      transition={reduced ? { duration: 0.05 } : SPRING.ALERT}
      className={cn("alert-card", `alert-card--${severity}`)}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <AlertTriangle
            size={14}
            className={cn(
              "flex-shrink-0 mt-0.5",
              severity === "critical" ? "text-[var(--color-status-critical-fg)]" :
              severity === "alarm"    ? "text-[var(--color-status-alarm-fg)]" :
              "text-[var(--color-status-warning-fg)]"
            )}
            aria-hidden="true"
          />
          <span id={headingId} className="sensor-id text-sm truncate">{assetId}</span>
          <StatusBadge status={severity} />
        </div>
        {rul != null && (
          <span className="mono-data text-xs text-[var(--color-fg-tertiary)] flex-shrink-0">
            RUL <span className="text-[var(--color-status-critical-fg)] font-semibold">{rul}</span> cy
          </span>
        )}
      </div>

      {/* Content */}
      <p className="text-sm font-medium text-[var(--color-fg-primary)] mb-1 leading-snug">{title}</p>
      <p className="text-xs text-[var(--color-fg-secondary)] leading-relaxed mb-3">{brief}</p>

      {/* Footer */}
      <div className="flex items-center justify-between gap-2">
        <time
          dateTime={timestamp}
          className="label-caps text-[var(--color-fg-faint)]"
        >
          {timestamp}
        </time>
        <div className="flex items-center gap-2">
          {onDrillDown && (
            <button
              type="button"
              onClick={onDrillDown}
              className="btn-secondary py-1.5 px-3 text-xs"
              aria-label={`Drill down into ${assetId} alert`}
            >
              Investigate
            </button>
          )}
          {onDismiss && (
            <button
              type="button"
              onClick={onDismiss}
              className="btn-ghost py-1.5 px-3 text-xs"
              aria-label={`Dismiss ${severity} alert for ${assetId}`}
            >
              Dismiss
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 5. EXPANDABLE OUTPUT CARD  — heading + brief, expand → enhanced brief
// ═══════════════════════════════════════════════════════════════════════════
interface OutputCardProps {
  heading:         string;
  brief:           string;
  enhancedBrief?:  React.ReactNode;   // full markdown/citations revealed on expand
  citations?:      string[];
  rul?:            number;
  riskBand?:       StatusBand;
  defaultExpanded?: boolean;
}

export function OutputCard({
  heading, brief, enhancedBrief, citations, rul, riskBand, defaultExpanded = false,
}: OutputCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const reduced = prefersReducedMotion();
  const bodyId = useId();

  return (
    <div
      className={cn("output-card", expanded && "output-card--expanded")}
    >
      {/* Clickable header */}
      <button
        type="button"
        aria-expanded={expanded}
        aria-controls={bodyId}
        onClick={() => setExpanded((v) => !v)}
        className="output-card-header w-full"
      >
        <div className="flex items-start gap-3 min-w-0">
          {/* Chevron */}
          <motion.span
            animate={{ rotate: expanded ? 90 : 0 }}
            transition={reduced ? { duration: 0 } : { duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="flex-shrink-0 mt-0.5 text-[var(--color-fg-tertiary)]"
            aria-hidden="true"
          >
            <ChevronRight size={15} />
          </motion.span>

          <div className="min-w-0 text-left">
            <div className="text-sm font-medium text-[var(--color-fg-primary)] mb-1 leading-snug">
              {heading}
            </div>
            <p className="text-xs text-[var(--color-fg-secondary)] leading-relaxed line-clamp-2">
              {brief}
            </p>
          </div>
        </div>

        {/* Right side: badges */}
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          {rul != null && (
            <span className="mono-data text-xs text-[var(--color-fg-tertiary)]">
              {rul} cy
            </span>
          )}
          {riskBand && <StatusBadge status={riskBand} compact />}
        </div>
      </button>

      {/* Expandable body */}
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            id={bodyId}
            role="region"
            aria-label={`Details for ${heading}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={reduced
              ? { duration: 0.05 }
              : { height: { type: "spring", stiffness: 260, damping: 30 }, opacity: { duration: 0.15 } }
            }
            style={{ overflow: "hidden" }}
          >
            <div className="output-card-body">
              {enhancedBrief && (
                <div className="text-sm text-[var(--color-fg-primary)] leading-relaxed mb-3">
                  {enhancedBrief}
                </div>
              )}
              {citations && citations.length > 0 && (
                <div
                  className="flex flex-wrap gap-1 mt-2"
                  aria-label="Source citations"
                >
                  <span className="label-caps mr-1 self-center">Sources:</span>
                  {citations.map((c, i) => (
                    <span key={i} className="cite-pill" aria-label={`Source ${c}`}>
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 6. COPILOT CHAT PANEL — EDITH conversation interface
// ═══════════════════════════════════════════════════════════════════════════
interface Message {
  id:        string;
  role:      "user" | "assistant";
  content:   string;
  citations?: string[];
  rul?:      number;
  riskBand?: StatusBand;
  turn?:     unknown; // full turn object if needed
}

interface CopilotPanelProps {
  messages:     Message[];
  isProcessing: boolean;
  demoChips?:   Array<{ label: string; query: string }>;
  onSubmit:     (query: string) => void;
}

export function CopilotPanel({ messages, isProcessing, demoChips, onSubmit }: CopilotPanelProps) {
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputId = useId();
  const reduced = prefersReducedMotion();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: reduced ? "instant" : "smooth" });
  }, [messages, reduced]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = draft.trim();
    if (!q || isProcessing) return;
    onSubmit(q);
    setDraft("");
  }

  return (
    <section
      className="hud-panel flex flex-col h-full"
      aria-label="EDITH copilot chat"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--color-border)]">
        <span className="status-dot status-dot--healthy" aria-hidden="true" />
        <span className="font-semibold text-sm text-[var(--color-fg-primary)] tracking-tight">EDITH</span>
        <span className="text-xs text-[var(--color-fg-tertiary)]">agentic maintenance wizard</span>
      </div>

      {/* Message list */}
      <div
        className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3"
        role="log"
        aria-live="polite"
        aria-label="Conversation history"
      >
        {/* Cold-start demo chips */}
        {messages.length === 0 && demoChips && (
          <motion.div
            initial={reduced ? {} : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={reduced ? { duration: 0 } : SPRING.PANEL}
            className="flex flex-wrap gap-2"
            aria-label="Quick start prompts"
          >
            <p className="w-full label-caps mb-1">Try a scenario:</p>
            {demoChips.map((chip) => (
              <button
                key={chip.label}
                type="button"
                onClick={() => onSubmit(chip.query)}
                className="demo-chip"
                aria-label={`Ask EDITH: ${chip.query}`}
              >
                {chip.label}
              </button>
            ))}
          </motion.div>
        )}

        {/* Messages */}
        <AnimatePresence initial={false} mode="popLayout">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              layout
              initial={reduced ? {} : { opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={reduced ? { duration: 0 } : SPRING.TILE}
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
                <div className="chat-bubble--edith">
                  {/* Role label */}
                  <p className="label-caps mb-1.5">EDITH</p>
                  <div className="text-sm leading-relaxed text-[var(--color-fg-primary)]">
                    {msg.content}
                  </div>
                  {/* Inline citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2" aria-label="Sources cited">
                      {msg.citations.map((c, i) => (
                        <span key={i} className="cite-pill">{c}</span>
                      ))}
                    </div>
                  )}
                  {/* Risk/RUL badge row */}
                  {(msg.riskBand || msg.rul != null) && (
                    <div className="flex items-center gap-2 mt-2.5 pt-2 border-t border-[var(--color-border-subtle)]">
                      {msg.riskBand && <StatusBadge status={msg.riskBand} />}
                      {msg.rul != null && (
                        <span className="mono-data text-xs text-[var(--color-fg-tertiary)]">
                          RUL <span className="font-semibold">{msg.rul}</span> cy
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ))}

          {/* Thinking indicator */}
          {isProcessing && (
            <motion.div
              key="thinking"
              initial={reduced ? {} : { opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex items-start"
              aria-label="EDITH is processing"
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
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={bottomRef} aria-hidden="true" />
      </div>

      {/* Input bar */}
      <form
        onSubmit={handleSubmit}
        className="px-4 py-3 border-t border-[var(--color-border)]"
        aria-label="Ask EDITH a question"
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
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSubmit(e as unknown as React.FormEvent); }
            }}
            placeholder="Diagnose an asset, ask about RUL, request a maintenance plan…"
            className={cn(
              "flex-1 resize-none bg-[var(--color-bg-elevated)] border border-[var(--color-border)]",
              "text-sm text-[var(--color-fg-primary)] placeholder:text-[var(--color-fg-faint)]",
              "rounded-[var(--radius-md)] px-3 py-2.5 leading-relaxed",
              "focus-visible:outline-none focus-visible:border-[var(--color-accent-400)]",
              "focus-visible:ring-1 focus-visible:ring-[var(--color-accent-glow-soft)]",
              "transition-colors duration-[var(--duration-fast)]",
              "min-h-[44px] max-h-[140px]"
            )}
            rows={1}
            aria-multiline="true"
            disabled={isProcessing}
            aria-disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={!draft.trim() || isProcessing}
            aria-disabled={!draft.trim() || isProcessing}
            aria-label="Send message to EDITH"
            className={cn(
              "btn-primary flex-shrink-0 self-end",
              isProcessing && "btn-loading"
            )}
          >
            {!isProcessing && "Send"}
          </button>
        </div>
        <p className="text-xs text-[var(--color-fg-faint)] mt-1.5">
          Enter to send · Shift+Enter for new line
        </p>
      </form>
    </section>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 7. REPORT BUTTONS  — export / download actions
// ═══════════════════════════════════════════════════════════════════════════
interface ReportButtonsProps {
  assetId:        string;
  onDownloadPDF:  () => void;
  onDownloadJSON: () => void;
  onViewFull:     () => void;
  isGenerating?:  boolean;
}

export function ReportButtons({
  assetId, onDownloadPDF, onDownloadJSON, onViewFull, isGenerating,
}: ReportButtonsProps) {
  return (
    <div
      className="flex items-center flex-wrap gap-2"
      role="group"
      aria-label={`Export options for ${assetId}`}
    >
      <button
        type="button"
        onClick={onViewFull}
        className="btn-primary"
        aria-label={`View full maintenance report for ${assetId}`}
      >
        <FileText size={14} aria-hidden="true" />
        Full Report
      </button>
      <button
        type="button"
        onClick={onDownloadPDF}
        disabled={isGenerating}
        aria-disabled={isGenerating}
        className={cn("btn-secondary", isGenerating && "btn-loading")}
        aria-label={`Download PDF report for ${assetId}`}
      >
        <Download size={13} aria-hidden="true" />
        PDF
      </button>
      <button
        type="button"
        onClick={onDownloadJSON}
        className="btn-ghost"
        aria-label={`Download JSON data for ${assetId}`}
      >
        JSON
      </button>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 8. HUD PANEL WRAPPER  — glass container with mount animation
// ═══════════════════════════════════════════════════════════════════════════
interface HudPanelProps {
  children:   React.ReactNode;
  title?:     string;
  className?: string;
  variant?:   "base" | "raised";
  delay?:     number;
}

export function HudPanel({ children, title, className, variant = "base", delay = 0 }: HudPanelProps) {
  const reduced = prefersReducedMotion();
  const titleId = useId();

  return (
    <motion.section
      aria-labelledby={title ? titleId : undefined}
      initial={reduced ? {} : { opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={reduced ? { duration: 0 } : { ...SPRING.PANEL, delay }}
      className={cn("hud-panel", variant === "raised" && "hud-panel--raised", className)}
    >
      {title && (
        <div className="px-4 pt-4 pb-0">
          <h2 id={titleId} className="hud-heading">{title}</h2>
        </div>
      )}
      {children}
    </motion.section>
  );
}


// ═══════════════════════════════════════════════════════════════════════════
// 9. LIVE GRAPH CANVAS WRAPPER  — chart container with Recharts/D3 guidance
// ═══════════════════════════════════════════════════════════════════════════
/**
 * Use this wrapper around Recharts <ResponsiveContainer>.
 *
 * CHART STYLING RULES (see data-viz spec):
 *
 * Grid:      stroke="oklch(100% 0 0 / 0.06)"  strokeDasharray="2 4"
 * Axis:      stroke="oklch(50% 0.010 250)"  tick.fill="oklch(50% 0.010 250)"  tick.fontSize=11
 * Active line (live reading): stroke="oklch(72% 0.16 213)"  strokeWidth=2
 * Historical line:             stroke="oklch(50% 0.010 250)" strokeWidth=1
 * Area fill under live line:   fill="oklch(72% 0.16 213 / 0.08)" (gradientId)
 * Threshold band WARNING:      fill="oklch(78% 0.17 78 / 0.08)"
 * Threshold band ALARM:        fill="oklch(72% 0.21 48 / 0.10)"
 * Threshold line WARNING:      stroke="oklch(78% 0.17 78 / 0.35)"  strokeDasharray="4 6"
 * Threshold line ALARM:        stroke="oklch(72% 0.21 48 / 0.45)"  strokeDasharray="4 6"
 * Tooltip:   glass panel (bg-glass-raised + shadow-md), mono font, tabular-nums
 * Dot on breach: fill="oklch(64% 0.23 27)"  r=4  filter with drop-shadow glow
 */
export function ChartCanvas({
  children,
  title,
  className,
  live = false,
}: {
  children: React.ReactNode;
  title?: string;
  className?: string;
  live?: boolean;
}) {
  const titleId = useId();
  return (
    <figure
      aria-labelledby={title ? titleId : undefined}
      role="img"
      className={cn("chart-canvas", className)}
    >
      {title && (
        <figcaption id={titleId} className="hud-heading mb-3 flex items-center gap-2">
          {title}
          {live && (
            <span
              className="status-dot status-dot--healthy"
              aria-label="Live data"
              title="Live"
            />
          )}
        </figcaption>
      )}
      {children}
    </figure>
  );
}
