"""The Control Unit Remote's mock-up (Y71; D-597, D-602, D-604, D-615): layout, fit rules, solids,
checks, output. Run by tools/mockup.py through FreeCAD's headless interpreter, never on its own.

Holds NO dimension: every number comes from control-unit-remote/data/cur_assembly_params.py, from the
face's geometry in tools/cur_board_sch.py (the D-602 face: FACE_W x FACE_H, the board at (EDGE, EDGE)),
or from the board it reads:

- cad/cur-board/cur-board.kicad_pcb   the CUR board: outline, thickness and every footprint, parsed here as
                                      text (no KiCad needed), so the face follows the board when it moves.

The unit: a front shell (the faceplate and four walls, one print) with a ledge the board's front rests on;
the board one encoder-body behind the face (the encoder's bushing through the face, its nut in front); a
cap per key through the face, a flange behind it, resting on its switch; the mirror control's knob in its
well; a rear cover whose lip plugs into the shell, its four posts pressing the board's corners, two M2
screws through the side walls into the lip, the pigtail through a grommet in its centre (D-615).

Four steps, in this order, and nothing is drawn until the second has passed:

    derive(P, src)      every position, from the parameters and the board - arithmetic only
    validate(P, src)    the fit rules: sentences naming the parameter and the way to move it
    build_*             the solids, all from what derive() returned
    check(...)          interference of every inside solid with every case solid, and the rest

Owns no fact in the record: the CUR is parts P156 / P198 / P199 / P204 / P219 / P226 / P249 / P250, its
connection DP-CUR on the pigtail (D-615).
"""
import copy
import importlib.util
import math
import os
import re
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

import enclosure_lib as L
import parts

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_spec = importlib.util.spec_from_file_location("cu_unit_lib", os.path.join(_HERE, "cu_assembly.py"))
CU = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CU)
import cur_board_sch as G  # noqa: E402  (the face's geometry: plain Python, no pcbnew at import)

NS, n, num = CU.NS, CU.n, CU.num
NAME = "cur-assembly"
CASE_PARTS = ("front_shell", "rear_cover")
OUTPUTS = ("%s.FCStd" % NAME, "%s.step" % NAME) + tuple("%s-%s.step" % (NAME, p) for p in CASE_PARTS)
VIEWS = ("front", "back", "side", "top")
SIDES = ("left", "right")
BOOLS = ("LED_WINDOW",)
WORDS = ("KEY_CAP_FROM", "MATERIAL")
TABLES = ("EARS", "BACK_HEIGHTS", "FRONT_HEIGHTS", "ENVELOPE")


# ------------------------------------------------------------------------------------ the board --
def _sexp(txt):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt)
    stack = [[]]
    for t in toks:
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop()
            stack[-1].append(done)
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return stack[0][0]


def _kids(node, name):
    return [k for k in node[1:] if isinstance(k, list) and k and k[0] == name]


def _one(node, name):
    k = _kids(node, name)
    return k[0] if k else None


def _xy(node):
    return float(node[1]), float(node[2])


def read_board(path):
    """The CUR board in KiCad's frame (mm, x right, y DOWN, seen from the front): outline box, thickness,
    and per footprint its ref, library name, side, place, pads and graphics in board coordinates."""
    root = _sexp(open(path, encoding="utf-8").read())
    gen = _one(root, "general")
    out = {"thickness": float(_one(gen, "thickness")[1]) if gen and _one(gen, "thickness") else None,
           "footprints": {}}
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
    if not xs:
        return out
    out["outline"] = [min(xs), max(xs), min(ys), max(ys)]
    for fp in _kids(root, "footprint"):
        at = _one(fp, "at")
        X, Y = _xy(at)
        a = math.radians(float(at[3])) if len(at) > 3 else 0.0
        back = (_one(fp, "layer") or [None, "F.Cu"])[1].startswith("B.")
        c, s = math.cos(a), math.sin(a)

        def tr(lx, ly, X=X, Y=Y, c=c, s=s):
            return (X + lx * c + ly * s, Y - lx * s + ly * c)
        props = {p[1]: p[2] for p in _kids(fp, "property") if len(p) > 2}
        gfx = []
        for g in fp[1:]:
            if not (isinstance(g, list) and g and g[0] in ("fp_line", "fp_rect", "fp_circle", "fp_poly")):
                continue
            lay = (_one(g, "layer") or [None, ""])[1]
            stroke = _one(g, "stroke")
            dashed = bool(stroke and _one(stroke, "type") and _one(stroke, "type")[1] == "dash")
            if g[0] == "fp_circle":
                cx, cy = _xy(_one(g, "center"))
                ex, ey = _xy(_one(g, "end"))
                gfx.append({"kind": "circle", "layer": lay, "dashed": dashed, "c": tr(cx, cy),
                            "r": math.hypot(ex - cx, ey - cy)})
                continue
            if g[0] == "fp_rect":
                (x0, y0), (x1, y1) = _xy(_one(g, "start")), _xy(_one(g, "end"))
                pts = [tr(x0, y0), tr(x1, y0), tr(x1, y1), tr(x0, y1)]
            elif g[0] == "fp_poly":
                pts = [tr(*_xy(q)) for q in _kids(_one(g, "pts"), "xy")]
            else:
                pts = [tr(*_xy(_one(g, k))) for k in ("start", "end") if _one(g, k)]
            gfx.append({"kind": g[0][3:], "layer": lay, "dashed": dashed,
                        "box": [min(p[0] for p in pts), max(p[0] for p in pts),
                                min(p[1] for p in pts), max(p[1] for p in pts)]})
        out["footprints"][props.get("Reference", "?")] = {
            "ref": props.get("Reference", "?"), "name": fp[1].split(":")[-1], "side": "back" if back else "front",
            "at": (X, Y), "value": props.get("Value", ""), "gfx": gfx}
    return out


