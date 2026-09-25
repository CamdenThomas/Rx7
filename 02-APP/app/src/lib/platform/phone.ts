// The Android app. The record comes from GitHub and is kept on the phone, so it reads the
// same with no signal as with full bars (D-403). An answer is saved on the phone the moment
// he saves it, and leaves only when GitHub has committed it — never lost in between.

import type { Answer, Commit, Snapshot } from '../model';
import { exportRecord, inboxFile, loadEngine } from './core';
import { github, GitHubError, wanted, type Fetch, type GitHub, type Repo } from './github';
import type { KV } from './storage';
import type { Draft, Platform, SaveOutcome, SyncInfo } from './types';

/** An answer on its way: written here, not yet committed on GitHub. */
export interface Outgoing {
  op: 'put' | 'delete';
  path: string;
  answer: Answer;
  body?: string;
}

interface FileCache {
  commit: string;
  date: string;
  files: Record<string, { sha: string; text?: string }>;
}

export interface PhoneOptions {
  kv: KV;
  fetch: Fetch;
  api?: string;
  raw?: string;
  pyodide?: string;
  repo?: Omit<Repo, 'token'>;
}

export const DEFAULT_REPO = { owner: 'CamdenThomas', name: 'Rx7', branch: 'master' };

/** The record he sees: GitHub's copy, with his answers still on the phone laid over it. */
export function overlay(snap: Snapshot, outbox: Outgoing[]): Snapshot {
  if (!outbox.length) return snap;
  const inbox = new Map(snap.inbox.map((a) => [`${a.area}/${a.id}`, a]));
  for (const o of outbox) {
    const key = `${o.answer.area}/${o.answer.id}`;
    if (o.op === 'put') inbox.set(key, { ...o.answer, pending: true });
    else inbox.delete(key);
  }
  const answered = new Set([...inbox.values()].map((a) => `${a.area}/${a.target}`));
  return {
    ...snap,
    inbox: [...inbox.values()],
    blocks: snap.blocks.map((b) => ({ ...b, answered: answered.has(`${b.area}/${b.id}`) })),
  };
}

