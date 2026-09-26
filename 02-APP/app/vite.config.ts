import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { defineConfig, type Plugin } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

/** The dev server hands out the test copy of the record from fixture/ (npm run fixture), so
 *  it is never part of public/ and never bundled into an installed app (plan P42). */
function fixture(): Plugin {
  const dir = join(__dirname, 'fixture');
  const serve = (server: { middlewares: { use: (p: string, h: (req: any, res: any, next: () => void) => void) => void } }) =>
    server.middlewares.use('/fixture/', (req, res, next) => {
      const file = join(dir, (req.url ?? '').split('?')[0].replace(/^\/+/, ''));
      if (!file.startsWith(dir) || !existsSync(file)) return next();
      res.setHeader('Content-Type', 'application/json');
      res.end(readFileSync(file));
    });
  return { name: 'rx7-fixture', configureServer: serve, configurePreviewServer: serve };
}

// Tauri serves the built files on the desktop and on the phone; in development it points at
// this server. The fixed port is what src-tauri/tauri.conf.json expects.
export default defineConfig({
  plugins: [svelte(), fixture()],
  clearScreen: false,
  server: { port: 5173, strictPort: true },
  optimizeDeps: { exclude: ['pyodide'] },
  build: { target: 'es2022', chunkSizeWarningLimit: 900 },
});
