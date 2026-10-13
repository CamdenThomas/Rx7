// The log pipeline (02-APP BL3; electrical D-478, D-493, log_files LF01-LF05): after a pull,
// each drive folder is one drive. From its files the app works out the drive's date, its end
// odometer and its distance, keeps a digest of every channel for the car's trends (BL4 reads
// it; this file builds no trend view), and writes ONE kind=drive inbox row per drive through
// the app's own answer path - the same one Log drive uses - never 00-CAR's drives.csv (R3).
//
// Pure apart from the files and the store it is handed; tests/logs.test.ts runs it on a
// synthetic drive.

import { COLUMNS, decodeSummary, decodeThin, value, type Header, type Summary, type ThinRecord } from './format';
import type { LogFiles } from './files';
import type { DriveBrief, DriveState, LogState, StateStore } from './state';

/** One column of the thinned record over a drive: the BL4 trend's raw material. */
export interface ColumnDigest {
  name: string;
  unit: string;
  kind: 'value' | 'state' | 'bitfield';
  /** samples that were not blank */
  n: number;
  /** seconds the channel was blank (LF04: unseen in that second) */
  blanks: number;
  min: number | null;
  max: number | null;
  mean: number | null;
  /** bitfields: every bit seen, and the seconds any bit was set */
  or?: number;
  nonzero?: number;
}

export interface Digest {
  seq: number;
  /** unix seconds, and whether it was worked out rather than read from the ICU's clock */
  startUnix: number;
  approx: boolean;
  /** how the date was found */
  dated: string;
  durationS: number;
  records: number;
  /** 0.1 mi */
  startOdoX10: number;
  endOdoX10: number;
  miles: number;
  /** what the ICU kept itself (log_summary_t), when the summary was pulled */
  summary: Summary | null;
  columns: Record<string, ColumnDigest>;
  /** what stands out: seconds over the ICU's own limits, faults, trips */
  flags: string[];
}

const round = (x: number, d = 3) => Math.round(x * 10 ** d) / 10 ** d;

/** Every channel's min / max / mean over the drive, blanks left out (LF04). */
export function digestColumns(records: ThinRecord[]): Record<string, ColumnDigest> {
  const out: Record<string, ColumnDigest> = {};
  for (const c of COLUMNS) {
    let n = 0, blanks = 0, sum = 0, or = 0, nonzero = 0;
    let min = Infinity, max = -Infinity;
    for (const r of records) {
      const raw = r[c.key];
      const v = value(c, raw);
      if (v === null) {
        blanks++;
        continue;
      }
      n++;
      sum += v;
      if (v < min) min = v;
      if (v > max) max = v;
      if (c.channel.kind === 'bitfield') {
        or |= raw;
        if (raw) nonzero++;
      }
    }
    const name = c.channel.count > 1 ? `${c.channel.name} [${c.index + 1}]` : c.channel.name;
    out[c.key] = {
      name, unit: c.channel.unit, kind: c.channel.kind, n, blanks,
      min: n ? round(min) : null, max: n ? round(max) : null, mean: n ? round(sum / n) : null,
      ...(c.channel.kind === 'bitfield' ? { or, nonzero } : {}),
    };
  }
  return out;
}

/**
 * What stands out in a drive. The app holds no limits of its own: the seconds over a limit
 * are the ICU's (the summary's rev_s, hot_s, low_oil_s, counted against stats.h's
 * REDLINE_RPM, HOT_WATER_C and LOW_OIL_CBAR), and the faults are the frames' own bits.
 */
export function flagsOf(summary: Summary | null, cols: Record<string, ColumnDigest>): string[] {
  const f: string[] = [];
  const s = summary ?? {};
  const secs = (k: string, what: string) => s[k] > 0 && f.push(`${s[k]} s ${what}`);
  secs('rev_s', 'over the redline');
  secs('hot_s', 'with the water hot');
  secs('low_oil_s', 'with low oil pressure');
  if (s.fuse_trips > 0) f.push(`${s.fuse_trips} soft-fuse trip${s.fuse_trips === 1 ? '' : 's'}${s.last_trip_ch ? ` (last on O${s.last_trip_ch})` : ''}`);
  if (s.sensor_faults > 0) f.push(`${s.sensor_faults} sensor fault${s.sensor_faults === 1 ? '' : 's'}`);
  if (s.can_timeouts > 0) f.push(`${s.can_timeouts} CAN timeout${s.can_timeouts === 1 ? '' : 's'}`);
  for (const id of ['LC05', 'LC09', 'LC25']) {
    const c = cols[id];
    if (c?.nonzero) f.push(`${c.name}: set for ${c.nonzero} s (bits 0x${(c.or ?? 0).toString(16)})`);
  }
  return f;
}

