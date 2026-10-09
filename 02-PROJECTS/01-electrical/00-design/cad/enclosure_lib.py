"""The parametric enclosures for the three boards (Y7, D-455): shared geometry, probe and fit check.

Run through FreeCAD's headless interpreter by each board's `enclosure/make_enclosure.py`, never on its
own. Three inputs, nothing typed:

- `board.json`  the board's outline, holes and footprints, written from the `.kicad_pcb` by
                `../enclosure_extract.py` (KiCad's Python);
- `probe.json`  what only the 3D model knows - the tallest part top and bottom, the DT13 flange
                front face, each housing's section where it passes the wall, TE's flange seal and
                the flange itself - read from the board STEP (`<board>.step`, gitignored) whenever it
                is present and cached here, so the enclosure still rebuilds on a clone without it;
- the parameters at the top of `make_enclosure.py` (walls, inserts, screws, the placing envelope).

Frame: the STEP export's, mm - x as KiCad, y = -y(KiCad), z up, the board's bottom face at z = 0.
The parts are written in that frame, so they open on top of the board STEP.

Owns no fact in the record: the measurements that place each box are work rows C4, V-102 and V-113
(`01-electrical/data/work.csv`), the parts are P111 / P152 / P122 / P150 (`parts.csv`), and the
DT13 panel cut-outs are TE application spec 114-151046 Rev A, 3.5 Panel Cutout (pp.7-8), option 2.
"""
import json
import math
import os

import FreeCAD
import Part
import Mesh
from FreeCAD import Vector as V

# --- TE 114-151046 Rev A, 3.5 Panel Cutout, option 2 (p.7: 6P; p.8: 8P, 12P), tolerance +-0.12 ---
# width, height, corner radius of the rounded-rectangle opening; screw-hole spacing; hole diameter.
# 3.11 (p.10): #6-19 thread-forming screws (Plastite 48), 1.24-1.46 Nm, panel 6.25 mm max.
TE_CUTOUT = {
    "DT13-06PA": {"w": 25.17, "h": 21.84, "r": 6.35, "pitch": 32.89, "hole": 3.94, "page": 7},
    "DT13-08PA": {"w": 37.47, "h": 23.77, "r": 6.35, "pitch": 45.21, "hole": 3.94, "page": 8},
    "DT13-12PA": {"w": 41.58, "h": 23.27, "r": 6.35, "pitch": 49.33, "hole": 3.94, "page": 8},
}
TE_PANEL_MAX = 6.25
CONTACT = 0.02   # mm: an overlap thinner than this is two faces touching, not an interference


# ------------------------------------------------------------------------------------------ io --
def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
        f.write("\n")


def fp(board, ref):
    for f in board["footprints"]:
        if f["ref"] == ref:
            return f
    raise KeyError(ref)


def cy_centre(f):
    c = f["courtyard"]
    return (c[0] + c[1]) / 2.0, (c[2] + c[3]) / 2.0


def is_dt13(f):
    return f["footprint"].startswith("DT13-")


# --------------------------------------------------------------------------------------- probe --
def _bb(shapes):
    bb = None
    for s in shapes:
        if bb is None:
            bb = FreeCAD.BoundBox(s.BoundBox)
        else:
            bb.add(s.BoundBox)
    return bb


def _in_box(x, y, box, m=0.0):
    return box[0] - m <= x <= box[1] + m and box[2] - m <= y <= box[3] + m


def _planar_y_faces(solid):
    out = {}
    for f in solid.Faces:
        b = f.BoundBox
        if b.YLength < 1e-3 and f.Area > 20:
            out.setdefault(round(b.YMin, 3), []).append(f)
    return out


