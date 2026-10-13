"""The climate control unit's mock-up (D-479, D-480, Y14): layout, fit rules, solids, checks, output.

Run by `make_unit.py` through FreeCAD's headless interpreter, never on its own. Holds NO dimension:
every number comes from `unit_params.py` (the parameter table), from `../../../tools/enclosure_lib.py` (TE's
DT13 panel cut-outs, the primitives) or from the DCU carrier's own files, which it only reads:

- `../dcu-carrier/enclosure/board.json`  the carrier's outline, holes and footprints;
- `../dcu-carrier/enclosure/probe.json`  each DT13's flange, housing section and height, as read
                                          from TE's models by the DCU enclosure build;
- `../dcu-carrier/dcu-carrier.step`      the board's 3D model, when it is there (git-ignored). With
                                          it the real board goes in the box; without it, or when
                                          CARRIER_W / CARRIER_D are not the drawn board's, plain
                                          stand-in blocks of the same sizes do.

Four steps, in this order, and nothing is drawn until the second has passed:

    derive(P, src)      every position, from the parameters - arithmetic only
    validate(P, src)    the fit rules: sentences naming the parameter and the way to move it
    build_*             the solids, all from what derive() returned
    check(...)          interference of every inside solid with every case solid, and the rest

Frame: X across the face (0 = left seen from the cabin), Y back from the faceplate's front, Z up
from the faceplate's bottom edge. Owns no fact in the record: the sizes that place this unit are
work rows V-102 and V-113 (`01-electrical/data/work.csv`); the parts are P152, P194, P195.
"""
import copy
import math
import os

import FreeCAD
import Part
from FreeCAD import Vector as V

import enclosure_lib as L

KINDS = {"window": ("w", "h"), "knob": ("d",), "key": ("w", "h"), "slot": ("w", "h")}
NONE_OK = ("FACE_W", "FACE_H", "PANEL_RIBBON_X")
ANCHORS = ("centre", "top", "bottom")
ZERO_OK = ("SCREEN_BORDER", "KNOB_FLOAT", "KEY_CLEAR", "PADDLE_CLEAR", "CUTOUT_CLEAR", "TOP_GAP",
           "CARRIER_FRONT_GAP", "CARRIER_BOT_H", "UPPER_BOT_H", "UPPER_CONN_GAP",
           "PLATE_LIP", "FLOOR_GROOVE", "SLOT_DEPTH", "SLOT_CLEAR", "PLUG_ROW_CLEAR", "CABLE_BEND",
           "PLUG_SIDE_CLEAR", "PLUG_GROW", "CONTROL_EDGE", "CONTROL_GAP", "CONTROL_BEHIND_CLEAR",
           "BEZEL_OVERLAP", "GAP", "LUG_EMBED", "INSERT_SKIN", "BOSS_H",
           "BOARD_JSON_EDGE", "OUTLINE_TOL", "COURTYARD_MATCH", "SEAL_SQUEEZE_MAX", "VOLUME_EPS",
           "EPS", "GASKET_R", "PANEL_RIBBON_Z", "PANEL_HOLE_INSET", "CARRIER_HOLE_INSET", "RIM_H")
OUTPUTS = ("climate-unit.FCStd", "climate-unit.step", "climate-unit-body.step",
           "climate-unit-rear_plate.step", "climate-unit-lid.step", "climate-unit-front_frame.step")
VIEWS = ("front", "back", "side", "top")


class NS(dict):
    """A dict read with dots."""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def n(x):
    s = "%.2f" % x
    return s.rstrip("0").rstrip(".")


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v


# ------------------------------------------------------------------------------------- source --
def load_source(cad_dir, P):
    """The carrier's files, read once: board.json, probe.json and the STEP if it is there."""
    car = os.path.join(cad_dir, "dcu-carrier")
    enc = os.path.join(car, "enclosure")
    src = {"problems": [], "notes": [], "step": None}
    for name in ("board.json", "probe.json"):
        path = os.path.join(enc, name)
        if not os.path.exists(path):
            src["problems"].append(
                "%s is missing from dcu-carrier/enclosure: run that folder's make_enclosure.py "
                "(and 00-design/tools/enclosure_extract.py dcu-carrier) first - this mock-up reads the carrier "
                "from it." % name)
            return src
        src[name.split(".")[0]] = L.load(path)
    board = src["board"]
    step = os.path.join(car, "dcu-carrier.step")
    if not os.path.exists(step):
        src["notes"].append("dcu-carrier.step is not there: the carrier is drawn as stand-in "
                            "blocks from board.json and probe.json")
        return src
    solids = Part.read(step).Solids
    thin = [s for s in solids if s.BoundBox.ZLength <= board["thickness"] + P["OUTLINE_TOL"]]
    if not thin:
        src["notes"].append("dcu-carrier.step holds no board solid: stand-in blocks used")
        return src
    slab = max(thin, key=lambda s: s.BoundBox.XLength * s.BoundBox.YLength)
    items = []
    for s in solids:
        ref = "?"
        if s.isSame(slab):
            ref = "board"
        else:
            c = s.BoundBox.Center
            for f in board["footprints"]:
                if L._in_box(c.x, c.y, f["courtyard"], P["COURTYARD_MATCH"]):
                    ref = f["ref"]
                    break
        items.append((ref, s))
    src["step"] = items
    src["step_board"] = [slab.BoundBox.XLength, slab.BoundBox.YLength]
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
        elif v < 0 or (v == 0 and name not in ZERO_OK):
            bad.append("%s is %s: it must be %s. Raise it."
                       % (name, n(v), "0 or more" if name in ZERO_OK else "more than 0"))
    if bad:
        return bad
    for row in P["CONTROLS"]:
        ok = (isinstance(row, (tuple, list)) and len(row) == 5 and row[1] in KINDS
              and num(row[2]) and num(row[3]) and isinstance(row[4], dict)
              and all(num(row[4].get(k)) and row[4][k] > 0 for k in KINDS[row[1]]))
        if not ok:
            bad.append("CONTROLS row %r is not (name, kind, x, z, size): kind is one of %s and "
                       "size holds %s, all more than 0."
                       % (row, ", ".join(sorted(KINDS)), "w and h, or d for a knob"))
    for row in P["UPPER_CONNECTORS"]:
        if not (isinstance(row, (tuple, list)) and len(row) == 3 and isinstance(row[1], int)
                and isinstance(row[2], bool)):
            bad.append("UPPER_CONNECTORS row %r is not (name, ways, fitted True/False)." % (row,))
    if P["CONTROLS_ANCHOR"] not in ANCHORS:
        bad.append("CONTROLS_ANCHOR is %r: it must be one of %s."
                   % (P["CONTROLS_ANCHOR"], ", ".join(repr(a) for a in ANCHORS)))
    for name in ("UPPER_STANDOFFS", "SIDE_SCREWS"):
        for row in P[name]:
            if not (isinstance(row, (tuple, list)) and len(row) == 2 and num(row[0])
                    and num(row[1])):
                bad.append("%s row %r is not a pair of numbers in mm." % (name, row))
    if not P["LID_LUGS"] or not all(num(f) and 0 <= f <= 1 for f in P["LID_LUGS"]):
        bad.append("LID_LUGS %r must be one or more fractions from 0 (the step wall) to 1 (the "
                   "rear plate)." % (P["LID_LUGS"],))
    env = P["ENVELOPE"]
    if env is not None:
        ok = isinstance(env, dict) and all(num(env.get(k)) and env[k] > 0
                                           for k in ("OPENING_W", "OPENING_H", "DEPTH"))
        ok = ok and (env.get("BEHIND_H") is None or (num(env["BEHIND_H"]) and env["BEHIND_H"] > 0))
        if not ok:
            bad.append("ENVELOPE must be None or {OPENING_W, OPENING_H, DEPTH, BEHIND_H} in mm "
                       "(BEHIND_H may be None).")
    return bad


