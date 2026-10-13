"""FreeCAD's half of export_glb.py (02-APP D-505, work row Y23): run by freecadcmd, never by hand.
The job is a JSON file named by the environment variable RX7_EXPORT_JOB:

  kind "unit"  one unit's mock-up, built by its own unit_lib (derive, validate, build_insides,
               build_case - the same calls make_unit.py makes, so no number is typed twice and the
               geometry is the mock-up's), then written as one glb: case:<part> for each case
               part, inside:<name> for each inside solid that no child board's glb stands for.
               The keep-outs (room, not things) are left out.
  kind "pmu"   ECUMaster's PMU-24 STEP, read by FreeCAD, each face coloured as the STEP colours
               it (FreeCAD without its GUI drops colours, so they are read from the STEP text and
               matched to each shell by its faces' surface types, in order).

Writes the glb and a meta JSON (sizes, node names, the connectors and the boards' places from
the mock-up's derive()). Exit 0 written; 1 the mock-up refuses its parameters (meta.problems);
3 a crash.
"""
import json
import os
import re
import sys
import traceback

import FreeCAD  # noqa: F401
import MeshPart
import Part

JOB = json.load(open(os.environ["RX7_EXPORT_JOB"]))
sys.path.insert(0, JOB["tools_dir"])
import export_glb as G  # noqa: E402


# ------------------------------------------------------------------------------- tessellation --
def mesh_faces(shape, linear, angular, colour_of_face=None, default=0):
    """[(material, positions, normals, indices)] for a shape, one patch per face: smooth within a
    face, sharp across faces, in the shape's own coordinates (mm, z up)."""
    MeshPart.meshFromShape(Shape=shape, LinearDeflection=linear, AngularDeflection=angular,
                           Relative=False)       # puts the triangulation on the shape's faces
    out = []
    for i, f in enumerate(shape.Faces):
        pts, tris = f.tessellate(linear)        # reads the triangulation just made
        if not tris:
            continue
        pos = G.array.array("f", [c for p in pts for c in (p.x, p.y, p.z)])
        idx = [i for t in tris for i in t]
        nrm = G.face_normals(pos, idx)
        mat = colour_of_face(i, f) if colour_of_face else default
        out.append((mat, pos, nrm, idx))
    return out


def colour_key(rgb):
    return tuple(round(c, 3) for c in rgb)


# ---------------------------------------------------------------------------------- the unit --
UNIT_COLOURS = [
    ("case", (0.62, 0.64, 0.66, 1.0), 0.0, 0.7),          # printed ASA, grey
    ("face", (0.10, 0.10, 0.11, 1.0), 0.0, 0.5),          # faceplate / bezel
    ("control", (0.22, 0.22, 0.24, 1.0), 0.2, 0.4),       # knobs, keys, the page button
    ("glass", (0.03, 0.04, 0.06, 1.0), 0.1, 0.15),        # a display, a screen window
    ("board", (0.08, 0.35, 0.18, 1.0), 0.0, 0.6),         # placeholder boards
    ("connector", (0.16, 0.16, 0.17, 1.0), 0.0, 0.6),     # Deutsch bodies
    ("hardware", (0.72, 0.66, 0.45, 1.0), 0.6, 0.4),      # standoffs, bosses
    ("other", (0.55, 0.55, 0.58, 1.0), 0.0, 0.6),
]


def unit_colour(name):
    n = name.lower()
    if n.startswith("case"):
        return "case"
    if "faceplate" in n or "bezel" in n:
        return "face"
    if "screen" in n or "display" in n:
        return "glass"
    if n.startswith("control") or "button" in n:
        return "control"
    if "board" in n or "parts" in n or "bridge" in n or "scaler" in n:
        return "board"
    if "dt13" in n or "dp-" in n:
        return "connector"
    if "standoff" in n or "boss" in n:
        return "hardware"
    return "other"


