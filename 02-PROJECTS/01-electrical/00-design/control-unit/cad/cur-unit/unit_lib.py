"""The Control Unit Remote's mock-up (D-514, Y25): layout, fit rules, solids, checks, output.

Run by `make_unit.py` through FreeCAD's headless interpreter, never on its own. Holds NO dimension:
every number comes from `unit_params.py` (the parameter table), from `../../../tools/enclosure_lib.py`
(TE's DT13 panel cut-outs, the primitives), or from files it only reads:

- `../left-plate/left-plate.kicad_pcb`   the plate's board (Y22): outline, thickness, holes and every
                                          footprint, parsed here as text (no KiCad needed), so the
                                          face follows the board when the board moves;
- `../dcu-carrier/enclosure/board.json`,
  `../dcu-carrier/enclosure/probe.json`  a DT13's flange, housing section, seal and nose, as the DCU
                                          enclosure build read them from TE's models.

Built the climate unit's way and, where its code is generic, WITH its code: `../climate-unit/
unit_lib.py` is imported (as `CU`) for the helpers, the 2D footprint arithmetic, the stand-in DT13
(`_standin_dt13`), the case builder (`build_case`: body with its beam and lugs, rear plate in its
channel with TE's cut-outs, lid with the gasket groove, front frame with its standoffs) and the
interference test. A change there changes the CUR too; the self-test here says so.

Four steps, in this order, and nothing is drawn until the second has passed:

    derive(P, src)      every position, from the parameters - arithmetic only
    validate(P, src)    the fit rules: sentences naming the parameter and the way to move it
    build_*             the solids, all from what derive() returned
    check(...)          interference of every inside solid with every case solid, and the rest

Owns no fact in the record: the plate is parts P198 / P199 / P204 / P156, its leads P200 and DV24
(D-492, D-504); the CUR's rear connection is block 01.41 and its codes DP-CUR / DP-CUR-B are provisional.
"""
import copy
import importlib.util
import math
import os
import re

import FreeCAD
import Part
from FreeCAD import Vector as V

import enclosure_lib as L

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "cu_unit_lib", os.path.join(os.path.dirname(_HERE), "climate-unit", "unit_lib.py"))
CU = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CU)

NS, n, num = CU.NS, CU.n, CU.num
NONE_OK = ("FACE_W", "FACE_H", "BOARD_GAP", "BOARD_BACK_H", "EAR_Y", "EAR_Z")
NEG_OK = ("BOARD_DX", "BOARD_DZ", "REAR_DX", "REAR_DZ")
ZERO_OK = ("CAP_CLEAR", "STICK_FLOAT", "LED_LIT_REACH", "LED_PIPE_CLEAR", "CONTROL_EDGE",
           "CONTROL_GAP", "CONTROL_BEHIND_CLEAR", "FRONT_CLEAR", "BOARD_DX", "BOARD_DZ",
           "REAR_DX", "REAR_DZ", "REAR_GAP", "REC_WIRE_L", "SEAL_LAND", "LEAD_BEND_IN",
           "CABLE_BEND", "PLUG_GROW", "BEZEL_OVERLAP", "GAP", "RIM_H", "PLATE_LIP", "SLOT_DEPTH",
           "SLOT_CLEAR", "FLOOR_GROOVE", "CUTOUT_CLEAR", "LUG_EMBED", "INSERT_SKIN", "GASKET_R",
           "OUTLINE_TOL", "BOARD_JSON_EDGE", "SEAL_SQUEEZE_MAX", "VOLUME_EPS", "EPS")
REARS = ("receptacle", "grommet")
SIDES = ("left", "right")
NAME = "cur-unit"
CASE_PARTS = ("body", "rear_plate", "lid", "front_frame")
OUTPUTS = ("%s.FCStd" % NAME, "%s.step" % NAME) + tuple("%s-%s.step" % (NAME, p) for p in CASE_PARTS)
VIEWS = ("front", "back", "side", "top")


# ---------------------------------------------------------------------------- the KiCad board --
def _sexp(txt):
    """A KiCad file's S-expression as nested lists of strings."""
    stack = [[]]
    for t in re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', txt):
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop()
            stack[-1].append(done)
        else:
            stack[-1].append(t[1:-1] if t[0] == '"' else t)
    return stack[0][0]


def _kids(node, name):
    return [k for k in node[1:] if isinstance(k, list) and k and k[0] == name]


def _one(node, name):
    k = _kids(node, name)
    return k[0] if k else None


def _xy(node):
    return float(node[1]), float(node[2])


def _circle_r(a, m, b):
    """Radius of the circle through three points."""
    ax, ay = a
    bx, by = m
    cx, cy = b
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return 0.0
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) +
          (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) +
          (cx * cx + cy * cy) * (bx - ax)) / d
    return math.hypot(ax - ux, ay - uy)


def read_board(path):
    """The plate board as the CUR needs it, in KiCad's own frame (mm, x right, y DOWN, seen from
    the front, F.Cu): outline box, corner radius, thickness, and per footprint its ref, library
    name, side, place, value, pads and its F.Fab / courtyard graphics in board coordinates."""
    root = _sexp(open(path, encoding="utf-8").read())
    gen = _one(root, "general")
    out = {"thickness": float(_one(gen, "thickness")[1]) if gen and _one(gen, "thickness")
           else None, "footprints": {}, "corner_r": 0.0}
    xs, ys = [], []
    for g in root[1:]:
        if not (isinstance(g, list) and g and g[0] in ("gr_line", "gr_arc", "gr_rect")):
            continue
        lay = _one(g, "layer")
        if not lay or lay[1] != "Edge.Cuts":
            continue
        pts = [_xy(_one(g, k)) for k in ("start", "mid", "end") if _one(g, k)]
        xs += [p[0] for p in pts]
        ys += [p[1] for p in pts]
        if g[0] == "gr_arc" and len(pts) == 3:
            out["corner_r"] = max(out["corner_r"], _circle_r(*pts))
    if not xs:
        return out
    # an arc's mid point is inside the corner: the box is the lines' and arcs' extreme points
    out["outline"] = [min(xs), max(xs), min(ys), max(ys)]
    for fp in _kids(root, "footprint"):
        at = _one(fp, "at")
        X, Y = _xy(at)
        a = math.radians(float(at[3])) if len(at) > 3 else 0.0
        c, s = math.cos(a), math.sin(a)

        def tr(lx, ly, X=X, Y=Y, c=c, s=s):
            return (X + lx * c + ly * s, Y - lx * s + ly * c)
        props = {p[1]: p[2] for p in _kids(fp, "property") if len(p) > 2}
        ref = props.get("Reference", "?")
        pads = []
        for p in _kids(fp, "pad"):
            pa = _one(p, "at")
            dr = _one(p, "drill")
            pads.append({"num": p[1], "at": tr(*_xy(pa)),
                         "drill": float(dr[1]) if dr and len(dr) > 1 and
                         re.match(r"^[\d.]+$", dr[1]) else None})
        gfx = []
        for g in fp[1:]:
            if not (isinstance(g, list) and g and g[0] in ("fp_line", "fp_rect", "fp_circle",
                                                           "fp_arc", "fp_poly")):
                continue
            lay = (_one(g, "layer") or [None, ""])[1]
            stroke = _one(g, "stroke")
            dashed = bool(stroke and _one(stroke, "type") and _one(stroke, "type")[1] == "dash")
            if g[0] == "fp_rect":
                (x0, y0), (x1, y1) = _xy(_one(g, "start")), _xy(_one(g, "end"))
                pts = [tr(x0, y0), tr(x1, y0), tr(x1, y1), tr(x0, y1)]
            elif g[0] == "fp_circle":
                cx, cy = _xy(_one(g, "center"))
                ex, ey = _xy(_one(g, "end"))
                r = math.hypot(ex - cx, ey - cy)
                gfx.append({"kind": "circle", "layer": lay, "dashed": dashed,
                            "c": tr(cx, cy), "r": r})
                continue
            elif g[0] == "fp_poly":
                pts = [tr(*_xy(q)) for q in _kids(_one(g, "pts"), "xy")]
            else:
                pts = [tr(*_xy(_one(g, k))) for k in ("start", "mid", "end") if _one(g, k)]
            gfx.append({"kind": g[0][3:], "layer": lay, "dashed": dashed,
                        "box": [min(p[0] for p in pts), max(p[0] for p in pts),
                                min(p[1] for p in pts), max(p[1] for p in pts)]})
        out["footprints"][ref] = {
            "ref": ref, "lib": fp[1], "name": fp[1].split(":")[-1],
            "side": "back" if (_one(fp, "layer") or [None, "F.Cu"])[1].startswith("B.") else "front",
            "at": (X, Y), "rot": float(at[3]) if len(at) > 3 else 0.0,
            "value": props.get("Value", ""), "pads": pads, "gfx": gfx}
    return out


def _union(boxes):
    return [min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes),
            max(b[3] for b in boxes)]


def _fab_rects(f, dashed):
    return [g["box"] for g in f["gfx"] if g["kind"] == "rect" and g["layer"].endswith("Fab")
            and g["dashed"] == dashed]


def _layer_box(f, suffix):
    """The bounding box of a footprint's graphics on its F./B. layer ending in `suffix`."""
    boxes = []
    for g in f["gfx"]:
        if not g["layer"].endswith(suffix):
            continue
        if g["kind"] == "circle":
            boxes.append([g["c"][0] - g["r"], g["c"][0] + g["r"], g["c"][1] - g["r"],
                          g["c"][1] + g["r"]])
        else:
            boxes.append(g["box"])
    return _union(boxes) if boxes else None


