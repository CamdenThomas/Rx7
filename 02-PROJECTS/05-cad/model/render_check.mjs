// render_check.mjs - does the car's scene load in three.js, and what does it look like? (05-cad A04)
//
//   node 02-PROJECTS/05-cad/model/render_check.mjs [OUT_DIR]
//
// Loads 02-APP/app/public/design/00-CAR/scene.json and every glb it names with the app's own
// three.js (02-APP/app/node_modules/three, GLTFLoader), hangs each under its parent at its place
// (mm, three.js Euler XYZ in degrees), prints the assembled box, and rasterises four orthographic
// views (side, top, front, three-quarter) and an exploded side view (each part moved by its
// mate.apart, chained) into PNG files in OUT_DIR (default: the system temp dir) - a software
// z-buffer, no WebGL. Exit 0 loaded; 1 a glb failed to load; 3 a crash.
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import zlib from "node:zlib";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..", "..");
const APP = path.join(ROOT, "02-APP", "app");
const THREE = await import(pathToFileURL(path.join(APP, "node_modules", "three", "build", "three.module.js")).href);
const { GLTFLoader } = await import(pathToFileURL(path.join(APP, "node_modules", "three", "examples", "jsm", "loaders", "GLTFLoader.js")).href);
const DIR = path.join(APP, "public", "design", "00-CAR");
const OUT = process.argv[2] || os.tmpdir();
const scene = JSON.parse(fs.readFileSync(path.join(DIR, "scene.json"), "utf8"));

const loader = new GLTFLoader();
const parse = (buf) => new Promise((res, rej) =>
  loader.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength), "", res, rej));

const root = new THREE.Group();
const objs = {};
let failed = 0;
for (const p of scene.parts) {
  const g = new THREE.Group();
  g.name = p.id;
  const d = THREE.MathUtils.degToRad;
  g.position.set(p.place.x, p.place.y, p.place.z);
  g.rotation.set(d(p.place.rx), d(p.place.ry), d(p.place.rz), "XYZ");
  if (p.glb) {
    try {
      const gl = await parse(fs.readFileSync(path.join(DIR, p.glb)));
      g.add(gl.scene);
    } catch (e) {
      console.error(`${p.id}: ${p.glb} failed to load: ${e.message || e}`);
      failed++;
    }
  }
  objs[p.id] = g;
}
for (const p of scene.parts) (p.parent && objs[p.parent] ? objs[p.parent] : root).add(objs[p.id]);
root.updateMatrixWorld(true);
const box = new THREE.Box3().setFromObject(root);
let meshes = 0, tris = 0;
root.traverse((o) => { if (o.isMesh) { meshes++; tris += (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3; } });
console.log(`loaded ${scene.parts.length} parts, ${meshes} meshes, ${tris} triangles, ${failed} failed`);
console.log(`box x ${box.min.x.toFixed(1)}..${box.max.x.toFixed(1)} y ${box.min.y.toFixed(1)}..${box.max.y.toFixed(1)} z ${box.min.z.toFixed(1)}..${box.max.z.toFixed(1)}`);

// ---------------------------------------------------------------------------- the rasteriser --
function png(w, h, rgb) {
  const crc = (b) => { let c, t = []; for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
    let x = 0xffffffff; for (const v of b) x = t[(x ^ v) & 0xff] ^ (x >>> 8); return (x ^ 0xffffffff) >>> 0; };
  const chunk = (type, data) => { const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const td = Buffer.concat([Buffer.from(type), data]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([len, td, c]); };
  const raw = Buffer.alloc((w * 3 + 1) * h);
  for (let y = 0; y < h; y++) { raw[y * (w * 3 + 1)] = 0; rgb.copy(raw, y * (w * 3 + 1) + 1, y * w * 3, (y + 1) * w * 3); }
  const ih = Buffer.alloc(13); ih.writeUInt32BE(w, 0); ih.writeUInt32BE(h, 4); ih[8] = 8; ih[9] = 2;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk("IHDR", ih), chunk("IDAT", zlib.deflateSync(raw)), chunk("IEND", Buffer.alloc(0))]);
}

