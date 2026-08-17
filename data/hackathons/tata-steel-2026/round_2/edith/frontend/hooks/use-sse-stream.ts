"use client";

import { useEffect, useRef } from "react";
import { toast } from "sonner";
import { API_BASE } from "@/lib/utils";
import type { AlertEvent, DiagnosisEvent, EndEvent, MetaEvent, TickEvent } from "@/lib/types";
import { useEdithStore } from "@/store/edith-store";

const STALE_TIMEOUT_MS = 8_000;
const RECONNECT_DELAY_MS = 3_000;
const MAX_RECONNECTS = 10;

export function useSseStream(assetId: string, speed: number = 8, role?: string) {
  const {
    initBuffers,
    appendTick,
    addAlert,
    setDiagnosis,
    setStreamConnected,
    setStreamStale,
    setStreamEnded,
  } = useEdithStore();

  const esRef = useRef<EventSource | null>(null);
  const staleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectCountRef = useRef(0);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    reconnectCountRef.current = 0;

    function resetStaleTimer() {
      if (staleTimerRef.current) clearTimeout(staleTimerRef.current);
      setStreamStale(false);
      staleTimerRef.current = setTimeout(() => {
        if (mountedRef.current) setStreamStale(true);
      }, STALE_TIMEOUT_MS);
    }

    function connect() {
      if (!mountedRef.current) return;
      const roleParam = role ? `&role=${encodeURIComponent(role.toLowerCase())}` : "";
      const url = `${API_BASE}/api/stream/${encodeURIComponent(assetId)}?speed=${speed}&window=900&seek_event=true${roleParam}`;
      const es = new EventSource(url);
      esRef.current = es;

      es.addEventListener("meta", (e) => {
        try {
          const data: MetaEvent = JSON.parse((e as MessageEvent).data);
          initBuffers(data.sensors);
          setStreamConnected(true);
          setStreamEnded(false);
          resetStaleTimer();
          reconnectCountRef.current = 0;
        } catch {}
      });

      es.addEventListener("tick", (e) => {
        try {
          const data: TickEvent = JSON.parse((e as MessageEvent).data);
          appendTick(data);
          resetStaleTimer();
        } catch {}
      });

      es.addEventListener("alert", (e) => {
        try {
          const data: AlertEvent = JSON.parse((e as MessageEvent).data);
          addAlert(data);
          const label = data.severity === "ALARM" ? "Alarm" : "Warning";
          toast[data.severity === "ALARM" ? "error" : "warning"](
            `${label}: ${data.sensor}`,
            { description: data.reason, duration: 6000 }
          );
        } catch {}
      });

      es.addEventListener("diagnosis", (e) => {
        try {
          const data: DiagnosisEvent = JSON.parse((e as MessageEvent).data);
          setDiagnosis(data);
        } catch {}
      });

      es.addEventListener("end", (e) => {
        try {
          const _data: EndEvent = JSON.parse((e as MessageEvent).data);
          setStreamEnded(true);
          setStreamConnected(false);
          es.close();
          if (staleTimerRef.current) clearTimeout(staleTimerRef.current);
        } catch {}
      });

      es.onerror = () => {
        if (!mountedRef.current) return;
        setStreamConnected(false);
        es.close();
        if (reconnectCountRef.current < MAX_RECONNECTS) {
          reconnectCountRef.current++;
          setTimeout(connect, RECONNECT_DELAY_MS);
        } else {
          toast.error("Stream disconnected. Reload to reconnect.");
        }
      };
    }

    connect();

    return () => {
      mountedRef.current = false;
      if (staleTimerRef.current) clearTimeout(staleTimerRef.current);
      esRef.current?.close();
      esRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assetId, speed, role]);
}
