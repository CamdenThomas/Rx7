// The Design page's pure half (D-505, M3D1) on a stub scene: two units, a board inside one,
// a node, two links and a missing entry. three.js appears only as its math.
import { Box3, Vector3 } from 'three';
import { describe, expect, it } from 'vitest';
import raw from './fixtures/design/scene.json';
import { childrenOf, family, fitDistance, focusOf, glbReading, looksAbsent, nodeMatches, parseScene, rootOf, tap, topLevel, type Scene } from '../src/lib/design';
import { CAR_TO_THREE, endPoint, fitView, glbMatrix, linkEnds, matrixUnder, placeMatrix, worldMatrix } from '../src/lib/designMath';

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
      version: 2,
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
    for (const w of ['version 2', "kind 'gizmo'", 'listed twice', "'nowhere'", 'ring', "'ghost'", 'part 6 has no id']) expect(text).toContain(w);
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

  it('frames a box from the direction asked', () => {
    const v = fitView(new Box3(new Vector3(-100, -100, -100), new Vector3(100, 300, 100)), new Vector3(0, 0, 2), 30, 1.5);
    near(v.target, 0, 100, 0);
    const r = new Vector3(200, 400, 200).length() / 2;
    near(v.position, 0, 100, fitDistance(r, 30, 1.5));
    expect(v.near).toBeLessThan(v.position.z - r);
    expect(v.far).toBeGreaterThan(v.position.z + r);
    expect(fitView(new Box3(), new Vector3(1, 0, 0), 30, 1).target.length()).toBe(0);
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
