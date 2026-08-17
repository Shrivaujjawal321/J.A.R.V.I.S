"use client";

/**
 * TickerInput — Terminal-style mono ticker input with autocomplete
 * Research ref: research/07_fintech_ui_references_2026.md (Bloomberg terminal amber widget)
 * Design: monospace font, cursor blink, uppercase auto-convert, ENTER to submit
 */

import { useState, useRef, useId, useCallback, type KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Search, ArrowRight } from "lucide-react";
import { cn, normalizeTicker, isValidTicker } from "@/lib/utils";

interface TickerInputProps {
  placeholder?: string;
  autoFocus?: boolean;
  className?: string;
  onSubmit?: (ticker: string) => void;
  defaultValue?: string;
}

const SUGGESTIONS = [
  { ticker: "NVDA", name: "NVIDIA Corporation" },
  { ticker: "AAPL", name: "Apple Inc." },
  { ticker: "MSFT", name: "Microsoft Corporation" },
  { ticker: "GOOGL", name: "Alphabet Inc." },
  { ticker: "AMZN", name: "Amazon.com Inc." },
  { ticker: "META", name: "Meta Platforms Inc." },
  { ticker: "TSLA", name: "Tesla Inc." },
  { ticker: "XOM", name: "Exxon Mobil Corporation" },
  { ticker: "WMT", name: "Walmart Inc." },
  { ticker: "JPM", name: "JPMorgan Chase & Co." },
  { ticker: "BABA", name: "Alibaba Group Holding" },
  { ticker: "BRK.B", name: "Berkshire Hathaway" },
];

export function TickerInput({
  placeholder = "Enter ticker...",
  autoFocus = false,
  className,
  onSubmit,
  defaultValue = "",
}: TickerInputProps) {
  const [value, setValue] = useState(defaultValue);
  const [focused, setFocused] = useState(false);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const listboxId = useId();

  const filtered = value.length > 0
    ? SUGGESTIONS.filter(
        (s) =>
          s.ticker.startsWith(value.toUpperCase()) ||
          s.name.toLowerCase().includes(value.toLowerCase()),
      ).slice(0, 5)
    : [];

  const showDropdown = focused && filtered.length > 0;

  const handleSubmit = useCallback(
    (ticker: string) => {
      const normalized = normalizeTicker(ticker);
      if (!isValidTicker(normalized)) return;

      if (onSubmit) {
        onSubmit(normalized);
      } else {
        router.push(`/brief/${normalized}`);
      }
    },
    [onSubmit, router],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (hoveredIdx !== null && filtered[hoveredIdx]) {
          handleSubmit(filtered[hoveredIdx].ticker);
        } else {
          handleSubmit(value);
        }
        setFocused(false);
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setHoveredIdx((prev) =>
          prev === null ? 0 : Math.min(prev + 1, filtered.length - 1),
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setHoveredIdx((prev) =>
          prev === null ? filtered.length - 1 : Math.max(prev - 1, 0),
        );
      } else if (e.key === "Escape") {
        setFocused(false);
        inputRef.current?.blur();
      }
    },
    [value, filtered, hoveredIdx, handleSubmit],
  );

  const valid = isValidTicker(normalizeTicker(value));

  return (
    <div className={cn("relative", className)}>
      {/* Input container */}
      <div
        className={cn(
          "flex items-center gap-3 rounded-lg border-2 px-4 py-3 transition-all duration-200",
          focused
            ? "border-[var(--color-accent)] bg-[var(--color-surface-1)] shadow-[0_0_0_3px_var(--color-accent-glow)]"
            : "border-[var(--color-border)] bg-[var(--color-surface-1)] hover:border-[var(--color-accent-dim)]",
        )}
      >
        <Search
          size={16}
          className={cn(
            "shrink-0 transition-colors",
            focused ? "text-[var(--color-accent)]" : "text-[var(--color-text-muted)]",
          )}
          aria-hidden="true"
        />

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => {
            setValue(e.target.value.toUpperCase());
            setHoveredIdx(null);
          }}
          onFocus={() => setFocused(true)}
          onBlur={() => {
            // Small delay to allow click on dropdown items
            setTimeout(() => setFocused(false), 150);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          maxLength={5}
          autoFocus={autoFocus}
          autoComplete="off"
          autoCapitalize="characters"
          spellCheck={false}
          className="flex-1 bg-transparent font-mono text-lg text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none min-w-0 tracking-widest"
          aria-label="Stock ticker symbol"
          aria-autocomplete="list"
          aria-controls={showDropdown ? listboxId : undefined}
          aria-haspopup={showDropdown ? "listbox" : undefined}
          aria-expanded={showDropdown}
          role="combobox"
        />

        {/* Submit button */}
        <motion.button
          type="button"
          onClick={() => {
            handleSubmit(value);
            setFocused(false);
          }}
          disabled={!valid}
          className={cn(
            "shrink-0 flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-mono font-bold uppercase tracking-wider transition-all",
            valid
              ? "bg-[var(--color-accent)] text-white hover:bg-[var(--color-accent-dim)] cursor-pointer"
              : "bg-[var(--color-surface-2)] text-[var(--color-text-muted)] cursor-not-allowed",
          )}
          whileTap={valid ? { scale: 0.96 } : undefined}
          aria-label="Analyze ticker"
        >
          <span className="hidden sm:inline">Analyze</span>
          <ArrowRight size={12} aria-hidden="true" />
        </motion.button>
      </div>

      {/* Autocomplete dropdown */}
      <AnimatePresence>
        {showDropdown && (
          <motion.ul
            id={listboxId}
            role="listbox"
            aria-label="Ticker suggestions"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.12 }}
            className="absolute top-full left-0 right-0 mt-1.5 z-50 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-1)] shadow-2xl overflow-hidden"
          >
            {filtered.map((s, i) => (
              <li
                key={s.ticker}
                role="option"
                aria-selected={hoveredIdx === i}
                onMouseEnter={() => setHoveredIdx(i)}
                onMouseLeave={() => setHoveredIdx(null)}
                onClick={() => {
                  handleSubmit(s.ticker);
                  setValue(s.ticker);
                  setFocused(false);
                }}
                className={cn(
                  "flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors border-b border-[var(--color-border-subtle)] last:border-b-0",
                  hoveredIdx === i
                    ? "bg-[var(--color-surface-2)]"
                    : "hover:bg-[var(--color-surface-2)]",
                )}
              >
                <span className="font-mono text-sm font-bold text-[var(--color-accent)] w-16 shrink-0">
                  {s.ticker}
                </span>
                <span className="text-sm text-[var(--color-text-secondary)] truncate">
                  {s.name}
                </span>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}