def run_unit():
    d = JOB["unit_dir"]
    sys.path.insert(0, d)
    import unit_params as U
    import unit_lib as K
    meta = {"problems": [], "notes": []}
    src = K.load_source(os.path.dirname(d), U.P)
    if src["problems"]:
        meta["problems"] = src["problems"]
        return meta, 1
    problems, D, _ = K.validate(U.P, src, U)
    if problems:
        meta["problems"] = ["the mock-up refuses its parameters: " + p for p in problems]
        return meta, 1
    insides = K.build_insides(U.P, D, src)
    case, _ = K.build_case(U.P, D)
    meta["notes"] = [n for n in D.get("notes", [])]

    # which inside solids a child board stands for
    ch = JOB["children"]
    kinds = {k for c in ch.values() for k in c.get("kinds", [])}
    names = {n for c in ch.values() for n in c.get("names", [])}
    upper_refs = set()
    if any(c.get("upper_dt13") for c in ch.values()):
        upper_refs = {u.ref for u in D.get("ups", []) if u.fitted}
    keep, gone = [], []
    for it in insides:
        if it["kind"] == "keepout":
            continue
        if it["kind"] in kinds or it["name"] in names or \
                (it.get("dt13") and it.get("ref") in upper_refs):
            gone.append(it["name"])
            continue
        keep.append(it)

    mats = [G.material(n, rgba, m, r) for (n, rgba, m, r) in UNIT_COLOURS]
    mat_ix = {m["name"]: i for i, m in enumerate(mats)}
    nodes, case_names, inside_names, placeholders = [], [], [], []
    lin, ang = JOB["linear"], JOB["angular"]
    for name in sorted(case):
        nn = "case:" + name
        nodes.append({"name": nn, "prims": mesh_faces(case[name], lin, ang,
                                                      default=mat_ix["case"])})
        case_names.append(nn)
    for it in keep:
        label = it["name"].replace(": ", " ")
        nn = "inside:" + label
        nodes.append({"name": nn, "prims": mesh_faces(it["shape"], lin, ang,
                                                      default=mat_ix[unit_colour(label)])})
        inside_names.append(nn)
        if "placeholder" in label or label.startswith("control"):
            placeholders.append(label)
    info = G.write_glb(JOB["glb"], nodes, mats, JOB["id"],
                       extras={"source": os.path.relpath(d, G.ROOT)})

    conns = []
    for c in D.conns:
        if not c.get("fitted", True):
            continue
        conns.append({"code": c.name, "at": [c.X, D.y_plate1, c.Z],
                      "note": "%s, the rear plate's outer face at the cut-out's centre (%s row)"
                              % (c.part, c.get("row", "lower"))})
    boards = {}
    if hasattr(K, "export_boards"):               # a mock-up that says where its boards go (the CUR)
        boards = K.export_boards(D)
    elif "dcu-carrier" in ch:
        boards["carrier"] = {"move": list(D.step_move), "turn": 180}
        boards["panel"] = [D.px0, D.px1, D.y_panel0, D.y_panel1, D.pz0, D.pz1]
        if D.get("ups"):
            boards["upper"] = [D.ux0, D.ux1, D.uy0, D.uy1, D.uz0, D.uz1]
            boards["upper_x"] = {u.name: u.X for u in D.ups if u.fitted}
    else:
        boards["carrier"] = {"move": [D.dx, D.dy, D.cz0], "turn": 0}
    if not D.get("carrier_real", True):
        meta["notes"].append("the carrier in the mock-up was a stand-in (its STEP was not used)")
    meta.update({"bytes": info["bytes"], "bbox": info["bbox"], "vertices": info["vertices"],
                 "triangles": info["triangles"], "face": [D.face_w, D.face_h],
                 "nodes": {"case": case_names, "inside": inside_names},
                 "left_to_children": len(gone), "connectors": conns, "boards": boards,
                 "placeholders": placeholders})
    return meta, 0


# ----------------------------------------------------------------------------------- the PMU --
FC_SURF = {"Plane": "Plane", "Cylinder": "Cylinder", "Cone": "Cone", "Sphere": "Sphere",
           "Toroid": "Toroid"}
SURF = {"PLANE": "Plane", "CYLINDRICAL_SURFACE": "Cylinder", "CONICAL_SURFACE": "Cone",
        "SPHERICAL_SURFACE": "Sphere", "TOROIDAL_SURFACE": "Toroid"}


