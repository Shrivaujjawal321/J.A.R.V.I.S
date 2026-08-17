"use client";

import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { AlertTriangle, X } from "lucide-react";
import { cn, formatTs } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/status-badge";
import { useEdithStore } from "@/store/edith-store";
import type { StatusBand } from "@/lib/types";

function severityToBand(sev: string): StatusBand {
  if (sev === "ALARM") return "alarm";
  if (sev === "WARNING") return "warning";
  return "unknown";
}

// G5-frontend: role-based severity filter
function rolePassesSeverity(role: string, severity: string): boolean {
  if (role === "Manager") return severity === "ALARM";
  if (role === "Engineer") return severity === "WARNING" || severity === "ALARM";
  return true; // Operator: all
}

export function AlertsFeed() {
  const { alerts, dismissAlert, userRole } = useEdithStore();

  // G5: client-side role filter
  const filtered = alerts.filter((a) => rolePassesSeverity(userRole, a.severity));

  if (filtered.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center h-24 px-4 gap-2"
        aria-live="polite"
        aria-label="No active alerts"
      >
        <span
          className="status-dot status-dot--healthy"
          aria-hidden="true"
        />
        <p className="panel-hint text-center leading-relaxed">
          No alerts right now. When a sensor crosses a safe limit, the alert
          appears here instantly. ALARM (red) = act now. WARNING (yellow) =
          early sign.
        </p>
      </div>
    );
  }

  return (
    <div
      className="flex flex-col gap-2 px-3 py-2 overflow-y-auto"
      role="log"
      aria-label="Active alerts feed"
      aria-live="polite"
    >
      <AnimatePresence initial={false} mode="popLayout">
        {filtered.map((alert) => {
          const band = severityToBand(alert.severity);
          return (
            <motion.div
              key={alert.id}
              role="alert"
              aria-live={alert.severity === "ALARM" ? "assertive" : "polite"}
              aria-atomic="true"
              initial={{ opacity: 0, x: -12, scale: 0.98 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 16, scale: 0.97 }}
              transition={{ type: "spring", stiffness: 380, damping: 24, mass: 0.9 }}
              className={cn("alert-card", `alert-card--${band}`)}
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5 min-w-0">
                  <AlertTriangle
                    size={12}
                    aria-hidden="true"
                    style={{
                      color:
                        band === "alarm"
                          ? "var(--color-status-alarm-fg)"
                          : "var(--color-status-warning-fg)",
                      flexShrink: 0,
                    }}
                  />
                  <span className="sensor-id text-xs truncate">{alert.sensor}</span>
                  <StatusBadge status={band} compact />
                </div>
                <button
                  type="button"
                  onClick={() => dismissAlert(alert.id)}
                  className="btn-ghost p-1 flex-shrink-0"
                  style={{ minHeight: "auto", minWidth: "auto" }}
                  aria-label={`Dismiss ${alert.severity} alert for ${alert.sensor}`}
                >
                  <X size={11} aria-hidden="true" />
                </button>
              </div>

              <p
                className="text-xs font-medium mb-1 leading-snug"
                style={{ color: "var(--color-fg-primary)" }}
              >
                {alert.reason}
              </p>

              <div className="flex items-center gap-3">
                <span
                  className="mono-data text-xs"
                  style={{ color: "var(--color-fg-secondary)" }}
                >
                  {typeof alert.value === "number" ? alert.value.toFixed(3) : alert.value}{" "}
                  {alert.unit}
                </span>
                <span
                  className="label-caps"
                  style={{ color: "var(--color-fg-faint)" }}
                >
                  /{" "}
                  {typeof alert.threshold === "number"
                    ? alert.threshold.toFixed(3)
                    : alert.threshold}
                </span>
                <time
                  dateTime={String(alert.ts)}
                  className="label-caps ml-auto"
                  style={{ color: "var(--color-fg-faint)" }}
                >
                  {formatTs(alert.ts)}
                </time>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
