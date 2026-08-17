"use client";

import React from "react";
import {
  Group as PanelGroup,
  Panel,
  Separator as PanelResizeHandle,
} from "react-resizable-panels";
import { AlertsFeed } from "./alerts-feed";
import { AssetStrip } from "./asset-strip";
import { CenterPanel } from "./center-panel";
import { CopilotPanel } from "./copilot-panel";
import { StartHereBanner } from "./start-here-banner";
import { useEdithStore, type UserRole } from "@/store/edith-store";

const ROLES: UserRole[] = ["Operator", "Engineer", "Manager"];

function ResizeHandle() {
  return (
    <PanelResizeHandle
      className="w-1 mx-0.5 rounded-full transition-colors duration-150 cursor-col-resize"
      style={{ background: "oklch(100% 0 0 / 0.06)" }}
      aria-label="Resize panel"
    />
  );
}

export function CockpitView() {
  const { userRole, setUserRole, roleHintSeen, setRoleHintSeen } = useEdithStore();

  return (
    <div
      className="h-screen w-screen flex flex-col overflow-hidden"
      style={{ background: "var(--color-bg-base)" }}
    >
      {/* Top header bar */}
      <header
        className="flex items-center gap-4 px-5 py-3 border-b flex-shrink-0"
        style={{
          background: "var(--color-glass-base)",
          backdropFilter: "blur(16px)",
          borderColor: "var(--color-glass-border)",
        }}
      >
        {/* Brand */}
        <div className="flex items-center gap-2.5">
          <span
            className="font-bold tracking-wider text-sm"
            style={{
              color: "var(--color-accent-400)",
              fontFamily: "var(--font-mono)",
              letterSpacing: "0.18em",
            }}
          >
            EDITH
          </span>
          <span
            className="label-caps hidden sm:inline"
            style={{ color: "var(--color-fg-faint)" }}
          >
            Maintenance Intelligence
          </span>
        </div>

        <div
          className="h-4 w-px hidden sm:block"
          style={{ background: "var(--color-border)" }}
          aria-hidden="true"
        />

        {/* Context breadcrumb */}
        <div className="flex items-center gap-1.5">
          <span
            className="label-caps"
            style={{ color: "var(--color-fg-faint)" }}
          >
            Hot Strip Mill
          </span>
          <span style={{ color: "var(--color-fg-faint)" }} aria-hidden="true">
            /
          </span>
          <span
            className="label-caps"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            Plant Monitoring
          </span>
        </div>

        <div className="ml-auto flex items-center gap-3 flex-wrap">
          {/* G5-frontend: role selector */}
          <div className="flex flex-col items-end gap-0.5">
            <div
              className="flex items-center gap-1 rounded-full overflow-hidden"
              role="group"
              aria-label="Alert role filter"
              style={{
                background: "var(--color-bg-elevated)",
                border: "1px solid var(--color-border)",
                padding: "2px",
              }}
            >
              {ROLES.map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => {
                    setUserRole(r);
                    setRoleHintSeen();
                  }}
                  aria-pressed={userRole === r}
                  className="transition-colors"
                  style={{
                    padding: "2px 8px",
                    borderRadius: "9999px",
                    fontSize: "10px",
                    fontFamily: "var(--font-mono)",
                    fontWeight: 600,
                    letterSpacing: "0.04em",
                    textTransform: "uppercase",
                    cursor: "pointer",
                    border: "none",
                    background: userRole === r
                      ? "var(--color-accent-400)"
                      : "transparent",
                    color: userRole === r
                      ? "var(--color-fg-on-accent)"
                      : "var(--color-fg-faint)",
                    transition: "background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out)",
                  }}
                >
                  {r}
                </button>
              ))}
            </div>
            {/* One-time hint on first use */}
            {!roleHintSeen && (
              <span
                className="text-[10px]"
                style={{ color: "var(--color-fg-faint)", fontFamily: "var(--font-sans)" }}
                aria-live="polite"
              >
                Alerts are routed by role — managers see only serious events.
              </span>
            )}
          </div>

          <span
            className="label-caps text-xs hidden md:block"
            style={{ color: "var(--color-fg-faint)" }}
          >
            Live feed active
          </span>
          <span
            className="status-dot status-dot--healthy"
            aria-label="System online"
          />
        </div>
      </header>

      {/* START HERE banner — only when ≥2 assets need action (spec §7a) */}
      <StartHereBanner />

      {/* 3-panel cockpit */}
      <main
        className="flex-1 min-h-0 overflow-hidden"
        aria-label="EDITH maintenance cockpit"
      >
        <PanelGroup orientation="horizontal" className="h-full w-full">
          {/* Left panel — asset health strip */}
          <Panel
            defaultSize="18%"
            minSize="14%"
            maxSize="28%"
            id="left"
            aria-label="Asset health strip"
          >
            <div
              className="h-full hud-panel rounded-none border-0 border-r overflow-hidden flex flex-col"
              style={{ borderColor: "var(--color-glass-border)" }}
            >
              <div
                className="px-3 pt-3 pb-2 border-b flex-shrink-0"
                style={{ borderColor: "var(--color-border)" }}
              >
                <h1 className="hud-heading mb-0 border-0 pb-0">Assets</h1>
              </div>
              <AssetStrip />
            </div>
          </Panel>

          <ResizeHandle />

          {/* Center panel — focused asset + verdict + graphs */}
          <Panel
            defaultSize="52%"
            minSize="38%"
            id="center"
            aria-label="Focused asset — diagnosis and sensor monitoring"
          >
            <div
              className="h-full min-w-0 hud-panel rounded-none border-0 overflow-hidden"
              style={{ borderColor: "var(--color-glass-border)" }}
            >
              <CenterPanel />
            </div>
          </Panel>

          <ResizeHandle />

          {/* Right panel — alerts + copilot */}
          <Panel
            defaultSize="30%"
            minSize="24%"
            maxSize="42%"
            id="right"
            aria-label="Active alerts and EDITH copilot"
          >
            <div className="h-full flex flex-col gap-0 overflow-hidden">
              {/* Alerts feed */}
              <div
                className="hud-panel rounded-none border-0 border-b flex-shrink-0"
                style={{
                  borderColor: "var(--color-glass-border)",
                  maxHeight: "42%",
                }}
              >
                <div
                  className="px-3 pt-3 pb-2 border-b"
                  style={{ borderColor: "var(--color-border)" }}
                >
                  <h2 className="hud-heading mb-0 border-0 pb-0">
                    Active Alerts
                  </h2>
                </div>
                <div
                  className="overflow-y-auto"
                  style={{ maxHeight: "calc(100% - 40px)" }}
                >
                  <AlertsFeed />
                </div>
              </div>

              {/* Copilot */}
              <div className="flex-1 min-h-0 overflow-hidden">
                <CopilotPanel />
              </div>
            </div>
          </Panel>
        </PanelGroup>
      </main>
    </div>
  );
}
