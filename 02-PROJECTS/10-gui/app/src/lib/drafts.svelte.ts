// What he has typed but not yet saved, kept on this device with every keystroke, so closing
// the app, losing signal or a crash never costs him a word (R3). A draft is cleared only
// after the answer it became is safely saved.

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
  #timer: ReturnType<typeof setTimeout> | undefined;

  async load() {
    if (this.#loaded || !app.platform) return;
    this.all = (await app.platform.kv.get<Record<string, DraftText>>('drafts')) ?? {};
    this.#loaded = true;
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
    clearTimeout(this.#timer);
    this.#timer = setTimeout(() => void app.platform?.kv.set('drafts', $state.snapshot(this.all)), delay);
  }
}

export const drafts = new Drafts();
