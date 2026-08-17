"use client";

import React, { useState, useEffect, useId } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronRight, Check, Edit3 } from "lucide-react";
import { cn, API_BASE } from "@/lib/utils";
import type { FocusData, AssetState, FocusPart } from "@/lib/types";

// ─── helpers ──────────────────────────────────────────────────────────────────

function stateLabel(state: AssetState, rulDays: number | null): string {
  if (state === "act_now") return "ACT NOW";
  if (state === "act_within")
    return rulDays != null ? `ACT WITHIN ${rulDays} DAYS` : "ACT WITHIN";
  if (state === "watch") return "WATCH";
  return "HEALTHY";
}

function stateHeaderClass(state: AssetState): string {
  return {
    healthy: "verdict-header--healthy",
    watch: "verdict-header--watch",
    act_within: "verdict-header--act-within",
    act_now: "verdict-header--act-now",
  }[state];
}

function stateBadgeClass(state: AssetState): string {
  return {
    healthy: "verdict-badge--healthy",
    watch: "verdict-badge--watch",
    act_within: "verdict-badge--act-within",
    act_now: "verdict-badge--act-now",
  }[state];
}

function stateCardClass(state: AssetState): string {
  return {
    healthy: "verdict-card--healthy",
    watch: "verdict-card--watch",
    act_within: "verdict-card--act-within",
    act_now: "verdict-card--act-now",
  }[state];
}

// ─── stock dot ────────────────────────────────────────────────────────────────

function StockDot({ inStock }: { inStock: boolean | null }) {
  if (inStock === true)
    return <span className="stock-dot stock-dot--in" aria-label="In stock" />;
  if (inStock === false)
    return <span className="stock-dot stock-dot--out" aria-label="Not in stock" />;
  return <span className="stock-dot stock-dot--unknown" aria-label="Stock status unknown" />;
}

// ─── parts table ──────────────────────────────────────────────────────────────

function PartsTable({ parts }: { parts: FocusPart[] }) {
  if (parts.length === 0) return null;
  return (
    <div role="table" aria-label="Parts required for this repair">
      {/* header row */}
      <div
        role="row"
        className="grid text-xs mb-2 pb-1"
        style={{
          gridTemplateColumns: "1fr 130px 120px",
          gap: "8px",
          color: "var(--color-fg-faint)",
          fontWeight: 500,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          fontFamily: "var(--font-sans)",
          borderBottom: "1px solid var(--color-border-subtle)",
        }}
      >
        <span role="columnheader">Part</span>
        <span role="columnheader">Stock</span>
        <span role="columnheader">Lead time</span>
      </div>

      {parts.map((part, i) => (
        <div
          key={`${part.name}-${i}`}
          role="row"
          className="grid items-center py-2"
          style={{
            gridTemplateColumns: "1fr 130px 120px",
            gap: "8px",
            borderTop: i > 0 ? "1px solid var(--color-border-subtle)" : undefined,
          }}
        >
          <span
            role="cell"
            className="text-xs leading-snug"
            style={{ color: "var(--color-fg-primary)" }}
          >
            {part.name}
          </span>

          <span role="cell" className="flex items-center gap-1.5">
            <StockDot inStock={part.in_stock} />
            <span
              className="text-xs"
              style={{
                color:
                  part.in_stock === false
                    ? "var(--color-status-critical-fg)"
                    : "var(--color-fg-secondary)",
              }}
            >
              {part.in_stock === true
                ? "In stock"
                : part.in_stock === false
                ? "Not in stock"
                : "Unknown"}
            </span>
          </span>

          <span
            role="cell"
            className="text-xs"
            style={{ color: "var(--color-fg-faint)" }}
          >
            {part.in_stock === true ? "—" : part.lead_text || "—"}
          </span>
        </div>
      ))}
    </div>
  );
}

// ─── feedback widget ──────────────────────────────────────────────────────────

type FbState = "default" | "confirmed" | "editing" | "submitted";

