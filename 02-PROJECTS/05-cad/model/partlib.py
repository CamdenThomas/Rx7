"""partlib.py - the solids, the tessellation and the files every assembly shares (05-cad A04).

Two halves:
  pure (any python)   Dim, Part and mate records an assembly's params.py declares; place / offset
                      arithmetic; the colours.
  FreeCAD (freecadcmd only, imported lazily)
                      plate, strip_xz / strip_yz (a polyline thickened to a sheet and extruded),
                      loft, beam / tube / box_tube, ring_plate, revolve_xr, mirror_x; mesh() and
                      write_part_glb() (through 01-electrical's export_glb.write_glb, imported, never
                      copied); write_step().

Frame: D-418's - mm, x right, y forward, z up. A part's glb is in the part's own frame: its
`origin` point is the glb's (0, 0, 0), and its place puts that point in its parent's frame.
Owns no fact about the car: the numbers are in each assembly's params.py with their sources.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXPORT_TOOLS = os.path.join(ROOT, "02-PROJECTS", "01-electrical", "00-design", "tools")
if EXPORT_TOOLS not in sys.path:
    sys.path.insert(0, EXPORT_TOOLS)
import export_glb as G  # noqa: E402  (write_glb, face_normals, material, glb_bbox)


# ======================================================================= pure: the declarations ==
class Dim:
    """One governing dimension: its value (mm or degrees), how it is known (model_dims.how:
    measured|factory|found|catalogue|derived|guess), its source and a note. `parts` are the
    record ids it governs (model_dims.part)."""

    def __init__(self, value, how, source, note="", parts=(), label=None):
        self.value, self.how, self.source, self.note = value, how, source, note
        self.parts, self.label = list(parts), label

    def __float__(self):
        return float(self.value)

    @property
    def confirm(self):
        return self.how != "measured"


class Params(dict):
    """{key: Dim}; P.v(key) is the number."""

    def v(self, key):
        return float(self[key].value)


def part(pid, record, *, name, kind="body", origin, made_from, source, place_from, dims,
         mate=None, parent=None, rot=(0.0, 0.0, 0.0), colour="steel", zone=None, side=None,
         origin_note="", confirm_text="", note="", system=None):
    """A part as the scene and the drafts need it. `origin` is the part's origin in its parent's
    frame (the car's for a top-level part), `rot` degrees XYZ. mate: {"to", "kind", "fasteners",
    "apart": (x, y, z) car frame mm, relative to `to`, "offset": text} or None."""
    return {"id": pid, "record": record, "name": name, "kind": kind, "origin": list(origin),
            "rot": list(rot), "made_from": made_from, "source": source, "place_from": place_from,
            "dims": list(dims), "mate": mate, "parent": parent, "colour": colour, "zone": zone,
            "side": side, "origin_note": origin_note, "confirm_text": confirm_text, "note": note,
            "system": system}


COLOURS = {   # name: (rgba, metallic, roughness)
    "steel": ((0.62, 0.63, 0.65, 1.0), 0.3, 0.55),       # bare body steel, primer grey
    "floor": ((0.48, 0.50, 0.52, 1.0), 0.2, 0.7),
    "rail": ((0.36, 0.38, 0.42, 1.0), 0.3, 0.6),
    "skin": ((0.74, 0.75, 0.77, 1.0), 0.6, 0.35),        # Sunbeam Silver (00-CAR body state)
    "tyre": ((0.08, 0.08, 0.09, 1.0), 0.0, 0.9),
    "wheel": ((0.70, 0.71, 0.73, 1.0), 0.7, 0.35),
    "hub": ((0.45, 0.44, 0.42, 1.0), 0.6, 0.5),
    "nut": ((0.80, 0.78, 0.70, 1.0), 0.8, 0.3),
}


# ==================================================================== FreeCAD: the solids ======
def _fc():
    import FreeCAD  # noqa: F401
    import Part
    return FreeCAD, Part


def V(x, y, z):
    FreeCAD, _ = _fc()
    return FreeCAD.Vector(float(x), float(y), float(z))


def _offset2(pts, t):
    """A 2D polyline thickened by t to one side (its left normal): the closed outline."""
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
        else:
            ax, ay = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            bx, by = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
            la, lb = math.hypot(ax, ay) or 1, math.hypot(bx, by) or 1
            dx, dy = ax / la + bx / lb, ay / la + by / lb
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        if 0 < i < n - 1:                     # miter, capped
            ax, ay = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
            la = math.hypot(ax, ay) or 1
            c = abs(nx * (-ay / la) + ny * (ax / la))
            k = 1.0 / max(c, 0.5)
            nx, ny = nx * k, ny * k
        out.append((pts[i][0] + nx * t, pts[i][1] + ny * t))
    return list(pts) + out[::-1]


def face_from(pts3):
    _, Part = _fc()
    vs = [V(*p) for p in pts3]
    return Part.Face(Part.makePolygon(vs + [vs[0]]))


def plate(pts3, t, normal):
    """A flat outline (3D points in one plane) extruded t along the unit normal."""
    nx, ny, nz = normal
    return face_from(pts3).extrude(V(nx * t, ny * t, nz * t))


def strip_xz(profile, y0, y1, t):
    """A sheet: polyline (x, z) thickened by t, extruded along y from y0 to y1."""
    o = _offset2(profile, t)
    return face_from([(x, y0, z) for x, z in o]).extrude(V(0, y1 - y0, 0))


def strip_yz(profile, x0, x1, t):
    """A sheet: polyline (y, z) thickened by t, extruded along x from x0 to x1."""
    o = _offset2(profile, t)
    return face_from([(x0, y, z) for y, z in o]).extrude(V(x1 - x0, 0, 0))


def strip_xy(profile, z0, z1, t):
    """A sheet: polyline (x, y) thickened by t, extruded along z from z0 to z1."""
    o = _offset2(profile, t)
    return face_from([(x, y, z0) for x, y in o]).extrude(V(0, 0, z1 - z0))


def loft(sections, ruled=False):
    """Closed 3D point loops, in order, lofted into one solid."""
    _, Part = _fc()
    wires = []
    for s in sections:
        vs = [V(*p) for p in s]
        wires.append(Part.makePolygon(vs + [vs[0]]))
    try:
        return Part.makeLoft(wires, True, ruled)
    except Exception:
        return Part.makeLoft(wires, True, True)


def section_xz(y, profile, t):
    """A loft section: polyline (x, z) thickened by t at station y."""
    return [(x, y, z) for x, z in _offset2(profile, t)]


def _frame(p0, p1, up=(0, 0, 1)):
    FreeCAD, _ = _fc()
    a, b = V(*p0), V(*p1)
    d = b - a
    d.normalize()
    u = V(*up)
    if abs(d.dot(u)) > 0.95:
        u = V(1, 0, 0)
    s = d.cross(u)
    s.normalize()
    u = s.cross(d)
    u.normalize()
    return a, b, d, s, u


def _rect(c, s, u, w, h):
    return [c + s * (w / 2) + u * (h / 2), c - s * (w / 2) + u * (h / 2),
            c - s * (w / 2) - u * (h / 2), c + s * (w / 2) - u * (h / 2)]


def beam(p0, p1, w, h, up=(0, 0, 1), w1=None, h1=None):
    """A solid rectangular member from p0 to p1, w across (sideways), h up; w1/h1 taper it."""
    _, Part = _fc()
    a, b, d, s, u = _frame(p0, p1, up)
    r0 = _rect(a, s, u, w, h)
    r1 = _rect(b, s, u, w1 or w, h1 or h)
    return Part.makeLoft([Part.makePolygon(r0 + [r0[0]]), Part.makePolygon(r1 + [r1[0]])],
                         True, True)


def tube(path, w, h, up=(0, 0, 1)):
    """Solid members along a polyline, fused (joints overlap)."""
    sh = None
    for p0, p1 in zip(path[:-1], path[1:]):
        b = beam(p0, p1, w, h, up)
        sh = b if sh is None else sh.fuse(b)
    return sh.removeSplitter() if hasattr(sh, "removeSplitter") else sh


def box_tube(path, w, h, t, up=(0, 0, 1)):
    """A closed box section of wall t along a polyline: each segment's outer member less its
    inner, extended past the joints so the hollows meet."""
    sh = None
    for p0, p1 in zip(path[:-1], path[1:]):
        outer = beam(p0, p1, w, h, up)
        a, b = V(*p0), V(*p1)
        d = b - a
        ln = d.Length
        d.normalize()
        e = d * min(t * 2, ln * 0.1)
        inner = beam(tuple(a - e), tuple(b + e), w - 2 * t, h - 2 * t, up)
        seg = outer.cut(inner)
        sh = seg if sh is None else sh.fuse(seg)
    return sh


def ring_plate(outer, inner, t, normal):
    """A flat ring: outer outline less inner outline (both 3D, same plane), extruded t."""
    hole = plate(inner, t * 3, normal)
    hole.translate(V(-normal[0] * t, -normal[1] * t, -normal[2] * t))
    return plate(outer, t, normal).cut(hole)


def revolve_xr(profile, deg=360.0):
    """A closed (x, r) outline revolved about the x axis (r measured along z)."""
    _, Part = _fc()
    f = face_from([(x, 0.0, r) for x, r in profile])
    return f.revolve(V(0, 0, 0), V(1, 0, 0), deg)


def cylinder_x(r, x0, x1, at=(0, 0, 0)):
    _, Part = _fc()
    return Part.makeCylinder(r, x1 - x0, V(x0 + at[0], at[1], at[2]), V(1, 0, 0))


def mirror_x(shape):
    """The same shape on the other side of the centreline (x -> -x)."""
    return shape.mirror(V(0, 0, 0), V(1, 0, 0))


def moved(shape, dx, dy, dz):
    s = shape.copy()
    s.translate(V(dx, dy, dz))
    return s


# ============================================================ FreeCAD: tessellation and files ==
def mesh(shape, mat, linear):
    """[(material, positions, normals, indices)] one patch per face: smooth inside a face, sharp
    across faces, in the shape's own coordinates."""
    out = []
    for f in shape.Faces:
        pts, tris = f.tessellate(linear)
        if not tris:
            continue
        pos = G.array.array("f", [c for p in pts for c in (p.x, p.y, p.z)])
        idx = [i for t in tris for i in t]
        out.append((mat, pos, G.face_normals(pos, idx), idx))
    return out


def write_part_glb(path, root, nodes, linear):
    """nodes: [(node name, shape, colour name)] -> one glb, mm, z up, the part's own frame."""
    names = sorted({c for _, _, c in nodes})
    mats = [G.material(n, *COLOURS[n]) for n in names]
    ix = {n: i for i, n in enumerate(names)}
    gn = [{"name": nm, "prims": mesh(sh, ix[c], linear)} for nm, sh, c in nodes]
    return G.write_glb(path, gn, mats, root, extras={"source": "02-PROJECTS/05-cad/model"})


def write_step(path, named_shapes):
    """One STEP holding every (label, shape) as its own body, labels kept."""
    import FreeCAD
    import Import
    doc = FreeCAD.newDocument("asm")
    objs = []
    for label, sh in named_shapes:
        o = doc.addObject("Part::Feature", "p%d" % len(objs))
        o.Shape = sh
        o.Label = label
        objs.append(o)
    Import.export(objs, path)
    FreeCAD.closeDocument(doc.Name)
