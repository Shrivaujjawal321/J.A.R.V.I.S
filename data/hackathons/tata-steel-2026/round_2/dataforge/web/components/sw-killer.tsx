"use client";

import { useEffect } from "react";

/**
 * Unregisters any rogue service worker on this origin and clears its caches.
 *
 * localhost:3000 is a shared origin — a service worker registered by a PREVIOUS
 * app on this port keeps intercepting fetches and serving stale JS bundles, which
 * makes code fixes appear not to take effect. This self-heals that: on load it
 * unregisters all SWs and deletes all caches, so the page always runs fresh code.
 */
export function SwKiller() {
  useEffect(() => {
    if (typeof navigator !== "undefined" && "serviceWorker" in navigator) {
      navigator.serviceWorker
        .getRegistrations()
        .then((regs) => {
          if (regs.length === 0) return;
          Promise.all(regs.map((r) => r.unregister())).then(() => {
            // A controlled page stays controlled until reload — force one fresh load.
            if (navigator.serviceWorker.controller) {
              window.location.reload();
            }
          });
        })
        .catch(() => {});
    }
    if (typeof window !== "undefined" && "caches" in window) {
      caches
        .keys()
        .then((keys) => Promise.all(keys.map((k) => caches.delete(k))))
        .catch(() => {});
    }
  }, []);

  return null;
}
