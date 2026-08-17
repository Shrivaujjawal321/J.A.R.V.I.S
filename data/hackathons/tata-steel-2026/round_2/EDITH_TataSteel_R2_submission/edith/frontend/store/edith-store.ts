"use client";

import { create } from "zustand";
import type { AlertEvent, DiagnosisEvent, PSSection, ReasoningTrace, SensorMeta, TickEvent } from "@/lib/types";

/** Role selector for alert routing — G5-frontend */
export type UserRole = "Operator" | "Engineer" | "Manager";

export interface LiveAlert extends AlertEvent {
  id: string; // synthetic dedup key
}

export interface SensorBuffer {
  tag: string;
  meta: SensorMeta;
  /** timestamps (seconds) */
  timestamps: number[];
  /** values */
  values: (number | null)[];
  /** latest status */
  status: string;
  /** latest value */
  latest: number | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: string[];
  riskBand?: string;
  rul?: number | null;
  sections?: PSSection[];
  /** J4/DIFF-04/G7: multi-agent reasoning trace */
  trace?: ReasoningTrace | null;
  /** J11/DIFF-08: reasoning mode pill */
  reasoningMode?: string | null;
  /** J11/DIFF-08: confidence label */
  confidenceLabel?: string | null;
}

interface EdithState {
  // Asset focus
  selectedAssetId: string;
  setSelectedAssetId: (id: string) => void;

  // Role selector — G5-frontend
  userRole: UserRole;
  setUserRole: (r: UserRole) => void;
  roleHintSeen: boolean;
  setRoleHintSeen: () => void;

  // SSE stream state
  streamConnected: boolean;
  setStreamConnected: (v: boolean) => void;

  streamStale: boolean;
  setStreamStale: (v: boolean) => void;

  streamEnded: boolean;
  setStreamEnded: (v: boolean) => void;

  // Live sensor buffers (keyed by tag)
  sensorBuffers: Record<string, SensorBuffer>;
  sensorMetas: SensorMeta[];
  initBuffers: (metas: SensorMeta[]) => void;
  appendTick: (tick: TickEvent) => void;

  // Asset worst status from last tick
  assetStatus: string;

  // Alerts feed (newest first, capped at 50)
  alerts: LiveAlert[];
  addAlert: (alert: AlertEvent) => void;
  dismissAlert: (id: string) => void;

  // Diagnosis cards from SSE
  diagnosis: DiagnosisEvent | null;
  setDiagnosis: (d: DiagnosisEvent) => void;

  // Copilot
  chatMessages: ChatMessage[];
  chatProcessing: boolean;
  addChatMessage: (msg: ChatMessage) => void;
  setChatProcessing: (v: boolean) => void;

  // Replay speed
  replaySpeed: number;
  setReplaySpeed: (s: number) => void;

  // Reset (when switching asset)
  resetStream: () => void;
}

const WINDOW = 900; // keep last 900 data points per sensor

export const useEdithStore = create<EdithState>((set, get) => ({
  selectedAssetId: "HSM.F3.WR.BRG01",
  setSelectedAssetId: (id) => {
    if (id !== get().selectedAssetId) {
      get().resetStream();
      set({ selectedAssetId: id });
    }
  },

  // Role selector — G5-frontend (default Engineer)
  userRole: "Engineer",
  setUserRole: (r) => set({ userRole: r }),
  roleHintSeen: false,
  setRoleHintSeen: () => set({ roleHintSeen: true }),

  streamConnected: false,
  setStreamConnected: (v) => set({ streamConnected: v }),

  streamStale: false,
  setStreamStale: (v) => set({ streamStale: v }),

  streamEnded: false,
  setStreamEnded: (v) => set({ streamEnded: v }),

  sensorBuffers: {},
  sensorMetas: [],
  initBuffers: (metas) => {
    const buffers: Record<string, SensorBuffer> = {};
    for (const m of metas) {
      buffers[m.tag] = {
        tag: m.tag,
        meta: m,
        timestamps: [],
        values: [],
        status: "normal",
        latest: null,
      };
    }
    set({ sensorBuffers: buffers, sensorMetas: metas });
  },

  appendTick: (tick) => {
    const ts = typeof tick.ts === "number" ? tick.ts : Date.parse(String(tick.ts)) / 1000;
    const buffers = { ...get().sensorBuffers };
    for (const tag of Object.keys(tick.values)) {
      if (!buffers[tag]) continue;
      const buf = { ...buffers[tag] };
      const tArr = [...buf.timestamps, ts];
      const vArr = [...buf.values, tick.values[tag]];
      // sliding window
      if (tArr.length > WINDOW) {
        tArr.splice(0, tArr.length - WINDOW);
        vArr.splice(0, vArr.length - WINDOW);
      }
      buf.timestamps = tArr;
      buf.values = vArr;
      buf.status = tick.status[tag] ?? buf.status;
      buf.latest = tick.values[tag] ?? buf.latest;
      buffers[tag] = buf;
    }
    set({ sensorBuffers: buffers, assetStatus: tick.worst });
  },

  assetStatus: "normal",

  alerts: [],
  addAlert: (alert) => {
    const id = `${alert.ts}-${alert.sensor}-${alert.row}`;
    set((s) => {
      // deduplicate
      if (s.alerts.some((a) => a.id === id)) return {};
      const next = [{ ...alert, id }, ...s.alerts].slice(0, 50);
      return { alerts: next };
    });
  },
  dismissAlert: (id) =>
    set((s) => ({ alerts: s.alerts.filter((a) => a.id !== id) })),

  diagnosis: null,
  setDiagnosis: (d) => set({ diagnosis: d }),

  chatMessages: [],
  chatProcessing: false,
  addChatMessage: (msg) =>
    set((s) => ({ chatMessages: [...s.chatMessages, msg] })),
  setChatProcessing: (v) => set({ chatProcessing: v }),

  replaySpeed: 8,
  setReplaySpeed: (s) => set({ replaySpeed: s }),

  resetStream: () =>
    set({
      sensorBuffers: {},
      sensorMetas: [],
      alerts: [],
      diagnosis: null,
      assetStatus: "normal",
      streamConnected: false,
      streamStale: false,
      streamEnded: false,
    }),
}));