# ------------------------------------------------------------------------------------- source --
def load_source(cad_dir, P):
    """The plate's board and a DT13's probed shapes, read once."""
    src = {"problems": [], "notes": [], "board": None, "dt13": {}}
    pcb = os.path.join(cad_dir, "left-plate", "left-plate.kicad_pcb")
    if not os.path.exists(pcb):
        src["problems"].append("left-plate/left-plate.kicad_pcb is not there: the CUR is built "
                               "round that board (Y22).")
        return src
    b = read_board(pcb)
    if "outline" not in b or not b["thickness"]:
        src["problems"].append("left-plate.kicad_pcb has no Edge.Cuts outline or no board "
                               "thickness: regenerate it (gen_left_plate.py pcb).")
        return src
    src["board"] = b
    enc = os.path.join(cad_dir, "dcu-carrier", "enclosure")
    for name in ("board.json", "probe.json"):
        if not os.path.exists(os.path.join(enc, name)):
            src["problems"].append(
                "%s is missing from dcu-carrier/enclosure: run that folder's make_enclosure.py "
                "first - the CUR's receptacle stand-in is the DT13 that build probed." % name)
            return src
    cb, pr = L.load(os.path.join(enc, "board.json")), L.load(os.path.join(enc, "probe.json"))
    yb_edge = cb["outline"]["ymin"] + P["BOARD_JSON_EDGE"]
    for f in cb["footprints"]:
        d = pr["dt13"].get(f["ref"]) or {}
        if not L.is_dt13(f) or f["dnp"] or not d.get("model") or f["footprint"] in src["dt13"]:
            continue
        h, fl, se = d["housing"], d["flange"], d["seal"]
        hx, hz = (h[0] + h[1]) / 2.0, (h[2] + h[3]) / 2.0
        src["dt13"][f["footprint"]] = {
            "from": "%s on the DCU carrier (%s)" % (f["ref"], f["value"].split()[0]),
            "housing": [h[0] - hx, h[1] - hx, h[2] - hz, h[3] - hz],
            "flange": [fl[0] - hx, fl[1] - hx, fl[2] - hz, fl[3] - hz],
            "seal": [se[0] - hx, se[1] - hx, se[2] - hz, se[3] - hz],
            "past": d["flange_front_past_board_edge"],
            "tip": yb_edge - d["y_tip"],
            "seal_proud": d["y_flange"] - d["y_seal"]}
    return src


# -------------------------------------------------------------------------------------- types --
def check_types(P, U):
    """Refuse a parameter set that is not numbers where numbers go, before any arithmetic."""
    bad = []
    for name in list(P):
        if name not in U.UNIT and name != "ENVELOPE":
            bad.append("%s is not a parameter of unit_params.py: check the spelling." % name)
    for name, unit in U.UNIT.items():
        if name not in P:
            bad.append("%s is missing from the parameters." % name)
            continue
        v = P[name]
        if not num(U.P[name]) and U.P[name] is not None:
            continue                                   # a table or a word: checked below
        if v is None:
            if name not in NONE_OK:
                bad.append("%s is None, but it has no derived value: give it a number in %s."
                           % (name, unit))
            continue
        if not num(v):
            bad.append("%s is %r: it must be a number in %s." % (name, v, unit))
        elif name in NEG_OK:
            continue
        elif v < 0 or (v == 0 and name not in ZERO_OK):
            bad.append("%s is %s: it must be %s. Raise it."
                       % (name, n(v), "0 or more" if name in ZERO_OK else "more than 0"))
    if bad:
        return bad
    if P["REAR"] not in REARS:
        bad.append("REAR is %r: it must be one of %s." % (P["REAR"], ", ".join(map(repr, REARS))))
    for row in P["LEADS"]:
        if not (isinstance(row, (tuple, list)) and len(row) == 3 and isinstance(row[0], str)
                and num(row[1]) and row[1] > 0):
            bad.append("LEADS row %r is not (header ref, outside diameter in mm, what)." % (row,))
    for row in P["RECEPTACLES"]:
        if not (isinstance(row, (tuple, list)) and len(row) == 3 and isinstance(row[0], str)
                and isinstance(row[1], str) and isinstance(row[2], (tuple, list))):
            bad.append("RECEPTACLES row %r is not (code, TE part, (header refs, ...))." % (row,))
    if not isinstance(P["BACK_PARTS"], dict) or not all(
            num(v) and v > 0 for v in P["BACK_PARTS"].values()):
        bad.append("BACK_PARTS must be {header ref: height in mm, more than 0}.")
    if not isinstance(P["EARS"], (list, tuple)) or any(e not in SIDES for e in P["EARS"]):
        bad.append("EARS %r must be a list of 'left' and / or 'right' ([] = none)." % (P["EARS"],))
    if not P["LID_LUGS"] or not all(num(f) and 0 <= f <= 1 for f in P["LID_LUGS"]):
        bad.append("LID_LUGS %r must be one or more fractions from 0 (the beam) to 1 (the rear "
                   "plate)." % (P["LID_LUGS"],))
    if not isinstance(P["KEY_CAP_FROM"], str):
        bad.append("KEY_CAP_FROM must be a footprint's reference, such as 'SW3'.")
    env = P["ENVELOPE"]
    if env is not None and not (isinstance(env, dict) and all(
            num(env.get(k)) and env[k] > 0 for k in ("OPENING_W", "OPENING_H", "DEPTH"))):
        bad.append("ENVELOPE must be None or {OPENING_W, OPENING_H, DEPTH} in mm.")
    return bad


# ------------------------------------------------------------------------------- the board, 2D --
def _plate_parts(P, src, D):
    """What the CUR needs from the board, classified by footprint: the switches under caps, the
    stick, the LEDs, the holes, the headers on the back. Board coordinates (KiCad's, y down)."""
    B = src["board"]
    fps = B["footprints"]
    out = NS(caps=[], stick=None, knob=None, leds=[], holes=[], back=[])
    capf = fps.get(P["KEY_CAP_FROM"])
    cap_box = (_fab_rects(capf, True) or [None])[0] if capf else None
    if cap_box is None:
        D.problems.append("KEY_CAP_FROM %r has no dashed cap outline on F.Fab in the board: name "
                          "a wink switch (P204 placeholder), such as SW3." % P["KEY_CAP_FROM"])
        return out
    cap_wh = (cap_box[1] - cap_box[0], cap_box[3] - cap_box[2])
    for ref in sorted(fps):
        f = fps[ref]
        nm = f["name"]
        if f["side"] == "back":
            if ref in P["BACK_PARTS"]:
                cy = _layer_box(f, "CrtYd")
                out.back.append(NS(ref=ref, value=f["value"], box=cy, h=P["BACK_PARTS"][ref],
                                   ways=len({p["num"] for p in f["pads"] if p["num"]})))
            continue
        if nm.startswith(("WinkSwitch", "HazardSwitch")):    # the hazard's cap is a wink's (D-589, Y62)
            cb = (_fab_rects(f, True) or [None])[0]
            body = _union(_fab_rects(f, False)) if _fab_rects(f, False) else None
            if cb is None or body is None:
                D.problems.append("%s (%s) has no dashed cap or solid body outline on F.Fab: the "
                                  "CUR reads the cap and the body from there." % (ref, nm))
                continue
            out.caps.append(NS(ref=ref, kind="wink", value=f["value"],
                               c=((cb[0] + cb[1]) / 2.0, (cb[2] + cb[3]) / 2.0),
                               w=cb[1] - cb[0], h=cb[3] - cb[2], body=body,
                               sw_h=P["WINK_SW_H"], glb=False))
        elif nm.startswith("SW_PUSH"):
            body = _union(_fab_rects(f, False) or [_layer_box(f, "Fab")])
            out.caps.append(NS(ref=ref, kind="key", value=f["value"],
                               c=((body[0] + body[1]) / 2.0, (body[2] + body[3]) / 2.0),
                               w=cap_wh[0], h=cap_wh[1], body=body, sw_h=P["KEY_SW_H"],
                               glb=True))
        elif nm.startswith("Thumbstick"):
            circ = [g for g in f["gfx"] if g["kind"] == "circle" and g["layer"].endswith("Fab")]
            body = (_fab_rects(f, False) or [None])[0]
            if not circ or body is None:
                D.problems.append("%s (%s) has no well circle or body square on F.Fab." % (ref, nm))
                continue
            out.stick = NS(ref=ref, value=f["value"], c=f["at"], well_d=2 * circ[0]["r"],
                           body=body)
        elif nm.startswith("ScreenKnob"):                    # D-581, Y51: KN1, the knob board's room
            body = (_fab_rects(f, False) or [None])[0]
            if body is None:
                D.problems.append("%s (%s) has no board square on F.Fab." % (ref, nm))
                continue
            out.knob = NS(ref=ref, value=f["value"], c=f["at"], body=body)
        elif nm.startswith("LED"):
            out.leds.append(NS(ref=ref, value=f["value"], c=f["at"]))
        elif nm.startswith("MountingHole"):
            d = max([p["drill"] or 0.0 for p in f["pads"]] or [0.0])
            out.holes.append(NS(ref=ref, c=f["at"], d=d))
    if not out.caps or out.stick is None or not out.holes:
        D.problems.append("The board has %d capped switches, %s stick and %d mounting holes: the "
                          "CUR needs the winks, the keys, the stick and the holes."
                          % (len(out.caps), "a" if out.stick else "no", len(out.holes)))
    return out


