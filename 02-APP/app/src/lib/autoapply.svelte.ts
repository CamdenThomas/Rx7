// Auto-apply (D-413): on the desktop his answers are applied without a press. The app pulls
// from GitHub every few minutes so the phone's answers arrive too, and once the newest answer
// waiting has sat quiet for a while, it applies them: first by rule, through `rx7.py apply`
// (a tick, a value, a choice with no words, a drive - one right answer, no model needed,
// plan P07), then whatever is left goes to ONE Claude run naming every area with answers
// (plan P08). An answer counts as tried only when its run ended well; a run that failed
// (the session limit, a crash) leaves the answers eligible and is retried, and the failure
// stays visible until a run succeeds or he presses Apply.

import { app } from './app.svelte';
import { runs } from './claude.svelte';

/** How long after his newest answer a run starts, so a batch of answers goes in one run. */
export const QUIET_MS = 90_000;
/** How often the desktop pulls from GitHub for the phone's answers. */
export const POLL_MS = 180_000;
/** Retries after a failed run: after these delays, then it waits for a press. */
const RETRY_MS = [5 * 60_000, 15 * 60_000, 60 * 60_000];

const ANSWER_KINDS = ['block', 'pick', 'work', 'drive'];

class AutoApply {
  #tried = new Set<string>();
  #timer: ReturnType<typeof setTimeout> | undefined;
  #started = false;
  #failures = 0;
  #retryAt = 0;
  /** Why the last automatic run failed, until one succeeds; shown on every Apply bar. */
  failed = $state('');

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
    this.#timer = setTimeout(() => void this.#check(), 0);
  }

  /**
   * Apply by rule what needs no judgement, in one or several areas. Returns the areas that
   * still hold answers for a run. Used by the Apply button too, so a press never starts a
   * model for a tick.
   */
  async mechanical(areas: string[]): Promise<string[]> {
    const p = app.platform;
    const remaining: string[] = [];
    if (!p?.applyMechanical) return areas;
    for (const area of areas) {
      try {
        const out = await p.applyMechanical(area);
        if (out.rc !== 0) remaining.push(area);
      } catch {
        remaining.push(area);
      }
    }
    if (remaining.length !== areas.length) await app.refresh(false);
    return remaining;
  }

  #fresh() {
    return (app.snapshot?.inbox ?? []).filter(
      (a) => ANSWER_KINDS.includes(a.kind) && !a.pending && !this.#tried.has(`${a.area}/${a.id}@${a.at}`),
    );
  }

  async #check() {
    runs.startRequested();
    if (!app.autoApply || runs.busy || runs.queued) return;
    const fresh = this.#fresh();
    if (!fresh.length) return;
    const newest = Math.max(...fresh.map((a) => Date.parse(a.at)));
    const wait = Math.max(newest + QUIET_MS, this.#retryAt) - Date.now();
    if (wait > 0) {
      this.#timer = setTimeout(() => void this.#check(), wait + 1000);
      return;
    }
    const areas = [...new Set(fresh.map((a) => a.area))];
    const remaining = await this.mechanical(areas);
    if (runs.busy || runs.queued) return;
    const still = this.#fresh().filter((a) => remaining.includes(a.area));
    if (!still.length) {
      this.failed = '';
      this.#failures = 0;
      return;
    }
    const n = still.length;
    const where = [...new Set(still.map((a) => a.area))];
    runs.start(
      'apply',
      where[0],
      `Auto-apply started this run (D-413): ${n} answer${n === 1 ? '' : 's'} of his wait in the inbox` +
        (where.length > 1 ? ` across ${where.map((w) => app.area(w)?.path ?? w).join(', ')} - apply every one of them in this run.` : '.'),
      undefined,
      (status, result) => this.#ended(still.map((a) => `${a.area}/${a.id}@${a.at}`), status, result),
    );
  }

  #ended(keys: string[], status: string, result: string) {
    if (status === 'done') {
      keys.forEach((k) => this.#tried.add(k));
      this.failed = '';
      this.#failures = 0;
      return;
    }
    const delay = RETRY_MS[Math.min(this.#failures, RETRY_MS.length - 1)];
    this.#failures += 1;
    this.#retryAt = Date.now() + delay;
    const why = (result || status).split('\n')[0].slice(0, 160);
    this.failed = this.#failures <= RETRY_MS.length
      ? `Auto-apply failed (${why}). Trying again in ${Math.round(delay / 60_000)} min, or press Apply.`
      : `Auto-apply failed ${this.#failures} times (${why}). Press Apply when you are ready.`;
    if (this.#failures <= RETRY_MS.length) this.#timer = setTimeout(() => void this.#check(), delay + 1000);
  }
}

export const autoApply = new AutoApply();
