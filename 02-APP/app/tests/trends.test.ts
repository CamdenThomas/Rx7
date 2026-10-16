// The car's trends and wear (02-APP BL4): the drift rule, the out-of-range flags, the miles
// and engine hours since a service, and the small chart's shaping - on synthetic drives
// written to the record's layouts (synth.ts) and digested by the pipeline itself.
import { describe, expect, it } from 'vitest';
import * as synth from '../src/lib/logs/synth';
import type * as P from '../src/lib/logs/protocol';
import { digest, type Digest } from '../src/lib/logs/pipeline';
import { memoryFiles } from '../src/lib/logs/files';
import { memoryState } from '../src/lib/logs/state';
import {
  CELL_SPREAD_MV, driveFlags, drift, limitsFrom, loadDigests, lookAt, spark, trends, type Limits,
} from '../src/lib/logs/trends';
import { hoursSince, milesSince, readings, wear } from '../src/lib/logs/wear';
import type { Due, ManualDrive, ManualInterval, ManualService, RawTable } from '../src/lib/model';

const DAY = 86_400;
const T0 = Math.floor(Date.UTC(2026, 9, 1, 12) / 1000); // 1 Oct 2026, midday UTC
const LIM: Limits = { redline_rpm: 7000, hot_water_c: 105, low_oil_bar: 1.0 };

/** One synthetic drive, digested: `day` days after T0, 300 s, 0.05 mi a second (15 mi), from 150,400 + 20 × seq mi. */
function drive(seq: number, day: number, set?: (s: number) => Record<string, number>, summary?: Record<string, number>): Digest {
  const d: synth.SynthDrive = { seq, seconds: 300, startOdoX10: 1_504_000 + seq * 200, unixStart: T0 + day * DAY, uptimeStart: 2000, speedX10PerS: 0.5, set, summary };
  return digest(synth.thin(d), synth.summary(d), { seq, item: {} as P.Item, held: [0, 0, 0], acked: [null, null, null] }, null, T0 + 400 * DAY)!;
}

describe('the drift rule', () => {
  const rule = { abs: 5, why: '' };
  it('marks the last three drives stepping away together, up or down', () => {
    expect(drift([88, 88, 89, 87, 96, 95, 97], rule)).toMatchObject({ dir: 'up', baseline: 88, recent: 96 });
    expect(drift([88, 88, 88, 80, 81, 79], rule)).toMatchObject({ dir: 'down', by: -8 });
  });
  it('does not mark one odd drive, a step inside the margin, too few drives, or a channel with no rule', () => {
    expect(drift([88, 88, 88, 88, 99, 88], rule)).toBeNull();
    expect(drift([88, 88, 88, 92, 92, 92], rule)).toBeNull();
    expect(drift([88, 88, 96, 96, 96], rule)).toBeNull(); // only two earlier drives
    expect(drift([88, 88, 88, 99, 99, 99], null)).toBeNull();
  });
  it('takes the larger of the absolute and the relative margin, and skips drives that missed the channel', () => {
    const r = { abs: 2, rel: 0.2, why: '' };
    expect(drift([20, 20, 20, 23, 23, 23], r)).toBeNull(); // 20 % of 20 is 4
    expect(drift([20, null, 20, 20, 25, null, 25, 25], r)).toMatchObject({ dir: 'up', margin: 4 });
  });
  it('follows a channel across synthetic drives: the water peak climbing 8 °C over the last three', () => {
    const ds = [1, 2, 3, 4, 5, 6].map((n) => drive(n, n, n > 3 ? (s) => ({ LC20: Math.min(96, 40 + s) }) : undefined));
    const water = trends(ds).find((t) => t.spec.key === 'LC20')!;
    expect(water.unit).toBe('°C');
    expect(water.points.map((p) => p.value)).toEqual([88, 88, 88, 96, 96, 96]);
    expect(water.drift).toMatchObject({ dir: 'up', by: 8 });
    expect(water.latest?.seq).toBe(6);
    // a steady channel carries no mark; one with no rule (the RPM peak) never does
    expect(trends(ds).find((t) => t.spec.key === 'LC10')!.drift).toBeNull();
    expect(trends(ds).find((t) => t.spec.key === 'LC19')!.spec.drift).toBeNull();
    // a channel no drive saw is left out (the cabin temperature is blank in synth: LF04)
    expect(trends(ds).some((t) => t.spec.key === 'LC40')).toBe(false);
  });
});