# ------------------------------------------------------------------------------------- derive --
def derive(P, src):
    """Every position in the unit, from the parameters, the board and the probed DT13."""
    TE = L.TE_CUTOUT
    B = src["board"]
    D = NS(problems=[], notes=list(src["notes"]))
    eps, G, WL, BZ = P["EPS"], P["GAP"], P["WALL"], P["BEZEL_OVERLAP"]
    o = B["outline"]
    D.bw, D.bh, D.bt, D.br = o[1] - o[0], o[3] - o[2], B["thickness"], B["corner_r"]
    pp = _plate_parts(P, src, D)
    if D.problems:
        return D
    D.pp = pp

    # ---- the leads and how each leaves: a receptacle that carries it, or the grommet
    heads = {b.ref: b for b in pp.back}
    leads = []
    for (ref, od, what) in P["LEADS"]:
        f = B["footprints"].get(ref)
        if f is None or f["side"] != "back":
            D.problems.append("LEADS names %s, which is no header on the board's back: use one "
                              "of %s." % (ref, ", ".join(sorted(heads)) or "none"))
            continue
        leads.append(NS(ref=ref, od=od, what=what,
                        ways=len({p["num"] for p in f["pads"] if p["num"]})))
    by_ref = {ld.ref: ld for ld in leads}
    recs = []
    if P["REAR"] == "receptacle":
        taken = {}
        for (code, part, carries) in P["RECEPTACLES"]:
            if part not in TE or part not in src["dt13"]:
                D.problems.append(
                    "RECEPTACLES %s is a %s: there is %s for it. Use one of %s." % (
                        code, part, "no TE cut-out (enclosure_lib.TE_CUTOUT)" if part not in TE
                        else "no probed model of one on the DCU carrier",
                        ", ".join(sorted(set(TE) & set(src["dt13"])))))
                continue
            for r in carries:
                if r not in by_ref:
                    D.problems.append("RECEPTACLES %s carries %r, which is not a lead in LEADS "
                                      "(%s)." % (code, r, ", ".join(sorted(by_ref))))
                elif r in taken:
                    D.problems.append("%s is carried by both %s and %s: give each lead one "
                                      "receptacle." % (r, taken[r], code))
                else:
                    taken[r] = code
            pr = src["dt13"][part]
            recs.append(NS(kind="receptacle", name=code, part=part, te=TE[part], pr=pr,
                           fitted=True, row="rear", carries=list(carries),
                           ways=int(part[5:7]),
                           conductors=sum(by_ref[r].ways for r in carries if r in by_ref),
                           w=pr["flange"][1] - pr["flange"][0],
                           h=pr["flange"][3] - pr["flange"][2]))
        D.grommet_leads = [ld for ld in leads if ld.ref not in taken]
    else:
        D.grommet_leads = list(leads)
    if D.problems:
        return D
    D.leads, D.recs = leads, recs
    row = list(recs)
    D.grommet = None
    if D.grommet_leads:
        D.grommet = NS(kind="grommet", name="grommet", w=P["GROMMET_FLANGE_D"],
                       h=P["GROMMET_FLANGE_D"], leads=D.grommet_leads)
        row.append(D.grommet)

    # ---- what the rear row needs across and up (the body grows to it, as it grows to the board)
    pe, cc = P["PLATE_EDGE"], P["CUTOUT_CLEAR"]
    D.row_w = sum(r.w for r in row) + P["REAR_GAP"] * (len(row) - 1)
    x = -D.row_w / 2.0
    for r in row:
        r.dx = x + r.w / 2.0                           # from the row's centre
        x += r.w + P["REAR_GAP"]
    span = []                                          # what must keep PLATE_EDGE from the walls
    for r in row:
        if r.kind == "receptacle":
            t = r.te
            reach = max(t["pitch"] / 2.0 + t["hole"] / 2.0, t["w"] / 2.0 + cc)
            span += [(r.dx - reach, r.dx + reach, t["h"] / 2.0 + cc)]
        else:
            span += [(r.dx - r.w / 2.0, r.dx + r.w / 2.0, r.h / 2.0)]
    need_w = max(D.row_w + 2 * G, max(s[1] for s in span) - min(s[0] for s in span) + 2 * pe)
    need_h = max(max(r.h for r in row) + 2 * G, 2 * max(s[2] for s in span) + 2 * pe)
    D.rear_need = [need_w + 2 * abs(P["REAR_DX"]), need_h + 2 * abs(P["REAR_DZ"])]
    D.board_need = [D.bw + 2 * G + 2 * abs(P["BOARD_DX"]), D.bh + 2 * G + 2 * abs(P["BOARD_DZ"])]

    # ---- across (X) and up (Z): the body round the inner room, the face round the body
    D.inner_w = max(D.board_need[0], D.rear_need[0])
    D.inner_h = max(D.board_need[1], D.rear_need[1])
    D.body_w = D.inner_w + 2 * WL
    D.body_h = P["FLOOR"] + D.inner_h + P["LID"]
    D.face_w_least, D.face_h_least = D.body_w + 2 * BZ, D.body_h + 2 * BZ
    D.face_w_typed, D.face_h_typed = P["FACE_W"] is not None, P["FACE_H"] is not None
    D.face_w = P["FACE_W"] if D.face_w_typed else D.face_w_least
    D.face_h = P["FACE_H"] if D.face_h_typed else D.face_h_least
    D.xc = D.face_w / 2.0
    D.bx0, D.bx1 = D.xc - D.body_w / 2.0, D.xc + D.body_w / 2.0
    D.ix0, D.ix1 = D.bx0 + WL, D.bx1 - WL
    D.zb = (D.face_h - D.body_h) / 2.0
    D.zf = D.zb + P["FLOOR"]
    D.z_rim = D.z_ceil = D.zf + D.inner_h
    D.z_lid = D.z_ft = D.z_rim + P["LID"]
    D.z_under = D.z_rim - P["RIM_H"]
    hangs = P["RIM_H"] > eps
    D.stepped = False
    D.zmid = (D.zf + D.z_rim) / 2.0
    D.front_h = D.rear_h = D.body_h

    # the board: KiCad's (x, y-down) -> the unit's (X, Z)
    D.bxl = D.xc + P["BOARD_DX"] - D.bw / 2.0
    D.bzt = D.zmid + P["BOARD_DZ"] + D.bh / 2.0
    D.bxr, D.bzb = D.bxl + D.bw, D.bzt - D.bh

    def bX(kx):
        return D.bxl + (kx - o[0])

    def bZ(ky):
        return D.bzt - (ky - o[2])

    def bbox(b):                                       # a board box -> [X0, X1, Z0, Z1]
        return [bX(b[0]), bX(b[1]), bZ(b[3]), bZ(b[2])]
    D.bX, D.bZ, D.bbox = bX, bZ, bbox

    # ---- the openings in the face, each over its part on the board
    cl = P["CAP_CLEAR"]
    D.controls, D.switches = [], []
    for c in pp.caps:
        X, Z = bX(c.c[0]), bZ(c.c[1])
        what = "wink" if c.kind == "wink" else "key"
        ctl = NS(name="%s %s cap" % (c.ref, what), kind="cap", ref=c.ref, X=X, Z=Z,
                 size=(c.w, c.h), value=c.value)
        ctl.seen = ctl.hole = ctl.behind = ("rect", c.w + 2 * cl, c.h + 2 * cl)
        D.controls.append(ctl)
        D.switches.append(NS(ref=c.ref, kind=c.kind, value=c.value, box=bbox(c.body),
                             sw_h=c.sw_h, glb=c.glb, cap=ctl))
    st = pp.stick
    D.stick = NS(ref=st.ref, value=st.value, X=bX(st.c[0]), Z=bZ(st.c[1]), well_d=st.well_d,
                 box=bbox(st.body))
    well = NS(name="%s mirror stick well" % st.ref, kind="well", ref=st.ref, X=D.stick.X,
              Z=D.stick.Z)
    well.seen = well.hole = well.behind = ("circ", st.well_d)
    D.controls.append(well)
    D.knob = None
    if pp.knob is not None:                            # the screen knob's hole (D-581, Y51)
        kb = pp.knob
        D.knob = NS(ref=kb.ref, value=kb.value, X=bX(kb.c[0]), Z=bZ(kb.c[1]), box=bbox(kb.body))
        kh = NS(name="%s screen knob" % kb.ref, kind="knob", ref=kb.ref, X=D.knob.X, Z=D.knob.Z)
        kh.seen = ("circ", P["KNOB_D"])
        kh.hole = kh.behind = ("circ", P["KNOB_HOLE_D"])
        D.controls.append(kh)
    D.leds = []
    reach = P["LED_LIT_REACH"]
    for led in pp.leds:
        X, Z = bX(led.c[0]), bZ(led.c[1])
        by = None
        for ctl in D.controls:
            if ctl.kind not in ("cap", "well"):
                continue
            pt = NS(X=X, Z=Z)
            g = CU._gap2d(pt, ("circ", 0.0), ctl, ctl.hole)
            if g <= reach + eps:
                by = ctl
                break
        rec = NS(ref=led.ref, value=led.value, X=X, Z=Z, lit_by=by.name if by else None)
        if by is None:
            win = NS(name="%s window" % led.ref, kind="window", ref=led.ref, X=X, Z=Z)
            win.seen = win.hole = win.behind = ("circ", P["LED_WINDOW_D"])
            D.controls.append(win)
            rec.window = win
        D.leds.append(rec)
    D.holes_xz = [(h.ref, bX(h.c[0]), bZ(h.c[1]), h.d) for h in pp.holes]
    D.panel_holes = [(x, z) for (_, x, z, _) in D.holes_xz]     # the front frame's standoffs

    # ---- going back (Y)
    D.y_face = P["FACE_T"]
    D.y_frame = D.y_face + P["FRAME_D"]
    cap_back = -P["CAP_PROUD"] + P["CAP_L"]
    floor_ = [(cap_back + max(s.sw_h for s in D.switches),
               "the tallest switch (%s %s) under a cap CAP_L %s deep standing CAP_PROUD %s"
               % (max(D.switches, key=lambda s: s.sw_h).ref, n(max(s.sw_h for s in D.switches)),
                  n(P["CAP_L"]), n(P["CAP_PROUD"]))),
              (D.y_face + P["FRONT_CLEAR"] + P["STICK_BODY_H"],
               "the stick's body (STICK_BODY_H %s) FRONT_CLEAR %s behind the face"
               % (n(P["STICK_BODY_H"]), n(P["FRONT_CLEAR"]))),
              (D.y_frame + P["FRONT_CLEAR"] + P["LED_H"],
               "the board's front parts FRONT_CLEAR behind the front frame's ring (FRAME_D %s)"
               % n(P["FRAME_D"]))]
    D.board_gap_why = floor_
    D.board_gap_least = max(f[0] for f in floor_) - D.y_face
    D.board_gap = P["BOARD_GAP"] if P["BOARD_GAP"] is not None else D.board_gap_least
    D.y_board0 = D.y_face + D.board_gap
    D.y_board1 = D.y_board0 + D.bt
    D.y_panel0 = D.y_board0                            # the climate unit's name, for build_case
    tall = max([b.h for b in pp.back] or [0.0])
    D.back_h_least = tall + P["HEADER_PLUG_H"]
    D.back_h = P["BOARD_BACK_H"] if P["BOARD_BACK_H"] is not None else D.back_h_least
    D.y_pko = D.y_board1 + D.back_h
    D.y_beam = max(D.y_pko, D.y_frame)
    D.y_step = D.y_beam + WL if hangs else D.y_beam
    D.y_riser = D.y_step + WL
    D.y_room = max(D.y_pko, D.y_riser + G)             # the rear section's room starts here
    if recs:
        past = max(r.pr["past"] for r in recs)
        D.y_rec0 = D.y_room + P["REC_WIRE_L"]          # the receptacles' housings, inside
        D.y_flange0 = D.y_rec0 + P["REC_BODY_L"]
        D.y_plate0 = D.y_flange0 + past
    else:
        D.y_plate0 = D.y_room + P["LEAD_BEND_IN"] + P["GROMMET_FLANGE_T"]
    if D.grommet and recs:
        D.y_plate0 = max(D.y_plate0, D.y_room + P["LEAD_BEND_IN"] + P["GROMMET_FLANGE_T"])
    D.y_plate1 = D.y_plate0 + P["PLATE"]
    D.y_end = D.y_plate1 + P["PLATE_LIP"]

    # ---- the rear row in place
    rx, rz = D.xc + P["REAR_DX"], D.zmid + P["REAR_DZ"]
    D.conns = []
    for r in row:
        r.X, r.Z = rx + r.dx, rz
        if r.kind != "receptacle":
            continue
        t, pr = r.te, r.pr
        r.cut = [r.X - t["w"] / 2.0 - cc, r.X + t["w"] / 2.0 + cc,
                 r.Z - t["h"] / 2.0 - cc, r.Z + t["h"] / 2.0 + cc]
        r.holes = [r.X - t["pitch"] / 2.0, r.X + t["pitch"] / 2.0]
        r.reach = [min(r.holes[0] - t["hole"] / 2.0, r.cut[0]),
                   max(r.holes[1] + t["hole"] / 2.0, r.cut[1]), r.cut[2], r.cut[3]]
        gr = P["PLUG_GROW"]
        r.plug = [r.X - t["w"] / 2.0 - gr, r.X + t["w"] / 2.0 + gr,
                  r.Z - t["h"] / 2.0 - gr, r.Z + t["h"] / 2.0 + gr]
        f, s = pr["flange"], pr["seal"]
        r.fl = [r.X - f[1], r.X - f[0], r.Z + f[2], r.Z + f[3]]     # mirrored, as the CU's ux
        r.seal = [r.X - s[1], r.X - s[0], r.Z + s[2], r.Z + s[3]]
        r.y_tip = D.y_plate0 - pr["past"] + pr["tip"]
        D.conns.append(r)
    D.y_tip = max([r.y_tip for r in D.conns] or [D.y_plate1])
    D.y_plugs = D.y_plate1 + P["PLUG_L"] + P["CABLE_BEND"] if D.conns else None
    if D.grommet:
        g = D.grommet
        k = len(g.leads)
        sw = sum(ld.od for ld in g.leads) + P["GROMMET_WEB"] * (k - 1)
        x = g.X - sw / 2.0
        for ld in g.leads:
            ld.X, ld.Z = x + ld.od / 2.0, g.Z
            x += ld.od + P["GROMMET_WEB"]
        g.bores_w = sw
    D.y_out = max([D.y_plugs or 0.0, D.y_tip, D.y_end] +
                  ([D.y_plate1 + P["LEAD_STUB_L"]] if D.grommet else []))

    # ---- the lid's lugs, the ears
    lr = P["LUG_D"] / 2.0
    D.lug_run = [D.y_riser + lr, D.y_plate0 - P["SLOT_CLEAR"] / 2.0 - G - lr]
    inset = lr - P["LUG_EMBED"]
    D.lugs = [(xx, D.lug_run[0] + fr * (D.lug_run[1] - D.lug_run[0]))
              for xx in (D.ix0 + inset, D.ix1 - inset) for fr in P["LID_LUGS"]]
    D.holes = []                                       # no carrier bosses in the CUR
    D.side_bosses = []                                 # the ears hold it instead
    D.ear_y = P["EAR_Y"] if P["EAR_Y"] is not None else D.y_frame
    D.ear_z = P["EAR_Z"] if P["EAR_Z"] is not None else (D.zb + D.z_lid) / 2.0
    D.ears = list(P["EARS"])
    return D


