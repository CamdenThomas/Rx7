// The TODO manual's view model (01-electrical D-533): a project's briefs and steps tables,
// read into what a row's page shows. No record is touched: the tables below are the fixture.

import { describe, expect, it } from 'vitest';
import { indexManuals, lines, myList, nextUnticked, parseFact, parseHow, progress, rich, startHere, workOrder, type RecordView, type Step } from '../src/lib/briefs';
import type { RawTable } from '../src/lib/model';
import { href, parse } from '../src/lib/router.svelte';
import { inlineMd } from '../src/lib/text';

const AREA = '01-electrical';
const table = (area: string, name: string, columns: string[], rows: string[][]): RawTable => ({ area, table: name, columns, rows });

const BRIEFS = ['id', 'goal', 'where', 'time', 'tools', 'parts', 'before', 'know', 'done_when', 'if_not', 'record'];
const STEPS = ['id', 'work', 'n', 'do', 'how', 'expect', 'caution'];

const record = (): RecordView => ({
  tables: [
    table(AREA, 'parts', ['id', 'store', 'section', 'sku', 'item', 'spec', 'qty', 'unit'], [
      ['P001', 'Waytek', 'Fuse blocks', '45643', 'ATC fuse block, 4-position', 'bussed input', '2', 'ea'],
      ['P037', '', '', '', 'Deutsch size-16 crimper', '', '1', ''],
    ]),
    table(AREA, 'cavities', ['id', 'housing', 'cav'], [['L3-S1 9', 'L3-S1', '9']]),
    table(AREA, 'fuses', ['id', 'rating'], [['F12', '10 A']]),
    table('00-CAR', 'parts', ['id', 'name'], [['PT025', 'Fuel pump']]),
    table('00-CAR', 'specs', ['id', 'item'], [['SP012', 'Fuel pressure']]),
    table(AREA, 'briefs', BRIEFS, [
      ['E8', 'The dash node is wired and powers up.', 'driver footwell', '2 h',
        'Deutsch size-16 crimper (P037)\n10 mm socket\n\n- multimeter on DC volts',
        'P001 P037, P999',
        'E7 done (the dash is out)\nBattery negative off',
        [
          'Cavity 9 is the headlight feed, red 18 AWG [cavities L3-S1 9]',
          'The fuel pump is under the rear bin [00-CAR PT025]',
          'The connector is on page 15-12 [S-002 p.15-12]',
          'The post is the one ground [D-280]',
          'The fuse is 10 A [fuses F12] [D-247 → D-278; block 01.27]',
          'The stud is M6 - confirm [E7]',
          'Nobody knows the clip count',
        ].join('\n'),
        'The node shows 12.6 V.', 'Stop and check F12.', 'Tick it done.'],
      ['E9', 'Only a goal here.', '', '', '', '', '', '', 'It is done.', '', ''],
    ]),
    table(AREA, 'steps', STEPS, [
      // out of order in the file, and no step 2: n rules, a gap is only a gap
      ['E8.04', 'E8', '4', 'Pin the plug', 'Pin-out: 1 red 18 AWG O3 headlight L · 2 blue 18 AWG O4 · 3 empty', 'Each pin clicks', ''],
      ['E8.01', 'E8', '1', 'Disconnect the battery negative', 'At the rear bin.\nUse the 10 mm socket.', 'No dome lamp', 'Never the positive first'],
      ['E8.03', 'E8', '3', 'Cut the wires', '', '', ''],
      ['X1.01', 'X1', '1', 'A step of a row with no brief', '', '', ''],
    ]),
  ],
  work: [{ area: AREA, id: 'E7' }, { area: AREA, id: 'E8' }, { area: AREA, id: 'E9' }, { area: '03-luxury', id: 'F-012' }],
  blocks: [{ area: AREA, id: '01.27' }],
});