# ------------------------------------------------------------------------------------- derive --
def derive(P, src):
    """Every position in the unit, from the parameters and the carrier's files. Arithmetic only."""
    TE = L.TE_CUTOUT
    board, pr = src["board"], src["probe"]
    D = NS(problems=[], notes=list(src["notes"]))
    e, tol = P["BOARD_JSON_EDGE"], P["OUTLINE_TOL"]
    o = board["outline"]
    drawn_w, drawn_d = o["xmax"] - o["xmin"] - 2 * e, o["ymax"] - o["ymin"] - 2 * e
    W, DP = P["CARRIER_W"], P["CARRIER_D"]
    D.drawn_size = [drawn_w, drawn_d]
    D.drawn = abs(drawn_w - W) <= tol and abs(drawn_d - DP) <= tol
    yb_edge = o["ymin"] + e                       # the connector edge, in the board's own frame

    # ---- the lower row: the carrier's own DT13s, as board.json and probe.json have them
    lows = []
    for f in board["footprints"]:
        if not L.is_dt13(f) or f["dnp"]:
            continue
        d = pr["dt13"].get(f["ref"]) or {}
        r = pr["refs"].get(f["ref"])
        if not d.get("model") or r is None or d.get("outward") != -1 or f["footprint"] not in TE:
            D.problems.append(
                "probe.json has no usable model of %s (%s) on the carrier's connector edge: "
                "re-run dcu-carrier/enclosure/make_enclosure.py with the board STEP present."
                % (f["ref"], f["footprint"]))
            continue
        c, h = f["courtyard"], d["housing"]
        lows.append(NS(ref=f["ref"], name=f["value"].split()[0], part=f["footprint"],
                       te=TE[f["footprint"]], fitted=True, row="lower",
                       xb=(h[0] + h[1]) / 2.0, zc=(h[2] + h[3]) / 2.0, flange=d["flange"],
                       housing=h, past=d["flange_front_past_board_edge"],
                       tip=yb_edge - d["y_tip"], body=[r[0], r[1]], inward=r[3] - yb_edge,
                       top=r[5], court=[c[0], c[1]], court_in=c[3] - yb_edge))
    if not lows or D.problems:
        if not lows:
            D.problems.append("board.json has no fitted DT13 on the carrier: nothing to build "
                              "the rear plate around.")
        return D
    lows.sort(key=lambda c: c.xb)
    span = [min(c.court[0] for c in lows), max(c.court[1] for c in lows)]
    D.edge_need = span[1] - span[0]
    xcb = (o["xmin"] + o["xmax"]) / 2.0 if D.drawn else (span[0] + span[1]) / 2.0
    xb0 = xcb - W / 2.0                           # the carrier's left edge, board frame
    yb_front = yb_edge + DP
    if not D.drawn:
        D.notes.append("CARRIER_W x CARRIER_D %s x %s is not the drawn board (%s x %s): a plain "
                       "slab stands in, its three connectors kept at their drawn spacing and "
                       "centred on it" % (n(W), n(DP), n(drawn_w), n(drawn_d)))

    # ---- across the face (X)
    G, WL, BZ = P["GAP"], P["WALL"], P["BEZEL_OVERLAP"]
    eps = P["EPS"]
    D.body_w_need = W + 2 * (G + WL)
    D.face_w_typed = P["FACE_W"] is not None
    D.face_w = P["FACE_W"] if D.face_w_typed else D.body_w_need + 2 * BZ
    D.xc = D.face_w / 2.0
    D.bx0, D.bx1 = BZ, D.face_w - BZ
    D.ix0, D.ix1 = D.bx0 + WL, D.bx1 - WL
    D.body_w = D.bx1 - D.bx0
    D.cx0, D.cx1 = D.xc - W / 2.0, D.xc + W / 2.0

    def ux(xb):
        return D.xc + xcb - xb

    def uy(yb):
        return D.cy0 + yb_front - yb

    D.ux, D.uy = ux, uy

    # ---- up (Z), as far as the two rows: none of this depends on the face
    D.zb = BZ
    D.zf = D.zb + P["FLOOR"]
    D.cz0 = D.zf + P["BOSS_H"]
    D.cz1 = D.cz0 + P["CARRIER_T"]
    for c in lows:
        c.X, c.Z, c.z_top = ux(c.xb), D.cz0 + c.zc, D.cz0 + c.top
    D.lows = lows

    # ---- the upper row
    ups = []
    by_part = {}
    for c in lows:
        by_part.setdefault(c.part, c)
    above = [c for c in lows if c.ref == P["UPPER_ABOVE"]]
    if P["UPPER_CONNECTORS"] and not above:
        D.problems.append("UPPER_ABOVE %r is not a DT13 on the carrier: use one of %s."
                          % (P["UPPER_ABOVE"], ", ".join(c.ref for c in lows)))
        return D
    toward = 1.0
    for (name, ways, fitted) in P["UPPER_CONNECTORS"]:
        part = "DT13-%02dPA" % ways
        twin = by_part.get(part)
        if twin is None:
            D.problems.append(
                "UPPER_CONNECTORS: %r is a %d-way, but the carrier carries no %s to take its "
                "size from: use %s ways." % (name, ways, part, " / ".join(
                    str(int(p[5:7])) for p in sorted(by_part))))
            continue
        cw = twin.court[1] - twin.court[0]
        if not ups:
            xb = above[0].xb
            toward = 1.0 if xb < xcb else -1.0
        else:
            xb = ups[-1].xb + toward * ((ups[-1].cw + cw) / 2.0 + P["UPPER_CONN_GAP"])
        ups.append(NS(ref="U%d" % (len(ups) + 1), name=name, part=part, te=twin.te, twin=twin,
                      fitted=fitted, row="upper", xb=xb, cw=cw, zc=twin.zc, past=twin.past,
                      tip=twin.tip, inward=twin.inward, court_in=twin.court_in,
                      flange=[twin.flange[0] - twin.xb + xb, twin.flange[1] - twin.xb + xb,
                              twin.flange[2], twin.flange[3]],
                      housing=[twin.housing[0] - twin.xb + xb, twin.housing[1] - twin.xb + xb,
                               twin.housing[2], twin.housing[3]],
                      body=[twin.body[0] - twin.xb + xb, twin.body[1] - twin.xb + xb],
                      court=[xb - cw / 2.0, xb + cw / 2.0], top=twin.top))
    if D.problems:
        return D
    D.uz0 = D.cz0 + P["ROW_PITCH"]
    D.uz1 = D.uz0 + P["UPPER_T"]
    for c in ups:
        c.X, c.Z, c.z_top = ux(c.xb), D.uz0 + c.zc, D.uz0 + c.top
        c.dX = c.X - c.twin.X
    D.ups = ups
    D.conns = lows + ups
    D.fitted = [c for c in D.conns if c.fitted]
    D.dt_top = max(c.top for c in lows)

    # ---- the controls: the sketch's block, and how far it must stay from the face's top and
    #      bottom edges (CONTROL_EDGE on the face; the roof, the floor and the panel board behind)
    pm = P["PANEL_MARGIN"]
    D.controls = []
    need_top, need_bot = [0.0], [0.0]
    for (name, kind, x, z, size) in P["CONTROLS"]:
        c = NS(name=name, kind=kind, X=D.xc + x, z=z, size=size)
        if kind == "knob":
            c.seen = ("circ", size["d"])
            c.hole = ("circ", P["KNOB_HOLE_D"])
            c.behind = c.hole
        elif kind == "key":
            k = P["KEY_CLEAR"]
            c.seen = c.hole = c.behind = ("rect", size["w"] + 2 * k, size["h"] + 2 * k)
        elif kind == "slot":
            c.seen = c.hole = c.behind = ("rect", size["w"], size["h"])
        else:
            b = P["SCREEN_BORDER"]
            c.seen = c.hole = ("rect", size["w"], size["h"])
            c.behind = ("rect", size["w"] + 2 * b, size["h"] + 2 * b)
        hs, hb = _half(c.seen)[1], _half(c.behind)[1]
        board_ = pm if kind != "window" else 0.0
        clr = P["CONTROL_BEHIND_CLEAR"]
        need_top += [P["CONTROL_EDGE"] - (z - hs), BZ + P["LID"] + clr - (z - hb),
                     board_ - (z - hb)]
        need_bot += [P["CONTROL_EDGE"] - (P["SKETCH_H"] - z - hs),
                     BZ + P["FLOOR"] + clr - (P["SKETCH_H"] - z - hb),
                     board_ - (P["SKETCH_H"] - z - hb)]
        D.controls.append(c)
    d_top, d_bot = max(need_top), max(need_bot)
    anchor = P["CONTROLS_ANCHOR"]
    D.face_h_controls = P["SKETCH_H"] + (2 * max(d_top, d_bot) if anchor == "centre"
                                         else d_top + d_bot)

    # ---- heights. The body is whatever the two rows need (never typed). FACE_H None = the face
    #      covers that body, so the unit is one height and goes in from the front; a typed FACE_H
    #      lower than that leaves a front section the face's height and a step up behind it.
    tops = [D.cz1 + P["CARRIER_TOP_H"]] + [c.z_top for c in D.conns]
    D.z_need = max(tops) + P["TOP_GAP"]                # the lid's underside, at the least
    D.body_h_need = D.z_need + P["LID"] - D.zb
    D.face_h_body = D.z_need + P["LID"] + BZ
    D.face_h_typed = P["FACE_H"] is not None
    D.face_h = P["FACE_H"] if D.face_h_typed else max(D.face_h_body, D.face_h_controls)
    D.z_ft = D.face_h - BZ
    D.z_ceil = D.z_ft - P["LID"]
    D.front_h = D.z_ft - D.zb
    D.z_rim = max(D.z_need, D.z_ceil)                  # the lid's underside
    D.stepped = D.z_rim > D.z_ceil + eps
    D.z_under = min(D.z_ceil, D.z_rim - P["RIM_H"])    # under the step wall / the lid's front beam
    hangs = D.z_under < D.z_ceil - eps                 # that beam hangs below the front roof
    D.z_lid = D.z_rim + P["LID"]
    D.rear_h = D.z_lid - D.zb
    D.rise = D.z_lid - D.z_ft                          # how far the rear stands above the front

    spare = D.face_h - P["SKETCH_H"]
    D.ctrl_top = {"centre": spare / 2.0, "top": d_top, "bottom": spare - d_bot}[anchor]
    D.ctrl_bottom = spare - D.ctrl_top
    for c in D.controls:
        c.Z = D.face_h - D.ctrl_top - c.z
    D.block = [D.xc - P["SKETCH_W"] / 2.0, D.xc + P["SKETCH_W"] / 2.0,
               D.ctrl_bottom, D.face_h - D.ctrl_top]

    # ---- going back (Y)
    D.y_face = P["FACE_T"]
    D.y_frame = D.y_face + P["FRAME_D"]                # the body starts where the frame ends
    D.y_panel0 = D.y_face + P["PANEL_GAP"]
    D.y_panel1 = D.y_panel0 + P["PANEL_T"]
    D.y_pko = D.y_panel1 + P["PANEL_BACK_H"]
    if D.stepped:
        # the front section is FRONT_L long; where the beam under the step wall hangs below the
        # front roof it starts a wall's length further forward, to join the roof by a face
        D.y_step = D.y_face + P["FRONT_L"]
        D.y_beam = D.y_step - WL if hangs else D.y_step
        D.cy0 = D.y_pko + P["CARRIER_FRONT_GAP"]
    else:
        # one height: no step wall, FRONT_L does not apply. The roof ends, and the lid begins,
        # on a beam straight behind the room kept for the panel board; the carrier, which drops
        # in from above, stands behind that beam.
        D.y_beam = max(D.y_pko, D.y_frame)
        D.y_step = D.y_beam + WL if hangs else D.y_beam
        D.cy0 = max(D.y_pko + P["CARRIER_FRONT_GAP"], D.y_step + WL + G)
    D.y_riser = D.y_step + WL
    D.carrier_pushed = D.cy0 - (D.y_pko + P["CARRIER_FRONT_GAP"])
    D.cy1 = D.cy0 + DP
    D.step_move = (D.xc + xcb, D.cy0 + yb_front, D.cz0)   # after a half turn about Z

    if ups:
        us = [min(c.court[0] for c in ups), max(c.court[1] for c in ups)]
        D.upper_need = us[1] - us[0]
        ub0 = (us[0] + us[1]) / 2.0 - P["UPPER_W"] / 2.0
        ub1 = ub0 + P["UPPER_W"]
        D.ux0, D.ux1 = ux(ub1), ux(ub0)
        D.uy0, D.uy1 = D.cy1 - P["UPPER_D"], D.cy1
        end = ub0 if toward > 0 else ub1               # the board's end under the first position
        D.standoffs = [(ux(end + toward * a), D.uy0 + b) for (a, b) in P["UPPER_STANDOFFS"]]
        D.standoffs_xb = [end + toward * a for (a, b) in P["UPPER_STANDOFFS"]]

    # ---- the carrier's holes and its ribbon header
    if D.drawn:
        D.holes = [(h["ref"], ux(h["x"]), uy(h["y"])) for h in board["holes"]
                   if h["ref"].startswith("H")]
    else:
        i = P["CARRIER_HOLE_INSET"]
        D.holes = [("H%d" % (k + 1), x, y) for k, (x, y) in enumerate(
            [(D.cx0 + i, D.cy0 + i), (D.cx1 - i, D.cy0 + i), (D.cx0 + i, D.cy1 - i),
             (D.cx1 - i, D.cy1 - i)])]
    j4 = pr["refs"].get("J4")
    D.j4 = None
    if j4:
        dx, dy = xb0 - (o["xmin"] + e), yb_front - (o["ymax"] - e)
        D.j4 = [ux(j4[1] + dx), ux(j4[0] + dx), uy(j4[3] + dy), uy(j4[2] + dy),
                D.cz1, D.cz0 + j4[5]]
        D.j4_h = j4[5] - pr["board_top"]
    else:
        D.notes.append("probe.json has no J4: the ribbon header is not drawn and its distance "
                       "is not reported")

    # ---- the rear plate, the plugs behind it
    D.y_plate0 = D.cy1 + max(c.past for c in D.conns)  # the plate's inner face = flange fronts
    D.y_plate1 = D.y_plate0 + P["PLATE"]
    D.y_end = D.y_plate1 + P["PLATE_LIP"]
    D.y_tip = D.cy1 + max(c.tip for c in D.fitted)
    D.y_plugs = D.y_plate1 + P["PLUG_L"] + P["CABLE_BEND"]
    gr, cc = P["PLUG_GROW"], P["CUTOUT_CLEAR"]
    for c in D.conns:
        t = c.te
        c.cut = [c.X - t["w"] / 2.0 - cc, c.X + t["w"] / 2.0 + cc,
                 c.Z - t["h"] / 2.0 - cc, c.Z + t["h"] / 2.0 + cc]
        c.holes = [c.X - t["pitch"] / 2.0, c.X + t["pitch"] / 2.0]
        c.reach = [c.holes[0] - t["hole"] / 2.0, c.holes[1] + t["hole"] / 2.0, c.cut[2], c.cut[3]]
        c.plug = [c.X - t["w"] / 2.0 - gr, c.X + t["w"] / 2.0 + gr,
                  c.Z - t["h"] / 2.0 - gr, c.Z + t["h"] / 2.0 + gr]
        z0 = D.uz0 if c.row == "upper" else D.cz0
        c.fl = [ux(c.flange[1]), ux(c.flange[0]), z0 + c.flange[2], z0 + c.flange[3]]

    # ---- the panel board and its ribbon header
    D.px0, D.px1, D.pz0, D.pz1 = pm, D.face_w - pm, pm, D.face_h - pm
    i = P["PANEL_HOLE_INSET"]
    D.panel_holes = [(D.px0 + i, D.pz0 + i), (D.px1 - i, D.pz0 + i), (D.px0 + i, D.pz1 - i),
                     (D.px1 - i, D.pz1 - i)]
    D.header, D.ribbon = None, None
    if D.j4:
        hx = P["PANEL_RIBBON_X"] if P["PANEL_RIBBON_X"] is not None else (D.j4[0] + D.j4[1]) / 2.0
        hw, hd = D.j4[1] - D.j4[0], D.j4[3] - D.j4[2]
        hz = D.pz0 + P["PANEL_RIBBON_Z"]
        D.header = [hx - hw / 2.0, hx + hw / 2.0, D.y_panel1, D.y_panel1 + D.j4_h,
                    hz - hd / 2.0, hz + hd / 2.0]
        a = (hx, D.y_panel1 + D.j4_h, hz)
        b = ((D.j4[0] + D.j4[1]) / 2.0, (D.j4[2] + D.j4[3]) / 2.0, D.j4[5])
        D.ribbon = math.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))

    # ---- the lid's lugs and the side screws' bosses
    lr = P["LUG_D"] / 2.0
    D.lug_run = [D.y_riser + lr, D.y_plate0 - P["SLOT_CLEAR"] / 2.0 - G - lr]
    inset = lr - P["LUG_EMBED"]
    D.lugs = [(x, D.lug_run[0] + f * (D.lug_run[1] - D.lug_run[0]))
              for x in (D.ix0 + inset, D.ix1 - inset) for f in P["LID_LUGS"]]
    D.side_bosses = [(side, y, z) for side in ("left", "right") for (y, z) in P["SIDE_SCREWS"]]
    return D


