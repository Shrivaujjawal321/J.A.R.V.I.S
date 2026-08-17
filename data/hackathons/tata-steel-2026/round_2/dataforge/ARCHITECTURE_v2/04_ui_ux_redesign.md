# E.D.I.T.H — UI/UX Redesign Spec v2

**Product:** EDITH DataForge — Dataset quality platform for Tata Steel Hackathon  
**Target bar:** Kaggle-level experience — dense leaderboard, clean upload flow, professional dark mode  
**Design system:** EDITH tokens (edith-theme.css / tokens.json) — no deviations  
**Stack:** Next.js 15 App Router, Tailwind v4, shadcn/ui, Framer Motion, Supabase auth  
**Date:** 2026-06-10

---

## 1. Design Direction

- **Brand-first restraint.** The product IS E.D.I.T.H — not "DataAnalizer by EDITH". Single clean wordmark in nav. No AI taglines. Signal confidence through silence.
- **Linear-dense, Kaggle-functional.** Dense leaderboard table (Kaggle's `/datasets` is the reference), search + filter as first-class controls, rank medals visible at a glance. No Notion-airy whitespace.
- **Status-aware surfaces.** Accepted / Processing / Rejected states each have a distinct visual language drawn from the existing semantic color ramp (healthy / warning / critical tokens). Zero ambiguity.
- **Motion aids cognition.** Spring-based card mounts (stiffness 320, damping 28). Score ring draws on mount. No hover-triggered parallax. `prefers-reduced-motion` collapses all to opacity-only fades.
- **Dark-only (EDITH-native).** The design system is intentionally dark-first. `color-scheme: dark` is set globally. No light mode parity needed for v2 (hackathon scope). Placeholder for future light mode via CSS custom property inversion.
- **References:** Kaggle `/datasets` leaderboard, Linear issue list density, Vercel deployment status cards, Stripe Dashboard empty state patterns.

---

## 2. Design Tokens (confirmed — from edith-theme.css + tokens.json)

All tokens are already defined in `/data/design/edith-design-system/`. The sections below document which tokens drive each new pattern introduced in v2. No new tokens are added; only new _usages_ are specified.

```json
{
  "_confirmed_token_usage_v2": {

    "rank_medals": {
      "gold":   "oklch(72% 0.16 85)",
      "silver": "oklch(72% 0.08 250)",
      "bronze": "oklch(60% 0.14 40)",
      "_note": "These are not new tokens — they use existing OKLCH values from the leaderboard component"
    },

    "dataset_status_mapping": {
      "scored":     "color.status.healthy  (green 148)",
      "processing": "color.status.warning  (amber 78)",
      "rejected":   "color.status.critical (red 27)"
    },

    "relevance_bar_fill": {
      "high_relevance":   "color.accent.400  oklch(72% 0.16 213)",
      "medium_relevance": "color.status.warning.fg oklch(78% 0.17 78)",
      "low_relevance":    "color.status.critical.fg oklch(64% 0.23 27)"
    },

    "upload_counter": {
      "plenty":   "color.status.healthy.fg  (3-5 remaining)",
      "low":      "color.status.warning.fg  (1-2 remaining)",
      "exhausted":"color.status.critical.fg (0 remaining)"
    },

    "card_border_left_status": {
      "_note": "Reuse status-tile left-border pattern from design system",
      "scored":     "var(--color-status-healthy-fg)  3px solid",
      "processing": "var(--color-status-warning-fg)  3px solid",
      "rejected":   "var(--color-status-critical-fg) 3px solid"
    }
  },

  "_type_usage_v2": {
    "dataset_name":       "text-base (14px) font-mono font-medium",
    "dataset_description":"text-sm (12px) font-sans color fg-secondary",
    "rank_number":        "text-kpi (28px) font-mono tabular-nums",
    "relevance_score":    "text-xs (11px) font-mono tabular-nums",
    "upload_counter":     "text-xs (11px) font-sans font-medium",
    "tag_pill":           "text-2xs (10px) font-mono uppercase tracking-widest",
    "rejection_headline": "text-xl (20px) font-semibold",
    "rejection_body":     "text-base (14px) font-sans color fg-secondary"
  },

  "_motion_v2": {
    "card_mount": { "stiffness": 320, "damping": 28, "mass": 1, "initial": {"opacity":0,"y":12}, "delay_per_item": 0.04 },
    "rank_badge_pop": { "stiffness": 400, "damping": 22, "initial": {"scale":0.7,"opacity":0}, "delay": 0.15 },
    "rejection_banner_enter": { "stiffness": 380, "damping": 24, "initial": {"opacity":0,"y":-8} },
    "upload_counter_tick": { "type":"spring","stiffness":280,"damping":32 },
    "filter_panel_open": { "duration": 200, "ease":"cubic-bezier(0.16,1,0.3,1)", "initial":{"height":0,"opacity":0} },
    "score_ring_draw": "existing pattern — unchanged",
    "reduced_motion": "all springs collapse to: opacity transition 80ms linear, no y/scale"
  }
}
```

---

## 3. Information Architecture + Page Map

```
E.D.I.T.H
│
├── /                          Home + Upload
│   ├── Nav (sticky, glass)
│   │   ├── [E.D.I.T.H wordmark]
│   │   ├── [Analyze] [Datasets]   ← nav links
│   │   └── [Upload counter pill]  [Avatar / Sign in]
│   │
│   ├── Hero section
│   │   ├── H1: "Know if your data is ready to train on"
│   │   └── UploadZone v2 (no Advanced Section)
│   │
│   ├── How it works (keep, update copy for CSV/XLSX/JSON)
│   └── Recent uploads preview strip (reuse trending row)
│
├── /datasets                  Leaderboard + Browse
│   ├── Nav
│   ├── Page header: "Datasets" + description + [Upload →] CTA
│   ├── Search bar (full-width, prominent)
│   ├── Filter row (horizontal pill filters: All / Accepted / Processing / Rejected | Sort: Rank / Score / Date / Size)
│   ├── Top 3 Podium (medal cards, special treatment for ranks 1-3)
│   ├── Dataset grid (responsive: 1/2/3 col) OR Table toggle
│   │   └── DatasetCard v2 (all states)
│   └── Leaderboard table (Kaggle-style, sortable columns)
│
├── /result                    Dataset Report
│   ├── Nav
│   ├── Back + Improve buttons
│   ├── RelevanceBanner (ACCEPTED green / REJECTED red — always shown at top)
│   ├── [if accepted] ScoreHero + rank badge + quality dimensions + EDITH analysis + improvements + preview
│   └── [if rejected] RejectionDetailScreen (informative guidance)
│
├── /login                     Supabase auth (new)
│   └── E.D.I.T.H logo + email/password or OAuth card
│
└── /board                     REDIRECT → /datasets (301)
```

**Layout system:**  
- Sticky nav: `h-14`, glass backdrop `oklch(8% 0.018 250 / 0.85)` + `backdrop-blur-xl`  
- Content max-width: `max-w-5xl` for datasets/result, `max-w-2xl` for upload hero  
- Page padding: `px-6 py-10` (desktop), `px-4 py-6` (mobile)  
- Responsive breakpoints: `sm` 640px, `md` 768px, `lg` 1024px, `xl` 1280px

---

## 4. Updated Type Definitions

These extend the existing `lib/types.ts`. Add to the file — do not replace.

```typescript
// lib/types.ts — additions for v2

export type DatasetStatus = "processing" | "scored" | "rejected";

// Extend existing DatasetCard interface:
export interface DatasetCard {
  // ── existing fields (keep as-is) ──
  audit_id: string;
  dataset_id: string;
  filename: string;
  composite_score: number;
  grade: string;
  n_rows: number;
  n_cols: number;
  download_count: number;
  created_at: string;

  // ── new v2 fields ──
  rank: number | null;              // null if rejected or still processing
  relevance_score: number | null;   // 0 if rejected; 0-100 if scored
  status: DatasetStatus;            // "processing" | "scored" | "rejected"
  description?: string;             // optional user-provided description
  tags?: string[];                  // backend-inferred or user-set tags
  file_size_bytes?: number;         // shown as "4.2 MB" on card
  rejection_reason?: string;        // human-readable reason for rejection
  uploaded_by?: string;             // user display name (from Supabase auth)
  is_own?: boolean;                 // true if this is the current user's upload
}

// New: extended audit result with relevance verdict
export interface AuditResult {
  // ── existing fields (keep as-is) ──
  audit_id: string;
  dataset_id: string;
  filename: string;
  dataset_type: DatasetType;
  n_rows: number;
  n_cols: number;
  composite_score: number;
  grade: string;
  sub_scores: Record<SubDimension, Sub>;
  readiness: ReadinessInfo | null;
  review: string;
  improvements: Improvement[];
  preview: Preview;

  // ── new v2 fields ──
  status: DatasetStatus;            // "scored" | "rejected"
  rank: number | null;
  relevance_score: number | null;
  rejection_reason?: string;        // populated only when status === "rejected"
  tags?: string[];
  file_size_bytes?: number;
}

// New: upload quota from Supabase
export interface UploadQuota {
  used: number;     // how many datasets this user has uploaded
  max: number;      // always 5
  remaining: number; // max - used
}

// AuditFormData stays the same — label_col/timestamp_col/target_auc ARE removed
// since we're removing the Advanced Section from the UI.
// The backend can still accept them but the UI won't send them.
export interface AuditFormData {
  file: File;
  // Advanced options removed from v2 UI — backend handles auto-detection
}
```

---

## 5. Component Anatomy + State Specs

### 5.1 Nav v2

**File:** `components/ui/nav.tsx`

**Anatomy:**
```
[E.D.I.T.H]  ···  [Analyze] [Datasets]  ···  [3 of 5 ↑]  [Avatar]
```

**States:**

| State | Behavior |
|---|---|
| Unauthenticated | Right slot: "Sign in" ghost button |
| Authenticated, quota available | Right slot: upload counter pill (green/amber) + avatar |
| Authenticated, quota exhausted | Right slot: "Limit reached" red pill + avatar |
| Active nav link | `bg-[var(--color-bg-elevated)]` + `text-fg-primary` |
| Inactive nav link | `text-fg-secondary` hover `text-fg-primary` |

**Keyboard:** Tab order — logo → Analyze → Datasets → upload counter → avatar. All focusable. `aria-current="page"` on active link.

**Change from v1:** Remove "DataAnalizer by EDITH" → replace with single "E.D.I.T.H" wordmark. Monogram changes from "DA" to "E" with accent gradient.

```tsx
// components/ui/nav.tsx — key changes snippet
// Logo: replace "DataAnalizer" with "E.D.I.T.H"
<Link href="/" aria-label="E.D.I.T.H — go to home">
  <div
    className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold font-mono"
    style={{ background: "linear-gradient(135deg, var(--color-accent-500), var(--color-accent-700))" }}
    aria-hidden="true"
  >
    E
  </div>
  <span className="font-semibold text-[var(--color-fg-primary)] text-sm tracking-tight font-mono">
    E.D.I.T.H
  </span>
</Link>

// Upload counter pill (right slot when authenticated)
<UploadCounter quota={quota} />
```

---

### 5.2 UploadCounter Component

**File:** `components/ui/upload-counter.tsx` (NEW)

**Anatomy:**
```
[■■■□□]  3 of 5 uploads remaining
```

**States:**

| Remaining | Color | Badge bg |
|---|---|---|
| 3-5 | `var(--color-status-healthy-fg)` | `healthy-bg` |
| 1-2 | `var(--color-status-warning-fg)` | `warning-bg` |
| 0 | `var(--color-status-critical-fg)` | `critical-bg` |

**ARIA:** `aria-label="3 of 5 dataset uploads remaining"`

```tsx
// components/ui/upload-counter.tsx
"use client";

import { motion } from "framer-motion";
import { useReducedMotion } from "framer-motion";
import type { UploadQuota } from "@/lib/types";

const COLORS = {
  plenty: {
    text: "var(--color-status-healthy-fg)",
    bg:   "var(--color-status-healthy-bg)",
    border: "var(--color-status-healthy-border)",
  },
  low: {
    text: "var(--color-status-warning-fg)",
    bg:   "var(--color-status-warning-bg)",
    border: "var(--color-status-warning-border)",
  },
  exhausted: {
    text: "var(--color-status-critical-fg)",
    bg:   "var(--color-status-critical-bg)",
    border: "var(--color-status-critical-border)",
  },
} as const;

interface UploadCounterProps {
  quota: UploadQuota;
}

export function UploadCounter({ quota }: UploadCounterProps) {
  const prefersReduced = useReducedMotion();
  const tier =
    quota.remaining === 0 ? "exhausted"
    : quota.remaining <= 2 ? "low"
    : "plenty";
  const colors = COLORS[tier];

  const label =
    quota.remaining === 0
      ? "Upload limit reached"
      : `${quota.remaining} of ${quota.max} uploads remaining`;

  return (
    <motion.div
      key={quota.remaining}
      initial={prefersReduced ? false : { scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 280, damping: 32 }}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium"
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
        color: colors.text,
      }}
      aria-label={label}
      title={label}
    >
      {/* Pip row */}
      <div className="flex gap-0.5" aria-hidden="true">
        {Array.from({ length: quota.max }).map((_, i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full transition-colors duration-200"
            style={{
              backgroundColor:
                i < quota.used ? "currentColor" : "currentColor",
              opacity: i < quota.used ? 1 : 0.25,
            }}
          />
        ))}
      </div>
      <span className="tabular-nums font-mono">{quota.remaining}</span>
      <span className="hidden sm:inline">remaining</span>
    </motion.div>
  );
}
```

---

### 5.3 UploadZone v2

**File:** `components/audit/upload-zone.tsx`

**Changes from v1:**
1. Remove the entire "Advanced options" collapsible section (`showOptions` state + `ChevronDown/Up` button + `label_col` / `timestamp_col` / `target_auc` fields)
2. Update `accept` to include `.csv`, `.xlsx`, `.xls`, `.json` — remove `.parquet`
3. Update hint text from "CSV or Parquet" to "CSV, XLSX, or JSON"
4. Add `quota: UploadQuota` prop — when `quota.remaining === 0`, disable the zone + show "You have reached the 5-dataset limit" message instead of the upload CTA
5. Show `<UploadCounter quota={quota} />` inline below the drop zone (or in the button area)

**State matrix:**

| State | Visual |
|---|---|
| Idle, no file | Dashed border `--color-border`, Upload icon, hint text |
| Drag-active | Border `--color-accent-400`, bg `--color-accent-tint`, icon springs up |
| File selected | Solid border `--color-accent-600`, file name + size, clear button |
| Loading | Opacity 60%, spinner in button, "E.D.I.T.H is analyzing…" |
| Quota exhausted | Opacity 50%, `cursor-not-allowed`, banner: "Upload limit reached (5/5)" |
| Error | Red border, error message `aria-live="polite"` |

**Removed:** `AuditFormData.label_col`, `AuditFormData.timestamp_col`, `AuditFormData.target_auc` from the submit call. The interface simplifies to just `{ file: File }`.

```tsx
// components/audit/upload-zone.tsx — critical diff

// REMOVE (entire block, lines 154-227 in current file):
{/* Collapsible options */}
<div className="rounded-xl border border-[var(--color-border-subtle)] overflow-hidden">
  // ... all of showOptions / label-col / timestamp-col / target-auc
</div>

// CHANGE accept types:
const { getRootProps, getInputProps, isDragActive } = useDropzone({
  onDrop,
  accept: {
    "text/csv":                      [".csv"],
    "application/vnd.ms-excel":      [".xls"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "application/json":              [".json"],
  },
  maxFiles: 1,
  disabled: isLoading || props.quota?.remaining === 0,
});

// CHANGE hint text:
<p className="text-[var(--color-fg-secondary)] text-sm mt-1">
  CSV, XLSX, or JSON · up to 500 MB
</p>

// ADD below the dropzone (before the CTA button):
{props.quota && (
  <div className="flex justify-end">
    <UploadCounter quota={props.quota} />
  </div>
)}

// ADD quota-exhausted guard above the CTA button:
{props.quota?.remaining === 0 && (
  <p
    className="text-center text-sm px-4 py-3 rounded-lg border"
    style={{
      color: "var(--color-status-critical-fg)",
      backgroundColor: "var(--color-status-critical-bg)",
      borderColor: "var(--color-status-critical-border)",
    }}
    role="alert"
  >
    You have reached the 5-dataset upload limit for this hackathon.
  </p>
)}

// SIMPLIFIED handleSubmit (no optional fields):
const handleSubmit = () => {
  if (!file || isLoading || props.quota?.remaining === 0) return;
  onSubmit({ file });
};
```

---

### 5.4 DatasetCard v2

**File:** `components/audit/dataset-card.tsx`

**Full anatomy:**
```
┌────────────────────────────────────────────────────┐
│  ┌──────────────────────────────┐  [SCORE RING]    │
│  │ RANK BADGE (1st / 2nd / #N) │                   │
│  └──────────────────────────────┘                   │
│                                                      │
│  [FileSpreadsheet]  dataset_name.csv                │
│                     Description text (1-2 lines)    │
│                                                      │
│  [steel-manufacturing] [time-series] [labeled]      │
│                                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                      │
│  10K rows  ·  24 cols  ·  4.2 MB  ·  Jun 10        │
│                                                      │
│  Relevance  [████████░░] 82                         │
│                                                      │
│  [↓ Download]                              123 DLs  │
└────────────────────────────────────────────────────┘

Rejected state:
┌────────────────────────────────────────────────────┐  ← 3px left border: critical-fg
│  [✕ NOT RELEVANT]               [Relevance: 0]     │
│                                                      │
│  [FileSpreadsheet]  dataset_name.csv                │
│                     ~~Description~~  (dimmed)       │
│                                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                      │
│  10K rows  ·  24 cols  ·  4.2 MB  ·  Jun 10        │
│                                                      │
│  Relevance  [░░░░░░░░░░] 0                          │
│                                                      │
│  [↓ Download] (dimmed, still downloadable)  0 DLs   │
└────────────────────────────────────────────────────┘

Processing state:
┌────────────────────────────────────────────────────┐  ← 3px left border: warning-fg
│  ● ANALYZING...   (pulsing amber dot)               │
│                                                      │
│  [FileSpreadsheet]  dataset_name.csv                │
│                     Scoring in progress             │
│                                                      │
│  [████████░░] analyzing...                          │
└────────────────────────────────────────────────────┘

Skeleton state:
┌────────────────────────────────────────────────────┐
│  ░░░░░░░░░░░░░░░  (shimmer bar, h-4, w-3/4)        │
│  ░░░░░░░░░░░░  (shimmer bar, h-3, w-1/2)           │
│  ░░░░░░░░░░░░░░░░░░░░░░  (h-2, w-full)             │
│  ░░░  ░░░  ░░░  (3 tag stubs)                      │
└────────────────────────────────────────────────────┘
```

**States:**

| State | Left border | Score ring | Download | Opacity |
|---|---|---|---|---|
| `scored` | `status-healthy-fg` | visible | enabled | 1.0 |
| `processing` | `status-warning-fg` | shimmer | disabled | 0.85 |
| `rejected` | `status-critical-fg` | hidden | enabled (dimmed) | 0.75 |
| hover | accent glow box-shadow | — | — | — |
| loading skeleton | none | — | hidden | shimmer animation |

**Keyboard:** `article` element with `tabIndex={0}`. Arrow keys within grid not needed (standard Tab). Download button inside is the only interactive element.

**ARIA:** `aria-label="Dataset: filename, Rank 3, Score 87, Grade B+"` for scored. `aria-label="Dataset: filename — Not relevant to Tata Steel Hackathon"` for rejected.

```tsx
// components/audit/dataset-card.tsx — full v2 rewrite

"use client";

import { useState } from "react";
import { motion, useReducedMotion, AnimatePresence } from "framer-motion";
import { Download, FileSpreadsheet, AlertCircle, Loader2 } from "lucide-react";
import { ScoreRing } from "@/components/ui/score-ring";
import { RankBadge } from "@/components/ui/rank-badge";
import { gradeColor, formatNumber, formatFileSize } from "@/lib/utils";
import { datasetFileUrl } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { DatasetCard } from "@/lib/types";

interface DatasetCardProps {
  dataset: DatasetCard;
  index: number;
}

function RelevanceBar({ score }: { score: number | null }) {
  const s = score ?? 0;
  const fillColor =
    s >= 70 ? "var(--color-accent-400)"
    : s >= 40 ? "var(--color-status-warning-fg)"
    : "var(--color-status-critical-fg)";

  return (
    <div className="flex items-center gap-2">
      <span className="label-caps w-20 flex-shrink-0">Relevance</span>
      <div
        className="flex-1 h-1.5 rounded-full"
        style={{ backgroundColor: "var(--color-bg-elevated)" }}
        role="meter"
        aria-valuenow={s}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Relevance score: ${s} out of 100`}
      >
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: fillColor }}
          initial={{ width: "0%" }}
          animate={{ width: `${s}%` }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
        />
      </div>
      <span
        className="mono-data text-xs tabular-nums w-8 text-right"
        style={{ color: fillColor }}
      >
        {s}
      </span>
    </div>
  );
}