function FeedbackWidget({ assetId }: { assetId: string }) {
  const [fbState, setFbState] = useState<FbState>("default");
  const [correction, setCorrection] = useState("");
  const [message, setMessage] = useState("");
  const areaId = useId();

  // Auto-reset to default after 3 s on confirmation/submission
  useEffect(() => {
    if (fbState === "confirmed" || fbState === "submitted") {
      const t = setTimeout(() => {
        setFbState("default");
        setMessage("");
        setCorrection("");
      }, 3000);
      return () => clearTimeout(t);
    }
  }, [fbState]);

  async function postFeedback(helpful: boolean, correctionText?: string) {
    try {
      const res = await fetch(`${API_BASE}/api/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          asset_id: assetId,
          helpful,
          correction: correctionText || undefined,
          section: "verdict",
        }),
      });
      const data = await res.json();
      setMessage(
        (data as { message?: string }).message ??
          (helpful
            ? "Got it — thank you. This helps EDITH improve."
            : "Noted — EDITH will factor this in. Thank you.")
      );
    } catch {
      setMessage(
        helpful ? "Got it — thank you." : "Noted — thank you."
      );
    }
  }

  if (fbState === "confirmed" || fbState === "submitted") {
    return (
      <motion.p
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0 }}
        className="text-xs"
        style={{ color: "var(--color-fg-tertiary)" }}
      >
        {message ||
          (fbState === "confirmed"
            ? "Got it — thank you. This helps EDITH improve."
            : "Noted — EDITH will factor this in. Thank you.")}
      </motion.p>
    );
  }

  if (fbState === "editing") {
    return (
      <motion.div
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-2"
      >
        <p className="text-xs font-medium" style={{ color: "var(--color-fg-secondary)" }}>
          What was the actual issue?
        </p>
        <label htmlFor={areaId} className="sr-only">
          Describe the actual issue or correct fix
        </label>
        <textarea
          id={areaId}
          value={correction}
          onChange={(e) => setCorrection(e.target.value)}
          placeholder='e.g. "It was a misalignment, not a bearing fault"'
          rows={2}
          className="w-full resize-none rounded px-3 py-2 text-xs border"
          style={{
            background: "var(--color-bg-elevated)",
            color: "var(--color-fg-primary)",
            borderColor: "var(--color-border)",
            fontFamily: "var(--font-sans)",
            borderRadius: "var(--radius-md)",
          }}
        />
        <div className="flex gap-2">
          <button
            type="button"
            disabled={!correction.trim()}
            onClick={() => {
              postFeedback(false, correction);
              setFbState("submitted");
            }}
            className="btn-secondary"
            style={{ minHeight: "28px", padding: "4px 12px", fontSize: "var(--text-xs)" }}
          >
            Submit
          </button>
          <button
            type="button"
            onClick={() => setFbState("default")}
            className="btn-ghost"
            style={{ minHeight: "28px", padding: "4px 12px", fontSize: "var(--text-xs)" }}
          >
            Cancel
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <span className="text-xs" style={{ color: "var(--color-fg-faint)" }}>
        Was this right?
      </span>
      <button
        type="button"
        onClick={() => {
          postFeedback(true);
          setFbState("confirmed");
        }}
        className="flex items-center gap-1 text-xs font-medium transition-colors hover:opacity-80"
        style={{ color: "var(--color-status-healthy-fg)" }}
      >
        <Check size={11} aria-hidden="true" />
        Yes, correct
      </button>
      <span aria-hidden="true" style={{ color: "var(--color-fg-faint)" }}>|</span>
      <button
        type="button"
        onClick={() => setFbState("editing")}
        className="flex items-center gap-1 text-xs font-medium transition-colors hover:opacity-80"
        style={{ color: "var(--color-fg-tertiary)" }}
      >
        <Edit3 size={11} aria-hidden="true" />
        Edit — it was actually…
      </button>
    </div>
  );
}

// ─── technical details expand ─────────────────────────────────────────────────

function TechnicalDetails({ data }: { data: FocusData }) {
  const [open, setOpen] = useState(false);
  const bodyId = useId();
  const t = data.technical;

  return (
    <div>
      <button
        type="button"
        aria-expanded={open}
        aria-controls={bodyId}
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 text-xs font-medium transition-colors hover:opacity-80"
        style={{ color: "var(--color-fg-faint)" }}
      >
        <motion.span
          animate={{ rotate: open ? 90 : 0 }}
          transition={{ duration: 0.15 }}
          aria-hidden="true"
        >
          <ChevronRight size={13} />
        </motion.span>
        {open ? "Hide technical details" : "Show technical details"}
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={bodyId}
            role="region"
            aria-label="Technical details"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{
              height: { type: "spring", stiffness: 280, damping: 28 },
              opacity: { duration: 0.15 },
            }}
            style={{ overflow: "hidden" }}
          >
            <div
              className="mt-3 p-3 space-y-1.5 text-xs"
              style={{
                background: "var(--color-bg-elevated)",
                border: "1px solid var(--color-border-subtle)",
                borderRadius: "var(--radius-md)",
              }}
            >
              {t.fault_mode && (
                <div className="flex gap-2">
                  <span className="flex-shrink-0" style={{ color: "var(--color-fg-faint)" }}>
                    Fault mode:
                  </span>
                  <span style={{ color: "var(--color-fg-secondary)", fontFamily: "var(--font-mono)" }}>
                    {t.fault_mode}
                  </span>
                </div>
              )}
              {t.rul_cycles != null && (
                <div className="flex gap-2">
                  <span className="flex-shrink-0" style={{ color: "var(--color-fg-faint)" }}>
                    RUL:
                  </span>
                  <span style={{ color: "var(--color-fg-secondary)", fontFamily: "var(--font-mono)" }}>
                    {Math.round(t.rul_cycles)} cycles
                  </span>
                </div>
              )}
              {t.rul_band && (
                <div className="flex gap-2">
                  <span className="flex-shrink-0" style={{ color: "var(--color-fg-faint)" }}>
                    RUL band:
                  </span>
                  <span style={{ color: "var(--color-fg-secondary)", fontFamily: "var(--font-mono)" }}>
                    {t.rul_band}
                  </span>
                </div>
              )}
              {t.anomaly_score != null && (
                <div className="flex gap-2">
                  <span className="flex-shrink-0" style={{ color: "var(--color-fg-faint)" }}>
                    Anomaly score:
                  </span>
                  <span style={{ color: "var(--color-fg-secondary)", fontFamily: "var(--font-mono)" }}>
                    {t.anomaly_score.toFixed(4)}
                  </span>
                </div>
              )}
              {t.fault_codes && t.fault_codes.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  <span className="flex-shrink-0" style={{ color: "var(--color-fg-faint)" }}>
                    Fault codes:
                  </span>
                  <div className="flex gap-1 flex-wrap">
                    {t.fault_codes.map((fc, i) => (
                      <span key={i} className="cite-pill">{fc}</span>
                    ))}
                  </div>
                </div>
              )}
              {t.safety_class && (
                <div className="flex gap-2">
                  <span className="flex-shrink-0" style={{ color: "var(--color-fg-faint)" }}>
                    Safety class:
                  </span>
                  <span style={{ color: "var(--color-fg-secondary)", fontFamily: "var(--font-mono)" }}>
                    {t.safety_class}
                  </span>
                </div>
              )}

              {/* Full step list if >3 steps */}
              {data.all_steps.length > 3 && (
                <div
                  className="pt-2 mt-2"
                  style={{ borderTop: "1px solid var(--color-border-subtle)" }}
                >
                  <p className="mb-1.5" style={{ color: "var(--color-fg-faint)" }}>
                    Full procedure ({data.all_steps.length} steps):
                  </p>
                  <ol className="space-y-1 pl-4 list-decimal">
                    {data.all_steps.map((step, i) => (
                      <li key={i} style={{ color: "var(--color-fg-secondary)" }}>
                        {step}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── skeleton loader ──────────────────────────────────────────────────────────

export function VerdictCardSkeleton() {
  return (
    <div className="verdict-card verdict-card--healthy" aria-busy="true" aria-label="Loading diagnosis">
      <div className="verdict-header verdict-header--healthy">
        <div className="skeleton h-5 w-24 rounded-full mb-3" />
        <div className="skeleton h-4 w-3/4 rounded mb-2" />
        <div className="skeleton h-3 w-2/4 rounded" />
      </div>
      <div className="verdict-body space-y-4">
        <div className="space-y-1.5">
          <div className="skeleton h-3 w-28 rounded" />
          <div className="skeleton h-3 w-full rounded" />
          <div className="skeleton h-3 w-5/6 rounded" />
        </div>
        <div className="space-y-1.5">
          <div className="skeleton h-3 w-24 rounded" />
          <div className="skeleton h-3 w-2/3 rounded" />
        </div>
        <div className="space-y-2">
          <div className="skeleton h-3 w-28 rounded" />
          <div className="skeleton h-3 w-full rounded" />
          <div className="skeleton h-3 w-5/6 rounded" />
          <div className="skeleton h-3 w-3/4 rounded" />
        </div>
      </div>
    </div>
  );
}

// ─── main export ──────────────────────────────────────────────────────────────

interface VerdictCardProps {
  data: FocusData;
  assetId: string;
}

export function VerdictCard({ data, assetId }: VerdictCardProps) {
  const [showAllSteps, setShowAllSteps] = useState(false);
  const [showParts, setShowParts] = useState(false);

  const label = stateLabel(data.state, data.rul_days);
  const partsAlwaysVisible = data.state === "act_now" || data.state === "act_within";
  const visibleSteps = showAllSteps ? data.all_steps : data.what_to_do;

  return (
    <div
      className={cn("verdict-card", stateCardClass(data.state))}
      aria-label={`EDITH assessment: ${label}`}
    >
      {/* ── VERDICT HEADER ─────────────────────────────── */}
      <div className={cn("verdict-header", stateHeaderClass(data.state))}>
        <span
          className={cn("verdict-badge", stateBadgeClass(data.state))}
          aria-label={`Status: ${label}`}
        >
          {label}
        </span>
        <p
          className="mt-2 text-base font-semibold leading-snug"
          style={{ color: "var(--color-fg-primary)" }}
        >
          {data.verdict}
        </p>
        <p
          className="mt-1 text-xs"
          style={{
            color:
              data.state === "act_now"
                ? "var(--color-status-critical-fg)"
                : data.state === "act_within"
                ? "var(--color-status-alarm-fg)"
                : "var(--color-fg-tertiary)",
            fontWeight: data.state === "act_now" ? 600 : 400,
          }}
        >
          {data.state === "healthy" && "All sensors within safe range."}
          {data.state === "watch" && "No immediate action — monitor daily."}
          {data.state === "act_within" && "Parts required — check stock."}
          {data.state === "act_now" && "Critical — cannot wait."}
        </p>
      </div>

      {/* ── CARD BODY ──────────────────────────────────── */}
      <div className="verdict-body space-y-4">

        {/* WHAT'S HAPPENING */}
        <section aria-labelledby={`whats-happening-${assetId}`}>
          <h3
            id={`whats-happening-${assetId}`}
            className="label-caps mb-1.5"
            style={{ color: "var(--color-fg-faint)" }}
          >
            What&apos;s happening
          </h3>
          <p
            className="text-sm leading-relaxed"
            style={{ color: "var(--color-fg-primary)" }}
          >
            {data.whats_happening}
          </p>
        </section>

        {/* HOW URGENT */}
        <section aria-labelledby={`how-urgent-${assetId}`}>
          <h3
            id={`how-urgent-${assetId}`}
            className="label-caps mb-1.5"
            style={{ color: "var(--color-fg-faint)" }}
          >
            How urgent
          </h3>
          <p
            className="text-sm leading-relaxed font-medium"
            style={{
              color:
                data.state === "act_now"
                  ? "var(--color-status-critical-fg)"
                  : data.state === "act_within"
                  ? "var(--color-status-alarm-fg)"
                  : "var(--color-fg-primary)",
            }}
          >
            {data.how_urgent}
          </p>
        </section>

        {/* WHAT TO DO NOW */}
        <section aria-labelledby={`what-to-do-${assetId}`}>
          <h3
            id={`what-to-do-${assetId}`}
            className="label-caps mb-2"
            style={{ color: "var(--color-fg-faint)" }}
          >
            What to do now
          </h3>
          <ol className="space-y-2" aria-label="Recommended steps">
            {visibleSteps.map((step, i) => (
              <li key={i} className="flex gap-3 items-start">
                <span
                  className="flex-shrink-0 font-semibold flex items-center justify-center rounded-full mt-0.5"
                  style={{
                    width: "20px",
                    height: "20px",
                    background: "var(--color-bg-elevated)",
                    color: "var(--color-fg-tertiary)",
                    fontFamily: "var(--font-mono)",
                    fontSize: "10px",
                    minWidth: "20px",
                  }}
                  aria-hidden="true"
                >
                  {i + 1}
                </span>
                <span
                  className="text-sm leading-relaxed flex-1"
                  style={{ color: "var(--color-fg-primary)" }}
                >
                  {step}
                </span>
              </li>
            ))}
          </ol>

          {!showAllSteps && data.more_steps > 0 && (
            <button
              type="button"
              onClick={() => setShowAllSteps(true)}
              className="mt-3 text-xs font-medium transition-colors hover:opacity-80"
              style={{ color: "var(--color-accent-400)" }}
              aria-label={`Show ${data.more_steps} more step${data.more_steps !== 1 ? "s" : ""}`}
            >
              Show {data.more_steps} more {data.more_steps === 1 ? "step" : "steps"} ↓
            </button>
          )}
          {showAllSteps && data.more_steps > 0 && (
            <button
              type="button"
              onClick={() => setShowAllSteps(false)}
              className="mt-3 text-xs font-medium transition-colors hover:opacity-80"
              style={{ color: "var(--color-fg-faint)" }}
            >
              Show fewer steps ↑
            </button>
          )}
        </section>

        {/* PARTS YOU'LL NEED */}
        {data.parts.length > 0 && (
          <section aria-labelledby={`parts-${assetId}`}>
            <div className="flex items-center justify-between mb-2">
              <h3
                id={`parts-${assetId}`}
                className="label-caps"
                style={{ color: "var(--color-fg-faint)" }}
              >
                Parts you&apos;ll need
              </h3>
              {!partsAlwaysVisible && (
                <button
                  type="button"
                  onClick={() => setShowParts((v) => !v)}
                  className="flex items-center gap-1 text-xs transition-colors hover:opacity-80"
                  style={{ color: "var(--color-fg-faint)" }}
                  aria-expanded={showParts}
                  aria-controls={`parts-table-${assetId}`}
                >
                  <motion.span
                    animate={{ rotate: showParts ? 90 : 0 }}
                    transition={{ duration: 0.15 }}
                    aria-hidden="true"
                  >
                    <ChevronRight size={12} />
                  </motion.span>
                  {showParts ? "Hide" : "Show"}
                </button>
              )}
            </div>

            <AnimatePresence initial={false}>
              {(partsAlwaysVisible || showParts) && (
                <motion.div
                  id={`parts-table-${assetId}`}
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{
                    height: { type: "spring", stiffness: 280, damping: 28 },
                    opacity: { duration: 0.15 },
                  }}
                  style={{ overflow: "hidden" }}
                >
                  <PartsTable parts={data.parts} />
                </motion.div>
              )}
            </AnimatePresence>
          </section>
        )}

        {/* IF UNADDRESSED — only renders when downstream data exists */}
        {data.if_unaddressed && (
          <section
            className="p-3 rounded"
            style={{
              background: "oklch(64% 0.23 27 / 0.05)",
              border: "1px solid oklch(64% 0.23 27 / 0.20)",
              borderRadius: "var(--radius-md)",
            }}
            aria-label="Downstream impact if unaddressed"
          >
            <p className="text-sm leading-relaxed" style={{ color: "var(--color-fg-primary)" }}>
              <span
                className="font-semibold"
                style={{ color: "var(--color-status-alarm-fg)" }}
              >
                If unaddressed:{" "}
              </span>
              {data.if_unaddressed}
            </p>
          </section>
        )}

        <div
          style={{ height: "1px", background: "var(--color-border-subtle)" }}
          aria-hidden="true"
        />

        {/* WAS THIS RIGHT? */}
        <FeedbackWidget assetId={assetId} />

        {/* SHOW TECHNICAL DETAILS */}
        <TechnicalDetails data={data} />
      </div>
    </div>
  );
}