def probe(board, step_path, cache_path):
    """Read the board STEP into probe.json; without the STEP, return the cached probe."""
    if not os.path.exists(step_path):
        if not os.path.exists(cache_path):
            raise SystemExit("no %s and no cached %s: export the STEP first (board README)"
                             % (step_path, cache_path))
        print("probe: %s absent - using the cached %s" % (os.path.basename(step_path),
                                                          os.path.basename(cache_path)))
        return load(cache_path)
    shape = Part.read(step_path)
    solids = shape.Solids
    o = board["outline"]
    board_solid = max(solids, key=lambda s: s.BoundBox.XLength * s.BoundBox.YLength
                      if s.BoundBox.ZLength < 2.0 else 0)
    parts = [s for s in solids if s is not board_solid]
    pr = {"step": os.path.basename(step_path), "board_top": round(board_solid.BoundBox.ZMax, 3),
          "dt13": {}, "refs": {}}
    # every DT13 receptacle: flange front face, TE's flange seal, the housing at the wall
    dt_solids = set()
    for f in board["footprints"]:
        if not is_dt13(f) or f["dnp"]:
            continue
        cands = [s for s in parts if s.BoundBox.ZMax > 20 and
                 _in_box(s.BoundBox.Center.x, s.BoundBox.Center.y, f["courtyard"], 2.0)]
        if not cands:
            pr["dt13"][f["ref"]] = {"model": False}
            continue
        s = max(cands, key=lambda s: s.Volume)
        dt_solids.add(id(s))
        b = s.BoundBox
        outward = +1 if b.YMax > o["ymax"] + 3 else -1
        faces = _planar_y_faces(s)
        edge = o["ymax"] if outward > 0 else o["ymin"]
        # the flange's front face: of the planar Y faces whose outline is the whole flange (within
        # 5 % of the largest), the most outward one; the seal is the next face outward (TE's VMQ
        # flange seal). The board edge does not decide it: the footprints put it on the flange's
        # rear face, the ICU's models on its front face (F11 measures which).
        def outline(y):
            bb = _bb(faces[y])
            return bb.XLength * bb.ZLength
        top = max(outline(y) for y in faces)
        y_flange = max([y for y in faces if outline(y) >= 0.95 * top], key=lambda y: y * outward)
        beyond = sorted([y for y in faces if (y - y_flange) * outward > 0.05],
                        key=lambda y: abs(y - y_flange))
        y_seal = beyond[0] if beyond else y_flange
        fb, sb = _bb(faces[y_flange]), _bb(faces[y_seal])
        # the housing where it crosses the wall: a section 2 mm outside the seal face
        ysec = y_seal + 2.0 * outward
        wires = s.slice(V(0, 1, 0), ysec)
        hb = _bb(wires)
        # the flange's screw holes, from a section through the flange itself
        holes = sorted({(round(e.Curve.Center.x, 2), round(e.Curve.Center.z, 2))
                        for w in s.slice(V(0, 1, 0), y_flange - 0.5 * outward) for e in w.Edges
                        if isinstance(e.Curve, Part.Circle) and 1.5 < e.Curve.Radius < 2.6})
        pr["dt13"][f["ref"]] = {
            "model": True, "outward": outward, "y_flange": round(y_flange, 3),
            "y_seal": round(y_seal, 3), "flange_front_past_board_edge": round((y_flange - edge) * outward, 3), "y_tip": round(b.YMax if outward > 0 else b.YMin, 3),
            "flange": [round(v, 3) for v in (fb.XMin, fb.XMax, fb.ZMin, fb.ZMax)],
            "seal": [round(v, 3) for v in (sb.XMin, sb.XMax, sb.ZMin, sb.ZMax)],
            "housing": [round(v, 3) for v in (hb.XMin, hb.XMax, hb.ZMin, hb.ZMax)],
            "flange_holes": holes,
            "pin_field_x": f["x"],
        }
    # everything else: the box the parts fill (DT13s only up to their flange front face)
    inner = [s for s in parts if id(s) not in dt_solids]
    ib = _bb(inner + [board_solid])
    xs = [ib.XMin, ib.XMax]
    ys = [ib.YMin, ib.YMax]
    for ref, d in pr["dt13"].items():
        if d.get("model"):
            xs += [d["flange"][0], d["flange"][1]]
    zt = [s.BoundBox.ZMax for s in parts]
    zb = [s.BoundBox.ZMin for s in parts]
    pr["content"] = {"xmin": round(min(xs), 3), "xmax": round(max(xs), 3),
                     "ymin": round(min(ys), 3), "ymax": round(max(ys), 3),
                     "ztop": round(max(zt), 3), "zbottom": round(min(zb), 3),
                     "ztop_without_dt13": round(max(s.BoundBox.ZMax for s in inner), 3)}
    # per-footprint 3D extents for the refs the enclosure places features on
    for f in board["footprints"]:
        mine = [s for s in parts if _in_box(s.BoundBox.Center.x, s.BoundBox.Center.y,
                                             f["courtyard"])]
        if mine and (f["ref"][0] in "JU" or f["ref"].startswith("SW")):
            b = _bb(mine)
            pr["refs"][f["ref"]] = [round(v, 3) for v in (b.XMin, b.XMax, b.YMin, b.YMax,
                                                          b.ZMin, b.ZMax)]
    save(cache_path, pr)
    print("probe: read %s (%d solids) -> %s" % (os.path.basename(step_path), len(solids),
                                                os.path.basename(cache_path)))
    return pr