function TagPill({ label }: { label: string }) {
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded"
      style={{
        backgroundColor: "var(--color-bg-elevated)",
        color: "var(--color-fg-tertiary)",
        fontSize: "var(--text-2xs)",
        fontFamily: "var(--font-mono)",
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        border: "1px solid var(--color-border)",
      }}
    >
      {label}
    </span>
  );
}

const STATUS_LEFT_BORDER: Record<string, string> = {
  scored:     "3px solid var(--color-status-healthy-fg)",
  processing: "3px solid var(--color-status-warning-fg)",
  rejected:   "3px solid var(--color-status-critical-fg)",
};

export function DatasetCardItem({ dataset, index }: DatasetCardProps) {
  const prefersReduced = useReducedMotion();
  const [downloadCount, setDownloadCount] = useState(dataset.download_count);
  const [isDownloading, setIsDownloading] = useState(false);

  const isRejected   = dataset.status === "rejected";
  const isProcessing = dataset.status === "processing";
  const isScored     = dataset.status === "scored";

  const cardLabel = isRejected
    ? `Dataset: ${dataset.filename} — Not relevant to Tata Steel Hackathon`
    : `Dataset: ${dataset.filename}${dataset.rank ? `, Rank ${dataset.rank}` : ""}, Score ${dataset.composite_score}, Grade ${dataset.grade}`;

  const handleDownload = () => {
    if (isDownloading || isProcessing) return;
    setIsDownloading(true);
    setDownloadCount((c) => c + 1);
    window.location.href = datasetFileUrl(dataset.audit_id);
    setTimeout(() => setIsDownloading(false), 800);
  };

  return (
    <motion.article
      initial={prefersReduced ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 320, damping: 28, delay: 0.04 * index }}
      whileHover={prefersReduced ? {} : { y: -2 }}
      className={cn(
        "group relative flex flex-col gap-3 rounded-xl p-5",
        "bg-[var(--color-bg-card)] border border-[var(--color-border)]",
        "transition-shadow duration-200",
        "hover:shadow-[var(--shadow-glow-accent)]",
        "focus-within:border-[var(--color-glass-border-accent)]",
        isRejected && "opacity-75",
        isProcessing && "opacity-85"
      )}
      style={{ borderLeft: STATUS_LEFT_BORDER[dataset.status] }}
      aria-label={cardLabel}
      tabIndex={0}
    >
      {/* Status banner row */}
      <div className="flex items-center justify-between gap-2">
        {/* Left: rank badge OR status badge */}
        {isScored && dataset.rank != null ? (
          <RankBadge rank={dataset.rank} />
        ) : isProcessing ? (
          <div className="inline-flex items-center gap-1.5 status-badge status-badge--warning">
            <Loader2 className="w-3 h-3 animate-spin" aria-hidden="true" />
            Analyzing
          </div>
        ) : isRejected ? (
          <div className="inline-flex items-center gap-1.5 status-badge status-badge--critical">
            <AlertCircle className="w-3 h-3" aria-hidden="true" />
            Not Relevant
          </div>
        ) : null}

        {/* Right: score ring (hidden if rejected/processing) */}
        {isScored && (
          <ScoreRing score={dataset.composite_score} size="sm" showGrade />
        )}
      </div>

      {/* File name + description */}
      <div className="flex items-start gap-3">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: "var(--color-bg-elevated)" }}
        >
          <FileSpreadsheet
            className="w-4 h-4"
            style={{ color: isRejected ? "var(--color-status-critical-fg)" : "var(--color-fg-tertiary)" }}
            aria-hidden="true"
          />
        </div>
        <div className="flex-1 min-w-0">
          <p
            className="text-sm font-mono font-medium truncate"
            style={{ color: "var(--color-fg-primary)" }}
          >
            {dataset.filename}
          </p>
          {dataset.description && (
            <p
              className="text-xs mt-0.5 line-clamp-2"
              style={{ color: "var(--color-fg-secondary)" }}
            >
              {dataset.description}
            </p>
          )}
          {isProcessing && !dataset.description && (
            <p className="text-xs mt-0.5" style={{ color: "var(--color-fg-tertiary)" }}>
              Scoring in progress…
            </p>
          )}
        </div>
      </div>

      {/* Tags */}
      {dataset.tags && dataset.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5" aria-label="Dataset tags">
          {dataset.tags.slice(0, 4).map((tag) => (
            <TagPill key={tag} label={tag} />
          ))}
        </div>
      )}

      {/* Divider */}
      <div className="hud-divider my-0" aria-hidden="true" />

      {/* Stats row */}
      <div
        className="flex items-center gap-3 text-xs mono-data tabular-nums"
        style={{ color: "var(--color-fg-tertiary)" }}
      >
        <span>{formatNumber(dataset.n_rows)} rows</span>
        <span aria-hidden="true">·</span>
        <span>{dataset.n_cols} cols</span>
        {dataset.file_size_bytes != null && (
          <>
            <span aria-hidden="true">·</span>
            <span>{formatFileSize(dataset.file_size_bytes)}</span>
          </>
        )}
        <span aria-hidden="true">·</span>
        <time dateTime={dataset.created_at}>
          {new Date(dataset.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
        </time>
      </div>

      {/* Relevance bar */}
      <RelevanceBar score={dataset.relevance_score} />

      {/* Download CTA */}
      <button
        onClick={handleDownload}
        disabled={isDownloading || isProcessing}
        className={cn(
          "btn-ghost w-full flex items-center justify-between",
          (isDownloading || isProcessing) && "opacity-40 cursor-not-allowed"
        )}
        aria-label={`Download ${dataset.filename}`}
        aria-disabled={isDownloading || isProcessing}
      >
        <span className="flex items-center gap-2">
          <Download className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Download</span>
        </span>
        <span className="mono-data tabular-nums text-xs" style={{ color: "var(--color-fg-faint)" }}>
          {formatNumber(downloadCount)} DLs
        </span>
      </button>
    </motion.article>
  );
}
```

---

### 5.5 RankBadge Component

**File:** `components/ui/rank-badge.tsx` (NEW)

```tsx
// components/ui/rank-badge.tsx
"use client";