# ------------------------------------------------------------------------------- 2D footprints --
def _half(fp):
    return (fp[1] / 2.0, fp[1] / 2.0) if fp[0] == "circ" else (fp[1] / 2.0, fp[2] / 2.0)


def _gap2d(a, afp, b, bfp):
    """Clear distance between two footprints on the face (negative = they overlap)."""
    dx, dz = abs(a.X - b.X), abs(a.Z - b.Z)
    if afp[0] == "circ" and bfp[0] == "circ":
        return math.hypot(dx, dz) - afp[1] / 2.0 - bfp[1] / 2.0
    if afp[0] == "rect" and bfp[0] == "rect":
        gx, gz = dx - (afp[1] + bfp[1]) / 2.0, dz - (afp[2] + bfp[2]) / 2.0
        return math.hypot(gx, gz) if gx > 0 and gz > 0 else max(gx, gz)
    circ, rect = (afp, bfp) if afp[0] == "circ" else (bfp, afp)
    gx, gz = dx - rect[1] / 2.0, dz - rect[2] / 2.0
    if gx > 0 or gz > 0:
        return math.hypot(max(gx, 0.0), max(gz, 0.0)) - circ[1] / 2.0
    return max(gx, gz) - circ[1] / 2.0


def _sides(c, fp, x0, x1, z0, z1):
    """How far a footprint is inside a rectangle, per side."""
    hx, hz = _half(fp)
    return {"left": c.X - hx - x0, "right": x1 - (c.X + hx), "bottom": c.Z - hz - z0,
            "top": z1 - (c.Z + hz)}