describe('a know line - the fact and where it comes from', () => {
  const m = indexManuals(record()).get(AREA)!;
  const know = m.rows.get('E8')!.brief!.know;

  it('peels the bracketed source off the end of the fact', () => {
    expect(know[0].text).toBe('Cavity 9 is the headlight feed, red 18 AWG');
    expect(know[0].sources).toEqual([{ text: 'cavities L3-S1 9', kind: 'row', href: '#/row/01-electrical/cavities/L3-S1%209' }]);
    expect(know[0].confirm).toBe(false);
  });
  it('links a 00-CAR part, a source with its page, and a decision where inlineMd links them', () => {
    expect(know[1].sources).toEqual([{ text: '00-CAR PT025', kind: 'part', href: '#/row/00-CAR/parts/PT025' }]);
    expect(know[2].sources).toEqual([{ text: 'S-002 p.15-12', kind: 'source', href: '#/row/00-CAR/sources/S-002' }]);
    expect(know[3].sources).toEqual([{ text: 'D-280', kind: 'decision', href: '#/d/D-280' }]);
    for (const s of [know[1], know[2], know[3]].flatMap((f) => f.sources)) expect(inlineMd(s.text)).toContain(`href="${s.href}"`);
  });
  it('takes several brackets, and several sources in one split on a semicolon', () => {
    expect(know[4].text).toBe('The fuse is 10 A');
    expect(know[4].sources.map((s) => [s.kind, s.href])).toEqual([
      ['row', '#/row/01-electrical/fuses/F12'],
      ['decision', '#/d/D-278'], // a superseded decision cited with its closer leads to the closer
      ['block', '#/p/01-electrical/blocks/01.27'], // an open block has a page
    ]);
  });
  it('reads a closing "- confirm" as a flag, and a bare work id as that row', () => {
    expect(know[5]).toEqual({ text: 'The stud is M6', confirm: true, sources: [{ text: 'E7', kind: 'work', href: '#/p/01-electrical/todo/E7' }] });
  });
  it('leaves a fact with no source whole', () => {
    expect(know[6]).toEqual({ text: 'Nobody knows the clip count', sources: [], confirm: false });
  });
  it('shows a source it cannot place as a chip without a link', () => {
    const look = parseFact('Measured by hand [tape measure, 2026-10-01]');
    expect(look.sources).toEqual([{ text: 'tape measure, 2026-10-01', kind: 'text', href: '' }]);
    expect(parseFact('A closed block [block 01.05]').sources[0]).toEqual({ text: 'block 01.05', kind: 'block', href: '#/search?q=01.05' });
    // a table that is there but a key that is not: no link, and no crash
    const rec = record();
    const all = indexManuals({ ...rec, tables: rec.tables.map((t) => (t.table === 'briefs' ? { ...t, rows: [['E8', 'g', '', '', '', '', '', 'x [fuses F99]', 'd', '', '']] } : t)) });
    expect(all.get(AREA)!.rows.get('E8')!.brief!.know[0].sources).toEqual([{ text: 'fuses F99', kind: 'text', href: '' }]);
  });
  it('writes the app\'s own addresses (the router reads each one back)', () => {
    expect(parse(know[0].sources[0].href)).toEqual({ name: 'row', area: AREA, table: 'cavities', key: 'L3-S1 9' });
    expect(know[0].sources[0].href).toBe(href({ name: 'row', area: AREA, table: 'cavities', key: 'L3-S1 9' }));
    expect(know[5].sources[0].href).toBe(href({ name: 'todo', area: AREA, id: 'E7' }));
    expect(know[4].sources[2].href).toBe(href({ name: 'blocks', area: AREA, id: '01.27' }));
  });
  it('follows a row of another area and a qualified work row', () => {
    const rec = record();
    const all = indexManuals({
      ...rec,
      tables: rec.tables.map((t) => (t.table === 'briefs' ? { ...t, rows: [['E8', 'g', '', '', '', '', '', 'a [00-CAR specs SP012]\nb [03-luxury:F-012]', 'd', '', '']] } : t)),
    });
    const k = all.get(AREA)!.rows.get('E8')!.brief!.know;
    expect(k[0].sources[0]).toEqual({ text: '00-CAR specs SP012', kind: 'row', href: '#/row/00-CAR/specs/SP012' });
    expect(k[1].sources[0]).toEqual({ text: '03-luxury:F-012', kind: 'work', href: '#/p/03-luxury/todo/F-012' });
  });
});

