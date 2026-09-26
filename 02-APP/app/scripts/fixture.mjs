// A copy of the record for development and tests (the web build reads it instead of the
// tree). Never committed and never bundled: it lives in fixture/ beside the app, and the dev
// server hands it out at /fixture/export.json (vite.config.ts), so the desktop RPM and the
// APK stop carrying a 3.7 MB copy of the record (plan P42).
import { execFileSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const tree = join(here, '..', '..', '..');
const out = join(here, '..', 'fixture', 'export.json');
mkdirSync(dirname(out), { recursive: true });
try {
  execFileSync('python3', [join(tree, 'tools', 'rx7.py'), 'export', '--out', out], { stdio: 'inherit' });
} catch (e) {
  if (e.status !== 1) throw e; // an invalid record still exports
}
console.log(`fixture written: ${out}`);