function render(file, view, offsets = {}) {
  const W = 1400, H = 700, rgb = Buffer.alloc(W * H * 3, 255), zb = new Float32Array(W * H).fill(-Infinity);
  const tri = [];
  const v = new THREE.Vector3(), M = new THREE.Matrix4();
  root.traverse((o) => {
    if (!o.isMesh) return;
    let top = o; while (top.parent && top.parent !== root && !(top.name in offsets)) top = top.parent;
    const off = offsets[top.name] || [0, 0, 0];
    M.copy(o.matrixWorld);
    const pos = o.geometry.attributes.position, idx = o.geometry.index;
    const col = o.material.color;
    const n = idx ? idx.count : pos.count;
    for (let i = 0; i < n; i += 3) {
      const t = [];
      for (let k = 0; k < 3; k++) { v.fromBufferAttribute(pos, idx ? idx.getX(i + k) : i + k).applyMatrix4(M); t.push([v.x + off[0], v.y + off[1], v.z + off[2]]); }
      tri.push([t, col]);
    }
  });
  const P = tri.flatMap(([t]) => t.map(view));
  const xs = P.map((p) => p[0]), ys = P.map((p) => p[1]);
  // a loop, not Math.min(...xs): the found model's parts run to 10^5 points, past the spread limit
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (let i = 0; i < xs.length; i++) { x0 = Math.min(x0, xs[i]); x1 = Math.max(x1, xs[i]); y0 = Math.min(y0, ys[i]); y1 = Math.max(y1, ys[i]); }
  const s = Math.min((W - 40) / (x1 - x0), (H - 40) / (y1 - y0));
  const L = new THREE.Vector3(0.3, 0.5, 0.8).normalize();
  for (const [t, col] of tri) {
    const q = t.map(view).map(([x, y, z]) => [20 + (x - x0) * s, H - 20 - (y - y0) * s, z]);
    const a = new THREE.Vector3(...t[0]), b = new THREE.Vector3(...t[1]), c = new THREE.Vector3(...t[2]);
    const nrm = b.clone().sub(a).cross(c.clone().sub(a)).normalize();
    const vn = new THREE.Vector3(...view([nrm.x, nrm.y, nrm.z], true)).normalize();
    const sh = 0.35 + 0.65 * Math.abs(vn.dot(L));
    const minx = Math.max(0, Math.floor(Math.min(q[0][0], q[1][0], q[2][0]))), maxx = Math.min(W - 1, Math.ceil(Math.max(q[0][0], q[1][0], q[2][0])));
    const miny = Math.max(0, Math.floor(Math.min(q[0][1], q[1][1], q[2][1]))), maxy = Math.min(H - 1, Math.ceil(Math.max(q[0][1], q[1][1], q[2][1])));
    const den = (q[1][1] - q[2][1]) * (q[0][0] - q[2][0]) + (q[2][0] - q[1][0]) * (q[0][1] - q[2][1]);
    if (Math.abs(den) < 1e-9) continue;
    for (let y = miny; y <= maxy; y++) for (let x = minx; x <= maxx; x++) {
      const w0 = ((q[1][1] - q[2][1]) * (x - q[2][0]) + (q[2][0] - q[1][0]) * (y - q[2][1])) / den;
      const w1 = ((q[2][1] - q[0][1]) * (x - q[2][0]) + (q[0][0] - q[2][0]) * (y - q[2][1])) / den;
      const w2 = 1 - w0 - w1;
      if (w0 < 0 || w1 < 0 || w2 < 0) continue;
      const z = w0 * q[0][2] + w1 * q[1][2] + w2 * q[2][2];
      const k = y * W + x;
      if (z <= zb[k]) continue;
      zb[k] = z;
      rgb[k * 3] = Math.min(255, col.r * 255 * sh); rgb[k * 3 + 1] = Math.min(255, col.g * 255 * sh); rgb[k * 3 + 2] = Math.min(255, col.b * 255 * sh);
    }
  }
  fs.writeFileSync(path.join(OUT, file), png(W, H, rgb));
  return path.join(OUT, file);
}

// views: [screen x, screen y, depth (bigger is nearer)]
const side = ([x, y, z]) => [-y, z, -x];                 // from the left, front to the left
const top = ([x, y, z]) => [-y, -x, z];                  // from above, front to the left
const front = ([x, y, z]) => [x, z, y];                  // from ahead
const c = Math.SQRT1_2, el = 0.5;
const iso = ([x, y, z]) => { const u = c * (-y) + c * (-x), w = c * (-x) - c * (-y); return [u, z * Math.cos(el) + w * Math.sin(el), -w * Math.cos(el) + z * Math.sin(el)]; };
const shots = [render("car-side.png", side), render("car-top.png", top), render("car-front.png", front), render("car-iso.png", iso)];
// exploded: each part moved by its chain of mate.apart
const by = Object.fromEntries(scene.parts.map((p) => [p.id, p]));
const chain = (id, seen = new Set()) => { const p = by[id]; if (!p || !p.mate || seen.has(id)) return [0, 0, 0]; seen.add(id);
  const up = chain(p.mate.to, seen); return [up[0] + p.mate.apart.x, up[1] + p.mate.apart.y, up[2] + p.mate.apart.z]; };
const offs = {};
for (const p of scene.parts) if (p.glb) offs[p.id] = chain(p.id);
shots.push(render("car-iso-apart.png", iso, offs));
console.log("rendered: " + shots.join(" "));
process.exit(failed ? 1 : 0);
