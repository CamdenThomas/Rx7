// What he has typed but not yet saved, kept on this device with every keystroke, so closing
// the app, losing signal or a crash never costs him a word (R3). A draft is cleared only
// after the answer it became is safely saved.
//
// The store is loaded before the first screen mounts (App.svelte) and MERGED with what was
// typed meanwhile, never replaced; nothing is written back until the load is done, so a
// draft typed in the first seconds can never overwrite the ones from yesterday (plan P36).

import { untrack } from 'svelte';
import { app } from './app.svelte';

export interface DraftText {
  choice: string;
  text: string;
  context: string;
}

const EMPTY: DraftText = { choice: '', text: '', context: '' };

class Drafts {
  all = $state<Record<string, DraftText>>({});
  #loaded = false;
  #dirty = false;
  #timer: ReturnType<typeof setTimeout> | undefined;

  async load() {
    if (this.#loaded || !app.platform) return;
    const stored = (await app.platform.kv.get<Record<string, DraftText>>('drafts')) ?? {};
    // What he typed before the load finished wins over the stored copy of the same draft.
    this.all = { ...stored, ...untrack(() => $state.snapshot(this.all)) };
    this.#loaded = true;
    if (this.#dirty) this.#persist(0);
  }

  get(area: string, target: string): DraftText {
    return this.all[`${area}/${target}`] ?? EMPTY;
  }

  has(area: string, target: string): boolean {
    const d = this.all[`${area}/${target}`];
    return !!d && !!(d.choice || d.text.trim() || d.context.trim());
  }

  /** Safe to call from an effect: it never makes the caller depend on the drafts. */
  set(area: string, target: string, patch: Partial<DraftText>) {
    untrack(() => {
      const key = `${area}/${target}`;
      const cur = this.all[key] ?? EMPTY;
      if (Object.entries(patch).every(([k, v]) => cur[k as keyof DraftText] === v)) return;
      this.all = { ...this.all, [key]: { ...cur, ...patch } };
      this.#persist();
    });
  }

  clear(area: string, target: string) {
    untrack(() => {
      const { [`${area}/${target}`]: _gone, ...rest } = this.all;
      this.all = rest;
      this.#persist(0);
    });
  }

  #persist(delay = 120) {
    this.#dirty = true;
    if (!this.#loaded) return;
    clearTimeout(this.#timer);
    this.#timer = setTimeout(() => {
      this.#dirty = false;
      void app.platform?.kv.set('drafts', $state.snapshot(this.all));
    }, delay);
  }
}

export const drafts = new Drafts();
