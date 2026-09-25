import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// Tauri serves the built files on the desktop and on the phone; in development it points at
// this server. The fixed port is what src-tauri/tauri.conf.json expects.
export default defineConfig({
  plugins: [svelte()],
  clearScreen: false,
  server: { port: 5173, strictPort: true },
  optimizeDeps: { exclude: ['pyodide'] },
  build: { target: 'es2022', chunkSizeWarningLimit: 900 },
});
