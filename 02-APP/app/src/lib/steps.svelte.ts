// The TODO manual's two pieces of state (02-electrical D-533): every project's briefs and
// steps, indexed once per snapshot (briefs.ts does the reading), and the step ticks, which
// live on this device only.
//
// A tick is never a fact of the record and never his answer: it is written to the device's
// own store (the same one the drafts use), never to the tree, and a row is done only when he
// answers it through the app's answer path. Reads (R6): briefs, steps, parts through briefs.ts.

import { untrack } from 'svelte';
import { app } from './app.svelte';
import { indexManuals, type AreaManual } from './briefs';

class Manuals {
  /** Rebuilt when the record is read again; a lookup per row after that. */
  all = $derived.by(() => {
    const s = app.snapshot;
    return s ? indexManuals({ tables: s.tables, work: s.work, blocks: s.blocks }) : new Map<string, AreaManual>();
  });

  of(area: string): AreaManual | undefined {
    return this.all.get(area);
  }

  /** Whether this project's TODO reads as a manual: at least one row carries a brief. */
  has(area: string): boolean {
    return (this.all.get(area)?.briefs ?? 0) > 0;
  }
}

export const manuals = new Manuals();

const NONE: string[] = [];

/** The stored value, whatever a damaged store hands back: only lists of strings survive. */
function clean(v: unknown): Record<string, string[]> {
  const out: Record<string, string[]> = {};
  if (!v || typeof v !== 'object') return out;
  for (const [k, list] of Object.entries(v as Record<string, unknown>)) {
    if (Array.isArray(list)) out[k] = list.filter((x): x is string => typeof x === 'string');
  }
  return out;
}

class Ticks {
  /** `<area>/<work id>` -> the ids ticked in that row (a step's id, or `before:<n>`). */
  all = $state<Record<string, string[]>>({});
  #loaded = false;
  #dirty = false;

  constructor() {
    void app.platformReady.then(() => this.load());
  }

  async load() {
    if (this.#loaded || !app.platform) return;
    let stored: Record<string, string[]> = {};
    try {
      stored = clean(await app.platform.kv.get('ticks'));
    } catch {
      // a store that cannot be read is an empty one: ticks are a convenience, never a record
    }
    // What he ticked before the load finished wins over the stored copy of the same row.
    this.all = { ...stored, ...untrack(() => $state.snapshot(this.all)) };
    this.#loaded = true;
    if (this.#dirty) this.#persist();
  }

  of(area: string, work: string): string[] {
    return this.all[`${area}/${work}`] ?? NONE;
  }

  has(area: string, work: string, id: string): boolean {
    return this.of(area, work).includes(id);
  }

  set(area: string, work: string, id: string, on: boolean) {
    untrack(() => {
      const key = `${area}/${work}`;
      const cur = this.all[key] ?? NONE;
      if (cur.includes(id) === on) return;
      const next = on ? [...cur, id] : cur.filter((x) => x !== id);
      const { [key]: _old, ...rest } = this.all;
      this.all = next.length ? { ...rest, [key]: next } : rest;
      this.#persist();
    });
  }

  clear(area: string, work: string) {
    untrack(() => {
      const { [`${area}/${work}`]: _gone, ...rest } = this.all;
      this.all = rest;
      this.#persist();
    });
  }

  #persist() {
    this.#dirty = true;
    if (!this.#loaded) return;
    this.#dirty = false;
    try {
      void app.platform?.kv.set('ticks', $state.snapshot(this.all)).catch(() => undefined);
    } catch {
      // a full or blocked store: the ticks stay for this session
    }
  }
}

export const ticks = new Ticks();
