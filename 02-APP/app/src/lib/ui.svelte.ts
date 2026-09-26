// What is open on screen right now — nothing here outlives the window.

import type { Route } from './router.svelte';
import { app } from './app.svelte';

class UI {
  searchOpen = $state(false);
  chatOpen = $state(false);
  /** What the chat should know he is looking at, set by the screen on show. */
  context = $state('');
  /** A question put into the chat's box for him to send or change (the Manual's Ask). */
  seed = $state('');

  /** Open the chat with words he selected, and a question about them ready to send (D-417, his 4.1). */
  ask(selected: string, where: string) {
    this.context = `he selected this text on ${where}: "${selected}"`;
    this.seed = `What does "${selected.length > 80 ? `${selected.slice(0, 77)}…` : selected}" mean here? `;
    this.chatOpen = true;
  }
}

export const ui = new UI();

export interface Crumb {
  label: string;
  route?: Route;
}

export function projectLabel(area: string): string {
  const a = app.area(area);
  return a ? `${a.prefix} · ${app.title(area)}` : area;
}

export const MANUAL_TITLE = {
  state: 'Car state', systems: 'Systems', car: 'The car', specs: 'Specs', service: 'Service', diagrams: 'Diagrams', notes: 'Notes', part: 'Part',
} as const;

const PAGE_TITLE = { blocks: 'Blocks', picks: 'Picks', todo: 'TODO', decisions: 'Decisions', parts: 'Parts', run: 'Run' } as const;

export function crumbs(r: Route): Crumb[] {
  const home: Crumb = { label: 'Home', route: { name: 'home' } };
  const projects: Crumb = { label: 'Projects', route: { name: 'projects' } };
  const project = (area: string): Crumb => ({ label: projectLabel(area), route: { name: 'project', area } });
  switch (r.name) {
    case 'home':
      return [{ label: 'Home' }];
    case 'waiting':
      return [home, projects, { label: 'Waiting for you' }];
    case 'manual': {
      if (!r.page) return [home, { label: 'Manual' }];
      const manual: Crumb = { label: 'Manual', route: { name: 'manual' } };
      if (r.page === 'part') {
        const p = app.snapshot?.manual?.parts.find((x) => x.id === r.id);
        const sys = app.snapshot?.manual?.systems.find((x) => x.id === p?.system);
        return [home, manual, { label: 'Systems', route: { name: 'manual', page: 'systems' } },
          ...(sys ? [{ label: sys.name, route: { name: 'manual', page: 'systems', id: sys.id } as Route }] : []), { label: p?.name ?? r.id ?? '' }];
      }
      const list: Crumb = { label: MANUAL_TITLE[r.page], route: r.id ? { name: 'manual', page: r.page } : undefined };
      if (!r.id) return [home, manual, list];
      const m = app.snapshot?.manual;
      const name =
        m?.systems.find((x) => x.id === r.id)?.name ??
        m?.zones.find((x) => x.id === r.id)?.name ??
        m?.circuits.find((x) => x.file.replace(/\.[^.]+$/, '') === r.id)?.title ??
        r.id;
      return [home, manual, list, { label: name }];
    }
    case 'projects':
      return [home, { label: 'Projects' }];
    case 'new-project':
      return [home, projects, { label: 'New project' }];
    case 'project':
      return [home, projects, { label: projectLabel(r.area) }];
    case 'parts':
    case 'run':
      return [home, projects, project(r.area), { label: PAGE_TITLE[r.name] }];
    case 'blocks':
    case 'picks':
    case 'todo':
    case 'decisions': {
      const list: Crumb = { label: PAGE_TITLE[r.name], route: r.id ? { name: r.name, area: r.area } : undefined };
      return [home, projects, project(r.area), list, ...(r.id ? [{ label: r.id }] : [])];
    }
    case 'decision': {
      const d = app.decision(r.id);
      return d
        ? [home, projects, project(d.area), { label: 'Decisions', route: { name: 'decisions', area: d.area } }, { label: r.id }]
        : [home, { label: r.id }];
    }
    case 'row': {
      const a = app.area(r.area);
      const base = a?.kind === 'project' ? [projects, project(r.area)] : [{ label: a?.name ?? r.area }];
      return [home, ...base, { label: r.table }, { label: r.key }];
    }
    case 'search':
      return [home, { label: 'Search' }];
    case 'settings':
      return [home, { label: 'Settings' }];
  }
}
