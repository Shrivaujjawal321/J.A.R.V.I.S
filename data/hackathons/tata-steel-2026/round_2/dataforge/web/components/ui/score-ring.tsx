"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion, useSpring, useTransform, useMotionValue } from "framer-motion";
import { scoreRingColor, gradeColor } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface ScoreRingProps {
  score: number;
  grade?: string;
  previousScore?: number;
  size?: "sm" | "md" | "lg" | "hero";
  showGrade?: boolean;
  showLabel?: boolean;
  className?: string;
  animateFrom?: number;
}

const SIZE_MAP = {
  sm: { px: 48, stroke: 4, fontSize: "text-sm", gradeFontSize: "text-[10px]" },
  md: { px: 80, stroke: 5, fontSize: "text-xl", gradeFontSize: "text-xs" },
  lg: { px: 120, stroke: 7, fontSize: "text-3xl", gradeFontSize: "text-sm" },
  hero: { px: 200, stroke: 10, fontSize: "text-6xl", gradeFontSize: "text-lg" },
};

export function ScoreRing({
  score,
  grade,
  previousScore,
  size = "md",
  showGrade = false,
  showLabel = false,
  className,
  animateFrom,
}: ScoreRingProps) {
  const prefersReduced = useReducedMotion();
  const config = SIZE_MAP[size];
  const radius = (config.px - config.stroke) / 2;
  const circumference = 2 * Math.PI * radius;

  const startScore = animateFrom ?? previousScore ?? (prefersReduced ? score : 0);
  const scoreMotion = useMotionValue(startScore);
  const springScore = useSpring(scoreMotion, { stiffness: 80, damping: 20 });

  const dashOffset = useTransform(springScore, (v) => {
    const pct = Math.max(0, Math.min(100, v)) / 100;
    return circumference * (1 - pct);
  });

  const [displayScore, setDisplayScore] = useState(startScore);

  useEffect(() => {
    const unsubscribe = springScore.on("change", (v) => {
      setDisplayScore(Math.round(v));
    });
    return unsubscribe;
  }, [springScore]);

  useEffect(() => {
    if (!prefersReduced) {
      scoreMotion.set(score);
    } else {
      setDisplayScore(score);
    }
  }, [score, scoreMotion, prefersReduced]);

  const ringColor = scoreRingColor(score);
  const prevRingColor = previousScore != null ? scoreRingColor(previousScore) : undefined;
  const prevDashOffset = previousScore != null
    ? circumference * (1 - previousScore / 100)
    : undefined;

  return (
    <div
      className={cn("relative inline-flex flex-col items-center gap-1", className)}
      role="img"
      aria-label={`Dataset quality score: ${score} out of 100${grade ? `, grade ${grade}` : ""}`}
    >
      <svg
        width={config.px}
        height={config.px}
        viewBox={`0 0 ${config.px} ${config.px}`}
        fill="none"
        style={{ transform: "rotate(-90deg)" }}
        aria-hidden="true"
      >
        {/* Background track */}
        <circle
          cx={config.px / 2}
          cy={config.px / 2}
          r={radius}
          strokeWidth={config.stroke}
          stroke="oklch(22% 0.008 250)"
          fill="none"
        />

        {/* Previous score ring (ghost) */}
        {previousScore != null && prevDashOffset != null && (
          <circle
            cx={config.px / 2}
            cy={config.px / 2}
            r={radius}
            strokeWidth={config.stroke}
            stroke={prevRingColor}
            strokeDasharray={circumference}
            strokeDashoffset={prevDashOffset}
            strokeLinecap="round"
            fill="none"
            opacity={0.25}
          />
        )}

        {/* Active score ring */}
        <motion.circle
          cx={config.px / 2}
          cy={config.px / 2}
          r={radius}
          strokeWidth={config.stroke}
          stroke={ringColor}
          strokeDasharray={circumference}
          strokeDashoffset={prefersReduced ? circumference * (1 - score / 100) : dashOffset}
          strokeLinecap="round"
          fill="none"
          style={{ filter: `drop-shadow(0 0 6px ${ringColor}44)` }}
        />
      </svg>

      {/* Center number */}
      <div
        className="absolute inset-0 flex flex-col items-center justify-center"
        style={{ transform: "none" }}
      >
        <span
          className={cn(
            "font-mono font-bold tabular-nums leading-none",
            config.fontSize
          )}
          style={{ color: ringColor }}
          aria-hidden="true"
        >
          {displayScore}
        </span>
        {showGrade && grade && (
          <span
            className={cn("font-mono font-semibold mt-0.5", config.gradeFontSize)}
            style={{ color: gradeColor(grade) }}
          >
            {grade}
          </span>
        )}
      </div>

      {showLabel && (
        <span className="text-xs text-[var(--color-fg-muted)] mt-1">/ 100</span>
      )}
    </div>
  );
}
