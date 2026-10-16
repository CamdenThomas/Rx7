// The car's trends (02-APP BL4; electrical D-478): every logged channel's per-drive figure
// across the drives this device has pulled, a drift mark when the newest drives step away from
// the ones before, and the out-of-range flags of each drive. All of it is worked out when the
// page opens, from the per-drive digests (pipeline.ts, digest.json) and the record: the limits
// are electrical params redline_rpm, hot_water_c and low_oil_bar, a channel's name, unit and
// blank are log_channels' (through layout.generated.ts). Nothing here is stored; digest.json is
// the only cache, and loadDigests rebuilds it from thin.bin and summary.bin when it is missing.
//
// Pure apart from the files and the store it is handed; tests/trends.test.ts runs it on
// synthetic drives (synth.ts).

import type { RawTable } from '../model';
import type { LogFiles } from './files';
import { digest, localIso, type ColumnDigest, type Digest } from './pipeline';
import type { Item } from './protocol';
import type { DriveState, StateStore } from './state';

// ---------------------------------------------------------------- the digests, loaded

/**
 * Every drive this device holds, as its digest, oldest first. A digest.json that is missing
 * or unreadable is rebuilt from the drive's thin.bin and summary.bin and written back: it is
 * a cache of those files and nothing else.
 */
export async function loadDigests(files: LogFiles, state: StateStore, now = Date.now()): Promise<{ digests: Digest[]; rebuilt: number[]; problems: string[] }> {
  const st = await state.load();
  const seqs = [...new Set([...Object.keys(st.drives).map(Number), ...(await files.list())])].sort((a, b) => a - b);
  const out = { digests: [] as Digest[], rebuilt: [] as number[], problems: [] as string[] };
  const pulledAt = st.last?.unix ?? Math.floor(now / 1000);
  for (const seq of seqs) {
    try {
      const raw = await files.read(seq, 'digest.json');
      if (raw.length) {
        const g = JSON.parse(new TextDecoder().decode(raw)) as Digest;
        if (g && g.seq === seq && g.columns) {
          out.digests.push(g);
          continue;
        }
      }
      const thin = await files.read(seq, 'thin.bin');
      if (!thin.length) continue;
      const sum = await files.read(seq, 'summary.bin');
      const d: DriveState = st.drives[seq] ?? { seq, item: { seq } as Item, held: [0, 0, 0], acked: [null, null, null] };
      const nb = st.drives[seq + 1]?.brief;
      const g = digest(thin, sum.length ? sum : null, d, nb ? Math.round(Date.parse(nb.start) / 1000) : null, pulledAt);
      if (!g) continue;
      await files.write(seq, 'digest.json', 0, new TextEncoder().encode(JSON.stringify(g)));
      out.digests.push(g);
      out.rebuilt.push(seq);
    } catch (e) {
      out.problems.push(`drive ${seq}: ${e instanceof Error ? e.message : String(e)}`);
    }
  }
  return out;
}

/** A drive's local start date, YYYY-MM-DD. */
export const driveDate = (g: Pick<Digest, 'startUnix'>) => localIso(new Date(g.startUnix * 1000)).slice(0, 10);

// ---------------------------------------------------------------- the limits, from the record

export interface Limits {
  redline_rpm: number | null;
  hot_water_c: number | null;
  low_oil_bar: number | null;
}

/** One 02-electrical params value as a number, or null when the record has none. */
export function param(tables: RawTable[] | undefined, key: string): number | null {
  const t = tables?.find((x) => x.area === '02-electrical' && x.table === 'params');
  if (!t) return null;
  const row = t.rows.find((r) => r[0] === key);
  const v = Number(row?.[t.columns.indexOf('value')]);
  return row && Number.isFinite(v) ? v : null;
}

/** The drive flags' limits (D-328): read from the record, never typed here. */
export function limitsFrom(tables: RawTable[] | undefined): Limits {
  return { redline_rpm: param(tables, 'redline_rpm'), hot_water_c: param(tables, 'hot_water_c'), low_oil_bar: param(tables, 'low_oil_bar') };
}

