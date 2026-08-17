"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: 2, refetchOnWindowFocus: false },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          style: {
            background: "oklch(16% 0.022 250)",
            border: "1px solid oklch(100% 0 0 / 0.09)",
            color: "oklch(96% 0.006 250)",
            fontFamily: "Geist, sans-serif",
            fontSize: "13px",
          },
        }}
      />
    </QueryClientProvider>
  );
}
