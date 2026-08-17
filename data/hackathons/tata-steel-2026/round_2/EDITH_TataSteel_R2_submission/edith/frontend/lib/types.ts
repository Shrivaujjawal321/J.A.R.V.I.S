// ─── Backend API types ────────────────────────────────────────────────────

export type HealthStatus = "normal" | "warning" | "alarm";
export type StatusBand = "healthy" | "warning" | "alarm" | "critical" | "unknown" | "offline";

/** Four guided states returned by /api/focus */
export type AssetState = "healthy" | "watch" | "act_within" | "act_now";

/** Maps backend health strings to StatusBand */
export function toStatusBand(health: HealthStatus | string): StatusBand {
  if (health === "normal") return "healthy";
  if (health === "warning") return "warning";
  if (health === "alarm") return "alarm";
  return "unknown";
}

/** Maps AssetState to StatusBand for compact badges */
export function stateToStatusBand(state: AssetState): StatusBand {
  if (state === "healthy") return "healthy";
  if (state === "watch") return "warning";
  if (state === "act_within") return "alarm";
  return "critical"; // act_now
}

// GET /api/assets
export interface AssetSummary {
  asset_id: string;
  equipment_class: string;
  description: string;
  criticality: string;
  process_stage: string;
  health: HealthStatus;
  n_sensors: number;
  /** Plain-language one-liner from backend (e.g. "All sensors normal — running healthy.") */
  headline?: string;
  /** Tag of the sensor most out of range, if any */
  worst_sensor?: string | null;
}

// GET /api/focus/{asset_id}
export interface FocusPart {
  part_id?: string;
  name: string;
  in_stock: boolean | null;
  lead_text: string;
}

export interface FocusChip {
  label: string;
  why: string;
}

export interface FocusTechnical {
  fault_mode: string | null;
  rul_cycles: number | null;
  rul_band: string | null;
  anomaly_score: number | null;
  fault_codes: string[];
  safety_class: string | null;
}

export interface FocusData {
  asset_id: string;
  name: string;
  health: HealthStatus;
  state: AssetState;
  /** One-line plain-language verdict */
  verdict: string;
  whats_happening: string;
  how_urgent: string;
  /** First 3 steps shown by default */
  what_to_do: string[];
  /** Count of additional steps beyond what_to_do */
  more_steps: number;
  /** All steps including what_to_do */
  all_steps: string[];
  parts: FocusPart[];
  /** Only present when downstream impact data exists — null otherwise */
  if_unaddressed: string | null;
  rul_days: number | null;
  chips: FocusChip[];
  technical: FocusTechnical;
}

// GET /api/bottleneck
export interface BottleneckItem {
  order: number;
  asset_id: string;
  health: HealthStatus;
  headline?: string;
  description?: string;
  why: string[];
  safety_class: string | null;
  gold_rank?: number;
  priority_score?: number;
}

export interface BottleneckData {
  count: number;
  items: BottleneckItem[];
}

// POST /api/feedback
export interface FeedbackRequest {
  asset_id: string;
  query?: string;
  helpful: boolean;
  correction?: string;
  section?: string;
}

export interface FeedbackResponse {
  ok: boolean;
  message: string;
}

// GET /api/asset/{id}
export interface SensorMeta {
  tag: string;
  /** Full readable name from backend, e.g. "Bearing temperature (drive end)" */
  label?: string;
  quantity: string;
  unit: string;
  normal: [number, number] | null;
  warning: number | null;
  alarm: number | null;
  direction: "upper" | "lower";
}

export interface Scenario {
  scenario_id: string;
  failure_mode: string;
  label: string;
  safety_class: string;
}

export interface AssetDetail {
  asset_id: string;
  equipment_class: string;
  description: string;
  criticality: string;
  process_stage: string;
  sensors: SensorMeta[];
  scenarios: Scenario[];
}

// SSE events
export interface MetaEvent {
  type: "meta";
  asset_id: string;
  description: string;
  sensors: SensorMeta[];
  rows: number;
}

