"use client";

import { cn } from "@/lib/utils";
import type { StatusBand } from "@/lib/types";

const LABEL: Record<StatusBand, string> = {
  healthy:  "Healthy",
  warning:  "Warning",
  alarm:    "Alarm",
  critical: "Critical",
  unknown:  "Unknown",
  offline:  "Offline",
};

interface StatusBadgeProps {
  status: StatusBand;
  compact?: boolean;
  className?: string;
}

export function StatusBadge({ status, compact, className }: StatusBadgeProps) {
  return (
    <span
      className={cn("status-badge", `status-badge--${status}`, className)}
      aria-label={`Status: ${LABEL[status]}`}
    >
      <span className={cn("status-dot", `status-dot--${status}`)} aria-hidden="true" />
      {!compact && LABEL[status]}
    </span>
  );
}

interface StatusDotProps {
  status: StatusBand;
  className?: string;
}

export function StatusDot({ status, className }: StatusDotProps) {
  return (
    <span
      className={cn("status-dot", `status-dot--${status}`, className)}
      aria-label={LABEL[status]}
      role="img"
    />
  );
}
