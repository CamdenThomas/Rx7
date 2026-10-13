// The Android app. The record comes from GitHub and is kept on the phone, so it reads the
// same with no signal as with full bars (D-403). An answer is saved on the phone the moment
// he saves it, and leaves only when GitHub has committed it — never lost in between.
//
// What it shows is the export the GitHub Action publishes after every push (D-511): one file,
// fetched and shown at once. The record's files are still kept in step behind it, because
// writing an answer is rx7.py's own inbox_entry() in WebAssembly, offline too — and that is
// the only time the engine loads.

import type { Answer, Commit, Snapshot } from '../model';
import { inboxFile, loadRecord } from './core';
import { exportNote, fetchExport, releaseBase, type ExportMeta } from './export';
import { github, GitHubError, wanted, type Fetch, type GitHub, type Repo, type Written } from './github';
import type { KV } from './storage';
import type { Draft, Platform, SaveOutcome, SyncInfo } from './types';

/** An answer on its way: written here, not yet committed on GitHub. */
export interface Outgoing {
  op: 'put' | 'delete';
  path: string;
  answer: Answer;
  body?: string;
}

/** An answer GitHub has committed that the published export may not hold yet: shown until an
 *  export of its commit (or a later one) arrives, so a sent answer never vanishes while the
 *  Action catches up. */
export interface Sent {
  op: 'put' | 'delete';
  answer: Answer;
  /** The commit that carried it, and that commit's time as GitHub gave it (else the phone's). */
  commit?: string;
  date: string;
}

interface FileCache {
  commit: string;
  date: string;
  files: Record<string, { sha: string; text?: string }>;
}

export interface PhoneOptions {
  /** His things: the outbox, the key, the drafts, the settings. Small, written often. */
  kv: KV;
  /** The record's copy: the file cache and the snapshot. Big, written per sync. Falls back
   *  to `kv` when absent (plan P37: two stores, so a torn write of the 6 MB cache can never
   *  take his unsent answers with it). */
  cache?: KV;
  fetch: Fetch;
  api?: string;
  raw?: string;
  pyodide?: string;
  /** Where the published export is downloaded from (default: the repository's `export` release). */
  releases?: string;
  repo?: Omit<Repo, 'token'>;
}

/** How often the phone asks GitHub whether the record moved, while it is in the foreground. */
export const HEAD_POLL_MS = 180_000;

export const DEFAULT_REPO = { owner: 'CamdenThomas', name: 'Rx7', branch: 'master' };

/** A sent answer is in the export once the export is of its commit or a later one; after two
 *  days it is let go whatever the Action did (an answer applied meanwhile is gone anyway). */
export function settled(s: Sent, meta: ExportMeta | undefined, now = Date.now()): boolean {
  if (now - Date.parse(s.date) > 2 * 86_400_000) return true;
  if (!meta) return false;
  if (s.commit && s.commit === meta.sha) return true;
  return Date.parse(meta.date) >= Date.parse(s.date);
}

/** The record he sees: the published export, with what he sent since it was made and what is
 *  still on the phone laid over it. */
