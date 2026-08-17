import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold tracking-wide transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[var(--color-accent)] text-white",
        secondary:
          "border-[var(--color-border)] bg-[var(--color-surface-2)] text-[var(--color-text-secondary)]",
        bullish:
          "border-[var(--color-bullish-dim)] bg-[var(--color-bullish-bg)] text-[var(--color-bullish)] uppercase font-mono",
        bearish:
          "border-[var(--color-bearish-dim)] bg-[var(--color-bearish-bg)] text-[var(--color-bearish)] uppercase font-mono",
        neutral:
          "border-[var(--color-neutral-dim)] bg-[var(--color-neutral-bg)] text-[var(--color-neutral)] uppercase font-mono",
        gold:
          "border-[var(--color-gold-border)] bg-[var(--color-gold-bg)] text-[var(--color-gold)] uppercase font-mono",
        caution:
          "border-orange-800/40 bg-orange-950/40 text-orange-400 uppercase font-mono",
        outline:
          "text-[var(--color-text-primary)] border-[var(--color-border)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
