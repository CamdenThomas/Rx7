"""FreeCAD's half of harness_devices.py (D-515, work row Y28): run by freecadcmd, never by hand.
The job is a JSON file named by the environment variable RX7_DEVICES_JOB, a list of models:

  kind "step"   a found model's STEP (or a STEP inside a zip), read by FreeCAD, turned by `rot`,
                its box's base centre moved to the origin; one node per top-level part,
                part:<label>, each face coloured as the STEP colours it, else the model's `mat`
  kind "prims"  a stand-in: boxes, cylinders, cones and hexagons, one node per named primitive,
                standin:<name>

Each is written as a glb (mm, z up, the part's own frame) by export_glb.py's write_glb, and
tessellated by export_glb_fc.py's mesh_faces with its STEP colour reader (taken from that file's
source, since running it would run its own job) - one implementation each. Writes a meta JSON
{model: {bytes, bbox, vertices, triangles, nodes, notes}}. Exit 0 written; 3 a crash.
"""
import ast
import json
import os
import re
import sys
import traceback
import zipfile

import FreeCAD
import MeshPart
import Part

JOB = json.load(open(os.environ["RX7_DEVICES_JOB"]))
sys.path.insert(0, JOB["tools_dir"])
import export_glb as G  # noqa: E402

V = FreeCAD.Vector


def _borrow(path, names):
    """The named functions and assignments of a module, without running the module."""
    tree = ast.parse(open(path).read())
    keep = [n for n in tree.body
            if (isinstance(n, ast.FunctionDef) and n.name in names)
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", None) in names
                                                  for t in n.targets))]
    ns = {"G": G, "MeshPart": MeshPart, "re": re}
    exec(compile(ast.Module(body=keep, type_ignores=[]), path, "exec"), ns)
    return ns


FC = _borrow(os.path.join(JOB["tools_dir"], "export_glb_fc.py"),
             {"mesh_faces", "colour_key", "step_shell_colours", "FC_SURF", "SURF"})
AXES = {"x": V(1, 0, 0), "-x": V(-1, 0, 0), "y": V(0, 1, 0), "-y": V(0, -1, 0),
        "z": V(0, 0, 1), "-z": V(0, 0, -1)}


def materials():
    mats = [G.material(n, rgba, m, r) for n, (rgba, m, r) in JOB["mats"].items()]
    return mats, {m["name"]: i for i, m in enumerate(mats)}


# --------------------------------------------------------------------------------- stand-ins --
def prim_shape(kind, a):
    if kind == "box":
        return Part.makeBox(a[3], a[4], a[5], V(a[0], a[1], a[2]))
    if kind == "cyl":
        return Part.makeCylinder(a[3], a[4], V(a[0], a[1], a[2]), AXES[a[5]])
    if kind == "cone":
        return Part.makeCone(a[3], a[4], a[5], V(a[0], a[1], a[2]), AXES[a[6]])
    if kind == "hex":
        import math
        r = a[3] / 2.0 / math.cos(math.pi / 6)
        pts = [V(a[0] + r * math.cos(math.pi / 3 * k), a[1] + r * math.sin(math.pi / 3 * k), a[2])
               for k in range(7)]
        return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, a[4]))
    raise ValueError("no primitive %r" % kind)


def build_prims(j):
    mats, ix = materials()
    nodes, order = {}, []
    for kind, node, mat, a in j["prims"]:
        nn = "standin:" + node
        if nn not in nodes:
            nodes[nn] = []
            order.append(nn)
        nodes[nn] += FC["mesh_faces"](prim_shape(kind, a), 0.05, 0.2, default=ix[mat])
    info = G.write_glb(j["glb"], [{"name": n, "prims": nodes[n]} for n in order], mats,
                       j["name"], extras={"source": "harness_devices.py STANDINS",
                                          "standin": True})
    return dict(info, nodes=order, notes=[])


# ------------------------------------------------------------------------------- found STEPs --
def build_step(j):
    import Import
    path = j["path"]
    if j.get("member"):
        with zipfile.ZipFile(path) as z:
            z.extract(j["member"], JOB["tmp"])
        path = os.path.join(JOB["tmp"], j["member"])
    doc = FreeCAD.newDocument("dev")
    Import.insert(path, doc.Name)
    groups = []
    for root in [o for o in doc.Objects if not o.InList]:
        if root.TypeId == "App::Part":
            for c in root.Group:
                if c.InList == [root]:
                    s = Part.getShape(c)
                    if not s.isNull() and s.Faces:
                        s.Placement = root.Placement.multiply(s.Placement)
                        groups.append((c.Label, s))
        else:
            s = Part.getShape(root)
            if not s.isNull() and s.Faces:
                groups.append((root.Label, s))
    rx, ry, rz = j["rot"]
    mtx = FreeCAD.Matrix()
    mtx.rotateX(rx * 3.141592653589793 / 180.0)
    mtx.rotateY(ry * 3.141592653589793 / 180.0)
    mtx.rotateZ(rz * 3.141592653589793 / 180.0)
    turned = []
    bb = None
    for label, s in groups:
        s = s.copy()
        s.transformShape(mtx)
        turned.append((label, s))
        bb = s.BoundBox if bb is None else bb.united(s.BoundBox)
    move = V(-(bb.XMin + bb.XMax) / 2.0, -(bb.YMin + bb.YMax) / 2.0, -bb.ZMin)
    shells = FC["step_shell_colours"](path)
    mats, ix = materials()
    of = {}
    default = j["mat"]

    def mat(rgb):
        if rgb is None:
            return ix[default]
        k = FC["colour_key"](rgb)
        if k not in of:
            of[k] = len(mats)
            mats.append(G.material("c%d" % len(mats), list(k) + [1.0], 0.0, 0.5))
        return of[k]

    nodes, matched, unmatched = {}, 0, 0
    order = []
    for label, s in turned:
        s.translate(move)
        face_col = {}
        for sh in s.Shells:
            sig = tuple(FC["FC_SURF"].get(type(f.Surface).__name__, "other") for f in sh.Faces)
            cols = shells.get(sig)
            if cols is None:
                unmatched += 1
                continue
            matched += 1
            for f, c in zip(sh.Faces, cols):
                face_col[f.hashCode()] = c
        name = "part:" + re.sub(r"\s+", " ", label).strip()
        if name not in nodes:
            nodes[name] = []
            order.append(name)
        nodes[name] += FC["mesh_faces"](s, j["linear"], j["angular"],
                                        colour_of_face=lambda i, f: mat(face_col.get(f.hashCode())))
    info = G.write_glb(j["glb"], [{"name": n, "prims": nodes[n]} for n in order], mats,
                       j["name"], extras={"source": os.path.basename(j["path"]),
                                          "standin": False})
    FreeCAD.closeDocument(doc.Name)
    return dict(info, nodes=order,
                notes=["colours matched to %d shells from the STEP, %d left %s"
                       % (matched, unmatched, default)])


try:
    meta = {}
    for j in JOB["jobs"]:
        meta[j["name"]] = build_step(j) if j["kind"] == "step" else build_prims(j)
    with open(JOB["meta"], "w") as fh:
        json.dump(meta, fh)
    rc = 0
except Exception:
    traceback.print_exc()
    rc = 3
sys.stdout.flush()
sys.stderr.flush()
os._exit(rc)
