// A stand-in ICU behind the LinkTransport interface: the C3 and the Teensy as log_link and the
// firmware (du_radio.ino, log_store.h's LogServer) describe them - status on every change,
// DATA chunked at MTU - 7 with its offset, END's CRC-32 of the whole tier, pulled set only on
// an ACK whose CRC matches, LIST 0 naming the drives whose summary or thin is not pulled. The
// tests drive the pull against it (a cut link, a bad CRC, a wrong protocol); the browser build
// can use it too (?ble=fake). It holds every control write it was sent.

import { LINK } from './layout.generated';
import { crc32, writeStruct } from './bytes';
import type { Status } from './protocol';
import type { Tier } from './format';
import { guardControl, type Advert, type LinkTransport, type Notify } from './transport';

export interface FakeDrive {
  seq: number;
  files: [Uint8Array, Uint8Array, Uint8Array];
  pulled?: [{ len: number; crc: number } | null, { len: number; crc: number } | null, { len: number; crc: number } | null];
  startOdoX10?: number;
  startUnix?: number;
}

export interface FakeIcuOptions {
  drives: FakeDrive[];
  protocol?: number;
  rtcSet?: boolean;
  unixTime?: number;
  uptimeMs?: number;
  odometerX10?: number;
  mtu?: number;
  name?: string;
  /** the link drops once this many file bytes have gone out (a walk-away mid-pull) */
  cutAfter?: number;
  /** END carries a wrong CRC for this (seq, tier), this many times */
  badCrc?: { seq: number; tier: Tier; times: number };
  /** a DATA notification lost once at this file offset of the thin tier */
  dropAt?: number;
  /** nothing is advertised (the key is off) */
  asleep?: boolean;
  /** extra advertisements beside the ICU (the Scan page; the BMS) */
  others?: Advert[];
}

const tick = () => new Promise((r) => setTimeout(r, 0));

export class FakeIcu implements LinkTransport {
  writes: Uint8Array[] = [];
  connects = 0;
  sent = 0;
  connected = false;
  rtcSet: boolean;
  unixTime: number;
  #subs: Partial<Record<Notify, (b: Uint8Array) => void>> = {};
  #onDisconnect: (() => void) | null = null;
  #status: Status = { state: 0, seq: 0, tier: 0, sent: 0, total: 0, crc32: 0, err: 0 };
  #run = 0;
  #dropped = false;

  constructor(public o: FakeIcuOptions) {
    this.rtcSet = !!o.rtcSet;
    this.unixTime = o.unixTime ?? 0;
    for (const d of o.drives) d.pulled ??= [null, null, null];
  }