export async function phonePlatform(opts: PhoneOptions): Promise<Platform> {
  const { kv } = opts;
  const repo = { ...DEFAULT_REPO, ...(opts.repo ?? {}), ...((await kv.get<Repo>('repo')) ?? {}) };
  let token = (await kv.get<string>('token')) ?? '';
  let gh: GitHub = github({ ...repo, token }, opts.fetch, opts.api, opts.raw);
  let cache: FileCache | null = (await kv.get<FileCache>('files')) ?? null;
  let snapshot: Snapshot | null = (await kv.get<Snapshot>('snapshot')) ?? null;
  let outbox: Outgoing[] = (await kv.get<Outgoing[]>('outbox')) ?? [];
  let engineHolds: string | null = null;

  const listeners = new Set<(s: SyncInfo) => void>();
  let info: SyncInfo = { online: navigator.onLine, busy: false, waiting: outbox.length, asOf: cache?.date };
  const publish = (next: Partial<SyncInfo>) => {
    info = { ...info, ...next, waiting: outbox.length };
    listeners.forEach((l) => l(info));
  };

  const keepOutbox = () => kv.set('outbox', outbox);

  /** Hand the engine the record's files, unless it already holds this commit's. */
  const prime = async () => {
    if (!cache) throw new Error('No copy of the record on this phone yet — connect once to fetch it.');
    if (engineHolds === cache.commit) return;
    const files = new Map(Object.entries(cache.files).map(([p, f]) => [p, f.text ?? '']));
    snapshot = await exportRecord(files, opts.pyodide);
    engineHolds = cache.commit;
  };

  const pull = async () => {
    const head = await gh.head();
    if (cache?.commit === head.sha && snapshot) return;
    const entries = (await gh.tree(head.tree)).filter((e) => e.type === 'blob' && wanted(e.path));
    const files: FileCache['files'] = {};
    const need = entries.filter((e) => wanted(e.path) === 'text' && cache?.files[e.path]?.sha !== e.sha);
    let i = 0;
    const worker = async () => {
      while (i < need.length) {
        const e = need[i++];
        files[e.path] = { sha: e.sha, text: await gh.text(head.sha, e.path) };
      }
    };
    await Promise.all(Array.from({ length: 6 }, worker));
    for (const e of entries) {
      files[e.path] ??= wanted(e.path) === 'text' ? cache!.files[e.path] : { sha: e.sha };
    }
    const next = { commit: head.sha, date: head.date, files };
    snapshot = await exportRecord(new Map(Object.entries(files).map(([p, f]) => [p, f.text ?? ''])), opts.pyodide);
    engineHolds = head.sha;
    cache = next;
    await kv.set('files', cache);
    await kv.set('snapshot', snapshot);
  };

  /** Send what is waiting, oldest first. Stops at the first failure and keeps the rest. */
  const flush = async (): Promise<void> => {
    if (!token) throw new Error('Add your GitHub key in Settings so the phone can send answers.');
    while (outbox.length) {
      const o = outbox[0];
      const verb = o.op === 'put' ? 'answered' : 'withdrew his answer to';
      const message = `Camden ${verb} ${o.answer.target} (phone)`;
      if (o.op === 'put') {
        let sha = cache?.files[o.path]?.sha;
        try {
          await gh.put(o.path, o.body!, message, sha);
        } catch (e) {
          if (!(e instanceof GitHubError) || ![409, 422].includes(e.status)) throw e;
          sha = await gh.sha(o.path);
          await gh.put(o.path, o.body!, message, sha);
        }
      } else {
        const sha = await gh.sha(o.path);
        if (sha) await gh.remove(o.path, message, sha);
      }
      outbox.shift();
      await keepOutbox();
      publish({});
    }
  };

  const connect = async (withPull: boolean) => {
    publish({ busy: true, error: undefined });
    try {
      if (outbox.length && token) await flush();
      if (withPull) await pull();
      publish({ busy: false, online: true, asOf: cache?.date, error: undefined });
    } catch (e) {
      const offline = !(e instanceof GitHubError) || e.status === 0;
      const why = e instanceof GitHubError && [401, 403].includes(e.status)
        ? 'GitHub refused the key — check it in Settings.'
        : e instanceof Error ? e.message : String(e);
      publish({ busy: false, online: !offline && navigator.onLine, error: offline && !navigator.onLine ? undefined : why });
      if (!snapshot) throw e;
    }
  };

  window.addEventListener('online', () => void connect(true));
  window.addEventListener('offline', () => publish({ online: false }));

  const platform: Platform & { setToken(t: string): Promise<void>; token(): string } = {
    kind: 'phone',
    canClaude: false,
    kv,
    cached: async () => (snapshot ? overlay(snapshot, outbox) : null),
    async load(sync) {
      if (sync || !snapshot) await connect(true);
      if (!snapshot) throw new Error('No copy of the record on this phone yet — connect once to fetch it.');
      return overlay(snapshot, outbox);
    },
    async save(d: Draft, at: string): Promise<SaveOutcome> {
      await prime();
      const f = await inboxFile(d.area, d.target, d.kind ?? '', d.choice, d.text, d.context, at);
      const answer: Answer = {
        area: d.area, id: f.id, target: d.target, kind: f.kind,
        choice: d.choice, text: d.text, context: d.context, device: 'phone', at, pending: true,
      };
      const path = `${f.areaPath}/data/inbox/${f.id}.csv`;
      outbox = outbox.filter((o) => o.path !== path);
      outbox.push({ op: 'put', path, answer, body: f.body });
      await keepOutbox();
      publish({});
      if (!token || !navigator.onLine) return { state: 'queued' };
      try {
        await flush();
        void connect(true);
        return { state: 'committed' };
      } catch (e) {
        return { state: 'queued', note: e instanceof Error ? e.message : String(e) };
      }
    },
    async withdraw(a: Answer): Promise<SaveOutcome> {
      const area = snapshot?.areas.find((x) => x.name === a.area);
      const path = `${area?.path ?? a.area}/data/inbox/${a.id}.csv`;
      const unsent = outbox.some((o) => o.path === path && o.op === 'put');
      outbox = outbox.filter((o) => o.path !== path);
      if (!unsent) outbox.push({ op: 'delete', path, answer: a });
      await keepOutbox();
      publish({});
      if (unsent || !token || !navigator.onLine) return { state: unsent ? 'committed' : 'queued' };
      try {
        await flush();
        void connect(true);
        return { state: 'committed' };
      } catch (e) {
        return { state: 'queued', note: e instanceof Error ? e.message : String(e) };
      }
    },
    outbox: () => outbox.map((o) => o.answer),
    syncInfo: () => info,
    onSync(l) {
      listeners.add(l);
      return () => listeners.delete(l);
    },
    async commits(path?: string, n = 20): Promise<Commit[]> {
      try {
        return await gh.commits(path, n);
      } catch {
        return [];
      }
    },
    claude: async () => {
      throw new Error('Claude runs on the desktop for now.');
    },
    open: (url) => window.open(url, '_blank'),
    photo: (path) => (cache ? gh.rawUrl(cache.commit, path) : ''),
    token: () => token,
    async setToken(t: string) {
      token = t.trim();
      await kv.set('token', token);
      gh = github({ ...repo, token }, opts.fetch, opts.api, opts.raw);
      void connect(true);
    },
  };
  void loadEngine(opts.pyodide).catch(() => undefined);
  return platform;
}
