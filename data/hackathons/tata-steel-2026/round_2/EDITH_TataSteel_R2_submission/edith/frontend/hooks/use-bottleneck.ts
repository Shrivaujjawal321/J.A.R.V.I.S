"use client";

import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "@/lib/utils";
import type { BottleneckData } from "@/lib/types";

export function useBottleneck() {
  return useQuery<BottleneckData>({
    queryKey: ["bottleneck"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/bottleneck`);
      if (!res.ok) throw new Error(`Bottleneck fetch failed: ${res.status}`);
      return res.json() as Promise<BottleneckData>;
    },
    refetchInterval: 10_000,
    staleTime: 9_000,
  });
}
