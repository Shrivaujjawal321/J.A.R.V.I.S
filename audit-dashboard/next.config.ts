import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/audit/:path*",
        destination: "http://127.0.0.1:8765/v1/audit/:path*",
      },
      {
        source: "/api/health",
        destination: "http://127.0.0.1:8765/health",
      },
    ];
  },
};

export default nextConfig;
