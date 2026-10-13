// The TODO page as a step-by-step manual (01-electrical D-533): a project's `briefs` and
// `steps` tables turned into what each of his rows shows - the brief, its steps in order, its
// parts by name, and where every fact comes from. Pure: no Svelte, no state of its own.
//
// Reads (R6): <area> briefs, <area> steps, <area> parts (a name and a quantity for each id a
// brief lists), and the key column of any table a `know` line cites. It owns no fact: nothing
// here is stored, and a project without the two tables gets no entry at all.

import type { RawTable } from './model';
import { citeHref, inlineMd } from './text';

export type SourceKind = 'decision' | 'block' | 'work' | 'part' | 'source' | 'row' | 'text';

/** One bracketed source of a fact: its words, what it names, and its page in the app ('' = none). */
export interface Source {
  text: string;
  kind: SourceKind;
  href: string;
}

/** One line of `know`: the fact, where it comes from, and whether it still wants measuring. */
export interface Fact {
  text: string;
  sources: Source[];
  confirm: boolean;
}

/** A parts id from a brief, resolved against the area's own parts table. */
export interface PartRef {
  id: string;
  found: boolean;
  name: string;
  spec: string;
  qty: string;
  unit: string;
  supplier: string;
  partNo: string;
  href: string;
}

export interface HowItem {
  /** the leading number of a list line ("9" of "9 red 18 AWG"), or '' */
  n: string;
  text: string;
}

/** A step's `how`, in pieces: prose with its line breaks, or a compact list. */
export type HowBlock = { kind: 'text'; text: string } | { kind: 'list'; items: HowItem[] };

export interface Step {
  id: string;
  work: string;
  n: number;
  do: string;
  how: HowBlock[];
  expect: string;
  caution: string;
}

export interface Brief {
  id: string;
  goal: string;
  where: string;
  time: string;
  tools: string[];
  parts: PartRef[];
  before: string[];
  know: Fact[];
  done_when: string;
  if_not: string;
  record: string;
}

export interface RowManual {
  brief: Brief | null;
  steps: Step[];
}

export interface AreaManual {
  area: string;
  /** how many rows carry a brief: 0 means the TODO page reads as it always has */
  briefs: number;
  rows: Map<string, RowManual>;
  /** the row page of one of this area's parts, or '' when the id is not one */
  partHref: (id: string) => string;
}

/** What of the snapshot this needs: every raw table, and the ids of work rows and open blocks. */
export interface RecordView {
  tables: RawTable[];
  work: { area: string; id: string }[];
  blocks: { area: string; id: string }[];
}

const e = encodeURIComponent;
// The app's addresses, as router.svelte.ts writes them (tests/briefs.test.ts holds them equal).
const rowHref = (area: string, table: string, key: string) => `#/row/${e(area)}/${e(table)}/${e(key)}`;
const todoHref = (area: string, id: string) => `#/p/${e(area)}/todo/${e(id)}`;
const blockHref = (area: string, id: string) => `#/p/${e(area)}/blocks/${e(id)}`;

const BLOCK_ID = /^(?:block\s+)?((?:\d{2}|CAR|REF|APP|VER)\.\d{2,3})$/;

/** The cell's lines, trimmed, a leading bullet dropped, empty ones gone. */
export function lines(cell: string): string[] {
  return (cell ?? '')
    .replace(/\r/g, '')
    .split('\n')
    .map((l) => l.trim().replace(/^[-*•]\s+/, ''))
    .filter(Boolean);
}

/** Every table of the record by area and name, with each one's keys looked up only when asked. */
class Lookup {
  #tables = new Map<string, RawTable>();
  #rows = new Map<string, Map<string, string[]>>();
  #work = new Map<string, Set<string>>();
  #blocks = new Map<string, string>();
  #areas = new Set<string>();

  constructor(rec: RecordView) {
    for (const t of rec.tables) {
      this.#tables.set(`${t.area}/${t.table}`, t);
      this.#areas.add(t.area);
    }
    for (const w of rec.work) {
      let s = this.#work.get(w.area);
      if (!s) this.#work.set(w.area, (s = new Set()));
      s.add(w.id);
      this.#areas.add(w.area);
    }
    for (const b of rec.blocks) this.#blocks.set(b.id, b.area);
  }