# -------------------------------------------------------------------------------------- rules --
def validate(P, src, U):
    """The fit rules. Returns (problems, D, margins): each problem is one plain sentence naming
    the parameter and the direction to move it. Runs before any geometry; with a problem, nothing
    is built."""
    problems = list(src["problems"]) + check_types(P, U)
    if problems:
        return problems, None, {}
    D = derive(P, src)
    problems += D.problems
    if problems:
        return problems, D, {}
    M = {}
    eps = P["EPS"]
    W, G, WL, BZ = P["CARRIER_W"], P["GAP"], P["WALL"], P["BEZEL_OVERLAP"]

    def bad(msg):
        problems.append(msg)

    # ---- the width rule
    room = D.ix1 - D.ix0
    M["carrier in the body, per side"] = (room - W) / 2.0, G
    if room < W + 2 * G - eps:
        bad("FACE_W %s is too narrow: it leaves a body %s wide and %s inside its walls, but the "
            "carrier is CARRIER_W %s and needs %s with GAP %s a side. Raise FACE_W to at least %s "
            "(or set it to None and it is derived), or narrow the carrier - CARRIER_W can come "
            "down to about %s, the width its three DT13s need side by side."
            % (n(D.face_w), n(D.body_w), n(room), n(W), n(W + 2 * G), n(G),
               n(D.body_w_need + 2 * BZ), n(math.ceil(D.edge_need))))
    if W < D.edge_need - eps:
        bad("CARRIER_W %s is narrower than its three DT13 footprints side by side (%s): raise "
            "CARRIER_W to at least %s, or move one of them to the upper row."
            % (n(W), n(D.edge_need), n(math.ceil(D.edge_need))))
    if problems:
        return problems, D, M                          # the rest would only echo this

    # ---- the panel board inside the front section
    pm = P["PANEL_MARGIN"]
    need_x = BZ + WL + G
    need_z = BZ + max(P["FLOOR"], P["LID"]) + G
    if pm < max(need_x, need_z) - eps:
        bad("PANEL_MARGIN %s puts the panel board through the box: the wall behind the face is "
            "BEZEL_OVERLAP %s + %s thick and the board needs GAP %s beside it. Raise PANEL_MARGIN "
            "to at least %s, or thin the wall, floor and roof."
            % (n(pm), n(BZ), n(max(WL, P["FLOOR"], P["LID"])), n(G), n(max(need_x, need_z))))
    least = 4 * P["PANEL_HOLE_INSET"]
    if D.pz1 - D.pz0 < least - eps:
        bad("FACE_H %s leaves a panel board only %s tall after PANEL_MARGIN %s a side - no room "
            "for its screws: raise FACE_H to at least %s."
            % (n(D.face_h), n(D.pz1 - D.pz0), n(pm), n(least + 2 * pm)))
    if D.px1 - D.px0 < least - eps:
        bad("FACE_W %s leaves a panel board only %s wide: raise FACE_W to at least %s."
            % (n(D.face_w), n(D.px1 - D.px0), n(least + 2 * pm)))
    if D.header:
        h = D.header
        if h[0] < D.px0 - eps or h[1] > D.px1 + eps or h[4] < D.pz0 - eps or h[5] > D.pz1 + eps:
            bad("The panel board's ribbon header (X %s to %s, Z %s to %s) hangs off the board "
                "(X %s to %s, Z %s to %s): set PANEL_RIBBON_X between %s and %s and "
                "PANEL_RIBBON_Z between %s and %s."
                % (n(h[0]), n(h[1]), n(h[4]), n(h[5]), n(D.px0), n(D.px1), n(D.pz0), n(D.pz1),
                   n(D.px0 + (h[1] - h[0]) / 2), n(D.px1 - (h[1] - h[0]) / 2),
                   n((h[5] - h[4]) / 2), n(D.pz1 - D.pz0 - (h[5] - h[4]) / 2)))
        if D.j4_h > P["PANEL_BACK_H"] + eps:
            bad("PANEL_BACK_H %s is less than the ribbon header's own height %s: raise "
                "PANEL_BACK_H to at least %s plus the plug."
                % (n(P["PANEL_BACK_H"]), n(D.j4_h), n(D.j4_h)))

    # ---- the controls: on the face, apart from each other, and over the box's opening
    edge, gap, clr = P["CONTROL_EDGE"], P["CONTROL_GAP"], P["CONTROL_BEHIND_CLEAR"]
    wall = {"left": BZ + WL, "right": BZ + WL, "bottom": BZ + P["FLOOR"], "top": BZ + P["LID"]}
    m_edge, m_behind, m_gap = [], [], []
    for c in D.controls:
        on = _sides(c, c.seen, 0.0, D.face_w, 0.0, D.face_h)
        be = _sides(c, c.behind, D.ix0, D.ix1, D.zf, D.z_ceil)
        m_edge.append(min(on.values()))
        m_behind.append(min(be.values()))
        for side in ("left", "right", "bottom", "top"):
            if side in ("left", "right"):
                dim, least = "FACE_W", D.face_w + 2 * max(edge - on[side], clr - be[side])
                how = "the control block stays centred"
            else:
                dim, least = "FACE_H", D.face_h_controls
                how = "the control block stays anchored %s; or set FACE_H to None and it is " \
                      "derived" % P["CONTROLS_ANCHOR"]
            move = {"left": "right", "right": "left", "bottom": "up", "top": "down"}[side]
            if on[side] < edge - eps:
                bad("Control '%s' %s the face's %s edge, and CONTROL_EDGE asks for %s: "
                    "raise %s to at least %s (%s), or move it %s by %s in "
                    "CONTROLS." % (c.name, ("is only %s from" % n(on[side])) if on[side] >= 0
                                   else ("hangs %s off" % n(-on[side])), side, n(edge), dim,
                                   n(least), how, move, n(edge - on[side])))
            elif be[side] < clr - eps:
                short = clr - be[side]
                bad("Control '%s': what it needs behind the face comes %s from the face's %s "
                    "edge, but the box's %s reaches %s in from that edge (BEZEL_OVERLAP + its "
                    "thickness) and CONTROL_BEHIND_CLEAR is %s, so %s of it would be over "
                    "plastic. Raise %s to at least %s (%s), or move it %s "
                    "by %s in CONTROLS, or thin that wall."
                    % (c.name, n(be[side] + wall[side]), side,
                       {"left": "side wall", "right": "side wall", "bottom": "floor",
                        "top": "roof"}[side], n(wall[side]), n(clr), n(short), dim,
                       n(least), how, move, n(short)))
        if c.kind != "window":
            pb = _sides(c, c.behind, D.px0, D.px1, D.pz0, D.pz1)
            if min(pb.values()) < -eps:
                bad("Control '%s' hangs %s off the panel board behind it: lower PANEL_MARGIN, "
                    "or move it inward in CONTROLS." % (c.name, n(-min(pb.values()))))
    for i, a in enumerate(D.controls):
        for b in D.controls[i + 1:]:
            g = _gap2d(a, a.seen, b, b.seen)
            m_gap.append(g)
            if g < gap - eps:
                bad("Controls '%s' and '%s' are %s apart, less than CONTROL_GAP %s: move them "
                    "apart by %s in CONTROLS." % (a.name, b.name, n(g), n(gap), n(gap - g)))
    if D.controls:
        M["controls to the face's edge"] = min(m_edge), edge
        M["control openings to the box behind the face"] = min(m_behind), clr
    if m_gap:
        M["controls to each other"] = min(m_gap), gap
    if P["KNOB_SHAFT_D"] > P["KNOB_HOLE_D"] + eps:
        bad("KNOB_SHAFT_D %s is wider than KNOB_HOLE_D %s: lower the shaft or raise the hole."
            % (n(P["KNOB_SHAFT_D"]), n(P["KNOB_HOLE_D"])))

    # ---- the front section, the step wall, and the carrier dropping in behind it
    if D.stepped and P["FRONT_L"] < P["FRAME_D"] + WL - eps:
        bad("FRONT_L %s is shorter than the front frame and a wall (FRAME_D %s + WALL %s): raise "
            "FRONT_L to at least %s." % (n(P["FRONT_L"]), n(P["FRAME_D"]), n(WL),
                                         n(P["FRAME_D"] + WL)))
    if D.cy0 < D.y_riser + G - eps:
        most = D.cy0 - G - WL - D.y_face
        bad("FRONT_L %s puts the step wall over the carrier: the wall's rear face is at Y %s, the "
            "carrier's front edge at Y %s, and the carrier drops in from above behind that wall "
            "with GAP %s. Shorten FRONT_L to at most %s, or push the carrier back by raising "
            "CARRIER_FRONT_GAP (or PANEL_BACK_H / PANEL_GAP) by %s."
            % (n(P["FRONT_L"]), n(D.y_riser), n(D.cy0), n(G), n(most), n(D.y_riser + G - D.cy0)))
    if D.z_under <= D.zf + eps:
        bad("RIM_H %s takes the lid's front beam down to the floor (Z %s): lower RIM_H to less "
            "than %s." % (n(P["RIM_H"]), n(D.z_under), n(D.z_rim - D.zf)))
    elif D.z_under < D.pz1 - eps and D.y_pko > D.y_beam + eps and D.y_beam < D.y_step:
        bad("The step is only %s, less than RIM_H %s, so the lid's front edge lands on a beam "
            "that hangs below the front roof (Y %s to %s, down to Z %s), and that is in the room "
            "kept behind the panel board (back to Y %s, up to Z %s): set FACE_H to None for a "
            "unit of one height, or raise FRONT_L to at least %s (and CARRIER_FRONT_GAP with it, "
            "so the carrier still drops in behind), or lower RIM_H (0 = no beam)."
            % (n(D.z_rim - D.z_ceil), n(P["RIM_H"]), n(D.y_beam), n(D.y_riser), n(D.z_under),
               n(D.y_pko), n(D.pz1), n(D.y_pko - D.y_face + D.y_step - D.y_beam)))
    if P["BOSS_H"] < P["CARRIER_BOT_H"] - eps:
        bad("BOSS_H %s is less than CARRIER_BOT_H %s, so the floor is inside the room kept under "
            "the carrier: raise BOSS_H to at least %s."
            % (n(P["BOSS_H"]), n(P["CARRIER_BOT_H"]), n(P["CARRIER_BOT_H"])))

    # ---- inserts and thin places
    deep = P["INSERT_DEPTH"] + P["INSERT_SKIN"]
    for label, have, what in (
            ("BOSS_H + FLOOR", P["BOSS_H"] + P["FLOOR"], "raise BOSS_H or FLOOR"),
            ("LUG_H", P["LUG_H"], "raise LUG_H"),
            ("WALL + SIDE_BOSS_L", WL + P["SIDE_BOSS_L"], "raise SIDE_BOSS_L")):
        if have < deep - eps:
            bad("%s is %s, less than an insert's bore and the skin beyond it (INSERT_DEPTH %s + "
                "INSERT_SKIN %s): %s by %s."
                % (label, n(have), n(P["INSERT_DEPTH"]), n(P["INSERT_SKIN"]), what,
                   n(deep - have)))
    wide = P["INSERT_BORE"] + 2 * P["INSERT_SKIN"]
    for name in ("BOSS_D", "LUG_D", "SIDE_BOSS_D"):
        if P[name] < wide - eps:
            bad("%s %s leaves less than INSERT_SKIN %s round an INSERT_BORE %s: raise %s to at "
                "least %s." % (name, n(P[name]), n(P["INSERT_SKIN"]), n(P["INSERT_BORE"]), name,
                               n(wide)))
    if P["STANDOFF_D"] < P["SCREW_CLEAR"] + 2 * P["INSERT_SKIN"] - eps:
        bad("STANDOFF_D %s leaves too little round a SCREW_CLEAR %s hole: raise STANDOFF_D to at "
            "least %s." % (n(P["STANDOFF_D"]), n(P["SCREW_CLEAR"]),
                           n(P["SCREW_CLEAR"] + 2 * P["INSERT_SKIN"])))
    if P["PLATE"] > L.TE_PANEL_MAX + eps:
        bad("PLATE %s is thicker than TE allows for a DT13's panel (%s, 114-151046 3.11): lower "
            "PLATE." % (n(P["PLATE"]), n(L.TE_PANEL_MAX)))
    for a, b, what in (("SLOT_DEPTH", "WALL", "the plate's channel cuts through the side wall"),
                       ("LUG_EMBED", "WALL", "the lid lugs break out of the side wall"),
                       ("FLOOR_GROOVE", "FLOOR", "the plate's channel cuts through the floor"),
                       ("GASKET_GROOVE_W", "WALL", "the gasket groove is wider than the wall"),
                       ("GASKET_GROOVE_W", "PLATE", "the gasket groove is wider than the plate"),
                       ("GASKET_GROOVE_D", "LID", "the gasket groove cuts through the lid"),
                       ("RESERVED_MARK_D", "PLATE", "the scribe cuts through the plate")):
        if P[a] >= P[b] - eps:
            bad("%s %s is not less than %s %s (%s): lower %s or raise %s."
                % (a, n(P[a]), b, n(P[b]), what, a, b))

    # ---- the two rows
    pe = P["PLATE_EDGE"]
    if D.ups:
        pitch = P["ROW_PITCH"]
        floor_ = []                                    # (least pitch, why)
        floor_.append((D.dt_top + P["UPPER_BOT_H"],
                       "a DT13 stands %s above its board's underside and the upper board needs "
                       "UPPER_BOT_H %s under it" % (n(D.dt_top), n(P["UPPER_BOT_H"]))))
        for u in D.ups:
            for c in D.lows:
                if u.plug[0] < c.plug[1] and c.plug[0] < u.plug[1]:      # one above the other
                    floor_.append((c.flange[3] - u.flange[2],
                                   "the flange of %s would overlap the flange of %s under it"
                                   % (u.name, c.name)))
                    hh = (u.te["h"] + c.te["h"]) / 2.0
                    floor_.append((hh + 2 * P["CUTOUT_CLEAR"] + pe,
                                   "the %d-way cut-outs are %s tall and need PLATE_EDGE %s of "
                                   "plate between the rows" % (int(u.part[5:7]), n(u.te["h"]),
                                                                n(pe))))
                    floor_.append((hh + 2 * P["PLUG_GROW"] + P["PLUG_ROW_CLEAR"],
                                   "two mated plugs (cut-out + PLUG_GROW %s a side) need "
                                   "PLUG_ROW_CLEAR %s between them"
                                   % (n(P["PLUG_GROW"]), n(P["PLUG_ROW_CLEAR"]))))
        least = max(f[0] for f in floor_)
        D.pitch_min = least
        worst = {}
        for f in floor_:
            if pitch < f[0] - eps and f[0] > worst.get(f[1], 0.0):
                worst[f[1]] = f[0]
        short = sorted(((v, k) for k, v in worst.items()), reverse=True)
        if short:
            bad("ROW_PITCH %s is too small: raise it to at least %s. What sets that, largest "
                "first: %s." % (n(pitch), n(math.ceil(least * 10) / 10.0),
                                "; ".join("%s (needs %s)" % (f[1], n(f[0])) for f in short)))
        M["row to row, plug to plug"] = min(
            [u.plug[2] - c.plug[3] for u in D.ups for c in D.lows
             if u.plug[0] < c.plug[1] and c.plug[0] < u.plug[1]] or [float("inf")]), \
            P["PLUG_ROW_CLEAR"]
        # the upper board
        if P["UPPER_W"] < D.upper_need - eps:
            bad("UPPER_W %s is narrower than its %d connector positions side by side (%s): raise "
                "UPPER_W to at least %s, or take a position out of UPPER_CONNECTORS."
                % (n(P["UPPER_W"]), len(D.ups), n(D.upper_need), n(math.ceil(D.upper_need))))
        if D.ux0 < D.ix0 + G - eps or D.ux1 > D.ix1 - G + eps:
            bad("The upper board (X %s to %s) does not fit between the side walls (X %s to %s "
                "with GAP): lower UPPER_W, take a position out of UPPER_CONNECTORS, or widen the "
                "unit (FACE_W)." % (n(D.ux0), n(D.ux1), n(D.ix0 + G), n(D.ix1 - G)))
        deep = max(u.court_in for u in D.ups) + P["UPPER_STANDOFF_D"]
        if P["UPPER_D"] < deep - eps:
            bad("UPPER_D %s is too shallow for a DT13's footprint (%s from the edge) and a "
                "standoff in front of it: raise UPPER_D to at least %s."
                % (n(P["UPPER_D"]), n(max(u.court_in for u in D.ups)), n(deep)))
        if P["UPPER_D"] > P["CARRIER_D"] + eps:
            bad("UPPER_D %s is deeper than the carrier it stands on (CARRIER_D %s): lower "
                "UPPER_D." % (n(P["UPPER_D"]), n(P["CARRIER_D"])))
        if D.stepped and D.uy0 < D.y_riser + G - eps:
            bad("The upper board's front edge (Y %s) is under the low front section, which ends "
                "at Y %s: lower UPPER_D to at most %s, or shorten FRONT_L."
                % (n(D.uy0), n(D.y_riser), n(D.cy1 - D.y_riser - G)))
        r = P["UPPER_STANDOFF_D"] / 2.0
        for k, (x, y) in enumerate(D.standoffs):
            a, b = P["UPPER_STANDOFFS"][k]
            if not (r - eps <= a <= P["UPPER_W"] - r + eps and r - eps <= b <= P["UPPER_D"] - r
                    + eps):
                bad("UPPER_STANDOFFS %d at (%s, %s) is off the upper board (%s x %s): keep it "
                    "between %s and %s along the board and %s and %s back from its front edge."
                    % (k + 1, n(a), n(b), n(P["UPPER_W"]), n(P["UPPER_D"]), n(r),
                       n(P["UPPER_W"] - r), n(r), n(P["UPPER_D"] - r)))
            elif b > P["UPPER_D"] - max(u.court_in for u in D.ups) - r + eps and any(
                    u.court[0] - r < D.standoffs_xb[k] < u.court[1] + r for u in D.ups):
                bad("UPPER_STANDOFFS %d at (%s, %s) is under a DT13's footprint, which starts %s "
                    "back from the upper board's front edge: lower its second number to at most "
                    "%s." % (k + 1, n(a), n(b),
                             n(P["UPPER_D"] - max(u.court_in for u in D.ups)),
                             n(P["UPPER_D"] - max(u.court_in for u in D.ups) - r)))

    # ---- every cut-out inside the plate, with plastic round it; plugs side by side
    m_plate, m_side = [], []
    for c in D.conns:
        m = {"left": c.reach[0] - D.ix0, "right": D.ix1 - c.reach[1],
             "bottom": c.reach[2] - D.zf, "top": D.z_rim - c.reach[3]}
        m_plate.append(min(m.values()))
        for side, v in m.items():
            if v < pe - eps:
                fix = {"left": "widen the unit (FACE_W) or move the connector",
                       "right": "widen the unit (FACE_W) or move the connector",
                       "bottom": "raise BOSS_H", "top": "raise TOP_GAP"}[side]
                bad("The cut-out for %s%s comes %s from the rear plate's %s edge, less than "
                    "PLATE_EDGE %s: %s by %s."
                    % (c.name, "" if c.fitted else " (reserved)", n(v), side, n(pe), fix,
                       n(pe - v)))
    for row in (D.lows, D.ups):
        seq = sorted(row, key=lambda c: c.X)
        for a, b in zip(seq, seq[1:]):
            m_plate.append(b.reach[0] - a.reach[1])
            m_side.append(b.plug[0] - a.plug[1])
            if b.reach[0] - a.reach[1] < pe - eps or b.fl[0] - a.fl[1] < -eps:
                bad("%s and %s stand too close on the rear plate (%s between their screw holes, "
                    "%s between their flanges): raise UPPER_CONN_GAP by %s."
                    % (a.name, b.name, n(b.reach[0] - a.reach[1]), n(b.fl[0] - a.fl[1]),
                       n(max(pe - (b.reach[0] - a.reach[1]), a.fl[1] - b.fl[0]))))
            elif b.plug[0] - a.plug[1] < P["PLUG_SIDE_CLEAR"] - eps:
                bad("The mated plugs of %s and %s are %s apart, less than PLUG_SIDE_CLEAR %s: "
                    "raise UPPER_CONN_GAP by %s, or lower PLUG_GROW."
                    % (a.name, b.name, n(b.plug[0] - a.plug[1]), n(P["PLUG_SIDE_CLEAR"]),
                       n(P["PLUG_SIDE_CLEAR"] - (b.plug[0] - a.plug[1]))))
    M["cut-outs and screw holes to the plate's edge and each other"] = min(m_plate), pe
    if m_side:
        M["plug to plug, side by side"] = min(m_side), P["PLUG_SIDE_CLEAR"]

    # ---- lugs and side screws
    if D.lug_run[1] < D.lug_run[0] - eps:
        bad("There is no room for a lid lug between the step wall and the rear plate (%s): "
            "lower LUG_D or shorten FRONT_L." % n(D.lug_run[1] - D.lug_run[0] + P["LUG_D"]))
    r = P["SIDE_BOSS_D"] / 2.0
    for k, (y, z) in enumerate(P["SIDE_SCREWS"]):
        top = D.z_rim if y - r >= D.y_riser - eps else min(D.z_ceil, D.z_under)
        y_lo, y_hi = D.y_frame + r, D.y_plate0 - P["SLOT_CLEAR"] / 2.0 - r
        if not (y_lo - eps <= y <= y_hi + eps):
            bad("SIDE_SCREWS %d at Y %s is off the side wall: keep Y between %s and %s."
                % (k + 1, n(y), n(y_lo), n(y_hi)))
        elif not (D.zf + r - eps <= z <= top - r + eps):
            bad("SIDE_SCREWS %d at Z %s is off the side wall there: keep Z between %s and %s."
                % (k + 1, n(z), n(D.zf + r), n(top - r)))

    # ---- the envelope, once measured
    env = P["ENVELOPE"]
    D.env = None
    if env is not None:
        D.env = []
        ow, oh = env["OPENING_W"], env["OPENING_H"]

        def rule(ok, name, msg):
            D.env.append((name, bool(ok), msg))
            if not ok:
                bad(msg)

        rule(D.body_w <= ow + eps and D.front_h <= oh + eps, "front section in the opening",
             "The front section is %s x %s and the opening is %s x %s: %s."
             % (n(D.body_w), n(D.front_h), n(ow), n(oh),
                "it goes in" if D.body_w <= ow + eps and D.front_h <= oh + eps else
                "narrow the unit (FACE_W, CARRIER_W) or lower it (ROW_PITCH; or a typed FACE_H, "
                "which steps the rear up behind the dash) until it does"))
        rule(D.face_w >= ow - eps and D.face_h >= oh - eps, "face covers the opening",
             "The face is %s x %s and the opening is %s x %s: %s."
             % (n(D.face_w), n(D.face_h), n(ow), n(oh),
                "it covers it" if D.face_w >= ow - eps and D.face_h >= oh - eps else
                "raise FACE_W / FACE_H to at least the opening"))
        deep = D.y_plugs - D.y_face
        rule(deep <= env["DEPTH"] + eps, "depth with plugs",
             "Behind the face the unit needs %s with its plugs and the opening has %s: %s."
             % (n(deep), n(env["DEPTH"]), "it goes in" if deep <= env["DEPTH"] + eps else
                "shorten it by %s (CARRIER_D, PLUG_L, CABLE_BEND, PANEL_BACK_H)"
                % n(deep - env["DEPTH"])))
        bh = env.get("BEHIND_H")
        if D.rear_h <= oh + eps:
            rule(True, "rear section through the opening",
                 "The rear section is %s tall and passes the %s opening from the front."
                 % (n(D.rear_h), n(oh)))
        elif bh is not None and D.rear_h <= bh + eps:
            rule(True, "rear section behind the dash",
                 "The rear section is %s tall: it fits the %s behind the dash but NOT through "
                 "the %s opening, so the unit goes in from behind or with the dash open, not "
                 "like a head unit." % (n(D.rear_h), n(bh), n(oh)))
        else:
            rule(False, "rear section through the opening",
                 "The rear section is %s tall and the opening is %s%s: it does not go in. Lower "
                 "ROW_PITCH (least %s), take the upper row to one side, or give BEHIND_H if "
                 "there is height behind the dash and it can be fitted from behind."
                 % (n(D.rear_h), n(oh), "" if bh is None else " (%s behind the dash)" % n(bh),
                    n(D.pitch_min) if D.ups else "n/a"))
    return problems, D, M