def step_shell_colours(path):
    """{surface-type signature: [colour per face]} for every shell in the STEP, from its
    STYLED_ITEMs (a face's own colour, else its solid's)."""
    txt = open(path, errors="replace").read()
    body = txt[txt.index("DATA;"):]
    ents = {}
    for m in re.finditer(r"#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|ENDSEC)", body, re.S):
        s = m.group(2).strip()
        t = re.match(r"([A-Z_0-9]+)\s*\(", s)
        ents[int(m.group(1))] = (t.group(1) if t else "COMPLEX", s)

    def refs(s):
        return [int(x) for x in re.findall(r"#(\d+)", s)]

    def colour(i, depth=0):
        t, s = ents.get(i, ("?", ""))
        if t == "COLOUR_RGB":
            return tuple(float(v) for v in re.findall(r"[-+0-9.Ee]+", s.split(",", 1)[1])[:3])
        if depth > 9:
            return None
        for r in refs(s):
            c = colour(r, depth + 1)
            if c:
                return c
        return None

    style = {}
    for i, (t, s) in ents.items():
        if t in ("STYLED_ITEM", "OVER_RIDING_STYLED_ITEM"):
            rr = refs(s)
            for r in rr[:-1]:
                c = colour(r)
                if c:
                    style[rr[-1]] = c
                    break
    owner = {}
    for i, (t, s) in ents.items():
        if t in ("MANIFOLD_SOLID_BREP", "SHELL_BASED_SURFACE_MODEL"):
            for r in refs(s):
                owner[r] = i
    out = {}
    for i, (t, s) in ents.items():
        if t not in ("CLOSED_SHELL", "OPEN_SHELL"):
            continue
        sig, cols = [], []
        for f in refs(s):
            fr = refs(ents[f][1])
            sig.append(SURF.get(ents.get(fr[-1], ("?",))[0], "other"))
            cols.append(style.get(f) or style.get(owner.get(i)) or style.get(i))
        out.setdefault(tuple(sig), cols)
    return out


def run_pmu():
    import Import
    doc = FreeCAD.newDocument("pmu")
    Import.insert(JOB["step"], doc.Name)
    shells = step_shell_colours(JOB["step"])
    default = (0.6, 0.6, 0.62)
    mats, mat_of = [], {}

    def mat(rgb):
        k = colour_key(rgb or default)
        if k not in mat_of:
            grey = abs(k[0] - k[1]) < 0.05 and abs(k[1] - k[2]) < 0.1
            mat_of[k] = len(mats)
            mats.append(G.material("c%d" % len(mats), list(k) + [1.0],
                                   0.5 if grey and k[0] > 0.6 else 0.0, 0.45))
        return mat_of[k]

    groups, order, matched, unmatched = {}, [], 0, 0
    conn_lo, conn_hi = [1e9] * 3, [-1e9] * 3
    for o in doc.Objects:
        if o.TypeId != "Part::Feature" or o.Shape.isNull():
            continue
        base = re.sub(r"(-\d+|\d{3})$", "", o.Label).strip() or o.Label
        name = "part:" + base
        if name not in groups:
            groups[name] = []
            order.append(name)
        s = o.Shape.copy()
        face_col = {}
        for sh in s.Shells:
            sig = tuple(FC_SURF.get(type(f.Surface).__name__, "other") for f in sh.Faces)
            cols = shells.get(sig)
            if cols is None:
                unmatched += 1
                continue
            matched += 1
            for f, c in zip(sh.Faces, cols):
                face_col[f.hashCode()] = c
        prims = mesh_faces(s, JOB["linear"], JOB["angular"],
                           colour_of_face=lambda i, f: mat(face_col.get(f.hashCode())))
        groups[name] += prims
        if base.lower().startswith("gniazdo"):          # ECUMaster's word: the sockets
            bb = s.BoundBox
            for k, (a, b) in enumerate(((bb.XMin, bb.XMax), (bb.YMin, bb.YMax),
                                        (bb.ZMin, bb.ZMax))):
                conn_lo[k], conn_hi[k] = min(conn_lo[k], a), max(conn_hi[k], b)
    nodes = [{"name": n, "prims": groups[n]} for n in order]
    info = G.write_glb(JOB["glb"], nodes, mats, "pmu",
                       extras={"source": os.path.relpath(JOB["step"], G.ROOT)})
    if conn_lo[0] > conn_hi[0]:
        conn_lo, conn_hi = info["bbox"]
    meta = {"problems": [], "bytes": info["bytes"], "bbox": info["bbox"],
            "vertices": info["vertices"], "triangles": info["triangles"],
            "nodes": {"parts": [n["name"] for n in nodes]},
            "connector_box": [conn_lo, conn_hi],
            "notes": ["colours matched to %d shells from the STEP, %d left grey"
                      % (matched, unmatched)],
            "tessellation": {"linear_mm": JOB["linear"], "angular_rad": JOB["angular"]}}
    return meta, 0


try:
    meta, rc = run_unit() if JOB["kind"] == "unit" else run_pmu()
    with open(JOB["meta"], "w") as fh:
        json.dump(meta, fh)
except Exception:
    traceback.print_exc()
    rc = 3
sys.stdout.flush()
sys.stderr.flush()
os._exit(rc)
