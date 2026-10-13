// The log link's messages (electrical log_link LL03-LL10, D-494; 02-APP BL2): what the app
// reads from the ICU and the one thing it writes. Every layout is layout.generated.ts's, read
// from the record. Pure - tests/logs.test.ts holds it to the firmware's struct sizes.

import { LINK } from './layout.generated';
import { fieldsLen, readStruct, writeStruct, type Fields } from './bytes';
import type { Tier } from './format';

export type Op = keyof typeof LINK.op;
export const OPS = Object.keys(LINK.op) as Op[];

/** LL03 */
export interface Info {
  protocol: number;
  icu_firmware: number;
  /** 0.1 mi */
  odometer: number;
  drive_count: number;
  drives_not_fully_pulled: number;
  card_free: number;
  rtc_set: number;
  unix_time: number;
  uptime_ms: number;
}

/** LL04: one drive the ICU holds; seq 0 ends a list */
export interface Item {
  seq: number;
  /** 0.1 mi */
  start_odo: number;
  duration_s: number;
  /** 0 = the clock was unset */
  start_unix: number;
  /** b0 summary, b1 thin, b2 full */
  pulled: number;
  summary_len: number;
  thin_len: number;
  full_len: number;
}

/** LL10 */
export interface Status {
  state: number;
  seq: number;
  tier: number;
  sent: number;
  total: number;
  crc32: number;
  err: number;
}

const as = <T>(r: Record<string, number>) => r as unknown as T;
const need = (b: Uint8Array, f: Fields, what: string) => {
  if (b.length < fieldsLen(f)) throw new Error(`${what} is ${b.length} bytes; the record lays out ${fieldsLen(f)}`);
};

export const INFO_LEN = fieldsLen(LINK.info);
export const ITEM_LEN = fieldsLen(LINK.item);
export const STATUS_LEN = fieldsLen(LINK.status);
export const DATA_HEAD_LEN = fieldsLen(LINK.dataHead);

export function decodeInfo(b: Uint8Array): Info {
  need(b, LINK.info, 'info');
  return as<Info>(readStruct(b, LINK.info));
}
export function decodeItem(b: Uint8Array): Item {
  need(b, LINK.item, 'a drives entry');
  return as<Item>(readStruct(b, LINK.item));
}
export function decodeStatus(b: Uint8Array): Status {
  need(b, LINK.status, 'status');
  return as<Status>(readStruct(b, LINK.status));
}
/** LL09: the offset, then the file's bytes from there */
export function decodeData(b: Uint8Array): { offset: number; bytes: Uint8Array } {
  need(b, LINK.dataHead, 'a data notification');
  return { offset: readStruct(b, LINK.dataHead).offset, bytes: b.subarray(DATA_HEAD_LEN) };
}

/** LL10's state and err codes, by number */
export const STATE = Object.fromEntries(Object.entries(LINK.state).map(([n, w]) => [w, Number(n)])) as Record<string, number>;
export const errText = (e: number) => (LINK.err as Record<string, string>)[String(e)] ?? `error ${e}`;
export const ERR_NONE = 0;
/** LL18: err 7, an ACK whose CRC does not match the tier */
export const ERR_CRC = 7;

// ---------------------------------------------------------------- the control write (LL05)
/** A control write: the opcode, then exactly its fields (LL06-LL08). */
export function encode(op: Op, values: Record<string, number> = {}): Uint8Array {
  const code = LINK.op[op];
  if (code === undefined) throw new Error(`${op} is not one of the six opcodes`);
  const body = writeStruct(LINK.opFields[op], values);
  const out = new Uint8Array(1 + body.length);
  out[0] = code;
  out.set(body, 1);
  return out;
}

/**
 * The firmware's ll_control_check, here: the opcode if `v` is one of the six with exactly its
 * fields (and a tier that is a tier), else -1. The app's only write passes through this first,
 * so nothing else can leave it (D-478, D-495).
 */
export function controlCheck(v: Uint8Array): number {
  if (!v.length) return -1;
  const op = OPS.find((o) => LINK.op[o] === v[0]);
  if (!op) return -1;
  const f = LINK.opFields[op];
  if (fieldsLen(f) !== v.length - 1) return -1;
  if (f.some(([k]) => k === 'tier')) {
    const t = readStruct(v.subarray(1), f).tier;
    if (!(t in LINK.tier)) return -1;
  }
  return v[0];
}

export const list = (fromSeq = 0) => encode('LIST', { from_seq: fromSeq });
export const open = (seq: number, tier: Tier, offset: number) => encode('OPEN', { seq, tier, offset });
export const ack = (seq: number, tier: Tier, crc: number) => encode('ACK', { seq, tier, crc32: crc });
export const abort = () => encode('ABORT');
export const setTime = (unix: number) => encode('SET_TIME', { unix });
export const ping = () => encode('PING');

/** LL08: SET_TIME is applied when the ICU's clock is unset or off by more than the slack. */
export const timeWanted = (info: Info, nowUnix: number) =>
  !info.rtc_set || info.unix_time === 0 || Math.abs(info.unix_time - nowUnix) > LINK.timeSlackS;
