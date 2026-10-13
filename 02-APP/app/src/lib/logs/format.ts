// The ICU's log files, decoded (electrical log_files LF01-LF05, log_channels; 02-APP BL3).
// Every layout here comes from layout.generated.ts - the record's rows and log_store.h's
// layout strings - so a byte that moves in the record moves here when the file is generated.
// A header whose layout CRC is not the one those layouts give is refused, never guessed at.
// Pure: tests/logs.test.ts runs it on a synthetic drive written to the same rows.

import { CHANNELS, FILES, LINK, THIN_LEN, type Channel, type Int } from './layout.generated';
import { crc32Text, parseLayout, readInt, readStruct, sizeOf } from './bytes';
import type { LogName } from './files';

export type Tier = 0 | 1 | 2;
export const TIERS: readonly Tier[] = [0, 1, 2];
export const TIER_NAME = LINK.tier as Record<Tier, string>;
/** LF01: summary.bin, thin.bin, full.bin in each drive's folder */
export const TIER_FILE = { 0: `${TIER_NAME[0]}.bin`, 1: `${TIER_NAME[1]}.bin`, 2: `${TIER_NAME[2]}.bin` } as Record<Tier, LogName>;

/** LF02: the thinned record's layout as the string "LC01:4;LC02:4;…LC53:1;" */
export const thinLayoutString = () => CHANNELS.map((c) => `${c.id}:${c.bytes};`).join('');

/** The header's layout CRC for a tier: CRC-32 of the tier's layout string (LF02). */
export function layoutCrc(tier: Tier): number {
  return crc32Text(tier === 1 ? thinLayoutString() : tier === 0 ? FILES.summaryLayout : FILES.fullLayout);
}

export function recordLen(tier: Tier): number {
  return tier === 1 ? THIN_LEN : tier === 0 ? FILES.summaryLen : FILES.fullLen;
}

export class LogFormatError extends Error {}

export interface Header {
  version: number;
  tier: Tier;
  seq: number;
  /** 0.1 mi */
  startOdoX10: number;
  /** ms since the ICU booted */
  uptimeStart: number;
  /** 0 = the ICU's clock was unset */
  unixStart: number;
  recordLen: number;
  layoutCrc: number;
}

const field = (key: string) => {
  const f = FILES.header.find((x) => x.key === key);
  if (!f) throw new Error(`LF02 has no ${key}`);
  return f as { key: string; type: Int | 'magic'; at: number; value?: string };
};

/** The 32-byte header (LF02), checked: magic, version, tier, record length and layout CRC. */
export function decodeHeader(file: Uint8Array, tier?: Tier): Header {
  if (file.length < FILES.headerLen) throw new LogFormatError(`the file is ${file.length} bytes, shorter than its ${FILES.headerLen}-byte header`);
  const v = new DataView(file.buffer, file.byteOffset, file.byteLength);
  const magic = field('magic');
  const want = magic.value ?? '';
  const got = String.fromCharCode(...file.subarray(magic.at, magic.at + want.length));
  if (got !== want) throw new LogFormatError(`not a log: the magic is "${got}", not "${want}"`);
  const num = (k: string) => {
    const f = field(k);
    return readInt(v, f.at, f.type as Int);
  };
  const h: Header = {
    version: num('version'),
    tier: num('tier') as Tier,
    seq: num('sequence'),
    startOdoX10: num('start_odometer'),
    uptimeStart: num('uptime_at_start'),
    unixStart: num('unix_time_at_start'),
    recordLen: num('record_length'),
    layoutCrc: num('layout_crc_32'),
  };
  if (h.version !== FILES.version) throw new LogFormatError(`log format version ${h.version}; this app reads ${FILES.version}`);
  if (!TIERS.includes(h.tier)) throw new LogFormatError(`tier ${h.tier} is not a tier`);
  if (tier !== undefined && h.tier !== tier) throw new LogFormatError(`a ${TIER_NAME[h.tier]} header where a ${TIER_NAME[tier]} file was expected`);
  if (h.recordLen !== recordLen(h.tier)) throw new LogFormatError(`${TIER_NAME[h.tier]} records of ${h.recordLen} bytes; the record says ${recordLen(h.tier)}`);
  const crc = layoutCrc(h.tier);
  if (h.layoutCrc !== crc)
    throw new LogFormatError(`the ${TIER_NAME[h.tier]} layout CRC is 0x${hex(h.layoutCrc)}, not 0x${hex(crc)}: the ICU writes a layout this app was not built from`);
  return h;
}

