// The record's own rules, on the phone: the same tools/rx7.py the desktop runs, loaded into
// Python compiled to WebAssembly (Pyodide). The phone never reimplements a rule — it hands
// rx7.py the record's files and asks for `export_data()` and `inbox_entry()`, exactly as
// the desktop does through a terminal.

import type { PyodideAPI } from 'pyodide';
import type { AnswerKind, Snapshot } from '../model';

let engine: Promise<PyodideAPI> | null = null;

const HELPERS = `
import json, sys
sys.path.insert(0, '/rx7/tools')
import rx7

def rx7_export():
    rx7._TREE = None
    return json.dumps(rx7.export_data())

def rx7_answer(area, target, device, kind, choice, text, context, at):
    found = [a for a in rx7.areas() if a.name == area]
    if not found:
        raise ValueError(f"no area named {area}")
    a = found[0]
    k, row = rx7.resolve_target(a, target, kind)
    why = rx7.check_choice(k, row, choice)
    if why:
        raise ValueError(why)
    iid, body = rx7.inbox_entry(target, device, k, choice, text, context, at)
    return json.dumps([rx7.rel(a), iid, body, k])
`;

/** Pyodide's files are served from the app itself (public/pyodide, staged by scripts/stage-core.mjs). */
export function loadEngine(indexURL = '/pyodide/'): Promise<PyodideAPI> {
  engine ??= import('pyodide').then(({ loadPyodide }) => loadPyodide({ indexURL, stdout: () => {}, stderr: () => {} }));
  return engine;
}

function reset(py: PyodideAPI, files: Map<string, string>) {
  const fs = py.FS;
  const wipe = (dir: string) => {
    for (const name of fs.readdir(dir) as string[]) {
      if (name === '.' || name === '..') continue;
      const p = `${dir}/${name}`;
      if (fs.isDir(fs.stat(p).mode)) {
        wipe(p);
        fs.rmdir(p);
      } else fs.unlink(p);
    }
  };
  if (fs.analyzePath('/rx7').exists) wipe('/rx7');
  else fs.mkdir('/rx7');
  for (const [path, text] of files) {
    const full = `/rx7/${path}`;
    fs.mkdirTree(full.slice(0, full.lastIndexOf('/')));
    fs.writeFile(full, text, { encoding: 'utf8' });
  }
  // A fresh rx7.py each time: the phone always runs the version the record was written with.
  py.runPython(`import sys\nsys.modules.pop('rx7', None)`);
  py.runPython(HELPERS);
}

/** The record as rx7.py exports it, from the given files (paths relative to the tree). */
export async function exportRecord(files: Map<string, string>, indexURL?: string): Promise<Snapshot> {
  const py = await loadEngine(indexURL);
  reset(py, files);
  return JSON.parse(py.globals.get('rx7_export')()) as Snapshot;
}

export interface InboxFile {
  areaPath: string;
  id: string;
  body: string;
  kind: AnswerKind;
}

/** One answer's file, checked and written by rx7.py's own inbox_entry(). Throws its reason. */
export async function inboxFile(
  area: string, target: string, kind: AnswerKind | '', choice: string, text: string, context: string, at: string,
): Promise<InboxFile> {
  const py = await loadEngine();
  try {
    const out = py.globals.get('rx7_answer')(area, target, 'phone', kind, choice, text, context, at);
    const [areaPath, id, body, resolved] = JSON.parse(out) as [string, string, string, AnswerKind];
    return { areaPath, id, body, kind: resolved };
  } catch (e) {
    const msg = String(e);
    const why = msg.match(/ValueError: (.*)/);
    throw new Error(why ? why[1] : msg);
  }
}
