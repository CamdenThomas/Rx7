// Auto-apply (D-413): on the desktop his answers are applied without a press. The app pulls
// from GitHub every few minutes so the phone's answers arrive too, and once the newest answer
// waiting in a project has sat quiet for a while, it starts that project's Apply run. Each
// answer starts at most one run: one a run leaves in the inbox (a question back it is still
// holding, say) waits for a press instead of starting run after run.

import { app } from './app.svelte';
import { runs } from './claude.svelte';

/** How long after his newest answer a run starts, so a batch of answers goes in one run. */
export const QUIET_MS = 90_000;
/** How often the desktop pulls from GitHub for the phone's answers. */
export const POLL_MS = 180_000;

const ANSWER_KINDS = ['block', 'pick', 'work'];

class AutoApply {
  #tried = new Set<string>();
  #timer: ReturnType<typeof setTimeout> | undefined;
  #started = false;

  async start() {
    const p = app.platform;
    if (this.#started || !p?.canClaude) return;
    this.#started = true;
    app.autoApply = (await p.kv.get<boolean>('autoApply')) ?? true;
    setInterval(() => {
      if (!runs.busy && !app.sync.busy) void app.refresh(true);
    }, POLL_MS);
    $effect.root(() => {
      $effect(() => {
        void app.snapshot;
        void runs.busy;
        this.nudge();
      });
    });
  }

  async set(on: boolean) {
    app.autoApply = on;
    await app.platform?.kv.set('autoApply', on);
    this.nudge();
  }

  /** Look again now: the record changed, a run ended, or the setting did. */
  nudge() {
    clearTimeout(this.#timer);
    this.#timer = setTimeout(() => this.#check(), 0);
  }

  #check() {
    runs.startRequested();
    if (!app.autoApply || runs.busy || runs.queued) return;
    const fresh = (app.snapshot?.inbox ?? []).filter(
      (a) => ANSWER_KINDS.includes(a.kind) && !a.pending && !this.#tried.has(`${a.area}/${a.id}@${a.at}`),
    );
    if (!fresh.length) return;
    const newest = Math.max(...fresh.map((a) => Date.parse(a.at)));
    const wait = newest + QUIET_MS - Date.now();
    if (wait > 0) {
      this.#timer = setTimeout(() => this.#check(), wait + 1000);
      return;
    }
    const areas = [...new Set(fresh.map((a) => a.area))];
    for (const area of areas) {
      const mine = fresh.filter((a) => a.area === area);
      mine.forEach((a) => this.#tried.add(`${a.area}/${a.id}@${a.at}`));
      const n = mine.length;
      runs.start('apply', area, `Auto-apply started this run (D-413): ${n} answer${n === 1 ? '' : 's'} of his wait in the inbox.`);
    }
  }
}

export const autoApply = new AutoApply();
