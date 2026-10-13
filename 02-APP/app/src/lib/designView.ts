/**
 * The Design page's drawing (D-505, M3D1; version 2 for 01-electrical D-514, M3D2): one
 * three.js view of a scene - the assembly, one part with its children, or one board - over a
 * canvas, with the labels as DOM elements (CSS2DRenderer: plain HTML, so they read the same
 * in Android's WebView as on the desktop). Everything placed is built in the car frame under
 * one root (designMath.ts's CAR_TO_THREE): the parts and every connector at its place, the
 * legs as tubes along their paths, the D-505 links as straight lines. Imported only on
 * demand, like CarModel's three.js, so the page's lists never wait on it. It reads
 * public/design/<project>/scene.json's models and no table. No part is ever moved here.
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import { CAR_TO_THREE, corners, fitView, glbMatrix, linkEnds, matrixUnder, placeMatrix, worldMatrix } from './designMath';
import {
  childrenOf,
  connectorShown,
  declutter,
  defaultToggles,
  drawnId,
  drawnIds,
  family,
  findConnector,
  fitSet,
  focusOf,
  frameGlb,
  glbReading,
  isConnector,
  labelT,
  legColour,
  legLabelAt,
  legPaths,
  legRadius,
  legShown,
  linkShown,
  modelled,
  nodeMatches,
  partById,
  type Focus,
  type Part,
  type Scene,
  type Selection,
  type Toggles,
} from './design';

export type Mode = { kind: 'assembly' } | { kind: 'part'; id: string } | { kind: 'board'; id: string };
export type LoadState = { state: 'loading' | 'ready' | 'none' } | { state: 'failed'; why: string };

export interface ViewerHooks {
  /** a part tapped in the 3D (its drawn id in the assembly; a connector answers for its
   *  housing), a leg's tube or label, or a link label */
  pick(sel: Selection): void;
  status(id: string, s: LoadState): void;
  /** the part view's named node groups, as found in its model */
  nodes(found: { case: boolean; inside: boolean }): void;
}

const FOV = 35;
// Where the camera starts, from the target, in the car frame: behind, on the driver's
// (left) side and above - the way he looks at the dash.
const VIEW_FROM_CAR = new THREE.Vector3(-0.45, -1, 0.65);
const FADE = 0.1;
// A link's label sits this far out from the modelled part it leaves (mm).
const LABEL_REACH = 160;
// With nothing isolated, link, node and housing labels show only nearer the camera than
// this share of the distance the modelled parts were framed from - zoom in and they appear.
const LABEL_NEAR = 0.85;

interface Loaded {
  group: THREE.Group; // the part's frame
  model?: THREE.Object3D; // the model (or its stand-in) inside it; a node has none
}

/** A label the declutter decides on: its kind sets when it may show and how much it matters. */
interface Tag {
  obj: CSS2DObject;
  kind: 'part' | 'node' | 'link' | 'conn' | 'housing' | 'leg';
  id: string;
  w: number;
  h: number;
  cy: number; // where it hangs from its point (CSS2DObject.center.y) before any shift
}

export class DesignView {
  private renderer: THREE.WebGLRenderer;
  private labels = new CSS2DRenderer();
  private scene = new THREE.Scene();
  private root = new THREE.Group();
  private linkLayer = new THREE.Group();
  private legLayer = new THREE.Group();
  private camera = new THREE.PerspectiveCamera(FOV, 1, 1, 100000);
  private controls: OrbitControls;
  private observer: ResizeObserver;
  private parts = new Map<string, Loaded>();
  private linkObjs = new Map<string, { line: THREE.Line; label: CSS2DObject; dots: CSS2DObject[] }>();
  private legObjs = new Map<string, THREE.Mesh[]>();
  private tags: Tag[] = [];
  private glbs = new Map<string, Promise<THREE.Object3D>>(); // one load per file, cloned per part
  private sel: Selection = null;
  private focus: Focus | null = null;
  private focusEnds = new Set<string>(); // the drawn parts at the ends of the isolated links
  private nearDist = Infinity;
  private toggles: Toggles;
  private frame = 0;
  private dead = false;
  private moved = false;
  private down: { x: number; y: number } | null = null;
  private fitDir = VIEW_FROM_CAR.clone().applyMatrix4(CAR_TO_THREE);

