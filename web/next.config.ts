import type { NextConfig } from "next";

// The API address is baked into the site at build time. On Netlify, a missing value would
// silently point the site at localhost, so the build stops with a clear message instead.
if (process.env.NETLIFY && !process.env.NEXT_PUBLIC_API_URL) {
  throw new Error("Defina NEXT_PUBLIC_API_URL no Netlify (endereço da API no Render) antes do deploy.");
}

// Every page is static, so the build exports plain HTML to `out/` (no server, no Netlify plugin).
// next/image has no optimizing server in that mode, so images are served as they are.
const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true, // each page becomes folder/index.html, which every static host serves without rules
};

export default nextConfig;
