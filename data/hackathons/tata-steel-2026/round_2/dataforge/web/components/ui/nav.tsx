"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { LogIn, LogOut, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { fetchQuota } from "@/lib/api";
import { UploadCounter } from "@/components/ui/upload-counter";
import { useAuth } from "@/providers/auth-provider";

// ─── Avatar / auth slot ───────────────────────────────────────────────────────
function AuthSlot() {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  if (loading) {
    // Skeleton pill while auth resolves — prevents layout shift
    return (
      <div
        className="w-7 h-7 rounded-full animate-pulse"
        style={{ backgroundColor: "var(--color-bg-elevated)" }}
        aria-hidden="true"
      />
    );
  }

  if (!user) {
    return (
      <Link
        href={`/login?next=${encodeURIComponent(pathname)}`}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors duration-100",
          "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]"
        )}
        style={{
          backgroundColor: "var(--color-bg-elevated)",
          borderColor: "var(--color-border)",
          color: "var(--color-fg-secondary)",
        }}
        aria-label="Sign in to E.D.I.T.H"
      >
        <LogIn className="w-3.5 h-3.5" aria-hidden="true" />
        <span className="hidden sm:inline">Sign in</span>
      </Link>
    );
  }

  // Derive initials for avatar
  const email = user.email ?? "";
  const displayName = user.user_metadata?.full_name ?? user.user_metadata?.name ?? email;
  const initials = displayName
    .split(" ")
    .map((w: string) => w[0] ?? "")
    .join("")
    .toUpperCase()
    .slice(0, 2) || email.slice(0, 2).toUpperCase();

  const avatarUrl = user.user_metadata?.avatar_url as string | undefined;

  return (
    <div className="flex items-center gap-2">
      {/* Avatar button — opens a minimal dropdown */}
      <div className="relative group">
        <button
          className={cn(
            "w-7 h-7 rounded-full flex items-center justify-center overflow-hidden",
            "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]",
            "transition-opacity duration-100"
          )}
          style={{
            background: avatarUrl
              ? undefined
              : "linear-gradient(135deg, var(--color-accent-400), var(--color-accent-700))",
          }}
          aria-label={`Signed in as ${email}. Click for options.`}
          aria-haspopup="true"
        >
          {avatarUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={avatarUrl}
              alt={displayName}
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          ) : (
            <span className="text-white text-xs font-bold font-mono" aria-hidden="true">
              {initials}
            </span>
          )}
        </button>

        {/* Hover / focus dropdown */}
        <div
          className={cn(
            "absolute right-0 top-full mt-2 w-52 rounded-xl border overflow-hidden z-50",
            "opacity-0 invisible group-hover:opacity-100 group-hover:visible",
            "group-focus-within:opacity-100 group-focus-within:visible",
            "transition-all duration-150 origin-top-right scale-95 group-hover:scale-100 group-focus-within:scale-100"
          )}
          style={{
            backgroundColor: "var(--color-bg-card)",
            borderColor: "var(--color-border)",
            boxShadow: "var(--shadow-overlay, 0 8px 32px oklch(0% 0 0 / 0.4))",
          }}
          role="menu"
          aria-label="User menu"
        >
          {/* User info */}
          <div
            className="px-4 py-3 border-b flex items-center gap-3"
            style={{ borderColor: "var(--color-border-subtle)" }}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden"
              style={{
                background: avatarUrl
                  ? undefined
                  : "linear-gradient(135deg, var(--color-accent-400), var(--color-accent-700))",
              }}
            >
              {avatarUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={avatarUrl}
                  alt={displayName}
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              ) : (
                <span className="text-white text-xs font-bold font-mono" aria-hidden="true">
                  {initials}
                </span>
              )}
            </div>
            <div className="flex flex-col min-w-0">
              {displayName !== email && (
                <span
                  className="text-xs font-medium truncate"
                  style={{ color: "var(--color-fg-primary)" }}
                >
                  {displayName}
                </span>
              )}
              <span
                className="text-xs truncate font-mono"
                style={{ color: "var(--color-fg-tertiary)" }}
              >
                {email}
              </span>
            </div>
          </div>

          {/* Profile link */}
          <Link
            href="/datasets"
            role="menuitem"
            className={cn(
              "flex items-center gap-2.5 px-4 py-2.5 text-xs transition-colors duration-75",
              "focus:outline-none focus-visible:ring-inset focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]"
            )}
            style={{ color: "var(--color-fg-secondary)" }}
            onClick={() => router.push("/datasets")}
          >
            <User className="w-3.5 h-3.5" aria-hidden="true" />
            My datasets
          </Link>

          {/* Sign out */}
          <button
            role="menuitem"
            onClick={signOut}
            className={cn(
              "w-full flex items-center gap-2.5 px-4 py-2.5 text-xs transition-colors duration-75",
              "focus:outline-none focus-visible:ring-inset focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]",
              "hover:bg-[var(--color-status-critical-bg)]"
            )}
            style={{ color: "var(--color-status-critical-fg)" }}
            aria-label="Sign out of E.D.I.T.H"
          >
            <LogOut className="w-3.5 h-3.5" aria-hidden="true" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Nav ──────────────────────────────────────────────────────────────────────
export function Nav() {
  const pathname = usePathname();
  const { user } = useAuth();

  // Only fetch quota when signed in — avoids a 401 for anon users
  const { data: quota } = useQuery({
    queryKey: ["quota", user?.id],
    queryFn: fetchQuota,
    staleTime: 30_000,
    enabled: user != null,
    retry: 1,
  });

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--color-border-subtle)] bg-[oklch(8%_0.018_250/0.85)] backdrop-blur-xl">
      <nav
        className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between gap-4"
        aria-label="Main navigation"
      >
        {/* E.D.I.T.H wordmark */}
        <Link
          href="/"
          className="flex items-center gap-2.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)] rounded"
          aria-label="E.D.I.T.H — go to home"
        >
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold font-mono flex-shrink-0"
            style={{
              background: "linear-gradient(135deg, var(--color-accent-400), var(--color-accent-700))",
            }}
            aria-hidden="true"
          >
            E
          </div>
          <span
            className="font-semibold text-sm tracking-tight font-mono"
            style={{ color: "var(--color-fg-primary)" }}
          >
            E.D.I.T.H
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1" role="list">
          {[
            { href: "/", label: "Analyze" },
            { href: "/datasets", label: "Datasets" },
          ].map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              role="listitem"
              className={cn(
                "px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors duration-100",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-400)]",
                pathname === href
                  ? "bg-[var(--color-bg-elevated)] text-[var(--color-fg-primary)]"
                  : "text-[var(--color-fg-secondary)] hover:text-[var(--color-fg-primary)] hover:bg-[var(--color-bg-elevated)]"
              )}
              aria-current={pathname === href ? "page" : undefined}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Right slot: upload counter (when signed in) + auth */}
        <div className="flex items-center gap-3">
          {quota && user && <UploadCounter quota={quota} />}
          <AuthSlot />
        </div>
      </nav>
    </header>
  );
}
