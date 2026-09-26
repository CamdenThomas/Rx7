// Search (lib/search.ts): the index built from a snapshot and the ranking of hits (plan P43).
import { describe, expect, it } from 'vitest';
import type { Snapshot } from '../src/lib/model';
import { buildIndex, search } from '../src/lib/search';

const snap = {
  version: 1,
  generated: '2026-09-26T10:00:00-06:00',
  record: { valid: true, problems: [] },
  areas: [
    { path: '02-PROJECTS/01-electrical', name: '01-electrical', prefix: '01', kind: 'project', project: { goal: 'a new harness' }, tables: [] },
    { path: '00-CAR', name: '00-CAR', prefix: 'CAR', kind: 'car', project: {}, tables: [{ name: 'parts', purpose: '', key: 'id', rows: 2, columns: [] }] },
  ],
  blocks: [{ area: '01-electrical', id: '01.12', title: 'What S1 waits on', opened: '2026-09-26', age: 0, ask: 'May S1 wait only on rows that need the car whole?', why: '', options: [], recommend: '(a)', recommended: 'a', stops: '', touches: [], unblocks: [], answered: false }],
  picks: [],
  work: [],
  decisions: [{ area: '01-electrical', id: 'D-323', system: 'process', title: 'Nothing is bought until the design is complete', date: '2026-09-11', status: 'standing', supersedes: [], superseded_by: '', closes: [], also: '', body: '**Decision.** No cart is paid early.', cited_by: [], cited_in: [] }],
  inbox: [],
  log: [],
  tables: [{ area: '00-CAR', table: 'parts', columns: ['id', 'name', 'note'], rows: [['PT077', 'Oil pan', 'confirm'], ['PT024', 'Battery', 'the Ionic']] }],
  photos: [],
  manual: { parts: [{ id: 'PT024', name: 'Battery' }], systems: [] },
} as unknown as Snapshot;

describe('search', () => {
  const docs = buildIndex(snap);

  it('finds a decision by words in its body and ranks the exact id first', () => {
    expect(search(docs, 'cart paid')[0].id).toBe('D-323');
    expect(search(docs, 'D-323')[0].id).toBe('D-323');
  });

  it('a block outranks a raw row for the same words', () => {
    const hits = search(docs, 'S1');
    expect(hits[0].kind).toBe('block');
  });

  it('a part the Manual shows lands on its Manual page; a held one on its raw row', () => {
    const shown = search(docs, 'Battery')[0];
    expect(shown.kind).toBe('part');
    expect(shown.route).toEqual({ name: 'manual', page: 'part', id: 'PT024' });
    const held = search(docs, 'Oil pan')[0];
    expect(held.kind).toBe('row');
    expect(held.route).toEqual({ name: 'row', area: '00-CAR', table: 'parts', key: 'PT077' });
  });

  it('every term must match, and a snippet shows where', () => {
    expect(search(docs, 'battery harness')).toHaveLength(0);
    expect(search(docs, 'ionic')[0].snippet).toContain('Ionic');
  });
});
