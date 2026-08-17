"use client";

import { cn, severityLabel } from "@/lib/utils";
import type { Severity } from "@/lib/types";
import {
  AlertOctagon,
  AlertTriangle,
  AlertCircle,
  Info,
  Shield,
} from "lucide-react";

const CONFIG: Record<
  Severity,
  {
    icon: React.ElementType;
    style: string;
    iconStyle: string;
  }
> = {
  critical: {
    icon: AlertOctagon,
    style:
      "bg-[var(--critical-bg)] text-[var(--critical)] border border-[var(--critical-border)]",
    iconStyle: "text-[var(--critical)]",
  },
  high: {
    icon: AlertTriangle,
    style:
      "bg-[var(--high-bg)] text-[var(--high)] border border-[var(--high-border)]",
    iconStyle: "text-[var(--high)]",
  },
  medium: {
    icon: AlertCircle,
    style:
      "bg-[var(--medium-bg)] text-[var(--medium)] border border-[var(--medium-border)]",
    iconStyle: "text-[var(--medium)]",
  },
  low: {
    icon: Shield,
    style:
      "bg-[var(--low-bg)] text-[var(--low)] border border-[var(--low-border)]",
    iconStyle: "text-[var(--low)]",
  },
  info: {
    icon: Info,
    style:
      "bg-[var(--info-bg)] text-[var(--info)] border border-[var(--info-border)]",
    iconStyle: "text-[var(--info)]",
  },
};

interface SeverityBadgeProps {
  severity: Severity;
  compact?: boolean;
  className?: string;
}

export function SeverityBadge({
  severity,
  compact = false,
  className,
}: SeverityBadgeProps) {
  const cfg = CONFIG[severity];
  const Icon = cfg.icon;

  if (compact) {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs font-medium",
          cfg.style,
          className
        )}
        aria-label={`Severity: ${severityLabel(severity)}`}
      >
        <Icon className={cn("h-3 w-3 shrink-0", cfg.iconStyle)} aria-hidden />
        <span>{severityLabel(severity)}</span>
      </span>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-semibold tracking-wide uppercase",
        cfg.style,
        className
      )}
      aria-label={`Severity: ${severityLabel(severity)}`}
    >
      <Icon className={cn("h-3.5 w-3.5 shrink-0", cfg.iconStyle)} aria-hidden />
      <span>{severityLabel(severity)}</span>
    </span>
  );
}

export function SeverityDot({ severity }: { severity: Severity }) {
  const cfg = CONFIG[severity];
  const Icon = cfg.icon;
  return (
    <Icon
      className={cn("h-4 w-4 shrink-0", cfg.iconStyle)}
      aria-label={`Severity: ${severityLabel(severity)}`}
    />
  );
}
