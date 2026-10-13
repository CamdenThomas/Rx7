// How he last filtered each project's TODO, so the one-at-a-time view steps through the same
// rows he was looking at. A project whose rows carry briefs (01-electrical D-533) opens as his
// own list, whole, from the first row to the last.

import { app } from '../../lib/app.svelte';
import { myList, workOrder } from '../../lib/briefs';
import type { WorkRow } from '../../lib/model';
import { manuals } from '../../lib/steps.svelte';

export type Who = 'all' | 'camden' | 'agent';

export interface TodoFilter {
  /** one track, or '' for every row */
  track: string;
  who: Who;
  readyOnly: boolean;
}

class TodoView {
  filters = $state<Record<string, TodoFilter>>({});

  get(area: string): TodoFilter {
    const set = this.filters[area];
    if (set) return set;
    if (manuals.has(area)) return { track: '', who: 'camden', readyOnly: false };
    const tracks = [...new Set(app.work(area).map((w) => w.track).filter(Boolean))];
    return { track: tracks.includes('design') ? 'design' : (tracks[0] ?? ''), who: 'all', readyOnly: false };
  }

  set(area: string, patch: Partial<TodoFilter>) {
    this.filters = { ...this.filters, [area]: { ...this.get(area), ...patch } };
  }
}

export const todoView = new TodoView();

/** The rows in working order for this filter, open rows only. */
export function visible(area: string, f: TodoFilter): WorkRow[] {
  const rows = app.work(area).filter((w) => (!f.track || w.track === f.track) && (f.who === 'all' || w.owner === f.who));
  const live = rows.filter((w) => w.status === 'ready' || w.status === 'waiting');
  const shown = f.readyOnly ? live.filter((w) => w.status === 'ready') : live;
  return shown.sort(workOrder);
}

/** His open rows as one sequence, whatever the filter: the numbers the list and a row show. */
export function mine(area: string): WorkRow[] {
  return myList(app.work(area));
}
