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

export const KINDS = ['unit', 'pcb', 'module', 'node', 'connector'] as const;
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
  // version 2, a connector (one half of a housing); empty for every other kind
  family: string;
  half: 'plug' | 'receptacle' | '';
  housing: string;
  leg: string;
  mate: string | null;
  cavities: Cavity[];
}
/** One cavity of a housing (version 2): what crosses it and in what state. */
export interface Cavity {
  cav: string;
  circuit: string;
  awg: string;
  colour: string;
  state: string;
}
/** One harness leg's run (version 2): its main path from the dash post outward and its
 *  branches, each starting on the main path and ending at a far-end node, in the car frame. */
export interface Leg {
  id: string;
  name: string;
  path: Xyz[];
  branches: { to: string; path: Xyz[] }[];
  radius_mm: number | null;
  conductors: number | null;
  housings: string[];
  routes: string[];
  place_from: string;
  confirm: boolean;
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
  legs: Leg[];
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
  if (version !== 1 && version !== 2) problems.push(`the scene says version ${raw.version ?? '(none)'}; this page reads versions 1 and 2`);

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
      family: str(p.family),
      half: p.half === 'plug' || p.half === 'receptacle' ? p.half : '',
      housing: str(p.housing),
      leg: str(p.leg),
      mate: str(p.mate) || null,
      cavities: arr(p.cavities)
        .filter(isObj)
        .map((c) => ({ cav: str(c.cav), circuit: str(c.circuit), awg: str(c.awg), colour: str(c.colour), state: str(c.state) })),
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

  for (const p of parts) {
    if (p.kind !== 'connector') continue;
    if (!p.housing) problems.push(`connector ${p.id} names no housing`);
    if (p.mate && !byId.has(p.mate)) {
      problems.push(`connector ${p.id}: its mate '${p.mate}' is not in the scene`);
      p.mate = null;
    }
  }

  const pts = (v: unknown): Xyz[] => arr(v).map(xyz).filter((q): q is Xyz => !!q);
  const legs: Leg[] = [];
  arr(raw.legs).forEach((l, i) => {
    if (!isObj(l)) return;
    const id = str(l.id) || `leg ${i + 1}`;
    const leg: Leg = {
      id,
      name: str(l.name) || id,
      path: pts(l.path),
      branches: arr(l.branches)
        .filter(isObj)
        .map((b) => ({ to: str(b.to), path: pts(b.path) })),
      radius_mm: typeof l.radius_mm === 'number' && l.radius_mm > 0 ? l.radius_mm : null,
      conductors: typeof l.conductors === 'number' && Number.isFinite(l.conductors) ? l.conductors : null,
      housings: strs(l.housings),
      routes: strs(l.routes),
      place_from: str(l.place_from),
      confirm: l.confirm === true,
    };
    if (leg.path.length < 2) problems.push(`leg ${id}: its path has fewer than two points; not drawn`);
    for (const b of leg.branches) {
      if (b.path.length < 2) problems.push(`leg ${id}: a branch to '${b.to}' has fewer than two points; not drawn`);
      if (b.to && !byId.has(b.to)) problems.push(`leg ${id}: its branch end '${b.to}' is not in the scene`);
    }
    legs.push(leg);
  });

  const missing: Missing[] = arr(raw.missing)
    .map((m) => (typeof m === 'string' ? { part: '', what: m, why: '' } : isObj(m) ? { part: str(m.part), what: str(m.what), why: str(m.why) } : null))
    .filter((m): m is Missing => !!m && !!(m.part || m.what || m.why));

  const frame: Record<string, string> = {};
  if (isObj(raw.frame)) for (const [k, v] of Object.entries(raw.frame)) frame[k] = str(v);