# -------------------------------------------------------------------------------------- rules --
def validate(P, src, U):
    """The fit rules. Returns (problems, D, margins): each problem is one plain sentence naming
    the parameter and the direction to move it. Runs before any geometry; with a problem, nothing
    is built."""
    problems = list(src["problems"])
    if problems:
        return problems, None, {}
    problems += check_types(P, U)
    if problems:
        return problems, None, {}
    D = derive(P, src)
    problems += D.problems
    if problems:
        return problems, D, {}
    M = {}
    eps, G, BZ = P["EPS"], P["GAP"], P["BEZEL_OVERLAP"]

    def bad(msg):
        problems.append(msg)

    # ---- the face round the body
    if D.face_w < D.face_w_least - eps:
        bad("FACE_W %s is narrower than the body (%s) and BEZEL_OVERLAP %s a side: raise FACE_W to "
            "at least %s, or set it to None and it is derived." % (
                n(D.face_w), n(D.body_w), n(BZ), n(D.face_w_least)))
    if D.face_h < D.face_h_least - eps:
        bad("FACE_H %s is lower than the body (%s) and BEZEL_OVERLAP %s a side: raise FACE_H to at "
            "least %s, or set it to None and it is derived." % (
                n(D.face_h), n(D.body_h), n(BZ), n(D.face_h_least)))
    if problems:
        return problems, D, M

    # ---- the board and the depth in front of it and behind it
    if D.board_gap < D.board_gap_least - eps:
        bad("BOARD_GAP %s is too small: raise it to at least %s (or set it to None). What sets "
            "that, largest first: %s." % (
                n(D.board_gap), n(D.board_gap_least), "; ".join(
                    "%s (needs %s)" % (f[1], n(f[0] - D.y_face)) for f in sorted(
                        D.board_gap_why, key=lambda f: -f[0]) if f[0] - D.y_face > D.board_gap)))
    if D.back_h < D.back_h_least - eps:
        bad("BOARD_BACK_H %s is less than the tallest header on the board's back (%s) and its "
            "mated plug (HEADER_PLUG_H %s): raise it to at least %s, or set it to None."
            % (n(D.back_h), n(D.back_h_least - P["HEADER_PLUG_H"]), n(P["HEADER_PLUG_H"]),
               n(D.back_h_least)))
    m = [D.bxl - D.ix0, D.ix1 - D.bxr, D.bzb - D.zf, D.z_rim - D.bzt]
    M["the board to the walls, floor and roof"] = min(m), G
    if min(m) < G - eps:
        bad("The board (X %s to %s, Z %s to %s) comes %s from the box's inside, less than GAP %s: "
            "bring BOARD_DX / BOARD_DZ toward 0." % (n(D.bxl), n(D.bxr), n(D.bzb), n(D.bzt),
                                                    n(min(m)), n(G)))

    # ---- the openings: on the face, over the box's opening behind it, apart from each other
    edge, gap, clr = P["CONTROL_EDGE"], P["CONTROL_GAP"], P["CONTROL_BEHIND_CLEAR"]
    m_edge, m_behind, m_gap = [], [], []
    for c in D.controls:
        on = CU._sides(c, c.seen, 0.0, D.face_w, 0.0, D.face_h)
        be = CU._sides(c, c.behind, D.ix0, D.ix1, D.zf, D.z_ceil)
        m_edge.append(min(on.values()))
        m_behind.append(min(be.values()))
        for side in ("left", "right", "bottom", "top"):
            if on[side] < edge - eps:
                bad("The %s comes %s from the face's %s edge, less than CONTROL_EDGE %s: raise "
                    "FACE_%s, or move the board (BOARD_DX / BOARD_DZ)." % (
                        c.name, n(on[side]), side, n(edge), "W" if side in ("left", "right")
                        else "H"))
            elif be[side] < clr - eps:
                bad("The %s comes %s from the box's %s inside, less than CONTROL_BEHIND_CLEAR %s: "
                    "move the board (BOARD_DX / BOARD_DZ) away from that side, or thin the wall."
                    % (c.name, n(be[side]), side, n(clr)))
    for i, a in enumerate(D.controls):
        for b in D.controls[i + 1:]:
            g = CU._gap2d(a, a.seen, b, b.seen)
            m_gap.append(g)
            if g < gap - eps:
                why = ""
                if "window" in (a.kind, b.kind):
                    why = " (an LED's window: raise LED_LIT_REACH so the opening beside it lights " \
                          "it, or lower LED_WINDOW_D)"
                bad("The %s and the %s are %s apart in the face, less than CONTROL_GAP %s: the "
                    "board puts them there - lower CAP_CLEAR or CONTROL_GAP, or move the parts on "
                    "the board (Y22)%s." % (a.name, b.name, n(g), n(gap), why))
    M["openings to the face's edge"] = min(m_edge), edge
    M["openings to the box behind the face"] = min(m_behind), clr
    if m_gap:
        M["openings to each other"] = min(m_gap), gap
    if P["STICK_SHAFT_D"] >= D.stick.well_d - eps:
        bad("STICK_SHAFT_D %s fills the stick's %s well: lower it." % (
            n(P["STICK_SHAFT_D"]), n(D.stick.well_d)))
    if P["LED_PIPE_CLEAR"] * 2 >= P["LED_WINDOW_D"] - eps:
        bad("LED_PIPE_CLEAR %s leaves no light pipe in a %s window: lower it."
            % (n(P["LED_PIPE_CLEAR"]), n(P["LED_WINDOW_D"])))

    # ---- inserts and thin places (the climate unit's rules, for the parts the CUR has)
    deep = P["INSERT_DEPTH"] + P["INSERT_SKIN"]
    if P["LUG_H"] < deep - eps:
        bad("LUG_H %s is less than an insert's bore and the skin beyond it (%s): raise LUG_H."
            % (n(P["LUG_H"]), n(deep)))
    wide = P["INSERT_BORE"] + 2 * P["INSERT_SKIN"]
    if P["LUG_D"] < wide - eps:
        bad("LUG_D %s leaves less than INSERT_SKIN round an INSERT_BORE: raise it to at least %s."
            % (n(P["LUG_D"]), n(wide)))
    if P["STANDOFF_D"] < P["SCREW_CLEAR"] + 2 * P["INSERT_SKIN"] - eps:
        bad("STANDOFF_D %s leaves too little round a SCREW_CLEAR %s hole: raise it to at least %s."
            % (n(P["STANDOFF_D"]), n(P["SCREW_CLEAR"]), n(P["SCREW_CLEAR"] + 2 * P["INSERT_SKIN"])))
    if P["PLATE"] > L.TE_PANEL_MAX + eps:
        bad("PLATE %s is thicker than TE allows for a DT13's panel (%s, 114-151046 3.11): lower "
            "PLATE." % (n(P["PLATE"]), n(L.TE_PANEL_MAX)))
    for a, b, what in (("SLOT_DEPTH", "WALL", "the plate's channel cuts through the side wall"),
                       ("LUG_EMBED", "WALL", "the lid lugs break out of the side wall"),
                       ("FLOOR_GROOVE", "FLOOR", "the plate's channel cuts through the floor"),
                       ("GASKET_GROOVE_W", "WALL", "the gasket groove is wider than the wall"),
                       ("GASKET_GROOVE_W", "PLATE", "the gasket groove is wider than the plate"),
                       ("GASKET_GROOVE_D", "LID", "the gasket groove cuts through the lid")):
        if P[a] >= P[b] - eps:
            bad("%s %s is not less than %s %s (%s): lower %s or raise %s."
                % (a, n(P[a]), b, n(P[b]), what, a, b))
    if D.lug_run[1] < D.lug_run[0] - eps:
        bad("There is no room for a lid lug between the beam and the rear plate: lower LUG_D.")

    # ---- the rear plate: every cut-out with plastic round it, every flange inside the box, the
    #      seal round the cut-out, the grommet's bores inside its body
    pe = P["PLATE_EDGE"]
    m_plate, m_seal, m_wall = [], [], []
    for r in D.conns:
        mm = {"left": r.reach[0] - D.ix0, "right": D.ix1 - r.reach[1],
              "bottom": r.reach[2] - D.zf, "top": D.z_rim - r.reach[3]}
        m_plate.append(min(mm.values()))
        for side, v in mm.items():
            if v < pe - eps:
                bad("The cut-out for %s comes %s from the rear plate's %s edge, less than "
                    "PLATE_EDGE %s: move it (REAR_DX / REAR_DZ) by %s." % (
                        r.name, n(v), side, n(pe), n(pe - v)))
        fw = min(r.fl[0] - D.ix0, D.ix1 - r.fl[1], r.fl[2] - D.zf, D.z_rim - r.fl[3])
        m_wall.append(fw)
        if fw < G - eps:
            bad("%s's flange (X %s to %s, Z %s to %s) comes %s from the box's inside, less than "
                "GAP %s: move it (REAR_DX / REAR_DZ) toward the middle." % (
                    r.name, n(r.fl[0]), n(r.fl[1]), n(r.fl[2]), n(r.fl[3]), n(fw), n(G)))
        land = min(r.cut[0] - r.seal[0], r.seal[1] - r.cut[1], r.cut[2] - r.seal[2],
                   r.seal[3] - r.cut[3])
        m_seal.append(land)
        if land < P["SEAL_LAND"] - eps:
            bad("%s's flange seal leaves only %s round TE's cut-out (CUTOUT_CLEAR %s included), "
                "less than SEAL_LAND %s: lower CUTOUT_CLEAR." % (
                    r.name, n(land), n(P["CUTOUT_CLEAR"]), n(P["SEAL_LAND"])))
        inside = min(r.holes[0] - r.te["hole"] / 2.0 - r.fl[0],
                     r.fl[1] - r.holes[1] - r.te["hole"] / 2.0)
        if inside < -eps:
            bad("%s's screw holes stand %s outside its flange: the probed flange is not the part "
                "the cut-out is for (%s)." % (r.name, n(-inside), r.part))
        sq = r.pr["seal_proud"]
        if not 0 < sq <= P["SEAL_SQUEEZE_MAX"] + eps:
            bad("%s's flange seal stands %s proud of its flange, outside 0 to SEAL_SQUEEZE_MAX %s: "
                "re-probe the DT13 (dcu-carrier/enclosure)." % (r.name, n(sq),
                                                                 n(P["SEAL_SQUEEZE_MAX"])))
    seq = sorted(D.conns, key=lambda r: r.X)
    for a, b in zip(seq, seq[1:]):
        g = b.reach[0] - a.reach[1]
        m_plate.append(g)
        if g < pe - eps or b.fl[0] - a.fl[1] < -eps:
            bad("%s and %s stand too close on the rear plate (%s between their screw holes, %s "
                "between their flanges): raise REAR_GAP." % (a.name, b.name, n(g),
                                                             n(b.fl[0] - a.fl[1])))
    if D.grommet:
        g = D.grommet
        mm = min(g.X - g.w / 2.0 - D.ix0, D.ix1 - g.X - g.w / 2.0, g.Z - g.h / 2.0 - D.zf,
                 D.z_rim - g.Z - g.h / 2.0)
        m_plate.append(mm)
        if mm < pe - eps:
            bad("The grommet's lips come %s from the rear plate's edge, less than PLATE_EDGE %s: "
                "move it (REAR_DX / REAR_DZ) or lower GROMMET_FLANGE_D." % (n(mm), n(pe)))
        need = g.bores_w + 2 * P["GROMMET_WEB"]
        far = max(math.hypot(ld.X - g.X, 0.0) + ld.od / 2.0 for ld in g.leads)
        M["the grommet's bores inside its body"] = P["GROMMET_BODY_D"] / 2.0 - far, \
            P["GROMMET_WEB"]
        if P["GROMMET_BODY_D"] / 2.0 - far < P["GROMMET_WEB"] - eps:
            bad("GROMMET_BODY_D %s is too small for its %d leads side by side (%s across with "
                "GROMMET_WEB %s): raise it to at least %s, or take a lead to a receptacle." % (
                    n(P["GROMMET_BODY_D"]), len(g.leads), n(g.bores_w), n(P["GROMMET_WEB"]),
                    n(need)))
        if P["GROMMET_FLANGE_D"] <= P["GROMMET_BODY_D"] + eps:
            bad("GROMMET_FLANGE_D %s is not wider than its body %s: raise it." % (
                n(P["GROMMET_FLANGE_D"]), n(P["GROMMET_BODY_D"])))
    if m_plate:
        M["cut-outs, screw holes and lips to the plate's edge and each other"] = min(m_plate), pe
    if m_wall:
        M["flanges to the box's inside"] = min(m_wall), G
    if m_seal:
        M["flange seal round the cut-out"] = min(m_seal), P["SEAL_LAND"]

    # ---- the ears
    if D.ears:
        y_lo, y_hi = D.y_frame, D.y_plate0 - P["SLOT_CLEAR"] / 2.0 - P["SLOT_DEPTH"] - P["EAR_T"]
        if not (y_lo - eps <= D.ear_y <= y_hi + eps):
            bad("EAR_Y %s puts the ears off the body: keep it between %s and %s." % (
                n(D.ear_y), n(y_lo), n(y_hi)))
        z_lo, z_hi = D.zb + P["EAR_W"] / 2.0, D.z_lid - P["EAR_W"] / 2.0
        if not (z_lo - eps <= D.ear_z <= z_hi + eps):
            bad("EAR_Z %s puts the ears off the body's side: keep it between %s and %s." % (
                n(D.ear_z), n(z_lo), n(z_hi)))
        if P["EAR_L"] < P["SCREW_CLEAR"] + 2 * P["INSERT_SKIN"] - eps or \
                P["EAR_W"] < P["SCREW_CLEAR"] + 2 * P["INSERT_SKIN"] - eps:
            bad("EAR_L %s / EAR_W %s leave too little round a SCREW_CLEAR %s hole: raise them to "
                "at least %s." % (n(P["EAR_L"]), n(P["EAR_W"]), n(P["SCREW_CLEAR"]),
                                  n(P["SCREW_CLEAR"] + 2 * P["INSERT_SKIN"])))

    # ---- the envelope, once measured
    env = P["ENVELOPE"]
    D.env = None
    if env is not None:
        D.env = []
        ow, oh = env["OPENING_W"], env["OPENING_H"]
        ear = 2 * P["EAR_L"] * len(D.ears) / 2.0 if D.ears else 0.0
        fits = D.body_w <= ow + eps and D.body_h <= oh + eps
        D.env.append(("body in the opening", fits,
                      "The body is %s x %s and the opening %s x %s%s." % (
                          n(D.body_w), n(D.body_h), n(ow), n(oh),
                          "" if not ear else " (the ears stand %s beyond it, behind the dash "
                          "skin)" % n(P["EAR_L"]))))
        if not fits:
            bad("The body is %s x %s and the opening %s x %s: it does not go in. Move parts on "
                "the board closer, or narrow the rear row (RECEPTACLES)." % (
                    n(D.body_w), n(D.body_h), n(ow), n(oh)))
        cover = D.face_w >= ow - eps and D.face_h >= oh - eps
        D.env.append(("face covers the opening", cover, "The face is %s x %s." % (
            n(D.face_w), n(D.face_h))))
        if not cover:
            bad("The face is %s x %s and the opening %s x %s: raise FACE_W / FACE_H to at least "
                "the opening." % (n(D.face_w), n(D.face_h), n(ow), n(oh)))
        deep = D.y_out - D.y_face
        D.env.append(("depth", deep <= env["DEPTH"] + eps,
                      "Behind the face it needs %s and the opening has %s." % (
                          n(deep), n(env["DEPTH"]))))
        if deep > env["DEPTH"] + eps:
            bad("Behind the face the CUR needs %s with its plugs or leads and the opening has %s: "
                "shorten it by %s (REC_BODY_L, REC_WIRE_L, HEADER_PLUG_H, PLUG_L, CABLE_BEND)."
                % (n(deep), n(env["DEPTH"]), n(deep - env["DEPTH"])))
    return problems, D, M