  isArea = (name: string) => this.#areas.has(name);
  table = (area: string, name: string) => this.#tables.get(`${area}/${name}`);
  isWork = (area: string, id: string) => !!this.#work.get(area)?.has(id);
  /** the area of an open block, or '' */
  blockArea = (id: string) => this.#blocks.get(id) ?? '';

  /** One row by its key (the table's first column), as its cells. */
  row(area: string, name: string, key: string): string[] | undefined {
    const k = `${area}/${name}`;
    let rows = this.#rows.get(k);
    if (!rows) {
      rows = new Map();
      for (const r of this.#tables.get(k)?.rows ?? []) if (r[0] && !rows.has(r[0])) rows.set(r[0], r);
      this.#rows.set(k, rows);
    }
    return rows.get(key);
  }
}

/** One source, as written between the brackets: "cavities L3-S1 9", "00-CAR PT025", "D-280". */
function parseSource(ref: string, area: string, look: Lookup): Source {
  const text = ref.trim();
  const as = (kind: SourceKind, href: string): Source => ({ text, kind, href });
  let scope = area;
  let body = text;
  // Another area named first: "00-CAR PT025", "00-CAR specs SP012".
  const first = text.split(/\s+/)[0];
  if (first !== text && look.isArea(first)) {
    scope = first;
    body = text.slice(first.length).trim();
  }
  // A work row of another area, qualified the way a gate writes it: "03-luxury:F-012".
  const q = body.match(/^([\w-]+):(\S+)$/);
  if (q && look.isWork(q[1], q[2])) return as('work', todoHref(q[1], q[2]));
  // A row of a table: "<table> <key>" - the whole rest as the key, else its first word.
  const sp = body.search(/\s/);
  if (sp > 0) {
    const table = body.slice(0, sp);
    const rest = body.slice(sp + 1).trim();
    const word = rest.split(/\s+/)[0].replace(/[,.;:]+$/, '');
    if (table === 'work') {
      if (look.isWork(scope, word)) return as('work', todoHref(scope, word));
    } else if (!['decisions', 'blocks'].includes(table) && look.table(scope, table)) {
      const key = look.row(scope, table, rest) ? rest : look.row(scope, table, word) ? word : '';
      if (key) return as(table === 'parts' && scope === '00-CAR' ? 'part' : table === 'sources' ? 'source' : 'row', rowHref(scope, table, key));
    }
  }
  // An id by its shape. A superseded decision cited with its closer leads to the closer.
  const ds = body.match(/\bD-\d{3}\b/g);
  if (ds) return as('decision', citeHref(ds[ds.length - 1]));
  const s = body.match(/\bS-\d{3}\b/);
  if (s) return as('source', citeHref(s[0]));
  const pt = body.match(/\bPT\d{3,4}\b/);
  if (pt) return as('part', citeHref(pt[0]));
  const b = body.match(BLOCK_ID);
  if (b) return as('block', look.blockArea(b[1]) ? blockHref(look.blockArea(b[1]), b[1]) : citeHref(b[1]));
  if (look.isWork(scope, body)) return as('work', todoHref(scope, body));
  return as('text', '');
}

/** One `know` line: the bracketed sources at its end peeled off (several brackets, or several
 *  sources in one bracket split on ';'), and a closing "- confirm" taken as a flag. */
export function parseFact(line: string, area = '', look: Lookup = new Lookup({ tables: [], work: [], blocks: [] })): Fact {
  let rest = line.trim();
  const groups: string[] = [];
  let confirm = false;
  for (;;) {
    const c = rest.match(/\s*[-–—]\s*confirm\.?$/i);
    if (c) {
      confirm = true;
      rest = rest.slice(0, c.index);
      continue;
    }
    const b = rest.match(/\s*\[([^[\]]+)\]\.?$/);
    if (b) {
      groups.unshift(b[1]);
      rest = rest.slice(0, b.index);
      continue;
    }
    break;
  }
  const sources = groups.flatMap((g) => g.split(/\s*;\s*/).filter((x) => x.trim()).map((x) => parseSource(x, area, look)));
  return { text: rest.trim(), sources, confirm };
}

const DOT = /\s+·\s+/;
const NUMBERED = /^\d+[A-Za-z]?[.):]?\s+\S/;