# ------------------------------------------------------------------------------------ insides --
def _item(name, shape, kind="part", **kw):
    d = {"name": name, "shape": shape, "kind": kind, "group": name, "dt13": False}
    d.update(kw)
    return d


def _standin_dt13(D, c, z0, z_board_top):
    """A DT13 as three blocks from probe.json: the body on its board (as wide and as tall as the
    model's whole extent - generous), the flange, and the nose with TE's corner radius."""
    ux = D.ux
    body = L.box(ux(c.body[1]), ux(c.body[0]), D.cy1 - c.inward, D.cy1, z_board_top, z0 + c.top)
    flange = L.box(ux(c.flange[1]), ux(c.flange[0]), D.cy1, D.cy1 + c.past,
                   z0 + c.flange[2], z0 + c.flange[3])
    h = c.housing
    nose = L.rrect_xz(h[1] - h[0], h[3] - h[2], c.te["r"], ux((h[0] + h[1]) / 2.0),
                      z0 + (h[2] + h[3]) / 2.0, D.cy1, D.cy1 + c.tip)
    return L.fuse([body, flange, nose])


def build_insides(P, D, src, standin=False):
    """Everything inside the case and on its face, as named solids. `kind` is `part`, `carrier`
    (the board's own solids) or `keepout` (room kept clear, not a thing)."""
    oc = P["OVERCUT"]
    out = []

    # ---- the faceplate and its controls
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
    for c in D.controls:
        s = c.size
        if c.kind == "knob":
            shape = L.fuse([L.cyl_y(s["d"] / 2.0, c.X, c.Z, -P["KNOB_PROUD"], -P["KNOB_FLOAT"]),
                            L.cyl_y(P["KNOB_SHAFT_D"] / 2.0, c.X, c.Z, -P["KNOB_FLOAT"],
                                    D.y_panel0)])
        elif c.kind == "key":
            shape = L.box(c.X - s["w"] / 2.0, c.X + s["w"] / 2.0, -P["KEY_PROUD"], D.y_panel0,
                          c.Z - s["h"] / 2.0, c.Z + s["h"] / 2.0)
        elif c.kind == "slot":
            k = P["PADDLE_CLEAR"]
            shape = L.box(c.X - s["w"] / 2.0 + k, c.X + s["w"] / 2.0 - k, -P["PADDLE_PROUD"],
                          D.y_panel0, c.Z - s["h"] / 2.0 + k, c.Z + s["h"] / 2.0 - k)
        else:
            shape = L.box(c.X - c.behind[1] / 2.0, c.X + c.behind[1] / 2.0, D.y_face,
                          D.y_face + P["SCREEN_T"], c.Z - c.behind[2] / 2.0,
                          c.Z + c.behind[2] / 2.0)
        out.append(_item("control: " + c.name, shape))

    # ---- the panel board, its ribbon header, the room behind it
    panel = L.box(D.px0, D.px1, D.y_panel0, D.y_panel1, D.pz0, D.pz1)
    panel = L.cut(panel, [L.cyl_y(P["SCREW_CLEAR"] / 2.0, x, z, D.y_panel0 - oc, D.y_panel1 + oc)
                          for (x, z) in D.panel_holes])
    out.append(_item("panel board", panel))
    if D.header:
        out.append(_item("panel ribbon header", L.box(*D.header)))
    out.append(_item("keep-out: behind the panel board",
                     L.box(D.px0, D.px1, D.y_panel1, D.y_pko, D.pz0, D.pz1), "keepout"))

    # ---- the carrier: the board's STEP when it is the drawn board, stand-in blocks otherwise
    real = bool(src["step"]) and bool(P["CARRIER_STEP"]) and D.drawn and not standin
    if not standin:
        D.carrier_real = real
    dt_refs = {c.ref for c in D.lows}
    twins = {}
    if real:
        mv = V(*D.step_move)
        for ref, s in src["step"]:
            t = s.rotated(V(0, 0, 0), V(0, 0, 1), 180).translated(mv)
            if ref in dt_refs:
                low = [c for c in D.lows if c.ref == ref][0]
                twins.setdefault(ref, []).append(t)
                out.append(_item("%s %s (%s)" % (ref, low.name, low.part), t, "carrier", ref=ref,
                                 dt13=True))
            else:
                out.append(_item("carrier: " + ref, t, "carrier", ref=ref,
                                 group="carrier board" if ref == "board" else "carrier parts"))
    else:
        out.append(_item("carrier board (stand-in)",
                         L.box(D.cx0, D.cx1, D.cy0, D.cy1, D.cz0, D.cz1), "carrier", ref="board"))
        for c in D.lows:
            out.append(_item("%s %s (%s, stand-in)" % (c.ref, c.name, c.part),
                             _standin_dt13(D, c, D.cz0, D.cz1), "carrier", ref=c.ref,
                             dt13=True))
        if D.j4:
            out.append(_item("J4 ribbon header (stand-in)", L.box(*D.j4), "carrier", ref="J4"))
    out.append(_item("keep-out: above the carrier",
                     L.box(D.cx0, D.cx1, D.cy0, D.cy1, D.cz1, D.cz1 + P["CARRIER_TOP_H"]),
                     "keepout"))
    if P["CARRIER_BOT_H"] > 0:
        under = L.box(D.cx0, D.cx1, D.cy0, D.cy1, D.cz0 - P["CARRIER_BOT_H"], D.cz0)
        r = P["BOSS_D"] / 2.0                          # the bosses stand in this room: square
        under = L.cut(under, [L.box(x - r, x + r, y - r, y + r,    # notches, no slivers
                                    D.cz0 - P["CARRIER_BOT_H"] - oc, D.cz0 + oc)
                              for (_, x, y) in D.holes])
        out.append(_item("keep-out: below the carrier", under, "keepout"))

    # ---- the upper row: its board, its connectors, the standoffs that carry it
    if D.ups:
        up_solids = []
        for u in D.ups:
            if real:
                shape = Part.makeCompound([t.translated(V(u.dX, 0, P["ROW_PITCH"]))
                                           for t in twins[u.twin.ref]])
                tag = u.part
            else:
                shape = _standin_dt13(D, u, D.uz0, D.uz1)
                tag = u.part + ", stand-in"
            if u.fitted:
                up_solids.append(shape)
                out.append(_item("%s (%s)" % (u.name, tag), shape, ref=u.ref, dt13=True))
            else:
                zone = L.box(u.fl[0], u.fl[1], D.y_plate0 - u.past, D.y_plate0, u.fl[2], u.fl[3])
                out.append(_item("reserved: %s (%s flange zone)" % (u.name, u.part), zone,
                                 "keepout"))
        ub = L.box(D.ux0, D.ux1, D.uy0, D.uy1, D.uz0, D.uz1)
        if real and up_solids:
            ub = L.cut(ub, up_solids)                  # the pins' holes
        out.append(_item("upper connector board", ub))
        for k, (x, y) in enumerate(D.standoffs):
            out.append(_item("upper board standoff %d" % (k + 1),
                             L.cyl(P["UPPER_STANDOFF_D"] / 2.0, x, y, D.cz1, D.uz0)))

    # ---- the mated plugs: room, not parts
    for c in D.fitted:
        out.append(_item("keep-out: mated plug on %s" % c.name,
                         L.box(c.plug[0], c.plug[1], D.y_plate1, D.y_plugs, c.plug[2], c.plug[3]),
                         "keepout"))
    return out


