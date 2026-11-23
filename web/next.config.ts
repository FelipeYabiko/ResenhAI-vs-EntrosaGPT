import type { NextConfig } from "next";

// The API address is baked into the site at build time. On Netlify, a missing value would
// silently point the site at localhost, so the build stops with a clear message instead.
if (process.env.NETLIFY && !process.env.NEXT_PUBLIC_API_URL) {
  throw new Error("Defina NEXT_PUBLIC_API_URL no Netlify (endereço da API no Render) antes do deploy.");
}

const nextConfig: NextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
