// One search box for everything (D-406 3.4): blocks, decisions, work rows, parts picks and
// every row of every table. The index is built from the snapshot on first use and whenever
// the record changes; a query is a few string scans, fast enough on a phone.

import type { Route } from './router.svelte';
import type { Snapshot } from './model';
import { plain } from './text';

export type HitKind = 'block' | 'decision' | 'work' | 'pick' | 'row' | 'project' | 'part';

export interface Doc {
  kind: HitKind;
  area: string;
  id: string;
  title: string;
  /** Everything searchable about it, as written; `hay` is the same, lower-cased. */
  text: string;
  hay: string;
  route: Route;
  sub?: string;
}

export interface Hit extends Doc {
  score: number;
  snippet: string;
}

const TITLE_COLUMNS = ['title', 'item', 'name', 'field', 'what', 'description', 'label', 'purpose', 'product', 'part', 'value', 'summary'];

export function buildIndex(s: Snapshot): Doc[] {
  const docs: Omit<Doc, 'hay'>[] = [];
  const join = (...xs: string[]) => xs.filter(Boolean).join(' · ');
  for (const a of s.areas.filter((a) => a.kind === 'project')) {
    docs.push({ kind: 'project', area: a.name, id: a.prefix, title: a.name, text: join(a.name, a.project.goal ?? ''), route: { name: 'project', area: a.name } });
  }
  for (const b of s.blocks) {
    docs.push({
      kind: 'block', area: b.area, id: b.id, title: b.title,
      text: join(b.id, b.title, b.ask, b.why, b.options.map((o) => o.text).join(' '), b.recommend, b.stops),
      route: { name: 'blocks', area: b.area, id: b.id },
    });
  }
  for (const d of s.decisions) {
    docs.push({
      kind: 'decision', area: d.area, id: d.id, title: d.title, sub: d.system,
      text: join(d.id, d.title, d.system, plain(d.body)),
      route: { name: 'decision', id: d.id },
    });
  }
  for (const w of s.work) {
    docs.push({
      kind: 'work', area: w.area, id: w.id, title: w.item, sub: w.stage_title,
      text: join(w.id, w.item, w.note, w.stage_title),
      route: { name: 'todo', area: w.area, id: w.id },
    });
  }
  for (const p of s.picks) {
    docs.push({
      kind: 'pick', area: p.area, id: p.id, title: `${p.product}${p.maker_pn ? ` (${p.maker_pn})` : ''}`, sub: `${p.part} ${p.part_item}`,
      text: join(p.id, p.product, p.maker_pn, p.vendor, p.part, p.part_item, p.why, p.meets, p.drawbacks),
      route: p.verdict === 'proposed' ? { name: 'picks', area: p.area, id: p.id } : { name: 'row', area: p.area, table: 'picks', key: p.id },
    });
  }
  // A part or a system the Manual shows lands on its Manual page, not the raw row (P40).
  const manualParts = new Set((s.manual?.parts ?? []).map((p) => p.id));
  const manualSystems = new Set((s.manual?.systems ?? []).map((x) => x.id));
  for (const t of s.tables) {
    const key = s.areas.find((a) => a.name === t.area)?.tables.find((m) => m.name === t.table)?.key ?? t.columns[0];
    const ki = Math.max(0, t.columns.indexOf(key ?? ''));
    const ti = t.columns.findIndex((c) => TITLE_COLUMNS.includes(c) && c !== key);
    for (const r of t.rows) {
      const id = r[ki] ?? '';
      const inManual = t.area === '00-CAR' && ((t.table === 'parts' && manualParts.has(id)) || (t.table === 'systems' && manualSystems.has(id)));
      docs.push({
        kind: inManual ? 'part' : 'row', area: t.area, id, sub: inManual ? 'Manual' : t.table,
        title: ti >= 0 && r[ti] ? r[ti] : r.filter(Boolean).slice(1, 3).join(' · '),
        text: join(...r),
        route: inManual
          ? { name: 'manual', page: t.table === 'parts' ? 'part' : 'systems', id }
          : { name: 'row', area: t.area, table: t.table, key: id },
      });
    }
  }
  return docs.map((d) => ({ ...d, hay: d.text.toLowerCase() }));
}

const KIND_WEIGHT: Record<HitKind, number> = { project: 6, block: 5, decision: 4, part: 3, pick: 3, work: 3, row: 1 };

export function search(docs: Doc[], query: string, limit = 60): Hit[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const terms = q.split(/\s+/).filter(Boolean);
  const hits: Hit[] = [];
  for (const d of docs) {
    if (!terms.every((t) => d.hay.includes(t))) continue;
    const id = d.id.toLowerCase();
    const title = d.title.toLowerCase();
    let score = KIND_WEIGHT[d.kind];
    if (id === q) score += 100;
    else if (id.startsWith(q)) score += 40;
    for (const t of terms) if (title.includes(t)) score += 10;
    if (title.startsWith(terms[0])) score += 5;
    hits.push({ ...d, score, snippet: snippet(d, terms[0]) });
  }
  return hits.sort((a, b) => b.score - a.score || a.id.localeCompare(b.id, undefined, { numeric: true })).slice(0, limit);
}

function snippet(d: Doc, term: string): string {
  const at = d.hay.indexOf(term);
  if (at < 0) return '';
  const from = Math.max(0, at - 50);
  const to = at + term.length + 90;
  const text = d.text.slice(from, to).replace(/\s+/g, ' ').trim();
  return `${from > 0 ? '…' : ''}${text}${to < d.text.length ? '…' : ''}`;
}
