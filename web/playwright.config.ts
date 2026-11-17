import { defineConfig, devices } from "@playwright/test";

// Runs against the production build (npm run build first). The API is mocked in each test,
// so these tests do not need the Python API running.
export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  reporter: "list",
  use: { baseURL: "http://localhost:3100", trace: "off" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "celular", use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: "npx next start -p 3100",
    url: "http://localhost:3100",
    reuseExistingServer: !process.env.CI,
  },
});
