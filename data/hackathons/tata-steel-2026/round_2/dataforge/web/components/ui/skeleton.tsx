import { cn } from "@/lib/utils";
import type { ComponentProps } from "react";

export function Skeleton({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-lg bg-[oklch(20%_0.006_250)]",
        className
      )}
      {...props}
    />
  );
}
