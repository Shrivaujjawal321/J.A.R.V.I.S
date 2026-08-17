"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ArrowRight, AlertTriangle } from "lucide-react";
import { useBottleneck } from "@/hooks/use-bottleneck";
import { useEdithStore } from "@/store/edith-store";

/**
 * Full-width "START HERE" banner — spec §7a.
 * Renders only when ≥2 assets need action, OR a single act_now (alarm) asset exists.
 * Dismissed per-session; re-appears if a new act_now asset appears after dismissal.
 */
export function StartHereBanner() {
  const { data } = useBottleneck();
  const { setSelectedAssetId } = useEdithStore();
  const [dismissed, setDismissed] = useState(false);
  const [lastActNowId, setLastActNowId] = useState<string | null>(null);

  // Re-show if a new act_now asset appears after the user dismissed
  const topItem = data?.items[0];
  const topIsActNow = topItem?.health === "alarm";

  useEffect(() => {
    if (topIsActNow && topItem && topItem.asset_id !== lastActNowId) {
      setLastActNowId(topItem.asset_id);
      setDismissed(false); // re-surface for new critical asset
    }
  }, [topIsActNow, topItem, lastActNowId]);

  // Trigger: ≥2 assets OR single act_now — spec §7a + user brief
  const shouldShow =
    data != null &&
    !dismissed &&
    (data.count >= 2 || (data.count === 1 && topIsActNow));

  if (!shouldShow || !data || data.items.length === 0) return null;

  const top = data.items[0];
  const whyText =
    top.why && top.why.length > 0 ? top.why.join(", ") : "it needs attention first";

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: "auto" }}
        exit={{ opacity: 0, height: 0 }}
        transition={{ type: "spring", stiffness: 340, damping: 30 }}
        className="start-here-banner"
        role="alert"
        aria-live="assertive"
        aria-label="Multiple machines need attention"
      >
        {/* Left: icon + message */}
        <AlertTriangle
          size={15}
          aria-hidden="true"
          className="flex-shrink-0"
          style={{ color: "var(--color-status-alarm-fg)" }}
        />
        <p
          className="text-sm leading-snug flex-1 min-w-0"
          style={{ color: "var(--color-fg-primary)" }}
        >
          <span
            className="font-semibold"
            style={{ color: "var(--color-status-alarm-fg)" }}
          >
            {data.count} {data.count === 1 ? "machine needs" : "machines need"} your
            attention
          </span>
          {" — start with "}
          <span className="font-semibold" style={{ color: "var(--color-fg-primary)" }}>
            {top.asset_id}
          </span>
          {" because "}
          {whyText}.
        </p>

        {/* Right: action + dismiss */}
        <div className="flex items-center gap-3 flex-shrink-0 ml-2">
          <button
            type="button"
            onClick={() => setSelectedAssetId(top.asset_id)}
            className="flex items-center gap-1.5 text-xs font-semibold whitespace-nowrap transition-colors hover:opacity-80"
            style={{ color: "var(--color-status-alarm-fg)" }}
            aria-label={`Focus on ${top.asset_id}`}
          >
            Focus {top.asset_id}
            <ArrowRight size={13} aria-hidden="true" />
          </button>

          <button
            type="button"
            onClick={() => setDismissed(true)}
            className="btn-ghost p-1.5"
            style={{ minHeight: "auto", minWidth: "auto" }}
            aria-label="Dismiss this banner"
          >
            <X size={13} aria-hidden="true" />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
