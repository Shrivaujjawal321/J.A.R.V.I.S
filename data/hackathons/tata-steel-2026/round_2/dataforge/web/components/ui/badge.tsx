import { cn } from "@/lib/utils";
import type { ComponentProps } from "react";

interface BadgeProps extends ComponentProps<"span"> {
  variant?: "default" | "outline" | "ghost";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium font-mono tabular-nums",
        variant === "default" && "bg-[oklch(22%_0.01_250)] text-[var(--color-fg)]",
        variant === "outline" && "border border-[var(--color-border)] text-[var(--color-fg-muted)]",
        variant === "ghost" && "text-[var(--color-fg-muted)]",
        className
      )}
      {...props}
    />
  );
}