/** When the drive started, and how that is known (D-493: no clock means approximate). */
export function dateOf(
  h: Header, summary: Summary | null, d: DriveState, durationS: number, nextStart: number | null, pulledAt: number,
): { unix: number; approx: boolean; dated: string } {
  if (h.unixStart) return { unix: h.unixStart, approx: false, dated: "the ICU's clock" };
  if (summary && summary.time_set_unix)
    return { unix: Math.round(summary.time_set_unix - (summary.time_set_uptime - h.uptimeStart) / 1000), approx: true, dated: 'the clock the app set during the drive' };
  if (d.openAt) return { unix: Math.round(d.openAt.unix - (d.openAt.uptimeMs - h.uptimeStart) / 1000), approx: true, dated: "the pull time and the ICU's uptime" };
  if (nextStart !== null) return { unix: nextStart - durationS, approx: true, dated: 'the next drive, taken to start as this one ended' };
  return { unix: pulledAt - durationS, approx: true, dated: 'the pull time, taken as the end of the drive' };
}

/** One drive's digest from its files; null when its thinned log is not held yet. */
export function digest(thin: Uint8Array, summaryFile: Uint8Array | null, d: DriveState, nextStart: number | null, pulledAt: number): Digest | null {
  if (thin.length === 0) return null;
  const { header, records } = decodeThin(thin);
  let summary: Summary | null = null;
  if (summaryFile && summaryFile.length) {
    const s = decodeSummary(summaryFile);
    if (s.header.seq !== header.seq) throw new Error(`drive ${d.seq}: the summary is drive ${s.header.seq}'s`);
    summary = s.summary;
  }
  if (header.seq !== d.seq) throw new Error(`drive ${d.seq}: the thinned log is drive ${header.seq}'s`);
  const last = records.at(-1);
  const durationS = last ? Math.max(0, Math.round((last.LC01 - header.uptimeStart) / 1000)) : summary?.duration_s ?? 0;
  // The odometer: the records' own (LC02), else the summary's; 0 is "not known" (F-007).
  const firstOdo = records.find((r) => r.LC02 > 0)?.LC02 ?? header.startOdoX10;
  let endOdo = [...records].reverse().find((r) => r.LC02 > 0)?.LC02 ?? 0;
  if (!endOdo && summary?.end_odo) endOdo = summary.end_odo;
  let distX10 = endOdo && firstOdo ? endOdo - firstOdo : 0;
  if (distX10 <= 0 && summary?.distance_x10) distX10 = summary.distance_x10;
  if (!endOdo && firstOdo && distX10) endOdo = firstOdo + distX10;
  const when = dateOf(header, summary, d, durationS, nextStart, pulledAt);
  const columns = digestColumns(records);
  return {
    seq: d.seq, startUnix: when.unix, approx: when.approx, dated: when.dated, durationS, records: records.length,
    startOdoX10: firstOdo, endOdoX10: endOdo, miles: Math.max(0, distX10) / 10, summary, columns, flags: flagsOf(summary, columns),
  };
}

