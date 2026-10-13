/**
 * The Design page's drawing (D-505, M3D1): one three.js view of a scene - the assembly, one
 * part with its children, or one board - over a canvas, with the labels as DOM elements
 * (CSS2DRenderer: plain HTML, so they read the same in Android's WebView as on the desktop).
 * Everything placed is built in the car frame under one root (design.ts's CAR_TO_THREE).
 * Imported only on demand, like CarModel's three.js, so the page's lists never wait on it.
 * It reads public/design/<project>/scene.json's models and no table.
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import { CAR_TO_THREE, fitView, glbMatrix, linkEnds, matrixUnder, placeMatrix } from './designMath';
import {
  childrenOf,
  family,
  findConnector,
  focusOf,
  glbReading,
  nodeMatches,
  partById,
  topLevel,
  type Part,
  type Scene,
  type Selection,
} from './design';

export type Mode = { kind: 'assembly' } | { kind: 'part'; id: string } | { kind: 'board'; id: string };
export type LoadState = { state: 'loading' | 'ready' | 'none' } | { state: 'failed'; why: string };

export interface ViewerHooks {
  /** a part tapped in the 3D (its top-level id in the assembly), or a link label tapped */
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

interface Loaded {
  group: THREE.Group; // the part's frame
  model?: THREE.Object3D; // the model (or its stand-in) inside it
}