export const hex = (n: number) => (n >>> 0).toString(16).padStart(8, '0');

// ---------------------------------------------------------------- summary.bin (LF03)
/** log_summary_t, field for field, from log_store.h's LOG_SUMMARY_LAYOUT */
export const SUMMARY_FIELDS = parseLayout(FILES.summaryLayout);
export type Summary = Record<string, number>;

export function decodeSummary(file: Uint8Array): { header: Header; summary: Summary } {
  const header = decodeHeader(file, 0);
  if (file.length < FILES.headerLen + FILES.summaryLen)
    throw new LogFormatError(`summary.bin is ${file.length} bytes; the header and one summary are ${FILES.headerLen + FILES.summaryLen}`);
  return { header, summary: readStruct(file, SUMMARY_FIELDS, FILES.headerLen) };
}

// ---------------------------------------------------------------- thin.bin (LF04)
/** One value of the thinned record: a channel, or one element of an array channel (LC15.0 is O1). */
export interface Column {
  key: string;
  channel: Channel;
  index: number;
  type: Int;
  at: number;
}

export const COLUMNS: readonly Column[] = (() => {
  const out: Column[] = [];
  let at = 0;
  for (const c of CHANNELS) {
    for (let i = 0; i < c.count; i++) {
      out.push({ key: c.count === 1 ? c.id : `${c.id}.${i}`, channel: c, index: i, type: c.type, at });
      at += sizeOf(c.type);
    }
  }
  if (at !== THIN_LEN) throw new Error(`the channels lay out ${at} bytes, the record is ${THIN_LEN}`);
  return out;
})();

/** A thinned record: each column's raw value. */
export type ThinRecord = Record<string, number>;

/** The record's columns as numbers in their units; a blank (LF04: unseen) is null. */
export function value(col: Column, raw: number): number | null {
  if (col.channel.blank !== null && raw === col.channel.blank) return null;
  return raw * col.channel.scale;
}

/** Every whole record after the header; a record still being written at the end is left off. */
export function decodeThin(file: Uint8Array): { header: Header; records: ThinRecord[]; tail: number } {
  const header = decodeHeader(file, 1);
  const body = file.length - FILES.headerLen;
  const n = Math.floor(body / THIN_LEN);
  const v = new DataView(file.buffer, file.byteOffset, file.byteLength);
  const records: ThinRecord[] = new Array(n);
  for (let r = 0; r < n; r++) {
    const base = FILES.headerLen + r * THIN_LEN;
    const rec: ThinRecord = {};
    for (const c of COLUMNS) rec[c.key] = readInt(v, base + c.at, c.type);
    records[r] = rec;
  }
  return { header, records, tail: body - n * THIN_LEN };
}

// ---------------------------------------------------------------- full.bin (LF05)
export const FULL_FIELDS = parseLayout(FILES.fullLayout);
/** where the `data` bytes sit in a full record, and how many */
const FULL_DATA = (() => {
  let at = 0;
  let first = -1;
  let n = 0;
  for (const [k, t] of FULL_FIELDS) {
    if (k.startsWith('data.')) {
      if (first < 0) first = at;
      n++;
    }
    at += sizeOf(t);
  }
  if (first < 0) throw new Error('LOG_FULL_LAYOUT has no data bytes');
  return { at: first, n };
})();

export interface FullRecord {
  /** ICU uptime */
  ms: number;
  /** the id's low 16 bits */
  id: number;
  /** LF05 flags: b0 extended id, b1 id truncated, b2 IMU sample, b4-7 DLC */
  extended: boolean;
  truncated: boolean;
  imu: boolean;
  dlc: number;
  data: Uint8Array;
}

export function decodeFull(file: Uint8Array): { header: Header; records: FullRecord[]; tail: number } {
  const header = decodeHeader(file, 2);
  const body = file.length - FILES.headerLen;
  const n = Math.floor(body / FILES.fullLen);
  const records: FullRecord[] = new Array(n);
  for (let r = 0; r < n; r++) {
    const at = FILES.headerLen + r * FILES.fullLen;
    const s = readStruct(file, FULL_FIELDS, at);
    const flags = s.flags;
    records[r] = {
      ms: s.ms,
      id: s.id,
      extended: (flags & 0x01) !== 0,
      truncated: (flags & 0x02) !== 0,
      imu: (flags & 0x04) !== 0,
      dlc: flags >> 4,
      data: file.slice(at + FULL_DATA.at, at + FULL_DATA.at + FULL_DATA.n),
    };
  }
  return { header, records, tail: body - n * FILES.fullLen };
}
