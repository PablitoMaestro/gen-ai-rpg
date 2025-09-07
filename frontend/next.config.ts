import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      // Local development - Supabase
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        pathname: '/storage/v1/object/public/**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        pathname: '/storage/v1/object/public/**',
      },
      // Production - Supabase
      {
        protocol: 'https',
        hostname: '*.supabase.co',
        pathname: '/storage/v1/object/public/**',
      },
      // Production - Backend API (Scaleway or other hosting)
      {
        protocol: 'https',
        hostname: '*.scw.cloud',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '*.scaleway.com',
        pathname: '/**',
      },
      // AI service images (Nano Banana, etc.)
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '*.googleapis.com',
        pathname: '/**',
      },
      // Any backend domain for character images
      {
        protocol: 'https',
        hostname: '**',
        pathname: '/api/characters/**',
      },
      // Placeholder service for fallback images
      {
        protocol: 'https',
        hostname: 'via.placeholder.com',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