import { motion, useReducedMotion } from "framer-motion";

const MEDAL_STYLES: Record<number, { text: string; bg: string; border: string; label: string }> = {
  1: {
    text:   "oklch(72% 0.16 85)",
    bg:     "oklch(72% 0.16 85 / 0.12)",
    border: "oklch(72% 0.16 85 / 0.40)",
    label:  "1st place",
  },
  2: {
    text:   "oklch(72% 0.08 250)",
    bg:     "oklch(72% 0.08 250 / 0.12)",
    border: "oklch(72% 0.08 250 / 0.35)",
    label:  "2nd place",
  },
  3: {
    text:   "oklch(60% 0.14 40)",
    bg:     "oklch(60% 0.14 40 / 0.12)",
    border: "oklch(60% 0.14 40 / 0.40)",
    label:  "3rd place",
  },
};

const DEFAULT_STYLE = {
  text:   "var(--color-fg-tertiary)",
  bg:     "var(--color-bg-elevated)",
  border: "var(--color-border)",
};

interface RankBadgeProps {
  rank: number;
  size?: "sm" | "md";
}

export function RankBadge({ rank, size = "sm" }: RankBadgeProps) {
  const prefersReduced = useReducedMotion();
  const style = MEDAL_STYLES[rank] ?? DEFAULT_STYLE;
  const isMedal = rank <= 3;

  return (
    <motion.div
      initial={prefersReduced ? false : { scale: 0.7, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 22, delay: 0.15 }}
      className="inline-flex items-center gap-1 rounded-full border font-mono font-bold tabular-nums"
      style={{
        color: style.text,
        backgroundColor: style.bg,
        borderColor: style.border,
        fontSize: size === "md" ? "var(--text-sm)" : "var(--text-xs)",
        padding: size === "md" ? "4px 10px" : "2px 8px",
        boxShadow: isMedal ? `0 0 10px ${style.border}` : "none",
      }}
      aria-label={style.label ?? `Rank ${rank}`}
    >
      {isMedal && <span aria-hidden="true">{rank === 1 ? "◆" : rank === 2 ? "◇" : "○"}</span>}
      {rank <= 3 ? `${rank}${rank === 1 ? "st" : rank === 2 ? "nd" : "rd"}` : `#${rank}`}
    </motion.div>
  );
}
```

---

### 5.6 RejectedBanner Component

**File:** `components/audit/rejected-banner.tsx` (NEW)

This banner appears at the top of `/result` when `result.status === "rejected"`. It replaces the score hero entirely for rejected datasets.

**States:** Single state — always shown when rejection is true.

**Design intent:** Informative and constructive, not punishing. Amber-to-red gradient left border. Provides guidance on what IS relevant. Never says "wrong" or "invalid" — says "not matched to hackathon scope."

```tsx
// components/audit/rejected-banner.tsx
"use client";