  async available() {
    return true;
  }
  async permissions() {
    return true;
  }
  async scan(onFound: (ads: Advert[]) => void, ms: number, signal?: AbortSignal) {
    const ads: Advert[] = [...(this.o.others ?? [])];
    if (!this.o.asleep) ads.push({ address: 'AA:BB:CC:00:11:22', name: this.o.name ?? LINK.name, rssi: -58, services: [LINK.uuid.service], manufacturerData: {} });
    await tick();
    onFound(ads);
    if (!ads.some((a) => a.name === LINK.name)) await new Promise((r) => setTimeout(r, Math.min(ms, 50)));
    void signal;
  }
  async connect(_address: string, onDisconnect: () => void) {
    this.connected = true;
    this.connects++;
    this.#onDisconnect = onDisconnect;
    this.#subs = {};
  }
  async disconnect() {
    this.connected = false;
    this.#run++;
  }
  async readInfo() {
    const notPulled = this.o.drives.filter((d) => !this.#isPulled(d, 0) || !this.#isPulled(d, 1)).length;
    return writeStruct(LINK.info, {
      protocol: this.o.protocol ?? LINK.protocol, icu_firmware: 600, odometer: this.o.odometerX10 ?? 0,
      drive_count: Math.max(0, ...this.o.drives.map((d) => d.seq)), drives_not_fully_pulled: notPulled, card_free: 80,
      rtc_set: this.rtcSet ? 1 : 0, unix_time: this.rtcSet ? this.unixTime : 0, uptime_ms: this.o.uptimeMs ?? 600_000,
    });
  }
  async subscribe(ch: Notify, on: (b: Uint8Array) => void) {
    this.#subs[ch] = on;
  }

  #isPulled(d: FakeDrive, t: Tier) {
    const p = d.pulled![t];
    return !!p && p.len !== 0 && p.len === d.files[t].length;
  }
  #notify(ch: Notify, b: Uint8Array) {
    if (this.connected) this.#subs[ch]?.(b);
  }
  #setStatus(s: Partial<Status>) {
    const next = { ...this.#status, ...s };
    if (JSON.stringify(next) === JSON.stringify(this.#status)) return; // the C3 notifies on change
    this.#status = next;
    this.#notify('status', writeStruct(LINK.status, next));
  }
  get status() {
    return this.#status;
  }
  #item(d: FakeDrive) {
    let pulled = 0;
    for (const t of [0, 1, 2] as Tier[]) if (this.#isPulled(d, t)) pulled |= 1 << t;
    return writeStruct(LINK.item, {
      seq: d.seq, start_odo: d.startOdoX10 ?? 0, duration_s: Math.floor(Math.max(0, d.files[1].length - 32) / 137),
      start_unix: d.startUnix ?? 0, pulled, summary_len: d.files[0].length, thin_len: d.files[1].length, full_len: d.files[2].length,
    });
  }

  async control(bytes: Uint8Array) {
    guardControl(bytes); // the same wall the real transport has
    if (!this.connected) throw new Error('not connected');
    this.writes.push(bytes.slice());
    const v = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    const run = ++this.#run;
    switch (bytes[0]) {
      case LINK.op.LIST: {
        const from = v.getUint32(1, true);
        this.#setStatus({ state: 1, err: 0 });
        void (async () => {
          for (const d of [...this.o.drives].sort((a, b) => a.seq - b.seq)) {
            if (from === 0 ? this.#isPulled(d, 0) && this.#isPulled(d, 1) : d.seq < from) continue;
            await tick();
            if (run !== this.#run) return;
            this.#notify('drives', this.#item(d));
          }
          await tick();
          if (run !== this.#run) return;
          this.#notify('drives', writeStruct(LINK.item, { seq: 0, start_odo: 0, duration_s: 0, start_unix: 0, pulled: 0, summary_len: 0, thin_len: 0, full_len: 0 }));
          this.#setStatus({ state: 0, err: 0 });
        })();
        return;
      }
      case LINK.op.OPEN: {
        const seq = v.getUint32(1, true);
        const tier = bytes[5] as Tier;
        const offset = v.getUint32(6, true);
        this.#setStatus({ state: 2, seq, tier, sent: offset, total: 0, crc32: 0, err: 0 });
        const d = this.o.drives.find((x) => x.seq === seq);
        void (async () => {
          await tick();
          if (run !== this.#run) return;
          const file = d?.files[tier];
          if (!file || offset > file.length) return this.#setStatus({ state: 4, err: 2 });
          this.#setStatus({ total: file.length });
          const chunk = (this.o.mtu ?? LINK.mtu) - 7;
          let pos = offset;
          while (pos < file.length) {
            for (let k = 0; k < 8 && pos < file.length; k++) {
              const n = Math.min(chunk, file.length - pos);
              if (this.o.cutAfter !== undefined && this.sent + n > this.o.cutAfter && !this.#dropped) {
                this.#dropped = true;
                this.connected = false;
                this.#onDisconnect?.();
                return;
              }
              const lose = this.o.dropAt !== undefined && tier === 1 && pos <= this.o.dropAt && this.o.dropAt < pos + n && !this.#lost;
              if (lose) this.#lost = true;
              else {
                const b = new Uint8Array(4 + n);
                new DataView(b.buffer).setUint32(0, pos, true);
                b.set(file.subarray(pos, pos + n), 4);
                this.#notify('data', b);
              }
              this.sent += n;
              pos += n;
              this.#setStatus({ sent: pos });
            }
            await tick();
            if (run !== this.#run) return;
          }
          let crc = crc32(file);
          const bad = this.o.badCrc;
          if (bad && bad.seq === seq && bad.tier === tier && bad.times > 0) {
            bad.times--;
            crc = (crc ^ 0xdeadbeef) >>> 0;
          }
          this.#setStatus({ state: 3, crc32: crc, err: 0 });
        })();
        return;
      }
      case LINK.op.ACK: {
        const seq = v.getUint32(1, true);
        const tier = bytes[5] as Tier;
        const crc = v.getUint32(6, true);
        const d = this.o.drives.find((x) => x.seq === seq);
        await tick();
        if (!d) return this.#setStatus({ state: 4, seq, tier, err: 2 });
        if (crc !== crc32(d.files[tier])) return this.#setStatus({ state: 4, seq, tier, err: 7 });
        d.pulled![tier] = { len: d.files[tier].length, crc };
        this.#setStatus({ state: 3, seq, tier, err: 0 }); // unchanged when it was the transfer just done
        return;
      }
      case LINK.op.SET_TIME: {
        const unix = v.getUint32(1, true);
        if (!this.rtcSet || Math.abs(this.unixTime - unix) > LINK.timeSlackS) {
          this.rtcSet = true;
          this.unixTime = unix;
        }
        return;
      }
      default:
        return; // ABORT, PING
    }
  }
  #lost = false;
}