def _rects(f, layer_end, dashed=None):
    return [g["box"] for g in f["gfx"] if g["kind"] == "rect" and g["layer"].endswith(layer_end)
            and (dashed is None or g["dashed"] == dashed)]


def _union(boxes):
    return [min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes)]


def load_source(cad_dir, P):
    src = {"problems": [], "notes": [], "board": None}
    pcb = parts.board_file("cur-board", "kicad_pcb")
    if not os.path.exists(pcb):
        src["problems"].append("cad/cur-board/cur-board.kicad_pcb is not there: draw it first "
                               "(tools/cur_board_sch.py sch, then pcb).")
        return src
    b = read_board(pcb)
    if "outline" not in b or not b["thickness"]:
        src["problems"].append("cur-board.kicad_pcb has no Edge.Cuts outline or no thickness: regenerate it.")
        return src
    src["board"] = b
    return src


# -------------------------------------------------------------------------------------- types --
def check_types(P, U):
    bad = []
    for name in U.UNIT:
        if name not in P:
            bad.append("%s is missing from the parameters." % name)
    for name in P:
        if name not in U.UNIT and name != "ENVELOPE":
            bad.append("%s is not a parameter of cur_assembly_params.py: check the spelling." % name)
    for name, v in P.items():
        if name in WORDS or name in TABLES:
            continue
        if name in BOOLS:
            if not isinstance(v, bool):
                bad.append("%s is %r: it must be True or False." % (name, v))
            continue
        if not num(v):
            bad.append("%s is %r: it must be a number in %s." % (name, v, U.UNIT.get(name, "mm")))
        elif v <= 0 and name not in ("CAP_CLEAR", "CAP_TRAVEL", "KNOB_HOLE_CLEAR", "COVER_CLEAR", "KNOB_FLOAT"):
            bad.append("%s is %s: it must be more than 0. Raise it." % (name, n(v)))
        elif v < 0:
            bad.append("%s is %s: it must be 0 or more. Raise it." % (name, n(v)))
    if not isinstance(P.get("EARS"), (list, tuple)) or any(e not in SIDES for e in P.get("EARS", [])):
        bad.append("EARS %r must be a list of 'left' and / or 'right' ([] = none)." % (P.get("EARS"),))
    env = P.get("ENVELOPE")
    if env is not None and not (isinstance(env, dict) and all(num(env.get(k)) and env[k] > 0
                                                              for k in ("OPENING_W", "OPENING_H", "DEPTH"))):
        bad.append("ENVELOPE must be None or {OPENING_W, OPENING_H, DEPTH} in mm.")
    return bad