# --------------------------------------------------------------------------------------- case --
def build_case(P, D):
    """The four printed parts: body, rear plate, lid, front frame. Also returns, per part, its
    named features (label, box, the parameters that move it) so an interference can say where."""
    oc = P["OVERCUT"]
    WL, FT, LT, PT = P["WALL"], P["FLOOR"], P["LID"], P["PLATE"]
    bx0, bx1, ix0, ix1 = D.bx0, D.bx1, D.ix0, D.ix1
    zb, zf, z_ft, z_ceil, z_rim = D.zb, D.zf, D.z_ft, D.z_ceil, D.z_rim
    feats = {"body": [], "rear_plate": [], "lid": [], "front_frame": []}

    # ---- body: floor, side walls, the front section's roof, the step wall, open at the rear
    blocks = [L.box(bx0, bx1, D.y_step, D.y_end, zb, z_rim)]
    if D.y_step > D.y_frame + P["EPS"]:
        blocks.append(L.box(bx0, bx1, D.y_frame, D.y_step, zb, z_ft))
    shell = L.fuse(blocks)
    inner = [L.box(ix0, ix1, D.y_frame - oc, D.y_riser + oc, zf, D.z_under),
             L.box(ix0, ix1, D.y_riser, D.y_end + oc, zf, z_rim + oc)]
    if D.y_beam < D.y_step:
        inner.append(L.box(ix0, ix1, D.y_frame - oc, D.y_beam, zf, z_ceil))
    shell = L.cut(shell, inner)
    adds, bores = [], []
    fb = feats["body"]
    for (ref, x, y) in D.holes:
        adds.append(L.cyl(P["BOSS_D"] / 2.0, x, y, zb, D.cz0))
        bores.append(L.cyl(P["INSERT_BORE"] / 2.0, x, y, D.cz0 - P["INSERT_DEPTH"], D.cz0 + oc))
        r = P["BOSS_D"] / 2.0
        fb.append(("carrier boss " + ref, [x - r, x + r, y - r, y + r, zf, D.cz0],
                   "BOSS_D, BOSS_H, or the carrier's holes"))
    lr = P["LUG_D"] / 2.0
    for k, (x, y) in enumerate(D.lugs):
        adds.append(L.cyl(lr, x, y, z_rim - P["LUG_H"], z_rim))
        bores.append(L.cyl(P["INSERT_BORE"] / 2.0, x, y, z_rim - P["INSERT_DEPTH"], z_rim + oc))
        fb.append(("lid lug %d" % (k + 1), [x - lr, x + lr, y - lr, y + lr, z_rim - P["LUG_H"],
                                            z_rim], "LID_LUGS, LUG_D, LUG_H"))
    sr = P["SIDE_BOSS_D"] / 2.0
    for k, (side, y, z) in enumerate(D.side_bosses):
        if side == "left":
            adds.append(L.cyl_x(sr, y, z, bx0, ix0 + P["SIDE_BOSS_L"]))
            bores.append(L.cyl_x(P["INSERT_BORE"] / 2.0, y, z, bx0 - oc, bx0 + P["INSERT_DEPTH"]))
            xr = [ix0, ix0 + P["SIDE_BOSS_L"]]
        else:
            adds.append(L.cyl_x(sr, y, z, ix1 - P["SIDE_BOSS_L"], bx1))
            bores.append(L.cyl_x(P["INSERT_BORE"] / 2.0, y, z, bx1 - P["INSERT_DEPTH"], bx1 + oc))
            xr = [ix1 - P["SIDE_BOSS_L"], ix1]
        fb.append(("side screw boss, %s wall, at (Y %s, Z %s)" % (side, n(y), n(z)),
                   xr + [y - sr, y + sr, z - sr, z + sr], "SIDE_SCREWS, SIDE_BOSS_L, SIDE_BOSS_D"))
    sd, sc = P["SLOT_DEPTH"], P["SLOT_CLEAR"]
    channel = L.box(ix0 - sd, ix1 + sd, D.y_plate0 - sc / 2.0, D.y_plate1 + sc / 2.0,
                    zf - P["FLOOR_GROOVE"], z_rim + oc)
    body = L.cut(L.fuse([shell] + adds), [channel] + bores)
    fb += [("step wall" if D.stepped else "the beam under the lid's front edge",
            [ix0, ix1, D.y_beam, D.y_riser, D.z_under, z_rim],
            "FRONT_L, RIM_H" if D.stepped else "RIM_H, PANEL_BACK_H"),
           ("front section's roof", [ix0, ix1, D.y_frame, D.y_step, z_ceil, z_ft],
            "FACE_H, LID, BEZEL_OVERLAP"),
           ("floor", [bx0, bx1, D.y_frame, D.y_end, zb, zf], "BOSS_H, FLOOR"),
           ("left wall", [bx0, ix0, D.y_frame, D.y_end, zb, max(z_rim, z_ft)],
            "FACE_W, WALL, GAP"),
           ("right wall", [ix1, bx1, D.y_frame, D.y_end, zb, max(z_rim, z_ft)],
            "FACE_W, WALL, GAP")]

    # ---- rear plate: every fitted DT13 through TE's cut-out; a reserved one only scribed
    plate = L.box(ix0 - sd + sc / 2.0, ix1 + sd - sc / 2.0, D.y_plate0, D.y_plate1,
                  zf - P["FLOOR_GROOVE"] + sc / 2.0, z_rim)
    cuts = []
    for c in D.conns:
        t = c.te
        w, h = c.cut[1] - c.cut[0], c.cut[3] - c.cut[2]
        if c.fitted:
            cuts.append(L.rrect_xz(w, h, t["r"], c.X, c.Z, D.y_plate0 - oc, D.y_plate1 + oc))
            cuts += [L.cyl_y(t["hole"] / 2.0, x, c.Z, D.y_plate0 - oc, D.y_plate1 + oc)
                     for x in c.holes]
        else:
            mw, md = P["RESERVED_MARK_W"], P["RESERVED_MARK_D"]
            y0, y1 = D.y_plate1 - md, D.y_plate1 + oc
            ring = L.rrect_xz(w + mw, h + mw, t["r"] + mw / 2.0, c.X, c.Z, y0, y1).cut(
                L.rrect_xz(w - mw, h - mw, t["r"] - mw / 2.0, c.X, c.Z, y0 - oc, y1 + oc))
            cuts.append(ring)
            cuts += [L.cyl_y(mw, x, c.Z, y0, y1) for x in c.holes]
        feats["rear_plate"].append(("the plate round %s's cut-out" % c.name,
                                    [c.fl[0], c.fl[1], D.y_plate0, D.y_plate1, c.fl[2], c.fl[3]],
                                    "ROW_PITCH, UPPER_CONN_GAP, CUTOUT_CLEAR"))
    plate = L.cut(plate, cuts)

    # ---- lid: flat, over the rear section; the gasket groove over the walls' centre lines
    lid = L.box(bx0, bx1, D.y_step, D.y_end, z_rim, D.z_lid)
    gw, gd = P["GASKET_GROOVE_W"], P["GASKET_GROOVE_D"]
    mx0, mx1 = bx0 + WL / 2.0, bx1 - WL / 2.0
    my0, my1 = D.y_step + WL / 2.0, D.y_plate0 + PT / 2.0
    outer = L.rrect_prism(mx1 - mx0 + gw, my1 - my0 + gw, P["GASKET_R"] + gw / 2.0,
                          (mx0 + mx1) / 2.0, (my0 + my1) / 2.0, z_rim - oc, z_rim + gd)
    inner_ = L.rrect_prism(mx1 - mx0 - gw, my1 - my0 - gw, max(gw / 2.0, P["GASKET_R"] - gw / 2.0),
                           (mx0 + mx1) / 2.0, (my0 + my1) / 2.0, z_rim - 2 * oc, z_rim + gd + oc)
    lid = L.cut(lid, [outer.cut(inner_)] +
                [L.cyl(P["SCREW_CLEAR"] / 2.0, x, y, z_rim - oc, D.z_lid + oc)
                 for (x, y) in D.lugs])
    feats["lid"].append(("lid", [bx0, bx1, D.y_step, D.y_end, z_rim, D.z_lid],
                         "TOP_GAP, ROW_PITCH"))

    # ---- front frame: a ring behind the faceplate, four standoffs to the panel board
    ring = L.box(bx0, bx1, D.y_face, D.y_frame, zb, z_ft).cut(
        L.box(ix0, ix1, D.y_face - oc, D.y_frame + oc, zf, z_ceil))
    adds, bores = [ring], []
    r = P["STANDOFF_D"] / 2.0
    zmid = (zf + z_ceil) / 2.0
    for k, (x, z) in enumerate(D.panel_holes):
        adds.append(L.cyl_y(r, x, z, D.y_face, D.y_panel0))
        ex = bx0 if x < D.xc else bx1
        ez = zb if z < zmid else z_ft
        adds.append(L.box(min(x, ex), max(x, ex), D.y_face, D.y_frame, z - P["WEB"] / 2.0,
                          z + P["WEB"] / 2.0))
        adds.append(L.box(x - P["WEB"] / 2.0, x + P["WEB"] / 2.0, D.y_face, D.y_frame,
                          min(z, ez), max(z, ez)))
        bores.append(L.cyl_y(P["SCREW_CLEAR"] / 2.0, x, z, D.y_face - oc, D.y_panel0 + oc))
        feats["front_frame"].append(
            ("panel standoff %d and its webs" % (k + 1),
             [min(x - r, ex), max(x + r, ex), D.y_face, D.y_panel0, min(z - r, ez),
              max(z + r, ez)], "PANEL_HOLE_INSET, PANEL_MARGIN, STANDOFF_D, or the control"))
    frame = L.cut(L.fuse(adds), bores)
    feats["front_frame"].append(("frame ring", [bx0, bx1, D.y_face, D.y_frame, zb, z_ft],
                                 "FACE_H / FACE_W, BEZEL_OVERLAP, WALL, LID, FLOOR"))
    return {"body": body, "rear_plate": plate, "lid": lid, "front_frame": frame}, feats


