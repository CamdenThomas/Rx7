import { defineConfig } from '@playwright/test';

// The app in Chromium against the dev server: the web build (a copy of the record, a
// stand-in Claude) for the screens, and the phone build against a stand-in GitHub for the
// phone's whole path — fetch, Python in WebAssembly, offline, sending answers.
export default defineConfig({
  testDir: 'e2e',
  timeout: 90_000,
  fullyParallel: false,
  workers: 1,
  use: { baseURL: 'http://localhost:5173', reducedMotion: 'reduce' },
  webServer: {
    command: 'npm run fixture && npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120_000,
  },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 900 } } },
    { name: 'phone', use: { viewport: { width: 412, height: 915 }, hasTouch: true, isMobile: true } },
  ],
});