describe('the out-of-range flags', () => {
  it('reads the limits from the record, never from the code', () => {
    const t: RawTable = {
      area: '02-electrical', table: 'params', columns: ['key', 'value', 'unit'],
      rows: [['redline_rpm', '6500', ''], ['hot_water_c', '100', ''], ['low_oil_bar', '1.2', '']],
    };
    expect(limitsFrom([t])).toEqual({ redline_rpm: 6500, hot_water_c: 100, low_oil_bar: 1.2 });
    expect(limitsFrom([])).toEqual({ redline_rpm: null, hot_water_c: null, low_oil_bar: null });
  });
  it('flags nothing on a drive in range', () => {
    expect(driveFlags(drive(1, 0), LIM)).toEqual([]);
  });
  it('flags the redline, hot water, low oil, faults, trips, CAN timeouts and a wide cell spread', () => {
    const g = drive(2, 0, (s) => ({
      LC19: s === 100 ? 7200 : 3000, LC20: s > 250 ? 108 : 85, LC05: s === 10 ? 0x04 : 0, LC09: s < 3 ? 0x01 : 0, LC25: s === 20 ? 0x02 : 0,
      LC32: s === 200 ? CELL_SPREAD_MV + 12 : 10,
    }), { rev_s: 1, hot_s: 50, min_oil_cbar: 80, low_oil_s: 4, fuse_trips: 2, last_trip_ch: 7, can_timeouts: 3, sensor_faults: 1 });
    const f = driveFlags(g, LIM);
    expect(f.map((x) => x.code)).toEqual(['redline', 'hot', 'low-oil', 'sensor-fault', 'pmu-fault', 'input-fault', 'fuse-trip', 'can-timeout', 'cell-spread']);
    expect(f[0].text).toMatch(/7200, over the redline of 7000 \(1 s above it\)/);
    expect(f[1].text).toMatch(/108 °C, over 105 °C/);
    expect(f[2].text).toMatch(/0.8 bar while running, under 1 bar/);
    expect(f.find((x) => x.code === 'pmu-fault')!.text).toMatch(/1 s \(0x4\)/);
    expect(f.find((x) => x.code === 'fuse-trip')!.text).toMatch(/2 soft-fuse trips, the last on O7/);
  });
  it('judges by the record limit: a lower redline in params flags the same drive', () => {
    const g = drive(3, 0, (s) => ({ LC19: s === 100 ? 6800 : 3000 }), { max_rpm: 6800 });
    expect(driveFlags(g, LIM)).toEqual([]);
    expect(driveFlags(g, { ...LIM, redline_rpm: 6500 }).map((x) => x.code)).toEqual(['redline']);
  });
  it('does not call key-on with the engine stopped low oil: only the running minimum counts', () => {
    const g = drive(4, 0, (s) => ({ LC22: s < 30 ? 0 : 300 }));
    expect(g.columns.LC22.min).toBe(0);
    expect(driveFlags(g, LIM)).toEqual([]);
  });
  it('lists what to look at: the newest flags first, counted across drives, then drift, then wear', () => {
    const hot = (s: number) => ({ LC20: s > 280 ? 110 : 85 });
    const ds = [drive(1, 0, hot), drive(2, 1), drive(3, 2, hot), drive(4, 3, undefined, { can_timeouts: 1 })];
    const looks = lookAt(ds, LIM, trends(ds), [{ item: 'Engine oil and filter', status: 'overdue', detail: 'x' }, { item: 'Plugs', status: 'ok', detail: '' }]);
    expect(looks.map((l) => l.kind)).toEqual(['flag', 'flag', 'wear']);
    expect(looks[0]).toMatchObject({ seq: 4, detail: 'the last drive' });
    expect(looks[1].detail).toMatch(/drive 3, .* · in 2 of 4 drives/);
    expect(looks[2].text).toBe('Engine oil and filter: overdue');
  });
});

