import { describe, expect, it } from 'vitest';
import { href, parse, type Route } from '../src/lib/router.svelte';

describe('every screen has an address, and it round-trips', () => {
  const routes: Route[] = [
    { name: 'home' }, { name: 'manual' }, { name: 'projects' }, { name: 'new-project' },
    { name: 'project', area: '01-electrical' },
    { name: 'blocks', area: '01-electrical' }, { name: 'blocks', area: '01-electrical', id: '01.29' },
    { name: 'picks', area: '02-luxury', id: 'PK021' }, { name: 'todo', area: '01-electrical', id: 'W-330b' },
    { name: 'decisions', area: '10-gui', id: 'D-405' }, { name: 'parts', area: '02-luxury' }, { name: 'run', area: '03-engine' },
    { name: 'decision', id: 'D-387' }, { name: 'row', area: '00-CAR', table: 'vehicle', key: 'fuel pump' },
    { name: 'search', q: 'fuse F3' }, { name: 'settings' },
  ];
  for (const r of routes) it(`${href(r)}`, () => expect(parse(href(r))).toEqual(r));
  it('an unknown address goes home', () => expect(parse('#/nowhere')).toEqual({ name: 'home' }));
});
