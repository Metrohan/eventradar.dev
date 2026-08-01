import { defineConfig } from '@playwright/test'

// Hydration regression tests for the prerender PoC (see
// docs/adr/0006-prerender-poc.md). Run against an already-built +
// prerendered dist/:
//   npm run build && npm run prerender && npx playwright test
export default defineConfig({
  testDir: 'tests',
  timeout: 30000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:4173',
    launchOptions: {
      executablePath: process.env.PRERENDER_CHROMIUM_PATH || undefined,
    },
  },
  webServer: process.env.PLAYWRIGHT_NO_WEBSERVER
    ? undefined
    : {
        command: 'npx vite preview --port 4173 --strictPort',
        url: 'http://localhost:4173',
        reuseExistingServer: true,
        timeout: 30000,
      },
})
