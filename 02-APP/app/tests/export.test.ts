// The phone reads the export the Action publishes (D-511): fetched and unzipped, said plainly
// when it is behind or when the last one is shown instead, and never computed on the phone.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { Snapshot } from '../src/lib/model';
import { exportNote, fetchExport, gunzipText, howOld, releaseBase, type ExportMeta } from '../src/lib/platform/export';
import type { KV } from '../src/lib/platform/storage';

// The phone's clock in tests: UTC, so a time reads the same on every machine.
vi.stubEnv('TZ', 'UTC');

vi.mock('../src/lib/platform/core', () => ({
  exportRecord: vi.fn(async () => {
    throw new Error('the phone must not export');
  }),
  loadRecord: vi.fn(async () => undefined),
  loadEngine: vi.fn(),
  inboxFile: vi.fn(),
}));

const BASE = 'https://github.com/CamdenThomas/Rx7/releases/download/export';
const HEAD = 'a'.repeat(40);
const OLD = 'b'.repeat(40);

const snap = (generated: string): Snapshot => ({
  version: 1, generated, record: { valid: true, problems: [] }, areas: [{ path: '00-CAR', name: '00-CAR' } as Snapshot['areas'][number]],
  picks: [], work: [], decisions: [], log: [], tables: [], photos: [], inbox: [], blocks: [],
});
const meta = (sha: string, date = '2026-10-13T10:00:00Z'): ExportMeta => ({ sha, date, built: date });

