// Copies Pyodide (Python compiled to WebAssembly) into public/pyodide, where the phone app
// loads it from its own files — no network needed to read the record offline.
import { cpSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const from = join(here, '..', 'node_modules', 'pyodide');
const to = join(here, '..', 'public', 'pyodide');
mkdirSync(to, { recursive: true });
for (const f of ['pyodide.asm.mjs', 'pyodide.asm.wasm', 'pyodide.mjs', 'python_stdlib.zip', 'pyodide-lock.json']) {
  cpSync(join(from, f), join(to, f));
}
console.log('pyodide staged in public/pyodide');