describe('a brief - parts by name, lists by line', () => {
  const m = indexManuals(record()).get(AREA)!;
  const brief = m.rows.get('E8')!.brief!;

  it('resolves each parts id against the area\'s parts table', () => {
    expect(brief.parts.map((p) => p.id)).toEqual(['P001', 'P037', 'P999']);
    expect(brief.parts[0]).toEqual({
      id: 'P001', found: true, name: 'ATC fuse block, 4-position', spec: 'bussed input', qty: '2', unit: 'ea',
      supplier: 'Waytek', partNo: '45643', href: '#/row/01-electrical/parts/P001',
    });
    expect(brief.parts[1]).toMatchObject({ found: true, name: 'Deutsch size-16 crimper', qty: '1', unit: '', supplier: '', partNo: '' });
  });
  it('keeps an id that resolves to nothing, as the bare id', () => {
    expect(brief.parts[2]).toEqual({ id: 'P999', found: false, name: '', spec: '', qty: '', unit: '', supplier: '', partNo: '', href: '' });
  });
  it('reads another project\'s column names (name, supplier, part_no)', () => {
    const all = indexManuals({
      tables: [
        table('09-x', 'parts', ['id', 'name', 'qty', 'supplier', 'part_no'], [['LP04', 'microSD card', '3', 'Mouser', 'SD-32']]),
        table('09-x', 'briefs', BRIEFS, [['A1', 'g', '', '', '', 'LP04', '', '', 'd', '', '']]),
      ],
      work: [], blocks: [],
    });
    expect(all.get('09-x')!.rows.get('A1')!.brief!.parts[0]).toMatchObject({ name: 'microSD card', qty: '3', supplier: 'Mouser', partNo: 'SD-32' });
  });
  it('splits tools and before one per line, bullets and blank lines dropped', () => {
    expect(brief.tools).toEqual(['Deutsch size-16 crimper (P037)', '10 mm socket', 'multimeter on DC volts']);
    expect(brief.before).toEqual(['E7 done (the dash is out)', 'Battery negative off']);
    expect(lines('')).toEqual([]);
  });
  it('counts the briefs, and gives a project without the tables no entry', () => {
    expect(m.briefs).toBe(2);
    const all = indexManuals(record());
    expect([...all.keys()]).toEqual([AREA]);
    expect(all.get('00-CAR')).toBeUndefined();
    // declared and empty: an entry, and nothing in it - the page reads as it always has
    const empty = indexManuals({ tables: [table('02-engine', 'briefs', BRIEFS, []), table('02-engine', 'steps', STEPS, [])], work: [], blocks: [] });
    expect(empty.get('02-engine')).toMatchObject({ briefs: 0 });
    expect(empty.get('02-engine')!.rows.size).toBe(0);
  });
  it('links the area\'s own part ids in a line, on top of inlineMd', () => {
    const h = rich('Crimp with **P037** per D-280, not P999 or F12.', m.partHref);
    expect(h).toBe('Crimp with <strong><a href="#/row/01-electrical/parts/P037" class="cite">P037</a></strong> per <a href="#/d/D-280" class="cite">D-280</a>, not P999 or F12.');
    expect(rich('<b>P037</b>')).toBe('&lt;b&gt;P037&lt;/b&gt;');
  });
});

describe('steps - in n order, whatever the file says', () => {
  const m = indexManuals(record()).get(AREA)!;
  const steps = m.rows.get('E8')!.steps;

  it('orders by n and survives a gap', () => {
    expect(steps.map((s) => [s.id, s.n])).toEqual([['E8.01', 1], ['E8.03', 3], ['E8.04', 4]]);
  });
  it('gives a row without a brief no brief, and a row with only a brief no steps', () => {
    expect(m.rows.get('X1')).toMatchObject({ brief: null });
    expect(m.rows.get('X1')!.steps).toHaveLength(1);
    expect(m.rows.get('E9')!.steps).toEqual([]);
    expect(m.rows.get('E7')).toBeUndefined();
  });
  it('puts a step whose n is not a number after the numbered ones, in file order', () => {
    const all = indexManuals({
      tables: [table('09-x', 'steps', STEPS, [['A1.b', 'A1', '', 'second', '', '', ''], ['A1.c', 'A1', 'x', 'third', '', '', ''], ['A1.a', 'A1', '1', 'first', '', '', '']])],
      work: [], blocks: [],
    });
    expect(all.get('09-x')!.rows.get('A1')!.steps.map((s) => s.do)).toEqual(['first', 'second', 'third']);
  });
  it('keeps prose with its line breaks', () => {
    expect(steps[0].how).toEqual([{ kind: 'text', text: 'At the rear bin.\nUse the 10 mm socket.' }]);
    expect(steps[1].how).toEqual([]);
  });
  it('reads a " · " line as a compact list, the lead-in before it as prose', () => {
    expect(steps[2].how).toEqual([
      { kind: 'text', text: 'Pin-out:' },
      { kind: 'list', items: [{ n: '1', text: 'red 18 AWG O3 headlight L' }, { n: '2', text: 'blue 18 AWG O4' }, { n: '3', text: 'empty' }] },
    ]);
  });
  it('reads consecutive "<n> <text>" lines as a list, and a lone one as prose', () => {
    expect(parseHow('Cut these:\n1 red 18 AWG, 400 mm\n2) blue 18 AWG, 350 mm\n10. black 16 AWG\nThen strip 6 mm.')).toEqual([
      { kind: 'text', text: 'Cut these:' },
      { kind: 'list', items: [{ n: '1', text: 'red 18 AWG, 400 mm' }, { n: '2', text: 'blue 18 AWG, 350 mm' }, { n: '10', text: 'black 16 AWG' }] },
      { kind: 'text', text: 'Then strip 6 mm.' },
    ]);
    expect(parseHow('12 AWG red from the busbar to F2.')).toEqual([{ kind: 'text', text: '12 AWG red from the busbar to F2.' }]);
    expect(parseHow('grey plug · black plug')).toEqual([{ kind: 'list', items: [{ n: '', text: 'grey plug' }, { n: '', text: 'black plug' }] }]);
    expect(parseHow('one\n\ntwo')).toEqual([{ kind: 'text', text: 'one' }, { kind: 'text', text: 'two' }]);
    expect(parseHow('')).toEqual([]);
  });
});