const body = (b: BodyInit, status = 200) => new Response(b, { status });
const gz = async (o: unknown) =>
  new Uint8Array(await new Response(new Blob([JSON.stringify(o)]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());

/** A stand-in for GitHub: the branch head, and the release's two files. */
function fakeNet(o: { head?: string; meta?: ExportMeta; snapshot?: Snapshot; down?: boolean }) {
  const calls: string[] = [];
  const fetch = vi.fn(async (url: string) => {
    calls.push(url);
    if (o.down) throw new TypeError('network down');
    if (url.includes('/branches/')) {
      return body(JSON.stringify({ commit: { sha: o.head, commit: { tree: { sha: 't' }, committer: { date: '2026-10-13T12:00:00Z' } } } }));
    }
    if (url.includes('/git/trees/')) return body(JSON.stringify({ tree: [], truncated: false }));
    if (url.endsWith('/export.meta.json')) return o.meta ? body(JSON.stringify(o.meta)) : body('Not Found', 404);
    if (url.endsWith('/export.json.gz')) return o.snapshot ? body(await gz(o.snapshot)) : body('Not Found', 404);
    return body('{}', 404);
  });
  return { fetch, calls };
}

const memKV = (init: Record<string, unknown> = {}): KV & { data: Record<string, unknown> } => {
  const data: Record<string, unknown> = { ...init };
  return {
    data,
    get: async <T,>(k: string) => data[k] as T | undefined,
    set: async (k, v) => void (data[k] = structuredClone(v)),
    delete: async (k) => void delete data[k],
  };
};

describe('the published export', () => {
  it('is found at the rolling release', () => {
    expect(releaseBase('CamdenThomas', 'Rx7')).toBe(BASE);
  });

  it('is fetched and unzipped', async () => {
    const { fetch, calls } = fakeNet({ meta: meta(HEAD), snapshot: snap('g1') });
    const got = await fetchExport(fetch, BASE);
    expect(got.meta.sha).toBe(HEAD);
    expect(got.snapshot?.generated).toBe('g1');
    expect(calls).toEqual([`${BASE}/export.meta.json`, `${BASE}/export.json.gz`]);
  });

  it('is not downloaded again when the phone already shows that commit', async () => {
    const { fetch, calls } = fakeNet({ meta: meta(HEAD), snapshot: snap('g1') });
    const got = await fetchExport(fetch, BASE, HEAD);
    expect(got.snapshot).toBeUndefined();
    expect(calls).toEqual([`${BASE}/export.meta.json`]);
  });

  it('reads a body already unzipped on the way as it is', async () => {
    expect(await gunzipText(new TextEncoder().encode('{"a":1}'))).toBe('{"a":1}');
    expect(await gunzipText(await gz({ a: 'µ ✓' }))).toBe('{"a":"µ ✓"}');
  });

  it('refuses a release that is missing', async () => {
    const { fetch } = fakeNet({});
    await expect(fetchExport(fetch, BASE)).rejects.toMatchObject({ status: 404 });
  });
});

describe('what the phone says about it', () => {
  const now = Date.parse('2026-10-13T13:30:00Z');
  it('nothing, when the export is of the head', () => {
    expect(exportNote({ meta: meta(HEAD), head: HEAD, fetched: true, now })).toBeUndefined();
  });
  it('its age and that the Action has not caught up, when it is behind the head', () => {
    expect(exportNote({ meta: meta(OLD), head: HEAD, fetched: true, now })).toBe(
      'export from 2026-10-13 10:00, 3 hours old; the Action has not caught up',
    );
  });
  it('that it shows the last one, when the fetch failed', () => {
    expect(exportNote({ meta: meta(OLD), fetched: false, now })).toBe('could not fetch the export; showing the one from 2026-10-13 10:00');
    expect(exportNote({ generated: '2026-10-12T08:05:00Z', fetched: false })).toBe('could not fetch the export; showing the one from 2026-10-12 08:05');
  });
  it('ages in plain units', () => {
    expect(howOld('2026-10-13T13:00:00Z', now)).toBe('30 minutes');
    expect(howOld('2026-10-13T12:30:00Z', now)).toBe('1 hour');
    expect(howOld('2026-10-10T13:30:00Z', now)).toBe('3 days');
  });
});

describe('the phone syncs from the published export', () => {
  beforeEach(() => {
    vi.stubGlobal('window', { addEventListener: () => undefined, open: () => undefined });
    vi.stubGlobal('navigator', { onLine: true });
    vi.stubGlobal('document', { visibilityState: 'hidden' });
    vi.useFakeTimers({ toFake: ['setInterval'] });
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  const phone = async (net: ReturnType<typeof fakeNet>, cache = memKV()) => {
    const { phonePlatform } = await import('../src/lib/platform/phone');
    const p = await phonePlatform({ kv: memKV(), cache, fetch: net.fetch, api: 'https://api.test', raw: 'https://raw.test', releases: BASE });
    return { p, cache };
  };

  it('shows the fetched export at once, stores it, and never runs the export itself', async () => {
    const core = await import('../src/lib/platform/core');
    const net = fakeNet({ head: HEAD, meta: meta(HEAD), snapshot: snap('fresh') });
    const { p, cache } = await phone(net);
    const s = await p.load(true);
    expect(s.generated).toBe('fresh');
    expect((cache.data.snapshot as Snapshot).generated).toBe('fresh');
    expect((cache.data.exportMeta as ExportMeta).sha).toBe(HEAD);
    expect(p.syncInfo().note).toBeUndefined();
    expect(p.syncInfo().online).toBe(true);
    expect(core.exportRecord).not.toHaveBeenCalled();
    expect(core.loadRecord).not.toHaveBeenCalled();
  });

  it('says so when the export is behind the head it saw', async () => {
    const net = fakeNet({ head: HEAD, meta: meta(OLD), snapshot: snap('older') });
    const { p } = await phone(net);
    expect((await p.load(true)).generated).toBe('older');
    expect(p.syncInfo().note).toMatch(/^export from .+ old; the Action has not caught up$/);
  });

  it('shows the stored export when the fetch fails, and says how old it is', async () => {
    const stored = memKV({ snapshot: snap('kept'), exportMeta: meta(OLD, '2026-10-12T09:15:00Z') });
    const net = fakeNet({ down: true });
    const { p } = await phone(net, stored);
    expect((await p.cached())?.generated).toBe('kept');
    expect((await p.load(true)).generated).toBe('kept');
    expect(p.syncInfo().note).toBe('could not fetch the export; showing the one from 2026-10-12 09:15');
    expect(p.syncInfo().online).toBe(false);
  });

  it('keeps the stored export when the release is missing but GitHub answers', async () => {
    const stored = memKV({ snapshot: snap('kept'), exportMeta: meta(OLD, '2026-10-12T09:15:00Z') });
    const net = fakeNet({ head: HEAD });
    const { p } = await phone(net, stored);
    expect((await p.load(true)).generated).toBe('kept');
    expect(p.syncInfo().note).toMatch(/^could not fetch the export; showing the one from/);
  });

  it('with nothing stored and nothing fetched, says it has no copy', async () => {
    const { p } = await phone(fakeNet({ down: true }));
    await expect(p.load(true)).rejects.toThrow();
  });
});
