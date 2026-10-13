/**
 * The Design page's pure half (D-505, work row M3D1): the scene file read defensively, the
 * tree of parts, what an isolated part shows, the camera distance and a model's reading.
 * No three.js here at all, so the page's lists never carry it; the matrices are
 * designMath.ts and the drawing designView.ts, both loaded with the 3D view.
 *
 * It owns no fact and reads no table: everything comes from
 * public/design/<project>/scene.json, written with the models by 01-electrical Y23's export
 * script from the design itself (KiCad, FreeCAD, the vendor's STEP). The scene is a view of
 * the design, never a source of facts (R11): a measurement beats it.
 */

export const KINDS = ['unit', 'pcb', 'module', 'node'] as const;
export type Kind = (typeof KINDS)[number];

export interface Xyz {
  x: number;
  y: number;
  z: number;
}
export interface Place extends Xyz {
  rx: number;
  ry: number;
  rz: number;
}
export interface Connector {
  code: string;
  at: Xyz | null;
  face: string;
  note: string;
}
export interface Part {
  id: string;
  name: string;
  kind: Kind;
  glb: string | null;
  bytes: number | null;
  parent: string | null;
  place: Place;
  place_from: string;
  confirm: boolean;
  size_mm: Xyz | null;
  origin: string;
  connectors: Connector[];
  children: string[];
  source: string;
  nodes: { case: string[]; inside: string[] };
}
export interface End {
  part: string;
  connector: string;
}
export interface Link {
  id: string;
  code: string;
  from: End;
  to: End;
  label: string;
  ways: number | null;
  carries: string[];
  confirm: boolean;
}
export interface Missing {
  part: string;
  what: string;
  why: string;
}
export interface Scene {
  version: number;
  built: string;
  project: string;
  frame: Record<string, string>;
  parts: Part[];
  links: Link[];
  missing: Missing[];
  notes: string[];
}
export type Parsed = { ok: true; scene: Scene; problems: string[] } | { ok: false; reason: string };

// ------------------------------------------------------------------ reading the file

type Obj = Record<string, unknown>;
const isObj = (v: unknown): v is Obj => typeof v === 'object' && v !== null && !Array.isArray(v);
const str = (v: unknown, d = ''): string => (typeof v === 'string' ? v : typeof v === 'number' ? String(v) : d);
const num = (v: unknown, d = 0): number => (typeof v === 'number' && Number.isFinite(v) ? v : d);
const arr = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);
const strs = (v: unknown): string[] => arr(v).filter((s) => typeof s === 'string' && s !== '') as string[];
const xyz = (v: unknown): Xyz | null => (isObj(v) ? { x: num(v.x), y: num(v.y), z: num(v.z) } : null);

/** The scene file, every field treated as possibly absent or wrong: a missing array is
 *  empty, an unknown kind is a module, a parent that is not in the scene (or that makes a
 *  ring) is dropped. Everything forgiven is listed in `problems`, which the page shows; only
 *  a file that is not a scene at all is refused. */