# ------------------------------------------------------------------------------------ insides --
_item = CU._item


def _receptacle(P, D, r):
    """The DT13 flange receptacle: the climate unit's stand-in (`_standin_dt13`: its housing
    behind the flange, the flange, the nose with TE's corner radius) placed on the rear plate's
    inside, and the flange seal standing proud of the flange into the plate - the squeeze."""
    pr = r.pr
    h = pr["housing"]
    xc = 0.0                                           # the probe is relative to the housing centre
    c = NS(body=[h[0], h[1]], inward=P["REC_BODY_L"], flange=pr["flange"], past=pr["past"],
           housing=h, te=r.te, tip=pr["tip"], top=h[3])
    Dk = NS(ux=lambda xb: r.X + xc - xb, cy1=D.y_plate0 - pr["past"])
    shape = CU._standin_dt13(Dk, c, r.Z, r.Z + h[2])
    t, cc = r.te, P["CUTOUT_CLEAR"]
    sq = pr["seal_proud"]
    seal = L.box(r.seal[0], r.seal[1], D.y_plate0, D.y_plate0 + sq, r.seal[2], r.seal[3]).cut(
        L.rrect_xz(t["w"] + 2 * cc, t["h"] + 2 * cc, t["r"], r.X, r.Z, D.y_plate0 - 1,
                   D.y_plate0 + sq + 1))
    return L.fuse([shape, seal])