function howItem(s: string): HowItem {
  const m = s.match(/^(\d+[A-Za-z]?)[.):]?\s+(.*)$/);
  return m ? { n: m[1], text: m[2] } : { n: '', text: s };
}

/**
 * A step's `how` in pieces. A line holding " · " is a compact list, one item per piece (a
 * lead-in ending in a colon before the first numbered item stays prose); lines that start
 * with a number are list items when the line above or below is one too. Everything else is
 * prose with its line breaks kept; a blank line starts a new paragraph.
 */
export function parseHow(how: string): HowBlock[] {
  const raw = (how ?? '').replace(/\r/g, '').split('\n').map((l) => l.trim());
  const kind = raw.map((l) => (!l ? 'blank' : DOT.test(l) ? 'dot' : NUMBERED.test(l) ? 'num' : 'text'));
  const listy = (i: number) => kind[i] === 'dot' || kind[i] === 'num';
  const out: HowBlock[] = [];
  let fresh = true; // a blank line, or the start: the next prose opens a new paragraph
  const text = (t: string) => {
    const last = out[out.length - 1];
    if (!fresh && last?.kind === 'text') last.text += `\n${t}`;
    else out.push({ kind: 'text', text: t });
    fresh = false;
  };
  const items = (its: HowItem[]) => {
    const last = out[out.length - 1];
    if (!fresh && last?.kind === 'list') last.items.push(...its);
    else out.push({ kind: 'list', items: its });
    fresh = false;
  };
  raw.forEach((l, i) => {
    if (kind[i] === 'blank') fresh = true;
    else if (kind[i] === 'dot') {
      const chunks = l.split(DOT).map((c) => c.trim()).filter(Boolean);
      const lead = chunks[0]?.match(/^(.*?:)\s+(\d+[A-Za-z]?[.):]?\s+\S.*)$/);
      if (lead) {
        text(lead[1]);
        chunks[0] = lead[2];
      }
      items(chunks.map(howItem));
    } else if (kind[i] === 'num' && (listy(i - 1) || listy(i + 1))) items([howItem(l)]);
    else text(l);
  });
  return out;
}

/** One line of a brief or a step as safe HTML: inlineMd()'s links, and every id of the
 *  area's own parts table a link to that part's row. */
export function rich(text: string, partHref: (id: string) => string = () => ''): string {
  const found: string[] = [];
  const marked = (text ?? '').replace(/\u0001/g, '').replace(/\b[A-Z]{1,3}\d{2,4}\b/g, (id) => {
    const h = partHref(id);
    return h ? `\u0001${found.push(`<a href="${h}" class="cite">${id}</a>`) - 1}\u0001` : id;
  });
  return inlineMd(marked).replace(/\u0001(\d+)\u0001/g, (_, i: string) => found[Number(i)]);
}

function resolvePart(id: string, area: string, look: Lookup): PartRef {
  const t = look.table(area, 'parts');
  const r = t ? look.row(area, 'parts', id) : undefined;
  if (!t || !r) return { id, found: false, name: '', spec: '', qty: '', unit: '', supplier: '', partNo: '', href: '' };
  // Each project names its columns its own way: the first of these that holds something.
  const pick = (...cols: string[]) => {
    for (const c of cols) {
      const v = (r[t.columns.indexOf(c)] ?? '').trim();
      if (v) return v;
    }
    return '';
  };
  return {
    id, found: true,
    name: pick('item', 'name', 'product'), spec: pick('spec'), qty: pick('qty'), unit: pick('unit'),
    supplier: pick('store', 'supplier', 'vendor', 'maker'), partNo: pick('sku', 'part_no', 'maker_pn', 'oem_no'),
    href: rowHref(area, 'parts', id),
  };
}

/** A table's rows as objects by column name. */
function objects(t: RawTable | undefined): Record<string, string>[] {
  if (!t) return [];
  return t.rows.map((r) => Object.fromEntries(t.columns.map((c, i) => [c, (r[i] ?? '').trim()])));
}

