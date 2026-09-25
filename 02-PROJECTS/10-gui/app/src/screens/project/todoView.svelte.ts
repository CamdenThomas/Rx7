// How he last filtered each project's TODO, so the one-at-a-time view steps through the same
// rows he was looking at.

import { app } from '../../lib/app.svelte';
import type { WorkRow } from '../../lib/model';

export type Who = 'all' | 'camden' | 'agent';

export interface TodoFilter {
  track: string;
  who: Who;
  readyOnly: boolean;
}

class TodoView {
  filters = $state<Record<string, TodoFilter>>({});

  get(area: string): TodoFilter {
    const tracks = [...new Set(app.work(area).map((w) => w.track).filter(Boolean))];
    return this.filters[area] ?? { track: tracks.includes('design') ? 'design' : (tracks[0] ?? ''), who: 'all', readyOnly: false };
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
  return shown.sort((a, b) => (f.track === 'design' ? a.seq - b.seq : a.order - b.order));
}