export function parseScene(raw: unknown): Parsed {
  if (!isObj(raw)) return { ok: false, reason: 'the file is not a JSON object' };
  if (!Array.isArray(raw.parts)) return { ok: false, reason: 'the file has no parts list' };
  const problems: string[] = [];
  const version = num(raw.version, 0);
  if (version !== 1) problems.push(`the scene says version ${raw.version ?? '(none)'}; this page reads version 1`);

  const parts: Part[] = [];
  const seen = new Set<string>();
  raw.parts.forEach((p, i) => {
    if (!isObj(p) || !str(p.id)) {
      problems.push(`part ${i + 1} has no id and is left out`);
      return;
    }
    const id = str(p.id);
    if (seen.has(id)) {
      problems.push(`part ${id} is listed twice; the second is left out`);
      return;
    }
    seen.add(id);
    let kind = str(p.kind) as Kind;
    if (!KINDS.includes(kind)) {
      if (p.kind !== undefined) problems.push(`part ${id}: kind '${str(p.kind)}' is not known; shown as a module`);
      kind = 'module';
    }
    const place = isObj(p.place) ? p.place : {};
    const nodes = isObj(p.nodes) ? p.nodes : {};
    parts.push({
      id,
      name: str(p.name) || id,
      kind,
      glb: str(p.glb) || null,
      bytes: typeof p.bytes === 'number' && Number.isFinite(p.bytes) ? p.bytes : null,
      parent: str(p.parent) || null,
      place: { x: num(place.x), y: num(place.y), z: num(place.z), rx: num(place.rx), ry: num(place.ry), rz: num(place.rz) },
      place_from: str(p.place_from),
      confirm: p.confirm === true,
      size_mm: xyz(p.size_mm),
      origin: str(p.origin),
      connectors: arr(p.connectors)
        .filter(isObj)
        .map((c) => ({ code: str(c.code), at: xyz(c.at), face: str(c.face), note: str(c.note) }))
        .filter((c) => c.code),
      children: strs(p.children),
      source: str(p.source),
      nodes: { case: strs(nodes.case), inside: strs(nodes.inside) },
    });
  });

  // A parent names the frame a child is placed in, so it must exist and must not loop.
  const byId = new Map(parts.map((p) => [p.id, p]));
  for (const p of parts) {
    if (p.parent && (p.parent === p.id || !byId.has(p.parent))) {
      problems.push(`part ${p.id}: parent '${p.parent}' is not in the scene; placed in the car frame`);
      p.parent = null;
    }
  }
  for (const p of parts) {
    const path = new Set<string>([p.id]);
    let q = p;
    while (q.parent) {
      if (path.has(q.parent)) {
        problems.push(`part ${q.id}: parent '${q.parent}' makes a ring; placed in the car frame`);
        q.parent = null;
        break;
      }
      path.add(q.parent);
      q = byId.get(q.parent)!;
    }
  }
  for (const p of parts) {
    for (const c of p.children) {
      if (!byId.has(c)) problems.push(`part ${p.id}: child '${c}' is not in the scene`);
    }
  }

  const end = (v: unknown): End => (isObj(v) ? { part: str(v.part), connector: str(v.connector) } : { part: '', connector: '' });
  const links: Link[] = [];
  const linkIds = new Set<string>();
  arr(raw.links).forEach((l, i) => {
    if (!isObj(l)) return;
    let id = str(l.id) || str(l.code) || `link ${i + 1}`;
    if (linkIds.has(id)) {
      problems.push(`link ${id} is listed twice`);
      id = `${id} (${i + 1})`;
    }
    linkIds.add(id);
    const link: Link = {
      id,
      code: str(l.code) || id,
      from: end(l.from),
      to: end(l.to),
      label: str(l.label) || str(l.code) || id,
      ways: typeof l.ways === 'number' && Number.isFinite(l.ways) ? l.ways : null,
      carries: strs(l.carries),
      confirm: l.confirm === true,
    };
    for (const [side, e] of [['from', link.from], ['to', link.to]] as const) {
      if (!byId.has(e.part)) problems.push(`link ${id}: its ${side} part '${e.part}' is not in the scene; not drawn`);
    }
    links.push(link);
  });

  const missing: Missing[] = arr(raw.missing)
    .map((m) => (typeof m === 'string' ? { part: '', what: m, why: '' } : isObj(m) ? { part: str(m.part), what: str(m.what), why: str(m.why) } : null))
    .filter((m): m is Missing => !!m && !!(m.part || m.what || m.why));

  const frame: Record<string, string> = {};
  if (isObj(raw.frame)) for (const [k, v] of Object.entries(raw.frame)) frame[k] = str(v);

  return {
    ok: true,
    scene: { version, built: str(raw.built), project: str(raw.project), frame, parts, links, missing, notes: strs(raw.notes) },
    problems,
  };
}

// ------------------------------------------------------------------ the tree

export const partById = (s: Scene, id: string) => s.parts.find((p) => p.id === id);
export const topLevel = (s: Scene) => s.parts.filter((p) => !p.parent);

/** A part's children: the parts that name it as their parent, then any its own `children`
 *  list names that do not (the parent decides the frame; the list only adds to the view). */
export function childrenOf(s: Scene, id: string): Part[] {
  const out = s.parts.filter((p) => p.parent === id);
  for (const c of partById(s, id)?.children ?? []) {
    const p = partById(s, c);
    if (p && p.id !== id && !out.includes(p)) out.push(p);
  }
  return out;
}

/** The part and everything below it, each once. */
export function family(s: Scene, id: string): Set<string> {
  const out = new Set<string>();
  const walk = (x: string) => {
    if (out.has(x)) return;
    out.add(x);
    for (const c of childrenOf(s, x)) walk(c.id);
  };
  if (partById(s, id)) walk(id);
  return out;
}

/** The top-level part a part sits in (itself when it is one). */
export function rootOf(s: Scene, id: string): string {
  let p = partById(s, id);
  const seen = new Set<string>();
  while (p?.parent && !seen.has(p.id)) {
    seen.add(p.id);
    p = partById(s, p.parent);
  }
  return p?.id ?? id;
}


/** A connector on a part, or on anything inside it (a unit's link may land on its board). */
export function findConnector(s: Scene, partId: string, code: string): { part: Part; c: Connector } | null {
  if (!code) return null;
  for (const id of family(s, partId)) {
    const part = partById(s, id)!;
    const c = part.connectors.find((x) => x.code === code && x.at);
    if (c) return { part, c };
  }
  return null;
}

