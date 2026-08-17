import type {
  AuditReport,
  AuditRequest,
  AuditRunView,
  FindingsPage,
} from "./types";

const BASE = "/api/audit";

export async function checkDaemonHealth(): Promise<boolean> {
  try {
    const res = await fetch("/api/health", {
      signal: AbortSignal.timeout(2000),
      cache: "no-store",
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function startAudit(req: AuditRequest): Promise<AuditRunView> {
  const res = await fetch(BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.error?.message ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getAuditStatus(auditId: string): Promise<AuditRunView> {
  const res = await fetch(`${BASE}/${auditId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getReport(auditId: string): Promise<AuditReport> {
  const res = await fetch(`${BASE}/${auditId}/report`, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getFindings(params: {
  auditId: string;
  limit?: number;
  cursor?: string;
  severity?: string;
  status?: string;
}): Promise<FindingsPage> {
  const { auditId, limit = 100, cursor, severity, status } = params;
  const url = new URL(`${BASE}/${auditId}/findings`, window.location.origin);
  url.searchParams.set("limit", String(limit));
  if (cursor) url.searchParams.set("cursor", cursor);
  if (severity) url.searchParams.set("severity", severity);
  if (status) url.searchParams.set("status", status);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function cancelAudit(auditId: string): Promise<void> {
  await fetch(`${BASE}/${auditId}/cancel`, { method: "POST" });
}