# ------------------------------------------------------------------------------------- derive --
def derive(P, src):
    """Every position in the unit, in the unit's frame (X across, Y back, Z up), from the parameters and
    the board. Arithmetic only."""
    B = src["board"]
    fps = B["footprints"]
    D = NS(problems=[], notes=[])
    D.face_w, D.face_h = G.FACE_W, G.FACE_H
    ox, oy = G.EDGE, G.EDGE                       # the board's corner on the face (from the face's top-left)
    x0, x1, y0, y1 = B["outline"]
    D.bw, D.bh, D.t = x1 - x0, y1 - y0, B["thickness"]

    def X(bx):
        return ox + (bx - x0)

    def Z(by):
        return D.face_h - oy - (by - y0)
    D.X, D.Z = X, Z
    D.bxl, D.bxr, D.bzt, D.bzb = X(x0), X(x1), Z(y0), Z(y1)
    # the depths
    D.y_face = P["FACE_T"]
    D.y_b0 = P["FACE_T"] + P["ENC_BODY_H"]        # the board's front: the encoder's shoulder on the face's back
    D.y_b1 = D.y_b0 + D.t
    D.y_c = D.y_b1 + P["BACK_ROOM"]              # the shell's open end = the cover plate's inner face
    D.y_out = D.y_c + P["COVER_T"]
    # the shell
    ov, w = P["BEZEL_OVERLAP"], P["WALL"]
    D.body = (ov, D.face_w - ov, ov, D.face_h - ov)                         # X0 X1 Z0 Z1, outside
    D.inner = (ov + w, D.face_w - ov - w, ov + w, D.face_h - ov - w)
    D.body_w, D.body_h = D.body[1] - D.body[0], D.body[3] - D.body[2]
    # the front parts
    capf = fps.get(P["KEY_CAP_FROM"])
    cap_wh = None
    if capf and _rects(capf, "Fab", True):
        cb = _rects(capf, "Fab", True)[0]
        cap_wh = (cb[1] - cb[0], cb[3] - cb[2])
    else:
        D.problems.append("KEY_CAP_FROM %r has no dashed cap outline on F.Fab: name a wink switch, such as SW3."
                          % P["KEY_CAP_FROM"])
    D.caps, D.fronts, D.backs, D.leds = [], [], [], []
    D.enc = D.stick = D.j1 = None
    for ref in sorted(fps):
        f = fps[ref]
        nm = f["name"]
        if f["side"] == "back":
            cy = _rects(f, "CrtYd")
            if not cy:
                continue
            box = _union(cy)
            if ref == "J1":
                D.j1 = NS(ref=ref, box=box)
                continue
            key = ref if ref in P["BACK_HEIGHTS"] else re.sub(r"\d+$", "", ref)
            h = P["BACK_HEIGHTS"].get(key)
            if h is None:
                D.problems.append("%s on the board's back has no height in BACK_HEIGHTS: add it." % ref)
                continue
            D.backs.append(NS(ref=ref, box=box, h=h))
            continue
        body = _rects(f, "Fab", False)
        if nm.startswith(("WinkSwitch", "HazardSwitch", "SW_PUSH")):
            dash = _rects(f, "Fab", True)
            if dash:
                cb = dash[0]
                cw, ch = cb[1] - cb[0], cb[3] - cb[2]
            elif cap_wh:
                cw, ch = cap_wh
            else:
                continue
            cx, cy_ = f["at"]
            sw_h = P["WINK_SW_H"] if nm.startswith("Wink") else P["HAZ_SW_H"] if nm.startswith("Hazard") else P["KEY_SW_H"]
            D.caps.append(NS(ref=ref, value=f["value"], c=(X(cx), Z(cy_)), w=cw, h=ch, sw_h=sw_h,
                             body=_union(body) if body else None))
        elif nm.startswith("Thumbstick"):
            circ = [g for g in f["gfx"] if g["kind"] == "circle" and g["layer"].endswith("Fab")]
            D.stick = NS(ref=ref, c=(X(f["at"][0]), Z(f["at"][1])), well_d=2 * circ[0]["r"] if circ else None,
                         body=_union(body) if body else None)
        elif nm.startswith("ScreenKnob"):
            D.enc = NS(ref=ref, c=(X(f["at"][0]), Z(f["at"][1])), body=_union(body) if body else None)
        elif nm.startswith("LED"):
            cy = _rects(f, "CrtYd")
            D.leds.append(NS(ref=ref, value=f["value"], c=(X(f["at"][0]), Z(f["at"][1])), box=_union(cy) if cy else None,
                             h=P["FRONT_HEIGHTS"]["LED"]))
    if not D.caps or D.stick is None or D.enc is None:
        D.problems.append("The board has %d capped switches, %s mirror control and %s encoder: the CUR needs "
                          "every key, the mirror control and the screen knob's encoder."
                          % (len(D.caps), "a" if D.stick else "no", "an" if D.enc else "no"))
    # where each LED shines: the cap or the well over it
    for led in D.leds:
        led.lit_by = None
        for c in D.caps:
            if abs(led.c[0] - c.c[0]) <= c.w / 2 and abs(led.c[1] - c.c[1]) <= c.h / 2:
                led.lit_by = "%s's cap" % c.ref
        if D.stick and D.stick.well_d and math.hypot(led.c[0] - D.stick.c[0], led.c[1] - D.stick.c[1]) <= D.stick.well_d / 2:
            led.lit_by = "the mirror control's well"
    # the rear cover: its posts at the board's corners, the screws at the walls' middle, the grommet central
    i = P["POST_INSET"]
    D.posts = [(D.bxl + i, D.bzt - i), (D.bxr - i, D.bzt - i), (D.bxl + i, D.bzb + i), (D.bxr - i, D.bzb + i)]
    D.screw_y = D.y_c - P["COVER_LIP"] / 2.0
    D.screw_z = D.face_h / 2.0
    D.grommet = (D.face_w / 2.0, D.face_h / 2.0)
    D.lip_out = (D.inner[0] + P["COVER_CLEAR"], D.inner[1] - P["COVER_CLEAR"], D.inner[2] + P["COVER_CLEAR"],
                 D.inner[3] - P["COVER_CLEAR"])
    D.lip_in = (D.lip_out[0] + P["COVER_LIP_T"], D.lip_out[1] - P["COVER_LIP_T"], D.lip_out[2] + P["COVER_LIP_T"],
                D.lip_out[3] - P["COVER_LIP_T"])
    D.knob_front = -(P["ENC_NUT_T"] + P["KNOB_FLOAT"] + P["KNOB_PROUD"])
    return D


