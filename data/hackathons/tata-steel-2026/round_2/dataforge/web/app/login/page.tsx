"use client";

import { useState, useEffect, Suspense, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, useReducedMotion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { Eye, EyeOff, AlertCircle, Loader2 } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/providers/auth-provider";
import { cn } from "@/lib/utils";

type AuthMode = "login" | "signup";

// ── Inner component — uses useSearchParams, must be inside Suspense ───────────
function LoginForm() {
  const prefersReduced = useReducedMotion();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { session } = useAuth();

  const next = searchParams.get("next") ?? "/";

  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Redirect away when already authenticated — must be after all hook calls
  useEffect(() => {
    if (session) {
      router.replace(next);
    }
  }, [session, router, next]);

  // While session is loading or redirect is in progress, render nothing
  if (session) return null;

  const handleEmailAuth = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    setLoading(true);

    try {
      if (mode === "signup") {
        const { error: signUpErr } = await supabase.auth.signUp({
          email,
          password,
          options: {
            // Override Supabase's default Site URL so confirmation links return
            // to THIS origin (prod/preview/local) instead of localhost:3000.
            emailRedirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}`,
          },
        });
        if (signUpErr) throw signUpErr;
        setSuccessMsg(
          "Account created. If email confirmation is on, check your inbox — otherwise you can sign in now."
        );
      } else {
        const { error: signInErr } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (signInErr) throw signInErr;
        router.replace(next);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Authentication failed.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100dvh-3.5rem)] flex items-center justify-center px-4 py-12">
      <motion.div
        initial={prefersReduced ? false : { opacity: 0, y: 16, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: "spring", stiffness: 320, damping: 28 }}
        className="w-full max-w-sm flex flex-col gap-8"
      >
        {/* Logo */}
        <div className="flex flex-col items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center text-white text-sm font-bold font-mono flex-shrink-0"
            style={{
              background:
                "linear-gradient(135deg, var(--color-accent-400), var(--color-accent-700))",
            }}
            aria-hidden="true"
          >
            E
          </div>
          <div className="flex flex-col items-center gap-1">
            <h1
              className="text-xl font-semibold font-mono tracking-tight"
              style={{ color: "var(--color-fg-primary)" }}
            >
              E.D.I.T.H
            </h1>
            <p className="text-sm text-center" style={{ color: "var(--color-fg-secondary)" }}>
              {mode === "login" ? "Sign in to your account" : "Create an account"}
            </p>
          </div>
        </div>

        {/* Card */}
        <div
          className="rounded-2xl border p-6 flex flex-col gap-5"
          style={{
            backgroundColor: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
          }}
        >
          {/* Mode toggle */}
          <div
            className="flex rounded-lg p-1 gap-1"
            style={{ backgroundColor: "var(--color-bg-elevated)" }}
            role="tablist"
            aria-label="Authentication mode"
          >
            {(["login", "signup"] as const).map((m) => (
              <button
                key={m}
                role="tab"
                aria-selected={mode === m}
                onClick={() => {
                  setMode(m);
                  setError(null);
                  setSuccessMsg(null);
                }}
                className={cn(
                  "flex-1 py-1.5 rounded-md text-xs font-medium transition-colors duration-100",
                  "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]"
                )}
                style={
                  mode === m
                    ? {
                        backgroundColor: "var(--color-bg-card)",
                        color: "var(--color-fg-primary)",
                      }
                    : { color: "var(--color-fg-tertiary)" }
                }
              >
                {m === "login" ? "Sign in" : "Sign up"}
              </button>
            ))}
          </div>

          {/* Email + password form */}
          <form onSubmit={handleEmailAuth} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="auth-email"
                className="text-xs font-medium"
                style={{ color: "var(--color-fg-secondary)" }}
              >
                Email address
              </label>
              <input
                id="auth-email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                className={cn(
                  "w-full px-3 py-2.5 rounded-lg text-sm font-sans transition-colors duration-150",
                  "focus:outline-none"
                )}
                style={{
                  backgroundColor: "var(--color-bg-elevated)",
                  border: "1px solid var(--color-border)",
                  color: "var(--color-fg-primary)",
                }}
                aria-required="true"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="auth-password"
                className="text-xs font-medium"
                style={{ color: "var(--color-fg-secondary)" }}
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="auth-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete={mode === "signup" ? "new-password" : "current-password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  placeholder={mode === "signup" ? "Min. 6 characters" : "Your password"}
                  className={cn(
                    "w-full pl-3 pr-10 py-2.5 rounded-lg text-sm font-sans transition-colors duration-150",
                    "focus:outline-none"
                  )}
                  style={{
                    backgroundColor: "var(--color-bg-elevated)",
                    border: "1px solid var(--color-border)",
                    color: "var(--color-fg-primary)",
                  }}
                  aria-required="true"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)] rounded"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff
                      className="w-4 h-4"
                      style={{ color: "var(--color-fg-tertiary)" }}
                      aria-hidden="true"
                    />
                  ) : (
                    <Eye
                      className="w-4 h-4"
                      style={{ color: "var(--color-fg-tertiary)" }}
                      aria-hidden="true"
                    />
                  )}
                </button>
              </div>
            </div>

            {/* Error / success messages */}
            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  key="error"
                  initial={prefersReduced ? false : { opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex items-start gap-2 text-xs px-3 py-2.5 rounded-lg border"
                  style={{
                    color: "var(--color-status-critical-fg)",
                    backgroundColor: "var(--color-status-critical-bg)",
                    borderColor: "var(--color-status-critical-border)",
                  }}
                  role="alert"
                  aria-live="polite"
                >
                  <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" aria-hidden="true" />
                  {error}
                </motion.div>
              )}
              {successMsg && (
                <motion.div
                  key="success"
                  initial={prefersReduced ? false : { opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="text-xs px-3 py-2.5 rounded-lg border"
                  style={{
                    color: "var(--color-status-healthy-fg)",
                    backgroundColor: "var(--color-status-healthy-bg)",
                    borderColor: "var(--color-status-healthy-border)",
                  }}
                  role="status"
                  aria-live="polite"
                >
                  {successMsg}
                </motion.div>
              )}
            </AnimatePresence>

            <button
              type="submit"
              disabled={loading || !email || !password}
              className={cn(
                "w-full py-2.5 rounded-lg text-sm font-semibold transition-all duration-150",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)] focus-visible:ring-offset-2",
                "focus-visible:ring-offset-[var(--color-bg-card)]",
                loading || !email || !password
                  ? "opacity-50 cursor-not-allowed"
                  : "cursor-pointer hover:brightness-110"
              )}
              style={{
                backgroundColor: "var(--color-accent-400)",
                color: "var(--color-fg-on-accent)",
              }}
              aria-disabled={loading || !email || !password}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  {mode === "login" ? "Signing in…" : "Creating account…"}
                </span>
              ) : mode === "login" ? (
                "Sign in"
              ) : (
                "Create account"
              )}
            </button>
          </form>
        </div>

        {/* Back to app */}
        <p className="text-xs text-center" style={{ color: "var(--color-fg-faint)" }}>
          <Link
            href="/"
            className="underline transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)] rounded"
            style={{ color: "var(--color-fg-tertiary)" }}
          >
            Continue without signing in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}

// ── Suspense wrapper skeleton ─────────────────────────────────────────────────
function LoginSkeleton() {
  return (
    <div className="min-h-[calc(100dvh-3.5rem)] flex items-center justify-center">
      <div
        className="w-full max-w-sm h-[420px] rounded-2xl animate-pulse"
        style={{ backgroundColor: "var(--color-bg-card)" }}
        aria-label="Loading login page"
        aria-busy="true"
      />
    </div>
  );
}

// ── Page export — wraps LoginForm in Suspense for useSearchParams ─────────────
export default function LoginPage() {
  return (
    <Suspense fallback={<LoginSkeleton />}>
      <LoginForm />
    </Suspense>
  );
}
