import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow 127.0.0.1 as a dev origin so Playwright + local tooling can load
  // JS chunks without being blocked by the cross-origin dev-resource guard
  allowedDevOrigins: ["127.0.0.1"],
};

export default nextConfig;