export interface TickEvent {
  type: "tick";
  ts: string | number;
  row: number;
  values: Record<string, number | null>;
  status: Record<string, HealthStatus>;
  worst: HealthStatus;
  fault_label: string | null;
}

export interface AlertEvent {
  type: "alert";
  ts: string | number;
  asset_id: string;
  sensor: string;
  quantity: string;
  unit: string;
  value: number;
  threshold: number;
  severity: "WARNING" | "ALARM";
  row: number;
  reason: string;
}

export interface FindingEntry {
  title: string;
  brief: string;
  detail: string;
  sources: string[];
}

// Ordered, judge-format PS output section (Diagnosis / Root Cause / RUL / Risk / Actions)
export interface PSSection {
  key: string;
  title: string;
  brief: string;
  detail: string;
  sources: string[];
}

export interface DiagnosisEvent {
  type?: "diagnosis";
  answer: string;
  risk_band: string;
  rul: number | null;
  rul_days?: number | null;
  confidence: number;
  sources: string[];
  findings: Record<string, FindingEntry>;
  sections?: PSSection[];
}

export interface EndEvent {
  type: "end";
  rows: number;
}

export type SSEEvent = MetaEvent | TickEvent | AlertEvent | DiagnosisEvent | EndEvent;

// GET /api/predict/{id}
export interface PredictResult {
  fault: Record<string, unknown>;
  anomaly: Record<string, unknown>;
  rul: Record<string, unknown>;
}

// POST /api/ask — reasoning trace (J4 + DIFF-04 + G7)
/** One step in EDITH's multi-agent reasoning chain */
export interface TraceStep {
  step: number;
  kind: "plan" | "tool" | "ml" | "rag" | "synthesis" | "llm" | string;
  thought: string;
  action: string;
  result_summary: string;
  sources: string[];
  latency_ms: number;
  detail: Record<string, unknown>;
  rung: string | null;
}

/** Full reasoning trace returned in every /api/ask response */
export interface ReasoningTrace {
  query: string;
  step_count: number;
  total_latency_ms: number;
  sources: string[];
  steps: TraceStep[];
}

// POST /api/ask
export interface AskResponse {
  answer: string;
  intent: string;
  asset_id: string | null;
  risk_band: string;
  rul: number | null;
  rul_days?: number | null;
  confidence: number | string;
  faithfulness: number;
  sources: string[];
  findings: Record<string, FindingEntry>;
  sections?: PSSection[];
  trace?: ReasoningTrace | null;
  /** J11 / DIFF-08: reasoning mode label — "fast grounded" | "edith-deep (cached)" | "edith-deep (live)" */
  reasoning_mode?: string | null;
  /** J11 / DIFF-08: human-readable confidence label */
  confidence_label?: string | null;
}

// GET /api/logbook?asset_id={id}&limit=20  (G9-frontend)
export type LogbookEntryType = "alert" | "diagnosis" | "report" | "feedback" | string;

export interface LogbookEntry {
  ts: string | number;
  asset_id: string;
  entry_type: LogbookEntryType;
  title: string;
  summary: string;
  ref_id?: string | null;
}

// POST /api/report
export interface ReportRequest {
  asset_id: string;
  scenario_id?: string;
  kind: "incident" | "decision";
}

export interface ReportResponse {
  report_id: string;
  report: ReportData;
}

export interface ReportData {
  report_id?: string;
  asset_id?: string;
  generated_at?: string;
  kind?: string;
  summary?: string;
  diagnosis?: FindingEntry | string;
  rca?: FindingEntry | string;
  predictor?: FindingEntry | string;
  prioritizer?: FindingEntry | string;
  recommender?: FindingEntry | string;
  risk_band?: string;
  rul?: number | null;
  confidence?: number;
  sources?: string[];
  findings?: Record<string, FindingEntry>;
  sensor_data?: unknown;
  [key: string]: unknown;
}