import { motion, useReducedMotion } from "framer-motion";
import { XCircle, ChevronRight } from "lucide-react";
import Link from "next/link";

const RELEVANT_EXAMPLES = [
  "Steel manufacturing sensor streams (blast furnace, rolling mill, caster)",
  "Industrial time-series with operational labels or defect flags",
  "Condition monitoring data (vibration, temperature, pressure readings)",
  "Quality defect datasets from steel production processes",
  "Predictive maintenance event logs from heavy industrial equipment",
];

interface RejectedBannerProps {
  filename: string;
  reason?: string;
}

export function RejectedBanner({ filename, reason }: RejectedBannerProps) {
  const prefersReduced = useReducedMotion();

  return (
    <motion.div
      initial={prefersReduced ? false : { opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 380, damping: 24 }}
      className="rounded-xl overflow-hidden"
      style={{
        background: "var(--color-status-critical-bg)",
        border: "1px solid var(--color-status-critical-border)",
        borderLeft: "4px solid var(--color-status-critical-fg)",
      }}
      role="alert"
      aria-labelledby="rejection-heading"
    >
      <div className="p-6 flex flex-col gap-5">
        {/* Header */}
        <div className="flex items-start gap-3">
          <XCircle
            className="w-6 h-6 flex-shrink-0 mt-0.5"
            style={{ color: "var(--color-status-critical-fg)" }}
            aria-hidden="true"
          />
          <div className="flex flex-col gap-1">
            <h2
              id="rejection-heading"
              className="text-xl font-semibold"
              style={{ color: "var(--color-fg-primary)" }}
            >
              Dataset not matched to hackathon scope
            </h2>
            <p className="text-sm" style={{ color: "var(--color-fg-secondary)" }}>
              <span className="font-mono">{filename}</span> —&nbsp;
              {reason ?? "Dataset is not relevant to the Tata Steel Hackathon. Relevance Score: 0."}
            </p>
          </div>
        </div>

        {/* Divider */}
        <div className="hud-divider" aria-hidden="true" />

        {/* What IS relevant */}
        <div className="flex flex-col gap-3">
          <p
            className="label-caps"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            What qualifies for this hackathon
          </p>
          <ul className="flex flex-col gap-2" aria-label="Accepted dataset types">
            {RELEVANT_EXAMPLES.map((example) => (
              <li
                key={example}
                className="flex items-start gap-2 text-sm"
                style={{ color: "var(--color-fg-secondary)" }}
              >
                <ChevronRight
                  className="w-4 h-4 flex-shrink-0 mt-0.5"
                  style={{ color: "var(--color-accent-400)" }}
                  aria-hidden="true"
                />
                {example}
              </li>
            ))}
          </ul>
        </div>

        {/* CTA */}
        <div className="flex gap-3 flex-wrap">
          <Link
            href="/"
            className="btn-primary"
          >
            Try a different dataset
          </Link>
          <Link
            href="/datasets"
            className="btn-secondary"
          >
            Browse accepted datasets
          </Link>
        </div>
      </div>
    </motion.div>
  );
}
```

---

### 5.7 Dashboard Page v2 (/datasets)

**File:** `app/datasets/page.tsx`

**Layout anatomy:**
```
/datasets
│
├── Page header
│   ├── H1: "Datasets"
│   ├── Subtitle: "Graded and ranked by quality score + Tata Steel relevance"
│   └── [Upload →] CTA button (links to /)
│
├── Search + Filter row
│   ├── [🔍 Search datasets…]           (full-width input on mobile, 60% on desktop)
│   └── Filter pills: [All ✓] [Accepted] [Processing] [Rejected] | Sort: [Rank ▼] [Score] [Date] [Size]
│
├── Top 3 Podium (only shown when 3+ accepted datasets exist)
│   ├── Card #2 (silver) — slightly shorter
│   ├── Card #1 (gold)   — tallest, center, glow-accent box-shadow
│   └── Card #3 (bronze) — slightly shorter
│
├── "All datasets" section heading + count
│   └── [Grid ⊞] [Table ≡] toggle (right aligned)
│
├── Grid view (default) OR Table view
│   ├── Grid: 1 col → 2 col (sm) → 3 col (lg), DatasetCard v2
│   └── Table: the existing LeaderboardRow component (enhanced with rank + relevance col)
│
└── Empty states (per filter)
```

**Search behavior:** Client-side filter on `filename` + `description` + `tags` (case-insensitive). Debounce 200ms. No server round-trip for v2.

**Filter pills:** Radix `ToggleGroup` single-select. Active state uses `btn-primary` token. Inactive uses `btn-ghost`.

**Sort behavior:**
- Rank: ascending (1 = best)
- Score: descending
- Date: descending (newest first)
- Size: descending (largest first)

**Empty state variants:**

```
No datasets at all:
  [upload icon]
  "No datasets yet"
  "Be the first to upload one for the hackathon."
  [Upload dataset →]

