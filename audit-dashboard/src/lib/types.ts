// Mirrors jarvis_core/audit_agent/models.py exactly

export type AuditState =
  | "scope_gate"
  | "recon"
  | "scan_running"
  | "analyze"
  | "verify"
  | "human_approval_pending"
  | "report_generating"
  | "done"
  | "scope_denied"
  | "cancelled";

export type Severity = "critical" | "high" | "medium" | "low" | "info";

export type VerificationStatus =
  | "unverified"
  | "confirmed"
  | "false_positive"
  | "needs_manual";

export type OWASPCategory =
  | "A01:2025-BAC"
  | "A02:2025-Misconfig"
  | "A03:2025-SupplyChain"
  | "A04:2025-CryptoFail"
  | "A05:2025-Injection"
  | "SECRETS"
  | "SCA:CVE"
  | "UNKNOWN";

export interface Finding {
  id: string;
  scanner: string;
  rule_id: string;
  cwe: string | null;
  owasp_category: OWASPCategory | null;
  cvss_vector: string | null;
  cvss_score: number | null;
  severity: Severity;
  file_path: string | null;
  line_start: number | null;
  line_end: number | null;
  endpoint: string | null;
  evidence: string;
  verification_status: VerificationStatus;
  confidence: number;
  dedupe_key: string;
  remediation: string | null;
  verification_reason: string | null;
  related_finding_ids: string[];
  scanners_agreeing: string[];
  is_actionable: boolean;
}

export interface AuditRunView {
  audit_id: string;
  audit_state: AuditState;
  target_uri: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  progress_pct: number;
  total_findings: number;
  cost_usd_total: number;
  error: string | null;
}

export interface FindingsPage {
  items: Finding[];
  next_cursor: string | null;
  total: number;
}

export interface AuditReport {
  audit_id: string;
  generated_at: string;
  target_uri: string;
  total_findings: number;
  by_severity: Record<string, number>;
  top_findings: Finding[];
  markdown_body: string;
  json_findings: Finding[];
  cvss_distribution: Record<string, number>;
}

export interface AuditRequest {
  user_id?: string;
  target_uri: string;
  target_kind?: "git_repo" | "local_dir" | "openapi_spec" | "container_image";
  included_paths?: string[];
  excluded_paths?: string[];
  allowed_scanners?: string[];
  allow_exploitation?: boolean;
  max_budget_usd?: number;
  max_duration_seconds?: number;
}

export interface RecentScan {
  audit_id: string;
  target_uri: string;
  scanned_at: string;
  total_findings: number;
  actionable_count: number;
  history: number[]; // last 7 scans finding counts
}

export const TERMINAL_STATES: AuditState[] = ["done", "scope_denied", "cancelled"];

export const SCANNER_LABELS: Record<string, string> = {
  semgrep: "Semgrep",
  trivy: "Trivy",
  osv: "OSV",
  gitleaks: "Gitleaks",
  trufflehog: "TruffleHog",
};

export const SEVERITY_ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];