// ------------------------------------------------------------------ isolating

export type Selection = { kind: 'part'; id: string } | { kind: 'link'; id: string } | null;

/** Tapping what is already isolated restores the whole assembly; tapping anything else
 *  isolates it. */
export function tap(sel: Selection, next: Selection): Selection {
  if (!next) return null;
  return sel && sel.kind === next.kind && sel.id === next.id ? null : next;
}

/** What an isolated part or link leaves at full strength (everything else fades): a part
 *  brings everything inside it and the links that touch it; a link brings the two parts it
 *  joins. `null` is the whole assembly. Parts are top-level ids, the ones the assembly draws. */
export function focusOf(s: Scene, sel: Selection): { parts: Set<string>; links: Set<string> } | null {
  if (!sel) return null;
  if (sel.kind === 'part') {
    if (!partById(s, sel.id)) return null;
    const inside = family(s, sel.id);
    const links = s.links.filter((l) => inside.has(l.from.part) || inside.has(l.to.part)).map((l) => l.id);
    return { parts: new Set([rootOf(s, sel.id)]), links: new Set(links) };
  }
  const l = s.links.find((x) => x.id === sel.id);
  if (!l) return null;
  const parts = [l.from.part, l.to.part].filter((p) => partById(s, p)).map((p) => rootOf(s, p));
  return { parts: new Set(parts), links: new Set([l.id]) };
}

// ------------------------------------------------------------------ the camera

const RAD = Math.PI / 180;

/** How far back a camera with this vertical field of view and aspect must stand for a sphere
 *  of this radius to fit both ways, with a margin. */
export function fitDistance(radius: number, fovDeg: number, aspect: number, margin = 1.15): number {
  const v = (fovDeg * RAD) / 2;
  const h = Math.atan(Math.tan(v) * Math.max(aspect, 1e-3));
  return (Math.max(radius, 1) * margin) / Math.sin(Math.min(v, h));
}

// ------------------------------------------------------------------ the models

/** How a model file is read into its part's frame. glTF is y up and in metres by its spec,
 *  and both KiCad and FreeCAD write it that way, but a file may be z up or in millimetres.
 *  When the scene gives the part's size, the reading whose extents match it best wins: metres
 *  or millimetres, and y up (turned +90 degrees about x into the part's z up) or z up as it
 *  stands. Without a size the spec's reading stands, millimetres only when the model is
 *  clearly too big to be metres. `ext` is the model's bounding box size as loaded. */
export function glbReading(ext: Xyz, size: Xyz | null): { scale: number; yUp: boolean } {
  const big = Math.max(ext.x, ext.y, ext.z);
  if (!(big > 0)) return { scale: 1000, yUp: true };
  const want = size && Math.max(size.x, size.y, size.z) > 0 ? size : null;
  if (!want) return { scale: big < 5 ? 1000 : 1, yUp: true };
  let best = { scale: 1000, yUp: true, err: Infinity };
  for (const yUp of [true, false]) {
    // y up: the model's (x, y, z) extents are the part's (x, z, y)
    const e = yUp ? { x: ext.x, y: ext.z, z: ext.y } : ext;
    for (const scale of [1000, 1]) {
      let err = 0;
      let n = 0;
      for (const k of ['x', 'y', 'z'] as const) {
        if (e[k] > 0 && want[k] > 0) {
          err += Math.abs(Math.log((e[k] * scale) / want[k]));
          n++;
        }
      }
      err = n ? err / n : Infinity;
      // ties (a cube) keep the spec's reading, which is tried first
      if (err < best.err - 1e-6) best = { scale, yUp, err };
    }
  }
  return { scale: best.scale, yUp: best.yUp };
}

/** Does a loaded node answer to a name in the scene's `nodes` groups? GLTFLoader keeps the
 *  file's own name in userData.name and strips `[ ] . : /` from `name`. */
export function nodeMatches(name: string, original: string | undefined, wanted: string): boolean {
  return original === wanted || name === wanted || name === wanted.replace(/\s/g, '_').replace(/[[\].:/]/g, '');
}

// ------------------------------------------------------------------ words

export const KIND_LABEL: Record<Kind, string> = { unit: 'Unit', pcb: 'Board', module: 'Module', node: 'Point' };

export function bytesLabel(n: number | null): string {
  if (n == null) return '';
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} kB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

export function builtLabel(iso: string): string {
  const d = new Date(iso);
  if (!iso || Number.isNaN(d.getTime())) return iso || 'an unknown time';
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** The plain reading of a scene that is absent: a 404, or a dev server / app shell that
 *  answers every unknown path with the page itself. */
export function looksAbsent(status: number, body: string): boolean {
  return status === 404 || status === 0 || /^\s*</.test(body);
}
