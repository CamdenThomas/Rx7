// Connect and log: the pull (02-APP BL2; electrical log_link LL01-LL10, LL18, D-494, D-483).
//
//   find RX7-ICU -> connect (bonded; the first time the OS asks for the cluster's passkey)
//   -> read info, refuse a protocol this app does not speak -> SET_TIME when the ICU's clock
//   is unset or off -> LIST -> per drive, oldest first: OPEN the summary at 0 (it is
//   rewritten in place), then the thinned log at the last byte held -> keep each chunk at its
//   offset -> on done, CRC-32 the whole tier as held against the ICU's -> ACK only on a match
//   -> the full log only when asked, drive by drive.
//
// A pull cut short loses nothing: the bytes held are on disk with no gap, and the next pull
// OPENs there (LL09, D-483). A CRC that does not match is never acknowledged; the tier is
// started again from 0. Only the six requests are ever written (transport.control).

import { LINK } from './layout.generated';
import { crc32 } from './bytes';
import { TIER_FILE, TIER_NAME, hex, type Tier } from './format';
import type { LogFiles } from './files';
import * as P from './protocol';
import { blank, type DriveState, type PullMoment, type StateStore } from './state';
import type { Advert, LinkTransport } from './transport';

export type Phase = 'scanning' | 'connecting' | 'info' | 'clock' | 'listing' | 'pulling' | 'checking' | 'done' | 'error';

export interface Progress {
  phase: Phase;
  message: string;
  /** drives this pull will fetch, and how many are done */
  drives: number;
  drivesDone: number;
  seq?: number;
  tier?: Tier;
  /** bytes received this pull, of the bytes it expects */
  bytes: number;
  expected: number;
  /** bytes a second, smoothed */
  rate: number;
}

export interface PullOptions {
  transport: LinkTransport;
  files: LogFiles;
  state: StateStore;
  /** the phone's clock, ms since 1970 */
  now?: () => number;
  /** drives whose full log he asked for (the full tier is never pulled otherwise, D-493) */
  full?: number[];
  /** pull the summary and thin tiers of the drives LIST 0 names (Connect and log); false for a full-log-only run */
  thin?: boolean;
  scanMs?: number;
  /** no data and no status for this long: re-OPEN where the bytes stop */
  silenceMs?: number;
  /** how long an ACK may be refused before it counts as taken */
  ackMs?: number;
  /** re-OPENs per tier before the drive is left for next time */
  retries?: number;
  /** bytes kept in memory before they are written to the drive's file */
  flushBytes?: number;
  onProgress?: (p: Progress) => void;
  signal?: AbortSignal;
}

export interface PullResult {
  info: P.Info;
  /** every drive touched, as now held */
  drives: DriveState[];
  /** "seq tier" acknowledged this pull */
  acked: string[];
  /** what went wrong but did not stop the pull - each a drive left for next time */
  problems: string[];
}

export class PullError extends Error {
  constructor(message: string, public readonly kind: 'not-found' | 'protocol' | 'link' | 'card' | 'refused' | 'stopped' | 'bluetooth') {
    super(message);
  }
}

const NOT_FOUND =
  `${LINK.name} was not found. The ICU is awake only with the key at ACC or RUN (D-483) - turn the key on and press Connect and log again. ` +
  'The first time, pair the phone with the car: a long press of the page button shows a six-digit key on the cluster.';

/** The ICU among the advertisements: by name, or by the log service (LL01). */
export const isIcu = (a: Advert) => a.name === LINK.name || a.services.some((s) => s.toLowerCase() === LINK.uuid.service);

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** Notifications, routed to whatever is waiting on them. */
class Wire {
  onItem: ((i: P.Item) => void) | null = null;
  onData: ((offset: number, bytes: Uint8Array) => void) | null = null;
  onStatus: ((s: P.Status) => void) | null = null;
  last = Date.now();
  touch() {
    this.last = Date.now();
  }
}

