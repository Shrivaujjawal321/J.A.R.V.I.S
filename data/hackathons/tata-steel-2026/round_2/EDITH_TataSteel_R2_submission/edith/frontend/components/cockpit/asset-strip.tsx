"use client";

import { useQuery } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { API_BASE } from "@/lib/utils";
import { StatusBadge } from "@/components/ui/status-badge";
import { toStatusBand } from "@/lib/types";
import type { AssetSummary } from "@/lib/types";
import { useEdithStore } from "@/store/edith-store";

async function fetchAssets(): Promise<AssetSummary[]> {
  const res = await fetch(`${API_BASE}/api/assets`);
  if (!res.ok) throw new Error(`Assets fetch failed: ${res.status}`);
  const data = await res.json();
  return data.assets ?? data;
}

function TileSkeleton() {
  return (
    <div
      className="status-tile"
      aria-busy="true"
      role="status"
      aria-label="Loading asset"
    >
      <div className="flex items-center justify-between mb-1.5 gap-2">
        <div className="skeleton h-3 w-20 rounded" />
        <div className="skeleton h-4 w-12 rounded-full" />
      </div>
      <div className="skeleton h-2.5 w-full rounded" />
    </div>
  );
}

export function AssetStrip() {
  const { selectedAssetId, setSelectedAssetId } = useEdithStore();

  const { data, isLoading, isError } = useQuery<AssetSummary[]>({
    queryKey: ["assets"],
    queryFn: fetchAssets,
    refetchInterval: 5_000,
    staleTime: 4_000,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col gap-2 p-3" aria-label="Loading asset list">
        {Array.from({ length: 8 }, (_, i) => (
          <TileSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div
        className="p-4 text-center"
        style={{ color: "var(--color-status-alarm-fg)" }}
        role="alert"
      >
        <p className="text-xs font-medium">Failed to load assets</p>
        <p className="text-xs mt-1" style={{ color: "var(--color-fg-tertiary)" }}>
          Check backend at 127.0.0.1:8077
        </p>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="p-4 flex items-center justify-center h-24">
        <p className="panel-hint text-center">
          All 15 assets at a glance. Red = act now. Yellow = watch. Green = all clear.
          Tap any asset to focus.
        </p>
      </div>
    );
  }

  return (
    <nav aria-label="Asset health strip" className="flex flex-col gap-1.5 p-2.5 overflow-y-auto">
      <AnimatePresence initial={false}>
        {data.map((asset, idx) => {
          const status = toStatusBand(asset.health);
          const selected = asset.asset_id === selectedAssetId;

          return (
            <motion.button
              key={asset.asset_id}
              type="button"
              role="button"
              aria-pressed={selected}
              aria-label={`${asset.asset_id} — ${status}${asset.headline ? `: ${asset.headline}` : ""}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                type: "spring",
                stiffness: 320,
                damping: 28,
                delay: idx * 0.025,
              }}
              onClick={() => setSelectedAssetId(asset.asset_id)}
              className={cn(
                "status-tile w-full text-left",
                `status-tile--${status}`,
                selected && "status-tile--selected"
              )}
            >
              {/* Row 1: asset ID + compact state badge */}
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="sensor-id truncate text-xs">{asset.asset_id}</span>
                <StatusBadge status={status} compact />
              </div>

              {/* Row 2: plain-language headline (one-liner) */}
              <p
                className="text-xs leading-snug truncate"
                style={{ color: "var(--color-fg-secondary)" }}
                title={asset.headline ?? asset.description}
              >
                {asset.headline ?? asset.description}
              </p>
            </motion.button>
          );
        })}
      </AnimatePresence>
    </nav>
  );
}