describe('wear against the intervals', () => {
  const iv = (id: string, every_miles: string, every_months: string, due: Due, extra: Record<string, string> = {}): ManualInterval =>
    ({ id, item: id, every_miles, every_months, spec: '', source: '', note: '', due, ...extra }) as ManualInterval;
  const svc = (id: string, date: string, mileage: string, items: string): ManualService => ({ id, date, mileage, work: '', items, parts: '', notes: '', fitted: [] });
  const service = [svc('SV01', '2025-08', '', 'plugs'), svc('SV04', '2026-07', '150000', 'oil'), svc('SV05', '2026-07-20', '', 'air_filter')];
  const drives: ManualDrive[] = [{ id: 'odo-1', date: '2026-09-01', odometer: '150400', kind: 'set', from: '', to: '', note: '', miles: 400 }];
  const odo = { miles: 150400, date: '2026-09-01', source: 'set', ref: 'odo-1' };
  // three pulled drives in October, 15 mi each, the last ending at 150,475; half an hour running each
  const ds = [1, 2, 3].map((n) => drive(n, n, undefined, { runtime_s: 1800 }));

  it('counts the miles from the visit when it has a mileage, against the newest reading', () => {
    const last = { service: 'SV04', date: '2026-07', miles: 150000 };
    const now = { date: '2026-10-04', miles: 150460, from: '' };
    expect(milesSince(last, now, [], [])).toEqual({ miles: 460, basis: 'service', from: 'SV04 at 150000' });
  });
  it('without a mileage, counts from the newest reading on or before the visit (at most), else the logged drives (at least)', () => {
    const all = readings(drives, service, []);
    const now = { date: '2026-09-01', miles: 150400, from: '' };
    expect(milesSince({ service: 'SV05', date: '2026-07-20', miles: null }, now, all, [])).toMatchObject({ miles: 400, basis: 'reading' });
    expect(milesSince({ service: 'SV01', date: '2025-08', miles: null }, now, all, ds)).toMatchObject({ miles: 45, basis: 'logged' });
    expect(milesSince({ service: 'SV01', date: '2025-08', miles: null }, now, all, [])).toBeNull();
    expect(milesSince(null, now, all, ds)).toBeNull();
  });
  it('adds the engine hours of the pulled drives since the visit, and says when the logs start after it', () => {
    expect(hoursSince('2026-07-01', ds)).toEqual({ hours: 1.5, drives: 3, complete: false, byDuration: 0 });
    expect(hoursSince('2026-10-03', ds)).toMatchObject({ hours: 1, drives: 2, complete: true });
    expect(hoursSince('2026-07-01', [])).toBeNull();
  });
  it("keeps rx7.py's status, adds the hours, and raises only from an interval kept in hours or a floor of miles", () => {
    const ok: Due = { last: { service: 'SV04', date: '2026-07', miles: 150000 }, next_miles: 157500, next_date: '2027-02-13', status: 'ok', miles_left: 7100, days_left: 120 };
    const never: Due = { last: null, next_miles: null, next_date: '', status: 'never' };
    const air: Due = { last: { service: 'SV05', date: '2026-07-20', miles: null }, next_miles: null, next_date: '2028-12-01', status: 'ok', miles_left: null, days_left: 800 };
    const plugs: Due = { last: { service: 'SV01', date: '2025-08', miles: null }, next_miles: null, next_date: '2028-02-01', status: 'ok', miles_left: null, days_left: 500 };
    const hourly: Due = { ...ok };
    const ws = wear(
      [
        iv('oil', '7500', '7.5', ok), iv('coolant', '30000', '30', never), iv('air_filter', '400', '30', air), iv('plugs', '40', '30', plugs),
        iv('hourly', '', '', hourly, { every_hours: '2' }), iv('premix', '', '', { last: null, next_miles: null, next_date: '', status: 'each' }),
      ],
      odo, drives, service, ds,
    );
    const by = Object.fromEntries(ws.map((w) => [w.id, w]));
    expect(by.premix).toBeUndefined(); // every fill: no interval to wear against
    expect(by.oil).toMatchObject({ status: 'ok', milesLeft: 7500 - 475, milesSince: { basis: 'service' }, hoursSince: { hours: 1.5 } });
    expect(by.oil.milesSince!.miles).toBe(Math.floor(ds[2].endOdoX10 / 10) - 150000); // a pulled drive ended past the record's odometer
    expect(by.coolant).toMatchObject({ status: 'never', milesSince: null });
    expect(by.coolant.detail).toMatch(/No service visit has done it yet/);
    // a ceiling (a reading before the visit) shows but does not move the status
    expect(by.air_filter.status).toBe('ok');
    expect(by.air_filter.milesSince!.basis).toBe('reading');
    // a floor (the pulled drives since) over the interval is overdue
    expect(by.plugs).toMatchObject({ status: 'overdue', milesLeft: -5, milesSince: { basis: 'logged', miles: 45 } });
    // an interval in hours: 2 h less 1.5 h run is due soon
    expect(by.hourly).toMatchObject({ hoursLeft: 0.5, status: 'soon' });
    expect(ws[0].status).toBe('overdue');
  });
});