export async function connectAndLog(o: PullOptions): Promise<PullResult> {
  const t = o.transport;
  const now = o.now ?? (() => Date.now());
  const silenceMs = o.silenceMs ?? 8000;
  // The C3 says nothing when an ACK is taken (its status is unchanged: done, err 0) and
  // notifies ERROR when it is refused, within a round trip of the UART; this long is plenty.
  const ackMs = o.ackMs ?? 800;
  const retries = o.retries ?? 3;
  const flushBytes = o.flushBytes ?? 32 * 1024;
  const pullThin = o.thin ?? true;
  const full = new Set(o.full ?? []);
  const problems: string[] = [];
  const acked: string[] = [];
  const prog: Progress = { phase: 'scanning', message: `Looking for ${LINK.name}…`, drives: 0, drivesDone: 0, bytes: 0, expected: 0, rate: 0 };
  const say = (p: Partial<Progress>) => {
    Object.assign(prog, p);
    o.onProgress?.({ ...prog });
  };
  const stopped = () => {
    if (o.signal?.aborted) throw new PullError('Stopped.', 'stopped');
  };

  if (!(await t.available())) throw new PullError('Bluetooth is not available on this device.', 'bluetooth');
  if (!(await t.permissions(true))) throw new PullError('Bluetooth permission was not given. Rx7 needs it to reach the car (Settings → Apps → Rx7 → Permissions).', 'bluetooth');

  // ---- find the ICU (LL01)
  say({ phase: 'scanning' });
  let icu: Advert | undefined;
  const found = new AbortController();
  o.signal?.addEventListener('abort', () => found.abort(), { once: true });
  await t.scan((ads) => {
    icu ??= ads.find(isIcu);
    if (icu) found.abort();
  }, o.scanMs ?? 12_000, found.signal);
  stopped();
  if (!icu) throw new PullError(NOT_FOUND, 'not-found');

  // ---- connect; the first read pairs (LL02)
  say({ phase: 'connecting', message: `Connecting to ${LINK.name}… The first time, type the six-digit key the cluster shows.` });
  let lost = false;
  await t.connect(icu.address, () => (lost = true));
  const wire = new Wire();
  const st = await o.state.load();
  try {
    say({ phase: 'info', message: 'Reading the ICU…' });
    const raw = await t.readInfo();
    if (raw.length < P.INFO_LEN) throw new PullError(`The ICU's info is ${raw.length} bytes; protocol ${LINK.protocol} sends ${P.INFO_LEN}.`, 'protocol');
    const info = P.decodeInfo(raw);
    if (info.protocol !== LINK.protocol)
      throw new PullError(`The ICU speaks log protocol ${info.protocol}; this app speaks ${LINK.protocol}. Update the app (or the ICU) before pulling.`, 'protocol');

    await t.subscribe('drives', (b) => (wire.touch(), wire.onItem?.(P.decodeItem(b))));
    await t.subscribe('data', (b) => {
      wire.touch();
      const d = P.decodeData(b);
      wire.onData?.(d.offset, d.bytes);
    });
    await t.subscribe('status', (b) => (wire.touch(), wire.onStatus?.(P.decodeStatus(b))));

    // ---- the clock (LL08, D-493): the one piece of state the app sets
    const nowUnix = Math.floor(now() / 1000);
    if (P.timeWanted(info, nowUnix)) {
      say({ phase: 'clock', message: "Setting the ICU's clock…" });
      await t.control(P.setTime(nowUnix));
    }
    const moment: PullMoment = { unix: nowUnix, uptimeMs: info.uptime_ms, driveCount: info.drive_count, odometer: info.odometer };
    st.last = moment;

    // ---- the list (LL04, LL06)
    const listFrom = async (from: number, until?: (i: P.Item) => boolean): Promise<P.Item[]> => {
      say({ phase: 'listing', message: 'Asking which drives wait…' });
      const items: P.Item[] = [];
      let end = false;
      let err: P.Status | null = null;
      wire.onItem = (i) => {
        if (i.seq === 0) end = true;
        else {
          items.push(i);
          if (until?.(i)) end = true;
        }
      };
      wire.onStatus = (s) => {
        if (s.state === P.STATE.error) err = s;
      };
      wire.touch();
      await t.control(P.list(from));
      while (!end && !err) {
        stopped();
        if (lost) throw new PullError('The link dropped while listing. Press Connect and log again.', 'link');
        if (Date.now() - wire.last > silenceMs) throw new PullError('The ICU stopped answering while listing.', 'link');
        await sleep(20);
      }
      wire.onItem = wire.onStatus = null;
      if (err) throw statusError(err as P.Status);
      return items;
    };

    const work: { d: DriveState; tiers: Tier[] }[] = [];
    if (pullThin) {
      for (const item of await listFrom(0)) {
        const d = (st.drives[item.seq] ??= blank(item));
        d.item = item;
        d.seenAt = moment;
        if (item.seq === info.drive_count) d.openAt = moment;
        const tiers: Tier[] = [];
        // the summary is rewritten every minute: always the whole of it
        if (!(item.pulled & 1) || d.held[0] !== item.summary_len) tiers.push(0);
        if (!(item.pulled & 2) || d.held[1] !== item.thin_len) tiers.push(1);
        if (full.has(item.seq) && d.held[2] !== item.full_len) tiers.push(2);
        full.delete(item.seq);
        if (tiers.length) work.push({ d, tiers });
      }
    }
    for (const seq of [...full].sort((a, b) => a - b)) {
      const items = await listFrom(seq, (i) => i.seq >= seq);
      const item = items.find((i) => i.seq === seq);
      if (!item) {
        problems.push(`drive ${seq}: the ICU no longer holds it (a full log is pruned oldest first past three-quarters of the card)`);
        continue;
      }
      const d = (st.drives[seq] ??= blank(item));
      d.item = item;
      d.seenAt = moment;
      if (item.full_len === 0) problems.push(`drive ${seq}: the ICU holds no full log for it`);
      else if (d.held[2] !== item.full_len) work.push({ d, tiers: [2] });
    }
    work.sort((a, b) => a.d.seq - b.d.seq);
    await o.state.save(st);

    // ---- the files
    const lenOf = (d: DriveState, tier: Tier) => (tier === 0 ? d.item.summary_len : tier === 1 ? d.item.thin_len : d.item.full_len);
    // The resume offset is what the file holds: it is only ever written at its own end, so its
    // length is the last contiguous byte (the store's copy can lag a crash by one flush). A
    // file longer than the ICU's is not that file any more, and starts again.
    for (const w of work) {
      for (const tier of w.tiers) {
        const size = await o.files.size(w.d.seq, TIER_FILE[tier]);
        w.d.held[tier] = tier === 0 || size > lenOf(w.d, tier) ? 0 : size;
      }
    }
    say({
      phase: 'pulling', drives: work.length, drivesDone: 0, bytes: 0,
      expected: work.reduce((s, w) => s + w.tiers.reduce((n: number, tier) => n + lenOf(w.d, tier) - w.d.held[tier], 0), 0),
    });
    let rateAt = Date.now();
    let rateBytes = 0;
    const counted = (n: number) => {
      rateBytes += n;
      const dt = Date.now() - rateAt;
      if (dt >= 500) {
        const r = (rateBytes * 1000) / dt;
        prog.rate = prog.rate ? prog.rate * 0.6 + r * 0.4 : r;
        rateAt = Date.now();
        rateBytes = 0;
      }
      say({ bytes: prog.bytes + n });
    };

    /** One tier from `held` to its end; true when held whole, CRC-checked and acknowledged. */
    const transfer = async (d: DriveState, tier: Tier): Promise<boolean> => {
      const name = TIER_FILE[tier];
      const label = `drive ${d.seq} ${TIER_NAME[tier]}`;
      for (let attempt = 0, restarts = 0; attempt <= retries; attempt++) {
        stopped();
        if (lost) throw new PullError('The link dropped. Press Connect and log again - the pull carries on where it stopped.', 'link');
        const from = d.held[tier];
        let pos = from;
        let pending: Uint8Array[] = [];
        let pendingLen = 0;
        let sending = false;
        let done: P.Status | null = null;
        let err: P.Status | null = null;
        let gap = false;
        const flush = async () => {
          if (!pendingLen) return;
          const parts = pending;
          const at = pos - pendingLen;
          pending = [];
          pendingLen = 0;
          const all = new Uint8Array(parts.reduce((s, p) => s + p.length, 0));
          let k = 0;
          for (const p of parts) (all.set(p, k), (k += p.length));
          await o.files.write(d.seq, name, at, all);
          d.held[tier] = at + all.length;
          await o.state.save(st);
        };
        wire.onData = (offset, bytes) => {
          if (gap) return;
          if (offset > pos) {
            gap = true; // a chunk went missing: re-OPEN at the last byte held
            return;
          }
          const fresh = bytes.subarray(Math.min(bytes.length, pos - offset));
          if (!fresh.length) return;
          pending.push(fresh.slice());
          pendingLen += fresh.length;
          pos += fresh.length;
          counted(fresh.length);
        };
        wire.onStatus = (s) => {
          if (s.seq !== d.seq || s.tier !== tier) return;
          if (s.state === P.STATE.sending) sending = true;
          else if (s.state === P.STATE.done && (sending || pos >= s.total)) done = s;
          else if (s.state === P.STATE.error) err = s;
        };
        say({ seq: d.seq, tier, message: `Drive ${d.seq}: the ${TIER_NAME[tier]}${from ? ` from byte ${from}` : ''}…` });
        wire.touch();
        await t.control(P.open(d.seq, tier, from));
        let flushing: Promise<void> = Promise.resolve();
        let busy = false;
        for (;;) {
          stopped();
          if (lost) {
            await flushing;
            await flush();
            throw new PullError('The link dropped. Press Connect and log again - the pull carries on where it stopped.', 'link');
          }
          const dn = done as P.Status | null;
          if (err || gap || (dn && pos >= dn.total) || Date.now() - wire.last > silenceMs) break;
          if (pendingLen >= flushBytes && !busy) {
            busy = true;
            flushing = flushing.then(flush).finally(() => (busy = false));
          }
          await sleep(15);
        }
        wire.onData = wire.onStatus = null;
        await flushing;
        await flush();
        const e = err as P.Status | null;
        if (e) {
          if (e.err === 3) throw new PullError('The ICU reports no card.', 'card');
          if (e.err === 1) throw new PullError(`The ICU refused a request as a bad opcode - its protocol is not ${LINK.protocol}.`, 'protocol');
          if (e.err === 2) {
            problems.push(`${label}: ${P.errText(e.err)}`);
            return false;
          }
          if (e.err === 4) await sleep(1000);
          continue; // aborted, silent, busy: again from the bytes held
        }
        if (gap || !done) continue; // a missing chunk, or silence: again from the bytes held
        const fin = done as P.Status;
        if (pos > fin.total) {
          // more bytes than the tier has: what is held is not this file - start again
          await o.files.write(d.seq, name, 0, new Uint8Array(0));
          d.held[tier] = 0;
          if (restarts++ > 0) break;
          continue;
        }
        say({ phase: 'checking', message: `Drive ${d.seq}: checking the ${TIER_NAME[tier]}…` });
        const file = await o.files.read(d.seq, name);
        const crc = crc32(file.subarray(0, fin.total));
        if (file.length !== fin.total || crc !== fin.crc32) {
          // never acknowledged; the tier starts again from 0 (once more this pull)
          problems.push(`${label}: CRC 0x${hex(crc)} over ${file.length} bytes, the ICU's is 0x${hex(fin.crc32)} over ${fin.total} - not acknowledged, pulled again`);
          await o.files.write(d.seq, name, 0, new Uint8Array(0));
          d.held[tier] = 0;
          await o.state.save(st);
          say({ phase: 'pulling' });
          if (restarts++ > 0) return false;
          continue;
        }
        // ---- ACK (LL08): the ICU marks the tier pulled only now
        let refused: P.Status | null = null;
        wire.onStatus = (s) => {
          if (s.seq === d.seq && s.tier === tier && s.state === P.STATE.error) refused = s;
        };
        await t.control(P.ack(d.seq, tier, crc));
        const until = Date.now() + ackMs;
        while (!refused && Date.now() < until && !lost) await sleep(20);
        wire.onStatus = null;
        say({ phase: 'pulling' });
        const r = refused as P.Status | null;
        if (r) {
          problems.push(`${label}: the ACK was refused (${P.errText(r.err)}); it is held here and acknowledged next time`);
          return false;
        }
        d.acked[tier] = { len: fin.total, crc };
        acked.push(`${d.seq} ${TIER_NAME[tier]}`);
        await o.state.save(st);
        return true;
      }
      problems.push(`${label}: the transfer kept breaking off at byte ${d.held[tier]} - carried on next time`);
      return false;
    };

    for (const w of work) {
      for (const tier of w.tiers) await transfer(w.d, tier);
      say({ drivesDone: prog.drivesDone + 1 });
    }
    await o.state.save(st);
    say({ phase: 'done', message: work.length ? `Pulled ${work.length} drive${work.length === 1 ? '' : 's'}.` : 'Nothing new on the ICU.' });
    return { info, drives: work.map((w) => w.d), acked, problems };
  } catch (e) {
    await o.state.save(st).catch(() => undefined);
    say({ phase: 'error', message: e instanceof Error ? e.message : String(e) });
    throw e;
  } finally {
    await t.disconnect().catch(() => undefined);
  }
}

function statusError(s: P.Status): PullError {
  const kind = s.err === 3 ? 'card' : s.err === 1 ? 'protocol' : 'link';
  return new PullError(`The ICU answered: ${P.errText(s.err)}.`, kind);
}