# ---------------------------------------------------------------------------------- primitives --
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, x, y, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def rrect_face(w, h, r):
    """A rounded rectangle centred on the origin in the XY plane."""
    r = min(r, w / 2.0 - 1e-3, h / 2.0 - 1e-3)
    if r <= 0:
        return Part.Face(Part.makePolygon([V(-w / 2, -h / 2, 0), V(w / 2, -h / 2, 0),
                                           V(w / 2, h / 2, 0), V(-w / 2, h / 2, 0),
                                           V(-w / 2, -h / 2, 0)]))
    a, b = w / 2.0, h / 2.0
    e = []
    e.append(Part.LineSegment(V(-a + r, -b, 0), V(a - r, -b, 0)).toShape())
    e.append(Part.ArcOfCircle(Part.Circle(V(a - r, -b + r, 0), V(0, 0, 1), r), -math.pi / 2, 0).toShape())
    e.append(Part.LineSegment(V(a, -b + r, 0), V(a, b - r, 0)).toShape())
    e.append(Part.ArcOfCircle(Part.Circle(V(a - r, b - r, 0), V(0, 0, 1), r), 0, math.pi / 2).toShape())
    e.append(Part.LineSegment(V(a - r, b, 0), V(-a + r, b, 0)).toShape())
    e.append(Part.ArcOfCircle(Part.Circle(V(-a + r, b - r, 0), V(0, 0, 1), r), math.pi / 2, math.pi).toShape())
    e.append(Part.LineSegment(V(-a, b - r, 0), V(-a, -b + r, 0)).toShape())
    e.append(Part.ArcOfCircle(Part.Circle(V(-a + r, -b + r, 0), V(0, 0, 1), r), math.pi, 1.5 * math.pi).toShape())
    return Part.Face(Part.Wire(e))


def rrect_prism(w, h, r, x, y, z0, z1):
    f = rrect_face(w, h, r)
    s = f.extrude(V(0, 0, z1 - z0))
    s.translate(V(x, y, z0))
    return s


def rrect_xz(w, h, r, x, z, y0, y1):
    """A rounded rectangle in the XZ plane at (x, z), extruded from y0 to y1."""
    f = rrect_face(w, h, r)
    s = f.extrude(V(0, 0, y1 - y0))
    s.rotate(V(0, 0, 0), V(1, 0, 0), -90)   # local z -> +y, local y -> z
    s.translate(V(x, y0, z))
    return s


def cyl_y(r, x, z, y0, y1):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cyl_x(r, y, z, x0, x1):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def ring(outer, inner):
    return outer.cut(inner)


def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()


def cut(s, tools):
    for t in tools:
        s = s.cut(t)
    return s.removeSplitter()


