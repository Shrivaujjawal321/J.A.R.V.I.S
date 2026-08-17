"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { Upload, FileSpreadsheet, X, LogIn } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn, formatFileSize } from "@/lib/utils";
import { UploadCounter } from "@/components/ui/upload-counter";
import { useAuth } from "@/providers/auth-provider";
import type { AuditFormData, UploadQuota } from "@/lib/types";

interface UploadZoneProps {
  onSubmit: (data: AuditFormData) => void;
  isLoading: boolean;
  quota?: UploadQuota;
}

export function UploadZone({ onSubmit, isLoading, quota }: UploadZoneProps) {
  const prefersReduced = useReducedMotion();
  const { user, loading: authLoading } = useAuth();
  const pathname = usePathname();
  const [file, setFile] = useState<File | null>(null);

  const isExhausted = quota?.remaining === 0;
  // Gate: unauthenticated users see a sign-in prompt, not the upload form
  const isUnauthenticated = !authLoading && !user;

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".xls"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "application/json": [".json"],
    },
    maxFiles: 1,
    disabled: isLoading || isExhausted || isUnauthenticated,
  });

  const handleSubmit = () => {
    if (!file || isLoading || isExhausted || isUnauthenticated) return;
    onSubmit({ file });
  };

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
  };

  // ── Unauthenticated variant ────────────────────────────────────────────────
  if (isUnauthenticated) {
    return (
      <div className="w-full max-w-2xl mx-auto flex flex-col gap-4">
        <div
          className="relative rounded-2xl border-2 border-dashed p-10 flex flex-col items-center gap-6"
          style={{
            borderColor: "var(--color-border)",
            backgroundColor: "var(--color-surface)",
          }}
          aria-label="Sign in required to upload a dataset"
        >
          <div
            className="w-14 h-14 rounded-xl flex items-center justify-center"
            style={{
              backgroundColor: "var(--color-accent-tint)",
              color: "var(--color-accent-400)",
            }}
          >
            <Upload className="w-6 h-6" aria-hidden="true" />
          </div>
          <div className="flex flex-col items-center gap-2 text-center">
            <p
              className="text-lg font-medium"
              style={{ color: "var(--color-fg)" }}
            >
              Sign in to upload
            </p>
            <p className="text-sm max-w-xs" style={{ color: "var(--color-fg-muted)" }}>
              Create a free account to upload up to 5 datasets and see where yours ranks.
            </p>
          </div>
          <Link
            href={`/login?next=${encodeURIComponent(pathname)}`}
            className={cn(
              "flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-150",
              "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)] focus-visible:ring-offset-2",
              "focus-visible:ring-offset-[var(--color-surface)]"
            )}
            style={{
              backgroundColor: "var(--color-accent-400)",
              color: "var(--color-fg-on-accent)",
            }}
          >
            <LogIn className="w-4 h-4" aria-hidden="true" />
            Sign in to upload
          </Link>
          <p className="text-xs" style={{ color: "var(--color-fg-faint)" }}>
            Accepted formats: CSV, XLSX, JSON &middot; up to 500 MB
          </p>
        </div>
      </div>
    );
  }

  // ── Auth loading skeleton ──────────────────────────────────────────────────
  if (authLoading) {
    return (
      <div className="w-full max-w-2xl mx-auto">
        <div
          className="rounded-2xl border-2 border-dashed p-10 animate-pulse"
          style={{
            borderColor: "var(--color-border-subtle)",
            backgroundColor: "var(--color-surface)",
            minHeight: "200px",
          }}
          aria-label="Loading upload zone"
          aria-busy="true"
        />
      </div>
    );
  }

  // ── Authenticated variant ──────────────────────────────────────────────────
  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col gap-4">

      {/* Drop zone */}
      <motion.div
        initial={prefersReduced ? false : { opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      >
        <div
          {...getRootProps()}
          className={cn(
            "relative rounded-2xl cursor-pointer select-none transition-all duration-150",
            "border-2 border-dashed p-10",
            !file && !isDragActive && !isExhausted
              ? "border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-accent-600)] hover:bg-[oklch(15%_0.008_250)]"
              : "",
            isDragActive
              ? "border-[var(--color-accent-400)] bg-[var(--color-accent-tint)] scale-[1.01]"
              : "",
            file && !isDragActive && !isExhausted
              ? "border-[var(--color-accent-600)] bg-[oklch(15%_0.009_250)]"
              : "",
            (isLoading || isExhausted) ? "opacity-60 cursor-not-allowed" : ""
          )}
          role="button"
          aria-label="File upload area. Drag and drop or click to select a CSV, XLSX, or JSON file."
          tabIndex={0}
        >
          <input {...getInputProps()} aria-label="Upload dataset file" />

          <AnimatePresence mode="wait">
            {!file ? (
              <motion.div
                key="empty"
                initial={prefersReduced ? false : { opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-4 text-center"
              >
                <motion.div
                  animate={
                    isDragActive && !prefersReduced
                      ? { scale: 1.15, rotate: -5 }
                      : { scale: 1, rotate: 0 }
                  }
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  className={cn(
                    "w-14 h-14 rounded-xl flex items-center justify-center",
                    isDragActive
                      ? "bg-[var(--color-accent-tint)] text-[var(--color-accent-400)]"
                      : "bg-[var(--color-surface-2)] text-[var(--color-fg-muted)]"
                  )}
                >
                  <Upload className="w-6 h-6" aria-hidden="true" />
                </motion.div>
                <div>
                  <p className="text-[var(--color-fg)] font-medium text-lg">
                    {isExhausted
                      ? "Upload limit reached"
                      : isDragActive
                      ? "Drop it here"
                      : "Drop your dataset here"}
                  </p>
                  <p className="text-[var(--color-fg-muted)] text-sm mt-1">
                    CSV, XLSX, or JSON &middot; up to 500 MB
                  </p>
                </div>
                {!isExhausted && (
                  <span className="text-xs text-[var(--color-fg-faint)] bg-[var(--color-surface-2)] px-3 py-1 rounded-full">
                    or click to browse
                  </span>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="file"
                initial={prefersReduced ? false : { opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                className="flex items-center gap-4"
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: "var(--color-accent-tint)", color: "var(--color-accent-400)" }}
                >
                  <FileSpreadsheet className="w-6 h-6" aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[var(--color-fg)] font-medium truncate font-mono text-sm">
                    {file.name}
                  </p>
                  <p className="text-[var(--color-fg-muted)] text-xs mt-0.5">
                    {formatFileSize(file.size)}
                  </p>
                </div>
                <button
                  onClick={clearFile}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-[var(--color-fg-faint)] hover:text-[var(--color-fg-muted)] hover:bg-[var(--color-surface-3)] transition-colors duration-100"
                  aria-label="Remove selected file"
                >
                  <X className="w-4 h-4" aria-hidden="true" />
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Upload counter + quota exhausted message */}
      {quota && (
        <div className="flex items-center justify-between gap-3">
          <div className="flex-1">
            {isExhausted && (
              <p
                className="text-sm px-4 py-3 rounded-lg border"
                style={{
                  color: "var(--color-status-critical-fg)",
                  backgroundColor: "var(--color-status-critical-bg)",
                  borderColor: "var(--color-status-critical-border)",
                }}
                role="alert"
              >
                You have reached the 5-dataset upload limit for this hackathon.
              </p>
            )}
          </div>
          <UploadCounter quota={quota} />
        </div>
      )}

      {/* CTA button */}
      <motion.button
        onClick={handleSubmit}
        disabled={!file || isLoading || isExhausted}
        whileTap={prefersReduced ? {} : { scale: 0.98 }}
        className={cn(
          "w-full py-4 rounded-xl font-semibold text-base transition-all duration-150",
          "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg)]",
          file && !isLoading && !isExhausted
            ? "bg-[var(--color-accent-400)] hover:bg-[var(--color-accent-300)] text-[var(--color-fg-on-accent)] cursor-pointer"
            : "bg-[var(--color-surface-2)] text-[var(--color-fg-faint)] cursor-not-allowed"
        )}
        aria-disabled={!file || isLoading || isExhausted}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span
              className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin"
              aria-hidden="true"
              style={{ animation: "spin 600ms linear infinite" }}
            />
            E.D.I.T.H is analyzing…
          </span>
        ) : isExhausted ? (
          "Upload limit reached (5/5)"
        ) : (
          "Analyze with E.D.I.T.H"
        )}
      </motion.button>
    </div>
  );
}
