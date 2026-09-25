// What is open on screen right now — nothing here outlives the window.

import type { Route } from './router.svelte';
import { app } from './app.svelte';

class UI {
  searchOpen = $state(false);
  chatOpen = $state(false);
  /** What the chat should know he is looking at, set by the screen on show. */
  context = $state('');
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

const PAGE_TITLE = { blocks: 'Blocks', picks: 'Picks', todo: 'TODO', decisions: 'Decisions', parts: 'Parts', run: 'Run' } as const;

export function crumbs(r: Route): Crumb[] {
  const home: Crumb = { label: 'Home', route: { name: 'home' } };
  const projects: Crumb = { label: 'Projects', route: { name: 'projects' } };
  const project = (area: string): Crumb => ({ label: projectLabel(area), route: { name: 'project', area } });
  switch (r.name) {
    case 'home':
      return [{ label: 'Home' }];
    case 'manual':
      return [home, { label: 'Manual' }];
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