No results for search:
  [search icon]
  "No datasets match '${query}'"
  "Try different keywords or clear the search."
  [Clear search ×]

No accepted datasets (filtered):
  "No accepted datasets yet"

No rejected datasets (filtered):
  "No rejected datasets" (positive — this is good news)
```

**Responsive grid:**
- `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`
- On table view: full-width, horizontally scrollable at < 640px

**Pagination / lazy loading:** Virtual scroll not needed for v2 (hackathon has bounded dataset count). If list > 50, add `Show more` button (load 12 at a time). TanStack Query `keepPreviousData` for smooth transitions.

```tsx
// app/datasets/page.tsx — v2 additions (key new elements)

// Search + Filter controls
function SearchFilterBar({
  query, setQuery, statusFilter, setStatusFilter, sort, setSort
}: SearchFilterBarProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-3" role="search">
      {/* Search input */}
      <div className="relative flex-1">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
          style={{ color: "var(--color-fg-tertiary)" }}
          aria-hidden="true"
        />
        <input
          type="search"
          placeholder="Search datasets…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 rounded-lg text-sm font-sans
                     bg-[var(--color-bg-card)] border border-[var(--color-border)]
                     text-[var(--color-fg-primary)] placeholder:text-[var(--color-fg-faint)]
                     focus:outline-none focus-visible:border-[var(--color-accent-400)]
                     transition-colors duration-150"
          aria-label="Search datasets by name, description, or tag"
        />
      </div>

      {/* Status filter pills */}
      <div className="flex gap-1.5 flex-wrap" role="group" aria-label="Filter by status">
        {(["all", "scored", "processing", "rejected"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={cn(
              "px-3.5 py-2 rounded-lg text-xs font-medium capitalize transition-colors duration-100",
              "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]",
              statusFilter === s
                ? "bg-[var(--color-accent-400)] text-[var(--color-fg-on-accent)]"
                : "btn-ghost text-xs"
            )}
            aria-pressed={statusFilter === s}
          >
            {s === "all" ? "All" : s}
          </button>
        ))}
      </div>

      {/* Sort dropdown */}
      <select
        value={sort}
        onChange={(e) => setSort(e.target.value as SortKey)}
        className="px-3 py-2.5 rounded-lg text-xs font-mono
                   bg-[var(--color-bg-card)] border border-[var(--color-border)]
                   text-[var(--color-fg-secondary)]
                   focus:outline-none focus-visible:border-[var(--color-accent-400)]"
        aria-label="Sort datasets by"
      >
        <option value="rank">Sort: Rank</option>
        <option value="score">Sort: Score</option>
        <option value="date">Sort: Date</option>
        <option value="size">Sort: Size</option>
      </select>
    </div>
  );
}
```

**Leaderboard table v2 — add Rank + Relevance columns:**

```tsx
// Updated column headers array in LeaderboardRow parent:
const COLS = ["#", "Name", "Relevance", "Score", "Grade", "Rows", "Size", "Uploaded"];