// ---------------------------------------------------------------- which channels trend, and how

/**
 * When the newest drives have stepped away from the earlier ones: the last DRIFT_RECENT drives
 * must EACH sit beyond the margin, on the same side, of the mean of up to DRIFT_EARLIER drives
 * before them, and there must be at least DRIFT_MIN_EARLIER of those. The margin is
 * max(abs, rel × |baseline|). One odd drive is not a drift. All margins are confirm: nothing
 * in the record sets them; they are this app's first guess, to be tuned once real drives exist.
 */
export interface DriftRule {
  abs: number;
  rel?: number;
  /** why this margin, in a line - shown with the mark */
  why: string;
}

export const DRIFT_RECENT = 3;
export const DRIFT_MIN_EARLIER = 3;
export const DRIFT_EARLIER = 10;

export type Group = 'Engine' | 'Fuel' | 'Electrical' | 'Battery' | 'Motion';

export interface TrendSpec {
  /** the digest column: a log_channels id, or id.index for one element of an array channel */
  key: string;
  group: Group;
  /** the per-drive figure the trend's latest value and its drift read */
  stat: 'mean' | 'max';
  digits: number;
  /** null: the channel has no drift rule, and why */
  drift: DriftRule | null;
  why?: string;
}

/** The trended channels and their drift rules (all margins confirm). */
export const TRENDS: readonly TrendSpec[] = [
  { key: 'LC20', group: 'Engine', stat: 'max', digits: 0, drift: { abs: 5, why: "the hottest the water got, 5 °C off its usual peak (confirm): the mean follows how long the drive's warm-up was" } },
  { key: 'LC21', group: 'Engine', stat: 'max', digits: 0, drift: { abs: 8, why: 'the hottest the oil got, 8 °C off its usual peak (confirm)' } },
  { key: 'LC22', group: 'Engine', stat: 'mean', digits: 2, drift: { abs: 0.3, why: 'the mean oil pressure, 0.3 bar off its usual (confirm); the mean includes key-on seconds before the engine starts' } },
  { key: 'LC16', group: 'Engine', stat: 'mean', digits: 3, drift: { abs: 0.05, why: 'the mean mixture, 0.05 λ off its usual (confirm): a leaner or richer carburettor' } },
  { key: 'LC19', group: 'Engine', stat: 'max', digits: 0, drift: null, why: 'how hard he drove, not wear: flagged against the redline instead' },
  { key: 'LC28', group: 'Fuel', stat: 'mean', digits: 1, drift: null, why: 'follows the fill-ups, not wear' },
  { key: 'LC10', group: 'Electrical', stat: 'mean', digits: 0, drift: { abs: 200, why: 'the mean system voltage, 200 mV off its usual (confirm): charging or a ground' } },
  { key: 'LC11', group: 'Electrical', stat: 'mean', digits: 1, drift: { abs: 2, rel: 0.2, why: 'the mean total current, 20 % or 2 A off its usual, whichever is more (confirm): a load drawing more' } },
  { key: 'LC46', group: 'Electrical', stat: 'mean', digits: 2, drift: { abs: 0.5, rel: 0.2, why: 'the mean comfort bus current, 20 % or 0.5 A off its usual (confirm)' } },
  { key: 'LC30', group: 'Battery', stat: 'mean', digits: 0, drift: { abs: 200, why: 'the mean pack voltage, 200 mV off its usual (confirm)' } },
  { key: 'LC31.0', group: 'Battery', stat: 'mean', digits: 0, drift: { abs: 30, why: 'the mean cell voltage, 30 mV off its usual (confirm)' } },
  { key: 'LC31.1', group: 'Battery', stat: 'mean', digits: 0, drift: { abs: 30, why: 'the mean cell voltage, 30 mV off its usual (confirm)' } },
  { key: 'LC31.2', group: 'Battery', stat: 'mean', digits: 0, drift: { abs: 30, why: 'the mean cell voltage, 30 mV off its usual (confirm)' } },
  { key: 'LC31.3', group: 'Battery', stat: 'mean', digits: 0, drift: { abs: 30, why: 'the mean cell voltage, 30 mV off its usual (confirm)' } },
  { key: 'LC32', group: 'Battery', stat: 'max', digits: 0, drift: { abs: 15, why: 'the widest cell spread, 15 mV off its usual (confirm): a cell falling behind' } },
  { key: 'LC51.0', group: 'Motion', stat: 'max', digits: 2, drift: null, why: 'how hard he drove, not wear' },
  { key: 'LC51.1', group: 'Motion', stat: 'max', digits: 2, drift: null, why: 'how hard he drove, not wear' },
  { key: 'LC51.2', group: 'Motion', stat: 'max', digits: 2, drift: null, why: 'how hard he drove, not wear' },
];

