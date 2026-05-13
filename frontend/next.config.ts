import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ['172.16.21.161'],
  
  // Proxy API requests to the FastAPI backend during development.
  // This avoids CORS issues entirely: the browser only ever talks to
  // localhost:3000, and Next.js forwards /api/v1/* to localhost:8000.
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: "http://127.0.0.1:8000/api/v1/:path*",
      },
      {
        source: "/health",
        destination: "http://127.0.0.1:8000/health",
      },
    ];
  },
};

export default nextConfig;