export function overlay(snap: Snapshot, outbox: Outgoing[], sent: Sent[] = []): Snapshot {
  if (!outbox.length && !sent.length) return snap;
  const inbox = new Map(snap.inbox.map((a) => [`${a.area}/${a.id}`, a]));
  for (const s of sent) {
    const key = `${s.answer.area}/${s.answer.id}`;
    if (s.op === 'delete') inbox.delete(key);
    else if (!inbox.has(key)) inbox.set(key, { ...s.answer, pending: false });
  }
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
  const store = opts.cache ?? kv;
  const repo = { ...DEFAULT_REPO, ...(opts.repo ?? {}), ...((await kv.get<Repo>('repo')) ?? {}) };
  let token = (await kv.get<string>('token')) ?? '';
  let gh: GitHub = github({ ...repo, token }, opts.fetch, opts.api, opts.raw);
  const releases = opts.releases ?? releaseBase(repo.owner, repo.name);
  let cache: FileCache | null = (await store.get<FileCache>('files')) ?? null;
  let snapshot: Snapshot | null = (await store.get<Snapshot>('snapshot')) ?? null;
  let meta: ExportMeta | undefined = (await store.get<ExportMeta>('exportMeta')) ?? undefined;
  let outbox: Outgoing[] = (await kv.get<Outgoing[]>('outbox')) ?? [];
  let sent: Sent[] = (await kv.get<Sent[]>('sent')) ?? [];
  let engineHolds: string | null = null;
  /** The record's files being brought in step with the head, behind the export already shown. */
  let filesTask: Promise<void> | null = null;
  let note: string | undefined;

  const listeners = new Set<(s: SyncInfo) => void>();
  let info: SyncInfo = { online: navigator.onLine, busy: false, waiting: outbox.length, asOf: meta?.date ?? cache?.date };
  const publish = (next: Partial<SyncInfo>) => {
    info = { ...info, ...next, waiting: outbox.length };
    listeners.forEach((l) => l(info));
  };

  const keepOutbox = () => kv.set('outbox', outbox);
  const view = (snap: Snapshot) => overlay(snap, outbox, sent);

  /** Hand the engine the record's files, unless it already holds this commit's. */
  const prime = async () => {
    if (filesTask) await filesTask;
    if (!cache) await gh.head().then(refreshFiles).catch(() => undefined);
    if (!cache) throw new Error('No copy of the record on this phone yet — connect once to fetch it.');
    if (engineHolds === cache.commit) return;
    const files = new Map(Object.entries(cache.files).map(([p, f]) => [p, f.text ?? '']));
    await loadRecord(files, opts.pyodide);
    engineHolds = cache.commit;
  };

  /** The record's files at the head: rx7.py and every table, only the ones that changed since
   *  the last sync. They are what an answer is written against, offline included. */
  const refreshFiles = async (head: { sha: string; tree: string; date: string }) => {
    if (cache?.commit === head.sha) return;
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
    cache = { commit: head.sha, date: head.date, files };
    await store.set('files', cache);
  };

  /**
   * The published export, shown at once (D-511). Only its small meta is fetched when the phone
   * already shows that commit's export. When it cannot be fetched the last one stays, and the
   * note says so and how old it is. Returns whether GitHub could be reached at all.
   */
  const pull = async (): Promise<boolean> => {
    const [h, got] = await Promise.allSettled([gh.head(), fetchExport(opts.fetch, releases, snapshot ? meta?.sha : undefined)]);
    const head = h.status === 'fulfilled' ? h.value : undefined;
    if (got.status === 'fulfilled') {
      meta = got.value.meta;
      if (got.value.snapshot) {
        snapshot = got.value.snapshot;
        await store.set('snapshot', snapshot);
      }
      await store.set('exportMeta', meta);
      const left = sent.filter((x) => !settled(x, meta));
      if (left.length !== sent.length) await kv.set('sent', (sent = left));
    } else if (!snapshot) throw got.reason;
    note = exportNote({ meta, generated: snapshot?.generated, head: head?.sha, fetched: got.status === 'fulfilled' });
    if (head && cache?.commit !== head.sha && !filesTask) {
      const task: Promise<void> = refreshFiles(head)
        .catch(() => undefined)
        .finally(() => {
          if (filesTask === task) filesTask = null;
        });
      filesTask = task;
    }
    return !!head || got.status === 'fulfilled';
  };

  /** The inbox path an outgoing answer lands at, resolved against the record as it is now, so a
   *  project renamed or renumbered since he answered never strands his words (plan P37). */
  const pathFor = (o: Outgoing): string => {
    const area = snapshot?.areas.find((a) => a.name === o.answer.area);
    if (!area) throw new Error(`Your answer to ${o.answer.target} waits: its project ${o.answer.area} is not in the record any more. It stays on this phone.`);
    return `${area.path}/data/inbox/${o.answer.id}.csv`;
  };

  /** Send what is waiting, oldest first. Stops at the first failure and keeps the rest. */
  const flush = async (): Promise<void> => {
    if (!token) throw new Error('Add your GitHub key in Settings so the phone can send answers.');
    while (outbox.length) {
      const o = outbox[0];
      const verb = o.op === 'put' ? 'answered' : 'withdrew his answer to';
      const message = `Camden ${verb} ${o.answer.target} (phone)`;
      const path = pathFor(o);
      let w: Written | undefined;
      if (o.op === 'put') {
        let sha = cache?.files[path]?.sha;
        try {
          w = await gh.put(path, o.body!, message, sha);
        } catch (e) {
          if (!(e instanceof GitHubError) || ![409, 422].includes(e.status)) throw e;
          sha = await gh.sha(path);
          w = await gh.put(path, o.body!, message, sha);
        }
      } else {
        const sha = await gh.sha(path);
        if (sha) w = await gh.remove(path, message, sha);
      }
      // Shown as sent until the published export holds it; kept before the outbox lets go.
      sent.push({ op: o.op, answer: { ...o.answer, pending: false }, commit: w?.commit?.sha, date: w?.commit?.committer?.date ?? new Date().toISOString() });
      await kv.set('sent', sent);
      outbox.shift();
      await keepOutbox();
      publish({});
    }
  };

  const connect = async (withPull: boolean) => {
    publish({ busy: true, error: undefined });
    try {
      if (outbox.length && token) await flush();
      const reached = withPull ? await pull() : true;
      publish({ busy: false, online: reached, asOf: meta?.date ?? cache?.date, note, error: undefined });
    } catch (e) {
      const offline = !(e instanceof GitHubError) || e.status === 0;
      const why = e instanceof GitHubError && [401, 403].includes(e.status)
        ? 'GitHub refused the key — check it in Settings.'
        : e instanceof Error ? e.message : String(e);
      if (withPull && snapshot) note = exportNote({ meta, generated: snapshot.generated, fetched: false });
      publish({ busy: false, online: !offline && navigator.onLine, note, error: offline && !navigator.onLine ? undefined : why });
      if (!snapshot) throw e;
    }
  };

  window.addEventListener('online', () => void connect(true));
  window.addEventListener('offline', () => publish({ online: false }));
  // While the app is in front, one small call every few minutes asks whether the record
  // moved; a sync only when it did, or while the published export is behind (plan P38, D-511).
  setInterval(() => {
    if (document.visibilityState !== 'visible' || !navigator.onLine || info.busy) return;
    gh.head().then((h) => { if (h.sha !== cache?.commit || h.sha !== meta?.sha) void connect(true); }).catch(() => undefined);
  }, HEAD_POLL_MS);

  const platform: Platform & { setToken(t: string): Promise<void>; token(): string } = {
    kind: 'phone',
    canClaude: false,
    kv,
    cached: async () => (snapshot ? view(snapshot) : null),
    async load(sync) {
      if (sync || !snapshot) await connect(true);
      if (!snapshot) throw new Error('No copy of the record on this phone yet — connect once to fetch it.');
      return view(snapshot);
    },
    async save(d: Draft, at: string): Promise<SaveOutcome> {
      await prime();
      // An earlier answer to the same target from this phone (sent, or still in the outbox) is
      // never overwritten without a trace: its choice and words ride along in context (R3, P18).
      const earlier =
        outbox.find((o) => o.op === 'put' && o.answer.area === d.area && o.answer.target === d.target)?.answer ??
        [...sent].reverse().find((s) => s.op === 'put' && s.answer.area === d.area && s.answer.target === d.target)?.answer ??
        snapshot?.inbox.find((a) => a.area === d.area && a.target === d.target && a.device === 'phone');
      let context = d.context;
      if (earlier && (earlier.choice !== d.choice || earlier.text !== d.text)) {
        const was = `earlier answer ${earlier.at}: ${earlier.choice} ${earlier.text}`.trim();
        context = [was, earlier.context, d.context].filter(Boolean).join('\n');
      }
      const f = await inboxFile(d.area, d.target, d.kind ?? '', d.choice, d.text, context, at);
      const answer: Answer = {
        area: d.area, id: f.id, target: d.target, kind: f.kind,
        choice: d.choice, text: d.text, context, device: 'phone', at, pending: true,
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
    photo: (path) => {
      const at = cache?.commit ?? meta?.sha;
      return at ? gh.rawUrl(at, path) : '';
    },
    token: () => token,
    async setToken(t: string) {
      token = t.trim();
      await kv.set('token', token);
      gh = github({ ...repo, token }, opts.fetch, opts.api, opts.raw);
      void connect(true);
    },
  };
  // The Python engine (13 MB of WebAssembly) loads only when an answer is first written:
  // reading the record needs no Python at all since the Action publishes the export (D-511).
  return platform;
}
