"use client";

import * as Dialog from "@radix-ui/react-dialog";
import * as Switch from "@radix-ui/react-switch";
import * as Slider from "@radix-ui/react-slider";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { Settings, X } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { cn } from "@/lib/utils";

const ALL_SCANNERS = [
  { id: "semgrep", label: "Semgrep (SAST)" },
  { id: "trivy", label: "Trivy (Container/IaC)" },
  { id: "osv", label: "OSV (SCA/CVE)" },
  { id: "gitleaks", label: "Gitleaks (Secrets)" },
  { id: "trufflehog", label: "TruffleHog (Secrets, verified)" },
];

const THEME_OPTIONS = [
  { value: "dark", label: "Dark" },
  { value: "light", label: "Light" },
  { value: "system", label: "System" },
] as const;

export function SettingsSheet() {
  const { enabledScanners, setEnabledScanners, llmBudget, setLlmBudget, theme, setTheme } =
    useAppStore();
  const shouldReduce = useReducedMotion();

  function toggleScanner(id: string) {
    if (enabledScanners.includes(id)) {
      setEnabledScanners(enabledScanners.filter((s) => s !== id));
    } else {
      setEnabledScanners([...enabledScanners, id]);
    }
  }

  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button
          type="button"
          className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors hover:bg-[var(--surface-raised)]"
          style={{
            borderColor: "var(--border)",
            background: "var(--surface)",
            color: "var(--text-muted)",
          }}
          aria-label="Open settings"
        >
          <Settings className="h-3.5 w-3.5" aria-hidden />
          Settings
        </button>
      </Dialog.Trigger>

      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/40" />
        <Dialog.Content
          className="fixed right-0 top-0 bottom-0 z-50 flex flex-col overflow-hidden shadow-2xl outline-none"
          style={{
            width: "min(400px, 90vw)",
            background: "var(--surface)",
            borderLeft: "1px solid var(--border)",
          }}
          aria-label="Settings"
        >
          {/* Header */}
          <div
            className="flex items-center justify-between p-4 shrink-0"
            style={{ borderBottom: "1px solid var(--border)" }}
          >
            <Dialog.Title
              className="text-sm font-semibold"
              style={{ color: "var(--text)" }}
            >
              Settings
            </Dialog.Title>
            <Dialog.Close asChild>
              <button
                type="button"
                className="rounded p-1.5 transition-colors hover:bg-[var(--surface-raised)]"
                style={{ color: "var(--text-muted)" }}
                aria-label="Close settings"
              >
                <X className="h-4 w-4" aria-hidden />
              </button>
            </Dialog.Close>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Scanners */}
            <section aria-label="Scanner configuration">
              <h3
                className="mb-3 text-xs font-semibold uppercase tracking-wider"
                style={{ color: "var(--text-muted)" }}
              >
                Scanners
              </h3>
              <div className="space-y-3">
                {ALL_SCANNERS.map((s) => (
                  <div key={s.id} className="flex items-center justify-between gap-4">
                    <label
                      htmlFor={`scanner-${s.id}`}
                      className="text-sm cursor-pointer"
                      style={{ color: "var(--text)" }}
                    >
                      {s.label}
                    </label>
                    <Switch.Root
                      id={`scanner-${s.id}`}
                      checked={enabledScanners.includes(s.id)}
                      onCheckedChange={() => toggleScanner(s.id)}
                      className={cn(
                        "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full transition-colors",
                        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
                      )}
                      style={{
                        background: enabledScanners.includes(s.id)
                          ? "var(--accent)"
                          : "var(--surface-overlay)",
                      }}
                    >
                      <Switch.Thumb
                        className="pointer-events-none block h-4 w-4 rounded-full shadow-sm transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0.5 mt-0.5"
                        style={{ background: "white" }}
                      />
                    </Switch.Root>
                  </div>
                ))}
              </div>
            </section>

            {/* LLM Budget */}
            <section aria-label="LLM verification budget">
              <h3
                className="mb-3 text-xs font-semibold uppercase tracking-wider"
                style={{ color: "var(--text-muted)" }}
              >
                LLM Verify Budget
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span style={{ color: "var(--text)" }}>Max per scan</span>
                  <span
                    className="font-mono font-semibold"
                    style={{ color: "var(--accent)" }}
                  >
                    ${llmBudget.toFixed(2)}
                  </span>
                </div>
                <Slider.Root
                  className="relative flex w-full touch-none select-none items-center"
                  value={[llmBudget]}
                  min={0}
                  max={10}
                  step={0.5}
                  onValueChange={([v]) => setLlmBudget(v)}
                  aria-label="LLM budget slider"
                >
                  <Slider.Track
                    className="relative h-1.5 w-full grow overflow-hidden rounded-full"
                    style={{ background: "var(--surface-overlay)" }}
                  >
                    <Slider.Range
                      className="absolute h-full rounded-full"
                      style={{ background: "var(--accent)" }}
                    />
                  </Slider.Track>
                  <Slider.Thumb
                    className="block h-4 w-4 rounded-full shadow-sm transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent)]"
                    style={{
                      background: "var(--accent)",
                      border: "2px solid var(--surface)",
                    }}
                  />
                </Slider.Root>
                <div
                  className="flex justify-between text-xs"
                  style={{ color: "var(--text-subtle)" }}
                  aria-hidden
                >
                  <span>$0</span>
                  <span>$10</span>
                </div>
              </div>
            </section>

            {/* Theme */}
            <section aria-label="Theme selection">
              <h3
                className="mb-3 text-xs font-semibold uppercase tracking-wider"
                style={{ color: "var(--text-muted)" }}
              >
                Theme
              </h3>
              <div className="flex gap-2" role="radiogroup" aria-label="Color theme">
                {THEME_OPTIONS.map((t) => (
                  <button
                    key={t.value}
                    type="button"
                    role="radio"
                    aria-checked={theme === t.value}
                    onClick={() => setTheme(t.value)}
                    className={cn(
                      "flex-1 rounded-lg border py-2 text-xs font-medium transition-colors",
                      theme === t.value
                        ? "border-[var(--accent)] bg-[var(--accent-muted)] text-[var(--accent)]"
                        : "border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)]"
                    )}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </section>

            {/* Safety note */}
            <section>
              <div
                className="rounded-lg border p-3 text-xs leading-relaxed"
                style={{
                  background: "var(--surface-raised)",
                  borderColor: "var(--border)",
                  color: "var(--text-muted)",
                }}
              >
                <strong style={{ color: "var(--text)" }}>Safety note:</strong> AuditAgent is
                designed for defensive use only. Only scan repositories you own or have explicit
                authorization to audit. Never run against third-party code without consent.
              </div>
            </section>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