# ------------------------------------------------------------------------- the carrier boxes --
def build_carrier(P, board, pr):
    """ICU / DCU: base (floor + three walls), the connector plate (the fourth wall, where the
    DT13s mount to TE's panel spec), and the lid. Built with the connector face toward +y; a board
    whose DT13s face -y is built the same way and turned 180 degrees about its centre."""
    o = board["outline"]
    dts = [f for f in board["footprints"] if is_dt13(f) and not f["dnp"]]
    known = [pr["dt13"][f["ref"]] for f in dts if pr["dt13"].get(f["ref"], {}).get("model")]
    outward = known[0]["outward"]
    cx, cy = (o["xmin"] + o["xmax"]) / 2.0, (o["ymin"] + o["ymax"]) / 2.0

    def lx(x):
        return x if outward > 0 else 2 * cx - x

    def ly(y):
        return y if outward > 0 else 2 * cy - y

    def lxx(a, b):
        return (min(lx(a), lx(b)), max(lx(a), lx(b)))

    def lyy(a, b):
        return (min(ly(a), ly(b)), max(ly(a), ly(b)))

    c = pr["content"]
    W, FT, LT, PT = P["WALL"], P["FLOOR"], P["LID"], P["PLATE"]
    G = P["GAP"]
    ref_dt = known[0]
    # the plate's inner face is the DT13 flange's front face (TE's seal is squeezed by the screws)
    y_in = ly(ref_dt["y_flange"]) - P["SEAL_SQUEEZE_OFFSET"]
    x0, x1 = lxx(c["xmin"], c["xmax"])
    y0, _ = lyy(c["ymin"], c["ymax"])
    ix0, ix1, iy0, iy1 = x0 - G, x1 + G, y0 - G, y_in
    zf = -P["BOSS_H"]                               # floor's inner face
    zc = c["ztop"] + P["TOP_GAP"]                   # wall top = lid underside
    zb = zf - FT                                    # base bottom
    lip = P["PLATE_LIP"]
    yend = iy1 + PT + lip                           # outer end of the side walls
    sd, sc = P["SLOT_DEPTH"], P["SLOT_CLEAR"]
    info = {"interior": [ix0, ix1, iy0, iy1, zf, zc]}

    # ---- base: floor and walls, open at the connector end; slots that take the plate
    base = box(ix0 - W, ix1 + W, iy0 - W, yend, zb, zc)
    blocks = []
    for xs in (ix0 - W - P["SLOT_BLOCK"], ix1 + W):
        blocks.append(box(xs, xs + P["SLOT_BLOCK"], iy1 - 4.0, yend, zb, zc))
    # lid-screw lugs outside the two side walls, near each end
    lug_r = P["LUG_D"] / 2.0
    lug_pts = []
    for x in (ix0 - W - lug_r + 1.5, ix1 + W + lug_r - 1.5):
        for y in (iy0 + 3.0, iy1 - 4.0 - lug_r - 0.5):
            lug_pts.append((x, y))
            blocks.append(cyl(lug_r, x, y, zb, zc))
    # mounting tabs to the car, at floor level on the side walls
    tabs = []
    for side, frac in P["TABS"]:
        y = iy0 + frac * (iy1 - iy0)
        if side == "left":
            t = box(ix0 - W - P["TAB_L"], ix0 - W + 0.01, y - P["TAB_W"] / 2, y + P["TAB_W"] / 2, zb, zb + FT)
            hx = ix0 - W - P["TAB_L"] / 2.0
        else:
            t = box(ix1 + W - 0.01, ix1 + W + P["TAB_L"], y - P["TAB_W"] / 2, y + P["TAB_W"] / 2, zb, zb + FT)
            hx = ix1 + W + P["TAB_L"] / 2.0
        blocks.append(t)
        tabs.append((hx, y))
    base = fuse([base] + blocks)
    cuts = [box(ix0, ix1, iy0, yend + 1, zf, zc + 1)]
    # the plate's channel: into both side walls and the floor
    cuts.append(box(ix0 - sd, ix1 + sd, iy1 - sc / 2, iy1 + PT + sc / 2, zf - P["FLOOR_GROOVE"], zc + 1))
    # floor beyond the plate stays as the lip; the end above the floor is open
    for (x, y) in lug_pts:
        cuts.append(cyl(P["INSERT_BORE"] / 2.0, x, y, zc - P["INSERT_DEPTH"], zc + 1))
    for (x, y) in tabs:
        cuts.append(cyl(P["TAB_HOLE"] / 2.0, x, y, zb - 1, zb + FT + 1))
    base = cut(base, cuts)
    # the board's bosses, from its M3 holes
    bosses, bores = [], []
    holes = [h for h in board["holes"] if h["ref"].startswith("H")]
    for h in holes:
        x, y = lx(h["x"]), ly(h["y"])
        bosses.append(cyl(P["BOSS_D"] / 2.0, x, y, zf - 0.01, 0.0))
        bores.append(cyl(P["INSERT_BORE"] / 2.0, x, y, -P["INSERT_DEPTH"], 0.5))
    base = cut(fuse([base] + bosses), bores)

    # ---- the grommet face (-y in this frame): grommet holes and the ribbon notch
    gcuts = []
    gz = []
    for g in P["GROMMETS"]:
        ref, z = (g, P["GROMMET_Z"]) if isinstance(g, str) else g
        f = fp(board, ref)
        x = lx(cy_centre(f)[0])
        gcuts.append(cyl_y(P["GROMMET_HOLE"] / 2.0, x, z, iy0 - W - 1, iy0 + 1))
        gz.append((ref, round(cy_centre(f)[0], 2), z))
    rib = fp(board, P["RIBBON_REF"])
    rx = lx(cy_centre(rib)[0])
    rw = P["RIBBON_WAYS"] * 1.27 + 2 * P["RIBBON_SIDE_CLEAR"]
    gcuts.append(box(rx - rw / 2, rx + rw / 2, iy0 - W - 1, iy0 + 1, zc - P["NOTCH_DEPTH"], zc + 1))
    base = cut(base, gcuts)
    info["grommets"] = gz
    gx = cy_centre(rib)[0]
    info["ribbon_notch"] = {"x": [round(gx - rw / 2, 2), round(gx + rw / 2, 2)],
                            "z": [round(zc - P["NOTCH_DEPTH"], 2), round(zc, 2)]}

    # ---- RF window (ICU): a thin solid wall, no metal and no infill, outside the antenna end
    rf = None
    if P.get("RF_REF"):
        f = fp(board, P["RF_REF"])
        b = pr["refs"].get(P["RF_REF"])
        ky = P["RF_KEEPOUT"]
        ya, yb = lyy(b[2], b[3])
        rf_side = P["RF_SIDE"]
        zt = b[5] + ky
        za = max(zf + 0.5, -ky)
        ya, yb = ya - ky, yb + ky
        if rf_side == "left":
            pocket = box(ix0 - W - 1, ix0 - P["RF_WALL"], ya, yb, za, zt)
            wall_x = ix0 - P["RF_WALL"]
        else:
            pocket = box(ix1 + P["RF_WALL"], ix1 + W + 1, ya, yb, za, zt)
            wall_x = ix1 + P["RF_WALL"]
        base = cut(base, [pocket])
        rf = {"side": rf_side, "y": [round(ya, 2), round(yb, 2)], "z": [round(za, 2), round(zt, 2)],
              "x_wall": round(wall_x, 2), "wall": P["RF_WALL"]}
        # metal near the window: every insert and screw, and the tabs' car screws
        metal = [("board insert " + h["ref"], lx(h["x"]), ly(h["y"]), -P["INSERT_DEPTH"], 0.0)
                 for h in holes]
        metal += [("lid insert", x, y, zc - P["INSERT_DEPTH"], zc) for (x, y) in lug_pts]
        metal += [("tab screw", x, y, zb, zb + FT) for (x, y) in tabs]
        near = []
        for name, x, y, za_, zb_ in metal:
            dx = max(0.0, abs(x - wall_x) - P["INSERT_BORE"] / 2)
            dy = max(0.0, ya - y, y - yb) - P["INSERT_BORE"] / 2
            dz = max(0.0, za - zb_, za_ - zt)
            d = math.sqrt(max(0, dx) ** 2 + max(0, dy) ** 2 + dz ** 2)
            near.append((round(d, 1), name))
        rf["nearest_metal"] = sorted(near)[0]
        info["rf"] = rf

    # ---- the connector plate
    pz0 = zf - P["FLOOR_GROOVE"] + sc / 2
    plate = box(ix0 - sd + sc / 2, ix1 + sd - sc / 2, iy1, iy1 + PT, pz0, zc)
    pcuts, cutinfo = [], []
    for f in dts:
        te = TE_CUTOUT[f["footprint"]]
        d = pr["dt13"].get(f["ref"], {})
        if d.get("model") and P["CUTOUT_ON"] == "model":
            hx = (d["housing"][0] + d["housing"][1]) / 2.0
            hz = (d["housing"][2] + d["housing"][3]) / 2.0
            src = "housing section of TE's model"
        else:
            # no model (or told to): the pin field's centre, at the height of a modelled housing
            hx = f["x"]
            hz = (ref_dt["housing"][2] + ref_dt["housing"][3]) / 2.0
            src = "pin field centre, housing height from %s" % ("a modelled DT13")
        x = lx(hx)
        pcuts.append(rrect_xz(te["w"] + 2 * P["CUTOUT_CLEAR"], te["h"] + 2 * P["CUTOUT_CLEAR"], te["r"],
                              x, hz, iy1 - 1, iy1 + PT + 1))
        for s in (-1, 1):
            pcuts.append(cyl_y(te["hole"] / 2.0, x + s * te["pitch"] / 2.0, hz, iy1 - 1, iy1 + PT + 1))
        ci = {"ref": f["ref"], "part": f["footprint"], "x": round(hx, 2), "z": round(hz, 2),
              "w": te["w"], "h": te["h"], "r": te["r"], "pitch": te["pitch"], "hole": te["hole"],
              "page": te["page"], "from": src, "pin_field_x": f["x"]}
        if d.get("model"):
            hw = d["housing"][1] - d["housing"][0]
            hh = d["housing"][3] - d["housing"][2]
            ci["housing_wh"] = [round(hw, 2), round(hh, 2)]
            ci["clear_per_side"] = [round((te["w"] - hw) / 2, 2), round((te["h"] - hh) / 2, 2)]
            ci["model_offset_from_pins"] = round(hx - f["x"], 2)
            if d["flange_holes"]:
                hxs = sorted(h[0] for h in d["flange_holes"])
                ci["model_flange_hole_pitch"] = round(hxs[-1] - hxs[0], 2)
                ci["model_flange_hole_z"] = d["flange_holes"][0][1]
        cutinfo.append(ci)
    plate = cut(plate, pcuts)
    info["cutouts"] = cutinfo
    # the plate's top corners must clear the lugs' inserts: nothing to do, they are outside

    # ---- lid: over the outer box and the lugs; the gasket groove on the wall's centre line,
    #      across the plate; the tongue that closes the ribbon notch onto the ribbon
    lo = [box(ix0 - W, ix1 + W, iy0 - W, yend, zc, zc + LT)]
    for xs in (ix0 - W - P["SLOT_BLOCK"], ix1 + W):
        lo.append(box(xs, xs + P["SLOT_BLOCK"], iy1 - 4.0, yend, zc, zc + LT))
    for (x, y) in lug_pts:
        lo.append(cyl(lug_r, x, y, zc, zc + LT))
    lid = fuse(lo)
    gw, gd = P["GASKET_GROOVE_W"], P["GASKET_GROOVE_D"]
    mx0, mx1 = ix0 - W / 2.0, ix1 + W / 2.0
    my0, my1 = iy0 - W / 2.0, iy1 + PT / 2.0
    outer = rrect_prism(mx1 - mx0 + gw, my1 - my0 + gw, P["GASKET_R"] + gw / 2,
                        (mx0 + mx1) / 2, (my0 + my1) / 2, zc - 0.01, zc + gd)
    inner = rrect_prism(mx1 - mx0 - gw, my1 - my0 - gw, max(0.5, P["GASKET_R"] - gw / 2),
                        (mx0 + mx1) / 2, (my0 + my1) / 2, zc - 0.02, zc + gd + 0.01)
    lid = cut(lid, [outer.cut(inner)])
    lid = cut(lid, [cyl(P["SCREW_CLEAR"] / 2.0, x, y, zc - 1, zc + LT + 1) for (x, y) in lug_pts])
    tongue = box(rx - rw / 2 + P["TONGUE_CLEAR"], rx + rw / 2 - P["TONGUE_CLEAR"], iy0 - W + 0.2, iy0 - 0.2,
                 zc - P["NOTCH_DEPTH"] + P["RIBBON_GAP"], zc + 0.01)
    lid = fuse([lid, tongue])
    if P.get("LID_VENTS"):
        vents = []
        n = P["LID_VENTS"]
        for i in range(n):
            x = ix0 + 15 + i * (ix1 - ix0 - 30) / max(1, n - 1)
            vents.append(box(x - 1.0, x + 1.0, iy0 + 15, iy1 - 15, zc - 1, zc + LT + 1))
        lid = cut(lid, vents)

    parts = {"base": base, "plate": plate, "lid": lid}
    if outward < 0:
        for k in parts:
            parts[k].rotate(V(cx, cy, 0), V(0, 0, 1), 180)
    info["outer"] = _outer(parts)
    info["box_no_tabs"] = [round(ix1 - ix0 + 2 * W, 2), round(yend - (iy0 - W), 2),
                           round(zc + LT - zb, 2)]
    info["lugs"] = len(lug_pts)
    info["tabs"] = len(tabs)
    info["outward"] = outward
    return parts, info