describe('the ticks, counted', () => {
  const steps = indexManuals(record()).get(AREA)!.rows.get('E8')!.steps;

  it('counts only ticks of steps that exist', () => {
    expect(progress(steps, [])).toEqual({ done: 0, total: 3 });
    expect(progress(steps, ['E8.03', 'E8.02', 'before:1'])).toEqual({ done: 1, total: 3 });
    expect(progress([], ['E8.01'])).toEqual({ done: 0, total: 0 });
  });
  it('finds the next unticked step, in order', () => {
    expect(nextUnticked(steps, [])?.id).toBe('E8.01');
    expect(nextUnticked(steps, ['E8.01'])?.id).toBe('E8.03');
    expect(nextUnticked(steps, ['E8.01', 'E8.04'])?.id).toBe('E8.03');
    expect(nextUnticked(steps, ['E8.01', 'E8.03', 'E8.04'])).toBeNull();
    expect(nextUnticked([] as Step[], [])).toBeNull();
  });
  it('goes on from a step when asked, and back to the first when nothing follows', () => {
    expect(nextUnticked(steps, [], 'E8.01')?.id).toBe('E8.03');
    expect(nextUnticked(steps, ['E8.04'], 'E8.03')?.id).toBe('E8.01');
  });
});

describe('his rows as one sequence', () => {
  const row = (id: string, owner: string, status: string, track: string, order: number, seq: number) => ({ id, owner, status, track, order, seq });
  const rows = [
    row('E8', 'camden', 'waiting', 'build', 0, 9),
    row('V2', 'camden', 'ready', 'design', 5, 1),
    row('A1', 'agent', 'ready', 'design', 1, 0),
    row('Y1', 'camden', 'ready', 'design', 2, 2),
    row('E7', 'camden', 'waiting', 'build', 3, 8),
    row('Z9', 'camden', 'done', 'design', 4, 3),
  ];

  it('runs the design track first by seq, then the rest by order', () => {
    expect([...rows].sort(workOrder).map((w) => w.id)).toEqual(['A1', 'V2', 'Y1', 'Z9', 'E8', 'E7']);
  });
  it('lists his open rows only, and starts at the first ready one he has not answered', () => {
    const list = myList(rows);
    expect(list.map((w) => w.id)).toEqual(['V2', 'Y1', 'E8', 'E7']);
    expect(startHere(list, () => false)?.id).toBe('V2');
    expect(startHere(list, (id) => id === 'V2')?.id).toBe('Y1');
    expect(startHere(list, () => true)).toBeUndefined();
  });
  it('orders a project without tracks by order alone', () => {
    const flat = [row('B', 'camden', 'ready', '', 2, 0), row('A', 'camden', 'ready', '', 1, 5)];
    expect(myList(flat).map((w) => w.id)).toEqual(['A', 'B']);
  });
});
