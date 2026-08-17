import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Severity, VerificationStatus } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function severityLabel(s: Severity): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function verificationLabel(v: VerificationStatus): string {
  switch (v) {
    case "confirmed": return "Confirmed";
    case "false_positive": return "False Positive";
    case "needs_manual": return "Needs Review";
    case "unverified": return "Unverified";
  }
}

export function cweLabel(cwe: string | null): string {
  if (!cwe) return "";
  // "CWE-89: SQL INJECTION" → "SQL Injection"
  const match = cwe.match(/CWE-\d+[:\s]+(.+)/);
  if (match) {
    return match[1]
      .toLowerCase()
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  }
  return cwe;
}

export function cweCode(cwe: string | null): string {
  if (!cwe) return "";
  const match = cwe.match(/(CWE-\d+)/);
  return match ? match[1] : cwe;
}

export function formatPath(filePath: string | null): string {
  if (!filePath) return "";
  // Strip long absolute prefixes for display
  const parts = filePath.split("/");
  if (parts.length > 5) {
    return ".../" + parts.slice(-3).join("/");
  }
  return filePath;
}

export function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function parseCvssVector(vector: string): Record<string, string> {
  const result: Record<string, string> = {};
  // CVSS:4.0/AV:N/AC:L/...
  const parts = vector.replace("CVSS:4.0/", "").split("/");
  for (const part of parts) {
    const [key, value] = part.split(":");
    if (key && value) result[key] = value;
  }
  return result;
}

const CVSS_METRIC_LABELS: Record<string, { label: string; values: Record<string, string> }> = {
  AV: { label: "Attack Vector", values: { N: "Network", A: "Adjacent", L: "Local", P: "Physical" } },
  AC: { label: "Attack Complexity", values: { L: "Low", H: "High" } },
  AT: { label: "Attack Requirements", values: { N: "None", P: "Present" } },
  PR: { label: "Privileges Required", values: { N: "None", L: "Low", H: "High" } },
  UI: { label: "User Interaction", values: { N: "None", P: "Passive", A: "Active" } },
  VC: { label: "Vuln. Conf. Impact", values: { N: "None", L: "Low", H: "High" } },
  VI: { label: "Vuln. Integ. Impact", values: { N: "None", L: "Low", H: "High" } },
  VA: { label: "Vuln. Avail. Impact", values: { N: "None", L: "Low", H: "High" } },
  SC: { label: "Sub. Conf. Impact", values: { N: "None", L: "Low", H: "High" } },
  SI: { label: "Sub. Integ. Impact", values: { N: "None", L: "Low", H: "High" } },
  SA: { label: "Sub. Avail. Impact", values: { N: "None", L: "Low", H: "High" } },
};

export function cvssMetricLabel(key: string): string {
  return CVSS_METRIC_LABELS[key]?.label ?? key;
}

export function cvssValueLabel(key: string, value: string): string {
  return CVSS_METRIC_LABELS[key]?.values[value] ?? value;
}
