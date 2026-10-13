// Bluetooth LE, as the log link needs it (02-APP BL2, D-495): scan, connect, read `info`,
// subscribe to drives / data / status, and write the control characteristic - nothing more.
//
// This is the only file that imports tauri-plugin-blec. Its write is wrapped: `control()`
// takes no UUID, checks the bytes with the firmware's own rule (protocol.controlCheck: one of
// the six opcodes with exactly its fields) and sends them to log_link LL05's characteristic
// and no other. Nothing else in the app can write a characteristic (D-478, D-495). The BMS
// (D-330) is only ever seen in a scan: no code here connects to it, and FEE7 or anything
// named DFU is never addressed.

import { LINK } from './layout.generated';
import { controlCheck } from './protocol';

/** One advertisement, as the Scan page lists it. */
export interface Advert {
  address: string;
  name: string;
  rssi: number;
  services: string[];
  /** company id -> the bytes after it, as the platforms hand it over */
  manufacturerData: Record<number, number[]>;
  bonded?: boolean;
}

export type Notify = 'drives' | 'data' | 'status';

/** What the pull needs of Bluetooth; the real one is blec, the tests use a fake ICU. */
export interface LinkTransport {
  /** false where there is no Bluetooth at all (the browser build) */
  available(): Promise<boolean>;
  /** Android's runtime permissions; true elsewhere */
  permissions(ask: boolean): Promise<boolean>;
  /** Scan for `ms`; `onFound` gets every device seen so far, each time the list changes. */
  scan(onFound: (ads: Advert[]) => void, ms: number, signal?: AbortSignal): Promise<void>;
  connect(address: string, onDisconnect: () => void): Promise<void>;
  disconnect(): Promise<void>;
  readInfo(): Promise<Uint8Array>;
  subscribe(ch: Notify, on: (b: Uint8Array) => void): Promise<void>;
  /** The one write: LL05's control characteristic, a checked opcode only. */
  control(bytes: Uint8Array): Promise<void>;
}

export class RefusedWrite extends Error {}

/** The guard every transport's write goes through. */
export function guardControl(bytes: Uint8Array): Uint8Array {
  if (controlCheck(bytes) < 0) throw new RefusedWrite(`refused: [${[...bytes].join(' ')}] is not one of the log link's six requests`);
  return bytes;
}

const sleep = (ms: number, signal?: AbortSignal) =>
  new Promise<void>((resolve) => {
    const t = setTimeout(resolve, ms);
    signal?.addEventListener('abort', () => (clearTimeout(t), resolve()), { once: true });
  });

const inTauri = () => typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;

/** tauri-plugin-blec (npm @mnlphlp/plugin-blec), on the phone and the desktops. */
export function bleTransport(): LinkTransport {
  const blec = () => import('@mnlphlp/plugin-blec');
  const svc = LINK.uuid.service;
  return {
    async available() {
      if (!inTauri()) return false;
      try {
        return (await (await blec()).getAdapterState()) !== 'Off';
      } catch {
        return false;
      }
    },
    async permissions(ask) {
      if (!/Android/i.test(navigator.userAgent)) return true;
      return (await blec()).checkPermissions(ask);
    },
    async scan(onFound, ms, signal) {
      const b = await blec();
      const run = b.startScan((devs) => onFound(devs.map((d) => ({
        address: d.address, name: d.name, rssi: d.rssi, services: d.services,
        manufacturerData: d.manufacturerData, bonded: d.isBonded,
      }))), ms);
      const stop = () => void b.stopScan().catch(() => undefined);
      signal?.addEventListener('abort', stop, { once: true });
      // The plugin's scan may resolve at once or at its timeout; the deadline is ours either way.
      await Promise.all([run, sleep(ms, signal)]);
      signal?.removeEventListener('abort', stop);
    },
    async connect(address, onDisconnect) {
      const b = await blec();
      // The first read of a bonded-only characteristic makes the OS pair: the passkey is
      // typed while the read waits, so the read may take most of the ICU's 60 s window (LL02).
      await b.setTimeouts({ read: 60_000, write: 10_000 });
      await b.connect(address, onDisconnect);
    },
    async disconnect() {
      await (await blec()).disconnect();
    },
    async readInfo() {
      return new Uint8Array(await (await blec()).read(LINK.uuid.info, svc));
    },
    async subscribe(ch, on) {
      await (await blec()).subscribe(LINK.uuid[ch], svc, (d) => on(new Uint8Array(d)));
    },
    async control(bytes) {
      const ok = guardControl(bytes);
      await (await blec()).send(LINK.uuid.control, [...ok], 'withResponse', svc);
    },
  };
}
