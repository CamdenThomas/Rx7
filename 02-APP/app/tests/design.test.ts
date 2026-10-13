// The Design page's pure half (D-505, M3D1) on a stub scene: two units, a board inside one,
// a node, two links and a missing entry; and the version-2 stub (v2/: the CUR, two legs, two
// mated pairs of connectors sharing one model, cavities). three.js appears only as its math.
import { Box3, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import raw from './fixtures/design/scene.json';
import rawV2 from './fixtures/design/v2/scene.json';
import {
  byLeg,
  connectorShown,
  defaultToggles,
  drawnId,
  drawnIds,
  housingsOf,
  legLabelAt,
  legPaths,
  legRadius,
  legShown,
  linkShown,
  listedChildren,
  listedTop,
  waysOf,
} from '../src/lib/design';
import {
  childrenOf,
  declutter,
  family,
  fitDistance,
  fitSet,
  focusOf,
  frameGlb,
  glbReading,
  labelT,
  looksAbsent,
  modelled,
  nodeMatches,
  parseScene,
  rootOf,
  tap,
  topLevel,
  type Scene,
} from '../src/lib/design';
import { CAR_TO_THREE, corners, endPoint, fitView, glbMatrix, linkEnds, matrixUnder, placeMatrix, worldMatrix } from '../src/lib/designMath';

const parsed = parseScene(raw);
if (!parsed.ok) throw new Error(parsed.reason);
const s: Scene = parsed.scene;

const near = (v: Vector3, x: number, y: number, z: number) => {
  expect(v.x).toBeCloseTo(x, 6);
  expect(v.y).toBeCloseTo(y, 6);
  expect(v.z).toBeCloseTo(z, 6);
};

describe('the scene file is read defensively', () => {
  it('reads the stub whole, with nothing to forgive', () => {
    expect(parsed.problems).toEqual([]);
    expect(s.parts.map((p) => p.id)).toEqual(['control-unit', 'dcu-carrier', 'pmu', 'ground-point']);
    expect(s.links.map((l) => l.id)).toEqual(['DP-DCU', 'GND-1']);
    expect(s.missing).toEqual([{ part: 'left-plate', what: 'housing model', why: 'the plate is not drawn yet' }]);
    expect(s.notes).toHaveLength(1);
    expect(s.frame.ruling).toBe('D-418');
  });

  it('fills what a part leaves out', () => {
    const g = s.parts.find((p) => p.id === 'ground-point')!;
    expect(g).toMatchObject({ kind: 'node', glb: null, connectors: [], children: [], size_mm: null, nodes: { case: [], inside: [] } });
    expect(g.place).toEqual({ x: 0, y: 0, z: 300, rx: 0, ry: 0, rz: 0 });
    // a connector with no `at` is kept, its place unknown
    expect(s.parts.find((p) => p.id === 'pmu')!.connectors[1]).toMatchObject({ code: 'C2', at: null });
  });

  it('refuses only what is not a scene', () => {
    expect(parseScene(null).ok).toBe(false);
    expect(parseScene([]).ok).toBe(false);
    expect(parseScene({ version: 1 }).ok).toBe(false);
    const empty = parseScene({ parts: [] });
    expect(empty.ok && empty.scene).toMatchObject({ links: [], missing: [], notes: [], built: '' });
  });

  it('forgives and lists: unknown kind, duplicate, lost parent, ring, bad link, old version', () => {
    const r = parseScene({
      version: 3,
      parts: [
        { id: 'a', kind: 'gizmo' },
        { id: 'a' },
        { id: 'b', parent: 'nowhere' },
        { id: 'c', parent: 'd' },
        { id: 'd', parent: 'c' },
        { name: 'no id' },
      ],
      links: [{ id: 'L', from: { part: 'a' }, to: { part: 'ghost' } }, 'junk'],
      missing: ['a plain string', 7],
      notes: ['n', 3],
    });
    if (!r.ok) throw new Error(r.reason);
    expect(r.scene.parts.map((p) => [p.id, p.kind, p.parent])).toEqual([
      ['a', 'module', null],
      ['b', 'module', null],
      ['c', 'module', 'd'],
      ['d', 'module', null],
    ]);
    expect(r.scene.links).toHaveLength(1);
    expect(r.scene.missing).toEqual([{ part: '', what: 'a plain string', why: '' }]);
    expect(r.scene.notes).toEqual(['n']);
    const text = r.problems.join('\n');
    for (const w of ['version 3', "kind 'gizmo'", 'listed twice', "'nowhere'", 'ring', "'ghost'", 'part 6 has no id']) expect(text).toContain(w);
  });
});

describe('the tree', () => {
  it('top level, children, family, root', () => {
    expect(topLevel(s).map((p) => p.id)).toEqual(['control-unit', 'pmu', 'ground-point']);
    expect(childrenOf(s, 'control-unit').map((p) => p.id)).toEqual(['dcu-carrier']);
    expect([...family(s, 'control-unit')]).toEqual(['control-unit', 'dcu-carrier']);
    expect(rootOf(s, 'dcu-carrier')).toBe('control-unit');
    expect(rootOf(s, 'pmu')).toBe('pmu');
  });
});

describe('the frames', () => {
  it('car (x right, y forward, z up) goes to three.js y up without a mirror', () => {
    near(new Vector3(1, 2, 3).applyMatrix4(CAR_TO_THREE), 1, 3, -2);
    expect(CAR_TO_THREE.determinant()).toBeCloseTo(1, 9);
  });

  it('rotations are intrinsic X then Y then Z, in degrees', () => {
    near(new Vector3(1, 0, 0).applyMatrix4(placeMatrix({ x: 0, y: 0, z: 0, rx: 0, ry: 0, rz: 90 })), 0, 1, 0);
    // X 90 turns the part's Y onto the car's Z; Y 90 is then about that, taking its X to the car's Y
    near(new Vector3(1, 0, 0).applyMatrix4(placeMatrix({ x: 0, y: 0, z: 0, rx: 90, ry: 90, rz: 0 })), 0, 1, 0);
    // rotation about the origin first, then the move
    near(new Vector3(10, 0, 0).applyMatrix4(placeMatrix({ x: 5, y: 6, z: 7, rx: 0, ry: 0, rz: 180 })), -5, 6, 7);
  });

  it('a child is placed in its parent frame', () => {
    near(new Vector3(60, 0, 2).applyMatrix4(worldMatrix(s, 'dcu-carrier')), -200, 460, 612);
    near(new Vector3(60, 0, 2).applyMatrix4(matrixUnder(s, 'dcu-carrier', 'control-unit')), 0, 60, 12);
  });
});

describe('the links', () => {
  it('runs connector to connector through each part place', () => {
    const e = linkEnds(s, s.links[0])!;
    near(e.from.at, -200, 340, 625);
    near(e.to.at, 290, 200, 400);
    expect(e.from.exact && e.to.exact).toBe(true);
  });

  it('falls back to the part centre when the connector is not placed', () => {
    const e = linkEnds(s, s.links[1])!;
    near(e.from.at, 300, 200, 400);
    near(e.to.at, 0, 0, 300);
    expect(e.from.exact || e.to.exact).toBe(false);
    const centred = linkEnds(s, s.links[1], new Map([['pmu', new Vector3(300, 200, 420)]]))!;
    near(centred.from.at, 300, 200, 420);
  });

  it('finds a connector on a part inside the one named', () => {
    const p = endPoint(s, { part: 'control-unit', connector: 'J1' })!;
    near(p.at, -200, 460, 612);
    expect(p.exact).toBe(true);
    expect(endPoint(s, { part: 'nobody', connector: 'J1' })).toBeNull();
  });
});

describe('isolating', () => {
  it('a tap isolates, the same tap restores', () => {
    const a = tap(null, { kind: 'part', id: 'pmu' });
    expect(a).toEqual({ kind: 'part', id: 'pmu' });
    expect(tap(a, { kind: 'part', id: 'pmu' })).toBeNull();
    expect(tap(a, { kind: 'link', id: 'pmu' })).toEqual({ kind: 'link', id: 'pmu' });
    expect(tap(a, null)).toBeNull();
  });

  it('a part keeps its links; a link keeps its two parts; a board answers for its unit', () => {
    expect(focusOf(s, null)).toBeNull();
    const pmu = focusOf(s, { kind: 'part', id: 'pmu' })!;
    expect([...pmu.parts]).toEqual(['pmu']);
    expect([...pmu.links]).toEqual(['DP-DCU', 'GND-1']);
    const link = focusOf(s, { kind: 'link', id: 'GND-1' })!;
    expect([...link.parts]).toEqual(['pmu', 'ground-point']);
    expect([...link.links]).toEqual(['GND-1']);
    expect([...focusOf(s, { kind: 'part', id: 'dcu-carrier' })!.parts]).toEqual(['control-unit']);
    expect(focusOf(s, { kind: 'part', id: 'gone' })).toBeNull();
  });
});

describe('the camera fit', () => {
  it('stands back far enough for the narrower field', () => {
    expect(fitDistance(100, 90, 1)).toBeCloseTo(115 / Math.sin(Math.PI / 4), 6);
    expect(fitDistance(100, 90, 0.5)).toBeCloseTo(115 / Math.sin(Math.atan(0.5)), 6);
    expect(fitDistance(100, 90, 0.5)).toBeGreaterThan(fitDistance(100, 90, 2));
  });

  it('frames every corner of a box from the direction asked, tighter than its sphere', () => {
    const box = new Box3(new Vector3(-100, -100, -100), new Vector3(100, 300, 100));
    const v = fitView(corners(box), new Vector3(0, 0, 2), 30, 1.5);
    near(v.target, 0, 100, 0);
    // the tallest corner decides: 100 deep, 200 up, a 15 degree half-field
    near(v.position, 0, 100, 100 + (1.15 * 200) / Math.tan((15 * Math.PI) / 180));
    expect(v.position.z).toBeLessThan(fitDistance(new Vector3(200, 400, 200).length() / 2, 30, 1.5));
    expect(v.near).toBeLessThan(v.position.z - 100);
    expect(v.far).toBeGreaterThan(v.position.z + 100);
    expect(fitView([], new Vector3(1, 0, 0), 30, 1).target.length()).toBe(0);
    // one point is framed as if it were minRadius across
    expect(fitView([new Vector3(5, 5, 5)], new Vector3(0, 0, 1), 30, 1, 120).position.z).toBeCloseTo(5 + fitDistance(120, 30, 1), 6);
  });
  it('centres what the camera sees, not the box: the near side looks bigger', () => {
    const pts = [new Vector3(-200, 0, 600), new Vector3(400, 0, -600), new Vector3(0, 100, 0), new Vector3(0, -100, 0)];
    const v = fitView(pts, new Vector3(0, 0, 1), 30, 1);
    const tan = Math.tan((15 * Math.PI) / 180);
    const xs = pts.map((p) => (p.x - v.target.x) / ((v.position.z - p.z) * tan));
    expect(Math.min(...xs) + Math.max(...xs)).toBeCloseTo(0, 2);
    expect(Math.max(...xs.map(Math.abs))).toBeLessThanOrEqual(1 / 1.15 + 1e-6);
  });
  it('looks straight down at a board without losing its bearings', () => {
    const v = fitView(corners(new Box3(new Vector3(-70, -1, -50), new Vector3(70, 1, 50))), new Vector3(0, 1, 0.0001), 35, 1);
    expect(Number.isFinite(v.position.y)).toBe(true);
    expect(v.position.y).toBeGreaterThan(100);
  });
});

describe('reading a model into its part frame', () => {
  it('metres and y up, as glTF is written (the stub housing and board)', () => {
    expect(glbReading({ x: 0.16, y: 0.05, z: 0.12 }, { x: 160, y: 120, z: 50 })).toEqual({ scale: 1000, yUp: true });
    expect(glbReading({ x: 0.14, y: 0.0016, z: 0.1 }, { x: 140, y: 100, z: 1.6 })).toEqual({ scale: 1000, yUp: true });
  });
  it('millimetres and z up, when that is what matches', () => {
    expect(glbReading({ x: 160, y: 120, z: 50 }, { x: 160, y: 120, z: 50 })).toEqual({ scale: 1, yUp: false });
  });
  it('without a size: the spec, unless clearly millimetres', () => {
    expect(glbReading({ x: 0.2, y: 0.1, z: 0.1 }, null)).toEqual({ scale: 1000, yUp: true });
    expect(glbReading({ x: 300, y: 10, z: 10 }, null)).toEqual({ scale: 1, yUp: true });
  });
  it('the matrix turns y up into z up and scales', () => {
    near(new Vector3(0, 0.05, 0).applyMatrix4(glbMatrix({ scale: 1000, yUp: true })), 0, 0, 50);
    near(new Vector3(0, 0, 0.12).applyMatrix4(glbMatrix({ scale: 1000, yUp: true })), 0, -120, 0);
  });
  it('node groups match the name GLTFLoader keeps or the one it cleans', () => {
    expect(nodeMatches('casebody', 'case:body', 'case:body')).toBe(true);
    expect(nodeMatches('casebody', undefined, 'case:body')).toBe(true);
    expect(nodeMatches('inside_carrier', undefined, 'inside carrier')).toBe(true);
    expect(nodeMatches('casebody', 'case:body', 'inside:carrier')).toBe(false);
  });
});

describe('an absent scene', () => {
  it('is a 404, or the app page answering for a missing file', () => {
    expect(looksAbsent(404, '')).toBe(true);
    expect(looksAbsent(200, '<!doctype html><html>')).toBe(true);
    expect(looksAbsent(200, '{"version":1}')).toBe(false);
  });
});

describe('the scene says how its models are written', () => {
  it('reads frame.glb before guessing, ignoring what a bracket says it is not', () => {
    expect(frameGlb("mm, z up, the part's own frame (not glTF's metres, y up)")).toEqual({ scale: 1, yUp: false });
    expect(frameGlb('metres, y up')).toEqual({ scale: 1000, yUp: true });
    expect(frameGlb('mm')).toBeNull();
    expect(frameGlb(undefined)).toBeNull();
  });
});

describe('what the camera frames', () => {
  it('by default the modelled parts only, never the far-end nodes', () => {
    const f = fitSet(s, null);
    expect([...f.parts]).toEqual(['control-unit', 'pmu']);
    expect(f.links.size).toBe(0);
  });
  it('an isolated part: its own box, not its links far ends', () => {
    const f = fitSet(s, { kind: 'part', id: 'pmu' });
    expect([...f.parts]).toEqual(['pmu']);
    expect(f.links.size).toBe(0);
    expect([...fitSet(s, { kind: 'part', id: 'dcu-carrier' }).parts]).toEqual(['control-unit']);
  });
  it('an isolated link: its modelled ends and both end points', () => {
    const f = fitSet(s, { kind: 'link', id: 'GND-1' });
    expect([...f.parts]).toEqual(['pmu']);
    expect([...f.links]).toEqual(['GND-1']);
  });
  it('everything: every part and every far end', () => {
    const f = fitSet(s, { kind: 'part', id: 'pmu' }, true);
    expect(f.parts.size).toBe(3);
    expect(f.links.size).toBe(2);
  });
  it('a scene of nodes alone still frames something', () => {
    const r = parseScene({ parts: [{ id: 'n', kind: 'node' }] });
    expect(r.ok && [...fitSet(r.scene, null).parts]).toEqual(['n']);
  });
});

describe('labels', () => {
  it('sit mid-way between two models, near the model when the other end is far', () => {
    expect(labelT(1000, true, true, 160)).toBe(0.5);
    expect(labelT(1000, false, false, 160)).toBe(0.5);
    expect(labelT(2000, true, false, 160)).toBeCloseTo(0.08, 9);
    expect(labelT(2000, false, true, 160)).toBeCloseTo(0.92, 9);
    expect(labelT(200, true, false, 160)).toBe(0.5);
  });
  it('never overlap: the first kept, a clash dropped, off screen dropped', () => {
    const keep = declutter(
      [
        { x: 100, y: 100, w: 60, h: 20 },
        { x: 120, y: 105, w: 60, h: 20 }, // overlaps the first
        { x: 100, y: 130, w: 60, h: 20 }, // clear below it
        { x: 500, y: 100, w: 60, h: 20 }, // off a 400-wide screen
      ],
      400,
      300,
    );
    expect(keep).toEqual([{ dx: 0, dy: 0 }, null, { dx: 0, dy: 0 }, null]);
  });
  it('a label with somewhere else to go goes there', () => {
    const keep = declutter(
      [
        { x: 100, y: 100, w: 60, h: 20 },
        { x: 110, y: 100, w: 60, h: 20, alts: [-40, 40] },
        { x: 105, y: 62, w: 60, h: 20, alts: [-60] }, // on the second; its only other place is off the top
      ],
      400,
      300,
    );
    expect(keep).toEqual([{ dx: 0, dy: 0 }, { dx: 0, dy: -40 }, null]);
  });
  it('a name near the edge slides in rather than vanish; one whose point is off screen does not', () => {
    const keep = declutter(
      [
        { x: 30, y: 100, w: 120, h: 20, slide: true },
        { x: 30, y: 200, w: 120, h: 20 },
        { x: -10, y: 250, w: 60, h: 20, slide: true },
      ],
      400,
      300,
    );
    expect(keep).toEqual([{ dx: 30, dy: 0 }, null, null]);
  });
  it('a node is not modelled; a unit, board or module is', () => {
    expect(modelled(s.parts.find((p) => p.id === 'ground-point'))).toBe(false);
    expect(modelled(s.parts.find((p) => p.id === 'pmu'))).toBe(true);
    expect(modelled(undefined)).toBe(false);
  });
});

// ------------------------------------------------------------------ version 2 (D-514, M3D2)


const p2 = parseScene(rawV2);
if (!p2.ok) throw new Error(p2.reason);
const s2: Scene = p2.scene;

describe('version 2: connectors, legs, the CUR', () => {
  it('reads the stub whole, with nothing to forgive', () => {
    expect(p2.problems).toEqual([]);
    expect(s2.version).toBe(2);
    expect(s2.legs.map((l) => l.id)).toEqual(['L1', 'L3']);
    const plug = s2.parts.find((p) => p.id === 'L1-S1:plug')!;
    expect(plug).toMatchObject({ kind: 'connector', family: 'DT06-12S', half: 'plug', housing: 'L1-S1', leg: 'L1 Engine', mate: 'L1-S1:receptacle' });
    expect(plug.cavities[0]).toEqual({ cav: '1', circuit: 'Ignition feed', awg: '16', colour: 'red/white', state: 'LIVE' });
  });

  it('a mate that is not in the scene, a short path and a lost branch end are listed', () => {
    const r = parseScene({
      version: 2,
      parts: [{ id: 'x:plug', kind: 'connector', housing: 'X', mate: 'x:gone' }],
      legs: [{ id: 'L9', path: [{ x: 0, y: 0, z: 0 }], branches: [{ to: 'nowhere', path: [{ x: 0, y: 0, z: 0 }, { x: 1, y: 0, z: 0 }] }] }],
    });
    if (!r.ok) throw new Error(r.reason);
    const text = r.problems.join('\n');
    for (const w of ["mate 'x:gone'", 'fewer than two points', "'nowhere'"]) expect(text).toContain(w);
    expect(r.scene.parts[0].mate).toBeNull();
    expect(legPaths(r.scene.legs[0])).toHaveLength(1); // the branch alone is drawable
  });

  it('pairs the halves into housings, with cavities, ways and where', () => {
    const hs = housingsOf(s2);
    expect(hs.map((h) => [h.code, h.plug?.id, h.receptacle?.id, h.ways, h.cavities.length])).toEqual([
      ['L1-S1', 'L1-S1:plug', 'L1-S1:receptacle', 12, 3],
      ['L3-S1', 'L3-S1:plug', 'L3-S1:receptacle', 12, 2],
    ]);
    expect(hs[0].where).toBe('Engine end');
    expect(hs[1].family).toBe('DT06-12S + DT04-12P'); // the plug's first, though the receptacle is listed first
    expect(hs[1].where).toBe('Control Unit Remote (CUR)');
    expect(waysOf('DTP04-4P')).toBe(4);
    expect(waysOf('mystery')).toBeNull();
  });

  it('groups housings by leg, in the scene leg order', () => {
    const r = parseScene({
      version: 2,
      parts: [
        { id: 'a:plug', kind: 'connector', housing: 'D-1', leg: 'Drop' },
        { id: 'b:plug', kind: 'connector', housing: 'L3-S2', leg: 'L3 Dash' },
        { id: 'c:plug', kind: 'connector', housing: 'L1-S9', leg: 'L1 Engine' },
        { id: 'd:plug', kind: 'connector', housing: 'Q-1' },
      ],
      legs: [
        { id: 'L1', name: 'L1 Engine', path: [] },
        { id: 'L3', name: 'L3 Dash', path: [] },
      ],
    });
    if (!r.ok) throw new Error(r.reason);
    expect(byLeg(r.scene).map((g) => [g.leg, g.legId, g.housings.map((h) => h.code)])).toEqual([
      ['L1 Engine', 'L1', ['L1-S9']],
      ['L3 Dash', 'L3', ['L3-S2']],
      ['Drop', null, ['D-1']],
      ['No leg', null, ['Q-1']],
    ]);
  });

  it('connectors are drawn on their own but not listed as parts', () => {
    expect(listedTop(s2).map((p) => p.id)).toEqual(['cur', 'pmu', 'dash-post', 'engine-end', 'rear-end']);
    expect(listedChildren(s2, 'cur').map((p) => p.id)).toEqual(['left-plate']);
    expect(drawnIds(s2)).toContain('L3-S1:receptacle');
    expect(drawnIds(s2)).not.toContain('left-plate');
    expect(drawnId(s2, 'L3-S1:receptacle')).toBe('L3-S1:receptacle');
    expect(drawnId(s2, 'left-plate')).toBe('cur');
  });

  it('a receptacle on a unit sits in the unit frame', () => {
    near(new Vector3().applyMatrix4(worldMatrix(s2, 'L3-S1:receptacle')), -600, -1080, 720);
  });

  it('isolating: a housing its two halves, a leg its housings and far ends, a unit its receptacles', () => {
    const h = focusOf(s2, { kind: 'housing', id: 'L1-S1' })!;
    expect([...h.parts].sort()).toEqual(['L1-S1:plug', 'L1-S1:receptacle']);
    expect([...h.links]).toEqual(['L1-S1']);
    expect(focusOf(s2, { kind: 'part', id: 'L1-S1:receptacle' })).toEqual(h); // a tapped half is its housing
    const leg = focusOf(s2, { kind: 'leg', id: 'L3' })!;
    expect([...leg.parts].sort()).toEqual(['L3-S1:plug', 'L3-S1:receptacle', 'rear-end']);
    expect([...leg.links]).toEqual(['L3-S1']);
    expect([...leg.legs]).toEqual(['L3']);
    expect([...focusOf(s2, { kind: 'part', id: 'cur' })!.parts].sort()).toEqual(['L3-S1:receptacle', 'cur']);
    expect(focusOf(s2, { kind: 'housing', id: 'nope' })).toBeNull();
  });

  it('framing: models by default, a housing its halves, a leg its runs', () => {
    expect([...fitSet(s2, null).parts]).toEqual(['cur', 'pmu']);
    expect([...fitSet(s2, { kind: 'housing', id: 'L3-S1' }).parts].sort()).toEqual(['L3-S1:plug', 'L3-S1:receptacle']);
    const leg = fitSet(s2, { kind: 'leg', id: 'L1' });
    expect([...leg.legs]).toEqual(['L1']);
    expect(leg.parts.size).toBe(0);
    expect(fitSet(s2, null, true).legs.size).toBe(2);
  });

  it('leg geometry: the main run and each branch; a radius given or grown from its conductors', () => {
    const l3 = s2.legs[1];
    const paths = legPaths(l3);
    expect(paths).toHaveLength(2);
    expect(paths[1][0]).toEqual(l3.path[1]); // the branch leaves from a point on the main run
    expect(legRadius(l3)).toBe(5);
    // the name sits out along the main run, off the shared dash post: 260 mm, or 40% of a short run
    const at = legLabelAt(l3)!;
    const run = Math.hypot(300, 100, 50) + Math.hypot(300, 100, 70);
    expect(Math.hypot(at.x - l3.path[0].x, at.y - l3.path[0].y, at.z - l3.path[0].z)).toBeCloseTo(Math.min(260, 0.4 * run), 6);
    expect(legLabelAt({ ...l3, path: [{ x: 0, y: 0, z: 0 }, { x: 1000, y: 0, z: 0 }] })).toEqual({ x: 260, y: 0, z: 0 });
    expect(legLabelAt({ ...l3, path: [{ x: 0, y: 0, z: 0 }, { x: 100, y: 0, z: 0 }] })).toEqual({ x: 40, y: 0, z: 0 });
    expect(legRadius(s2.legs[0])).toBeGreaterThanOrEqual(3);
    expect(legRadius({ ...s2.legs[0], conductors: 200 })).toBeGreaterThan(legRadius(s2.legs[0]));
  });
});

describe('the layers', () => {
  it('start with the legs on and the straight links off when there are legs; v1 as it was', () => {
    expect(defaultToggles(s2)).toEqual({ legs: true, links: false, connectors: true, labels: true });
    expect(defaultToggles(s)).toEqual({ legs: false, links: true, connectors: true, labels: true });
  });
  it('a layer turned off still shows what is isolated', () => {
    const off = { legs: false, links: false, connectors: false, labels: true };
    const f = focusOf(s2, { kind: 'leg', id: 'L3' });
    expect(linkShown(off, null, 'L3-S1')).toBe(false);
    expect(linkShown(off, f, 'L3-S1')).toBe(true);
    expect(linkShown(off, f, 'L1-S1')).toBe(false);
    expect(legShown(off, f, 'L3')).toBe(true);
    expect(legShown(off, f, 'L1')).toBe(false);
    expect(connectorShown(off, f, 'L3-S1:plug')).toBe(true);
    expect(connectorShown(off, f, 'L1-S1:plug')).toBe(false);
    expect(connectorShown({ ...off, connectors: true }, null, 'L1-S1:plug')).toBe(true);
  });
});