  return {
    ok: true,
    scene: { version, built: str(raw.built), project: str(raw.project), frame, parts, links, missing, notes: strs(raw.notes), legs },
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

export const isConnector = (p: Part | undefined) => p?.kind === 'connector';

/** The parts the Parts list shows: every top-level part but the connectors, which have
 *  their own list by housing (version 2). */
export const listedTop = (s: Scene) => topLevel(s).filter((p) => !isConnector(p));
export const listedChildren = (s: Scene, id: string) => childrenOf(s, id).filter((p) => !isConnector(p));

/** What the assembly draws as its own object: every top-level part, and every connector
 *  wherever it sits (a unit's receptacle is drawn at its place, not hidden in the unit). */
export function drawnIds(s: Scene): string[] {
  return s.parts.filter((p) => !p.parent || isConnector(p)).map((p) => p.id);
}
/** The drawn object a part shows up as: a connector itself, anything else its top-level part. */
export const drawnId = (s: Scene, id: string) => (isConnector(partById(s, id)) ? id : rootOf(s, id));

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

export type Selection =
  | { kind: 'part'; id: string }
  | { kind: 'link'; id: string }
  | { kind: 'housing'; id: string }
  | { kind: 'leg'; id: string }
  | null;

/** Tapping what is already isolated restores the whole assembly; tapping anything else
 *  isolates it. */
export function tap(sel: Selection, next: Selection): Selection {
  if (!next) return null;
  return sel && sel.kind === next.kind && sel.id === next.id ? null : next;
}

export interface Focus {
  /** drawn ids (design.ts drawnIds) left at full strength */
  parts: Set<string>;
  links: Set<string>;
  legs: Set<string>;
}

/** What an isolated thing leaves at full strength (everything else fades). A part brings
 *  its connectors and the links that touch it; a link its two ends; a housing its two
 *  halves (and its link, when one has its code); a leg its housings, its far ends and its
 *  links. `null` is the whole assembly. */
export function focusOf(s: Scene, sel: Selection): Focus | null {
  if (!sel) return null;
  if (sel.kind === 'part') {
    const p = partById(s, sel.id);
    if (!p) return null;
    if (isConnector(p) && p.housing) return focusOf(s, { kind: 'housing', id: p.housing });
    const inside = family(s, sel.id);
    const links = s.links.filter((l) => inside.has(l.from.part) || inside.has(l.to.part)).map((l) => l.id);
    const own = [...family(s, rootOf(s, sel.id))].filter((id) => isConnector(partById(s, id)));
    return { parts: new Set([drawnId(s, sel.id), ...own]), links: new Set(links), legs: new Set() };
  }
  if (sel.kind === 'link') {
    const l = s.links.find((x) => x.id === sel.id);
    if (!l) return null;
    const parts = [l.from.part, l.to.part].filter((p) => partById(s, p)).map((p) => drawnId(s, p));
    return { parts: new Set(parts), links: new Set([l.id]), legs: new Set() };
  }
  if (sel.kind === 'housing') {
    const h = housingsOf(s).find((x) => x.code === sel.id);
    if (!h) return null;
    const parts = [h.plug, h.receptacle].filter((p): p is Part => !!p).map((p) => p.id);
    return { parts: new Set(parts), links: new Set(s.links.filter((l) => l.code === h.code).map((l) => l.id)), legs: new Set() };
  }
  const leg = s.legs.find((x) => x.id === sel.id);
  if (!leg) return null;
  const codes = new Set(leg.housings);
  const parts = s.parts.filter((p) => isConnector(p) && (codes.has(p.housing) || legKey(p.leg) === legKey(leg.name))).map((p) => p.id);
  for (const b of leg.branches) if (partById(s, b.to)) parts.push(b.to);
  return { parts: new Set(parts), links: new Set(s.links.filter((l) => codes.has(l.code)).map((l) => l.id)), legs: new Set([leg.id]) };
}

// ------------------------------------------------------------------ housings and legs

export interface Housing {
  code: string;
  leg: string;
  family: string;
  ways: number | null;
  plug?: Part;
  receptacle?: Part;
  cavities: Cavity[];
  where: string;
  confirm: boolean;
}

const legKey = (name: string) => name.trim().toLowerCase();

/** A family's ways from its name (DT06-12S is twelve, DTP04-4P four), else none. */
export function waysOf(family: string): number | null {
  const m = /-(\d+)/.exec(family);
  return m ? Number(m[1]) : null;
}

/** The connectors paired into housings: each housing's plug and receptacle (found by the
 *  housing code, or failing that by `mate`), both halves' families, its cavities (whichever
 *  half carries them), its ways and where it sits - the unit a half is mounted on, else the nearest far end. */
export function housingsOf(s: Scene): Housing[] {
  const out = new Map<string, Housing>();
  for (const p of s.parts) {
    if (!isConnector(p)) continue;
    let code = p.housing;
    if (!code && p.mate) code = partById(s, p.mate)?.housing ?? '';
    if (!code) code = p.id;
    let h = out.get(code);
    if (!h) {
      h = { code, leg: '', family: '', ways: null, cavities: [], where: '', confirm: false };
      out.set(code, h);
    }
    if (p.half === 'receptacle' && !h.receptacle) h.receptacle = p;
    else if (!h.plug) h.plug = p;
    else if (!h.receptacle) h.receptacle = p;
    h.leg ||= p.leg;
    h.confirm ||= p.confirm;
    if (p.cavities.length > h.cavities.length) h.cavities = p.cavities;
  }
  for (const h of out.values()) {
    // both halves' families, the plug's first (DT06-12S + DT04-12P)
    const families = [...new Set([h.plug?.family, h.receptacle?.family].filter((f): f is string => !!f))];
    h.family = families.join(' + ');
    h.ways = waysOf(families[0] ?? '') ?? (h.cavities.length || null);
    const mounted = [h.receptacle, h.plug].find((p) => p?.parent);
    h.where = mounted?.parent ? (partById(s, mounted.parent)?.name ?? mounted.parent) : nearestNode(s, (h.plug ?? h.receptacle)!.id) ?? (h.plug ?? h.receptacle)!.place_from;
  }
  return [...out.values()].sort((a, b) => a.code.localeCompare(b.code, undefined, { numeric: true }));
}

/** The name of the far-end node nearest a top-level part's place (within half a metre). */
export function nearestNode(s: Scene, id: string): string | null {
  const p = partById(s, id);
  if (!p || p.parent) return null;
  let best: { name: string; d: number } | null = null;
  for (const n of s.parts) {
    if (n.kind !== 'node' || n.parent) continue;
    const d = Math.hypot(n.place.x - p.place.x, n.place.y - p.place.y, n.place.z - p.place.z);
    if (d <= 500 && (!best || d < best.d)) best = { name: n.name, d };
  }
  return best?.name ?? null;
}

/** The housings grouped by leg, in the scene's own leg order, then any other leg by name,
 *  then those with none. `legId` is the scene leg the group is, when there is one. */
export function byLeg(s: Scene, hs: Housing[] = housingsOf(s)): { leg: string; legId: string | null; housings: Housing[] }[] {
  const groups = new Map<string, { leg: string; legId: string | null; housings: Housing[] }>();
  const legOf = (h: Housing) => s.legs.find((l) => l.housings.includes(h.code)) ?? s.legs.find((l) => legKey(l.name) === legKey(h.leg) || legKey(l.id) === legKey(h.leg));
  for (const h of hs) {
    const leg = legOf(h);
    const name = leg?.name ?? (h.leg || 'No leg');
    const g = groups.get(name) ?? { leg: name, legId: leg?.id ?? null, housings: [] };
    g.housings.push(h);
    groups.set(name, g);
  }
  const order = (g: { leg: string; legId: string | null }) => {
    const i = s.legs.findIndex((l) => l.id === g.legId);
    return i >= 0 ? i : g.leg === 'No leg' ? 1e9 : 1e6;
  };
  return [...groups.values()].sort((a, b) => order(a) - order(b) || a.leg.localeCompare(b.leg, undefined, { numeric: true }));
}

/** Where a leg's name sits: a little way out along its main run (at most `reach` mm, at
 *  most 40% of it), so legs that leave the same dash post do not stack their names. */
export function legLabelAt(leg: Leg, reach = 260): Xyz | null {
  const path = leg.path;
  if (path.length < 2) return path[0] ?? null;
  const seg = path.slice(1).map((q, i) => Math.hypot(q.x - path[i].x, q.y - path[i].y, q.z - path[i].z));
  let want = Math.min(reach, 0.4 * seg.reduce((a, b) => a + b, 0));
  for (let i = 0; i < seg.length; i++) {
    if (want <= seg[i] || i === seg.length - 1) {
      const t = seg[i] ? Math.min(1, want / seg[i]) : 0;
      const a = path[i];
      const b = path[i + 1];
      return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t, z: a.z + (b.z - a.z) * t };
    }
    want -= seg[i];
  }
  return path[0];
}

/** A leg's runs that can be drawn: the main path, then each branch, two points or more. */
export function legPaths(leg: Leg): Xyz[][] {
  return [leg.path, ...leg.branches.map((b) => b.path)].filter((p) => p.length >= 2);
}

/** A tube's radius: the scene's, else one that grows with the conductors in it (a bundle of
 *  n wires about 1.2 mm across each), never under 3 mm. */
export function legRadius(leg: Leg): number {
  if (leg.radius_mm) return leg.radius_mm;
  return Math.max(3, Math.round(0.6 * Math.sqrt(leg.conductors ?? 10) * 1.15 * 10) / 10);
}

/** One colour per leg, by its place in the scene's list (sky, ember, gold, green, violet). */
export const LEG_COLOURS = [0x98c1d9, 0xee6c4d, 0xe9c46a, 0x8fd694, 0xb39ddb] as const;
export const legColour = (s: Scene, id: string) => LEG_COLOURS[Math.max(0, s.legs.findIndex((l) => l.id === id)) % LEG_COLOURS.length];
export const legColourCss = (s: Scene, id: string) => `#${legColour(s, id).toString(16).padStart(6, '0')}`;

// ------------------------------------------------------------------ toggles

export interface Toggles {
  legs: boolean;
  links: boolean;
  connectors: boolean;
  labels: boolean;
}

/** The assembly's starting toggles: the legs on when the scene has them, and then the
 *  straight links off (the legs carry the harness); connectors and labels on. */
export function defaultToggles(s: Scene): Toggles {
  return { legs: s.legs.length > 0, links: s.legs.length === 0, connectors: true, labels: true };
}

/** What is drawn under the toggles: a layer turned off still shows what is isolated. */
export const linkShown = (t: Toggles, f: Focus | null, id: string) => (f ? f.links.has(id) : t.links);
export const legShown = (t: Toggles, f: Focus | null, id: string) => (f?.legs.has(id) ? true : t.legs);
export const connectorShown = (t: Toggles, f: Focus | null, id: string) => (f?.parts.has(id) ? true : t.connectors);

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

/** The scene's own word on its models (`frame.glb`, e.g. "mm, z up, the part's own frame"),
 *  read before any guess: the units and the up axis, from the text before any bracket (which
 *  may name what it is not). `null` when it does not say both - then glbReading guesses. */
export function frameGlb(text: string | undefined): { scale: number; yUp: boolean } | null {
  if (!text) return null;
  const t = text.split('(')[0].toLowerCase();
  const scale = /\bmm\b|millimet/.test(t) ? 1 : /\bm\b|\bmetres?\b|\bmeters?\b/.test(t) ? 1000 : null;
  const yUp = /\bz[ -]?up\b/.test(t) ? false : /\by[ -]?up\b/.test(t) ? true : null;
  return scale == null || yUp == null ? null : { scale, yUp };
}

// ------------------------------------------------------------------ framing and labels

/** A part with a model of its own (a node is only a place, a far end of the harness). */
export const modelled = (p: Part | undefined) => !!p && (p.kind === 'unit' || p.kind === 'pcb' || p.kind === 'module');

/** What the assembly's camera frames. By default, and on "Show everything", the units,
 *  boards and modules only - the far-end nodes and the legs' connectors are spread over the
 *  whole car and would shrink the units to dots. An isolated part: its own box. A link: its
 *  two ends. A housing: its two halves. A leg: its runs. `all`: everything, every far end
 *  and every leg. Parts are drawn ids; links count by their end points, legs by their paths. */
export function fitSet(s: Scene, sel: Selection, all = false): { parts: Set<string>; links: Set<string>; legs: Set<string> } {
  const drawn = drawnIds(s);
  const none = new Set<string>();
  if (all) return { parts: new Set(drawn), links: new Set(s.links.map((l) => l.id)), legs: new Set(s.legs.map((l) => l.id)) };
  const f = focusOf(s, sel);
  if (f && sel?.kind === 'part' && !isConnector(partById(s, sel.id))) return { parts: new Set([drawnId(s, sel.id)]), links: none, legs: none };
  if (f && sel?.kind === 'link') return { parts: new Set([...f.parts].filter((id) => modelled(partById(s, id)))), links: f.links, legs: none };
  if (f && sel?.kind === 'leg') return { parts: none, links: none, legs: f.legs };
  if (f) return { parts: f.parts, links: none, legs: none };
  const models = drawn.filter((id) => modelled(partById(s, id)));
  return { parts: new Set(models.length ? models : drawn), links: none, legs: none };
}

/** Where along a link (0 at `from`, 1 at `to`) its label sits: the middle between two
 *  modelled parts (or two nodes), else `reach` mm out from the modelled end, so a unit's
 *  labels gather round it rather than out in the car where its far ends are. */
export function labelT(length: number, fromModelled: boolean, toModelled: boolean, reach: number): number {
  if (fromModelled === toModelled || !(length > 0)) return 0.5;
  const t = Math.min(0.5, reach / length);
  return fromModelled ? t : 1 - t;
}

export interface LabelBox {
  x: number;
  y: number;
  w: number;
  h: number;
  /** other places to try, as downward shifts in pixels, when the first is taken */
  alts?: number[];
  /** may slide sideways to stay wholly on screen (a part's name near the edge) */
  slide?: boolean;
}

/** Never more labels than can be read: given label boxes (centre x, y in screen pixels) in
 *  order of importance, keep each one wholly on screen and clear of every one kept before
 *  it, with `pad` pixels between - where it is, else at the first of its `alts` that is
 *  clear, slid in from the edge when it may slide. Each answer is the shift used ({dx, dy},
 *  zero where it is), or null when it is not shown. */
export function declutter(items: LabelBox[], width: number, height: number, pad = 4): ({ dx: number; dy: number } | null)[] {
  const kept: LabelBox[] = [];
  const fits = (b: LabelBox) =>
    b.x - b.w / 2 >= 0 &&
    b.y - b.h / 2 >= 0 &&
    b.x + b.w / 2 <= width &&
    b.y + b.h / 2 <= height &&
    kept.every((k) => Math.abs(k.x - b.x) * 2 >= k.w + b.w + pad * 2 || Math.abs(k.y - b.y) * 2 >= k.h + b.h + pad * 2);
  return items.map((b) => {
    // slide in from the edge only for an anchor that is itself on screen
    const onScreen = b.x >= 0 && b.x <= width;
    const dx = b.slide && onScreen && b.w <= width ? Math.min(Math.max(b.x, b.w / 2), width - b.w / 2) - b.x : 0;
    for (const dy of [0, ...(b.alts ?? [])]) {
      const at = { ...b, x: b.x + dx, y: b.y + dy };
      if (fits(at)) {
        kept.push(at);
        return { dx, dy };
      }
    }
    return null;
  });
}

// ------------------------------------------------------------------ words

export const KIND_LABEL: Record<Kind, string> = { unit: 'Unit', pcb: 'Board', module: 'Module', node: 'Point', connector: 'Connector' };

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
