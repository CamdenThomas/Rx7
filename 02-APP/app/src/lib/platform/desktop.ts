// The desktop app: the tree is on this PC. Reading is `rx7.py export`, saving is
// `rx7.py answer` plus a commit of that one file, and git keeps it in step with GitHub.
// All of it happens in the Rust shell (src-tauri/src/desktop).

import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { openUrl } from '@tauri-apps/plugin-opener';
import type { Answer, Commit, Snapshot } from '../model';
import type { Applied, ClaudeHandle, ClaudeLine, ClaudeMode, ClaudeOpts, Draft, Platform, SaveOutcome, SyncInfo } from './types';
import { tauriKV } from './storage';

interface GitState {
  branch: string;
  ahead: number;
  behind: number;
  dirty: number;
  online: boolean;
  error: string | null;
}

interface Saved {
  path: string;
  committed: boolean;
  note: string;
}

export async function desktopPlatform(): Promise<Platform> {
  const kv = await tauriKV();
  const root = await kv.get<string>('treeRoot');
  if (root) await invoke('set_tree_root', { path: root }).catch(() => undefined);

  const listeners = new Set<(s: SyncInfo) => void>();
  let info: SyncInfo = { online: true, busy: false, waiting: 0 };
  const publish = (next: Partial<SyncInfo>) => {
    info = { ...info, ...next };
    listeners.forEach((l) => l(info));
  };
  const fromGit = (g: GitState): Partial<SyncInfo> => ({
    online: g.online || info.online,
    waiting: g.ahead,
    dirty: g.dirty,
    error: g.error ?? undefined,
  });
  await listen<GitState>('sync', (e) => publish({ ...fromGit(e.payload), busy: false }));

  // The record is exported again only when something under a data folder or HEAD changed:
  // the 3-minute poll and the sync after a save used to run a 4 s export each, twice (P38).
  let last: { fp: string; snap: Snapshot } | null = null;
  const exportRecord = async (): Promise<Snapshot> => {
    const fp = await invoke<string>('record_fingerprint').catch(() => '');
    if (fp && last && last.fp === fp) return last.snap;
    const snap = JSON.parse(await invoke<string>('record_export')) as Snapshot;
    if (fp) last = { fp, snap };
    publish({ asOf: snap.generated });
    return snap;
  };

  const outcome = (s: Saved): SaveOutcome =>
    s.committed ? { state: 'committed' } : { state: 'saved', note: s.note };

  return {
    kind: 'desktop',
    canClaude: true,
    kv,
    // The last export, kept by the shell in the app's data folder: the screen fills at once
    // while the fresh read runs (plan P32).
    cached: async () => {
      try {
        const text = await invoke<string>('record_cached');
        return text ? (JSON.parse(text) as Snapshot) : null;
      } catch {
        return null;
      }
    },
    async load(sync) {
      if (sync) {
        publish({ busy: true });
        let g: Partial<SyncInfo> = {};
        try {
          const s = await invoke<GitState>('sync');
          g = { ...fromGit(s), online: s.online };
        } catch (e) {
          g = { error: String(e) };
        }
        // busy stays true until the export is in, so the listener that reloads after a
        // sync does not start a second export (plan P38).
        try {
          return await exportRecord();
        } finally {
          publish({ ...g, busy: false });
        }
      }
      invoke<GitState>('sync_state').then((g) => publish(fromGit(g)), () => undefined);
      return exportRecord();
    },
    async save(d: Draft, at: string) {
      const saved = await invoke<Saved>('answer_save', {
        area: d.area, target: d.target, kind: d.kind ?? null,
        choice: d.choice, text: d.text, context: d.context, at,
      });
      publish({ busy: saved.committed });
      return outcome(saved);
    },
    async withdraw(a: Answer) {
      return outcome(await invoke<Saved>('answer_withdraw', { area: a.area, id: a.id }));
    },
    outbox: () => [],
    syncInfo: () => info,
    onSync(l) {
      listeners.add(l);
      return () => listeners.delete(l);
    },
    commits: (path, n = 20) => invoke<Commit[]>('git_log', { path: path ?? null, n }),
    applyMechanical: (area: string) => invoke<Applied>('record_apply', { area }),
    async claude(mode: ClaudeMode, prompt: string, session: string | null, onLine: (e: ClaudeLine) => void, opts: ClaudeOpts = {}) {
      const id = `c${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
      const unlisten = await listen<string>(`claude:${id}`, (e) => {
        let line: ClaudeLine;
        try {
          line = JSON.parse(e.payload);
        } catch {
          line = { type: 'stderr', text: e.payload };
        }
        onLine(line);
        if (line.type === 'exit') unlisten();
      });
      try {
        await invoke('claude_start', { id, mode, prompt, session, opts });
      } catch (e) {
        unlisten();
        throw e;
      }
      const handle: ClaudeHandle = { id, stop: () => invoke('claude_stop', { id }) };
      return handle;
    },
    open: (url) => void openUrl(url),
    treeRoot: () => invoke<string>('tree_root'),
    async setTreeRoot(path: string) {
      const set = await invoke<string>('set_tree_root', { path });
      await kv.set('treeRoot', set);
      return set;
    },
    photo: (path) => `photo://localhost/${path.split('/').map(encodeURIComponent).join('/')}`,
  };
}