# ------------------------------------------------------------------------------ the panel mount --
def build_panel(P, board, pr):
    """Control panel (H-008): a rear tray behind the board and a front frame between the board and
    the faceplate. Four M3 bolts from the faceplate pass the frame's standoffs and the board into
    heat-set inserts in the tray's bosses; the frame's lip tabs are the alternative hang on the
    opening's lip (V-113)."""
    o = board["outline"]
    c = pr["content"]
    W, FT, G = P["WALL"], P["FLOOR"], P["GAP"]
    bt = pr["board_top"]
    ix0, ix1 = min(o["xmin"], c["xmin"]) - G + 0.05, max(o["xmax"], c["xmax"]) + G - 0.05
    iy0, iy1 = min(o["ymin"], c["ymin"]) - G + 0.05, max(o["ymax"], c["ymax"]) + G - 0.05
    r_in = o["corner_r"] + G
    cx, cy = (ix0 + ix1) / 2.0, (iy0 + iy1) / 2.0
    w, h = ix1 - ix0, iy1 - iy0
    back = max(-c["zbottom"] + P["BACK_GAP"], P["BACK_MIN"])
    zf = -back
    zb = zf - FT
    tray = rrect_prism(w + 2 * W, h + 2 * W, r_in + W, cx, cy, zb, bt)
    tray = tray.cut(rrect_prism(w, h, r_in, cx, cy, zf, bt + 1))
    holes = [hh for hh in board["holes"] if hh["ref"].startswith("H")]
    tray = fuse([tray] + [cyl(P["BOSS_D"] / 2.0, hh["x"], hh["y"], zf - 0.01, 0.0) for hh in holes])
    cuts = [cyl(P["INSERT_BORE"] / 2.0, hh["x"], hh["y"], -P["INSERT_DEPTH"], 0.5) for hh in holes]
    # the ribbon: the 20-way IDC plug passes the floor under J1
    j1 = fp(board, P["RIBBON_REF"])["courtyard"]
    m = P["RIBBON_SLOT_MARGIN"]
    cuts.append(box(j1[0] - m, j1[1] + m, j1[2] - m, j1[3] + m, zb - 1, zf + 1))
    # grommets in the floor under each lead
    for ref in P["GROMMETS"]:
        x, y = cy_centre(fp(board, ref))
        cuts.append(cyl(P["GROMMET_HOLE"] / 2.0, x, y, zb - 1, zf + 1))
    tray = cut(tray, cuts)
    # the front frame: a ring from the board's top face to the faceplate's back, the four standoffs
    zt = bt + P["STANDOFF_FRONT"]
    frame = rrect_prism(w + 2 * W, h + 2 * W, r_in + W, cx, cy, bt, zt)
    frame = frame.cut(rrect_prism(w, h, r_in, cx, cy, bt - 1, zt + 1))
    adds = []
    for hh in holes:
        adds.append(cyl(P["STANDOFF_D"] / 2.0, hh["x"], hh["y"], bt, zt))
        # a web from each standoff out to the ring
        ex = ix0 if hh["x"] < cx else ix1
        ey = iy0 if hh["y"] < cy else iy1
        adds.append(box(min(hh["x"], ex), max(hh["x"], ex), hh["y"] - P["WEB"] / 2, hh["y"] + P["WEB"] / 2, bt, zt))
        adds.append(box(hh["x"] - P["WEB"] / 2, hh["x"] + P["WEB"] / 2, min(hh["y"], ey), max(hh["y"], ey), bt, zt))
    tabs = []
    for (side, frac) in P["LIP_TABS"]:
        if side in ("left", "right"):
            y = iy0 + frac * h
            x0 = ix0 - W - P["LIP_TAB_L"] if side == "left" else ix1 + W
            adds.append(box(x0, x0 + P["LIP_TAB_L"], y - P["LIP_TAB_W"] / 2, y + P["LIP_TAB_W"] / 2,
                            zt - P["LIP_TAB_T"], zt))
            tabs.append((x0 + P["LIP_TAB_L"] / 2.0, y, "x"))
        else:
            x = ix0 + frac * w
            y0 = iy0 - W - P["LIP_TAB_L"] if side == "bottom" else iy1 + W
            adds.append(box(x - P["LIP_TAB_W"] / 2, x + P["LIP_TAB_W"] / 2, y0, y0 + P["LIP_TAB_L"],
                            zt - P["LIP_TAB_T"], zt))
            tabs.append((x, y0 + P["LIP_TAB_L"] / 2.0, "y"))
    frame = fuse([frame] + adds)
    fcuts = [cyl(P["SCREW_CLEAR"] / 2.0, hh["x"], hh["y"], bt - 1, zt + 1) for hh in holes]
    for (x, y, ax) in tabs:   # a slot, so the tab finds the lip's real hole (V-113)
        sl = P["LIP_SLOT"]
        if ax == "x":
            fcuts.append(rrect_prism(sl, P["SCREW_CLEAR"], P["SCREW_CLEAR"] / 2 - 0.01, x, y, zt - 5, zt + 1))
        else:
            fcuts.append(rrect_prism(P["SCREW_CLEAR"], sl, P["SCREW_CLEAR"] / 2 - 0.01, x, y, zt - 5, zt + 1))
    frame = cut(frame, fcuts)
    parts = {"base": tray, "lid": frame}
    info = {"interior": [ix0, ix1, iy0, iy1, zf, zt], "back_depth": round(back, 2),
            "outer": _outer(parts), "box_no_tabs": [round(w + 2 * W, 2), round(h + 2 * W, 2),
                                                    round(zt - zb, 2)],
            "faceplate_plane_z": round(zt, 2)}
    return parts, info


