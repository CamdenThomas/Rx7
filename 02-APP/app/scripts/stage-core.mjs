// Copies Pyodide (Python compiled to WebAssembly) into public/pyodide, where the phone app
// loads it from its own files — no network needed to read the record offline.
//
// Only the Android build and the browser build need it. A Tauri desktop build sets
// TAURI_ENV_PLATFORM to linux/darwin/windows; then nothing is staged and a stale copy is
// removed, so the desktop RPM stops carrying 13 MB it never runs (plan P42).
import { cpSync, existsSync, mkdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const from = join(here, '..', 'node_modules', 'pyodide');
const to = join(here, '..', 'public', 'pyodide');
const platform = process.env.TAURI_ENV_PLATFORM ?? '';
if (platform && platform !== 'android') {
  if (existsSync(to)) rmSync(to, { recursive: true, force: true });
  console.log(`pyodide not staged for the ${platform} build`);
} else {
  mkdirSync(to, { recursive: true });
  for (const f of ['pyodide.asm.mjs', 'pyodide.asm.wasm', 'pyodide.mjs', 'python_stdlib.zip', 'pyodide-lock.json']) {
    cpSync(join(from, f), join(to, f));
  }
  console.log('pyodide staged in public/pyodide');
}