// Additional cells in LeaderboardRow:
<td className="px-5 py-4">
  <RelevanceBar score={dataset.relevance_score} />
</td>
<td className="px-5 py-4 font-mono tabular-nums text-sm text-[var(--color-fg-faint)]">
  {dataset.file_size_bytes != null ? formatFileSize(dataset.file_size_bytes) : "—"}
</td>
<td className="px-5 py-4 text-xs text-[var(--color-fg-faint)]">
  <time dateTime={dataset.created_at}>
    {new Date(dataset.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
  </time>
</td>
```

---

### 5.8 Result Page v2 (/result)

**File:** `app/result/page.tsx`

**Changes:**
1. Add `RejectedBanner` as first section — conditional on `result.status === "rejected"`
2. When rejected: do NOT render ScoreHero, SubScores, ImprovementCards (no meaningful data)
3. When rejected: still render a minimal DataPreview so user can see what was in their file
4. Add `RankBadge` alongside the grade in ScoreHero (for scored datasets with a rank)
5. Add relevance score display in the score hero area

**Conditional rendering tree:**
```tsx
// app/result/page.tsx — structural changes
{result.status === "rejected" ? (
  <>
    <RejectedBanner filename={result.filename} reason={result.rejection_reason} />
    <section aria-labelledby="preview-heading">
      <DataPreview preview={result.preview} />
    </section>
  </>
) : (
  <>
    {/* Accepted — existing score hero + quality dimensions etc. */}
    <RelevanceAcceptedBadge score={result.relevance_score} rank={result.rank} />
    <ScoreHeroSection ... />
    <SubScores ... />
    <EdithReview ... />
    <ImprovementCards ... />
    <DataPreview ... />
  </>
)}
```

**RelevanceAcceptedBadge (inline, above score hero):**
```tsx
// Inline component — no separate file needed
function RelevanceAcceptedBadge({ score, rank }: { score: number | null; rank: number | null }) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      <div className="inline-flex items-center gap-2 status-badge status-badge--healthy">
        <span className="status-dot status-dot--healthy" aria-hidden="true" />
        Accepted — Relevant to Tata Steel
      </div>
      {rank != null && <RankBadge rank={rank} size="md" />}
      {score != null && (
        <span
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono border"
          style={{
            color: "var(--color-accent-400)",
            backgroundColor: "var(--color-accent-tint)",
            borderColor: "oklch(72% 0.16 213 / 0.30)",
          }}
        >
          Relevance {score}/100
        </span>
      )}
    </div>
  );
}
```

---

### 5.9 Upload Flow — Full State Machine

```
User lands on / (unauthenticated)
  └── UploadZone shown but CTA says "Sign in to upload"
      └── Click → /login → Supabase auth → redirect back to /