# ------------------------------------------------------------------------------ check / export --
def _outer(parts):
    bb = None
    for s in parts.values():
        if bb is None:
            bb = FreeCAD.BoundBox(s.BoundBox)
        else:
            bb.add(s.BoundBox)
    return [round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)]


def envelope_check(info, envelope):
    """True when the box (tabs excluded) fits the measured envelope in some orientation."""
    if envelope is None:
        return None
    a = sorted(info["box_no_tabs"])
    b = sorted(envelope)
    return all(x <= y for x, y in zip(a, b))


def fit_check(parts, step_path, board, seal_refs=()):
    """Interference of every part with every solid of the board STEP. A DT13's own flange seal
    against the plate is reported apart (that squeeze is TE's seal doing its job), and so is a
    touch thinner than CONTACT mm (a face resting on a face, e.g. the board's edge on the plate)."""
    if not os.path.exists(step_path):
        return None
    shape = Part.read(step_path)
    board_solid = max(shape.Solids, key=lambda s: s.BoundBox.XLength * s.BoundBox.YLength
                      if s.BoundBox.ZLength < 2.0 else 0)
    res = {}
    for name, p in parts.items():
        pb = p.BoundBox
        hits, seal, touch = [], 0.0, []
        for s in shape.Solids:
            sb = s.BoundBox
            if not sb.intersect(pb):
                continue
            com = p.common(s)
            v = com.Volume if not com.isNull() else 0.0
            ctr = sb.Center
            ref = "board" if s.isSame(board_solid) else "?"
            for f in ([] if ref == "board" else board["footprints"]):
                if _in_box(ctr.x, ctr.y, f["courtyard"], 0.5):
                    ref = f["ref"]
                    break
            if v > 1e-4:
                cb = com.optimalBoundingBox()
                thin = min(cb.XLength, cb.YLength, cb.ZLength)
                if ref in seal_refs and thin <= 0.6 and cb.ZLength > 20:
                    seal += v
                    continue
                if thin < CONTACT:
                    touch.append((ref, round(thin, 3)))
                    continue
                hits.append((ref, round(v, 2), [round(t, 1) for t in (cb.XMin, cb.XMax, cb.YMin,
                                                                       cb.YMax, cb.ZMin, cb.ZMax)]))
        res[name] = {"interferences": hits, "seal_squeeze_mm3": round(seal, 1), "contact": touch}
    return res