# ------------------------------------------------------------------------------------- checks --
def _common(P, a, b):
    """(volume, thinnest extent, box) of what two shapes share, or None."""
    if not a.BoundBox.intersect(b.BoundBox):
        return None
    com = a.common(b)
    if com.isNull() or com.Volume <= P["VOLUME_EPS"]:
        return None
    cb = com.optimalBoundingBox()
    pieces = []
    for s in (com.Solids if len(com.Solids) > 1 else []):
        b = s.BoundBox
        pieces.append([b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax])
    box = [cb.XMin, cb.XMax, cb.YMin, cb.YMax, cb.ZMin, cb.ZMax]
    return com.Volume, min(cb.XLength, cb.YLength, cb.ZLength), box, pieces or [box]


def _where(feats, part, pieces):
    """Which named features of a case part an overlap is in, and the parameters that move them."""
    labels, moves = [], []
    for box in pieces:
        cx, cy, cz = (box[0] + box[1]) / 2.0, (box[2] + box[3]) / 2.0, (box[4] + box[5]) / 2.0
        for label, fb, mv in feats.get(part, []):
            if fb[0] <= cx <= fb[1] and fb[2] <= cy <= fb[3] and fb[4] <= cz <= fb[5]:
                if label not in labels:
                    labels.append(label)
                if mv not in moves:
                    moves.append(mv)
                break
    if not labels:
        return part.replace("_", " "), ""
    return "%s (%s)" % (" and ".join(labels), part.replace("_", " ")), "; ".join(moves)


def check(P, D, M, insides, case, feats):
    """Everything that is checked on the built solids. Returns the list of checks, each
    {name, ok, detail} - ok False is exit code 1."""
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": ok, "detail": detail})

    # ---- each case part is one sound solid, and no two share material
    sick = [k for k, s in case.items() if not s.isValid() or len(s.Solids) != 1]
    add("case parts are single sound solids", not sick,
        "all %d" % len(case) if not sick else "not sound: " + ", ".join(sick))
    mine = [it for it in insides if it["kind"] != "carrier" and "ref" not in it]
    sick = [it["name"] for it in mine if not it["shape"].isValid()]
    add("inside solids drawn here are sound", not sick,
        "all %d" % len(mine) if not sick else "not sound: " + ", ".join(sick))
    names = list(case)
    clash = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            c = _common(P, case[a], case[b])
            if c and c[1] >= L.CONTACT:
                clash.append("%s into %s, %s mm3" % (a, b, n(c[0])))
    add("case parts do not overlap each other", not clash,
        "none overlap" if not clash else "; ".join(clash))

    # ---- every inside solid against every case solid
    hits, squeeze, touch = [], {}, 0
    for part, cs in case.items():
        for it in insides:
            c = _common(P, cs, it["shape"])
            if not c:
                continue
            vol, thin, box, pieces = c
            if it["dt13"] and part == "rear_plate" and thin <= P["SEAL_SQUEEZE_MAX"]:
                squeeze[it["name"]] = squeeze.get(it["name"], 0.0) + vol
                continue
            if thin < L.CONTACT:
                touch += 1
                continue
            label, moves = _where(feats, part, pieces)
            what = "the room kept clear" if it["kind"] == "keepout" else "the part"
            hits.append("%s is inside %s '%s' by %s mm3 at X %s..%s, Y %s..%s, Z %s..%s%s"
                        % (label, what, it["name"].replace("keep-out: ", ""), n(vol),
                           n(box[0]), n(box[1]), n(box[2]), n(box[3]), n(box[4]), n(box[5]),
                           (": move one of them - %s" % moves) if moves else ""))
    add("insides clear of the case (%d solids against %d)" % (len(insides), len(case)), not hits,
        "0 interferences%s%s" % (
            ("; DT13 flange seals squeezed against the plate, as intended: %s mm3"
             % n(sum(squeeze.values()))) if squeeze else "",
            ("; %d faces resting on faces" % touch) if touch else "")
        if not hits else "%d interferences: %s" % (len(hits), " | ".join(hits)))

    # ---- the real inside parts against each other (rooms kept clear are not parts)
    real = [it for it in insides if it["kind"] != "keepout"]
    hits = []
    for i, a in enumerate(real):
        for b in real[i + 1:]:
            if a["kind"] == "carrier" and b["kind"] == "carrier":
                continue
            c = _common(P, a["shape"], b["shape"])
            if c and c[1] >= L.CONTACT:
                hits.append("'%s' into '%s' by %s mm3 at X %s..%s, Y %s..%s, Z %s..%s"
                            % (a["name"], b["name"], n(c[0]), n(c[2][0]), n(c[2][1]), n(c[2][2]),
                               n(c[2][3]), n(c[2][4]), n(c[2][5])))
    add("inside parts clear of each other", not hits,
        "0 interferences" if not hits else "%d interferences: %s" % (len(hits), " | ".join(hits)))

    # ---- the margins the fit rules measured (they passed, or nothing would be built)
    for name, (value, least) in M.items():
        add(name, value >= least - P["EPS"],
            "%s mm (least allowed %s)" % ("no pair" if value == float("inf") else n(value),
                                          n(least)))

    # ---- can it go in from the front (said, not judged: a typed FACE_H may ask for the step)
    ok, line = front_install(P, D)
    add("front install", True if ok else None, line.split(": ", 1)[1])

    # ---- the envelope
    if D.env is None:
        add("envelope (V-113 opening, V-102 depth)", None,
            "not measured - ENVELOPE is None, nothing checked (confirm)")
    else:
        for name, ok, msg in D.env:
            add("envelope: " + name, ok, msg)
    return checks