// ---------------------------------------------------------------- the drives row
const pad = (n: number) => String(Math.abs(n)).padStart(2, '0');
/** local time with its offset - what inbox.at holds */
export function localIso(d: Date): string {
  const off = -d.getTimezoneOffset();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` +
    `${off >= 0 ? '+' : '-'}${pad(Math.trunc(off / 60))}:${pad(off % 60)}`;
}
/** drive-YYYYMMDDTHHMMSS's stamp (manual.ts's stamp) */
export const stamp = (d: Date) => `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}T${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;

export interface DriveAnswer {
  area: '00-CAR';
  target: string;
  kind: 'drive';
  /** the odometer at the end, whole miles (rx7.py: a reading is whole miles) */
  choice: string;
  text: string;
  context: string;
  /** the drive's end: rx7.py apply takes the drives row's date from it */
  at: string;
}

/** The inbox row for a drive, or why there is none. */
export function driveAnswer(g: Digest): DriveAnswer | { skip: string } {
  if (g.miles < 0.1) return { skip: 'the car did not move (a key turned on, or idling)' };
  const endMiles = Math.floor(g.endOdoX10 / 10);
  if (endMiles < 1) return { skip: "the odometer is not known to the ICU yet (F-007), so there is no reading to file" };
  const end = new Date((g.startUnix + g.durationS) * 1000);
  const start = new Date(g.startUnix * 1000);
  const mins = Math.max(1, Math.round(g.durationS / 60));
  const lines = [
    `Pulled from the ICU, drive ${g.seq}: ${g.miles.toFixed(1)} mi in ${mins} min, from ${localIso(start).slice(0, 16).replace('T', ' ')}.`,
    g.approx ? `Date approximate: the ICU's clock was unset, so it was worked out from ${g.dated}.` : '',
    g.flags.length ? `Flags: ${g.flags.join('; ')}.` : '',
  ];
  return { area: '00-CAR', target: `drive-${stamp(end)}`, kind: 'drive', choice: String(endMiles), text: lines.filter(Boolean).join('\n'), context: '', at: localIso(end) };
}

export interface FileOptions {
  files: LogFiles;
  state: StateStore;
  /** save one answer through the app's inbox path; false if it was not saved */
  save: (a: DriveAnswer) => Promise<boolean>;
  /** targets already in the record or the inbox, so nothing is filed twice */
  known: Set<string>;
  /** only these drives (the ones a pull just touched); all held when absent */
  seqs?: number[];
  now?: () => number;
}

export interface Filed {
  written: string[];
  skipped: string[];
  problems: string[];
}

/** Digest every drive given and file the ones not yet filed, oldest first. */
export async function fileDrives(o: FileOptions): Promise<Filed> {
  const st: LogState = await o.state.load();
  const out: Filed = { written: [], skipped: [], problems: [] };
  const seqs = (o.seqs ?? Object.keys(st.drives).map(Number)).sort((a, b) => b - a);
  const pulledAt = st.last?.unix ?? Math.floor((o.now?.() ?? Date.now()) / 1000);
  // newest first, so each drive can lean on the start of the one after it
  const starts = new Map<number, number>();
  const digests: Digest[] = [];
  for (const seq of seqs) {
    const d = st.drives[seq];
    if (!d) continue;
    try {
      const thin = await o.files.read(seq, 'thin.bin');
      const sum = await o.files.read(seq, 'summary.bin');
      const nb = st.drives[seq + 1]?.brief;
      const next = starts.get(seq + 1) ?? (nb ? Math.round(Date.parse(nb.start) / 1000) : null);
      const g = digest(thin, sum.length ? sum : null, d, next, pulledAt);
      if (!g) continue;
      starts.set(seq, g.startUnix);
      digests.push(g);
      await o.files.write(seq, 'digest.json', 0, new TextEncoder().encode(JSON.stringify(g)));
      const brief: DriveBrief = {
        start: localIso(new Date(g.startUnix * 1000)), approx: g.approx, minutes: Math.round(g.durationS / 60),
        miles: g.miles, endOdo: Math.floor(g.endOdoX10 / 10), flags: g.flags,
      };
      d.brief = brief;
    } catch (e) {
      out.problems.push(`drive ${seq}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }
  for (const g of digests.sort((a, b) => a.seq - b.seq)) {
    const d = st.drives[g.seq];
    if (d.filed?.target) continue; // filed once; later bytes of an open drive do not file it again
    const a = driveAnswer(g);
    if ('skip' in a) {
      d.filed = { skipped: a.skip, at: localIso(new Date()) };
      out.skipped.push(`drive ${g.seq}: ${a.skip}`);
      continue;
    }
    if (o.known.has(a.target)) {
      d.filed = { target: a.target, at: localIso(new Date()) };
      continue;
    }
    if (await o.save(a)) {
      d.filed = { target: a.target, at: localIso(new Date()) };
      o.known.add(a.target);
      out.written.push(a.target);
    } else out.problems.push(`drive ${g.seq}: its drives row was not saved; it is tried again next time`);
    await o.state.save(st);
  }
  await o.state.save(st);
  return out;
}
