// A synthetic drive, written to the record's layouts (electrical log_files LF02-LF05,
// log_channels LC01-LC53) - what the tests and the browser build's stand-in ICU pull. It
// lays bytes out from layout.generated.ts by itself, the way the firmware's LogStore does,
// so a decoder that disagrees with the generated tables fails against it; the firmware's own
// files (tests/fixtures/icu-drive, written by scripts/icu-drive.cpp) are the second check.

import { FILES } from './layout.generated';
import { concat, writeInt, writeStruct } from './bytes';
import { COLUMNS, SUMMARY_FIELDS, FULL_FIELDS, layoutCrc, recordLen, type Tier } from './format';
import type { Int } from './layout.generated';

export interface SynthDrive {
  seq: number;
  seconds: number;
  /** 0.1 mi at key-on */
  startOdoX10: number;
  /** 0 = the clock was unset */
  unixStart: number;
  uptimeStart: number;
  /** tenths of a mile covered each second */
  speedX10PerS?: number;
  /** per-second overrides: column key -> raw value */
  set?: (s: number) => Record<string, number>;
  summary?: Record<string, number>;
}

export function header(tier: Tier, d: SynthDrive): Uint8Array {
  const b = new Uint8Array(FILES.headerLen);
  const v = new DataView(b.buffer);
  const values: Record<string, number> = {
    version: FILES.version, tier, sequence: d.seq, start_odometer: d.startOdoX10, uptime_at_start: d.uptimeStart,
    unix_time_at_start: d.unixStart, record_length: recordLen(tier), layout_crc_32: layoutCrc(tier),
  };
  for (const f of FILES.header) {
    if (f.type === 'magic') b.set(new TextEncoder().encode(f.value), f.at);
    else if (f.type !== 'pad') writeInt(v, f.at, f.type as Int, values[f.key]);
  }
  return b;
}

/** The thinned log: one record a second, an engine idling then pulling away. */
export function thin(d: SynthDrive): Uint8Array {
  const recs = new Uint8Array(d.seconds * recordLen(1));
  const v = new DataView(recs.buffer);
  const per = d.speedX10PerS ?? 0;
  for (let s = 1; s <= d.seconds; s++) {
    const raw: Record<string, number> = {
      LC01: d.uptimeStart + s * 1000,
      LC02: d.startOdoX10 + Math.floor(per * s),
      LC03: 2,
      LC10: 13_900 + (s % 7),
      LC11: 180 + (s % 5),
      LC18: Math.min(4500, 900 + 20 * s), // pulling away, then cruising: under the redline
      LC19: Math.min(5200, 950 + 20 * s),
      LC20: Math.min(88, 40 + s),
      LC21: Math.min(95, 35 + s),
      LC22: 300 + (s % 11),
      LC23: per ? 50 : 0,
      LC28: 615,
      LC30: 13_250,
      'LC31.0': 3312, 'LC31.1': 3313, 'LC31.2': 3311, 'LC31.3': 3314,
      LC40: -128, // the cabin sensor unseen: a blank (LF04)
      LC42: 18,
      'LC50.0': 5, 'LC50.1': -3, 'LC50.2': 100,
      LC52: 40,
      ...(d.set?.(s) ?? {}),
    };
    const base = (s - 1) * recordLen(1);
    for (const c of COLUMNS) writeInt(v, base + c.at, c.type, raw[c.key] ?? 0);
  }
  return concat([header(1, d), recs]);
}

export function summary(d: SynthDrive): Uint8Array {
  const per = d.speedX10PerS ?? 0;
  const s: Record<string, number> = Object.fromEntries(SUMMARY_FIELDS.map(([k]) => [k, 0]));
  Object.assign(s, {
    seq: d.seq, start_odo: d.startOdoX10, end_odo: d.startOdoX10 + Math.floor(per * d.seconds), duration_s: d.seconds,
    unix_start: d.unixStart, uptime_start: d.uptimeStart, max_rpm: Math.min(5200, 950 + 20 * d.seconds), runtime_s: d.seconds,
    distance_x10: Math.floor(per * d.seconds),
    // stats.h samples oil pressure only while running; the thinned record's LC22 is 300-310 cbar
    min_oil_cbar: 300, max_oil_cbar: 310, ...(d.summary ?? {}),
  });
  return concat([header(0, d), writeStruct(SUMMARY_FIELDS, s)]);
}

/** A few full-log records: 0x200 frames and an IMU sample (LF05's flags). */
export function full(d: SynthDrive, frames = 40): Uint8Array {
  const parts: Uint8Array[] = [header(2, d)];
  for (let i = 0; i < frames; i++) {
    const imu = i % 10 === 9;
    const r: Record<string, number> = { ms: d.uptimeStart + i * 50, id: imu ? 0 : 0x200, flags: imu ? 0x04 : 0x80 };
    for (let k = 0; k < 8; k++) r[`data.${k}`] = imu ? 0 : (i + k) & 0xff;
    parts.push(writeStruct(FULL_FIELDS, r));
  }
  return concat(parts);
}

export function files(d: SynthDrive): [Uint8Array, Uint8Array, Uint8Array] {
  return [summary(d), thin(d), full(d)];
}