export class DesignView {
  private renderer: THREE.WebGLRenderer;
  private labels = new CSS2DRenderer();
  private scene = new THREE.Scene();
  private root = new THREE.Group();
  private linkLayer = new THREE.Group();
  private camera = new THREE.PerspectiveCamera(FOV, 1, 1, 100000);
  private controls: OrbitControls;
  private observer: ResizeObserver;
  private parts = new Map<string, Loaded>();
  private linkObjs = new Map<string, { line: THREE.Line; label: CSS2DObject; dots: CSS2DObject[] }>();
  private focus: ReturnType<typeof focusOf> = null;
  private showLabels = true;
  private frame = 0;
  private dead = false;
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
    this.root.add(this.linkLayer);
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
      for (const p of topLevel(this.s)) this.addPart(p, this.root, placeMatrix(p.place));
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
    if (p.kind === 'node' || !p.glb) {
      entry.model = this.marker(p);
      group.add(entry.model);
      this.hooks.status(p.id, { state: 'none' });
      return;
    }
    this.hooks.status(p.id, { state: 'loading' });
    const url = new URL(p.glb, new URL(this.base, location.href)).href;
    new GLTFLoader()
      .loadAsync(url)
      .then((gltf) => {
        if (this.dead) return dispose(gltf.scene);
        const model = gltf.scene;
        const ext = new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3());
        const holder = new THREE.Group();
        holder.matrixAutoUpdate = false;
        holder.matrix.copy(glbMatrix(glbReading(ext, p.size_mm)));
        holder.add(model);
        model.traverse((o) => {
          const mesh = o as THREE.Mesh;
          if (mesh.isMesh) mesh.userData.partId = p.id;
        });
        entry.model = holder;
        group.add(holder);
        this.applyFocus();
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
        entry.model = this.standIn(p);
        group.add(entry.model);
        this.applyFocus();
        this.hooks.status(p.id, { state: 'failed', why: reason(e) });
        this.afterLoad();
      });
  }

  private afterLoad() {
    this.drawLinks();
    // refit while models arrive, until he moves the camera himself
    if (!this.moved) this.fit();
    this.request();
  }
  private moved = false;

  /** A place without a model (a node), or a part with none exported. */
  private marker(p: Part): THREE.Object3D {
    const size = p.size_mm ? Math.max(p.size_mm.x, p.size_mm.y, p.size_mm.z) : 0;
    if (size > 0) return this.standIn(p);
    const g = new THREE.Mesh(
      new THREE.OctahedronGeometry(12),
      new THREE.MeshStandardMaterial({ color: 0x98c1d9, roughness: 0.5, metalness: 0.1 }),
    );
    g.userData.partId = p.id;
    const label = this.label(p.name, 'd3-node');
    label.center.set(0.5, 1.6);
    g.add(label);
    return g;
  }

  private standIn(p: Part): THREE.Object3D {
    const s = p.size_mm ?? { x: 40, y: 40, z: 40 };
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
          new THREE.LineBasicMaterial({ color: l.confirm ? 0xee6c4d : 0x98c1d9, depthTest: false, transparent: true }),
        );
        line.renderOrder = 10;
        const label = this.label(l.code, 'd3-link', () => this.hooks.pick({ kind: 'link', id: l.id }));
        const dots = [this.label('', 'd3-dot'), this.label('', 'd3-dot')];
        this.linkLayer.add(line, label, ...dots);
        o = { line, label, dots };
        this.linkObjs.set(l.id, o);
      }
      o.line.geometry.setFromPoints([ends.from.at, ends.to.at]);
      o.line.geometry.computeBoundingSphere();
      o.label.position.copy(ends.from.at).lerp(ends.to.at, 0.5);
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
        const dot = this.label('', 'd3-dot');
        const label = this.label(c.code, 'd3-conn');
        label.center.set(0.5, 1.5);
        dot.position.copy(at);
        label.position.copy(at);
        dot.userData.ownerId = label.userData.ownerId = hit.part.id;
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

  /** The assembly: fade everything outside the isolated part or link, and frame it. */
  setSelection(sel: Selection) {
    this.focus = focusOf(this.s, sel);
    this.applyFocus();
    this.moved = false;
    this.fit();
  }

  private applyFocus() {
    const f = this.focus;
    for (const [id, e] of this.parts) {
      const faded = !!f && this.mode.kind === 'assembly' && !f.parts.has(id);
      e.group.traverse((o) => {
        const mesh = o as THREE.Mesh;
        if (!mesh.isMesh && !(o as THREE.LineSegments).isLineSegments) return;
        for (const m of ([] as THREE.Material[]).concat((mesh.material as THREE.Material | THREE.Material[]) ?? [])) {
          if (m.userData.base === undefined) m.userData.base = { opacity: m.opacity, transparent: m.transparent, depthWrite: m.depthWrite };
          const b = m.userData.base as { opacity: number; transparent: boolean; depthWrite: boolean };
          m.opacity = faded ? Math.min(b.opacity, FADE) : b.opacity;
          m.transparent = faded || b.transparent;
          m.depthWrite = faded ? false : b.depthWrite;
          m.needsUpdate = true;
        }
      });
      e.group.traverse((o) => {
        if (o instanceof CSS2DObject) o.visible = !faded && this.showLabels;
      });
    }
    for (const [id, o] of this.linkObjs) {
      const on = !f || f.links.has(id);
      o.line.visible = on;
      o.label.visible = on && this.showLabels;
      o.dots.forEach((d) => (d.visible = on));
      o.label.element.classList.toggle('on', !!f && f.links.has(id));
    }
    if (this.mode.kind !== 'assembly') {
      this.linkLayer.traverse((o) => {
        if (!(o instanceof CSS2DObject)) return;
        const owner = o.userData.ownerId as string | undefined;
        const hidden = owner ? !this.parts.get(owner)?.group.visible : false;
        o.visible = !hidden && (this.showLabels || (o as CSS2DObject).element.classList.contains('d3-dot'));
      });
    }
    this.request();
  }

  setLabels(on: boolean) {
    this.showLabels = on;
    this.applyFocus();
  }

  /** The part view's toggles: 'case' and 'inside' are the model's named node groups, any
   *  other key a child part. */
  setHidden(hidden: Set<string>) {
    if (this.mode.kind === 'assembly') return;
    const p = partById(this.s, this.mode.id);
    const own = p && this.parts.get(p.id)?.model;
    if (p && own) {
      for (const o of this.named(own, p.nodes.case)) o.visible = !hidden.has('case');
      for (const o of this.named(own, p.nodes.inside)) o.visible = !hidden.has('inside');
    }
    for (const [id, e] of this.parts) if (id !== p?.id) e.group.visible = !hidden.has(id) && !this.hiddenAbove(id, hidden);
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

  /** Frame what is in focus (or everything) from the current direction. */
  fit() {
    this.root.updateMatrixWorld(true);
    const box = new THREE.Box3();
    for (const [id, e] of this.parts) {
      if (this.focus && this.mode.kind === 'assembly' && !this.focus.parts.has(id)) continue;
      if (e.model && e.group.visible) box.expandByObject(e.model);
    }
    if (this.mode.kind === 'assembly') {
      for (const [id, o] of this.linkObjs) {
        if (this.focus && !this.focus.links.has(id)) continue;
        o.dots.forEach((d) => box.expandByPoint(d.getWorldPosition(new THREE.Vector3())));
      }
    }
    const v = fitView(box, this.fitDir, FOV, this.camera.aspect);
    this.controls.target.copy(v.target);
    this.camera.position.copy(v.position);
    this.camera.near = v.near;
    this.camera.far = v.far;
    this.camera.updateProjectionMatrix();
    this.controls.minDistance = v.near * 2;
    this.controls.maxDistance = v.far / 2;
    this.controls.update();
    this.request();
  }

  // ---------------------------------------------------------------- input and drawing

  private onDown = (e: PointerEvent) => {
    this.down = { x: e.clientX, y: e.clientY };
  };

  /** A tap (not a drag) picks the part under it. Empty space does nothing, so a slip while
   *  turning the view never loses what is isolated. */
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
    const targets = [...this.parts.values()].map((p) => p.group);
    for (const hit of ray.intersectObjects(targets, true)) {
      if (!(hit.object as THREE.Mesh).isMesh || !hit.object.visible) continue;
      let o: THREE.Object3D | null = hit.object;
      while (o && !o.userData.partId) o = o.parent;
      if (o) {
        this.hooks.pick({ kind: 'part', id: o.userData.partId as string });
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
    this.scene.environment?.dispose();
    this.renderer.dispose();
    this.renderer.forceContextLoss();
    el.remove();
    this.labels.domElement.remove();
  }
}

function dispose(root: THREE.Object3D) {
  root.traverse((o) => {
    const mesh = o as THREE.Mesh;
    mesh.geometry?.dispose();
    for (const m of ([] as THREE.Material[]).concat((mesh.material as THREE.Material | THREE.Material[]) ?? [])) {
      for (const v of Object.values(m)) if ((v as THREE.Texture)?.isTexture) (v as THREE.Texture).dispose();
      m.dispose();
    }
    if (o instanceof CSS2DObject) (o as CSS2DObject).element.remove();
  });
}

function reason(e: unknown): string {
  const m = e instanceof Error ? e.message : String(e);
  if (/404|not found/i.test(m)) return 'the file is not there';
  if (/Unexpected token|JSON|magic|glTF/i.test(m)) return 'the file is not a model';
  return m.slice(0, 120) || 'it did not load';
}