# ----------------------------------------------------------------------------------- validate --
def validate(P, src, U):
    """The fit rules. Each refusal names the parameter and the way to move it."""
    bad = list(src["problems"])
    if bad:
        return bad, None, None
    bad = check_types(P, U)
    if bad:
        return bad, None, None
    D = derive(P, src)
    bad = list(D.problems)
    if bad:
        return bad, D, None
    eps = P["EPS"]
    # the board inside the walls
    if D.bxl - D.inner[0] < P["GAP"] - eps or D.inner[1] - D.bxr < P["GAP"] - eps or \
            D.inner[3] - D.bzt < P["GAP"] - eps or D.bzb - D.inner[2] < P["GAP"] - eps:
        bad.append("WALL %s with BEZEL_OVERLAP %s leaves less than GAP %s round the board: the board is the face's "
                   "control area, so lower WALL or BEZEL_OVERLAP." % (n(P["WALL"]), n(P["BEZEL_OVERLAP"]), n(P["GAP"])))
    # every cap's opening and flange inside the walls, and no two flanges meeting
    fl = P["CAP_FLANGE"]
    for c in D.caps:
        x0, x1, z0, z1 = c.c[0] - c.w / 2 - fl, c.c[0] + c.w / 2 + fl, c.c[1] - c.h / 2 - fl, c.c[1] + c.h / 2 + fl
        if x0 < D.inner[0] - eps or x1 > D.inner[1] + eps or z0 < D.inner[2] - eps or z1 > D.inner[3] + eps:
            bad.append("%s's cap with its flange (CAP_FLANGE %s) reaches into the shell's wall: lower WALL, "
                       "BEZEL_OVERLAP or CAP_FLANGE." % (c.ref, n(fl)))
        need = c.sw_h + P["CAP_TRAVEL"] + P["CAP_FLANGE_T"]
        if P["ENC_BODY_H"] < need - eps:
            bad.append("ENC_BODY_H %s sets the board %s behind the face, but %s's cap needs %s (its switch %s, "
                       "CAP_TRAVEL, CAP_FLANGE_T): raise ENC_BODY_H (a taller encoder) or lower the switch."
                       % (n(P["ENC_BODY_H"]), n(P["ENC_BODY_H"]), c.ref, n(need), n(c.sw_h)))
    for i, a in enumerate(D.caps):
        for b in D.caps[i + 1:]:
            if abs(a.c[0] - b.c[0]) < (a.w + b.w) / 2 + 2 * fl - eps and abs(a.c[1] - b.c[1]) < (a.h + b.h) / 2 + 2 * fl - eps:
                bad.append("the flanges of %s's and %s's caps meet (CAP_FLANGE %s): lower CAP_FLANGE."
                           % (a.ref, b.ref, n(fl)))
    # the ledge: under the board's edge by LEDGE_BEAR at least, and clear of the board's front parts
    band = D.inner[0] + P["LEDGE_W"] - D.bxl
    if band < P["LEDGE_BEAR"] - eps:
        bad.append("LEDGE_W %s reaches only %s under the board's edge (LEDGE_BEAR %s): raise LEDGE_W." % (
            n(P["LEDGE_W"]), n(max(band, 0.0)), n(P["LEDGE_BEAR"])))
    if band > eps:
        things = [(c.ref, c.body) for c in D.caps if c.body] + [(led.ref, led.box) for led in D.leds if led.box]
        things += [(D.stick.ref, D.stick.body), (D.enc.ref, D.enc.body)]
        x0b, x1b, y0b, y1b = src["board"]["outline"]
        for ref, bx in things:
            if bx is None:
                continue
            if bx[0] < x0b + band or bx[1] > x1b - band or bx[2] < y0b + band or bx[3] > y1b - band:
                bad.append("LEDGE_W %s: the ledge under the board's edge reaches %s: lower LEDGE_W." % (n(P["LEDGE_W"]), ref))
    # the stick, the encoder
    if D.stick.well_d and P["STICK_KNOB_D"] >= D.stick.well_d:
        bad.append("STICK_KNOB_D %s does not move in its %s well: lower it." % (n(P["STICK_KNOB_D"]), n(D.stick.well_d)))
    if P["ENC_BUSHING_L"] < P["FACE_T"] + P["ENC_NUT_T"] - eps:
        bad.append("ENC_BUSHING_L %s does not reach through FACE_T %s and the nut %s: a longer bushing or a thinner face."
                   % (n(P["ENC_BUSHING_L"]), n(P["FACE_T"]), n(P["ENC_NUT_T"])))
    # the back
    tallest = max([b.h for b in D.backs] + [0.0])
    if P["BACK_ROOM"] < max(P["SOLDER_JOINT_H"], tallest) + P["GROMMET_FLANGE_T"] - eps or P["BACK_ROOM"] <= P["COVER_LIP"] + eps:
        bad.append("BACK_ROOM %s: the pigtail's joints (SOLDER_JOINT_H %s), the back's tallest part (%s), the grommet's "
                   "inner lip (%s) and the cover's lip (COVER_LIP %s) do not fit behind the board - raise BACK_ROOM."
                   % (n(P["BACK_ROOM"]), n(P["SOLDER_JOINT_H"]), n(tallest), n(P["GROMMET_FLANGE_T"]), n(P["COVER_LIP"])))
    # the grommet
    gx, gz = D.grommet
    r = P["GROMMET_FLANGE_D"] / 2.0
    if gx - r < D.lip_in[0] - eps or gx + r > D.lip_in[1] + eps or gz - r < D.lip_in[2] - eps or gz + r > D.lip_in[3] + eps:
        bad.append("GROMMET_FLANGE_D %s is wider than the cover inside its lip: lower it." % n(P["GROMMET_FLANGE_D"]))
    if P["PIGTAIL_D"] + 2 * P["GROMMET_WEB"] > P["GROMMET_HOLE_D"] + eps:
        bad.append("PIGTAIL_D %s with GROMMET_WEB %s does not fit the grommet's hole %s: a bigger hole or a thinner cable."
                   % (n(P["PIGTAIL_D"]), n(P["GROMMET_WEB"]), n(P["GROMMET_HOLE_D"])))
    # the envelope
    env = P["ENVELOPE"]
    if env:
        if D.body_w > env["OPENING_W"] - eps or D.body_h > env["OPENING_H"] - eps:
            bad.append("the shell, %s x %s, does not pass the opening %s x %s: the opening is too small for the face's "
                       "box." % (n(D.body_w), n(D.body_h), n(env["OPENING_W"]), n(env["OPENING_H"])))
        if D.face_w < env["OPENING_W"] or D.face_h < env["OPENING_H"]:
            bad.append("the face, %s x %s, does not cover the opening %s x %s." % (n(D.face_w), n(D.face_h),
                                                                                     n(env["OPENING_W"]), n(env["OPENING_H"])))
        if D.y_out > env["DEPTH"]:
            bad.append("the box is %s deep behind the face, more than DEPTH %s." % (n(D.y_out), n(env["DEPTH"])))
    return bad, D, None


