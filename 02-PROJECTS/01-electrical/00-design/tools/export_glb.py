"""The electrical design in 3D for the app (02-APP D-505, work row Y23). One command, from the
tree's root:

    python3 02-PROJECTS/01-electrical/00-design/tools/export_glb.py [--out DIR] [--only NAME]
    python3 02-PROJECTS/01-electrical/00-design/tools/export_glb.py --check
    python3 02-PROJECTS/01-electrical/00-design/tools/export_glb.py --selftest [SCENE]

It writes, into DIR (default 02-APP/app/public/design/01-electrical):

  <board>.glb       each KiCad board with its parts' 3D models, tracks, pads, zones, silkscreen
                    and soldermask (kicad-cli pcb export glb), re-packed (see below)
  control-unit.glb  the climate unit's case and the insides no board stands for, from the
  display-unit.glb  FreeCAD mock-ups (export_glb_fc.py imports their own unit_lib, so nothing
                    is drawn twice), one named node per solid: case:<name>, inside:<name>
  pmu.glb           ECUMaster's PMU-24 STEP from 01-REFERENCE, with its own face colours
  scene.json        every part, its place, its connectors, and one labelled link per housing
                    (contract version 1, described in 00-design/README.md)

Every glb is in the part's own frame, in millimetres, z up - NOT glTF's metres and y up - so a
viewer working in the car's frame (D-418) puts the file under a node at `place` and nothing else.
The geometry is re-packed: one node per named group, one primitive per material (chunks of at
most 65535 vertices, 16-bit indices), float positions and 8-bit normals (KHR_mesh_quantization,
which three.js reads natively).

Reads the record only through `rx7.py export` (00-CAR zones and parts, 01-electrical housings,
cavities, modules and parts) and writes nothing to it. Owns no fact: every place it cannot find
in a row is `place_from: provisional` and `confirm: true`; the far ends' and the units' spots are
judgement, one line each in WHERE and TOP below.

Exit 0 built (or, with --check, current) - 1 a source is inconsistent (a board the scene names
has no glb, a mock-up refuses its parameters, a scene that breaks the contract, a stale asset
under --check) - 2 with --check, assets missing (not built on this machine) - 3 a usage error or
a tool crash.
"""
import argparse
import array
import datetime
import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)                                   # 00-design
ROOT = os.path.abspath(os.path.join(DESIGN, "..", "..", ".."))  # the tree
OUT_DEFAULT = os.path.join(ROOT, "02-APP", "app", "public", "design", "01-electrical")
KICAD_CLI = os.environ.get("KICAD_CLI", "/opt/homebrew/bin/kicad-cli")
FREECADCMD = os.environ.get("FREECADCMD",
                            "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")
KICAD_MODELS = os.environ.get("KICAD10_3DMODEL_DIR",
                              "/Applications/KiCad/KiCad.app/Contents/SharedSupport/3dmodels")
RX7_MODELS = os.path.join(ROOT, "01-REFERENCE", "model", "library", "electrical")
PMU_STEP = os.path.join(ROOT, "01-REFERENCE", "PMU_info", "PMU CAD info", "PMU-24.STEP")

# The PMU sets the standard (D-505): fine enough that every radius reads round.
PMU_LINEAR, PMU_ANGULAR = 0.03, 0.15          # mm, radians
UNIT_LINEAR, UNIT_ANGULAR = 0.05, 0.2

KICAD_FLAGS = ["--subst-models", "--include-tracks", "--include-pads", "--include-zones",
               "--include-silkscreen", "--include-soldermask"]

# ---------------------------------------------------------------------------------- the design --
# Each board: its KiCad project and the record row that names it (01-electrical parts / modules).
BOARDS = {
    "dcu-carrier": ("control-unit/cad/dcu-carrier/dcu-carrier.kicad_pcb", "parts", "P144"),
    "panel": ("control-unit/cad/panel/panel.kicad_pcb", "modules", "PANEL"),
    "upper-board": ("control-unit/cad/upper-board/upper-board.kicad_pcb", "parts", "P195"),
    "left-plate": ("control-unit/cad/left-plate/left-plate.kicad_pcb", "parts", "P198"),
    "icu-carrier": ("display-unit/cad/icu-carrier/icu-carrier.kicad_pcb", "parts", "P103"),
}
# Each unit: its mock-up, the record row that names it, and which of the mock-up's inside solids
# a child board's glb stands for (those are left out of the unit's glb, so nothing is drawn twice).
UNITS = {
    "control-unit": {"dir": "control-unit/cad/climate-unit", "row": ("modules", "DCU"),
                     "housing": "P152",
                     "children": {"dcu-carrier": {"kinds": ["carrier"]},
                                  "panel": {"names": ["panel board", "panel ribbon header"]},
                                  "upper-board": {"names": ["upper connector board"],
                                                  "upper_dt13": True}}},
    "display-unit": {"dir": "display-unit/cad/icu-unit", "row": ("modules", "ICU"),
                     "housing": "P111",
                     "children": {"icu-carrier": {"kinds": ["carrier"]}}},
}
PMU = {"id": "pmu", "row": ("modules", "PMU")}
ASSETS = list(BOARDS) + list(UNITS) + ["pmu"]