export interface Drift {
  dir: 'up' | 'down';
  baseline: number;
  recent: number;
  by: number;
  margin: number;
}

const avg = (xs: number[]) => xs.reduce((a, b) => a + b, 0) / xs.length;

/** The drift rule above, over one channel's per-drive figures, oldest first (nulls left out). */
export function drift(values: (number | null)[], rule: DriftRule | null): Drift | null {
  if (!rule) return null;
  const v = values.filter((x): x is number => x !== null && Number.isFinite(x));
  if (v.length < DRIFT_RECENT + DRIFT_MIN_EARLIER) return null;
  const recent = v.slice(-DRIFT_RECENT);
  const earlier = v.slice(0, -DRIFT_RECENT).slice(-DRIFT_EARLIER);
  const baseline = avg(earlier);
  const margin = Math.max(rule.abs, (rule.rel ?? 0) * Math.abs(baseline));
  const up = recent.every((x) => x - baseline > margin);
  const down = recent.every((x) => baseline - x > margin);
  if (!up && !down) return null;
  const r = avg(recent);
  return { dir: up ? 'up' : 'down', baseline, recent: r, by: r - baseline, margin };
}

export interface TrendPoint {
  seq: number;
  date: string;
  approx: boolean;
  min: number | null;
  max: number | null;
  mean: number | null;
  /** the spec's stat */
  value: number | null;
}

export interface Trend {
  spec: TrendSpec;
  name: string;
  unit: string;
  points: TrendPoint[];
  latest: TrendPoint | null;
  drift: Drift | null;
}

/** Each trended channel across the drives (oldest first); a channel no drive saw is left out. */
export function trends(digests: Digest[]): Trend[] {
  const ds = [...digests].sort((a, b) => a.seq - b.seq);
  const out: Trend[] = [];
  for (const spec of TRENDS) {
    const cols = ds.map((g) => [g, g.columns[spec.key]] as [Digest, ColumnDigest | undefined]);
    const seen = cols.find(([, c]) => c && c.n > 0)?.[1];
    if (!seen) continue;
    const points = cols.map(([g, c]): TrendPoint => {
      const has = !!c && c.n > 0;
      return {
        seq: g.seq, date: driveDate(g), approx: g.approx,
        min: has ? c!.min : null, max: has ? c!.max : null, mean: has ? c!.mean : null, value: has ? c![spec.stat] : null,
      };
    });
    const latest = [...points].reverse().find((p) => p.value !== null) ?? null;
    out.push({ spec, name: seen.name, unit: seen.unit, points, latest, drift: drift(points.map((p) => p.value), spec.drift) });
  }
  return out;
}

// ---------------------------------------------------------------- out of range

/** A Battery cell spread wider than this, in mV, is flagged (confirm: no record row sets it). */
export const CELL_SPREAD_MV = 50;

export interface Flag {
  code: 'redline' | 'hot' | 'low-oil' | 'sensor-fault' | 'pmu-fault' | 'input-fault' | 'fuse-trip' | 'can-timeout' | 'cell-spread';
  text: string;
}

const bits = (c: ColumnDigest | undefined) => `0x${(c?.or ?? 0).toString(16)}`;

/**
 * What is out of range in one drive. The limits are the record's (limitsFrom); the seconds over
 * them are the ICU's own counts (the summary's rev_s, hot_s, low_oil_s, from stats.h); the fault
 * bits are the frames' (LC05 global fault, LC09 input faults, LC25 sensor fault type).
 * Low oil is judged only from the summary: the thinned record's oil pressure is 0 with the key
 * on and the engine stopped, which is not low oil.
 */