  /** Throws when the device has no WebGL; the page says so and keeps its lists. */
  constructor(
    private host: HTMLElement,
    private s: Scene,
    private base: string,
    private mode: Mode,
    private hooks: ViewerHooks,
  ) {
    this.toggles = defaultToggles(s);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.AgXToneMapping;
    host.appendChild(this.renderer.domElement);
    this.labels.domElement.className = 'd3-labels';
    host.appendChild(this.labels.domElement);

    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    this.scene.add(new THREE.HemisphereLight(0xe0fbfc, 0x293241, 0.6));
    this.root.matrixAutoUpdate = false;
    this.root.matrix.copy(CAR_TO_THREE);
    this.root.add(this.linkLayer, this.legLayer);
    this.scene.add(this.root);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.screenSpacePanning = true;
    this.controls.addEventListener('change', () => this.request());

    const el = this.renderer.domElement;
    el.addEventListener('pointerdown', this.onDown);
    el.addEventListener('pointerup', this.onUp);

    this.observer = new ResizeObserver(() => this.resize());
    this.observer.observe(host);
    this.resize();
    this.build();
  }

  // ---------------------------------------------------------------- building

  private build() {
    const m = this.mode;
    if (m.kind === 'assembly') {
      // the top-level parts at their places, and every connector at its own, a unit's
      // receptacles included (drawn beside it, not inside it, so they fade and pick alone)
      for (const id of drawnIds(this.s)) {
        const p = partById(this.s, id)!;
        this.addPart(p, this.root, p.parent ? worldMatrix(this.s, id) : placeMatrix(p.place));
      }
      this.drawLegs();
      this.drawLinks();
    } else {
      const p = partById(this.s, m.id);
      if (!p) return;
      // The part alone at the origin, its children placed in its frame.
      this.addPart(p, this.root, new THREE.Matrix4());
      const under = (c: Part) => {
        if (this.parts.has(c.id)) return;
        this.addPart(c, this.root, matrixUnder(this.s, c.id, p.id));
        childrenOf(this.s, c.id).forEach(under);
      };
      childrenOf(this.s, p.id).forEach(under);
      this.drawConnectors(p);
      if (m.kind === 'board') this.fitDir = new THREE.Vector3(0, 1, 0.0001);
    }
    this.fit();
  }

