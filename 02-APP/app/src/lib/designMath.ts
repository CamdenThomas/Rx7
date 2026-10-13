/**
 * The Design page's frames (D-505, M3D1): the car frame, each part's place, where a link's
 * ends sit, the camera's framing and a model's reading - three.js's math only, kept apart
 * from design.ts so the page's lists never carry three.js (it loads with the 3D view, like
 * CarModel's). Reads the scene (design.ts) and no table.
 */
import { Box3, Euler, Matrix4, Quaternion, Vector3 } from 'three';
import { findConnector, fitDistance, partById, type End, type Link, type Part, type Place, type Scene } from './design';

// ------------------------------------------------------------------ frames

const RAD = Math.PI / 180;

/** The car frame (D-418) is millimetres, x right, y forward, z up: right-handed. three.js is
 *  y up with the camera looking down -z. Everything is built in the car frame under one root
 *  group carrying this matrix, -90 degrees about x: car (x, y, z) -> three (x, z, -y). Right
 *  stays right, up is up, forward goes into the screen, and the determinant is +1, so
 *  nothing is mirrored. */
export const CAR_TO_THREE = new Matrix4().makeRotationX(-Math.PI / 2);

/** A part's place as a matrix: rotate rx, then ry, then rz degrees as intrinsic X-Y-Z
 *  rotations (each about the part's own axes as the previous one left them) about the part's
 *  origin, then move that origin to (x, y, z) mm. A top-level part's place is in the car
 *  frame, a child's in its parent's frame. three.js's Euler order 'XYZ' is exactly this
 *  (its matrix is Rx·Ry·Rz); the export script states its rotations in the same words. */
export function placeMatrix(p: Place): Matrix4 {
  const q = new Quaternion().setFromEuler(new Euler(p.rx * RAD, p.ry * RAD, p.rz * RAD, 'XYZ'));
  return new Matrix4().compose(new Vector3(p.x, p.y, p.z), q, new Vector3(1, 1, 1));
}

/** A part's frame in the car frame: its parents' places, outermost first, then its own. */
export function worldMatrix(s: Scene, id: string): Matrix4 {
  const chain: Part[] = [];
  const seen = new Set<string>();
  for (let p = partById(s, id); p && !seen.has(p.id); p = p.parent ? partById(s, p.parent) : undefined) {
    seen.add(p.id);
    chain.unshift(p);
  }
  const m = new Matrix4();
  for (const p of chain) m.multiply(placeMatrix(p.place));
  return m;
}

/** The same, relative to an ancestor (the part view and board view draw one part at the
 *  origin and its children placed under it). */
export function matrixUnder(s: Scene, id: string, ancestor: string): Matrix4 {
  return worldMatrix(s, ancestor).invert().multiply(worldMatrix(s, id));
}

export interface EndPoint {
  at: Vector3;
  /** true when the connector is in the scene with its place; false is the part's centre */
  exact: boolean;
}

/** Where one end of a link sits in the car frame: the connector's `at` carried through its
 *  part's place (and its parents'), else the part's centre - the loaded model's, when the
 *  viewer knows it (`centres`, car frame), else the part's origin. */
export function endPoint(s: Scene, e: End, centres?: Map<string, Vector3>): EndPoint | null {
  if (!partById(s, e.part)) return null;
  const hit = findConnector(s, e.part, e.connector);
  if (hit) return { at: new Vector3(hit.c.at!.x, hit.c.at!.y, hit.c.at!.z).applyMatrix4(worldMatrix(s, hit.part.id)), exact: true };
  const centre = centres?.get(e.part);
  return { at: centre ? centre.clone() : new Vector3().applyMatrix4(worldMatrix(s, e.part)), exact: false };
}

export function linkEnds(s: Scene, l: Link, centres?: Map<string, Vector3>): { from: EndPoint; to: EndPoint } | null {
  const from = endPoint(s, l.from, centres);
  const to = endPoint(s, l.to, centres);
  return from && to ? { from, to } : null;
}

// ------------------------------------------------------------------ the camera

/** A box's eight corners (none for an empty box). */
export function corners(b: Box3): Vector3[] {
  if (b.isEmpty()) return [];
  const out: Vector3[] = [];
  for (const x of [b.min.x, b.max.x]) for (const y of [b.min.y, b.max.y]) for (const z of [b.min.z, b.max.z]) out.push(new Vector3(x, y, z));
  return out;
}

/** The camera that frames these points (three.js coordinates), looking along `dir` (from
 *  the target towards the camera), y up: it stands back just far enough for every point to
 *  sit inside both fields of view with a margin - tighter than a bounding sphere, which
 *  leaves a long, flat set (the harness over the whole car) small in the middle. No points
 *  frame half a metre round the origin; a set smaller than `minRadius` (one node) is framed
 *  as if that big. */
export function fitView(points: Vector3[], dir: Vector3, fovDeg: number, aspect: number, minRadius = 1, margin = 1.15) {
  const box = new Box3().setFromPoints(points);
  const target = box.isEmpty() ? new Vector3() : box.getCenter(new Vector3());
  const radius = box.isEmpty() ? 500 : Math.max(box.getSize(new Vector3()).length() / 2, minRadius);
  const back = dir.lengthSq() ? dir.clone().normalize() : new Vector3(0, 0, 1);
  const right = new Vector3().crossVectors(new Vector3(0, 1, 0), back);
  if (right.lengthSq() < 1e-10) right.set(1, 0, 0);
  right.normalize();
  const up = new Vector3().crossVectors(back, right).normalize();
  const tanV = Math.tan((fovDeg * RAD) / 2);
  const tanH = tanV * Math.max(aspect, 1e-3);
  const q = new Vector3();
  const stand = () => {
    let d = fitDistance(box.isEmpty() ? 500 : minRadius, fovDeg, aspect, margin);
    for (const p of points) {
      q.subVectors(p, target);
      d = Math.max(d, q.dot(back) + margin * Math.max(Math.abs(q.dot(right)) / tanH, Math.abs(q.dot(up)) / tanV));
    }
    return d;
  };
  let distance = stand();
  // Seen in perspective the near side looks bigger, so the box's centre is not the picture's:
  // move the target across the view to centre what the camera sees, and stand again.
  for (let i = 0; i < 8 && points.length > 1; i++) {
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (const p of points) {
      q.subVectors(p, target);
      const depth = Math.max(distance - q.dot(back), 1e-6);
      const x = q.dot(right) / (depth * tanH);
      const y = q.dot(up) / (depth * tanV);
      x0 = Math.min(x0, x);
      x1 = Math.max(x1, x);
      y0 = Math.min(y0, y);
      y1 = Math.max(y1, y);
    }
    const mx = (x0 + x1) / 2;
    const my = (y0 + y1) / 2;
    if (Math.abs(mx) < 1e-3 && Math.abs(my) < 1e-3) break;
    target.addScaledVector(right, mx * tanH * distance).addScaledVector(up, my * tanV * distance);
    distance = stand();
  }
  return { target, position: target.clone().addScaledVector(back, distance), near: Math.max(distance / 100, 0.1), far: distance * 20 + radius * 4 };
}

// ------------------------------------------------------------------ the models

/** The matrix that carries a model's own coordinates into its part's frame. */
export function glbMatrix(r: { scale: number; yUp: boolean }): Matrix4 {
  const m = r.yUp ? new Matrix4().makeRotationX(Math.PI / 2) : new Matrix4();
  return m.multiply(new Matrix4().makeScale(r.scale, r.scale, r.scale));
}