export function driveFlags(g: Digest, lim: Limits): Flag[] {
  const f: Flag[] = [];
  const s = g.summary ?? {};
  const col = (k: string) => (g.columns[k]?.n ? g.columns[k] : undefined);
  const rpm = Math.max(col('LC19')?.max ?? 0, s.max_rpm ?? 0);
  if ((lim.redline_rpm !== null && rpm > lim.redline_rpm) || s.rev_s > 0)
    f.push({ code: 'redline', text: `RPM peak ${rpm}${lim.redline_rpm !== null ? `, over the redline of ${lim.redline_rpm}` : ''}${s.rev_s ? ` (${s.rev_s} s above it)` : ''}` });
  const water = col('LC20')?.max ?? null;
  if ((lim.hot_water_c !== null && water !== null && water > lim.hot_water_c) || s.hot_s > 0)
    f.push({ code: 'hot', text: `Water reached ${water ?? s.max_water_c} °C${lim.hot_water_c !== null ? `, over ${lim.hot_water_c} °C` : ''}${s.hot_s ? ` (${s.hot_s} s hot)` : ''}` });
  const runMin = g.summary && s.runtime_s > 0 && s.min_oil_cbar < 0xffff ? s.min_oil_cbar / 100 : null;
  if ((lim.low_oil_bar !== null && runMin !== null && runMin < lim.low_oil_bar) || s.low_oil_s > 0)
    f.push({ code: 'low-oil', text: `Oil pressure fell to ${runMin ?? '?'} bar while running${lim.low_oil_bar !== null ? `, under ${lim.low_oil_bar} bar` : ''}${s.low_oil_s ? ` (${s.low_oil_s} s low)` : ''}` });
  const sf = col('LC25');
  if (sf?.nonzero || s.sensor_faults > 0)
    f.push({ code: 'sensor-fault', text: [sf?.nonzero && `Sensor fault bits set for ${sf.nonzero} s (${bits(sf)})`, s.sensor_faults > 0 && `${s.sensor_faults} sensor fault${s.sensor_faults === 1 ? '' : 's'} counted`].filter(Boolean).join('; ') });
  const gf = col('LC05');
  if (gf?.nonzero) f.push({ code: 'pmu-fault', text: `PMU global fault set for ${gf.nonzero} s (${bits(gf)})` });
  const inf = col('LC09');
  if (inf?.nonzero) f.push({ code: 'input-fault', text: `PMU input faults set for ${inf.nonzero} s (${bits(inf)})` });
  if (s.fuse_trips > 0) f.push({ code: 'fuse-trip', text: `${s.fuse_trips} soft-fuse trip${s.fuse_trips === 1 ? '' : 's'}${s.last_trip_ch ? `, the last on O${s.last_trip_ch}` : ''}` });
  if (s.can_timeouts > 0) f.push({ code: 'can-timeout', text: `${s.can_timeouts} CAN timeout${s.can_timeouts === 1 ? '' : 's'}` });
  const spread = col('LC32')?.max ?? null;
  if (spread !== null && spread > CELL_SPREAD_MV) f.push({ code: 'cell-spread', text: `Cell spread reached ${spread} mV, over ${CELL_SPREAD_MV} mV (confirm)` });
  return f;
}

// ---------------------------------------------------------------- what to look at

export interface Look {
  kind: 'flag' | 'drift' | 'wear';
  text: string;
  detail: string;
  /** the newest drive it was seen in */
  seq?: number;
}

/** The wear rows lookAt reads (wear.ts's Wear has them). */
export interface WearLike {
  item: string;
  status: string;
  detail: string;
}

/**
 * Everything that stands out, most pressing first: flags of the newest drive, then flags seen
 * in earlier drives (one line per kind, with how many drives), then drift, then wear that is
 * overdue or due soon.
 */