  private addPart(p: Part, parent: THREE.Object3D, matrix: THREE.Matrix4) {
    const group = new THREE.Group();
    group.name = `part:${p.id}`;
    group.userData.partId = p.id;
    group.matrixAutoUpdate = false;
    group.matrix.copy(matrix);
    parent.add(group);
    const entry: Loaded = { group };
    this.parts.set(p.id, entry);
    if (p.kind === 'node') {
      // A far end: a dot (tap it to isolate it) and its name, which the declutter rations.
      group.add(this.dot('d3-nodedot', () => this.hooks.pick({ kind: 'part', id: p.id })));
      const label = this.label(p.name, 'd3-node');
      label.center.set(0.5, 1.4);
      group.add(label);
      this.tag(label, 'node', p.id);
      this.hooks.status(p.id, { state: 'none' });
      return;
    }
    if (this.mode.kind === 'assembly') {
      const conn = isConnector(p);
      const label = conn
        ? this.label(p.housing || p.id, 'd3-housing', () => this.hooks.pick(p.housing ? { kind: 'housing', id: p.housing } : { kind: 'part', id: p.id }))
        : this.label(p.name, 'd3-part');
      label.center.set(0.5, conn ? 1.5 : 1.2);
      group.add(label);
      this.tag(label, conn ? 'housing' : 'part', p.id);
    }
    if (!p.glb) {
      this.setModel(p, entry, this.standIn(p));
      this.hooks.status(p.id, { state: 'none' });
      return;
    }
    this.hooks.status(p.id, { state: 'loading' });
    this.model(p.glb)
      .then((model) => {
        if (this.dead) return dispose(model);
        const holder = new THREE.Group();
        holder.matrixAutoUpdate = false;
        // The scene says how its models are written (frame.glb); a guess from the size only
        // when it does not.
        const reading = frameGlb(this.s.frame.glb) ?? glbReading(new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3()), p.size_mm);
        holder.matrix.copy(glbMatrix(reading));
        holder.add(model);
        model.traverse((o) => {
          if ((o as THREE.Mesh).isMesh) o.userData.partId = p.id;
        });
        this.setModel(p, entry, holder);
        if (this.mode.kind !== 'assembly' && this.mode.id === p.id) {
          this.hooks.nodes({ case: this.named(holder, p.nodes.case).length > 0, inside: this.named(holder, p.nodes.inside).length > 0 });
        }
        this.hooks.status(p.id, { state: 'ready' });
        this.afterLoad();
      })
      .catch((e: unknown) => {
        if (this.dead) return;
        // Name it and keep the rest: a wire box of the part's size stands in, so its links
        // still land somewhere.
        this.setModel(p, entry, this.standIn(p));
        this.hooks.status(p.id, { state: 'failed', why: reason(e) });
        this.afterLoad();
      });
  }

  /** A model file, loaded once however many parts use it (every DT06-12S half is one file),
   *  and handed out as a copy with its own materials, so one can fade without the others. */
  private async model(glb: string): Promise<THREE.Object3D> {
    const url = new URL(glb, new URL(this.base, location.href)).href;
    let first = this.glbs.get(url);
    if (!first) {
      first = new GLTFLoader().loadAsync(url).then((g) => g.scene);
      this.glbs.set(url, first);
    }
    const copy = (await first).clone(true);
    copy.traverse((o) => {
      const mesh = o as THREE.Mesh;
      if (mesh.isMesh) mesh.material = Array.isArray(mesh.material) ? mesh.material.map((m) => m.clone()) : mesh.material.clone();
    });
    return copy;
  }

  /** Put a model in its part's frame, and its name label on top of it. */
  private setModel(p: Part, entry: Loaded, model: THREE.Object3D) {
    entry.model = model;
    entry.group.add(model);
    this.root.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(model);
    const label = this.tags.find((t) => (t.kind === 'part' || t.kind === 'housing') && t.id === p.id)?.obj;
    if (label && !box.isEmpty()) {
      const top = box.getCenter(new THREE.Vector3());
      top.y = box.max.y; // three.js y is the car's up
      label.position.copy(entry.group.worldToLocal(top));
    }
    this.applyFocus();
  }

  private afterLoad() {
    this.drawLinks();
    // refit while models arrive, until he moves the camera himself
    if (!this.moved) this.fit();
    this.request();
  }

  private standIn(p: Part): THREE.Object3D {
    const s = p.size_mm && Math.max(p.size_mm.x, p.size_mm.y, p.size_mm.z) > 0 ? p.size_mm : { x: 40, y: 40, z: 40 };
    const geo = new THREE.BoxGeometry(Math.max(s.x, 1), Math.max(s.y, 1), Math.max(s.z, 1));
    const box = new THREE.Mesh(
      geo,
      new THREE.MeshBasicMaterial({ color: 0xee6c4d, transparent: true, opacity: 0.08, depthWrite: false }),
    );
    box.userData.partId = p.id;
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: 0xee6c4d }));
    box.add(edges);
    return box;
  }

  private label(text: string, cls: string, onTap?: () => void): CSS2DObject {
    const el = document.createElement(onTap ? 'button' : 'div');
    el.className = `d3-label ${cls}`;
    el.textContent = text;
    if (onTap) {
      el.setAttribute('type', 'button');
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        onTap();
      });
    }
    return new CSS2DObject(el);
  }

  private dot(cls = '', onTap?: () => void): CSS2DObject {
    const d = this.label('', `d3-dot ${cls}`, onTap);
    if (onTap) d.element.setAttribute('aria-hidden', 'true');
    return d;
  }

  private tag(obj: CSS2DObject, kind: Tag['kind'], id: string) {
    obj.userData.tag = true;
    const text = obj.element.textContent ?? '';
    // a label's size, estimated (measuring every frame would cost a layout each time)
    this.tags.push({ obj, kind, id, w: text.length * 7.4 + 18, h: kind === 'link' || kind === 'leg' ? 28 : 22, cy: obj.center.y });
  }

  /** The car-frame centres of the models loaded so far, for links whose connector is not in
   *  the scene. */
  private centres(): Map<string, THREE.Vector3> {
    const out = new Map<string, THREE.Vector3>();
    this.root.updateMatrixWorld(true);
    const toCar = this.root.matrixWorld.clone().invert();
    for (const [id, e] of this.parts) {
      if (!e.model) continue;
      const box = new THREE.Box3().setFromObject(e.model);
      if (!box.isEmpty()) out.set(id, box.getCenter(new THREE.Vector3()).applyMatrix4(toCar));
    }
    return out;
  }

  /** The legs (version 2): each run a tube along its path in the leg's colour, and the leg's
   *  name near its root. Its route, not a measurement (R11): every point is provisional. */
  private drawLegs() {
    for (const leg of this.s.legs) {
      const paths = legPaths(leg);
      if (!paths.length) continue;
      const colour = legColour(this.s, leg.id);
      const meshes = paths.map((path) => {
        const pts = path.map((q) => new THREE.Vector3(q.x, q.y, q.z));
        const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
        const geo = new THREE.TubeGeometry(curve, Math.max(8, pts.length * 12), legRadius(leg), 8, false);
        const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: colour, roughness: 0.55, metalness: 0.05 }));
        mesh.userData.legId = leg.id;
        this.legLayer.add(mesh);
        return mesh;
      });
      this.legObjs.set(leg.id, meshes);
      const label = this.label(leg.name, 'd3-leg', () => this.hooks.pick({ kind: 'leg', id: leg.id }));
      label.element.style.setProperty('--leg', `#${colour.toString(16).padStart(6, '0')}`);
      label.center.set(0.5, 1.3);
      const at = legLabelAt(leg) ?? paths[0][0];
      label.position.set(at.x, at.y, at.z);
      this.legLayer.add(label);
      this.tag(label, 'leg', leg.id);
    }
  }

  /** The harness as straight labelled lines, connector to connector (no route, no length). */
  private drawLinks() {
    if (this.mode.kind !== 'assembly') return;
    const centres = this.centres();
    for (const l of this.s.links) {
      const ends = linkEnds(this.s, l, centres);
      if (!ends) continue;
      let o = this.linkObjs.get(l.id);
      if (!o) {
        const line = new THREE.Line(
          new THREE.BufferGeometry(),
          new THREE.LineBasicMaterial({ color: l.confirm ? 0xee6c4d : 0x98c1d9, depthTest: false, transparent: true, opacity: 0.75 }),
        );
        line.renderOrder = 10;
        const label = this.label(l.code, 'd3-link', () => this.hooks.pick({ kind: 'link', id: l.id }));
        this.tag(label, 'link', l.id);
        const dots = [this.dot(), this.dot()];
        this.linkLayer.add(line, label, ...dots);
        o = { line, label, dots };
        this.linkObjs.set(l.id, o);
      }
      o.line.geometry.setFromPoints([ends.from.at, ends.to.at]);
      o.line.geometry.computeBoundingSphere();
      const fromM = modelled(partById(this.s, drawnId(this.s, l.from.part)));
      const toM = modelled(partById(this.s, drawnId(this.s, l.to.part)));
      o.label.position.copy(ends.from.at).lerp(ends.to.at, labelT(ends.from.at.distanceTo(ends.to.at), fromM, toM, LABEL_REACH));
      o.dots[0].position.copy(ends.from.at);
      o.dots[1].position.copy(ends.to.at);
      o.dots[0].element.classList.toggle('approx', !ends.from.exact);
      o.dots[1].element.classList.toggle('approx', !ends.to.exact);
    }
    this.applyFocus();
  }

  /** The part view's and board view's connectors: a dot and its code at each. */
  private drawConnectors(p: Part) {
    const codes = new Set<string>();
    for (const id of family(this.s, p.id)) {
      for (const c of partById(this.s, id)?.connectors ?? []) {
        if (codes.has(c.code)) continue;
        const hit = findConnector(this.s, id, c.code);
        if (!hit) continue;
        codes.add(c.code);
        const at = new THREE.Vector3(hit.c.at!.x, hit.c.at!.y, hit.c.at!.z).applyMatrix4(matrixUnder(this.s, hit.part.id, p.id));
        const dot = this.dot();
        const label = this.label(c.code, 'd3-conn');
        label.center.set(0.5, 1.5);
        dot.position.copy(at);
        label.position.copy(at);
        dot.userData.ownerId = hit.part.id;
        this.tag(label, 'conn', hit.part.id);
        this.linkLayer.add(dot, label);
      }
    }
  }

  private named(model: THREE.Object3D, names: string[]): THREE.Object3D[] {
    const out: THREE.Object3D[] = [];
    if (!names.length) return out;
    model.traverse((o) => {
      if (names.some((n) => nodeMatches(o.name, o.userData.name as string | undefined, n))) out.push(o);
    });
    return out;
  }

  // ---------------------------------------------------------------- what is shown

  /** The assembly: fade everything outside the isolated part, link, housing or leg, and
   *  frame it. */
  setSelection(sel: Selection) {
    this.sel = sel;
    this.focus = focusOf(this.s, sel);
    this.focusEnds = new Set();
    for (const l of this.s.links) {
      if (!this.focus?.links.has(l.id)) continue;
      this.focusEnds.add(drawnId(this.s, l.from.part));
      this.focusEnds.add(drawnId(this.s, l.to.part));
    }
    this.applyFocus();
    this.moved = false;
    this.fit();
  }

  /** The assembly's layers: legs, links, connectors, labels. */
  setToggles(t: Toggles) {
    this.toggles = { ...t };
    this.applyFocus();
  }

  private faded(id: string): boolean {
    return !!this.focus && this.mode.kind === 'assembly' && !this.focus.parts.has(id);
  }

  private fade(o: THREE.Object3D, faded: boolean) {
    o.traverse((x) => {
      const mesh = x as THREE.Mesh;
      if (!mesh.isMesh && !(x as THREE.LineSegments).isLineSegments) return;
      for (const m of ([] as THREE.Material[]).concat((mesh.material as THREE.Material | THREE.Material[]) ?? [])) {
        if (m.userData.base === undefined) m.userData.base = { opacity: m.opacity, transparent: m.transparent, depthWrite: m.depthWrite };
        const b = m.userData.base as { opacity: number; transparent: boolean; depthWrite: boolean };
        m.opacity = faded ? Math.min(b.opacity, FADE) : b.opacity;
        m.transparent = faded || b.transparent;
        m.depthWrite = faded ? false : b.depthWrite;
        m.needsUpdate = true;
      }
    });
  }

  /** Materials, lines, dots and what each toggle hides; the labels are the declutter's, on
   *  every frame. */
  private applyFocus() {
    const f = this.focus;
    const t = this.toggles;
    const asm = this.mode.kind === 'assembly';
    for (const [id, e] of this.parts) {
      const faded = this.faded(id);
      if (asm && isConnector(partById(this.s, id))) e.group.visible = connectorShown(t, f, id);
      e.group.traverse((o) => {
        if (o instanceof CSS2DObject && !o.userData.tag) o.visible = !faded;
      });
      if (e.model) this.fade(e.model, faded);
    }
    for (const [id, meshes] of this.legObjs) {
      const on = legShown(t, f, id);
      const faded = !!f && !f.legs.has(id);
      for (const m of meshes) {
        m.visible = on;
        this.fade(m, faded);
      }
    }
    for (const [id, o] of this.linkObjs) {
      const on = linkShown(t, f, id);
      o.line.visible = on;
      o.dots.forEach((d) => (d.visible = on));
      o.label.element.classList.toggle('on', !!f && f.links.has(id));
    }
    if (!asm) {
      this.linkLayer.traverse((o) => {
        if (!(o instanceof CSS2DObject) || o.userData.tag) return;
        const owner = o.userData.ownerId as string | undefined;
        o.visible = owner ? !!this.parts.get(owner)?.group.visible : true;
      });
    }
    this.request();
  }

  /** Which labels show this frame. A part's name and a leg's always (unless faded or
   *  hidden); with something isolated, only its links', housings' and far ends'; with
   *  nothing isolated, the link, housing and node labels near the camera. Then the most
   *  important first, nearest first, each only where it overlaps none already shown. */
  private declutterLabels() {
    const f = this.focus;
    const t = this.toggles;
    const { clientWidth: w, clientHeight: h } = this.host;
    const camPos = this.camera.position;
    const cands: { t: Tag; rank: number; d: number; x: number; y: number }[] = [];
    const v = new THREE.Vector3();
    for (const tg of this.tags) {
      let want = false;
      let rank = 2;
      let nearOnly = false;
      if (t.labels) {
        switch (tg.kind) {
          case 'part':
            want = !this.faded(tg.id);
            rank = 0;
            break;
          case 'leg':
            want = legShown(t, f, tg.id) && (!f || f.legs.has(tg.id));
            rank = 0;
            break;
          case 'conn':
            want = !!this.parts.get(tg.id)?.group.visible;
            break;
          case 'link':
            want = f ? f.links.has(tg.id) : t.links;
            nearOnly = !f;
            rank = 1;
            break;
          case 'housing':
            want = !!this.parts.get(tg.id)?.group.visible && (!f || f.parts.has(tg.id));
            nearOnly = !f;
            rank = 1;
            break;
          case 'node':
            want = f ? this.focusEnds.has(tg.id) || f.parts.has(tg.id) : true;
            nearOnly = !f;
            rank = 1;
            break;
        }
      }
      if (want) {
        tg.obj.getWorldPosition(v);
        const d = v.distanceTo(camPos);
        if (nearOnly && d > this.nearDist) want = false;
        else {
          const p = v.clone().project(this.camera);
          if (p.z > 1 || p.z < -1) want = false;
          else cands.push({ t: tg, rank, d, x: ((p.x + 1) / 2) * w, y: ((1 - p.y) / 2) * h - tg.h * (tg.cy - 0.5) });
        }
      }
      if (!want) tg.obj.visible = false;
    }
    cands.sort((a, b) => a.rank - b.rank || a.d - b.d);
    // a part's name may drop below its anchor, onto the model, when above it is taken, and
    // a part's or leg's name slides in from the edge rather than vanish
    const keep = declutter(
      cands.map((c) => ({ x: c.x, y: c.y, w: c.t.w, h: c.t.h, alts: c.t.kind === 'part' ? [c.t.h * 1.6, -c.t.h * 1.2] : [], slide: c.t.kind === 'part' || c.t.kind === 'leg' })),
      w,
      h,
    );
    cands.forEach((c, i) => {
      const k = keep[i];
      c.t.obj.visible = k !== null;
      c.t.obj.center.set(0.5 - (k?.dx ?? 0) / c.t.w, c.t.cy - (k?.dy ?? 0) / c.t.h);
    });
  }

  /** The part view's toggles: 'case' and 'inside' are the model's named node groups,
   *  'connectors' every connector inside the part, any other key a child part. */
  setHidden(hidden: Set<string>) {
    if (this.mode.kind === 'assembly') return;
    const p = partById(this.s, this.mode.id);
    const own = p && this.parts.get(p.id)?.model;
    if (p && own) {
      for (const o of this.named(own, p.nodes.case)) o.visible = !hidden.has('case');
      for (const o of this.named(own, p.nodes.inside)) o.visible = !hidden.has('inside');
    }
    for (const [id, e] of this.parts) {
      if (id === p?.id) continue;
      const conn = isConnector(partById(this.s, id));
      e.group.visible = !hidden.has(id) && !this.hiddenAbove(id, hidden) && !(conn && hidden.has('connectors'));
    }
    this.applyFocus();
  }

  private hiddenAbove(id: string, hidden: Set<string>): boolean {
    for (let q = partById(this.s, id); q?.parent; q = partById(this.s, q.parent)) if (hidden.has(q.parent)) return true;
    return false;
  }

  /** The board view: look at its top (+z of the board) or its bottom. */
  setSide(side: 'top' | 'bottom') {
    this.fitDir = new THREE.Vector3(0, side === 'top' ? 1 : -1, 0.0001);
    this.moved = false;
    this.fit();
  }

  /** Frame, from the current direction: in the assembly what design.ts's fitSet says (the
   *  modelled parts, or the isolated part's own box, a link's two ends, a housing's halves, a
   *  leg's runs; `all` adds every far end and leg); in a part or board view, what is shown. */
  fit(all = false) {
    this.root.updateMatrixWorld(true);
    const pts: THREE.Vector3[] = [];
    const set = this.mode.kind === 'assembly' ? fitSet(this.s, this.sel, all) : null;
    for (const [id, e] of this.parts) {
      if ((set && !set.parts.has(id)) || !e.group.visible) continue;
      if (e.model) pts.push(...corners(new THREE.Box3().setFromObject(e.model)));
      else pts.push(e.group.getWorldPosition(new THREE.Vector3()));
    }
    for (const id of set?.links ?? []) {
      this.linkObjs.get(id)?.dots.forEach((d) => pts.push(d.getWorldPosition(new THREE.Vector3())));
    }
    for (const id of set?.legs ?? []) {
      const leg = this.s.legs.find((l) => l.id === id);
      for (const path of leg ? legPaths(leg) : []) for (const q of path) pts.push(new THREE.Vector3(q.x, q.y, q.z).applyMatrix4(this.root.matrixWorld));
    }
    const v = fitView(pts, this.fitDir, FOV, this.camera.aspect, 120);
    this.controls.target.copy(v.target);
    this.camera.position.copy(v.position);
    // near enough to label: a share of the distance the modelled parts are framed from
    if (set && !this.sel && !all) this.nearDist = v.position.distanceTo(v.target) * LABEL_NEAR;
    // the far ends stay in the clip range from any fit
    this.camera.near = Math.max(v.near / 4, 0.5);
    this.camera.far = v.far + 20000;
    this.camera.updateProjectionMatrix();
    this.controls.minDistance = 20;
    this.controls.maxDistance = Math.max(v.far / 2, 12000);
    this.controls.update();
    this.request();
  }

  // ---------------------------------------------------------------- input and drawing

  private onDown = (e: PointerEvent) => {
    this.down = { x: e.clientX, y: e.clientY };
  };

  /** A tap (not a drag) picks what is under it: a part, a connector (its housing) or a leg's
   *  tube. Empty space does nothing, so a slip while turning the view never loses what is
   *  isolated. Nothing is ever dragged or moved. */
  private onUp = (e: PointerEvent) => {
    const d = this.down;
    this.down = null;
    if (!d) return;
    if (Math.hypot(e.clientX - d.x, e.clientY - d.y) > 6) {
      this.moved = true;
      return;
    }
    if (this.mode.kind !== 'assembly') return;
    const r = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    const ray = new THREE.Raycaster();
    ray.setFromCamera(ndc, this.camera);
    const targets = [...[...this.parts.values()].map((p) => p.group), this.legLayer];
    for (const hit of ray.intersectObjects(targets, true)) {
      if (!(hit.object as THREE.Mesh).isMesh || !visibleUp(hit.object)) continue;
      if (hit.object.userData.legId) {
        this.hooks.pick({ kind: 'leg', id: hit.object.userData.legId as string });
        return;
      }
      let o: THREE.Object3D | null = hit.object;
      while (o && !o.userData.partId) o = o.parent;
      if (o) {
        const p = partById(this.s, o.userData.partId as string);
        this.hooks.pick(p && isConnector(p) && p.housing ? { kind: 'housing', id: p.housing } : { kind: 'part', id: o.userData.partId as string });
        return;
      }
    }
  };

  private resize() {
    const { clientWidth: w, clientHeight: h } = this.host;
    this.renderer.setSize(w, h, false);
    this.labels.setSize(w, h);
    this.camera.aspect = w / Math.max(h, 1);
    this.camera.updateProjectionMatrix();
    this.request();
  }

  /** Drawn on demand, not every frame: a phone's battery is spent only while it moves. */
  private request() {
    if (this.frame || this.dead) return;
    this.frame = requestAnimationFrame(() => {
      this.frame = 0;
      if (this.dead) return;
      const moving = this.controls.update();
      this.renderer.render(this.scene, this.camera);
      this.declutterLabels();
      this.labels.render(this.scene, this.camera);
      if (moving) this.request();
    });
  }

  /** Everything on the GPU and in the DOM goes when the page does (CarModel's pattern, plus
   *  the geometries, materials and textures of every model, and the context itself). */
  dispose() {
    this.dead = true;
    cancelAnimationFrame(this.frame);
    this.observer.disconnect();
    this.controls.dispose();
    const el = this.renderer.domElement;
    el.removeEventListener('pointerdown', this.onDown);
    el.removeEventListener('pointerup', this.onUp);
    dispose(this.scene);
    for (const first of this.glbs.values()) void first.then(dispose, () => undefined);
    this.scene.environment?.dispose();
    this.renderer.dispose();
    this.renderer.forceContextLoss();
    el.remove();
    this.labels.domElement.remove();
  }
}

/** Visible, and every parent visible (a hidden connector's meshes are not pickable). */
function visibleUp(o: THREE.Object3D | null): boolean {
  for (; o; o = o.parent) if (!o.visible) return false;
  return true;
}

function dispose(root: THREE.Object3D) {
  root.traverse((o) => {
    const mesh = o as THREE.Mesh;
    mesh.geometry?.dispose();
    for (const m of ([] as THREE.Material[]).concat((mesh.material as THREE.Material | THREE.Material[]) ?? [])) {
      for (const v of Object.values(m)) if ((v as THREE.Texture)?.isTexture) (v as THREE.Texture).dispose();
      m.dispose();
    }
    if (o instanceof CSS2DObject) o.element.remove();
  });
}

function reason(e: unknown): string {
  const m = e instanceof Error ? e.message : String(e);
  if (/404|not found/i.test(m)) return 'the file is not there';
  if (/Unexpected token|JSON|magic|glTF/i.test(m)) return 'the file is not a model';
  return m.slice(0, 120) || 'it did not load';
}