# ------------------------------------------------------------------------------------- solids --
def _box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def _cyl_y(cx, cz, d, y0, y1):
    return Part.makeCylinder(d / 2.0, y1 - y0, V(cx, y0, cz), V(0, 1, 0))


def _cyl_x(cy, cz, d, x0, x1):
    return Part.makeCylinder(d / 2.0, x1 - x0, V(x0, cy, cz), V(1, 0, 0))


def _bx(D, box):
    """A board-coordinate box (x0 x1 y0 y1) as the unit's (X0 X1 Z0 Z1)."""
    return D.X(box[0]), D.X(box[1]), D.Z(box[3]), D.Z(box[2])


def build_insides(P, D, src, standin=False):
    out = []

    def add(name, shape, kind="part"):
        out.append({"name": name, "shape": shape, "kind": kind})
    add("CUR board", _box(D.bxl, D.bxr, D.y_b0, D.y_b1, D.bzb, D.bzt))
    for c in D.caps:
        if c.body:
            x0, x1, z0, z1 = _bx(D, c.body)
            add("switch %s" % c.ref, _box(x0, x1, D.y_b0 - c.sw_h, D.y_b0, z0, z1))
        cl, fl = P["CAP_CLEAR"], P["CAP_FLANGE"]
        y_end = D.y_b0 - c.sw_h
        body = _box(c.c[0] - c.w / 2 + cl, c.c[0] + c.w / 2 - cl, -P["CAP_PROUD"], y_end, c.c[1] - c.h / 2 + cl, c.c[1] + c.h / 2 - cl)
        y_f = D.y_face + P["CAP_TRAVEL"]
        flange = _box(c.c[0] - c.w / 2 - fl, c.c[0] + c.w / 2 + fl, y_f, y_f + P["CAP_FLANGE_T"], c.c[1] - c.h / 2 - fl, c.c[1] + c.h / 2 + fl)
        add("cap %s" % c.ref, body.fuse(flange).removeSplitter())
    s = D.stick
    x0, x1, z0, z1 = _bx(D, s.body)
    add("mirror control %s" % s.ref, _box(x0, x1, D.y_b0 - P["STICK_SW_H"], D.y_b0, z0, z1))
    add("mirror control's stem", _cyl_y(s.c[0], s.c[1], P["STICK_SHAFT_D"], -P["STICK_KNOB_PROUD"], D.y_b0 - P["STICK_SW_H"]))
    add("mirror control's knob", _cyl_y(s.c[0], s.c[1], P["STICK_KNOB_D"], -P["STICK_KNOB_PROUD"], -P["KNOB_FLOAT"]))
    e = D.enc
    x0, x1, z0, z1 = _bx(D, e.body)
    ex, ez = e.c
    add("encoder %s" % e.ref, _box(x0, x1, D.y_face, D.y_b0, z0, z1))
    add("encoder's bushing", _cyl_y(ex, ez, P["ENC_BUSHING_D"], D.y_face - P["ENC_BUSHING_L"], D.y_face))
    add("encoder's shaft", _cyl_y(ex, ez, P["ENC_SHAFT_D"], D.y_face - P["ENC_SHAFT_L"], D.y_face - P["ENC_BUSHING_L"]))
    add("encoder's nut", _cyl_y(ex, ez, P["ENC_NUT_AF"], -P["ENC_NUT_T"], 0.0).cut(
        _cyl_y(ex, ez, P["ENC_BUSHING_D"], -P["ENC_NUT_T"] - 1, 1)))
    add("screen knob", _cyl_y(ex, ez, P["KNOB_D"], D.knob_front, -(P["ENC_NUT_T"] + P["KNOB_FLOAT"])).cut(
        _cyl_y(ex, ez, P["ENC_SHAFT_D"], D.y_face - P["ENC_SHAFT_L"], 0.0)))
    for led in D.leds:
        if led.box:
            x0, x1, z0, z1 = _bx(D, led.box)
            add("LED %s" % led.ref, _box(x0, x1, D.y_b0 - led.h, D.y_b0, z0, z1))
    for b in D.backs:
        x0, x1, z0, z1 = _bx(D, b.box)
        add("%s (back)" % b.ref, _box(x0, x1, D.y_b1, D.y_b1 + b.h, z0, z1))
    if D.j1:
        x0, x1, z0, z1 = _bx(D, D.j1.box)
        add("pigtail joints J1 (room)", _box(x0, x1, D.y_b1, D.y_b1 + P["SOLDER_JOINT_H"], z0, z1), "keepout")
    gx, gz = D.grommet
    gr = _cyl_y(gx, gz, P["GROMMET_HOLE_D"], D.y_c, D.y_out)
    gr = gr.fuse(_cyl_y(gx, gz, P["GROMMET_FLANGE_D"], D.y_c - P["GROMMET_FLANGE_T"], D.y_c))
    gr = gr.fuse(_cyl_y(gx, gz, P["GROMMET_FLANGE_D"], D.y_out, D.y_out + P["GROMMET_FLANGE_T"]))
    add("grommet", gr.cut(_cyl_y(gx, gz, P["PIGTAIL_D"], D.y_c - 5, D.y_out + 5)).removeSplitter())
    add("pigtail (P200)", _cyl_y(gx, gz, P["PIGTAIL_D"], D.y_c - P["GROMMET_FLANGE_T"], D.y_out + P["PIGTAIL_L"]))
    return out


