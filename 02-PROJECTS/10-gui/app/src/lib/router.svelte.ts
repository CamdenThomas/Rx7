// Every screen has an address, kept in the URL's #fragment so it survives a reload and the
// back button works on both apps: #/p/00-electrical/blocks/00.29.

export type Route =
  | { name: 'home' }
  | { name: 'manual' }
  | { name: 'projects' }
  | { name: 'new-project' }
  | { name: 'project'; area: string }
  | { name: 'blocks'; area: string; id?: string }
  | { name: 'picks'; area: string; id?: string }
  | { name: 'todo'; area: string; id?: string }
  | { name: 'decisions'; area: string; id?: string }
  | { name: 'parts'; area: string }
  | { name: 'run'; area: string }
  | { name: 'decision'; id: string }
  | { name: 'row'; area: string; table: string; key: string }
  | { name: 'search'; q: string }
  | { name: 'settings' };

const PAGES = ['blocks', 'picks', 'todo', 'decisions', 'parts', 'run'] as const;

export function parse(hash: string): Route {
  const [path, query = ''] = hash.replace(/^#/, '').split('?');
  const seg = path.split('/').filter(Boolean).map(decodeURIComponent);
  const q = new URLSearchParams(query);
  switch (seg[0]) {
    case undefined:
      return { name: 'home' };
    case 'manual':
      return { name: 'manual' };
    case 'projects':
      return seg[1] === 'new' ? { name: 'new-project' } : { name: 'projects' };
    case 'p': {
      const area = seg[1];
      const page = seg[2] as (typeof PAGES)[number] | undefined;
      if (!area) return { name: 'projects' };
      if (!page || !PAGES.includes(page)) return { name: 'project', area };
      if (page === 'parts' || page === 'run') return { name: page, area };
      return { name: page, area, id: seg[3] };
    }
    case 'd':
      return seg[1] ? { name: 'decision', id: seg[1] } : { name: 'home' };
    case 'row':
      return { name: 'row', area: seg[1] ?? '', table: seg[2] ?? '', key: seg.slice(3).join('/') };
    case 'search':
      return { name: 'search', q: q.get('q') ?? '' };
    case 'settings':
      return { name: 'settings' };
    default:
      return { name: 'home' };
  }
}

export function href(r: Route): string {
  const e = encodeURIComponent;
  switch (r.name) {
    case 'home':
      return '#/';
    case 'manual':
      return '#/manual';
    case 'projects':
      return '#/projects';
    case 'new-project':
      return '#/projects/new';
    case 'project':
      return `#/p/${e(r.area)}`;
    case 'parts':
    case 'run':
      return `#/p/${e(r.area)}/${r.name}`;
    case 'blocks':
    case 'picks':
    case 'todo':
    case 'decisions':
      return `#/p/${e(r.area)}/${r.name}${r.id ? `/${e(r.id)}` : ''}`;
    case 'decision':
      return `#/d/${e(r.id)}`;
    case 'row':
      return `#/row/${e(r.area)}/${e(r.table)}/${e(r.key)}`;
    case 'search':
      return `#/search${r.q ? `?q=${e(r.q)}` : ''}`;
    case 'settings':
      return '#/settings';
  }
}

class Router {
  route = $state<Route>(parse(typeof location === 'undefined' ? '' : location.hash));

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('hashchange', () => {
        this.route = parse(location.hash);
      });
    }
  }

  go(r: Route, replace = false) {
    const h = href(r);
    if (replace) {
      history.replaceState(null, '', h);
      this.route = parse(h);
    } else {
      location.hash = h;
    }
  }
}

export const router = new Router();
