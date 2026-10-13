// Bytes for the log link: CRC-32, little-endian structs, and the firmware's layout strings.
// Pure - no Tauri, no DOM - so every byte rule is unit-tested (tests/logs.test.ts).

import type { Int } from './layout.generated';

const SIZE: Record<Int, number> = { u8: 1, i8: 1, u16: 2, i16: 2, u32: 4, i32: 4 };
export const sizeOf = (t: Int) => SIZE[t];

// ---------------------------------------------------------------- CRC-32
// IEEE 802.3 / zlib: reflected 0xEDB88320, init and final xor 0xFFFFFFFF;
// "123456789" -> 0xCBF43926 - the firmware's ll_crc32 (icu/log_link.h, LL08, LL13).
const TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

export const CRC32_INIT = 0xffffffff;
export function crc32Update(crc: number, data: Uint8Array): number {
  let c = crc >>> 0;
  for (let i = 0; i < data.length; i++) c = TABLE[(c ^ data[i]) & 0xff] ^ (c >>> 8);
  return c >>> 0;
}
export const crc32Final = (crc: number) => (crc ^ 0xffffffff) >>> 0;
export const crc32 = (data: Uint8Array) => crc32Final(crc32Update(CRC32_INIT, data));
export const crc32Text = (s: string) => crc32(new TextEncoder().encode(s));

// ---------------------------------------------------------------- little-endian fields
export function readInt(v: DataView, at: number, t: Int): number {
  switch (t) {
    case 'u8': return v.getUint8(at);
    case 'i8': return v.getInt8(at);
    case 'u16': return v.getUint16(at, true);
    case 'i16': return v.getInt16(at, true);
    case 'u32': return v.getUint32(at, true);
    case 'i32': return v.getInt32(at, true);
  }
}

export function writeInt(v: DataView, at: number, t: Int, x: number) {
  switch (t) {
    case 'u8': return v.setUint8(at, x);
    case 'i8': return v.setInt8(at, x);
    case 'u16': return v.setUint16(at, x, true);
    case 'i16': return v.setInt16(at, x, true);
    case 'u32': return v.setUint32(at, x >>> 0, true);
    case 'i32': return v.setInt32(at, x, true);
  }
}

export type Fields = readonly (readonly [string, Int])[];
export const fieldsLen = (f: Fields) => f.reduce((n, [, t]) => n + SIZE[t], 0);

/** A packed struct, as the firmware's `__attribute__((packed))` lays it out. */
export function readStruct(bytes: Uint8Array, f: Fields, at = 0): Record<string, number> {
  const v = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const out: Record<string, number> = {};
  for (const [k, t] of f) {
    out[k] = readInt(v, at, t);
    at += SIZE[t];
  }
  return out;
}

export function writeStruct(f: Fields, values: Record<string, number>): Uint8Array {
  const b = new Uint8Array(fieldsLen(f));
  const v = new DataView(b.buffer);
  let at = 0;
  for (const [k, t] of f) {
    const x = values[k];
    if (typeof x !== 'number' || !Number.isFinite(x)) throw new Error(`field ${k} is missing`);
    writeInt(v, at, t, x);
    at += SIZE[t];
  }
  return b;
}

// ---------------------------------------------------------------- layout strings
/**
 * The firmware's layout string ("a,b:u32;c:i16;data:u8x8;", log_store.h) as packed fields,
 * in order: `data:u8x8` is eight u8s named data.0 .. data.7.
 */
export function parseLayout(s: string): [string, Int][] {
  const out: [string, Int][] = [];
  for (const group of s.split(';').filter(Boolean)) {
    const [names, type] = group.split(':');
    const m = (type ?? '').match(/^([ui](?:8|16|32))(?:x(\d+))?$/);
    if (!m || !names) throw new Error(`layout group '${group}' is not names:type`);
    const t = m[1] as Int;
    const n = m[2] ? Number(m[2]) : 1;
    for (const name of names.split(',')) {
      if (n === 1) out.push([name, t]);
      else for (let i = 0; i < n; i++) out.push([`${name}.${i}`, t]);
    }
  }
  return out;
}

export function concat(parts: Uint8Array[]): Uint8Array {
  const n = parts.reduce((s, p) => s + p.length, 0);
  const out = new Uint8Array(n);
  let at = 0;
  for (const p of parts) {
    out.set(p, at);
    at += p.length;
  }
  return out;
}
