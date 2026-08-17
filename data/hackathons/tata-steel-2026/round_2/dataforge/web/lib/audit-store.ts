"use client";

import { createContext, useContext } from "react";
import type { AuditResult } from "./types";

export interface AuditStoreState {
  current: AuditResult | null;
  previous: AuditResult | null;
  /** true once localStorage has been read on mount */
  hydrated: boolean;
  setCurrent: (result: AuditResult, previous?: AuditResult | null) => void;
  clearAll: () => void;
}

export const AuditStoreContext = createContext<AuditStoreState | null>(null);

export function useAuditStore(): AuditStoreState {
  const ctx = useContext(AuditStoreContext);
  if (!ctx) throw new Error("useAuditStore must be used within AuditStoreProvider");
  return ctx;
}

// LocalStorage key
export const LS_KEY = "dataforge_last_audit";