# ------------------------------------------------------------------------------------ one run --
def numbers(P, D):
    """The derived dimensions the report lists."""
    out = {
        "face_w": D.face_w, "face_w_is": "typed" if D.face_w_typed else "derived",
        "face_h": D.face_h,
        "face_h_is": "typed" if D.face_h_typed else "derived",
        "face_h_to_cover_the_body": D.face_h_body,
        "face_h_the_controls_need": D.face_h_controls,
        "sketch": [P["SKETCH_W"], P["SKETCH_H"]],
        "controls_anchor": P["CONTROLS_ANCHOR"],
        "controls_block_below_face_top": D.ctrl_top,
        "controls_block_above_face_bottom": D.ctrl_bottom,
        "body_w": D.body_w, "body_w_needed_by_carrier": D.body_w_need,
        "body_h": D.rear_h, "body_h_the_rows_need": D.body_h_need,
        "front_h": D.front_h, "rear_h": D.rear_h, "rear_above_front": D.rise,
        "rear_above_face_top": D.z_lid - D.face_h, "stepped": D.stepped,
        "front_install": front_install(P, D)[0],
        "front_install_line": front_install(P, D)[1],
        "carrier_pushed_back_by_the_lid_beam": D.carrier_pushed,
        "box_depth": D.y_end, "depth_to_plate_outer_face": D.y_plate1,
        "depth_to_receptacle_tips": D.y_tip, "depth_with_plugs": D.y_plugs,
        "ribbon_header_distance": D.ribbon,
        "row_pitch": P["ROW_PITCH"] if D.ups else None,
        "row_pitch_least": D.get("pitch_min"),
        "carrier": "the drawn board's STEP" if D.get("carrier_real") else "stand-in blocks",
        "carrier_front_edge_y": D.cy0, "carrier_underside_z": D.cz0,
        "upper_board_underside_z": D.uz0 if D.ups else None,
        "lid_underside_z": D.z_rim,
        "panel_board": [D.px1 - D.px0, D.pz1 - D.pz0],
        "connector_edge_needs": D.edge_need,
        "smallest_opening_it_slides_through": [D.body_w, max(D.front_h, D.rear_h)],
        "cutouts": [{"name": c.name, "part": c.part, "row": c.row, "fitted": c.fitted,
                     "x": c.X, "z": c.Z, "w": c.te["w"], "h": c.te["h"], "r": c.te["r"],
                     "screw_pitch": c.te["pitch"], "screw_hole": c.te["hole"],
                     "te_page": c.te["page"]} for c in D.conns],
        "controls": [{"name": c.name, "kind": c.kind, "x": c.X, "z": c.Z} for c in D.controls],
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


def front_install(P, D):
    """(yes or no, the one line that says it): can the unit go into its opening from the front,
    like a head unit (D-480)? Yes when it is one height front to back; no when the rear steps up
    behind a face too low to cover it."""
    if not D.stepped:
        return True, ("front install: yes - one height front to back, %s x %s; it passes an "
                      "opening that size and the %s x %s face covers it by BEZEL_OVERLAP %s a side"
                      % (n(D.body_w), n(D.rear_h), n(D.face_w), n(D.face_h),
                         n(P["BEZEL_OVERLAP"])))
    return False, ("front install: no - the rear is %s mm taller than the face covers (rear %s, "
                   "front section %s behind a %s face); it goes in from behind or with the dash "
                   "open. Set FACE_H to None, or to at least %s, for a unit that goes in from "
                   "the front" % (n(D.rise), n(D.rear_h), n(D.front_h), n(D.face_h),
                                  n(D.face_h_body)))


# ------------------------------------------------------------------------------------ outputs --
def _safe(name):
    return "".join(ch if ch.isalnum() else "_" for ch in name).strip("_")


def clear_outputs(outdir):
    """A refused build leaves no stale geometry behind to be mistaken for this one."""
    gone = []
    for name in OUTPUTS + tuple("view-%s.svg" % v for v in VIEWS):
        path = os.path.join(outdir, name)
        if os.path.exists(path):
            os.remove(path)
            gone.append(name)
    return gone


def write_model(outdir, insides, case):
    """climate-unit.FCStd (groups Insides > Keepouts, Case), one STEP per case part, and the
    assembly STEP (parts only: the kept-clear rooms are in the FCStd, not the STEP)."""
    files = []
    doc = FreeCAD.newDocument("climate_unit")
    g_in = doc.addObject("App::DocumentObjectGroup", "Insides")
    g_keep = doc.addObject("App::DocumentObjectGroup", "Keepouts")
    g_in.addObject(g_keep)
    g_case = doc.addObject("App::DocumentObjectGroup", "Case")
    grouped, order = {}, []
    for it in insides:
        key = (it["group"], it["kind"] == "keepout")
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(it["shape"])
    solid_objs = []
    for (label, keep) in order:
        shapes = grouped[(label, keep)]
        obj = doc.addObject("Part::Feature", _safe(label))
        obj.Label = label
        obj.Shape = shapes[0] if len(shapes) == 1 else Part.makeCompound(shapes)
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
        path = os.path.join(outdir, "climate-unit-%s.step" % name)
        s.exportStep(path)
        files.append(path)
    doc.recompute()
    path = os.path.join(outdir, "climate-unit.FCStd")
    if os.path.exists(path):
        os.remove(path)                                # or FreeCAD keeps a .FCBak of every build
    doc.saveAs(path)
    files.append(path)
    path = os.path.join(outdir, "climate-unit.step")
    try:
        import Import
        Import.export(solid_objs, path)
    except Exception:
        Part.makeCompound([o.Shape for o in solid_objs]).exportStep(path)
    files.append(path)
    FreeCAD.closeDocument(doc.Name)
    return files


def _paths(shape, flip, deflection):
    out = []
    if shape is None or shape.isNull():
        return out
    for e in shape.Edges:
        try:
            pts = e.discretize(Deflection=deflection) if not isinstance(e.Curve, Part.Line) else \
                [e.valueAt(e.FirstParameter), e.valueAt(e.LastParameter)]
        except Exception:
            continue
        if len(pts) > 1:
            out.append("M" + " L".join("%.2f %.2f" % (p.x, flip - p.y) for p in pts))
    return out


def write_views(P, outdir, insides, case, D):
    """Four orthographic line drawings by hidden-line projection (TechDraw.projectEx). Parts in
    black (hidden edges grey dashes), the rooms kept clear in blue, and on the front view the
    sketch's control block in orange, so the spare face round it shows. Drawn from stand-in blocks
    for the carrier: TE's connector models make the projection fail."""
    import TechDraw
    M = FreeCAD.Matrix
    looks = {   # the unit's (X, Y, Z) -> the picture's (right, up, toward the eye)
        "front": M(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1),
        "back": M(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1),
        "side": M(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1),
        "top": M(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
    }
    said = {"front": "from the cabin", "back": "from behind, as it is plugged",
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
               "<title>Climate control unit mock-up - %s</title>" % view,
               '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="white"/>'
               % (bb.XMin - m, bb.YMin - m, w, h)]
        svg.append('<g fill="none" stroke="#9a9a9a" stroke-width="%.2f" stroke-dasharray="%.2f '
                   '%.2f">' % (sw / 2.0, 4 * sw, 4 * sw))
        svg += ['<path d="%s"/>' % d for k in (5, 8) for d in _paths(pa[k], flip, dfl)]
        svg.append("</g>")
        if pb:
            svg.append('<g fill="none" stroke="#2f6fb5" stroke-width="%.2f" stroke-dasharray='
                       '"%.2f %.2f">' % (sw, 8 * sw, 4 * sw))
            svg += ['<path d="%s"/>' % d for k in (0, 3) for d in _paths(pb[k], flip, dfl)]
            svg.append("</g>")
        svg.append('<g fill="none" stroke="black" stroke-width="%.2f" stroke-linecap="round">'
                   % sw)
        svg += ['<path d="%s"/>' % d for k in (0, 3) for d in _paths(pa[k], flip, dfl)]
        svg.append("</g>")
        extra = "; blue = room kept clear" if pb else ""
        if view == "front":
            x0, x1, z0, z1 = D.block
            svg.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" '
                       'stroke="#d9730d" stroke-width="%.2f" stroke-dasharray="%.2f %.2f"/>'
                       % (x0, flip - z1, x1 - x0, z1 - z0, sw, 8 * sw, 4 * sw))
            extra = "; orange = the sketch's %s x %s control block, anchored %s" % (
                n(P["SKETCH_W"]), n(P["SKETCH_H"]), P["CONTROLS_ANCHOR"])
        for k, line in enumerate((
                "Climate control unit, mock-up: %s (%s), %.1f x %.1f mm."
                % (view, said[view], bb.XLength, bb.YLength),
                "Provisional, nothing measured. Carrier as stand-in blocks%s." % extra)):
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
        "what": "Climate control unit mock-up (D-479, D-480, Y14) - provisional, nothing measured",
        "rc": res["rc"],
        "built": res["case"] is not None,
        "problems": res["problems"],
        "notes": res["notes"],
        "numbers": res["numbers"],
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
    print("Climate control unit - MOCK-UP (D-479, D-480, Y14) - provisional, nothing measured (R11)")
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
    print("WIDTH RULE: the carrier is %s wide, so the body is %s (carrier + 2 x (GAP %s + WALL "
          "%s)) and the face %s (%s)." % (
              n(P["CARRIER_W"]), n(D.body_w), n(P["GAP"]), n(P["WALL"]), n(D.face_w),
              "typed" if D.face_w_typed else "DERIVED: body + 2 x BEZEL_OVERLAP %s"
              % n(P["BEZEL_OVERLAP"])))
    if D.face_h_typed:
        how = "typed; %s would cover the body, the control block needs %s" % (
            n(D.face_h_body), n(D.face_h_controls))
    elif D.face_h_body >= D.face_h_controls:
        how = "DERIVED: body + 2 x BEZEL_OVERLAP %s" % n(P["BEZEL_OVERLAP"])
    else:
        how = "DERIVED: the least the control block needs; the rows need only a %s body" \
              % n(D.body_h_need)
    print("HEIGHT RULE: the two rows need a body %s tall (floor %s + bosses %s%s + DT13 %s + "
          "TOP_GAP %s + lid %s); the body is %s and the face %s (%s)." % (
              n(D.body_h_need), n(P["FLOOR"]), n(P["BOSS_H"]),
              (" + ROW_PITCH %s" % n(P["ROW_PITCH"])) if D.ups else "", n(D.dt_top),
              n(P["TOP_GAP"]), n(P["LID"]),
              ("%s at the rear, %s for the first %s mm" % (n(D.rear_h), n(D.front_h),
                                                           n(P["FRONT_L"])))
              if D.stepped else n(D.rear_h), n(D.face_h), how))
    print("FACE: the sketch is %s x %s; this face is %s x %s, %s wider and %s taller. The "
          "sketch's control block is kept whole, anchored %s: %s of face above it, %s below."
          % (n(P["SKETCH_W"]), n(P["SKETCH_H"]), n(D.face_w), n(D.face_h),
             n(D.face_w - P["SKETCH_W"]), n(D.face_h - P["SKETCH_H"]), P["CONTROLS_ANCHOR"],
             n(D.ctrl_top), n(D.ctrl_bottom)))
    print()
    rows = [("face (FACE_W x FACE_H)", "%s x %s" % (n(D.face_w), n(D.face_h))),
            ("body width", n(D.body_w))]
    if D.stepped:
        rows += [("front height (first %s mm behind the face)" % n(P["FRONT_L"]), n(D.front_h)),
                 ("rear height (derived, never typed)", n(D.rear_h))]
    else:
        rows += [("body height (one height front to back)", n(D.rear_h))]
    rows += [
        ("box depth (face front to the rear lip)", n(D.y_end)),
        ("  to the rear plate's outer face", n(D.y_plate1)),
        ("  to the receptacles' tips", n(D.y_tip)),
        ("depth with plugs (PLUG_L + CABLE_BEND)", n(D.y_plugs)),
        ("carrier's front edge", "Y %s%s" % (n(D.cy0), (
            " (%s further back than CARRIER_FRONT_GAP asks: it drops in behind the beam under "
            "the lid's front edge)" % n(D.carrier_pushed)) if D.carrier_pushed > P["EPS"] else "")),
        ("ribbon headers, straight line", "n/a" if D.ribbon is None else
         "%s (panel header face to the carrier's J4 face; the ribbon stays inside)"
         % n(D.ribbon)),
        ("ROW_PITCH (least that builds)", "%s (%s)" % (n(P["ROW_PITCH"]), n(D.pitch_min))
         if D.ups else "no upper row"),
        ("panel board", "%s x %s" % (n(D.px1 - D.px0), n(D.pz1 - D.pz0))),
        ("carrier", N["carrier"]),
    ]
    for k, v in rows:
        print("  %-46s %s" % (k, v))
    print()
    print("rear plate, seen from behind (X is the unit's, 0 = the cabin's left):")
    for c in sorted(D.conns, key=lambda c: (c.row != "upper", -c.X)):
        print("  %-5s %-24s %-9s X %7s  Z %6s  %s" % (
            c.row, c.name, c.part, n(c.X), n(c.Z),
            "TE cut-out %s x %s R%s, screws %s apart (114-151046 p.%d)"
            % (n(c.te["w"]), n(c.te["h"]), n(c.te["r"]), n(c.te["pitch"]), c.te["page"])
            if c.fitted else "RESERVED - no cut-out, flange zone kept flat, outline scribed"))
    print()
    print("checks:")
    for c in res["checks"]:
        mark = {True: "ok  ", False: "FAIL", None: "--  "}[c["ok"]]
        print("  %s %s: %s" % (mark, c["name"], c["detail"]))
    print()
    print("confirm (guesses until measured or bought - %d):" % len(U.CONFIRM))
    for k in sorted(U.CONFIRM):
        v = P[k]
        print("  %-18s %-10s %s" % (k, "(table)" if isinstance(v, (list, dict)) else
                                    "None" if v is None else v, U.CONFIRM[k]))
    print()
    for f in files:
        print("  wrote %-34s %9d bytes" % (os.path.basename(f), os.path.getsize(f)))
    if views_note:
        print("  views: " + views_note)
    print("exit code %d" % res["rc"])


# ------------------------------------------------------------------------------------ selftest --
OUTCOMES = {"clear": "BUILT CLEAR", "fails": "BUILT, FAILS", "refused": "REFUSED"}


def selftest(U, src):
    """Rebuild under each parameter set of unit_params.SELFTEST, in memory (no files written), and
    hold each to the outcome stored with it: `clear` (built, every check passes), `fails` (built,
    a check fails) or `refused` (a fit rule, in words). Exit 0 every set as expected; 1 an outcome
    differs - a later edit changed what the model does; 3 a set crashed."""
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
        size = "face %s x %s, body %s x %s%s, depth %s / %s with plugs, front install %s" % (
            n(N["face_w"]), n(N["face_h"]), n(N["body_w"]), n(N["rear_h"]),
            (" (front %s)" % n(N["front_h"])) if N["stepped"] else "", n(N["box_depth"]),
            n(N["depth_with_plugs"]), "yes" if N["front_install"] else "no")
        rows.append((label, want, "BUILT, FAILS" if fails else "BUILT CLEAR", size,
                     ["%s: %s" % (c["name"], c["detail"]) for c in fails]))
    print("=" * 96)
    print("Climate control unit mock-up - self-test: %d parameter sets" % len(rows))
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
