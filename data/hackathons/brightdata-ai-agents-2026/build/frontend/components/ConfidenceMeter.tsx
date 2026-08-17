"use client";

import { motion } from "framer-motion";
import { cn, formatConfidence } from "@/lib/utils";
import type { DataQualityFlag } from "@/lib/types";

interface ConfidenceMeterProps {
  confidence: number; // [0.0, 1.0]
  qualityFlag: DataQualityFlag;
  size?: "sm" | "md" | "lg";
  className?: string;
  showLabel?: boolean;
}

const SIZE_MAP = {
  sm: { cx: 40, cy: 40, r: 30, strokeWidth: 4, fontSize: "text-xs" },
  md: { cx: 56, cy: 56, r: 44, strokeWidth: 5, fontSize: "text-sm" },
  lg: { cx: 72, cy: 72, r: 58, strokeWidth: 6, fontSize: "text-base" },
};

const QUALITY_COLORS: Record<DataQualityFlag, string> = {
  full: "var(--color-bullish)",
  partial: "var(--color-neutral)",
  minimal: "var(--color-bearish)",
};

export function ConfidenceMeter({
  confidence,
  qualityFlag,
  size = "md",
  className,
  showLabel = true,
}: ConfidenceMeterProps) {
  const { cx, cy, r, strokeWidth, fontSize } = SIZE_MAP[size];
  const svgSize = cx * 2;
  const circumference = 2 * Math.PI * r;
  const strokeDashoffset = circumference * (1 - confidence);
  const color = QUALITY_COLORS[qualityFlag];

  return (
    <div
      className={cn("flex flex-col items-center gap-2", className)}
      role="meter"
      aria-valuenow={Math.round(confidence * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Confidence: ${formatConfidence(confidence)}, data quality: ${qualityFlag}`}
    >
      <svg
        width={svgSize}
        height={svgSize}
        viewBox={`0 0 ${svgSize} ${svgSize}`}
        aria-hidden="true"
      >
        {/* Background ring */}
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="var(--color-surface-2)"
          strokeWidth={strokeWidth}
        />
        {/* Progress ring */}
        <motion.circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.2, ease: [0.19, 1, 0.22, 1] }}
          transform={`rotate(-90 ${cx} ${cy})`}
        />
        {/* Center text */}
        <text
          x={cx}
          y={cy}
          textAnchor="middle"
          dominantBaseline="central"
          fill="var(--color-text-primary)"
          className={cn("font-mono font-bold", fontSize)}
          style={{ fontSize: size === "lg" ? "1.1rem" : size === "md" ? "0.9rem" : "0.7rem" }}
        >
          {formatConfidence(confidence)}
        </text>
      </svg>
      {showLabel && (
        <div className="text-center">
          <p
            className="text-xs font-mono uppercase tracking-widest"
            style={{ color }}
          >
            {qualityFlag === "full"
              ? "Full Coverage"
              : qualityFlag === "partial"
                ? "Partial Coverage"
                : "Minimal Coverage"}
          </p>
        </div>
      )}
    </div>
  );
}