def build_case(P, D):
    oc = P["OVERCUT"]
    # the front shell: the faceplate, the walls, the ledge
    face = _box(0, D.face_w, 0, D.y_face, 0, D.face_h)
    for c in D.caps:
        face = face.cut(_box(c.c[0] - c.w / 2, c.c[0] + c.w / 2, -oc, D.y_face + oc, c.c[1] - c.h / 2, c.c[1] + c.h / 2))
    face = face.cut(_cyl_y(D.stick.c[0], D.stick.c[1], D.stick.well_d, -oc, D.y_face + oc))
    face = face.cut(_cyl_y(D.enc.c[0], D.enc.c[1], P["ENC_BUSHING_D"] + 2 * P["KNOB_HOLE_CLEAR"], -oc, D.y_face + oc))
    b, i = D.body, D.inner
    walls = _box(b[0], b[1], D.y_face, D.y_c, b[2], b[3]).cut(_box(i[0], i[1], D.y_face - oc, D.y_c + oc, i[2], i[3]))
    lw = P["LEDGE_W"]
    ledge = _box(i[0], i[1], D.y_b0 - P["LEDGE_H"], D.y_b0, i[2], i[3]).cut(
        _box(i[0] + lw, i[1] - lw, D.y_b0 - P["LEDGE_H"] - oc, D.y_b0 + oc, i[2] + lw, i[3] - lw))
    shell = face.fuse(walls).fuse(ledge)
    for x0, x1 in ((b[0] - oc, i[0] + oc), (i[1] - oc, b[1] + oc)):
        shell = shell.cut(_cyl_x(D.screw_y, D.screw_z, P["SCREW_D"], x0, x1))
    shell = shell.removeSplitter()
    # the rear cover: plate, lip, posts, grommet hole, screw pilots, ears
    plate = _box(b[0], b[1], D.y_c, D.y_out, b[2], b[3])
    lo, li = D.lip_out, D.lip_in
    lip = _box(lo[0], lo[1], D.y_c - P["COVER_LIP"], D.y_c, lo[2], lo[3]).cut(
        _box(li[0], li[1], D.y_c - P["COVER_LIP"] - oc, D.y_c + oc, li[2], li[3]))
    cover = plate.fuse(lip)
    for (px, pz) in D.posts:
        cover = cover.fuse(_cyl_y(px, pz, P["POST_D"], D.y_b1, D.y_c))
    for side in P["EARS"]:
        if side == "left":
            ear = _box(b[0] - P["EAR_L"], b[0], D.y_c, D.y_c + P["EAR_T"], D.face_h / 2 - P["EAR_W"] / 2, D.face_h / 2 + P["EAR_W"] / 2)
            hx = b[0] - P["EAR_L"] / 2
        else:
            ear = _box(b[1], b[1] + P["EAR_L"], D.y_c, D.y_c + P["EAR_T"], D.face_h / 2 - P["EAR_W"] / 2, D.face_h / 2 + P["EAR_W"] / 2)
            hx = b[1] + P["EAR_L"] / 2
        cover = cover.fuse(ear.cut(_cyl_y(hx, D.face_h / 2, P["EAR_HOLE_D"], D.y_c - oc, D.y_c + P["EAR_T"] + oc)))
    gx, gz = D.grommet
    cover = cover.cut(_cyl_y(gx, gz, P["GROMMET_HOLE_D"], D.y_c - oc, D.y_out + oc))
    cover = cover.cut(_cyl_x(D.screw_y, D.screw_z, P["SCREW_PILOT_D"], lo[0] - oc, li[0] + oc))
    cover = cover.cut(_cyl_x(D.screw_y, D.screw_z, P["SCREW_PILOT_D"], li[1] - oc, lo[1] + oc))
    cover = cover.removeSplitter()
    return {"front_shell": shell, "rear_cover": cover}, {}


# -------------------------------------------------------------------------------------- check --
def check(P, D, insides, case):
    res = []
    hits = []
    for it in insides:
        for cname, cs in case.items():
            try:
                v = it["shape"].common(cs).Volume
            except Exception:
                v = 0.0
            if v > P["VOLUME_EPS"]:
                hits.append("%s in the %s (%.2f mm3)" % (it["name"], cname.replace("_", " "), v))
    res.append({"name": "interference, every inside part and room against the case", "ok": not hits,
                "detail": "; ".join(hits) if hits else "none - %d parts and rooms, %d case parts" % (len(insides), len(case))})
    dark = [led.ref for led in D.leds if not led.lit_by]
    res.append({"name": "every LED shines through a cap or the well", "ok": not dark,
                "detail": ("unlit: " + ", ".join(dark)) if dark else ", ".join("%s via %s" % (l_.ref, l_.lit_by) for l_ in D.leds)})
    v = sum(s.Volume for s in case.values())
    res.append({"name": "the case's plastic", "ok": None, "detail": "%.1f cm3 of %s, the two parts" % (v / 1000.0, P["MATERIAL"])})
    return res


