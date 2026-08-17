"use client";

import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "@/lib/utils";
import type { FocusData } from "@/lib/types";

export function useFocus(assetId: string) {
  return useQuery<FocusData>({
    queryKey: ["focus", assetId],
    queryFn: async () => {
      const res = await fetch(
        `${API_BASE}/api/focus/${encodeURIComponent(assetId)}`
      );
      if (!res.ok) throw new Error(`Focus fetch failed: ${res.status}`);
      return res.json() as Promise<FocusData>;
    },
    refetchInterval: 5_000,
    staleTime: 4_000,
    enabled: Boolean(assetId),
  });
}