User lands on / (authenticated, quota > 0)
  └── UploadZone: idle state
      ├── [Drop file or click]
      │   └── File selected state (name + size shown, clear button)
      │       └── [Analyze with E.D.I.T.H]
      │           └── Loading state (spinner + "E.D.I.T.H is analyzing…")
      │               ├── [SUCCESS, status=scored]   → router.push("/result") with AuditResult
      │               ├── [SUCCESS, status=rejected] → router.push("/result") with rejection data
      │               └── [ERROR] → inline error message aria-live="polite"
      └── [Drag file]
          └── Drag-active state → same as above

User lands on / (authenticated, quota === 0)
  └── UploadZone: disabled, quota-exhausted banner shown
      └── "You have reached the 5-dataset upload limit"
          └── CTA: [Browse datasets →] links to /datasets
```

---

## 6. Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| `< 640px` (mobile) | Single column grid. Filter pills wrap. Table scrolls horizontally. Nav: hide "Datasets" label, show icon only if needed. |
| `640-1024px` (tablet) | 2-col grid. Filter pills in scrollable row. |
| `>= 1024px` (desktop) | 3-col grid. Podium visible. Full table. |

**Nav on mobile:** Keep E.D.I.T.H wordmark + both links + upload counter (counter abbreviates to just the number on mobile). Avatar always shown.

---

## 7. A11y Annotations (WCAG 2.2 AA)

| Rule | Implementation |
|---|---|
| Color not sole indicator | Status conveyed by badge text + border + color. Relevance bar has numeric value. Rank badge has ordinal text. |
| Focus visible | Global `:focus-visible` ring from edith-theme: `1.5px solid var(--color-accent-400)` with `2px offset`. All interactive elements tabbable. |
| Target size ≥ 24px | All buttons use `min-height: 36px` (`.btn-primary`, `.btn-secondary`, `.btn-ghost`). Download button on card: `py-2.5` = 40px touch target. Tag pills: `min-height: 24px`. |
| Form labels | Search input has `aria-label`. Sort select has `aria-label`. Filter buttons use `aria-pressed`. Upload zone has `aria-label` on the dropzone div. |
| Drag alternative | react-dropzone provides both drag AND click-to-browse. WCAG 2.5.7 satisfied. |
| Live regions | Error messages on upload: `role="alert"` + `aria-live="polite"`. Processing status: `aria-live="polite"` on the status section. |
| Skip link | Add `<a href="#main-content" className="sr-only focus:not-sr-only">Skip to main content</a>` in layout.tsx. |
| Screen reader narrative | Result page: `<h1 id="result-heading" className="sr-only">Audit result for {filename}</h1>`. RejectedBanner: `aria-labelledby="rejection-heading"`. |
| Reduced motion | All `motion.*` components use `useReducedMotion()`. When true: `initial={false}`, no spring, opacity-only `duration: 80ms`. Score ring draw animation: skips to final state. |
| Color contrast | Accent 400 on bg-base: ~6.1:1. Status fg tokens on bg-card: all verified in edith-theme comments (healthy 5.1:1, warning 6.2:1, critical 4.5:1). All pass AA. |
| Heading hierarchy | H1 (page) → H2 (section) → H3 (subsection). Result page sections use `aria-labelledby` pointing to H2s. |
| `<time>` element | All dates use `<time dateTime={iso}>`. |
| Table | Leaderboard uses `<table>` with `<th scope="col">`. `aria-label` on the table element. |
| Icon-only buttons | The "clear file" button in UploadZone has `aria-label="Remove selected file"`. Download button: `aria-label="Download {filename}"`. |

---

## 8. Motion Spec (per component)

| Component | Enter | Exit | Reduced-motion |
|---|---|---|---|
| DatasetCard mount | `y: 12→0`, `opacity: 0→1`, spring `{320,28}`, stagger `0.04s * index` | — | opacity only |
| RankBadge pop | `scale: 0.7→1`, `opacity: 0→1`, spring `{400,22}`, `delay: 0.15s` | — | opacity only |
| RejectedBanner enter | `y: -8→0`, `opacity: 0→1`, spring `{380,24}` | — | opacity only |
| RelevanceBar fill | `width: 0→${score}%`, `duration: 0.8s`, ease `[0.16,1,0.3,1]`, `delay: 0.2s` | — | instant |
| UploadCounter tick (quota changes) | `scale: 0.9→1`, `opacity: 0→1`, spring `{280,32}` | — | opacity only |
| Filter panel open | `height: 0→auto`, `opacity: 0→1`, `duration: 200ms`, `ease-out` | same reversed | instant |
| Search input focus | border-color transition `120ms` via CSS only | — | — |
| Card hover lift | `y: 0→-2`, spring `{300,30}` (via `whileHover`) | `y: -2→0` | disabled |
| Score ring draw | existing pattern (stroke-dashoffset) — unchanged | — | skips to final |
| Page route transition | None for v2 (View Transitions API can be added later as enhancement) | — | — |

**Motion intent rationale:** Every animation here aids cognition — staggered card mounts let the eye parse the list sequentially. RankBadge pop draws attention to rank (the most important data point). Relevance bar fill gives visual weight to the score meaning. No decorative animations.

---

## 9. Component Inventory + Change List (Build Checklist)

### Files to EDIT

| File | Change | Priority |
|---|---|---|
| `web/lib/types.ts` | Add `DatasetStatus`, extend `DatasetCard` with rank/relevance_score/status/tags/description/file_size_bytes/rejection_reason/is_own, extend `AuditResult` with status/rank/relevance_score/rejection_reason/tags/file_size_bytes, add `UploadQuota`, simplify `AuditFormData` to `{ file: File }` | P0 |
| `web/lib/api.ts` | Update `runAudit` to not send `label_col`/`timestamp_col`/`target_auc`. Add `fetchQuota(): Promise<UploadQuota>` call to `/api/quota`. Update `fetchDatasets` to expect new `DatasetCard` fields. | P0 |
| `web/components/ui/nav.tsx` | Rebrand "DataAnalizer" → "E.D.I.T.H". Monogram "DA" → "E". Remove `"by EDITH"` span. Add `<UploadCounter>` in right slot (conditional on auth). Add `aria-label="E.D.I.T.H — go to home"`. | P0 |
| `web/components/audit/upload-zone.tsx` | Remove entire Advanced Section (collapsible div + all 3 inputs + ChevronDown/Up + showOptions state). Update `accept` for CSV/XLSX/JSON. Add `quota: UploadQuota` prop. Add exhausted guard. Update hint text. Simplify `handleSubmit`. | P0 |
| `web/app/page.tsx` | Remove eyebrow badge (`"Powered by EDITH — AI Dataset Intelligence"`). Update "How it works" step 1 copy ("CSV, XLSX, or JSON" not "CSV or Parquet"). Pass `quota` prop to `<UploadZone>`. | P0 |
| `web/app/result/page.tsx` | Add `RejectedBanner` at top (conditional on `result.status === "rejected"`). Add `RelevanceAcceptedBadge` for accepted. Add `RankBadge` in score hero area. Conditional render: skip ScoreHero/SubScores/ImprovementCards for rejected. | P0 |
| `web/app/datasets/page.tsx` | Add `SearchFilterBar` component above top-ranked section. Add grid/table toggle. Add sort controls. Leaderboard table: add Rank, Relevance, Size columns. Empty state variants. Pass `dataset.rank` to `DatasetCardItem`. | P1 |
| `web/components/audit/dataset-card.tsx` | Full rewrite per spec §5.4. Add status left border, RankBadge, description, tags, RelevanceBar, file size, upload date, status-conditional rendering. | P0 |
| `web/app/layout.tsx` | Add skip-to-content link (`<a href="#main-content" className="sr-only focus:not-sr-only">`). Add `id="main-content"` to main wrapper. | P1 |

### Files to CREATE (New)

| File | Purpose | Priority |
|---|---|---|
| `web/components/ui/rank-badge.tsx` | Gold/silver/bronze + numbered rank badge component | P0 |
| `web/components/ui/upload-counter.tsx` | Upload quota pip display for nav + upload zone | P0 |
| `web/components/audit/rejected-banner.tsx` | Full rejection screen with guidance | P0 |
| `web/app/login/page.tsx` | Supabase auth page (email + password or OAuth). Returns to previous route on success. | P1 |

### Files to DELETE / Redirect

| File | Action |
|---|---|
| `web/app/board/page.tsx` | Replace content with: `redirect("/datasets")` (Next.js 15 static redirect). The old board UI had zero polish and duplicates /datasets. |

### Files to LEAVE UNCHANGED

| File | Reason |
|---|---|
| `web/components/audit/score-hero.tsx` | Good as-is; accepts enhancements via parent, no internal changes needed |
| `web/components/audit/sub-scores.tsx` | Good as-is |
| `web/components/audit/edith-review.tsx` | Good as-is |
| `web/components/audit/improvement-cards.tsx` | Good as-is |
| `web/components/audit/data-preview.tsx` | Good as-is |
| `web/components/ui/score-ring.tsx` | Good as-is |
| `web/components/ui/skeleton.tsx` | Good as-is |
| `web/lib/utils.ts` | Add `formatFileSize` if not present; rest unchanged |

---

## 10. Open Questions for Engineering

1. **Backend rejection response shape:** The spec assumes `AuditResult.status === "rejected"` comes from the API. Does the `/api/audit` endpoint currently return a `status` field? If not, engineer needs to add it (plus `rejection_reason`, `relevance_score`, `rank` to the audit response). The API contract must match the extended `AuditResult` type.

2. **`/api/quota` endpoint:** Does this endpoint exist? Needs to return `{ used, max, remaining }` for the current authenticated user. Depends on Supabase auth being wired into the API backend.

3. **Supabase auth integration on frontend:** Is `@supabase/ssr` installed? Does the app have a `supabase/` client helper already, or does `/app/login/page.tsx` need to set this up from scratch? The design assumes `useSession()` or equivalent.

4. **`rank` computation:** Is rank computed server-side and returned on each `DatasetCard` + `AuditResult`, or does the frontend compute it from the sorted list? Server-side is preferred (rank changes when new datasets are uploaded by others). Confirm API returns `rank` on `/api/datasets` response.

5. **`file_size_bytes` on card:** Is this stored in the database and returned on the `/api/datasets` list endpoint? Currently `DatasetCard` doesn't include it. If backend doesn't store it, frontend can omit the size display without breaking anything (the field is typed as `optional`).

6. **`description` and `tags`:** Are these user-provided at upload time (requiring a UI form field) or backend-inferred from the dataset content? If user-provided, we need an optional description field in the UploadZone (single text input, NOT part of the removed Advanced Section). If backend-inferred, no UI change needed.

7. **Authentication gate on upload:** The spec gates upload behind auth. Is this already enforced server-side? The frontend will check auth and show "Sign in to upload" but the real gate is the API returning 401 for unauthenticated upload requests.

8. **`formatFileSize` utility:** The function is used in `upload-zone.tsx` (exists) but not exported from `utils.ts` for `dataset-card.tsx`. Engineer needs to ensure it is exported from `lib/utils.ts`.

9. **`/board` redirect:** Confirm it is safe to replace `/board` with a redirect — are there any existing links or external references to `dataforge-delta.vercel.app/board`?

---

## Summary

**E.D.I.T.H v2** redesigns the DataForge frontend around three pillars:

1. **Brand clarity.** "DataAnalizer by EDITH" → single "E.D.I.T.H" wordmark. Zero AI taglines. Zero Advanced Section.  
2. **Kaggle-grade dataset experience.** Dense leaderboard + search/filter/sort + medal podium for top 3 + all-state dataset cards (scored / processing / rejected) with rank, tags, relevance bar, size, date.  
3. **Rejection UX that guides, not punishes.** Rejected datasets get a constructive banner explaining exactly what qualifies, with a CTA to try again — no dead ends.

All changes stay within the existing EDITH token system (OKLCH surfaces, accent hue 213, status semantic ramp). No new dependencies needed beyond what is already installed.
