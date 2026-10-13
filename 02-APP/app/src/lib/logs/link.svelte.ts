// Connect and log, as the screens see it (02-APP BL2, BL3, BL5): one pull at a time, its
// progress, the drives this device holds, and the Scan page's advertisements. The pull runs
// here, not in a screen, so leaving the page does not stop it. The protocol is pull.ts's, the
// pipeline pipeline.ts's; drives reach the record only as kind=drive answers through app.save,
// the same path Log drive takes (D-401 / D-403).

import { app } from '../app.svelte';
import { toast } from '../toast.svelte';
import { tauriFiles, memoryFiles, type LogFiles } from './files';
import { FakeIcu } from './fake';
import { fileDrives, type Filed } from './pipeline';
import { connectAndLog, PullError, type Progress } from './pull';
import { kvState, memoryState, type DriveState, type StateStore } from './state';
import * as synth from './synth';
import { bleTransport, type Advert, type LinkTransport } from './transport';

export interface Outcome {
  at: string;
  acked: string[];
  problems: string[];
  filed: Filed | null;
  error?: string;
}

const inTauri = () => typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;

/** The browser build's stand-in ICU (?ble=fake): two drives and the Ionic's advertisement. */
function fakeIcu(): FakeIcu {
  const now = Math.floor(Date.now() / 1000);
  const ds: synth.SynthDrive[] = [
    { seq: 11, seconds: 1500, startOdoX10: 1534100, unixStart: now - 86_400, uptimeStart: 2500, speedX10PerS: 0.06 },
    { seq: 12, seconds: 900, startOdoX10: 1534190, unixStart: 0, uptimeStart: 2400, speedX10PerS: 0.05 },
  ];
  return new FakeIcu({
    drives: ds.map((d) => ({ seq: d.seq, files: synth.files(d), startOdoX10: d.startOdoX10, startUnix: d.unixStart })),
    uptimeMs: 960_000,
    others: [
      { address: 'C8:47:8C:10:20:30', name: 'IONIC-12V40', rssi: -71, services: ['0000ffe0-0000-1000-8000-00805f9b34fb'], manufacturerData: { 13012: [0x01, 0x00, 0x64] } },
      { address: '5A:11:22:33:44:55', name: '', rssi: -88, services: [], manufacturerData: { 76: [0x10, 0x05, 0x01] } },
    ],
  });
}

class LogLink {
  running = $state(false);
  progress = $state<Progress | null>(null);
  last = $state<Outcome | null>(null);
  drives = $state<DriveState[]>([]);
  where = $state('');
  available = $state<boolean | null>(null);
  scanning = $state(false);
  adverts = $state<Advert[]>([]);

  #t: LinkTransport | null = null;
  #files: LogFiles | null = null;
  #state: StateStore | null = null;
  #abort: AbortController | null = null;

  async #ready() {
    if (this.#t && this.#files && this.#state) return;
    await app.platformReady;
    const fake = typeof location !== 'undefined' && new URLSearchParams(location.search).get('ble') === 'fake';
    this.#t = fake ? fakeIcu() : bleTransport();
    this.#files = inTauri() ? await tauriFiles() : memoryFiles();
    this.#state = app.platform ? kvState(app.platform.kv) : memoryState();
    this.where = await this.#files.where().catch(() => '');
  }

  /** What this device holds, newest first; and whether Bluetooth is there at all. */
  async load() {
    await this.#ready();
    const st = await this.#state!.load();
    this.drives = Object.values(st.drives).sort((a, b) => b.seq - a.seq);
    this.available = await this.#t!.available();
  }

  /** Inbox targets the record already has, so no drive is filed twice. */
  #known(): Set<string> {
    const s = new Set<string>();
    for (const d of app.snapshot?.manual?.drives ?? []) s.add(d.id);
    for (const a of app.snapshot?.inbox ?? []) if (a.area === '00-CAR' && a.kind === 'drive') s.add(a.target);
    return s;
  }

  /** Connect and log: every drive not yet pulled, and the full log of `full` when asked. */
  async pull(full: number[] = [], thin = true) {
    if (this.running) return;
    await this.#ready();
    this.running = true;
    this.#abort = new AbortController();
    const out: Outcome = { at: new Date().toISOString(), acked: [], problems: [], filed: null };
    try {
      const r = await connectAndLog({
        transport: this.#t!, files: this.#files!, state: this.#state!, full, thin, signal: this.#abort.signal,
        onProgress: (p) => (this.progress = p),
      });
      out.acked = r.acked;
      out.problems = r.problems;
      if (r.drives.length) {
        out.filed = await fileDrives({
          files: this.#files!, state: this.#state!, known: this.#known(), seqs: r.drives.map((d) => d.seq),
          save: async (a) => (await app.save(a)) !== null,
        });
      }
      if (out.filed?.written.length) toast(`${out.filed.written.length} drive${out.filed.written.length === 1 ? '' : 's'} saved from the car - waiting to be filed.`, 'ok');
    } catch (e) {
      out.error = e instanceof Error ? e.message : String(e);
      if (!(e instanceof PullError && e.kind === 'stopped')) toast(out.error, 'warn');
    } finally {
      this.last = out;
      this.running = false;
      this.#abort = null;
      await this.load().catch(() => undefined);
    }
  }

  stop() {
    this.#abort?.abort();
  }

  /** The Scan page (BL5): every advertisement for `ms`, the list replaced as it grows. */
  async scan(ms = 15_000) {
    if (this.scanning || this.running) return;
    await this.#ready();
    this.scanning = true;
    this.#abort = new AbortController();
    try {
      if (!(await this.#t!.available())) throw new Error('Bluetooth is not available on this device.');
      if (!(await this.#t!.permissions(true))) throw new Error('Bluetooth permission was not given.');
      const seen = new Map<string, Advert>();
      await this.#t!.scan((ads) => {
        for (const a of ads) seen.set(a.address, a);
        this.adverts = [...seen.values()].sort((a, b) => b.rssi - a.rssi);
      }, ms, this.#abort.signal);
    } catch (e) {
      toast(e instanceof Error ? e.message : String(e), 'warn');
    } finally {
      this.scanning = false;
      this.#abort = null;
    }
  }
}

export const logLink = new LogLink();
