/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    if (isServer) {
      // better-sqlite3 is a native module — keep it external on the server
      config.externals = [...(config.externals || []), 'better-sqlite3'];
    }

    // Phaser uses browser globals; exclude it from SSR bundle
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
      };
    }

    return config;
  },
};

export default nextConfig;
