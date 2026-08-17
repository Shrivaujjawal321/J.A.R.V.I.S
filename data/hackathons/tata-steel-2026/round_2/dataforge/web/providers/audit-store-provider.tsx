"use client";

import { useState, useCallback, useEffect, type ReactNode } from "react";
import { AuditStoreContext, LS_KEY, type AuditStoreState } from "@/lib/audit-store";
import type { AuditResult } from "@/lib/types";

export function AuditStoreProvider({ children }: { children: ReactNode }) {
  const [current, setCurrent_] = useState<AuditResult | null>(null);
  const [previous, setPrevious] = useState<AuditResult | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // Hydrate from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as { current: AuditResult; previous: AuditResult | null };
        setCurrent_(parsed.current ?? null);
        setPrevious(parsed.previous ?? null);
      }
    } catch {
      // ignore corrupt localStorage
    } finally {
      setHydrated(true);
    }
  }, []);

  const setCurrent = useCallback(
    (result: AuditResult, prev?: AuditResult | null) => {
      const prevVal = prev !== undefined ? prev : current;
      setCurrent_(result);
      setPrevious(prevVal);
      try {
        localStorage.setItem(LS_KEY, JSON.stringify({ current: result, previous: prevVal }));
      } catch {
        // localStorage unavailable
      }
    },
    [current]
  );

  const clearAll = useCallback(() => {
    setCurrent_(null);
    setPrevious(null);
    localStorage.removeItem(LS_KEY);
  }, []);

  const value: AuditStoreState = { current, previous, hydrated, setCurrent, clearAll };

  return (
    <AuditStoreContext.Provider value={value}>
      {children}
    </AuditStoreContext.Provider>
  );
}
