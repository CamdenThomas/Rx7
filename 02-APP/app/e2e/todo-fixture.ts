// A project that exists only in the tests: the copy of the record the browser build reads
// (fixture/export.json) with one more area laid over it, `90-manual`, whose rows carry briefs
// and steps (01-electrical D-533). Nothing here is ever written to the tree: todo.spec.ts
// hands the patched export to the page with page.route, so the TODO manual is tested on rows
// that do not move when the real record does.

export const AREA = '90-manual';

const col = (column: string, type = 'str') => ({ column, type, required: 'no', ref: '', note: '' });
const meta = (name: string, columns: string[], rows: number) => ({ name, purpose: '', key: columns[0], rows, columns: columns.map((c) => col(c)) });

const work = (id: string, o: Record<string, unknown>) => ({
  area: AREA, id, order: 0, seq: 0, stage: 'M', stage_title: 'The manual fixture', item: '', owner: 'camden', state: 'open', status: 'ready',
  gate: [], blockers: [], note: '', track: 'design', part: 1, depth: 0, reply: 'check', choices: [], unit: '', ...o,
});

const PARTS = ['id', 'store', 'section', 'sku', 'item', 'spec', 'qty', 'unit'];
const CAVITIES = ['id', 'housing', 'cav', 'circuit'];
const BRIEFS = ['id', 'goal', 'where', 'time', 'tools', 'parts', 'before', 'know', 'done_when', 'if_not', 'record'];
const STEPS = ['id', 'work', 'n', 'do', 'how', 'expect', 'caution'];

const parts = [
  ['P001', 'Waytek', 'Fuse blocks', '45643', 'ATC fuse block, 4-position', 'bussed input', '2', 'ea'],
  ['P037', 'Mouser', 'Tools', '', 'Deutsch size-16 crimper', '', '1', 'ea'],
];
const cavities = [['T1-S1 9', 'T1-S1', '9', 'Headlight feed']];

const briefs = [
  ['M1', 'The test plug is pinned and every cavity checked.', 'bench', '40 min',
    'Deutsch size-16 crimper (P037)\n10 mm socket\nmultimeter on continuity',
    'P001 P404',
    'The battery negative is off\nEye protection on',
    [
      'Cavity 9 carries the headlight feed, red 18 AWG [cavities T1-S1 9]',
      'The app shows the record, not a page [D-405]',
      'The engine is the 12A [00-CAR PT001]',
      'The wire colours are the 1982 diagram\'s [S-001 p.3]',
      'The stud size is not in the record - confirm [tape measure]',
    ].join('\n'),
    'Every cavity reads under 1 ohm end to end.',
    'Stop. Pull the pin with the removal tool and crimp a new terminal.',
    'Tick the row done.'],
  ['M2', 'The resting voltage is known.', 'driver footwell and under the dash, by the fuse box', '5 min',
    'multimeter on DC volts', '', 'M1 is done', 'A rested battery reads 12.6 V or more [D-405]',
    'The reading is entered.', '', 'The voltage, in volts.'],
  ['M4', 'The plug is in the car.', 'engine bay', 'a weekend', '', '', '', '', 'It clicks home.', '', ''],
];

const steps = [
  // written out of order and without a step 3: the page shows them by n
  ['M1.04', 'M1', '4', 'Test every cavity', 'Meter on continuity, one probe each end.', 'Under 1 ohm on each', ''],
  ['M1.01', 'M1', '1', 'Lay out the wires', 'On the bench, in cavity order.\nKeep the labels facing up.', 'Three wires, labelled', ''],
  ['M1.02', 'M1', '2', 'Crimp and pin the plug', 'Pin-out: 1 red 18 AWG headlight L · 2 blue 18 AWG headlight R · 9 black 16 AWG ground', 'Each terminal clicks and does not pull out', 'Crimp once: a terminal crimped twice is scrap.'],
  ['M2.01', 'M2', '1', 'Set the meter to DC volts', '', '', ''],
  ['M2.02', 'M2', '2', 'Read across the battery posts', 'Red on positive, black on negative.', '12.6 V or more', ''],
];

interface Export {
  areas: unknown[];
  work: unknown[];
  tables: unknown[];
}

/** The export with the test project laid over it. */
export function withManual<T extends Export>(base: T): T {
  const rows = [
    work('M1', { order: 0, seq: 0, item: 'Pin the test plug', note: 'The practice plug from the bench kit. Keep the offcuts.' }),
    work('M2', { order: 1, seq: 1, item: 'Measure the resting voltage', reply: 'value', unit: 'V' }),
    work('M3', {
      order: 2, seq: 2, item: 'Photograph the finished plug', status: 'waiting', gate: ['M1'], depth: 1,
      blockers: [{ ref: 'M1', kind: 'work', label: 'Pin the test plug', owner: 'camden', state: 'ready' }],
      note: 'A plain row: no brief, no steps. One photo from each side.',
    }),
    work('A1', { order: 3, seq: 3, item: 'Check the pin-out against the cavities table', owner: 'agent' }),
    work('M4', {
      order: 4, seq: 4, item: 'Fit the plug in the car', status: 'waiting', track: 'build', part: 3, stage: 'E', stage_title: 'Install',
      gate: ['phase:SOURCING'], blockers: [{ ref: 'phase:SOURCING', kind: 'phase', label: 'the project reaches SOURCING', freeze: true }],
    }),
  ];
  const tables: [string, string[], string[][]][] = [['parts', PARTS, parts], ['cavities', CAVITIES, cavities], ['briefs', BRIEFS, briefs], ['steps', STEPS, steps]];
  const area = {
    path: `02-PROJECTS/${AREA}`, name: AREA, prefix: '90', kind: 'project',
    project: { name: AREA, kind: 'electrical', goal: 'A project for the tests of the TODO manual', phase: 'PLANNING', opened: '2026-10', icon: 'zap', title: 'Manual fixture' },
    tables: [meta('work', ['id', 'item'], rows.length), ...tables.map(([n, c, r]) => meta(n, c, r.length))],
  };
  return {
    ...base,
    areas: [...base.areas, area],
    work: [...base.work, ...rows],
    tables: [...base.tables, ...tables.map(([table, columns, r]) => ({ area: AREA, table, columns, rows: r }))],
  };
}