def numbers(P, D):
    return {"face_w": D.face_w, "face_h": D.face_h, "body_w": D.body_w, "body_h": D.body_h,
            "board": [D.bw, D.bh, D.t], "box_depth": D.y_out, "depth_overall": D.y_out - D.knob_front,
            "rear": "pigtail through a grommet (D-615)", "front_install": True, "connectors": [],
            "front_install_line": "INSTALL: from the front - the shell (%s x %s) passes an opening its own size, the face "
                                  "(%s x %s) covers the edge, the ears screw to a bracket behind." % (
                                      n(D.body_w), n(D.body_h), n(D.face_w), n(D.face_h))}


def run(P, src, U):
    res = {"rc": 1, "problems": [], "checks": [], "numbers": None, "notes": list(src["notes"]),
           "insides": None, "case": None, "D": None}
    problems, D, _M = validate(P, src, U)
    res["D"] = D
    if problems:
        res["problems"] = problems
        return res
    insides = build_insides(P, D, src)
    case, _f = build_case(P, D)
    res["checks"] = check(P, D, insides, case)
    res["numbers"] = numbers(P, D)
    res["notes"] = D.notes
    res["insides"], res["case"] = insides, case
    res["rc"] = 1 if any(c["ok"] is False for c in res["checks"]) else 0
    return res


# ------------------------------------------------------------------------------------ outputs --
def clear_outputs(outdir):
    gone = []
    for name in OUTPUTS + tuple("%s-view-%s.svg" % (NAME, v) for v in VIEWS):
        path = os.path.join(outdir, name)
        if os.path.exists(path):
            os.remove(path)
            gone.append(name)
    return gone


def write_model(outdir, insides, case):
    """cur-assembly.FCStd (groups Insides > Keepouts, Case), one STEP per case part, and the assembly STEP."""
    for old in ("body", "rear_plate", "lid", "front_frame"):         # the plate unit's parts, retired by D-615
        p = os.path.join(outdir, "%s-%s.step" % (NAME, old))
        if os.path.exists(p):
            os.remove(p)
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
        obj.Label = "case: " + name.replace("_", " ")
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
    """Four orthographic line drawings by hidden-line projection: parts in black (hidden edges grey dashes),
    rooms kept clear in blue; on the front view the board's outline in orange."""
    import TechDraw
    M = FreeCAD.Matrix
    looks = {
        "front": M(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1),
        "back": M(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1),
        "side": M(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1),
        "top": M(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
    }
    said = {"front": "from the driver's seat", "back": "from behind, the pigtail leaving",
            "side": "from the right, the face to the left", "top": "from above, the face down"}
    solids = Part.makeCompound([it["shape"] for it in insides if it["kind"] != "keepout"] + list(case.values()))
    rooms = Part.makeCompound([it["shape"] for it in insides if it["kind"] == "keepout"])
    files = []
    m, sw, dfl = P["VIEW_MARGIN"], P["VIEW_STROKE"], P["VIEW_DEFLECTION"]
    for view in VIEWS:
        a = solids.copy()
        a.transformShape(looks[view])
        b = rooms.copy()
        b.transformShape(looks[view])
        bb = FreeCAD.BoundBox(a.BoundBox)
        bb.add(b.BoundBox)
        pa = TechDraw.projectEx(a, V(0, 0, 1))
        pb = TechDraw.projectEx(b, V(0, 0, 1)) if view in ("side", "top", "back") else None
        flip = bb.YMax + bb.YMin
        w, h = bb.XLength + 2 * m, bb.YLength + 4 * m
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.1fmm" height="%.1fmm" viewBox="%.2f %.2f %.2f %.2f">'
               % (w, h, bb.XMin - m, bb.YMin - m, w, h),
               "<title>Control Unit Remote (CUR) mock-up - %s</title>" % view,
               '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="white"/>' % (bb.XMin - m, bb.YMin - m, w, h)]
        svg.append('<g fill="none" stroke="#9a9a9a" stroke-width="%.3f" stroke-dasharray="%.2f %.2f">' % (sw / 2.0, 4 * sw, 4 * sw))
        svg += ['<path d="%s"/>' % d for k in (5, 8) for d in CU._paths(pa[k], flip, dfl)]
        svg.append("</g>")
        if pb:
            svg.append('<g fill="none" stroke="#2f6fb5" stroke-width="%.3f" stroke-dasharray="%.2f %.2f">' % (sw, 8 * sw, 4 * sw))
            svg += ['<path d="%s"/>' % d for k in (0, 3) for d in CU._paths(pb[k], flip, dfl)]
            svg.append("</g>")
        svg.append('<g fill="none" stroke="black" stroke-width="%.3f" stroke-linecap="round">' % sw)
        svg += ['<path d="%s"/>' % d for k in (0, 3) for d in CU._paths(pa[k], flip, dfl)]
        svg.append("</g>")
        extra = "; blue = room kept for the pigtail's joints" if pb else ""
        if view == "front":
            svg.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="#d9730d" stroke-width="%.3f" '
                       'stroke-dasharray="%.2f %.2f"/>' % (D.bxl, flip - D.bzt, D.bw, D.bh, sw, 8 * sw, 4 * sw))
            extra = "; orange = the board's %s x %s outline" % (n(D.bw), n(D.bh))
        for k, line in enumerate((
                "CUR mock-up - %s (%s), %.1f x %.1f mm" % (view, said[view], bb.XLength, bb.YLength),
                "the D-602 face; the pigtail through the rear grommet (D-615); board rev %s" % G.REV,
                "nothing measured or bought (R11)%s" % extra)):
            svg.append('<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="%.2f">%s</text>'
                       % (bb.XMin, bb.YMax + (1.2 + 0.55 * k) * m, m / 4.0, line))
        svg.append("</svg>")
        path = os.path.join(outdir, "%s-view-%s.svg" % (NAME, view))
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
    L.save(path, {
        "what": "Control Unit Remote (CUR) mock-up (Y71, D-602, D-615) - provisional, nothing measured",
        "rc": res["rc"], "built": res["case"] is not None, "problems": res["problems"], "notes": res["notes"],
        "numbers": res["numbers"], "checks": res["checks"], "parameters": {k: plain(v) for k, v in P.items()},
        "confirm": U.CONFIRM, "files": [os.path.basename(f) for f in files], "views": views_note})