# Where a housing's far end is when the record names a place, not a modelled part. Judgement,
# one line each: (node id, the 00-CAR zone, fx fy fz as fractions across that zone's first box).
# The zone box is the record's (zones.model_box_mm); the fractions are not, so every node made
# from this table is provisional and confirm.
WHERE = {
    "L1 Engine": ("leg-l1", "engine_bay", (0.5, 0.5, 0.5), "L1 Engine - the leg's far end"),
    "L2 Front": ("leg-l2", "front", (0.5, 0.5, 0.5), "L2 Front - the leg's far end"),
    "L3 Dash": ("leg-l3", "dash", (0.35, 0.45, 0.45), "L3 Dash - the leg's devices"),
    "L4 Rear": ("leg-l4", "cargo", (0.5, 0.5, 0.3), "L4 Rear - the leg's far end"),
    "HVAC case": ("hvac-case", "dash", (0.62, 0.75, 0.4), "HVAC case"),
    "Sill node": ("sill-node", "cabin", (0.05, 0.95, 0.15), "Sill node (driver kick panel)"),
    "Glovebox": ("glovebox", "dash", (0.75, 0.2, 0.35), "Glovebox"),
    "Nose": ("nose", "front", (0.5, 0.8, 0.45), "Nose"),
    "Nose, behind the front bumper": ("nose-bumper", "front", (0.5, 0.95, 0.35),
                                      "Nose, behind the front bumper"),
    "Centre stack": ("centre-stack", "dash", (0.5, 0.3, 0.2), "Centre stack, behind it"),
    "Behind the dash": ("behind-dash", "dash", (0.45, 0.6, 0.55), "Behind the dash"),
    "Rear node": ("rear-node", "cargo", (0.5, 0.6, 0.2), "Rear node"),
    "Under the driver's seat": ("seat-driver", "cabin", (0.3, 0.5, 0.08),
                                "Under the driver's seat"),
    "Under the passenger seat": ("seat-passenger", "cabin", (0.7, 0.5, 0.08),
                                 "Under the passenger seat"),
    "Hatch, behind the trim": ("hatch", "cargo", (0.5, 0.15, 0.9), "Hatch, behind the trim"),
    "Driver kick panel": ("kick-driver", "cabin", (0.05, 0.97, 0.12), "Driver kick panel"),
    "Passenger kick panel": ("kick-passenger", "cabin", (0.95, 0.97, 0.12),
                             "Passenger kick panel"),
    "Driver A-pillar base / sail panel": ("pillar-driver", "dash", (0.03, 0.15, 0.95),
                                          "Driver A-pillar base"),
    "Passenger A-pillar base / sail panel": ("pillar-passenger", "dash", (0.97, 0.15, 0.95),
                                             "Passenger A-pillar base"),
    "Console, between the seats": ("console", "cabin", (0.5, 0.75, 0.3),
                                   "Console, between the seats"),
    "Driver rear quarter trim": ("quarter-driver", "cargo", (0.04, 0.8, 0.4),
                                 "Driver rear quarter trim"),
    "Passenger rear quarter trim": ("quarter-passenger", "cargo", (0.96, 0.8, 0.4),
                                    "Passenger rear quarter trim"),
    "Driver-side cargo bin": ("cargo-bin", "cargo", (0.15, 0.5, 0.15), "Driver-side cargo bin"),
}
# The top-level parts: no row places any of them yet (00-CAR parts has no model_at_mm for the
# cluster, the radio or the PMU, and D-416 says nothing places the dash node), so each is a
# judgement inside 00-CAR zones dash: (fx fy fz across the box, what the spot stands for). The
# point is the face's centre for a unit, the board's centre for the plate, the box's centre for
# the PMU. Driver on the left: a US car (x right, D-418).
TOP = {
    "control-unit": ((0.5, 0.12, 0.33), "the centre stack's opening (modules DCU)"),
    "display-unit": ((0.28, 0.1, 0.72), "the binnacle aperture ahead of the driver (modules ICU)"),
    "pmu": ((0.5, 0.8, 0.3), "the dash node, behind the stack at the firewall (modules PMU)"),
    "left-plate": ((0.12, 0.04, 0.55), "the dash face left of the wheel (P198)"),
}
# Drops whose far end is not the dash post: the record's rulings, one line each.
FAR_END = {
    "DP-DCU-D": ("hvac-case", "D-480: the door servos and the blower stage at the HVAC case"),
    "DP-DCU-E": ("left-plate", "D-492: the left plate's link"),
}


def rel(p):
    return os.path.relpath(p, ROOT)


class Fail(Exception):
    """rc 1: a source is inconsistent."""


class Crash(Exception):
    """rc 3: a tool is missing or crashed."""


# =================================================================================== glb, pure ==
# Read, write and measure binary glTF without numpy: the system python and FreeCAD's both import
# this module.
F32, U8, I8, U16, U32 = 5126, 5121, 5120, 5123, 5125
_CT = {F32: ("f", 4), U8: ("B", 1), I8: ("b", 1), U16: ("H", 2), U32: ("I", 4)}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    with open(path, "rb") as fh:
        data = fh.read()
    magic, ver, length = struct.unpack("<4sII", data[:12])
    if magic != b"glTF" or ver != 2:
        raise Fail("%s is not a glTF 2 binary" % path)
    off, js, bin_ = 12, None, b""
    while off < length:
        clen, ctype = struct.unpack("<I4s", data[off:off + 8])
        chunk = data[off + 8:off + 8 + clen]
        if ctype == b"JSON":
            js = json.loads(chunk.decode("utf-8"))
        elif ctype == b"BIN\x00":
            bin_ = chunk
        off += 8 + clen
    return js, bin_


def _accessor(js, bin_, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    code, size = _CT[a["componentType"]]
    nc = _NC[a["type"]]
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0) or size * nc
    count = a["count"]
    out = array.array(code)
    if stride == size * nc:
        out.frombytes(bin_[base:base + count * stride])
    else:
        for k in range(count):
            o = base + k * stride
            out.frombytes(bin_[o:o + size * nc])
    if sys.byteorder != "little":
        out.byteswap()
    if a.get("normalized") and code in "bB":
        scale = 127.0 if code == "b" else 255.0
        out = array.array("f", [max(v / scale, -1.0) for v in out])
    return out


def _mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _node_matrix(n):
    if "matrix" in n:
        m = n["matrix"]
        return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
    t = n.get("translation", [0, 0, 0])
    x, y, z, w = n.get("rotation", [0, 0, 0, 1])
    s = n.get("scale", [1, 1, 1])
    r = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return [[r[0][0] * s[0], r[0][1] * s[1], r[0][2] * s[2], t[0]],
            [r[1][0] * s[0], r[1][1] * s[1], r[1][2] * s[2], t[1]],
            [r[2][0] * s[0], r[2][1] * s[1], r[2][2] * s[2], t[2]],
            [0, 0, 0, 1]]


def _walk(js, visit):
    """visit(node_index, world_matrix, top_level_index) for every node under the scene."""
    eye = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    scene = js["scenes"][js.get("scene", 0)]
    stack = [(i, eye, None) for i in scene["nodes"]]
    while stack:
        i, parent, top = stack.pop()
        m = _mat_mul(parent, _node_matrix(js["nodes"][i]))
        visit(i, m, top)
        for c in js["nodes"][i].get("children", []):
            stack.append((c, m, c if top is None else top))


def glb_bbox(path):
    """The file's bounding box in its own frame: accessor min / max through each node's matrix."""
    js, _ = read_glb(path)
    lo, hi = [math.inf] * 3, [-math.inf] * 3

    def visit(i, m, top):
        n = js["nodes"][i]
        if "mesh" not in n:
            return
        for p in js["meshes"][n["mesh"]]["primitives"]:
            a = js["accessors"][p["attributes"]["POSITION"]]
            amin, amax = a["min"], a["max"]
            for cx in (amin[0], amax[0]):
                for cy in (amin[1], amax[1]):
                    for cz in (amin[2], amax[2]):
                        for k in range(3):
                            v = m[k][0] * cx + m[k][1] * cy + m[k][2] * cz + m[k][3]
                            lo[k], hi[k] = min(lo[k], v), max(hi[k], v)
    _walk(js, visit)
    return lo, hi


def material(name, rgba, metallic=0.0, roughness=0.6):
    return {"name": name, "rgba": [round(float(c), 4) for c in rgba],
            "metallic": metallic, "roughness": roughness}