describe('the small chart', () => {
  it('spaces the drives evenly, scales to the lowest min and highest max, and breaks the line at a gap', () => {
    const s = spark([
      { min: 0, max: 10, value: 5 },
      { min: null, max: null, value: null },
      { min: 5, max: 10, value: 10 },
    ], 100, 20, 0);
    expect([s.lo, s.hi]).toEqual([0, 10]);
    expect(s.bars).toEqual([{ x: 0, y1: 0, y2: 20 }, { x: 100, y1: 0, y2: 10 }]);
    expect(s.paths).toEqual(['M0 10', 'M100 0']);
    expect(s.last).toEqual({ x: 100, y: 0 });
  });
  it('centres one drive and widens a flat range', () => {
    const s = spark([{ min: 13.9, max: 13.9, value: 13.9 }], 100, 20, 0);
    expect(s.paths).toEqual(['M50 10']);
    expect(s.hi - s.lo).toBeCloseTo(13.9 * 0.1, 6);
  });
});

describe('the digests as a cache', () => {
  it('reads digest.json, and rebuilds it from the drive files when it is missing', async () => {
    const files = memoryFiles();
    const d: synth.SynthDrive = { seq: 9, seconds: 120, startOdoX10: 1_500_000, unixStart: T0, uptimeStart: 1000, speedX10PerS: 0.5 };
    const [sum, thin] = synth.files(d);
    await files.write(9, 'summary.bin', 0, sum);
    await files.write(9, 'thin.bin', 0, thin);
    const first = await loadDigests(files, memoryState());
    expect(first.rebuilt).toEqual([9]);
    expect(first.digests[0]).toMatchObject({ seq: 9, durationS: 120, miles: 6 });
    expect((await files.read(9, 'digest.json')).length).toBeGreaterThan(0);
    const again = await loadDigests(files, memoryState());
    expect(again.rebuilt).toEqual([]);
    expect(again.digests[0].columns.LC20.max).toBe(first.digests[0].columns.LC20.max);
  });
});