def build_insides(P, D, src, standin=False):
    """Everything inside the case and on its face, as named solids. `kind` is `part`, `plate`
    (the board and what the board's own glb draws: the headers, the tactile keys) or `keepout`
    (room kept clear, not a thing)."""
    oc = P["OVERCUT"]
    out = []

    # ---- the faceplate and its openings
    face = L.box(0.0, D.face_w, 0.0, D.y_face, 0.0, D.face_h)
    holes = []
    for c in D.controls:
        if c.hole[0] == "circ":
            holes.append(L.cyl_y(c.hole[1] / 2.0, c.X, c.Z, -oc, D.y_face + oc))
        else:
            holes.append(L.box(c.X - c.hole[1] / 2.0, c.X + c.hole[1] / 2.0, -oc, D.y_face + oc,
                               c.Z - c.hole[2] / 2.0, c.Z + c.hole[2] / 2.0))
    for (x, z) in D.panel_holes:
        holes.append(L.cyl_y(P["SCREW_CLEAR"] / 2.0, x, z, -oc, D.y_face + oc))
    out.append(_item("faceplate", L.cut(face, holes)))

    # ---- the caps and the switches under them
    for s in D.switches:
        c = s.cap
        w, h = c.size
        top = D.y_board0 - s.sw_h
        out.append(_item("control: %s" % c.name,
                         L.box(c.X - w / 2.0, c.X + w / 2.0, -P["CAP_PROUD"], top,
                               c.Z - h / 2.0, c.Z + h / 2.0)))
        b = s.box
        body = L.box(b[0], b[1], top, D.y_board0, b[2], b[3])
        if s.glb:                                      # the board's glb draws the 6 mm key
            out.append(_item("%s key switch (stand-in)" % s.ref, body, "plate"))
        else:
            out.append(_item("control: %s wink switch (P204 placeholder)" % s.ref, body))

    # ---- the mirror stick: body behind the face, lever through the well, knob in front
    st = D.stick
    b = st.box
    stick = L.fuse([L.box(b[0], b[1], D.y_board0 - P["STICK_BODY_H"], D.y_board0, b[2], b[3]),
                    L.cyl_y(P["STICK_SHAFT_D"] / 2.0, st.X, st.Z, -P["STICK_FLOAT"],
                            D.y_board0 - P["STICK_BODY_H"]),
                    L.cyl_y(P["STICK_KNOB_D"] / 2.0, st.X, st.Z, -P["STICK_PROUD"],
                            -P["STICK_FLOAT"])])
    out.append(_item("control: %s mirror stick (P156 placeholder)" % st.ref, stick))

    # ---- the screen knob: its encoder board off the plate, the encoder, the shaft, the knob in front
    if D.knob is not None:
        k, b = D.knob, D.knob.box
        y_kb1 = D.y_board0 - P["KNOB_STANDOFF"]
        y_kb0 = y_kb1 - P["KNOB_BOARD_T"]
        ew, eh, ed = P["KNOB_ENC"]
        y_enc = max(y_kb0 - ed, D.y_face)
        knob = L.fuse([L.box(b[0], b[1], y_kb0, y_kb1, b[2], b[3]),
                       L.box(k.X - ew / 2.0, k.X + ew / 2.0, y_enc, y_kb0, k.Z - eh / 2.0, k.Z + eh / 2.0),
                       L.cyl_y(P["KNOB_SHAFT_D"] / 2.0, k.X, k.Z, -P["KNOB_FLOAT"], y_enc),
                       L.cyl_y(P["KNOB_D"] / 2.0, k.X, k.Z, -P["KNOB_PROUD"], -P["KNOB_FLOAT"])])
        out.append(_item("control: %s screen knob and its encoder board (P219 placeholder)" % k.ref, knob))

    # ---- light pipes for the LEDs no opening lights
    for led in D.leds:
        if led.lit_by is None:
            out.append(_item("control: %s light pipe" % led.ref, L.cyl_y(
                P["LED_WINDOW_D"] / 2.0 - P["LED_PIPE_CLEAR"], led.X, led.Z, 0.0,
                D.y_board0 - P["LED_H"])))

    # ---- the board, its headers, the room behind it
    slab = L.rrect_xz(D.bw, D.bh, D.br, (D.bxl + D.bxr) / 2.0, (D.bzb + D.bzt) / 2.0,
                      D.y_board0, D.y_board1)
    slab = L.cut(slab, [L.cyl_y(d / 2.0, x, z, D.y_board0 - oc, D.y_board1 + oc)
                        for (_, x, z, d) in D.holes_xz if d > 0])
    out.append(_item("left plate board", slab, "plate"))
    for bp in D.pp.back:
        bb = D.bbox(bp.box)
        out.append(_item("%s header (stand-in)" % bp.ref,
                         L.box(bb[0], bb[1], D.y_board1, D.y_board1 + bp.h, bb[2], bb[3]),
                         "plate"))
    out.append(_item("keep-out: behind the board (headers and their plugs)",
                     L.box(D.bxl, D.bxr, D.y_board1, D.y_pko, D.bzb, D.bzt), "keepout"))

    # ---- the rear: receptacles, the grommet and its captive leads
    for r in D.conns:
        out.append(_item("%s (%s, stand-in)" % (r.name, r.part), _receptacle(P, D, r),
                         ref=r.name, dt13=True))
        hs = r.pr["housing"]
        out.append(_item("keep-out: wires into %s" % r.name,
                         L.box(r.X - hs[1], r.X - hs[0], D.y_room, D.y_rec0, r.Z + hs[2],
                               r.Z + hs[3]), "keepout"))
        out.append(_item("keep-out: mated plug on %s" % r.name,
                         L.box(r.plug[0], r.plug[1], D.y_plate1, D.y_plugs, r.plug[2],
                               r.plug[3]), "keepout"))
    if D.grommet:
        g = D.grommet
        ft = P["GROMMET_FLANGE_T"]
        body = L.fuse([L.cyl_y(P["GROMMET_BODY_D"] / 2.0, g.X, g.Z, D.y_plate0, D.y_plate1),
                       L.cyl_y(g.w / 2.0, g.X, g.Z, D.y_plate0 - ft, D.y_plate0),
                       L.cyl_y(g.w / 2.0, g.X, g.Z, D.y_plate1, D.y_plate1 + ft)])
        body = L.cut(body, [L.cyl_y(ld.od / 2.0, ld.X, ld.Z, D.y_plate0 - ft - oc,
                                    D.y_plate1 + ft + oc) for ld in g.leads])
        out.append(_item("grommet (sealed, %d leads, stand-in)" % len(g.leads), body))
        for ld in g.leads:
            out.append(_item("lead: %s, %s (captive)" % (ld.ref, ld.what), L.cyl_y(
                ld.od / 2.0, ld.X, ld.Z, D.y_plate0 - ft, D.y_plate1 + P["LEAD_STUB_L"])))
        out.append(_item("keep-out: leads turning to the grommet",
                         L.box(g.X - g.w / 2.0, g.X + g.w / 2.0, D.y_room, D.y_plate0 - ft,
                               g.Z - g.h / 2.0, g.Z + g.h / 2.0), "keepout"))
    return out


# --------------------------------------------------------------------------------------- case --
def build_case(P, D):
    """The climate unit's four printed parts, drawn by its own `build_case` from this unit's
    derive(): body (floor, walls, the roof over the board, the beam the lid lands on, the lid
    lugs, the plate's channel), rear plate (TE's cut-out for each receptacle), lid (gasket groove),
    front frame (ring and the standoffs to the board). Then what the CUR adds: the grommet's hole
    in the plate and the mounting ears on the body."""
    cp = dict(P)
    cp["SIDE_BOSS_D"] = 0.0                            # the CU's side bosses: the CUR has none
    case, feats = CU.build_case(cp, D)
    oc = P["OVERCUT"]
    if D.grommet:
        g = D.grommet
        case["rear_plate"] = L.cut(case["rear_plate"], [L.cyl_y(
            P["GROMMET_BODY_D"] / 2.0, g.X, g.Z, D.y_plate0 - oc, D.y_plate1 + oc)])
        feats["rear_plate"].append(("the plate round the grommet's hole",
                                    [g.X - g.w / 2.0, g.X + g.w / 2.0, D.y_plate0, D.y_plate1,
                                     g.Z - g.h / 2.0, g.Z + g.h / 2.0],
                                    "REAR_DX, REAR_DZ, GROMMET_BODY_D"))
    if D.ears:
        adds, bores = [], []
        y0, y1 = D.ear_y, D.ear_y + P["EAR_T"]
        z0, z1 = D.ear_z - P["EAR_W"] / 2.0, D.ear_z + P["EAR_W"] / 2.0
        for side in D.ears:
            x0, x1 = (D.bx0 - P["EAR_L"], D.bx0) if side == "left" else (D.bx1, D.bx1 + P["EAR_L"])
            xm = (x0 + x1) / 2.0 + (-1 if side == "left" else 1) * 0.0
            adds.append(L.box(x0, x1, y0, y1, z0, z1))
            bores.append(L.cyl_y(P["SCREW_CLEAR"] / 2.0, xm, D.ear_z, y0 - oc, y1 + oc))
            feats["body"].append(("mounting ear, %s" % side, [x0, x1, y0, y1, z0, z1],
                                  "EARS, EAR_Y, EAR_Z, EAR_L, EAR_W, EAR_T"))
        case["body"] = L.cut(L.fuse([case["body"]] + adds), bores)
    return case, feats