export function lookAt(digests: Digest[], lim: Limits, ts: Trend[], wear: WearLike[] = []): Look[] {
  const ds = [...digests].sort((a, b) => a.seq - b.seq);
  const newest = ds.at(-1)?.seq;
  const byCode = new Map<string, { flag: Flag; g: Digest; n: number }>();
  for (const g of ds) {
    for (const flag of driveFlags(g, lim)) {
      const had = byCode.get(flag.code);
      byCode.set(flag.code, { flag, g, n: (had?.n ?? 0) + 1 });
    }
  }
  const flags = [...byCode.values()].sort((a, b) => b.g.seq - a.g.seq);
  const out: Look[] = flags.map(({ flag, g, n }) => ({
    kind: 'flag',
    text: flag.text,
    detail: `${g.seq === newest ? 'the last drive' : `drive ${g.seq}, ${driveDate(g)}`}${n > 1 ? ` · in ${n} of ${ds.length} drives` : ''}`,
    seq: g.seq,
  }));
  for (const t of ts) {
    if (!t.drift) continue;
    const d = t.drift;
    const fmt = (x: number) => x.toFixed(t.spec.digits);
    out.push({
      kind: 'drift',
      text: `${t.name} ${d.dir === 'up' ? 'up' : 'down'} ${fmt(Math.abs(d.by))}${t.unit ? ` ${t.unit}` : ''} over the last ${DRIFT_RECENT} drives`,
      detail: `${t.spec.stat === 'max' ? 'peak' : 'mean'} ${fmt(d.recent)} against ${fmt(d.baseline)} before; margin ${fmt(d.margin)} (confirm)`,
      seq: t.latest?.seq,
    });
  }
  for (const w of wear) if (w.status === 'overdue' || w.status === 'soon') out.push({ kind: 'wear', text: `${w.item}: ${w.status === 'overdue' ? 'overdue' : 'due soon'}`, detail: w.detail });
  return out;
}

// ---------------------------------------------------------------- the small chart

export interface Bar {
  x: number;
  y1: number;
  y2: number;
}

export interface Spark {
  w: number;
  h: number;
  lo: number;
  hi: number;
  /** the stat's line, one SVG path per run of drives that had the channel */
  paths: string[];
  /** each drive's min-to-max */
  bars: Bar[];
  /** the newest point of the line */
  last: { x: number; y: number } | null;
}

/**
 * A drive-by-drive chart, shaped for inline SVG: drives spaced evenly left to right (oldest
 * first), the y range the lowest min to the highest max (widened when flat), a bar from each
 * drive's min to its max and a line through the chosen stat, broken where a drive did not see
 * the channel.
 */
export function spark(points: Pick<TrendPoint, 'min' | 'max' | 'value'>[], w = 160, h = 40, pad = 3): Spark {
  const ys = points.flatMap((p) => [p.min, p.max, p.value]).filter((x): x is number => x !== null && Number.isFinite(x));
  let lo = ys.length ? Math.min(...ys) : 0;
  let hi = ys.length ? Math.max(...ys) : 1;
  if (hi === lo) {
    const d = Math.abs(lo) * 0.05 || 1;
    lo -= d;
    hi += d;
  }
  const n = points.length;
  const X = (i: number) => (n <= 1 ? w / 2 : pad + (i * (w - 2 * pad)) / (n - 1));
  const Y = (v: number) => pad + ((hi - v) * (h - 2 * pad)) / (hi - lo);
  const r = (x: number) => Math.round(x * 100) / 100;
  const paths: string[] = [];
  let run: string[] = [];
  const bars: Bar[] = [];
  let last: Spark['last'] = null;
  points.forEach((p, i) => {
    if (p.min !== null && p.max !== null) bars.push({ x: r(X(i)), y1: r(Y(p.max)), y2: r(Y(p.min)) });
    if (p.value === null) {
      if (run.length) paths.push(run.join(' '));
      run = [];
      return;
    }
    const x = r(X(i));
    const y = r(Y(p.value));
    run.push(`${run.length ? 'L' : 'M'}${x} ${y}`);
    last = { x, y };
  });
  if (run.length) paths.push(run.join(' '));
  return { w, h, lo, hi, paths, bars, last };
}