def export(parts, outdir, prefix):
    out = []
    for name, s in parts.items():
        base = os.path.join(outdir, "%s-enclosure-%s" % (prefix, name))
        s.exportStep(base + ".step")
        m = Mesh.Mesh(s.tessellate(0.05))
        m.write(base + ".stl")
        for ext in (".step", ".stl"):
            out.append((os.path.basename(base + ext), os.path.getsize(base + ext)))
    return out


def report(title, P, info, fit, files, env_ok, envelope_name):
    print("=" * 78)
    print(title)
    print("material %s; wall %.1f, floor %.1f, lid %.1f mm" % (P["MATERIAL"], P["WALL"], P["FLOOR"],
                                                                P.get("LID", 0)))
    print("box (tabs and lugs excluded) %s mm; overall %s mm" % (info["box_no_tabs"], info["outer"]))
    if env_ok is None:
        print("envelope %s: not measured - the box is the provisional outline plus walls (confirm)"
              % envelope_name)
    else:
        print("envelope %s: %s" % (envelope_name, "FITS" if env_ok else "DOES NOT FIT"))
    for k in ("cutouts", "grommets", "ribbon_notch", "rf", "back_depth", "faceplate_plane_z"):
        if k in info:
            v = info[k]
            if isinstance(v, list) and v and isinstance(v[0], dict):
                for d in v:
                    print("  %s: %s" % (k, json.dumps(d)))
            else:
                print("  %s: %s" % (k, json.dumps(v)))
    if fit is None:
        print("fit check: skipped - no board STEP")
    else:
        for name, r in fit.items():
            print("fit %-6s interferences %d%s%s%s" % (
                name, len(r["interferences"]),
                (" " + json.dumps(r["interferences"])) if r["interferences"] else "",
                ("; DT13 seal squeeze %.1f mm3 (intended)" % r["seal_squeeze_mm3"])
                if r["seal_squeeze_mm3"] else "",
                ("; faces touching %s" % json.dumps(r["contact"])) if r["contact"] else ""))
    for n, sz in files:
        print("  wrote %-40s %8d bytes" % (n, sz))
