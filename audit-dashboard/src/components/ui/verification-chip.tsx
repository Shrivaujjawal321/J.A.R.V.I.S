"use client";

import { cn, verificationLabel } from "@/lib/utils";
import type { VerificationStatus } from "@/lib/types";
import { CheckCircle2, XCircle, Circle, HelpCircle } from "lucide-react";

const CONFIG: Record<
  VerificationStatus,
  { icon: React.ElementType; style: string }
> = {
  confirmed: {
    icon: CheckCircle2,
    style:
      "bg-[var(--critical-bg)] text-[var(--critical)] border border-[var(--critical-border)]",
  },
  false_positive: {
    icon: XCircle,
    style:
      "bg-[var(--surface-overlay)] text-[var(--text-muted)] border border-[var(--border)]",
  },
  needs_manual: {
    icon: HelpCircle,
    style:
      "bg-[var(--medium-bg)] text-[var(--medium)] border border-[var(--medium-border)]",
  },
  unverified: {
    icon: Circle,
    style:
      "bg-[var(--surface-overlay)] text-[var(--text-muted)] border border-[var(--border)]",
  },
};

interface VerificationChipProps {
  status: VerificationStatus;
  className?: string;
}

export function VerificationChip({ status, className }: VerificationChipProps) {
  const cfg = CONFIG[status];
  const Icon = cfg.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs font-medium",
        cfg.style,
        className
      )}
    >
      <Icon className="h-3 w-3 shrink-0" aria-hidden />
      {verificationLabel(status)}
    </span>
  );
}
