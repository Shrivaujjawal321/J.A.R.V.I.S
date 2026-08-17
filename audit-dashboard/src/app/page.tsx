import { Suspense } from "react";
import { HomeClient } from "./home-client";

export default function HomePage() {
  return (
    <Suspense
      fallback={
        <div
          className="flex h-screen items-center justify-center"
          style={{ background: "var(--bg)", color: "var(--text-muted)" }}
        >
          Loading…
        </div>
      }
    >
      <HomeClient />
    </Suspense>
  );
}