# ------------------------------------------------------------------------------------- checks --
def check(P, D, M, insides, case, feats):
    """Everything that is checked on the built solids: each {name, ok, detail}; ok False is exit
    code 1, None is said but not judged."""
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": ok, "detail": detail})

    sick = [k for k, s in case.items() if not s.isValid() or len(s.Solids) != 1]
    add("case parts are single sound solids", not sick,
        "all %d" % len(case) if not sick else "not sound: " + ", ".join(sick))
    sick = [it["name"] for it in insides if not it["shape"].isValid()]
    add("inside solids are sound", not sick,
        "all %d" % len(insides) if not sick else "not sound: " + ", ".join(sick))
    names = list(case)
    clash = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            c = CU._common(P, case[a], case[b])
            if c and c[1] >= L.CONTACT:
                clash.append("%s into %s, %s mm3" % (a, b, n(c[0])))
    add("case parts do not overlap each other", not clash,
        "none overlap" if not clash else "; ".join(clash))

    # ---- every inside solid against every case solid; a DT13 seal into the plate is squeeze
    hits, squeeze, touch = [], {}, 0
    for part, cs in case.items():
        for it in insides:
            c = CU._common(P, cs, it["shape"])
            if not c:
                continue
            vol, thin, box, pieces = c
            if it["dt13"] and part == "rear_plate" and thin <= P["SEAL_SQUEEZE_MAX"]:
                squeeze[it["ref"]] = (squeeze.get(it["ref"], (0.0, 0.0))[0] + vol, thin)
                continue
            if thin < L.CONTACT:
                touch += 1
                continue
            label, moves = CU._where(feats, part, pieces)
            what = "the room kept clear" if it["kind"] == "keepout" else "the part"
            hits.append("%s is inside %s '%s' by %s mm3 at X %s..%s, Y %s..%s, Z %s..%s%s"
                        % (label, what, it["name"].replace("keep-out: ", ""), n(vol),
                           n(box[0]), n(box[1]), n(box[2]), n(box[3]), n(box[4]), n(box[5]),
                           (": move one of them - %s" % moves) if moves else ""))
    add("insides clear of the case (%d solids against %d)" % (len(insides), len(case)), not hits,
        "0 interferences%s" % (("; %d faces resting on faces" % touch) if touch else "")
        if not hits else "%d interferences: %s" % (len(hits), " | ".join(hits)))
    for r in D.conns:
        got = squeeze.get(r.name)
        add("%s's flange seal squeezed against the rear plate" % r.name, bool(got),
            ("%s mm3, %s mm deep (TE's seal, probed; SEAL_SQUEEZE_MAX %s)"
             % (n(got[0]), n(got[1]), n(P["SEAL_SQUEEZE_MAX"]))) if got else
            "the seal does not reach the plate: the flange stands off it")

    # ---- the inside parts against each other (rooms kept clear are not parts)
    real = [it for it in insides if it["kind"] != "keepout"]
    hits = []
    for i, a in enumerate(real):
        for b in real[i + 1:]:
            c = CU._common(P, a["shape"], b["shape"])
            if c and c[1] >= L.CONTACT:
                hits.append("'%s' into '%s' by %s mm3 at X %s..%s, Y %s..%s, Z %s..%s"
                            % (a["name"], b["name"], n(c[0]), n(c[2][0]), n(c[2][1]), n(c[2][2]),
                               n(c[2][3]), n(c[2][4]), n(c[2][5])))
    add("inside parts clear of each other", not hits,
        "0 interferences" if not hits else "%d interferences: %s" % (len(hits), " | ".join(hits)))

    # ---- the margins the fit rules measured
    for name, (value, least) in M.items():
        add(name, value >= least - P["EPS"], "%s mm (least allowed %s)" % (n(value), n(least)))

    # ---- what each receptacle carries against its ways
    for r in D.conns:
        add("%s carries its leads' conductors" % r.name, r.conductors <= r.ways,
            "%d conductors (%s) on %d ways%s" % (
                r.conductors, " + ".join("%s %d" % (ld.ref, ld.ways) for ld in D.leads
                                         if ld.ref in r.carries), r.ways,
                "" if r.conductors <= r.ways else
                " - %d too many: J1 fills a %s alone (DP-DCU-E's twelve, D-492); the wink "
                "lead needs a receptacle of its own (RECEPTACLES) or the grommet beside it "
                "(take it out of %s's row) (block 01.41)" % (
                    r.conductors - r.ways, r.part, r.name)))
    if D.grommet:
        add("leads through the grommet", True, ", ".join(
            "%s (%d conductors, %s mm)" % (ld.ref, ld.ways, n(ld.od)) for ld in D.grommet.leads))

    ok, line = front_install(P, D)
    add("front install", True if ok else None, line.split(": ", 1)[1])
    if D.env is None:
        add("envelope (the opening left of the wheel)", None,
            "not measured - ENVELOPE is None, nothing checked (confirm)")
    else:
        for name, ok_, msg in D.env:
            add("envelope: " + name, ok_, msg)
    return checks


def front_install(P, D):
    if D.ears:
        return False, ("front install: no - the %s ear%s stand%s %s beyond the %s-wide body, so "
                       "the box goes in from behind the dash skin with the face fitted after "
                       "(provisional; EARS = [] for a box that slides in from the front)" % (
                           " and ".join(D.ears), "s" if len(D.ears) > 1 else "",
                           "" if len(D.ears) > 1 else "s", n(P["EAR_L"]), n(D.body_w)))
    return True, ("front install: yes - one height, %s x %s; it passes an opening that size "
                  "and the %s x %s face covers it" % (n(D.body_w), n(D.body_h), n(D.face_w),
                                                      n(D.face_h)))


# ------------------------------------------------------------------------------------ one run --
def connectors(D):
    """The rear row as the export and the scene read it: each receptacle's code and its place,
    the rear plate's outer face at the cut-out's centre, in the unit's frame."""
    out = []
    for r in D.conns:
        out.append({"code": r.name, "part": r.part, "at": [r.X, D.y_plate1, r.Z], "face": "rear",
                    "carries": r.carries, "conductors": r.conductors, "ways": r.ways,
                    "code_is": "provisional (block 01.41; no housings row yet)"})
    return out


def export_boards(D):
    """Where the plate board's glb goes in this unit (the export's child_place): its box in the
    unit's frame, [X0, X1, Y front face, Y back face, Z0, Z1]."""
    return {"plate": [D.bxl, D.bxr, D.y_board0, D.y_board1, D.bzb, D.bzt]}


def numbers(P, D):
    """The derived dimensions the report lists."""
    out = {
        "face_w": D.face_w, "face_w_is": "typed" if D.face_w_typed else "derived",
        "face_h": D.face_h, "face_h_is": "typed" if D.face_h_typed else "derived",
        "body_w": D.body_w, "body_h": D.body_h, "front_h": D.body_h, "rear_h": D.body_h,
        "stepped": False,
        "body_needed_by_board": D.board_need, "body_needed_by_rear": D.rear_need,
        "box_depth": D.y_end, "depth_to_plate_outer_face": D.y_plate1,
        "depth_to_receptacle_tips": D.y_tip if D.conns else None,
        "depth_with_plugs": D.y_plugs, "depth_overall": D.y_out,
        "board_gap": D.board_gap, "board_gap_least": D.board_gap_least,
        "board_back_h": D.back_h,
        "board": {"size": [D.bw, D.bh, D.bt], "x": [D.bxl, D.bxr], "y": [D.y_board0, D.y_board1],
                  "z": [D.bzb, D.bzt]},
        "rear": P["REAR"],
        "connectors": connectors(D),
        "grommet": None if not D.grommet else {
            "x": D.grommet.X, "y": D.y_plate1, "z": D.grommet.Z,
            "leads": [ld.ref for ld in D.grommet.leads]},
        "controls": [{"name": c.name, "kind": c.kind, "x": c.X, "z": c.Z} for c in D.controls],
        "leds": [{"ref": l.ref, "value": l.value, "x": l.X, "z": l.Z,
                  "lit": ("through the %s" % l.lit_by) if l.lit_by else "its own window"}
                 for l in D.leds],
        "ears": D.ears, "front_install": front_install(P, D)[0],
        "front_install_line": front_install(P, D)[1],
    }

    def tidy(v):
        if isinstance(v, float):
            return round(v, 3)
        if isinstance(v, list):
            return [tidy(x) for x in v]
        if isinstance(v, dict):
            return {k: tidy(x) for k, x in v.items()}
        return v
    return tidy(out)


def run(P, src, U):
    """Validate, build, check. Never raises for a parameter set that merely does not fit."""
    res = {"rc": 1, "problems": [], "checks": [], "numbers": None, "notes": list(src["notes"]),
           "insides": None, "case": None, "D": None}
    problems, D, M = validate(P, src, U)
    res["D"] = D
    if problems:
        res["problems"] = problems
        return res
    insides = build_insides(P, D, src)
    case, feats = build_case(P, D)
    res["checks"] = check(P, D, M, insides, case, feats)
    res["numbers"] = numbers(P, D)
    res["notes"] = D.notes
    res["insides"], res["case"] = insides, case
    res["rc"] = 1 if any(c["ok"] is False for c in res["checks"]) else 0
    return res


# ------------------------------------------------------------------------------------ outputs --
def clear_outputs(outdir):
    gone = []
    for name in OUTPUTS + tuple("view-%s.svg" % v for v in VIEWS):
        path = os.path.join(outdir, name)
        if os.path.exists(path):
            os.remove(path)
            gone.append(name)
    return gone


def write_model(outdir, insides, case):
    """cur-unit.FCStd (groups Insides > Keepouts, Case), one STEP per case part, and the assembly
    STEP (parts only)."""
    files = []
    doc = FreeCAD.newDocument("cur_unit")
    g_in = doc.addObject("App::DocumentObjectGroup", "Insides")
    g_keep = doc.addObject("App::DocumentObjectGroup", "Keepouts")
    g_in.addObject(g_keep)
    g_case = doc.addObject("App::DocumentObjectGroup", "Case")
    solid_objs = []
    for it in insides:
        keep = it["kind"] == "keepout"
        obj = doc.addObject("Part::Feature", CU._safe(it["name"]))
        obj.Label = it["name"]
        obj.Shape = it["shape"]
        (g_keep if keep else g_in).addObject(obj)
        if keep:
            try:
                obj.Visibility = False
            except Exception:
                pass
        else:
            solid_objs.append(obj)
    for name, s in case.items():
        obj = doc.addObject("Part::Feature", "case_" + name)
        obj.Label = "case: " + name
        obj.Shape = s
        g_case.addObject(obj)
        solid_objs.append(obj)
        path = os.path.join(outdir, "%s-%s.step" % (NAME, name))
        s.exportStep(path)
        files.append(path)
    doc.recompute()
    path = os.path.join(outdir, "%s.FCStd" % NAME)
    if os.path.exists(path):
        os.remove(path)
    doc.saveAs(path)
    files.append(path)
    path = os.path.join(outdir, "%s.step" % NAME)
    try:
        import Import
        Import.export(solid_objs, path)
    except Exception:
        Part.makeCompound([o.Shape for o in solid_objs]).exportStep(path)
    files.append(path)
    FreeCAD.closeDocument(doc.Name)
    return files


