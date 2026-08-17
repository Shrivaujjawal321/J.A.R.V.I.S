"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { RecentScan } from "./types";

interface AppState {
  // Demo vs live mode
  isDemoMode: boolean;
  setDemoMode: (v: boolean) => void;

  // Settings
  enabledScanners: string[];
  setEnabledScanners: (scanners: string[]) => void;
  llmBudget: number;
  setLlmBudget: (v: number) => void;
  theme: "dark" | "light" | "system";
  setTheme: (t: "dark" | "light" | "system") => void;

  // Recent scans
  recentScans: RecentScan[];
  addRecentScan: (scan: RecentScan) => void;
  clearRecentScans: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      isDemoMode: true,
      setDemoMode: (v) => set({ isDemoMode: v }),

      enabledScanners: ["semgrep", "trivy", "osv", "gitleaks", "trufflehog"],
      setEnabledScanners: (scanners) => set({ enabledScanners: scanners }),

      llmBudget: 2.0,
      setLlmBudget: (v) => set({ llmBudget: v }),

      theme: "dark",
      setTheme: (t) => set({ theme: t }),

      recentScans: [
        {
          audit_id: "2d919643-fbfa-4b2a-a1fd-e70b91905939",
          target_uri: "/My Apps/apps/enginerd",
          scanned_at: "2026-06-06T03:57:00Z",
          total_findings: 52,
          actionable_count: 15,
          history: [8, 12, 10, 14, 11, 13, 15],
        },
      ],
      addRecentScan: (scan) =>
        set((state) => {
          const filtered = state.recentScans.filter(
            (s) => s.target_uri !== scan.target_uri
          );
          return { recentScans: [scan, ...filtered].slice(0, 10) };
        }),
      clearRecentScans: () => set({ recentScans: [] }),
    }),
    {
      name: "audit-agent-store",
      partialize: (state) => ({
        enabledScanners: state.enabledScanners,
        llmBudget: state.llmBudget,
        theme: state.theme,
        recentScans: state.recentScans,
      }),
    }
  )
);
