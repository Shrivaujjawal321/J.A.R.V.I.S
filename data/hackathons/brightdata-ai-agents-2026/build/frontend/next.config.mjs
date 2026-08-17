/** @type {import('next').NextConfig} */
const nextConfig = {
  // React 19 strict mode — catches issues early
  reactStrictMode: true,

  // Direct browser → Fly.io SSE (no Next API proxy)
  // See: research/16_sse_streaming_patterns.md §3a
  async headers() {
    return [
      {
        // Security headers for the frontend
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },

  // Image optimization
  images: {
    formats: ["image/avif", "image/webp"],
  },
};

export default nextConfig;
