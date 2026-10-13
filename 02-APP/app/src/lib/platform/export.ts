// The record's export, as the GitHub Action publishes it (D-511): the rx7 workflow runs
// `rx7.py export` after every push to master that passes `check`, and attaches the result to a
// rolling release, tag `export`, as export.json.gz beside export.meta.json (which commit it was
// made from, that commit's time, when it was built). The phone fetches those two files and
// shows them; it no longer computes the export itself. Nothing here reads a table: the export
// is rx7.py's own export_data(), made on GitHub's runner instead of on the phone.

import type { Snapshot } from '../model';
import type { Fetch } from './github';

/** The release the Action keeps rolling (.github/workflows/rx7.yml, job `publish`). */
export const EXPORT_TAG = 'export';

export interface ExportMeta {
  /** The commit the export was made from. */
  sha: string;
  /** That commit's time (ISO). */
  date: string;
  /** When the Action built it (ISO). */
  built: string;
  bytes?: number;
}

export class ExportError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

/** Where a repository's published export is downloaded from. Public repository: no key. */
export function releaseBase(owner: string, name: string, tag = EXPORT_TAG): string {
  return `https://github.com/${owner}/${name}/releases/download/${tag}`;
}

/** The text of a gzip file, by the WebView's own DecompressionStream. A body that is not gzip
 *  (a server or an HTTP client that already undid it) is read as it is. */
export async function gunzipText(bytes: ArrayBuffer | Uint8Array): Promise<string> {
  const u8 = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  if (u8.length < 2 || u8[0] !== 0x1f || u8[1] !== 0x8b) return new TextDecoder().decode(u8);
  const stream = new Blob([u8 as BlobPart]).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Response(stream).text();
}

const get = async (fetch: Fetch, url: string): Promise<Response> => {
  let res: Response;
  try {
    res = await fetch(url, { cache: 'no-store' });
  } catch (e) {
    throw new ExportError(0, `could not reach ${url}: ${e instanceof Error ? e.message : String(e)}`);
  }
  if (!res.ok) throw new ExportError(res.status, `${url.split('/').pop()}: ${res.status} ${res.statusText}`.trim());
  return res;
};

/**
 * The published export. The small meta comes first; the export itself is downloaded only when
 * it holds a different commit from `have` (the one this phone already shows) — then `snapshot`
 * is left out and the caller keeps its own.
 */
export async function fetchExport(
  fetch: Fetch, base: string, have?: string,
): Promise<{ meta: ExportMeta; snapshot?: Snapshot }> {
  const meta = (await (await get(fetch, `${base}/export.meta.json`)).json()) as ExportMeta;
  if (!meta?.sha || !meta.date) throw new ExportError(0, 'export.meta.json does not name its commit');
  if (have && have === meta.sha) return { meta };
  const text = await gunzipText(await (await get(fetch, `${base}/export.json.gz`)).arrayBuffer());
  const snapshot = JSON.parse(text) as Snapshot;
  if (!snapshot || !Array.isArray(snapshot.areas)) throw new ExportError(0, 'export.json.gz is not the record');
  return { meta, snapshot };
}

const two = (n: number) => String(n).padStart(2, '0');

/** A time as he reads it: the phone's own date and clock, to the minute. */
export function when(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return `${d.getFullYear()}-${two(d.getMonth() + 1)}-${two(d.getDate())} ${two(d.getHours())}:${two(d.getMinutes())}`;
}

/** How old, in the largest whole unit that says it plainly. */
export function howOld(iso: string, now = Date.now()): string {
  const min = Math.max(0, Math.floor((now - new Date(iso).getTime()) / 60_000));
  const say = (n: number, unit: string) => `${n} ${unit}${n === 1 ? '' : 's'}`;
  if (min < 60) return say(min, 'minute');
  const h = Math.floor(min / 60);
  return h < 48 ? say(h, 'hour') : say(Math.floor(h / 24), 'day');
}

/** What the phone says about the export it shows, or nothing when it is current.
 *  `head` is the branch's newest commit as this sync saw it; `fetched` false means the
 *  export could not be fetched and the stored one is shown. */
export function exportNote(o: { meta?: ExportMeta; generated?: string; head?: string; fetched: boolean; now?: number }): string | undefined {
  const date = o.meta?.date ?? o.generated;
  if (!o.fetched) return date ? `could not fetch the export; showing the one from ${when(date)}` : 'could not fetch the export';
  if (o.meta && o.head && o.meta.sha !== o.head) {
    return `export from ${when(o.meta.date)}, ${howOld(o.meta.date, o.now)} old; the Action has not caught up`;
  }
  return undefined;
}