def print_report(P, U, res, files, views_note, gone):
    D, N = res["D"], res["numbers"]
    bar = "=" * 96
    print(bar)
    print("Control Unit Remote (CUR) - MOCK-UP (Y71, D-602, D-615) - provisional, nothing measured (R11)")
    print(bar)
    if res["problems"]:
        print("REFUSED - %d fit rule%s failed; nothing was built:" % (len(res["problems"]), "" if len(res["problems"]) == 1 else "s"))
        for p in res["problems"]:
            print("  - " + p)
        if gone:
            print("removed the stale outputs of the last good build: " + ", ".join(gone))
        print("exit code 1")
        return
    print(N["front_install_line"])
    print("SIZE: face %s x %s; shell %s x %s; board %s x %s x %s." % (n(D.face_w), n(D.face_h), n(D.body_w), n(D.body_h),
                                                                     n(D.bw), n(D.bh), n(D.t)))
    print("DEPTH: board front %s behind the face's front (the encoder's body), the box %s deep, %s with the knob." % (
        n(D.y_b0), n(D.y_out), n(N["depth_overall"])))
    print()
    print("the face's openings, from the board (X from the face's left, Z up):")
    for c in D.caps:
        print("  %-6s cap %s x %s at X %s Z %s, switch %s tall" % (c.ref, n(c.w), n(c.h), n(c.c[0]), n(c.c[1]), n(c.sw_h)))
    print("  %-6s well d %s at X %s Z %s" % (D.stick.ref, n(D.stick.well_d), n(D.stick.c[0]), n(D.stick.c[1])))
    print("  %-6s bushing d %s at X %s Z %s, knob d %s" % (D.enc.ref, n(P["ENC_BUSHING_D"]), n(D.enc.c[0]), n(D.enc.c[1]), n(P["KNOB_D"])))
    for led in D.leds:
        print("  %-6s lit through %s" % (led.ref, led.lit_by))
    print()
    print("checks:")
    for c in res["checks"]:
        mark = {True: "ok  ", False: "FAIL", None: "--  "}[c["ok"]]
        print("  %s %s: %s" % (mark, c["name"], c["detail"]))
    print()
    print("confirm (guesses until measured or bought - %d)" % len(U.CONFIRM))
    for f in files:
        print("  wrote %-36s %9d bytes" % (os.path.basename(f), os.path.getsize(f)))
    if views_note:
        print("  views: " + views_note)
    print("exit code %d" % res["rc"])


# ------------------------------------------------------------------------------------ selftest --
OUTCOMES = CU.OUTCOMES


def selftest(U, src):
    """Rebuild under each parameter set of the table's SELFTEST, in memory (no files written), and hold each to
    the outcome stored with it. Exit 0 every set as expected; 1 an outcome differs; 3 a set crashed."""
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
            rows.append((label, want, "REFUSED", "%d fit rule%s" % (len(res["problems"]), "" if len(res["problems"]) == 1 else "s"),
                         res["problems"]))
            continue
        fails = [c for c in res["checks"] if c["ok"] is False]
        N = res["numbers"]
        size = "face %s x %s, shell %s x %s, %s deep" % (n(N["face_w"]), n(N["face_h"]), n(N["body_w"]), n(N["body_h"]), n(N["box_depth"]))
        rows.append((label, want, "BUILT, FAILS" if fails else "BUILT CLEAR", size, ["%s: %s" % (c["name"], c["detail"]) for c in fails]))
    print("=" * 96)
    print("Control Unit Remote (CUR) mock-up - self-test: %d parameter sets" % len(rows))
    print("=" * 96)
    wrong = 0
    for label, want, got, size, why in rows:
        same = want == got
        wrong += 0 if same else 1
        print("%-5s %-13s %-13s %s" % ("ok" if same else "DIFF", want, got, label))
        print("%-33s %s" % ("", size))
        for w in why:
            print("%-33s - %s" % ("", w))
    rc = 3 if crashed else (1 if wrong else 0)
    print("-" * 96)
    print("%s - exit code %d" % ("a parameter set CRASHED" if crashed else
                                 ("%d of %d sets did NOT come out as expected" % (wrong, len(rows))) if wrong else
                                 "all %d sets came out as expected" % len(rows), rc))
    return rc
