// Writes the stub scene's two models (node tests/fixtures/design/make.mjs): plain boxes in
// glTF's own convention - metres, y up - with the node names the scene's `nodes` groups
// use, so the page's reading of a real export (design.ts glbReading) is exercised. pmu.glb
// is left absent on purpose: the page must name a model that does not load and keep the rest.
import { writeFileSync } from 'node:fs';

const FACES = [
  [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[-1, 0, 0], [0, 0, 1], [0, 1, 0]],
  [[0, 1, 0], [0, 0, 1], [1, 0, 0]], [[0, -1, 0], [1, 0, 0], [0, 0, 1]],
  [[0, 0, 1], [1, 0, 0], [0, 1, 0]], [[0, 0, -1], [0, 1, 0], [1, 0, 0]],
];

function box([cx, cy, cz], [sx, sy, sz]) {
  const pos = [], nor = [], idx = [];
  for (const [n, u, v] of FACES) {
    const base = pos.length / 3;
    for (const [a, b] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
      const p = [0, 1, 2].map((k) => (n[k] + a * u[k] + b * v[k]) / 2);
      pos.push(cx + p[0] * sx, cy + p[1] * sy, cz + p[2] * sz);
      nor.push(...n);
    }
    idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
  }
  return { pos, nor, idx };
}

function glb(file, meshes) {
  const json = { asset: { version: '2.0', generator: 'rx7 stub' }, scene: 0, scenes: [{ nodes: [0] }], nodes: [{ name: 'root', children: [] }], meshes: [], materials: [], accessors: [], bufferViews: [], buffers: [] };
  const chunks = [];
  let offset = 0;
  const view = (bytes, target) => {
    json.bufferViews.push({ buffer: 0, byteOffset: offset, byteLength: bytes.byteLength, target });
    chunks.push(Buffer.from(bytes.buffer));
    offset += bytes.byteLength;
    return json.bufferViews.length - 1;
  };
  for (const m of meshes) {
    const b = box(m.at, m.size);
    const pos = new Float32Array(b.pos), nor = new Float32Array(b.nor), idx = new Uint16Array(b.idx);
    const min = [0, 1, 2].map((k) => Math.min(...b.pos.filter((_, i) => i % 3 === k)));
    const max = [0, 1, 2].map((k) => Math.max(...b.pos.filter((_, i) => i % 3 === k)));
    const a = json.accessors.length;
    json.accessors.push(
      { bufferView: view(pos, 34962), componentType: 5126, count: pos.length / 3, type: 'VEC3', min, max },
      { bufferView: view(nor, 34962), componentType: 5126, count: nor.length / 3, type: 'VEC3' },
      { bufferView: view(idx, 34963), componentType: 5123, count: idx.length, type: 'SCALAR' },
    );
    if (offset % 4) { chunks.push(Buffer.alloc(4 - (offset % 4))); offset += 4 - (offset % 4); }
    json.materials.push({ name: m.name, pbrMetallicRoughness: { baseColorFactor: m.color, metallicFactor: 0.2, roughnessFactor: 0.6 } });
    json.meshes.push({ name: m.name, primitives: [{ attributes: { POSITION: a, NORMAL: a + 1 }, indices: a + 2, material: json.materials.length - 1 }] });
    json.nodes.push({ name: m.name, mesh: json.meshes.length - 1 });
    json.nodes[0].children.push(json.nodes.length - 1);
  }
  const bin = Buffer.concat(chunks);
  json.buffers.push({ byteLength: bin.length });
  let text = Buffer.from(JSON.stringify(json));
  if (text.length % 4) text = Buffer.concat([text, Buffer.alloc(4 - (text.length % 4), 0x20)]);
  const head = Buffer.alloc(12);
  const total = 12 + 8 + text.length + 8 + bin.length;
  head.writeUInt32LE(0x46546c67, 0); head.writeUInt32LE(2, 4); head.writeUInt32LE(total, 8);
  const ch = (len, type) => { const h = Buffer.alloc(8); h.writeUInt32LE(len, 0); h.writeUInt32LE(type, 4); return h; };
  writeFileSync(new URL(file, import.meta.url), Buffer.concat([head, ch(text.length, 0x4e4f534a), text, ch(bin.length, 0x004e4942), bin]));
}

// The control unit: 160 x 120 x 50 mm (x, y, z in its own z-up frame), origin at the middle
// of its base - in glTF that is x 0.16, y 0.05 (up), z 0.12.
glb('control-unit.glb', [
  { name: 'case:body', at: [0, 0.025, 0], size: [0.16, 0.05, 0.12], color: [0.24, 0.35, 0.5, 1] },
  { name: 'inside:carrier', at: [0, 0.012, 0], size: [0.14, 0.002, 0.1], color: [0.1, 0.45, 0.2, 1] },
]);
// Its carrier board: 140 x 100 x 1.6 mm.
glb('dcu-carrier.glb', [{ name: 'board', at: [0, 0.0008, 0], size: [0.14, 0.0016, 0.1], color: [0.1, 0.45, 0.2, 1] }]);