def write_glb(path, nodes, materials, root_name, extras=None):
    """nodes: [{"name", "prims": [(material index, positions array('f'), normals array('f'),
    indices array('I'))]}] in the part's own frame, mm, z up. One glTF node per entry under one
    root, one primitive per material per chunk of at most 65535 vertices. Returns
    {"bytes", "bbox": [lo, hi], "vertices", "triangles"}."""
    blob = bytearray()
    views, accs, meshes, gnodes = [], [], [], []
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    nverts = ntris = 0

    def put(data, target, stride=None):
        while len(blob) % 4:
            blob.append(0)
        v = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data), "target": target}
        if stride:
            v["byteStride"] = stride
        blob.extend(data)
        views.append(v)
        return len(views) - 1

    def flush(mat, pos, nrm, idx, prims):
        nonlocal nverts, ntris
        n = len(pos) // 3
        if n == 0 or not idx:
            return
        xs, ys, zs = pos[0::3], pos[1::3], pos[2::3]
        mn, mx = [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]
        for k in range(3):
            lo[k], hi[k] = min(lo[k], mn[k]), max(hi[k], mx[k])
        p = array.array("f", pos)
        qb = array.array("b", [127 if c >= 1.0 else -127 if c <= -1.0 else int(round(c * 127.0))
                               for c in nrm]).tobytes()
        q = bytearray(4 * n)                       # int8 x3, padded to 4 bytes a vertex
        q[0::4], q[1::4], q[2::4] = qb[0::3], qb[1::3], qb[2::3]
        wide = n > 65535
        ix = array.array("I" if wide else "H", idx)
        if sys.byteorder != "little":
            p.byteswap()
            ix.byteswap()
        accs.append({"bufferView": put(p.tobytes(), 34962), "componentType": F32, "count": n,
                     "type": "VEC3", "min": mn, "max": mx})
        pa = len(accs) - 1
        accs.append({"bufferView": put(bytes(q), 34962, 4), "componentType": I8,
                     "normalized": True, "count": n, "type": "VEC3"})
        na = len(accs) - 1
        accs.append({"bufferView": put(ix.tobytes(), 34963),
                     "componentType": U32 if wide else U16, "count": len(ix), "type": "SCALAR"})
        prims.append({"attributes": {"POSITION": pa, "NORMAL": na}, "indices": len(accs) - 1,
                      "material": mat, "mode": 4})
        nverts += n
        ntris += len(ix) // 3

    for node in nodes:
        by_mat = {}
        for (mat, pos, nrm, idx) in node["prims"]:
            by_mat.setdefault(mat, []).append((pos, nrm, idx))
        prims = []
        for mat in sorted(by_mat):
            pos, nrm, idx = array.array("f"), array.array("f"), []
            for (p, nm, ix) in by_mat[mat]:
                n = len(p) // 3
                if len(pos) // 3 + n > 65535 and len(pos):
                    flush(mat, pos, nrm, idx, prims)
                    pos, nrm, idx = array.array("f"), array.array("f"), []
                base = len(pos) // 3
                pos.extend(p)
                nrm.extend(nm)
                idx.extend([i + base for i in ix])
            flush(mat, pos, nrm, idx, prims)
        if not prims:
            continue
        meshes.append({"name": node["name"], "primitives": prims})
        gnodes.append({"name": node["name"], "mesh": len(meshes) - 1})
    js = {
        "asset": {"version": "2.0", "generator": "Rx7 00-design/tools/export_glb.py",
                  "extras": dict(extras or {}, units="mm", up="z")},
        "extensionsUsed": ["KHR_mesh_quantization"],
        "extensionsRequired": ["KHR_mesh_quantization"],
        "scene": 0,
        "scenes": [{"name": root_name, "nodes": [0]}],
        "nodes": [{"name": root_name, "children": list(range(1, len(gnodes) + 1))}] + gnodes,
        "meshes": meshes,
        "materials": [{"name": m["name"], "doubleSided": True,
                       "pbrMetallicRoughness": {"baseColorFactor": m["rgba"],
                                                "metallicFactor": m["metallic"],
                                                "roughnessFactor": m["roughness"]}}
                      for m in materials],
        "accessors": accs,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    if any(m["rgba"][3] < 1 for m in materials):
        for g, m in zip(js["materials"], materials):
            if m["rgba"][3] < 1:
                g["alphaMode"] = "BLEND"
    jb = json.dumps(js, separators=(",", ":")).encode("utf-8")
    jb += b" " * ((4 - len(jb) % 4) % 4)
    while len(blob) % 4:
        blob.append(0)
    total = 12 + 8 + len(jb) + 8 + len(blob)
    tmp = path + ".part"
    with open(tmp, "wb") as fh:
        fh.write(struct.pack("<4sII", b"glTF", 2, total))
        fh.write(struct.pack("<I4s", len(jb), b"JSON"))
        fh.write(jb)
        fh.write(struct.pack("<I4s", len(blob), b"BIN\x00"))
        fh.write(blob)
    os.replace(tmp, path)
    box = [[round(v, 3) + 0.0 for v in lo], [round(v, 3) + 0.0 for v in hi]]
    return {"bytes": total, "bbox": box, "vertices": nverts, "triangles": ntris}


def repack_kicad(src, dst, root_name):
    """kicad-cli's glb (metres, y up, one node per part and per layer, 40 000-odd primitives)
    -> ours: mm, z up, the board frame (x = KiCad x, y = -KiCad y, z up from the board's
    underside - the frame of the board's STEP and of enclosure_extract's board.json), two nodes:
    `pcb:board` (the laminate, copper, mask, silkscreen) and `pcb:parts` (the parts' models)."""
    js, bin_ = read_glb(src)
    mats, mat_of = [], {}
    for i, m in enumerate(js.get("materials", [])):
        pbr = m.get("pbrMetallicRoughness", {})
        rgba = pbr.get("baseColorFactor", [0.7, 0.7, 0.7, 1.0])
        key = tuple(round(c, 4) for c in rgba)
        if key not in mat_of:
            mat_of[key] = len(mats)
            mats.append(material("m%d" % len(mats), rgba, pbr.get("metallicFactor", 0.0),
                                 pbr.get("roughnessFactor", 0.6)))
        mat_of[i] = mat_of[key]
    if not mats:
        mats.append(material("default", [0.7, 0.7, 0.7, 1.0]))
    groups = {"pcb:board": [], "pcb:parts": []}
    names = js["nodes"]

    def visit(i, m, top):
        n = names[i]
        if "mesh" not in n:
            return
        # the frame: glTF (X, Y, Z) metres -> (1000 X, -1000 Z, 1000 Y) mm
        c = [[1000 * m[0][j] for j in range(4)],
             [-1000 * m[2][j] for j in range(4)],
             [1000 * m[1][j] for j in range(4)]]
        tname = names[top].get("name", "") if top is not None else ""
        group = "pcb:board" if (top is None or tname.startswith("=>")) else "pcb:parts"
        for p in js["meshes"][n["mesh"]]["primitives"]:
            if p.get("mode", 4) != 4:
                continue
            pos = _accessor(js, bin_, p["attributes"]["POSITION"])
            xs, ys, zs = pos[0::3], pos[1::3], pos[2::3]
            out = array.array("f", bytes(4 * len(pos)))
            for k in range(3):
                a, b, cc, d = c[k]
                out[k::3] = array.array("f", [a * x + b * y + cc * z + d
                                              for x, y, z in zip(xs, ys, zs)])
            if "indices" in p:
                idx = list(_accessor(js, bin_, p["indices"]))
            else:
                idx = list(range(len(pos) // 3))
            if "NORMAL" in p["attributes"]:
                nr = _accessor(js, bin_, p["attributes"]["NORMAL"])
                nx, ny, nz = nr[0::3], nr[1::3], nr[2::3]
                outn = array.array("f", bytes(4 * len(nr)))
                for k in range(3):
                    a, b, cc, _ = c[k]
                    outn[k::3] = array.array("f", [a * x + b * y + cc * z
                                                   for x, y, z in zip(nx, ny, nz)])
                for k in range(0, len(outn), 3):
                    ln = math.sqrt(outn[k] ** 2 + outn[k + 1] ** 2 + outn[k + 2] ** 2) or 1.0
                    outn[k], outn[k + 1], outn[k + 2] = (outn[k] / ln, outn[k + 1] / ln,
                                                         outn[k + 2] / ln)
            else:
                outn = face_normals(out, idx)
            if group == "pcb:board":
                out, outn, idx = _drop_low_walls(out, outn, idx)
            if idx:
                groups[group].append((mat_of.get(p.get("material"), 0), out, outn, idx))
    _walk(js, visit)
    nodes = [{"name": g, "prims": groups[g]} for g in ("pcb:board", "pcb:parts")]
    return write_glb(dst, nodes, mats, root_name)


LOW_WALL = 0.1    # mm: a vertical wall shorter than this is a copper or mask edge


def _drop_low_walls(pos, nrm, idx):
    """Drop the board's vertical walls under LOW_WALL tall - the 35 um edges of every track,
    pad and pour, invisible at any zoom and half the copper's vertices. The laminate's edge and
    the via barrels (1.6 mm) stay."""
    zs = pos[2::3]
    nz = nrm[2::3]
    keep = []
    for t in range(0, len(idx) - 2, 3):
        a, b, c = idx[t], idx[t + 1], idx[t + 2]
        if abs(nz[a]) < 0.1 and abs(nz[b]) < 0.1 and abs(nz[c]) < 0.1 and \
                max(zs[a], zs[b], zs[c]) - min(zs[a], zs[b], zs[c]) < LOW_WALL:
            continue
        keep += (a, b, c)
    if len(keep) == len(idx):
        return pos, nrm, idx
    remap, p2, n2 = {}, array.array("f"), array.array("f")
    out = []
    for v in keep:
        w = remap.get(v)
        if w is None:
            w = remap[v] = len(p2) // 3
            p2.extend(pos[3 * v:3 * v + 3])
            n2.extend(nrm[3 * v:3 * v + 3])
        out.append(w)
    return p2, n2, out


def face_normals(pos, idx):
    """Smooth normals over one patch: each vertex the area-weighted mean of its triangles'."""
    n = len(pos) // 3
    acc = [0.0] * (3 * n)
    for t in range(0, len(idx) - 2, 3):
        a, b, c = idx[t], idx[t + 1], idx[t + 2]
        ax, ay, az = pos[3 * a], pos[3 * a + 1], pos[3 * a + 2]
        ux, uy, uz = pos[3 * b] - ax, pos[3 * b + 1] - ay, pos[3 * b + 2] - az
        vx, vy, vz = pos[3 * c] - ax, pos[3 * c + 1] - ay, pos[3 * c + 2] - az
        cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        for v in (a, b, c):
            acc[3 * v] += cx
            acc[3 * v + 1] += cy
            acc[3 * v + 2] += cz
    out = array.array("f", acc)
    for k in range(0, len(out), 3):
        ln = math.sqrt(out[k] ** 2 + out[k + 1] ** 2 + out[k + 2] ** 2)
        if ln > 0:
            out[k], out[k + 1], out[k + 2] = out[k] / ln, out[k + 1] / ln, out[k + 2] / ln
        else:
            out[k], out[k + 1], out[k + 2] = 0.0, 0.0, 1.0
    return out


# ============================================================================== the KiCad side ==
def pcb_outline(pcb):
    """The board's Edge.Cuts bounding box in the board frame (x, -y KiCad): [x0, x1, y0, y1]."""
    txt = open(pcb, encoding="utf-8").read()
    xs, ys = [], []
    for m in re.finditer(r"\((gr_line|gr_rect|gr_arc|gr_poly|gr_circle)\b", txt):
        depth, k = 0, m.start()
        while True:
            ch = txt[k]
            depth += (ch == "(") - (ch == ")")
            k += 1
            if depth == 0:
                break
        block = txt[m.start():k]
        if '"Edge.Cuts"' not in block:
            continue
        for x, y in re.findall(r"\((?:start|end|mid|center|xy)\s+([-\d.]+)\s+([-\d.]+)\)", block):
            xs.append(float(x))
            ys.append(-float(y))
    if not xs:
        raise Fail("%s has no Edge.Cuts outline" % rel(pcb))
    return [min(xs), max(xs), min(ys), max(ys)]


def pcb_footprint_at(pcb, ref):
    """A footprint's origin in the board frame, or None."""
    txt = open(pcb, encoding="utf-8").read()
    for m in re.finditer(r"\(footprint\s+\"[^\"]*\"", txt):
        head = txt[m.start():m.start() + 4000]
        if re.search(r'\(property\s+"Reference"\s+"%s"' % re.escape(ref), head):
            at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)", head)
            if at:
                return [float(at.group(1)), -float(at.group(2))]
    return None


def build_board(bid, out):
    pcb = os.path.join(DESIGN, BOARDS[bid][0])
    if not os.path.exists(pcb):
        raise Fail("%s: %s is not there" % (bid, rel(pcb)))
    if not os.path.exists(KICAD_CLI):
        raise Crash("kicad-cli is not at %s (set KICAD_CLI)" % KICAD_CLI)
    env = dict(os.environ, RX7_MODELS=RX7_MODELS, KICAD10_3DMODEL_DIR=KICAD_MODELS)
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, bid + ".glb")
        r = subprocess.run([KICAD_CLI, "pcb", "export", "glb"] + KICAD_FLAGS +
                           ["-f", "-o", raw, pcb], env=env, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(raw):
            raise Crash("kicad-cli failed on %s: %s" % (rel(pcb), (r.stderr or r.stdout)[-400:]))
        missing = sorted(set(re.findall(r"Could not add 3D model for (\S+?)\.",
                                        r.stdout + r.stderr)))
        files = sorted(set(os.path.basename(f) for f in re.findall(
            r"File not found: (\S+)", r.stdout + r.stderr)))
        info = repack_kicad(raw, os.path.join(out, bid + ".glb"), bid)
    meta = {"id": bid, "kind": "pcb", "glb": bid + ".glb", "bytes": info["bytes"],
            "bbox": info["bbox"], "vertices": info["vertices"], "triangles": info["triangles"],
            "nodes": {"board": ["pcb:board"], "parts": ["pcb:parts"]},
            "outline": pcb_outline(pcb), "source": rel(pcb),
            "missing_models": missing, "missing_files": files,
            "origin": "KiCad's origin, the board frame of its STEP: x = KiCad x, y = -KiCad y, "
                      "z = 0 on the board's underside"}
    if bid == "left-plate":
        meta["j1"] = pcb_footprint_at(pcb, "J1")
    if bid == "upper-board":
        meta["dt13"] = {r: pcb_footprint_at(pcb, r) for r in ("J1", "J2")}
    return meta


# =========================================================================== the FreeCAD side ==
def run_fc(job):
    if not os.path.exists(FREECADCMD):
        raise Crash("freecadcmd is not at %s (set FREECADCMD)" % FREECADCMD)
    with tempfile.TemporaryDirectory() as tmp:
        jpath = os.path.join(tmp, "job.json")
        job = dict(job, meta=os.path.join(tmp, "meta.json"))
        with open(jpath, "w") as fh:
            json.dump(job, fh)
        env = dict(os.environ, RX7_EXPORT_JOB=jpath)
        r = subprocess.run([FREECADCMD, os.path.join(HERE, "export_glb_fc.py")], env=env,
                           capture_output=True, text=True, cwd=tmp)
        meta = None
        if os.path.exists(job["meta"]):
            meta = json.load(open(job["meta"]))
        if r.returncode == 1 and meta and meta.get("problems"):
            raise Fail("%s: %s" % (job["id"], " | ".join(meta["problems"])))
        if r.returncode != 0 or meta is None:
            raise Crash("freecadcmd failed on %s (rc %s): %s"
                        % (job["id"], r.returncode, (r.stderr or r.stdout)[-600:]))
        return meta


def build_unit(uid, out):
    u = UNITS[uid]
    meta = run_fc({"id": uid, "kind": "unit", "unit_dir": os.path.join(DESIGN, u["dir"]),
                   "tools_dir": HERE, "glb": os.path.join(out, uid + ".glb"),
                   "children": u["children"], "linear": UNIT_LINEAR, "angular": UNIT_ANGULAR})
    meta.update({"id": uid, "kind": "unit", "glb": uid + ".glb",
                 "source": u["dir"] + " (unit_params.py, unit_lib.py)"})
    return meta


def build_pmu(out):
    if not os.path.exists(PMU_STEP):
        raise Fail("the PMU's STEP is not at %s" % rel(PMU_STEP))
    meta = run_fc({"id": "pmu", "kind": "pmu", "step": PMU_STEP, "tools_dir": HERE,
                   "glb": os.path.join(out, "pmu.glb"),
                   "linear": PMU_LINEAR, "angular": PMU_ANGULAR})
    meta.update({"id": "pmu", "kind": "module", "glb": "pmu.glb", "source": rel(PMU_STEP)})
    return meta


# =============================================================================== the stamps ==
def _hash_files(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(rel(p).encode())
        with open(p, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def source_files(aid):
    """Every file an asset is made from (and this script), for the staleness stamp."""
    mine = [os.path.join(HERE, "export_glb.py"), os.path.join(HERE, "export_glb_fc.py")]
    if aid in BOARDS:
        pcb = os.path.join(DESIGN, BOARDS[aid][0])
        d = os.path.dirname(pcb)
        files = [pcb] + [os.path.join(dp, f) for dp, _, fs in os.walk(d) for f in fs
                         if dp.endswith(".pretty") and f.endswith(".kicad_mod")]
        return mine + files
    if aid in UNITS:
        d = os.path.join(DESIGN, UNITS[aid]["dir"])
        car = os.path.join(os.path.dirname(d), [c for c in UNITS[aid]["children"]
                                                if "carrier" in c][0])
        files = [os.path.join(d, f) for f in ("unit_params.py", "unit_lib.py")]
        files += [os.path.join(car, "enclosure", f) for f in ("board.json", "probe.json")]
        files.append(os.path.join(HERE, "enclosure_lib.py"))
        return mine + [f for f in files if os.path.exists(f)]
    if aid == "pmu":
        return mine + [PMU_STEP]
    raise KeyError(aid)


# =============================================================================== the record ==
def read_record():
    """The tables the scene reads, through rx7.py export (the machine-readable view)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "record.json")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "rx7.py"), "export",
                            "--out", path], cwd=ROOT, capture_output=True, text=True)
        if r.returncode not in (0, 2) or not os.path.exists(path):
            raise Crash("rx7.py export failed (rc %s): %s" % (r.returncode, r.stderr[-300:]))
        data = json.load(open(path))
    want = {("00-CAR", "zones"), ("00-CAR", "parts"), ("01-electrical", "housings"),
            ("01-electrical", "cavities"), ("01-electrical", "modules"),
            ("01-electrical", "parts")}
    out = {}
    for t in data["tables"]:
        key = (t["area"], t["table"])
        if key in want:
            cols = t["columns"]
            out[key] = [dict(zip(cols, row)) for row in t["rows"]]
    for key in want:
        if key not in out:
            raise Fail("the record has no %s %s" % key)
    return out


def _short(text):
    """The record's words, up to the first ' - ' or em dash: its name, not its note."""
    text = (text or "").strip()
    for sep in (" - ", " — ", " – "):
        if sep in text:
            text = text.split(sep)[0]
    return text.strip()


def _zone_box(rec, zid):
    for z in rec[("00-CAR", "zones")]:
        if z["id"] == zid and z.get("model_box_mm"):
            first = z["model_box_mm"].split(";")[0].split()
            return [float(v) for v in first]
    raise Fail("00-CAR zones has no model_box_mm for %r" % zid)


def _in_zone(rec, zid, f):
    b = _zone_box(rec, zid)
    return [round(b[0] + f[0] * (b[1] - b[0]), 1), round(b[2] + f[1] * (b[3] - b[2]), 1),
            round(b[4] + f[2] * (b[5] - b[4]), 1)]


# ================================================================================ the scene ==
def _place(x=0.0, y=0.0, z=0.0, rx=0.0, ry=0.0, rz=0.0):
    return {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3),
            "rx": rx, "ry": ry, "rz": rz}


def _rot(p, place):
    """A point in a child's frame -> its parent's, by `place` (three.js Euler XYZ, degrees)."""
    x, y, z = p
    for axis, deg in (("z", place["rz"]), ("y", place["ry"]), ("x", place["rx"])):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        if axis == "x":
            y, z = c * y - s * z, s * y + c * z
        elif axis == "y":
            x, z = c * x + s * z, -s * x + c * z
        else:
            x, y = c * x - s * y, s * x + c * y
    return [x, y, z]


def _size(meta):
    lo, hi = meta["bbox"]
    return {"x": round(hi[0] - lo[0], 2), "y": round(hi[1] - lo[1], 2),
            "z": round(hi[2] - lo[2], 2)}


def _row(rec, table, key):
    area_table = ("01-electrical", table)
    k = "id"
    for r in rec[area_table]:
        if r.get(k) == key:
            return r
    raise Fail("01-electrical %s has no row %s" % (table, key))


def _name(rec, table, key):
    r = _row(rec, table, key)
    return _short(r.get("module") or r.get("item") or key)


def assemble(rec, metas, built):
    """scene.json from the record and the assets' metas. Raises Fail on an inconsistency."""
    notes, missing, parts = [], [], {}
    for aid in ASSETS:
        if aid not in metas:
            raise Fail("%s has no glb: build it (export_glb.py --only %s)" % (aid, aid))

    # ---- the units, with their boards inside
    for uid, u in UNITS.items():
        m = metas[uid]
        name = _name(rec, *u["row"])
        anchor = _in_zone(rec, "dash", TOP[uid][0])
        fw, fh = m["face"]
        pl = _place(anchor[0] - fw / 2.0, anchor[1], anchor[2] - fh / 2.0)
        conns = [{"code": c["code"], "at": {"x": round(c["at"][0], 2), "y": round(c["at"][1], 2),
                                            "z": round(c["at"][2], 2)},
                  "face": "rear", "note": c.get("note", "")} for c in m["connectors"]]
        parts[uid] = {
            "id": uid, "name": name, "kind": "unit", "glb": m["glb"], "bytes": m["bytes"],
            "parent": None, "place": pl, "place_from": "provisional", "confirm": True,
            "place_note": "inside 00-CAR zones dash: %s, the face's centre there" % TOP[uid][1],
            "size_mm": _size(m),
            "origin": "the mock-up's frame: the face's front, bottom-left corner seen from the "
                      "cabin; x across the face, y back into the dash (= the car's forward), z up",
            "connectors": conns, "children": list(u["children"]), "source": m["source"],
            "nodes": m["nodes"]}
        for kid in u["children"]:
            km = metas[kid]
            cp = child_place(kid, m, km, notes)
            parts[kid] = board_part(rec, kid, km, uid, cp, "mock-up report", False)
        if m.get("placeholders"):
            missing.append({"part": uid, "what": ", ".join(m["placeholders"]),
                            "why": "placeholder blocks in the mock-up: no model of these parts "
                                   "is in the tree"})
        notes += ["%s: %s" % (uid, n) for n in m.get("notes", [])]

    # ---- the left plate: a board with no housing yet, standing for the plate
    lm = metas["left-plate"]
    anchor = _in_zone(rec, "dash", TOP["left-plate"][0])
    o = lm["outline"]
    c = _rot([(o[0] + o[1]) / 2.0, (o[2] + o[3]) / 2.0, 0.0], _place(rx=90))
    lp = _place(anchor[0] - c[0], anchor[1] - c[1], anchor[2] - c[2], rx=90)
    parts["left-plate"] = board_part(rec, "left-plate", lm, None, lp, "provisional", True)
    parts["left-plate"]["place_note"] = ("inside 00-CAR zones dash: %s, the board facing the "
                                         "driver" % TOP["left-plate"][1])
    missing.append({"part": "left-plate", "what": "housing model",
                    "why": "no plate housing is drawn yet; the board stands for the plate"})
    if lm.get("j1"):
        parts["left-plate"]["connectors"] = [{"code": "DP-DCU-E", "at": {
            "x": lm["j1"][0], "y": lm["j1"][1], "z": 0.0}, "face": "rear",
            "note": "J1, the cable to DP-DCU-E (D-492), at its footprint's origin"}]

    # ---- the PMU
    pm = metas["pmu"]
    anchor = _in_zone(rec, "dash", TOP["pmu"][0])
    lo, hi = pm["bbox"]
    ctr = [(lo[k] + hi[k]) / 2.0 for k in range(3)]
    parts["pmu"] = {
        "id": "pmu", "name": _name(rec, *PMU["row"]), "kind": "module", "glb": "pmu.glb",
        "bytes": pm["bytes"], "parent": None,
        "place": _place(anchor[0] - ctr[0], anchor[1] - ctr[1], anchor[2] - ctr[2]),
        "place_from": "provisional", "confirm": True,
        "place_note": "inside 00-CAR zones dash: %s, the box's centre there, as the vendor "
                      "model lies" % TOP["pmu"][1],
        "size_mm": _size(pm), "origin": "the vendor STEP's own origin (ECUMaster's frame)",
        "connectors": [], "children": [], "source": pm["source"], "nodes": pm["nodes"]}

    # ---- links: one per housing, and the nodes their far ends need
    nodes = {}

    def node(key):
        nid, zone, f, label = WHERE[key]
        if nid not in nodes:
            at = _in_zone(rec, zone, f)
            nodes[nid] = {"id": nid, "name": label, "kind": "node", "glb": None, "bytes": 0,
                          "parent": None, "place": _place(*at), "place_from": "provisional",
                          "confirm": True, "place_note": "inside 00-CAR zones %s" % zone,
                          "size_mm": {"x": 0, "y": 0, "z": 0}, "origin": "the place itself",
                          "connectors": [], "children": [],
                          "source": "01-electrical housings.where / leg"}
        return nid

    cav_by = {}
    for cv in rec[("01-electrical", "cavities")]:
        cav_by.setdefault(cv["housing"], []).append(cv)
    unit_of = {"ICU unit": "display-unit", "Climate unit": "control-unit"}
    links, post = [], []
    for h in rec[("01-electrical", "housings")]:
        code, where = h["code"], (h.get("where") or "").strip()
        cavs = sorted(cav_by.get(code, []), key=lambda r: int(r.get("cav") or 0))
        carries = [re.sub(r"\s*\([^)]*\)", "", cv["circuit"]).strip() for cv in cavs
                   if (cv.get("circuit") or "").strip()]
        ways = int(h.get("cavs") or len(cavs) or 0)
        side = h.get("box_side") or h.get("leg_side") or ""
        family = side.split("-")[0] if side else "?"
        label = "%s · %s %d-way" % (code, family, ways)
        on_unit = next((p for k, p in unit_of.items() if where.startswith(k)), None)
        if on_unit:
            frm = {"part": on_unit, "connector": code}
            if code in FAR_END:
                far = FAR_END[code][0]
                if far not in parts:
                    far = node(next(k for k, v in WHERE.items() if v[0] == far))
                to = {"part": far, "connector": code}
            else:
                to = {"part": "pmu", "connector": code}
                post.append(code)
        elif where == "Dash post":
            frm = {"part": "pmu", "connector": code}
            post.append(code)
            leg = (h.get("leg") or "").strip()
            if leg not in WHERE:
                raise Fail("housing %s: leg %r has no far end in WHERE" % (code, leg))
            to = {"part": node(leg), "connector": code}
        else:
            if where not in WHERE:
                raise Fail("housing %s: where %r has no node in WHERE" % (code, where))
            frm = {"part": "pmu", "connector": code}
            post.append(code)
            to = {"part": node(where), "connector": code}
        links.append({"id": code, "code": code, "from": frm, "to": to, "label": label,
                      "ways": ways, "carries": carries, "confirm": False})
    for nid, n in nodes.items():
        n["connectors"] = [{"code": l["code"], "at": {"x": 0, "y": 0, "z": 0}, "face": "",
                            "note": ""} for l in links if l["to"]["part"] == nid]
    # the dash post's receptacles are not modelled: spread along the PMU's connector face
    lo, hi = pm["connector_box"]
    blo, bhi = pm["bbox"]
    span = [hi[k] - lo[k] for k in range(3)]
    ax = max(range(3), key=lambda k: span[k])
    face = [(lo[i] + hi[i]) / 2.0 for i in range(3)]
    for i in range(3):                  # the sockets' outer face: where their box meets the PMU's
        if i != ax and abs(lo[i] - blo[i]) < 1.0:
            face[i] = lo[i]
            break
        if i != ax and abs(hi[i] - bhi[i]) < 1.0:
            face[i] = hi[i]
            break
    for k, code in enumerate(post):
        at = list(face)
        at[ax] = lo[ax] + span[ax] * (k + 0.5) / len(post)
        parts["pmu"]["connectors"].append({
            "code": code, "at": {"x": round(at[0], 2), "y": round(at[1], 2),
                                 "z": round(at[2], 2)}, "face": "connectors",
            "note": "the dash post's receptacle - not modelled; spread along the PMU's "
                    "connector face (provisional)"})
    missing.append({"part": "pmu", "what": "the dash post's receptacles",
                    "why": "no model of the post; its links start on the PMU's connector face"})
    for bid in BOARDS:
        bm = metas[bid]
        if bm.get("missing_models"):
            missing.append({"part": bid, "what": "3D models of %s" % ", ".join(
                bm["missing_models"]), "why": "kicad-cli found no file for them on this "
                "machine (%s); the boards show their pads" % ", ".join(bm["missing_files"])})
    notes += [
        "Every glb is in mm with z up, in the part's own frame; place it at `place` (three.js "
        "Euler XYZ, degrees) under its parent, the car's frame for a top-level part (D-418).",
        "No place here is measured: every unit, the PMU, the left plate and every far end is a "
        "judgement inside its 00-CAR zone box, confirm until the dash is measured (C4, V-102, "
        "V-113).",
        "The PMU stands for the dash node: every leg and drop meets it at the dash post (modules "
        "PMU: Dash node).",
        "A link is a straight line from connector to connector, not the wire's run: the harness "
        "drawings (D-385) stay the wire's truth.",
        "The boards show every part they draw, DNP ones too - the worst case the mock-ups' fit "
        "checks use.",
    ]
    seen = set()
    for l in links:
        if l["id"] in seen:
            raise Fail("two links share the id %s" % l["id"])
        seen.add(l["id"])
    order = list(UNITS) + [k for u in UNITS.values() for k in u["children"]] + \
        ["left-plate", "pmu"]
    out_parts = [parts[k] for k in order] + [nodes[k] for k in sorted(nodes)]
    return {
        "version": 1,
        "built": built,
        "project": "01-electrical",
        "frame": {"units": "mm", "x": "right", "y": "forward", "z": "up", "ruling": "D-418",
                  "glb": "mm, z up, the part's own frame (not glTF's metres, y up)",
                  "rotation": "degrees, three.js Euler order XYZ"},
        "parts": out_parts,
        "links": links,
        "missing": missing,
        "notes": notes,
        "assets": {k: metas[k] for k in ASSETS},
    }


def board_part(rec, bid, m, parent, place, place_from, confirm):
    table, key = BOARDS[bid][1], BOARDS[bid][2]
    return {"id": bid, "name": _name(rec, table, key), "kind": "pcb", "glb": m["glb"],
            "bytes": m["bytes"], "parent": parent, "place": place, "place_from": place_from,
            "confirm": confirm, "size_mm": _size(m), "origin": m["origin"], "connectors": [],
            "children": [], "source": m["source"], "nodes": m["nodes"]}


def child_place(kid, um, km, notes):
    """A board's place in its unit, from the mock-up's own numbers (um, written by
    export_glb_fc.py from the mock-up's derive()) and the board's outline."""
    o = km["outline"]
    bc = [(o[0] + o[1]) / 2.0, (o[2] + o[3]) / 2.0]
    b = um["boards"]
    if kid in ("dcu-carrier", "icu-carrier"):
        mv, turn = b["carrier"]["move"], b["carrier"]["turn"]
        return _place(mv[0], mv[1], mv[2], rz=turn)
    if kid == "panel":
        x0, x1, y0, y1, z0, z1 = b["panel"]
        return _place((x0 + x1) / 2.0 - bc[0], y1, (z0 + z1) / 2.0 - bc[1], rx=90)
    if kid == "upper-board":
        x0, x1, y0, y1, z0, z1 = b["upper"]
        pl = _place((x0 + x1) / 2.0 + bc[0], (y0 + y1) / 2.0 + bc[1], z0, rz=180)
        for code, X in b.get("upper_x", {}).items():
            ref = {"DP-DCU-D": "J1", "DP-DCU-E": "J2"}.get(code)
            at = km.get("dt13", {}).get(ref) if ref else None
            if at:
                got = _rot([at[0], at[1], 0.0], pl)[0] + pl["x"]
                if abs(got - X) > 1.0:
                    notes.append("upper-board: %s's footprint lands at X %.2f, the mock-up's "
                                 "cut-out at %.2f - the board and the mock-up disagree"
                                 % (code, got, X))
        return pl
    raise Fail("no rule places %s in its unit" % kid)


# ============================================================================== the selftest ==
def validate_scene(path):
    """The contract, version 1. Returns a list of problems (empty when it holds)."""
    bad = []
    try:
        s = json.load(open(path))
    except Exception as e:
        return ["%s does not read as JSON: %s" % (path, e)]
    base = os.path.dirname(path)
    for k in ("version", "built", "project", "frame", "parts", "links", "missing", "notes"):
        if k not in s:
            bad.append("no %r" % k)
    if bad:
        return bad
    if s["version"] != 1:
        bad.append("version is %r, not 1" % s["version"])
    try:
        datetime.datetime.fromisoformat(s["built"])
    except Exception:
        bad.append("built %r is not ISO 8601" % s["built"])
    f = s["frame"]
    if (f.get("units"), f.get("x"), f.get("y"), f.get("z")) != ("mm", "right", "forward", "up"):
        bad.append("frame is not mm / right / forward / up")
    ids, conns = {}, {}
    for p in s["parts"]:
        pid = p.get("id")
        if not pid or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pid):
            bad.append("part id %r is not kebab-case" % pid)
        if pid in ids:
            bad.append("part id %s twice" % pid)
        ids[pid] = p
        conns[pid] = {c.get("code") for c in p.get("connectors", [])}
        if p.get("kind") not in ("unit", "pcb", "module", "node"):
            bad.append("%s: kind %r" % (pid, p.get("kind")))
        pl = p.get("place", {})
        if sorted(pl) != sorted("x y z rx ry rz".split()) or not all(
                isinstance(pl[k], (int, float)) and not isinstance(pl[k], bool) for k in pl):
            bad.append("%s: place is not six numbers" % pid)
        if not isinstance(p.get("confirm"), bool):
            bad.append("%s: confirm is not true / false" % pid)
        if p.get("place_from") is None:
            bad.append("%s: no place_from" % pid)
        if p.get("kind") == "node":
            if p.get("glb") is not None:
                bad.append("%s: a node with a glb" % pid)
        else:
            g = p.get("glb")
            if not g:
                bad.append("%s: no glb" % pid)
            else:
                gp = os.path.join(base, g)
                if not os.path.exists(gp):
                    bad.append("%s: %s is not there" % (pid, g))
                elif os.path.getsize(gp) != p.get("bytes"):
                    bad.append("%s: %s is %d bytes, the scene says %s"
                               % (pid, g, os.path.getsize(gp), p.get("bytes")))
        sz = p.get("size_mm", {})
        if sorted(sz) != ["x", "y", "z"]:
            bad.append("%s: size_mm is not x y z" % pid)
        for c in p.get("connectors", []):
            at = c.get("at", {})
            if sorted(at) != ["x", "y", "z"] or not c.get("code"):
                bad.append("%s: a connector without a code or an x y z" % pid)
    for p in s["parts"]:
        par = p.get("parent")
        if par is not None and par not in ids:
            bad.append("%s: parent %s is no part" % (p["id"], par))
        for ch in p.get("children", []):
            if ch not in ids:
                bad.append("%s: child %s is no part" % (p["id"], ch))
            elif ids[ch].get("parent") != p["id"]:
                bad.append("%s: child %s names another parent" % (p["id"], ch))
    lids = set()
    for l in s["links"]:
        if l.get("id") in lids:
            bad.append("link id %s twice" % l.get("id"))
        lids.add(l.get("id"))
        for end in ("from", "to"):
            e = l.get(end, {})
            if e.get("part") not in ids:
                bad.append("link %s: %s part %s is no part" % (l.get("id"), end, e.get("part")))
            elif e.get("connector") not in conns[e["part"]]:
                bad.append("link %s: %s has no connector %s" % (l.get("id"), e["part"],
                                                                e.get("connector")))
        if not isinstance(l.get("ways"), int) or not isinstance(l.get("carries"), list):
            bad.append("link %s: ways or carries malformed" % l.get("id"))
    for m in s["missing"]:
        if m.get("part") not in ids:
            bad.append("missing names %s, no part" % m.get("part"))
    return bad


def selftest(path):
    """The contract check, run on the output and on broken copies of it (each must refuse)."""
    probs = validate_scene(path)
    if probs:
        for p in probs:
            print("  scene: " + p)
        return 1
    s = json.load(open(path))
    cases = []
    t = json.loads(json.dumps(s))
    t["parts"].append(dict(t["parts"][0]))
    cases.append(("a duplicate id", t))
    t = json.loads(json.dumps(s))
    t["parts"][1]["parent"] = "no-such-part"
    cases.append(("a parent that does not exist", t))
    t = json.loads(json.dumps(s))
    t["links"][0]["to"]["part"] = "no-such-part"
    cases.append(("a link end that does not exist", t))
    t = json.loads(json.dumps(s))
    t["parts"][0]["bytes"] += 1
    cases.append(("a glb of other bytes", t))
    t = json.loads(json.dumps(s))
    del t["parts"][0]["place"]["rz"]
    cases.append(("a place of five numbers", t))
    rc = 0
    base = os.path.dirname(os.path.abspath(path))
    for what, t in cases:
        tmp = os.path.join(base, ".selftest-scene.json")
        try:
            with open(tmp, "w") as fh:
                json.dump(t, fh)
            got = validate_scene(tmp)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        print("  %-34s %s" % (what, "refused" if got else "NOT REFUSED"))
        rc |= 0 if got else 1
    print("selftest: %s (the scene holds; %d broken copies, %d refused)"
          % ("pass" if rc == 0 else "FAIL", len(cases), len(cases) - rc))
    return rc


# ==================================================================================== the run ==
class _Args(argparse.ArgumentParser):
    def error(self, message):                     # a usage error is rc 3 here, not argparse's 2
        self.print_usage(sys.stderr)
        print("export_glb: %s" % message, file=sys.stderr)
        sys.exit(3)


def main(argv):
    ap = _Args(description=__doc__.split("\n\n")[0],
               formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--only", choices=ASSETS + ["scene"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", nargs="?", const="", metavar="SCENE")
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    scene_path = os.path.join(out, "scene.json")
    if a.selftest is not None:
        return selftest(a.selftest or scene_path)
    old = json.load(open(scene_path)) if os.path.exists(scene_path) else None
    stamps = {aid: _hash_files(source_files(aid)) for aid in ASSETS}

    if a.check:
        if old is None:
            print("scene.json is not there: build with export_glb.py")
            return 2
        rc, absent = 0, False
        for aid in ASSETS:
            m = old.get("assets", {}).get(aid)
            g = os.path.join(out, aid + ".glb")
            if not os.path.exists(g):
                print("%-14s not built here" % aid)
                absent = True
            elif m is None or os.path.getsize(g) != m["bytes"]:
                print("%-14s does not match scene.json" % aid)
                rc = 1
            elif m.get("stamp") != stamps[aid]:
                print("%-14s stale: its sources changed since it was built" % aid)
                rc = 1
            else:
                print("%-14s current" % aid)
        rec_stamp = _record_stamp(read_record())
        if old.get("record_stamp") != rec_stamp:
            print("scene.json     stale: the record's housings, cavities or places changed")
            rc = 1
        probs = validate_scene(scene_path) if not absent else []
        for p in probs:
            print("scene: " + p)
        if probs:
            rc = 1
        return rc if rc else (2 if absent else 0)

    os.makedirs(out, exist_ok=True)
    metas = dict(old.get("assets", {})) if old else {}
    todo = ASSETS if a.only is None else ([] if a.only == "scene" else [a.only])
    for aid in todo:
        print("%-14s building ..." % aid, flush=True)
        if aid in BOARDS:
            m = build_board(aid, out)
        elif aid in UNITS:
            m = build_unit(aid, out)
        else:
            m = build_pmu(out)
        m["stamp"] = stamps[aid]
        metas[aid] = m
        print("%-14s %8.2f MB  %s x %s x %s mm" % (aid, m["bytes"] / 1e6, *[
            round(m["bbox"][1][k] - m["bbox"][0][k], 1) for k in range(3)]), flush=True)
    rec = read_record()
    built = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    scene = assemble(rec, metas, built)
    scene["record_stamp"] = _record_stamp(rec)
    with open(scene_path + ".part", "w") as fh:
        json.dump(scene, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    os.replace(scene_path + ".part", scene_path)
    probs = validate_scene(scene_path)
    for p in probs:
        print("scene: " + p)
    total = sum(m["bytes"] for m in metas.values()) + os.path.getsize(scene_path)
    print("%-14s %8.2f MB  %d parts, %d links" % ("scene.json", os.path.getsize(scene_path) / 1e6,
                                                   len(scene["parts"]), len(scene["links"])))
    print("%-14s %8.2f MB" % ("total", total / 1e6))
    return 1 if probs else 0


def _record_stamp(rec):
    h = hashlib.sha256()
    for key in sorted(rec):
        h.update(json.dumps([key, rec[key]], sort_keys=True).encode())
    return h.hexdigest()[:16]


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Fail as e:
        print("export_glb: %s" % e, file=sys.stderr)
        sys.exit(1)
    except Crash as e:
        print("export_glb: %s" % e, file=sys.stderr)
        sys.exit(3)
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(3)
