import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  // the ICU firmware's own log files (tests/fixtures/icu-drive), read as ?inline data URLs
  assetsInclude: ['**/*.bin'],
  test: { include: ['tests/**/*.test.ts'], environment: 'node' },
  resolve: { conditions: ['browser'] },
});