def write_views(P, outdir, insides, case, D):
    """Four orthographic line drawings by hidden-line projection, as the climate unit's: parts in
    black (hidden edges grey dashes), rooms kept clear in blue; on the front view the board's
    outline in orange, so the face round it shows."""
    import TechDraw
    M = FreeCAD.Matrix
    looks = {
        "front": M(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1),
        "back": M(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1),
        "side": M(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1),
        "top": M(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
    }
    said = {"front": "from the driver's seat", "back": "from behind, as it is plugged",
            "side": "from the right, the face to the left", "top": "from above, the face down"}
    parts = Part.makeCompound([it["shape"] for it in insides if it["kind"] != "keepout"] +
                              list(case.values()))
    rooms = Part.makeCompound([it["shape"] for it in insides if it["kind"] == "keepout"])
    files = []
    m, sw, dfl = P["VIEW_MARGIN"], P["VIEW_STROKE"], P["VIEW_DEFLECTION"]
    for view in VIEWS:
        a = parts.copy()
        a.transformShape(looks[view])
        b = rooms.copy()
        b.transformShape(looks[view])
        bb = FreeCAD.BoundBox(a.BoundBox)
        bb.add(b.BoundBox)
        pa = TechDraw.projectEx(a, V(0, 0, 1))
        pb = TechDraw.projectEx(b, V(0, 0, 1)) if view in ("side", "top", "back") else None
        flip = bb.YMax + bb.YMin
        w, h = bb.XLength + 2 * m, bb.YLength + 4 * m
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.1fmm" height="%.1fmm" '
               'viewBox="%.2f %.2f %.2f %.2f">' % (w, h, bb.XMin - m, bb.YMin - m, w, h),
               "<title>Control Unit Remote (CUR) mock-up - %s</title>" % view,
               '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="white"/>'
               % (bb.XMin - m, bb.YMin - m, w, h)]
        svg.append('<g fill="none" stroke="#9a9a9a" stroke-width="%.2f" stroke-dasharray="%.2f '
                   '%.2f">' % (sw / 2.0, 4 * sw, 4 * sw))
        svg += ['<path d="%s"/>' % d for k in (5, 8) for d in CU._paths(pa[k], flip, dfl)]
        svg.append("</g>")
        if pb:
            svg.append('<g fill="none" stroke="#2f6fb5" stroke-width="%.2f" stroke-dasharray='
                       '"%.2f %.2f">' % (sw, 8 * sw, 4 * sw))
            svg += ['<path d="%s"/>' % d for k in (0, 3) for d in CU._paths(pb[k], flip, dfl)]
            svg.append("</g>")
        svg.append('<g fill="none" stroke="black" stroke-width="%.2f" stroke-linecap="round">'
                   % sw)
        svg += ['<path d="%s"/>' % d for k in (0, 3) for d in CU._paths(pa[k], flip, dfl)]
        svg.append("</g>")
        extra = "; blue = room kept clear" if pb else ""
        if view == "front":
            svg.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" '
                       'stroke="#d9730d" stroke-width="%.2f" stroke-dasharray="%.2f %.2f"/>'
                       % (D.bxl, flip - D.bzt, D.bw, D.bh, sw, 8 * sw, 4 * sw))
            extra = "; orange = the plate board's %s x %s outline behind the face" % (
                n(D.bw), n(D.bh))
        for k, line in enumerate((
                "Control Unit Remote (CUR), mock-up: %s (%s), %.1f x %.1f mm, rear: %s."
                % (view, said[view], bb.XLength, bb.YLength, P["REAR"]),
                "Provisional, nothing measured%s." % extra)):
            svg.append('<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="%.2f">%s'
                       '</text>' % (bb.XMin, bb.YMax + (1.4 + 0.7 * k) * m, m / 2.5, line))
        svg.append("</svg>")
        path = os.path.join(outdir, "view-%s.svg" % view)
        with open(path, "w") as f:
            f.write("\n".join(svg) + "\n")
        files.append(path)
    return files


# ------------------------------------------------------------------------------------- report --
def report_json(path, P, U, res, files, views_note):
    def plain(v):
        if isinstance(v, (list, tuple)):
            return [plain(x) for x in v]
        if isinstance(v, dict):
            return {k: plain(x) for k, x in v.items()}
        return v
    data = {
        "what": "Control Unit Remote (CUR) mock-up (D-514, Y25) - provisional, nothing measured",
        "rc": res["rc"],
        "built": res["case"] is not None,
        "problems": res["problems"],
        "notes": res["notes"],
        "numbers": res["numbers"],
        "connectors": res["numbers"]["connectors"] if res["numbers"] else [],
        "front_install": res["numbers"]["front_install_line"] if res["numbers"] else None,
        "checks": res["checks"],
        "parameters": {k: plain(v) for k, v in P.items()},
        "confirm": U.CONFIRM,
        "files": [os.path.basename(f) for f in files],
        "views": views_note,
    }
    L.save(path, data)


def print_report(P, U, res, files, views_note, gone):
    D, N = res["D"], res["numbers"]
    bar = "=" * 96
    print(bar)
    print("Control Unit Remote (CUR) - MOCK-UP (D-514, Y25) - provisional, nothing measured (R11)")
    print(bar)
    for note in res["notes"]:
        print("note: " + note)
    if res["problems"]:
        print("REFUSED - %d fit rule%s failed; nothing was built:" %
              (len(res["problems"]), "" if len(res["problems"]) == 1 else "s"))
        for p in res["problems"]:
            print("  - " + p)
        if gone:
            print("removed the stale outputs of the last good build: " + ", ".join(gone))
        print("exit code 1")
        return
    print(N["front_install_line"])
    print("SIZE: the board is %s x %s; the body %s x %s (set by the %s across, the %s up), the "
          "face %s x %s (%s)." % (
              n(D.bw), n(D.bh), n(D.body_w), n(D.body_h),
              "board" if D.board_need[0] >= D.rear_need[0] else "rear row",
              "board" if D.board_need[1] >= D.rear_need[1] else "rear row",
              n(D.face_w), n(D.face_h),
              "derived: body + 2 x BEZEL_OVERLAP %s" % n(P["BEZEL_OVERLAP"])
              if not (D.face_w_typed or D.face_h_typed) else "typed"))
    print("DEPTH: board %s behind the face's rear (%s, least %s), %s kept behind it; box %s to the "
          "rear lip, %s overall%s." % (
              n(D.board_gap), "derived" if P["BOARD_GAP"] is None else "typed",
              n(D.board_gap_least), n(D.back_h), n(D.y_end), n(D.y_out),
              " with the plugs" if D.conns else " with the captive leads drawn"))
    print()
    print("face, from the board's footprints (X from the face's left, Z up):")
    for c in D.controls:
        fp = c.hole
        print("  %-30s X %7s  Z %6s  %s" % (c.name, n(c.X), n(c.Z),
                                            "%s x %s" % (n(fp[1]), n(fp[2])) if fp[0] == "rect"
                                            else "d %s" % n(fp[1])))
    for led in D.leds:
        print("  %-30s X %7s  Z %6s  %s" % (led.ref + " " + led.value, n(led.X), n(led.Z),
                                            "lit through the " + led.lit_by if led.lit_by
                                            else "its own window"))
    print()
    print("rear plate (%s):" % P["REAR"])
    for r in D.conns:
        print("  %-9s %-9s X %7s  Z %6s  carries %s: %d conductors on %d ways" % (
            r.name, r.part, n(r.X), n(r.Z), " + ".join(r.carries), r.conductors, r.ways))
    if D.grommet:
        print("  grommet             X %7s  Z %6s  leads %s, captive" % (
            n(D.grommet.X), n(D.grommet.Z), ", ".join(ld.ref for ld in D.grommet.leads)))
    print()
    print("checks:")
    for c in res["checks"]:
        mark = {True: "ok  ", False: "FAIL", None: "--  "}[c["ok"]]
        print("  %s %s: %s" % (mark, c["name"], c["detail"]))
    print()
    print("confirm (guesses until measured or bought - %d):" % len(U.CONFIRM))
    for k in sorted(U.CONFIRM):
        v = P[k]
        print("  %-18s %-10s %s" % (k, "(table)" if isinstance(v, (list, dict, tuple)) else
                                    "None" if v is None else v, U.CONFIRM[k]))
    print()
    for f in files:
        print("  wrote %-34s %9d bytes" % (os.path.basename(f), os.path.getsize(f)))
    if views_note:
        print("  views: " + views_note)
    print("exit code %d" % res["rc"])


# ------------------------------------------------------------------------------------ selftest --
OUTCOMES = CU.OUTCOMES


def selftest(U, src):
    """Rebuild under each parameter set of unit_params.SELFTEST, in memory (no files written), and
    hold each to the outcome stored with it. Exit 0 every set as expected; 1 an outcome differs;
    3 a set crashed."""
    import traceback
    rows, crashed = [], False
    for label, over, expect in U.SELFTEST:
        P = copy.deepcopy(U.P)
        P.update(copy.deepcopy(over))
        want = OUTCOMES.get(expect, "?? %r" % (expect,))
        try:
            res = run(P, src, U)
        except Exception:
            traceback.print_exc()
            rows.append((label, want, "CRASH", "see the traceback above", []))
            crashed = True
            continue
        if res["problems"]:
            rows.append((label, want, "REFUSED", "%d fit rule%s" % (
                len(res["problems"]), "" if len(res["problems"]) == 1 else "s"), res["problems"]))
            continue
        fails = [c for c in res["checks"] if c["ok"] is False]
        N = res["numbers"]
        size = "face %s x %s, body %s x %s, depth %s / %s overall, rear %s, front install %s" % (
            n(N["face_w"]), n(N["face_h"]), n(N["body_w"]), n(N["body_h"]), n(N["box_depth"]),
            n(N["depth_overall"]), N["rear"], "yes" if N["front_install"] else "no")
        rows.append((label, want, "BUILT, FAILS" if fails else "BUILT CLEAR", size,
                     ["%s: %s" % (c["name"], c["detail"]) for c in fails]))
    print("=" * 96)
    print("Control Unit Remote (CUR) mock-up - self-test: %d parameter sets" % len(rows))
    print("=" * 96)
    print("%-5s %-13s %-13s %s" % ("", "expected", "got", "set"))
    wrong = 0
    for label, want, got, size, why in rows:
        same = want == got
        wrong += 0 if same else 1
        print("%-5s %-13s %-13s %s" % ("ok" if same else "DIFF", want, got, label))
        print("%-33s %s" % ("", size))
        for w in why:
            print("%-33s - %s" % ("", w))
    count = {}
    for r in rows:
        count[r[2]] = count.get(r[2], 0) + 1
    print("-" * 96)
    print("; ".join("%d %s" % (v, k) for k, v in sorted(count.items())))
    rc = 3 if crashed else (1 if wrong else 0)
    print("%s - exit code %d" % (
        "a parameter set CRASHED" if crashed else
        ("%d of %d sets did NOT come out as expected" % (wrong, len(rows))) if wrong else
        "all %d sets came out as expected" % len(rows), rc))
    return rc
