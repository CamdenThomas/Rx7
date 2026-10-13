// What this device knows about the logs it has pulled (02-APP BL2, BL3): per drive, the
// ICU's last listing of it, the bytes held of each tier (the offset a broken pull resumes
// from, LL09), what was acknowledged, when it was seen open, and whether it has become a
// drives row. Kept in the device's own store (platform kv), never in the record: the record
// gets one kind=drive inbox row per drive, and nothing else (R3).

import type { KV } from '../platform/storage';
import type { Item } from './protocol';

export const KV_KEY = 'logs';

export interface PullMoment {
  /** the phone's clock at the pull, unix seconds */
  unix: number;
  /** the ICU's uptime then (LL03), ms */
  uptimeMs: number;
  /** the ICU's newest drive then: the one open while it was awake */
  driveCount: number;
  /** 0.1 mi (LL03) */
  odometer: number;
}

export interface DriveState {
  seq: number;
  item: Item;
  /** bytes held of summary, thin, full - each from 0 with no gap (the resume offset) */
  held: [number, number, number];
  /** the length and CRC-32 the ICU took an ACK for, per tier */
  acked: [{ len: number; crc: number } | null, { len: number; crc: number } | null, { len: number; crc: number } | null];
  /** the pull at which this drive was the ICU's open one (it was still being written) */
  openAt?: PullMoment;
  /** the newest pull that listed it */
  seenAt?: PullMoment;
  /** set once the pipeline has run: the inbox target written, or why none was */
  filed?: { target?: string; skipped?: string; at: string };
  /** the pipeline's figures, for the Connect page (the full digest is digest.json) */
  brief?: DriveBrief;
}

export interface DriveBrief {
  /** ISO local date-time of the start */
  start: string;
  approx: boolean;
  minutes: number;
  /** miles, one decimal */
  miles: number;
  endOdo: number;
  flags: string[];
}

export interface LogState {
  drives: Record<string, DriveState>;
  last?: PullMoment;
}

export interface StateStore {
  load(): Promise<LogState>;
  save(s: LogState): Promise<void>;
}

export function kvState(kv: KV): StateStore {
  return {
    load: async () => (await kv.get<LogState>(KV_KEY)) ?? { drives: {} },
    save: (s) => kv.set(KV_KEY, s),
  };
}

export function memoryState(init: LogState = { drives: {} }): StateStore & { now: LogState } {
  const box = { now: structuredClone(init) };
  return Object.assign(box, {
    load: async () => structuredClone(box.now),
    save: async (s: LogState) => void (box.now = structuredClone(s)),
  });
}

export function blank(item: Item): DriveState {
  return { seq: item.seq, item, held: [0, 0, 0], acked: [null, null, null] };
}