/**
 * Every project's manual, read once per snapshot: one pass over each area's `briefs` and
 * `steps`, so a list of a hundred rows and a thousand steps looks each row up in a map. An
 * area without either table has no entry.
 */
export function indexManuals(rec: RecordView): Map<string, AreaManual> {
  const look = new Lookup(rec);
  const out = new Map<string, AreaManual>();
  const areas = new Set(rec.tables.filter((t) => t.table === 'briefs' || t.table === 'steps').map((t) => t.area));
  for (const area of areas) {
    const rows = new Map<string, RowManual>();
    const at = (id: string) => {
      let m = rows.get(id);
      if (!m) rows.set(id, (m = { brief: null, steps: [] }));
      return m;
    };
    let briefs = 0;
    for (const b of objects(look.table(area, 'briefs'))) {
      if (!b.id) continue;
      briefs += 1;
      at(b.id).brief = {
        id: b.id, goal: b.goal ?? '', where: b.where ?? '', time: b.time ?? '',
        tools: lines(b.tools),
        parts: [...new Set((b.parts ?? '').split(/[\s,;|]+/).filter(Boolean))].map((id) => resolvePart(id, area, look)),
        before: lines(b.before),
        know: lines(b.know).map((l) => parseFact(l, area, look)),
        done_when: b.done_when ?? '', if_not: b.if_not ?? '', record: b.record ?? '',
      };
    }
    objects(look.table(area, 'steps')).forEach((s, i) => {
      if (!s.id || !s.work) return;
      const n = Number(s.n);
      at(s.work).steps.push({
        id: s.id, work: s.work, n: Number.isFinite(n) && s.n !== '' ? n : Number.MAX_SAFE_INTEGER - 10_000 + i,
        do: s.do ?? '', how: parseHow(s.how ?? ''), expect: s.expect ?? '', caution: s.caution ?? '',
      });
    });
    // In n order whatever the file's order; a gap in n is just a gap, a tie falls back to the id.
    for (const m of rows.values()) m.steps.sort((a, b) => a.n - b.n || a.id.localeCompare(b.id, undefined, { numeric: true }));
    out.set(area, { area, briefs, rows, partHref: (id) => (look.row(area, 'parts', id) ? rowHref(area, 'parts', id) : '') });
  }
  return out;
}

// ------------------------------------------------------------------ the ticks, counted

/** How many of these steps are ticked. A tick for a step that no longer exists counts for nothing. */
export function progress(steps: Step[], ticked: Iterable<string>): { done: number; total: number } {
  const t = new Set(ticked);
  return { done: steps.filter((s) => t.has(s.id)).length, total: steps.length };
}

/** The next step not yet ticked: the first one after `after` when that is given and there is
 *  one, otherwise the first in the row. null when every step is ticked. */
export function nextUnticked(steps: Step[], ticked: Iterable<string>, after = ''): Step | null {
  const t = new Set(ticked);
  const open = steps.filter((s) => !t.has(s.id));
  if (!open.length) return null;
  const i = after ? steps.findIndex((s) => s.id === after) : -1;
  return (i >= 0 ? steps.slice(i + 1).find((s) => !t.has(s.id)) : undefined) ?? open[0];
}

// ------------------------------------------------------------------ his rows, in order

export interface Ordered {
  id: string;
  owner: string;
  status: string;
  track: string;
  order: number;
  seq: number;
}

/** Working order, as the TODO page lists it: the design track first in pure working order
 *  (`seq`), then everything else stage by stage (`order`). */
export function workOrder(a: Ordered, b: Ordered): number {
  const da = a.track === 'design';
  const db = b.track === 'design';
  if (da !== db) return da ? -1 : 1;
  return da ? a.seq - b.seq : a.order - b.order;
}

/** His open rows as one sequence, first to last. */
export function myList<T extends Ordered>(rows: T[]): T[] {
  return rows.filter((w) => w.owner === 'camden' && (w.status === 'ready' || w.status === 'waiting')).sort(workOrder);
}

/** The first row he can do now: his, ready, and not answered yet. */
export function startHere<T extends Ordered>(list: T[], answered: (id: string) => boolean): T | undefined {
  return list.find((w) => w.status === 'ready' && !answered(w.id));
}
