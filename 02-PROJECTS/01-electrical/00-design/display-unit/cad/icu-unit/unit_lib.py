"""The ICU unit's mock-up (D-491, D-270, D-268, Y19): layout, fit rules, solids, checks, output.

Run by `make_unit.py` through FreeCAD's headless interpreter, never on its own. Holds NO dimension:
every number comes from `unit_params.py` (the parameter table), from `../../../tools/enclosure_lib.py` (TE's
DT13 panel cut-outs, the primitives) or from the ICU carrier's own files, which it only reads:

- `../icu-carrier/enclosure/board.json`  the carrier's outline, holes and footprints;
- `../icu-carrier/enclosure/probe.json`  each DT13's flange, housing section and tip, and every
                                          part's 3D extent (the XIAO, J4, SW1 ...), as read from the
                                          board STEP by the Y7 enclosure build;
- `../icu-carrier/icu-carrier.step`      the board's 3D model, when it is there (git-ignored). With
                                          it the real board goes in the box; without it, plain
                                          stand-in blocks of the probed sizes do.

Four steps, in this order, and nothing is drawn until the second has passed:

    derive(P, src)      every position, from the parameters - arithmetic only
    validate(P, src)    the fit rules: sentences naming the parameter and the way to move it
    build_*             the solids, all from what derive() returned
    check(...)          interference of every inside solid with every case solid, the RF window

Frame: X across the face (0 = left seen from the driver's seat), Y back from the bezel's front, Z up
from the bezel's bottom edge. The carrier keeps its board frame's directions (its DT13s face +y in
board.json, which is the rear here), so it is only moved, never turned.

Copied in method, and in places in code, from `../../../control-unit/cad/climate-unit/unit_lib.py` (Y14), which it does
not import: the helpers NS / n / num, the interference test and its feature naming, the stand-in
DT13, the rear plate, the lid with its gasket groove and lugs, the side screw bosses, the writers,
the report and the self-test. Owns no fact in the record: the sizes that place this unit are work
rows C4 and M-1 / C1 (`01-electrical/data/work.csv`); the parts are P111, P117 to P122.
"""
import copy
import math
import os

import FreeCAD
import Part
from FreeCAD import Vector as V

import enclosure_lib as L

NONE_OK = ("FACE_W", "FACE_H", "BUTTON_X", "BT_X", "BT_Z")
NEG_OK = ("BUTTON_X", "BUTTON_Z", "FLEX_X", "ACTIVE_DX", "ACTIVE_DZ")
ZERO_OK = ("DISP_TAPE", "DISP_BACK_CLEAR", "DISP_CLEAR", "WINDOW_MARGIN", "BEZEL_LEDGE",
           "BEZEL_SKIN", "CONTROL_EDGE", "FLEX_ROOM", "FLEX_SLOT_CLEAR", "BT_UNDER_H", "BT_Z",
           "CARRIER_FRONT_GAP", "CARRIER_BOT_H", "BOSS_H", "BUTTON_GAP", "BUTTON_HOLE_CLEAR",
           "IDC_PLUG_H", "IDC_GROW", "CABLE_BEND", "PLUG_GROW", "PLUG_SIDE_CLEAR", "TOP_GAP",
           "RIM_H", "PLATE_LIP", "SLOT_DEPTH", "SLOT_CLEAR", "FLOOR_GROOVE", "CUTOUT_CLEAR",
           "BEZEL_OVERLAP", "GAP", "LUG_EMBED", "INSERT_SKIN", "BOARD_JSON_EDGE", "OUTLINE_TOL",
           "COURTYARD_MATCH", "SEAL_SQUEEZE_MAX", "VOLUME_EPS", "EPS", "GASKET_R", "RF_KEEPOUT",
           "BT_X")
LAYOUTS = ("behind", "below")
SIDES = ("left", "centre", "right")
RF_WALLS = ("left", "right", "lid", "floor", "rear")
NAME = "icu-unit"
CASE_PARTS = ("body", "rear_plate", "lid", "front_frame")
OUTPUTS = ("%s.FCStd" % NAME, "%s.step" % NAME) + tuple("%s-%s.step" % (NAME, p) for p in CASE_PARTS)
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


def _overlap(a0, a1, b0, b1):
    return a0 < b1 and b0 < a1


def _box_gap(a, b):
    """Clear distance between two axis-aligned boxes [x0, x1, y0, y1, z0, z1] (0 = touching or
    overlapping)."""
    d = [max(0.0, b[2 * i] - a[2 * i + 1], a[2 * i] - b[2 * i + 1]) for i in range(3)]
    return math.sqrt(sum(v * v for v in d))


def _dist(a, b):
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(a, b)))


# ------------------------------------------------------------------------------------- source --
def load_source(cad_dir, P):
    """The carrier's files, read once: board.json, probe.json and the STEP if it is there."""
    car = os.path.join(cad_dir, "icu-carrier")
    enc = os.path.join(car, "enclosure")
    src = {"problems": [], "notes": [], "step": None}
    for name in ("board.json", "probe.json"):
        path = os.path.join(enc, name)
        if not os.path.exists(path):
            src["problems"].append(
                "%s is missing from icu-carrier/enclosure: run that folder's make_enclosure.py "
                "(and 00-design/tools/enclosure_extract.py icu-carrier) first - this mock-up reads the carrier "
                "from it." % name)
            return src
        src[name.split(".")[0]] = L.load(path)
    board = src["board"]
    step = os.path.join(car, "icu-carrier.step")
    if not os.path.exists(step):
        src["notes"].append("icu-carrier.step is not there: the carrier is drawn as stand-in "
                            "blocks from board.json and probe.json")
        return src
    solids = Part.read(step).Solids
    thin = [s for s in solids if s.BoundBox.ZLength <= board["thickness"] + P["OUTLINE_TOL"]]
    if not thin:
        src["notes"].append("icu-carrier.step holds no board solid: stand-in blocks used")
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
    if P["CARRIER_LAYOUT"] not in LAYOUTS:
        bad.append("CARRIER_LAYOUT is %r: it must be one of %s."
                   % (P["CARRIER_LAYOUT"], ", ".join(repr(a) for a in LAYOUTS)))
    cx = P["CARRIER_X"]
    if not (cx in SIDES or (num(cx) and cx >= 0)):
        bad.append("CARRIER_X is %r: it must be one of %s, or a number of mm (the carrier's left "
                   "edge from the inside of the left wall)." % (cx, ", ".join(repr(a) for a in SIDES)))
    if P["RF_WINDOW_ON"] not in RF_WALLS:
        bad.append("RF_WINDOW_ON is %r: it must be one of %s."
                   % (P["RF_WINDOW_ON"], ", ".join(repr(a) for a in RF_WALLS)))
    for name in ("DISPLAY_CENTRED", "CARRIER_STEP"):
        if not isinstance(P[name], bool):
            bad.append("%s is %r: it must be True or False." % (name, P[name]))
    c8 = P["BT_CN8"]
    if not (isinstance(c8, (tuple, list)) and len(c8) == 2 and num(c8[0]) and num(c8[1])):
        bad.append("BT_CN8 %r must be a pair of numbers in mm (right, up from the board's "
                   "bottom-centre)." % (c8,))
    names = []
    for row in P["DRIVER_BOARDS"]:
        ok = (isinstance(row, (tuple, list)) and len(row) == 7 and isinstance(row[0], str)
              and isinstance(row[1], str) and all(num(v) and v > 0 for v in row[2:5])
              and num(row[5]) and row[5] >= 0 and (row[6] is None or (num(row[6]) and row[6] >= 0)))
        if not ok:
            bad.append("DRIVER_BOARDS row %r is not (name, what, w, h, depth, x0, z0): w, h and "
                       "depth more than 0, x0 0 or more, z0 0 or more or None." % (row,))
        else:
            if row[0] in names or row[0] == "BT817":
                bad.append("DRIVER_BOARDS: the name %r is used twice (or is 'BT817'): give each "
                           "board its own name." % row[0])
            names.append(row[0])
    if not bad and P["FLEX_TO"] not in names + ["BT817"]:
        bad.append("FLEX_TO is %r, which is no board in the unit: use %s."
                   % (P["FLEX_TO"], " or ".join(repr(x) for x in names + ["BT817"])))
    for name in ("BEZEL_SCREWS_AT", "LID_LUGS"):
        if not P[name] or not all(num(f) and 0 <= f <= 1 for f in P[name]):
            bad.append("%s %r must be one or more fractions from 0 to 1." % (name, P[name]))
    for row in P["SIDE_SCREWS"]:
        if not (isinstance(row, (tuple, list)) and len(row) == 2 and num(row[0]) and num(row[1])):
            bad.append("SIDE_SCREWS row %r is not a pair of numbers in mm (Y, Z)." % (row,))
    if not isinstance(P["CONNECTOR_NAMES"], dict):
        bad.append("CONNECTOR_NAMES must be a dict of carrier reference to housing name.")
    env = P["ENVELOPE"]
    if env is not None:
        ok = isinstance(env, dict) and all(num(env.get(k)) and env[k] > 0
                                           for k in ("OPENING_W", "OPENING_H", "DEPTH"))
        if not ok:
            bad.append("ENVELOPE must be None or {OPENING_W, OPENING_H, DEPTH}, numbers of mm.")
    return bad


# ------------------------------------------------------------------------------------- derive --
def derive(P, src):
    """Every position in the unit, from the parameters and the carrier's files. Arithmetic only."""
    TE = L.TE_CUTOUT
    board, pr = src["board"], src["probe"]
    D = NS(problems=[], notes=list(src["notes"]))
    e, eps = P["BOARD_JSON_EDGE"], P["EPS"]
    o = board["outline"]
    bx0b, bx1b, by0b, by1b = o["xmin"] + e, o["xmax"] - e, o["ymin"] + e, o["ymax"] - e
    D.carrier_w, D.carrier_d = bx1b - bx0b, by1b - by0b
    refs = pr["refs"]
    c_left = min(bx0b, pr["content"]["xmin"])      # the carrier's whole extent across, board frame
    c_right = max(bx1b, pr["content"]["xmax"])
    D.overhang_left = bx0b - c_left

    # ---- the carrier's DT13s, as board.json and probe.json have them
    conns = []
    for f in board["footprints"]:
        if not L.is_dt13(f) or f["dnp"]:
            continue
        d = pr["dt13"].get(f["ref"]) or {}
        r = refs.get(f["ref"])
        if not d.get("model") or r is None or d.get("outward") != 1 or f["footprint"] not in TE:
            D.problems.append(
                "probe.json has no usable model of %s (%s) on the carrier's connector edge: "
                "re-run icu-carrier/enclosure/make_enclosure.py with the board STEP present."
                % (f["ref"], f["footprint"]))
            continue
        h = d["housing"]
        conns.append(NS(ref=f["ref"], name=P["CONNECTOR_NAMES"].get(f["ref"], f["ref"]),
                        part=f["footprint"], te=TE[f["footprint"]], xb=(h[0] + h[1]) / 2.0,
                        zc=(h[2] + h[3]) / 2.0, flange=d["flange"], housing=h,
                        y_flange=d["y_flange"], y_tip=d["y_tip"], body=r))
    if not conns and not D.problems:
        D.problems.append("board.json has no fitted DT13 on the carrier: nothing to build the "
                          "rear plate around.")
    for ref in (P["RF_REF"], "J4", "SW1"):
        if ref not in refs:
            D.problems.append("probe.json has no 3D extent for %s: re-run "
                              "icu-carrier/enclosure/make_enclosure.py with the board STEP "
                              "present." % ref)
    if D.problems:
        return D
    conns.sort(key=lambda c: c.xb)
    D.conns = conns
    D.dt_top = max(c.body[5] for c in conns)       # above the board's underside
    D.board_top = pr["board_top"]

    G, WL, BZ = P["GAP"], P["WALL"], P["BEZEL_OVERLAP"]
    FL, LT = P["FLOOR"], P["LID"]
    dw, dh, clr, BB = P["DISP_W"], P["DISP_H"], P["DISP_CLEAR"], P["BEZEL_BORDER"]
    hr, br = P["BUTTON_HEAD_D"] / 2.0, P["BUTTON_BODY_D"] / 2.0
    edge = P["CONTROL_EDGE"]
    D.button_derived = P["BUTTON_X"] is None
    cx = P["CARRIER_X"]
    if D.button_derived:                               # beside the display, on the carrier's side
        side = -1.0 if cx == "left" or (num(cx) and cx + D.carrier_w / 2.0 < dw / 2.0) else 1.0
        bx = side * (dw / 2.0 + P["BUTTON_GAP"] + max(hr, br))
    else:
        bx = P["BUTTON_X"]
    bz = P["BUTTON_Z"]
    D.button_rel = (bx, bz)
    # BUTTON_FITTED False (D-580: the page button left the Display Unit): no hole, no solid, no
    # size it asks of the face or the body, no rule it is held to
    D.button = bool(P.get("BUTTON_FITTED", True))
    BTN = (lambda rows: rows) if D.button else (lambda rows: [])

    # ---- across (X), measured first from the display's centre: what each side of the face needs
    left = [(dw / 2.0 + BB, "the display + BEZEL_BORDER"),
            (dw / 2.0 + clr + WL + BZ, "the display's pocket + WALL + BEZEL_OVERLAP")] + BTN([
            (-bx + hr + edge, "the page button + CONTROL_EDGE"),
            (-bx + br + G + WL + BZ, "the page button's body inside the wall")])
    right = [(dw / 2.0 + BB, "the display + BEZEL_BORDER"),
             (dw / 2.0 + clr + WL + BZ, "the display's pocket + WALL + BEZEL_OVERLAP")] + BTN([
             (bx + hr + edge, "the page button + CONTROL_EDGE"),
             (bx + br + G + WL + BZ, "the page button's body inside the wall")])
    lft = max(left)[0]
    # the inside, from the left wall: the carrier, the BT817 board, the driver boards
    inner = [(c_right - c_left + 2 * G, "the carrier and the XIAO's overhang, GAP each side")]
    if num(cx):
        inner.append((cx + c_right - bx0b + G, "CARRIER_X and the carrier"))
    inner.append(((P["BT_X"] + P["BT_W"] / 2.0 + G) if P["BT_X"] is not None
                  else P["BT_W"] + 2 * G, "the BT817 board"))
    for row in P["DRIVER_BOARDS"]:
        inner.append((row[5] + row[2] + G, "the %s at its x0" % row[0]))
    in_need = max(inner)
    ix0_rel = -(lft - BZ - WL)
    right.append((ix0_rel + in_need[0] + WL + BZ, in_need[1]))
    rgt = max(right)[0]
    if P["DISPLAY_CENTRED"]:
        lft = rgt = max(lft, rgt)
    D.face_w_need = lft + rgt
    D.width_set_by = [max(left)[1], max(right)[1]]
    D.face_w_typed = P["FACE_W"] is not None
    if D.face_w_typed:
        if P["FACE_W"] < D.face_w_need - eps:
            D.problems.append(
                "FACE_W %s is narrower than the unit needs (%s: left of the display's centre %s, "
                "set by %s; right %s, set by %s): raise FACE_W to at least %s, or set it to None "
                "and it is derived." % (n(P["FACE_W"]), n(D.face_w_need), n(lft), D.width_set_by[0],
                                        n(rgt), D.width_set_by[1], n(D.face_w_need)))
            return D
        extra = (P["FACE_W"] - D.face_w_need) / 2.0
        lft, rgt = lft + extra, rgt + extra
    D.face_w = lft + rgt
    D.xd = lft                                       # the display's centre
    D.bx0, D.bx1 = BZ, D.face_w - BZ
    D.ix0, D.ix1 = D.bx0 + WL, D.bx1 - WL
    D.body_w = D.bx1 - D.bx0

    # ---- the carrier across, and what stands on the display plate
    if cx == "left":
        dx = D.ix0 + G - c_left
    elif cx == "right":
        dx = D.ix1 - G - c_right
    elif cx == "centre":
        dx = (D.ix0 + D.ix1) / 2.0 - (bx0b + bx1b) / 2.0
    else:
        dx = D.ix0 + cx - bx0b
    D.dx = dx
    D.cx0, D.cx1 = bx0b + dx, bx1b + dx               # the board's edges
    D.kx0, D.kx1 = c_left + dx, c_right + dx          # everything on it
    j4 = refs["J4"]
    D.j4x = (j4[0] + j4[1]) / 2.0 + dx
    bw, bh = P["BT_W"], P["BT_H"]
    if P["BT_X"] is None:
        xc = D.j4x - P["BT_CN8"][0]
        xc = min(max(xc, D.ix0 + G + bw / 2.0), D.ix1 - G - bw / 2.0)
    else:
        xc = D.ix0 + P["BT_X"]
    bt_d = P["BT_STANDOFF"] + P["BT_T"] + max(P["BT_PARTS_H"], P["CN8_T"] + P["IDC_PLUG_H"])
    plate_items = [NS(name="BT817", what="BT817 eval board (P117)", label="BT817 board",
                      x0=xc - bw / 2.0, x1=xc + bw / 2.0, h=bh, depth=bt_d, z_typed=P["BT_Z"],
                      param="BT_Z")]
    for (name, what, w, h, dep, x0, z0) in P["DRIVER_BOARDS"]:
        plate_items.append(NS(name=name, what=what, label=name, x0=D.ix0 + x0,
                              x1=D.ix0 + x0 + w, h=h, depth=dep, z_typed=z0,
                              param="DRIVER_BOARDS '%s' z0" % name))
    below = P["CARRIER_LAYOUT"] == "below"
    for it in plate_items:
        it.over_carrier = _overlap(it.x0, it.x1, D.kx0 - G, D.kx1 + G)

    # ---- up (Z), measured first from the display's centre
    bottom = [(dh / 2.0 + BB, "the display + BEZEL_BORDER"),
              (dh / 2.0 + clr + P["FLEX_ROOM"] + FL + BZ, "the display's pocket, FLEX_ROOM and "
               "the floor")] + BTN([
              (-bz + hr + edge, "the page button + CONTROL_EDGE"),
              (-bz + br + G + FL + BZ, "the page button's body above the floor")])
    bot = max(bottom)[0]
    # heights above the floor's inside face, which do not depend on the face
    D.cz0_f = P["BOSS_H"]
    D.cz1_f = D.cz0_f + D.board_top
    D.ktop_f = D.cz1_f + P["CARRIER_TOP_H"]
    for it in plate_items:
        if it.z_typed is not None:
            it.z0_f = it.z_typed
        elif below and it.over_carrier:
            it.z0_f = D.ktop_f + G
        else:
            it.z0_f = G
        it.z1_f = it.z0_f + it.h
    tops_f = [(D.cz0_f + D.dt_top + P["TOP_GAP"], "the DT13s + TOP_GAP"),
              (D.ktop_f + P["TOP_GAP"], "the room kept above the carrier + TOP_GAP")]
    tops_f += [(it.z1_f + P["RIM_H"] + G, "the %s under the lid's front beam" % it.name)
               for it in plate_items]

    # the button's body reaches past the display plate, under the lid's front beam, when it is
    # longer than the frame is deep
    y_frame = P["FACE_T"] + P["DISP_TAPE"] + P["DISP_T"] + P["DISP_BACK_CLEAR"] + P["BULKHEAD"]
    b_rim = P["RIM_H"] if P["FACE_T"] + P["BUTTON_DEPTH"] > y_frame + eps else 0.0

    def top_for(b):
        dz = b - BZ - FL                               # the display's centre above the floor
        t = [(dh / 2.0 + BB, "the display + BEZEL_BORDER"),
             (dh / 2.0 + clr + LT + BZ, "the display's pocket and the lid")] + BTN([
             (bz + hr + edge, "the page button + CONTROL_EDGE"),
             (bz + br + G + b_rim + LT + BZ, "the page button's body under the lid's beam")])
        t += [(h - dz + LT + BZ, why) for (h, why) in tops_f]
        return max(t)
    top, top_why = top_for(bot)
    if P["DISPLAY_CENTRED"]:
        bot = max(bot, top)
        top = max(top_for(bot)[0], bot)
    D.face_h_need = bot + top
    D.height_set_by = [max(bottom)[1], top_why]
    D.face_h_typed = P["FACE_H"] is not None
    if D.face_h_typed:
        if P["FACE_H"] < D.face_h_need - eps:
            D.problems.append(
                "FACE_H %s is lower than the unit needs (%s: below the display's centre %s, set "
                "by %s; above %s, set by %s): raise FACE_H to at least %s, or set it to None and "
                "it is derived." % (n(P["FACE_H"]), n(D.face_h_need), n(bot), D.height_set_by[0],
                                    n(top), D.height_set_by[1], n(D.face_h_need)))
            return D
        extra = (P["FACE_H"] - D.face_h_need) / 2.0
        bot, top = bot + extra, top + extra
    D.face_h = bot + top
    D.zd = bot
    D.zb = BZ
    D.zf = D.zb + FL
    D.z_rim = D.face_h - BZ - LT                      # the lid's underside, the frame's inside top
    D.z_lid = D.face_h - BZ
    D.body_h = D.z_lid - D.zb
    D.borders = {"left": D.xd - dw / 2.0, "right": D.face_w - D.xd - dw / 2.0,
                 "bottom": D.zd - dh / 2.0, "top": D.face_h - D.zd - dh / 2.0}

    # ---- the display, its window, its flex, the page button (absolute now)
    D.disp = [D.xd - dw / 2.0, D.xd + dw / 2.0, D.zd - dh / 2.0, D.zd + dh / 2.0]
    ax, az = D.xd + P["ACTIVE_DX"], D.zd + P["ACTIVE_DZ"]
    D.active = [ax - P["ACTIVE_W"] / 2.0, ax + P["ACTIVE_W"] / 2.0,
                az - P["ACTIVE_H"] / 2.0, az + P["ACTIVE_H"] / 2.0]
    m = P["WINDOW_MARGIN"]
    D.window = [D.active[0] - m, D.active[1] + m, D.active[2] - m, D.active[3] + m]
    D.bX, D.bZ = D.xd + bx, D.zd + bz
    D.y_face = P["FACE_T"]
    D.y_disp0 = D.y_face + P["DISP_TAPE"]
    D.y_disp1 = D.y_disp0 + P["DISP_T"]
    D.y_bulk0 = D.y_disp1 + P["DISP_BACK_CLEAR"]
    D.y_bulk1 = D.y_bulk0 + P["BULKHEAD"]
    D.y_frame = D.y_bulk1                              # the front frame ends, the body begins
    D.y_button = D.y_face + P["BUTTON_DEPTH"]
    fx = D.xd + P["FLEX_X"]
    D.flex = [fx - P["FLEX_W"] / 2.0, fx + P["FLEX_W"] / 2.0, D.y_disp0, D.y_bulk1,
              D.disp[2] - P["FLEX_ROOM"], D.disp[2]]

    # ---- what stands on the display plate, absolute
    for it in plate_items:
        it.z0, it.z1 = D.zf + it.z0_f, D.zf + it.z1_f
        it.y0, it.y1 = D.y_bulk1, D.y_bulk1 + it.depth
    D.plate_items = plate_items
    bt = plate_items[0]
    D.drivers = plate_items[1:]
    bt.yb0 = D.y_bulk1 + P["BT_STANDOFF"]              # the board's front face
    bt.yb1 = bt.yb0 + P["BT_T"]
    bt.xc = (bt.x0 + bt.x1) / 2.0
    i = P["BT_HOLE_INSET"]
    bt.holes = [(bt.x0 + i, bt.z0 + i), (bt.x1 - i, bt.z0 + i), (bt.x0 + i, bt.z1 - i),
                (bt.x1 - i, bt.z1 - i)]
    cnx, cnz = bt.xc + P["BT_CN8"][0], bt.z0 + P["BT_CN8"][1]
    bt.cn8 = [cnx - P["CN8_W"] / 2.0, cnx + P["CN8_W"] / 2.0, bt.yb1, bt.yb1 + P["CN8_T"],
              cnz - P["CN8_H"] / 2.0, cnz + P["CN8_H"] / 2.0]
    g = P["IDC_GROW"]
    bt.cn8_plug = [bt.cn8[0] - g, bt.cn8[1] + g, bt.cn8[3], bt.cn8[3] + P["IDC_PLUG_H"],
                   bt.cn8[4] - g, bt.cn8[5] + g]
    D.bt = bt

    # ---- going back (Y): the carrier
    D.cz0, D.cz1, D.ktop = D.zf + D.cz0_f, D.zf + D.cz1_f, D.zf + D.ktop_f
    least = [D.y_frame + WL + G]                       # it drops in past the lid's front beam
    if below:
        least.append(D.y_bulk1 + P["CARRIER_FRONT_GAP"])
    else:
        least += [it.y1 + P["CARRIER_FRONT_GAP"] for it in plate_items if it.over_carrier]
    if D.button and _overlap(D.bX - br, D.bX + br, D.kx0 - G, D.kx1 + G) and \
            _overlap(D.bZ - br, D.bZ + br, D.zf, D.ktop + G):
        least.append(D.y_button + G)
    D.cy0 = max(least)
    dy = D.cy0 - by0b
    D.dy = dy
    D.cy1 = by1b + dy

    def box_of(ref):
        r = refs[ref]
        return [r[0] + dx, r[1] + dx, r[2] + dy, r[3] + dy, D.cz0 + r[4], D.cz0 + r[5]]
    D.box_of = box_of
    D.ref_boxes = {ref: box_of(ref) for ref in refs}
    for c in conns:
        c.X, c.Z = c.xb + dx, D.cz0 + c.zc
        c.yf = c.y_flange + dy                         # the flange's front face
        c.tip = c.y_tip + dy
        c.box = box_of(c.ref)
    D.y_plate0 = max(c.yf for c in conns)              # the plate's inner face = flange fronts
    D.y_plate1 = D.y_plate0 + P["PLATE"]
    D.y_end = D.y_plate1 + P["PLATE_LIP"]
    D.y_tip = max(c.tip for c in conns)
    D.y_plugs = D.y_plate1 + P["PLUG_L"] + P["CABLE_BEND"]
    gr, cc = P["PLUG_GROW"], P["CUTOUT_CLEAR"]
    for c in conns:
        t = c.te
        c.cut = [c.X - t["w"] / 2.0 - cc, c.X + t["w"] / 2.0 + cc,
                 c.Z - t["h"] / 2.0 - cc, c.Z + t["h"] / 2.0 + cc]
        c.holes = [c.X - t["pitch"] / 2.0, c.X + t["pitch"] / 2.0]
        c.reach = [c.holes[0] - t["hole"] / 2.0, c.holes[1] + t["hole"] / 2.0, c.cut[2], c.cut[3]]
        c.plug = [c.X - t["w"] / 2.0 - gr, c.X + t["w"] / 2.0 + gr,
                  c.Z - t["h"] / 2.0 - gr, c.Z + t["h"] / 2.0 + gr]
        c.fl = [c.flange[0] + dx, c.flange[1] + dx, D.cz0 + c.flange[2], D.cz0 + c.flange[3]]
    D.holes = [(h["ref"], h["x"] + dx, h["y"] + dy) for h in board["holes"]
               if h["ref"].startswith("H")]

    # ---- the ribbon, the flex, the button's lead: straight lines
    jb = D.ref_boxes["J4"]
    D.j4_top = ((jb[0] + jb[1]) / 2.0, (jb[2] + jb[3]) / 2.0, jb[5])
    D.cn8_face = ((bt.cn8[0] + bt.cn8[1]) / 2.0, bt.cn8[3], (bt.cn8[4] + bt.cn8[5]) / 2.0)
    D.ribbon = _dist(D.cn8_face, D.j4_top)
    sb = D.ref_boxes["SW1"]
    D.sw1_top = ((sb[0] + sb[1]) / 2.0, (sb[2] + sb[3]) / 2.0, sb[5])
    D.button_back = (D.bX, D.y_button, D.bZ)
    D.button_lead = _dist(D.button_back, D.sw1_top)
    target = [it for it in plate_items if it.name == P["FLEX_TO"]][0]
    D.flex_target = target
    a = (fx, D.y_disp1, D.disp[2])
    near = (min(max(a[0], target.x0), target.x1), target.y0, min(max(a[2], target.z0), target.z1))
    D.flex_len = _dist(a, near)

    # ---- the lid's lugs and the side screws' bosses
    lr = P["LUG_D"] / 2.0
    D.lug_run = [D.y_frame + WL + lr, D.y_plate0 - P["SLOT_CLEAR"] / 2.0 - G - lr]
    inset = lr - P["LUG_EMBED"]
    D.lugs = [(x, D.lug_run[0] + f * (D.lug_run[1] - D.lug_run[0]))
              for x in (D.ix0 + inset, D.ix1 - inset) for f in P["LID_LUGS"]]
    D.side_bosses = [(side, y, z) for side in ("left", "right") for (y, z) in P["SIDE_SCREWS"]]
    D.bezel_screws = [(D.ix0 + f * (D.ix1 - D.ix0), z) for f in P["BEZEL_SCREWS_AT"]
                      for z in ((D.zb + D.zf) / 2.0, (D.z_rim + D.z_lid) / 2.0)]

    # ---- the RF window: the wall over the radio's span plus RF_KEEPOUT, as far as the inside
    xa = list(D.ref_boxes[P["RF_REF"]])
    xa[4] = max(xa[4], D.cz1)                          # the module sits on the board; its pin
    D.xiao = xa                                        # tails below are not the radio
    k = P["RF_KEEPOUT"]
    sc = P["SLOT_CLEAR"]
    ys = [max(D.y_frame + WL + 0.5, xa[2] - k), min(D.y_plate0 - sc / 2.0 - 0.5, xa[3] + k)]
    xs = [max(D.ix0 + 0.5, xa[0] - k), min(D.ix1 - 0.5, xa[1] + k)]
    zs = [max(D.zf + 0.5, xa[4] - k), min(D.z_rim - 0.5, xa[5] + k)]
    on = P["RF_WINDOW_ON"]
    w = P["RF_WALL"]
    oc = P["OVERCUT"]
    if on == "left":
        D.rf = [D.bx0, D.ix0] + ys + zs
        D.rf_path = [D.ix0, xa[0]] + ys + zs
        D.rf_pocket = [D.bx0 - oc, D.ix0 - w] + ys + zs
    elif on == "right":
        D.rf = [D.ix1, D.bx1] + ys + zs
        D.rf_path = [xa[1], D.ix1] + ys + zs
        D.rf_pocket = [D.ix1 + w, D.bx1 + oc] + ys + zs
    elif on == "floor":
        D.rf = xs + ys + [D.zb, D.zf]
        D.rf_path = xs + ys + [D.zf, xa[4]]
        D.rf_pocket = xs + ys + [D.zb - oc, D.zf - w]
    elif on == "lid":
        D.rf = xs + ys + [D.z_rim, D.z_lid]
        D.rf_path = xs + ys + [xa[5], D.z_rim]
        D.rf_pocket = xs + ys + [D.z_rim + w, D.z_lid + oc]
    else:
        D.rf = xs + [D.y_plate0, D.y_plate1] + zs
        D.rf_path = xs + [xa[3], D.y_plate0] + zs
        D.rf_pocket = xs + [D.y_plate0 + w, D.y_plate1 + oc] + zs
    D.rf_reach = _box_gap(xa, D.rf)
    return D


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
    G, WL = P["GAP"], P["WALL"]

    def bad(msg):
        problems.append(msg)

    # ---- the display, its active area and the bezel's window
    for a, b, sd in (("ACTIVE_W", "DISP_W", "ACTIVE_DX"), ("ACTIVE_H", "DISP_H", "ACTIVE_DZ")):
        if P[a] + 2 * abs(P[sd]) > P[b] + eps:
            bad("%s %s with %s %s reaches past the display's outline (%s %s): lower %s or %s."
                % (a, n(P[a]), sd, n(P[sd]), b, n(P[b]), a, sd))
    ledge = min(D.window[0] - D.disp[0], D.disp[1] - D.window[1], D.window[2] - D.disp[2],
                D.disp[3] - D.window[3])
    M["the display's active area inside the bezel window, per side"] = P["WINDOW_MARGIN"], 0.0
    M["the bezel window inside the display's outline (the ledge that holds the glass)"] = \
        ledge, P["BEZEL_LEDGE"]
    if ledge < P["BEZEL_LEDGE"] - eps:
        bad("The bezel's window (the active area + WINDOW_MARGIN %s) comes %s from the display's "
            "edge, less than BEZEL_LEDGE %s, so the bezel does not hold the glass: lower "
            "WINDOW_MARGIN to at most %s, or lower BEZEL_LEDGE, or check ACTIVE_DX / ACTIVE_DZ."
            % (n(P["WINDOW_MARGIN"]), n(ledge), n(P["BEZEL_LEDGE"]),
               n(max(0.0, P["WINDOW_MARGIN"] - (P["BEZEL_LEDGE"] - ledge)))))
    if P["FLEX_W"] > P["DISP_W"] + eps or abs(P["FLEX_X"]) + P["FLEX_W"] / 2.0 > \
            P["DISP_W"] / 2.0 + eps:
        bad("The flex (FLEX_X %s, FLEX_W %s) runs past the display's bottom edge: move FLEX_X "
            "toward 0 or narrow FLEX_W." % (n(P["FLEX_X"]), n(P["FLEX_W"])))

    # ---- the page button: clear of the display, inside the face and the body
    if D.button:
        r = max(P["BUTTON_HEAD_D"], P["BUTTON_BODY_D"]) / 2.0
        gx = max(D.disp[0] - D.bX, D.bX - D.disp[1], 0.0)
        gz = max(D.disp[2] - D.bZ, D.bZ - D.disp[3], 0.0)
        if gx > 0 or gz > 0:
            gap = math.hypot(gx, gz) - r
        else:
            gap = -min(D.bX - D.disp[0], D.disp[1] - D.bX, D.bZ - D.disp[2], D.disp[3] - D.bZ) - r
        M["the page button to the display's outline"] = gap, P["BUTTON_GAP"]
        if gap < P["BUTTON_GAP"] - eps:
            need_x = P["DISP_W"] / 2.0 + P["BUTTON_GAP"] + r
            need_z = P["DISP_H"] / 2.0 + P["BUTTON_GAP"] + r
            bad("The page button at BUTTON_X %s, BUTTON_Z %s (from the display's centre) is %s the "
                "display: its head or body (%s across) must stay BUTTON_GAP %s off the display's "
                "outline. Move it off the display - BUTTON_X beyond %s (right) or -%s (left), or "
                "BUTTON_Z beyond %s (above) or -%s (below) - or set BUTTON_X to None (just beside "
                "the display, on the carrier's side)."
                % (n(D.button_rel[0]), n(D.button_rel[1]),
                   "over" if gap < -2 * r + eps or (gx == 0 and gz == 0) else "%s mm from" % n(gap),
                   n(2 * r), n(P["BUTTON_GAP"]), n(need_x), n(need_x), n(need_z), n(need_z)))
        if P["BUTTON_HOLE_D"] > P["BUTTON_HEAD_D"] - eps:
            bad("BUTTON_HOLE_D %s is not less than BUTTON_HEAD_D %s: the head would fall through the "
                "bezel - raise BUTTON_HEAD_D." % (n(P["BUTTON_HOLE_D"]), n(P["BUTTON_HEAD_D"])))

    # ---- the carrier inside the walls; what stands on the display plate
    m = min(D.kx0 - D.ix0, D.ix1 - D.kx1)
    M["carrier in the body, per side"] = m, P["GAP"]
    if m < G - eps:
        bad("CARRIER_X %r puts the carrier %s from a side wall (its XIAO overhangs the board's "
            "left edge by %s): keep CARRIER_X at least %s (or use 'left' / 'centre' / 'right')."
            % (P["CARRIER_X"], n(m), n(D.overhang_left), n(D.overhang_left + G)))
    for it in D.plate_items:
        if it.x0 < D.ix0 + G - eps or it.x1 > D.ix1 - G + eps:
            bad("The %s (X %s to %s) does not stand between the side walls with GAP (X %s to %s): "
                "move it in (%s), or narrow it." % (
                    it.label, n(it.x0), n(it.x1), n(D.ix0 + G), n(D.ix1 - G),
                    "BT_X" if it.name == "BT817" else "DRIVER_BOARDS '%s' x0" % it.name))
        if P["CARRIER_LAYOUT"] == "below" and it.over_carrier and it.z0 < D.ktop + G - eps:
            bad("%s puts the %s (bottom at Z %s) into the room kept above the carrier (up to Z %s), "
                "which it stands over with the carrier below: raise it to at least %s above the "
                "floor, or set it to None (as low as it goes), or set CARRIER_LAYOUT 'behind'."
                % (it.param, it.label, n(it.z0), n(D.ktop), n(D.ktop_f + G)))
    for i, a in enumerate(D.plate_items):
        for b in D.plate_items[i + 1:]:
            if _overlap(a.x0, a.x1, b.x0 - G, b.x1 + G) and _overlap(a.z0, a.z1, b.z0 - G, b.z1 + G):
                bad("The %s and the %s overlap on the display plate, GAP %s included (X %s-%s / "
                    "%s-%s, Z %s-%s / %s-%s): move one of them (BT_X, BT_Z, or the DRIVER_BOARDS "
                    "x0 / z0)." % (a.label, b.label, n(G), n(a.x0), n(a.x1), n(b.x0), n(b.x1), n(a.z0), n(a.z1),
                       n(b.z0), n(b.z1)))
    if D.button and D.y_button > D.y_bulk1 + eps:      # the button's body reaches past the plate
        rb = P["BUTTON_BODY_D"] / 2.0
        for it in D.plate_items:
            if _overlap(D.bX - rb, D.bX + rb, it.x0 - G, it.x1 + G) and \
                    _overlap(D.bZ - rb, D.bZ + rb, it.z0 - G, it.z1 + G):
                bad("The page button's body (X %s-%s, Z %s-%s, back to Y %s) runs into the %s on "
                    "the display plate (X %s-%s, Z %s-%s), GAP %s included: move the button "
                    "(BUTTON_X / BUTTON_Z, from the display's centre) or the %s (%s)."
                    % (n(D.bX - rb), n(D.bX + rb), n(D.bZ - rb), n(D.bZ + rb), n(D.y_button),
                       it.label, n(it.x0), n(it.x1), n(it.z0), n(it.z1), n(G), it.label,
                       "BT_X / BT_Z" if it.name == "BT817" else
                       "its DRIVER_BOARDS x0 / z0"))
    bt = D.bt
    if not (bt.x0 <= bt.cn8[0] + eps and bt.cn8[1] <= bt.x1 + eps and bt.z0 <= bt.cn8[4] + eps
            and bt.cn8[5] <= bt.z1 + eps):
        bad("BT_CN8 %r puts CN8 off the BT817 board (%s x %s): keep it within %s across and "
            "between %s and %s up." % (P["BT_CN8"], n(P["BT_W"]), n(P["BT_H"]),
                                       n((P["BT_W"] - P["CN8_W"]) / 2.0), n(P["CN8_H"] / 2.0),
                                       n(P["BT_H"] - P["CN8_H"] / 2.0)))
    if P["BT_STANDOFF"] < P["BT_UNDER_H"] - eps:
        bad("BT_STANDOFF %s is less than BT_UNDER_H %s: the BT817 board's front parts would sit "
            "on the display plate. Raise BT_STANDOFF to at least %s."
            % (n(P["BT_STANDOFF"]), n(P["BT_UNDER_H"]), n(P["BT_UNDER_H"])))
    if P["BT_HOLE_INSET"] < P["BT_STANDOFF_D"] / 2.0 - eps:
        bad("BT_HOLE_INSET %s puts the standoffs (BT_STANDOFF_D %s) past the BT817 board's edge: "
            "raise BT_HOLE_INSET to at least %s."
            % (n(P["BT_HOLE_INSET"]), n(P["BT_STANDOFF_D"]), n(P["BT_STANDOFF_D"] / 2.0)))

    # ---- inserts, pilots and thin places
    deep = P["INSERT_DEPTH"] + P["INSERT_SKIN"]
    for label, have, what in (
            ("BOSS_H + FLOOR", P["BOSS_H"] + P["FLOOR"], "raise BOSS_H or FLOOR"),
            ("LUG_H", P["LUG_H"], "raise LUG_H"),
            ("WALL + SIDE_BOSS_L", WL + P["SIDE_BOSS_L"], "raise SIDE_BOSS_L"),
            ("BT_STANDOFF + BULKHEAD", P["BT_STANDOFF"] + P["BULKHEAD"],
             "raise BT_STANDOFF or BULKHEAD")):
        if have < deep - eps:
            bad("%s is %s, less than an insert's bore and the skin beyond it (INSERT_DEPTH %s + "
                "INSERT_SKIN %s): %s by %s."
                % (label, n(have), n(P["INSERT_DEPTH"]), n(P["INSERT_SKIN"]), what,
                   n(deep - have)))
    wide = P["INSERT_BORE"] + 2 * P["INSERT_SKIN"]
    for name in ("BOSS_D", "LUG_D", "SIDE_BOSS_D", "BT_STANDOFF_D"):
        if P[name] < wide - eps:
            bad("%s %s leaves less than INSERT_SKIN %s round an INSERT_BORE %s: raise %s to at "
                "least %s." % (name, n(P[name]), n(P["INSERT_SKIN"]), n(P["INSERT_BORE"]), name,
                               n(wide)))
    band = min(P["FLOOR"], P["LID"])
    if P["BEZEL_PILOT"] + 2 * P["BEZEL_SKIN"] > band + eps:
        bad("BEZEL_PILOT %s with BEZEL_SKIN %s each side needs %s of the front frame's top and "
            "bottom bands, which are FLOOR / LID %s thick: lower BEZEL_PILOT or raise FLOOR and "
            "LID." % (n(P["BEZEL_PILOT"]), n(P["BEZEL_SKIN"]),
                      n(P["BEZEL_PILOT"] + 2 * P["BEZEL_SKIN"]), n(band)))
    if P["BEZEL_SCREW_CLEAR"] <= P["BEZEL_PILOT"] + eps:
        bad("BEZEL_SCREW_CLEAR %s is not more than BEZEL_PILOT %s: the bezel's hole must clear "
            "the screw - raise BEZEL_SCREW_CLEAR." % (n(P["BEZEL_SCREW_CLEAR"]), n(P["BEZEL_PILOT"])))
    ring = D.y_bulk1 - D.y_face
    if P["BEZEL_PILOT_DEPTH"] > ring - P["INSERT_SKIN"] + eps:
        bad("BEZEL_PILOT_DEPTH %s is deeper than the front frame (%s) less INSERT_SKIN: lower it "
            "to at most %s." % (n(P["BEZEL_PILOT_DEPTH"]), n(ring), n(ring - P["INSERT_SKIN"])))
    if P["PLATE"] > L.TE_PANEL_MAX + eps:
        bad("PLATE %s is thicker than TE allows for a DT13's panel (%s, 114-151046 3.11): lower "
            "PLATE." % (n(P["PLATE"]), n(L.TE_PANEL_MAX)))
    rf_wall = {"left": "WALL", "right": "WALL", "floor": "FLOOR", "lid": "LID",
               "rear": "PLATE"}[P["RF_WINDOW_ON"]]
    for a, b, what in (("SLOT_DEPTH", "WALL", "the plate's channel cuts through the side wall"),
                       ("LUG_EMBED", "WALL", "the lid lugs break out of the side wall"),
                       ("FLOOR_GROOVE", "FLOOR", "the plate's channel cuts through the floor"),
                       ("GASKET_GROOVE_W", "WALL", "the gasket groove is wider than the wall"),
                       ("GASKET_GROOVE_W", "PLATE", "the gasket groove is wider than the plate"),
                       ("GASKET_GROOVE_D", "LID", "the gasket groove cuts through the lid"),
                       ("RF_WALL", rf_wall, "the RF window is no thinner than its wall")):
        if P[a] >= P[b] - eps:
            bad("%s %s is not less than %s %s (%s): lower %s or raise %s."
                % (a, n(P[a]), b, n(P[b]), what, a, b))
    if P["BOSS_H"] < P["CARRIER_BOT_H"] - eps:
        bad("BOSS_H %s is less than CARRIER_BOT_H %s, so the floor is inside the room kept under "
            "the carrier: raise BOSS_H to at least %s."
            % (n(P["BOSS_H"]), n(P["CARRIER_BOT_H"]), n(P["CARRIER_BOT_H"])))

    # ---- every cut-out inside the plate, with plastic round it; plugs side by side
    pe = P["PLATE_EDGE"]
    m_plate, m_side = [], []
    for c in D.conns:
        mm = {"left": c.reach[0] - D.ix0, "right": D.ix1 - c.reach[1],
              "bottom": c.reach[2] - D.zf, "top": D.z_rim - c.reach[3]}
        m_plate.append(min(mm.values()))
        for side, v in mm.items():
            if v < pe - eps:
                fix = {"left": "move the carrier right (CARRIER_X)",
                       "right": "move the carrier left (CARRIER_X)",
                       "bottom": "raise BOSS_H", "top": "raise TOP_GAP"}[side]
                bad("The cut-out for %s comes %s from the rear plate's %s edge, less than "
                    "PLATE_EDGE %s: %s by %s." % (c.name, n(v), side, n(pe), fix, n(pe - v)))
    seq = sorted(D.conns, key=lambda c: c.X)
    for a, b in zip(seq, seq[1:]):
        m_plate.append(b.reach[0] - a.reach[1])
        m_side.append(b.plug[0] - a.plug[1])
        if b.reach[0] - a.reach[1] < pe - eps:
            bad("%s and %s stand %s apart on the rear plate, less than PLATE_EDGE %s: that is "
                "the carrier's drawing (F11 moves them)." % (a.name, b.name,
                                                             n(b.reach[0] - a.reach[1]), n(pe)))
        elif b.plug[0] - a.plug[1] < P["PLUG_SIDE_CLEAR"] - eps:
            bad("The mated plugs of %s and %s are %s apart, less than PLUG_SIDE_CLEAR %s: lower "
                "PLUG_GROW." % (a.name, b.name, n(b.plug[0] - a.plug[1]), n(P["PLUG_SIDE_CLEAR"])))
    M["cut-outs and screw holes to the plate's edge and each other"] = min(m_plate), pe
    if m_side:
        M["plug to plug, side by side"] = min(m_side), P["PLUG_SIDE_CLEAR"]

    # ---- lugs, side screws, the RF window's span
    if D.lug_run[1] < D.lug_run[0] - eps:
        bad("There is no room for a lid lug between the lid's front beam and the rear plate: "
            "lower LUG_D.")
    r = P["SIDE_BOSS_D"] / 2.0
    for k, (y, z) in enumerate(P["SIDE_SCREWS"]):
        y_lo, y_hi = D.y_frame + r, D.y_plate0 - P["SLOT_CLEAR"] / 2.0 - r
        z_lo, z_hi = D.zf + r, D.z_rim - r
        if not (y_lo - eps <= y <= y_hi + eps):
            bad("SIDE_SCREWS %d at Y %s is off the side wall: keep Y between %s and %s."
                % (k + 1, n(y), n(y_lo), n(y_hi)))
        elif not (z_lo - eps <= z <= z_hi + eps):
            bad("SIDE_SCREWS %d at Z %s is off the side wall: keep Z between %s and %s."
                % (k + 1, n(z), n(z_lo), n(z_hi)))
    w = D.rf
    if w[1] - w[0] <= eps or w[3] - w[2] <= eps or w[5] - w[4] <= eps:
        bad("RF_WINDOW_ON %r leaves no window: the radio's span plus RF_KEEPOUT does not reach "
            "that wall's inside. Choose another wall." % P["RF_WINDOW_ON"])

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

        fits = D.body_w <= ow + eps and D.body_h <= oh + eps
        rule(fits, "body through the aperture",
             "The body is %s x %s and the aperture %s x %s: %s."
             % (n(D.body_w), n(D.body_h), n(ow), n(oh), "it goes in from the front" if fits else
                "it does not go in - a smaller display (DISP_W / DISP_H), a thinner WALL, or the "
                "page button inside the display's width; or D-270's separate box (the fallback)"))
        cov = D.face_w >= ow - eps and D.face_h >= oh - eps
        rule(cov, "face covers the aperture",
             "The face is %s x %s and the aperture %s x %s: %s."
             % (n(D.face_w), n(D.face_h), n(ow), n(oh), "it covers it" if cov else
                "raise FACE_W / FACE_H (or BEZEL_BORDER) to at least the aperture"))
        deep = D.y_plugs - D.y_face
        rule(deep <= env["DEPTH"] + eps, "depth with plugs",
             "Behind the face the unit needs %s with its plugs and the binnacle has %s: %s."
             % (n(deep), n(env["DEPTH"]), "it goes in" if deep <= env["DEPTH"] + eps else
                "shorten it by %s - CARRIER_LAYOUT 'below' saves the depth of what stands on the "
                "display plate; PLUG_L and CABLE_BEND are guesses; or D-270's separate box (the "
                "fallback)" % n(deep - env["DEPTH"])))
    return problems, D, M


# ------------------------------------------------------------------------------------ insides --
def _item(name, shape, kind="part", **kw):
    d = {"name": name, "shape": shape, "kind": kind, "group": name, "dt13": False}
    d.update(kw)
    return d


def _bx(b):
    return L.box(b[0], b[1], b[2], b[3], b[4], b[5])


def _standin_dt13(P, D, c):
    """A DT13 as three blocks from probe.json: the body on the board (as wide and as tall as the
    model's whole extent - generous) up to the flange's front face, the flange, and the nose with
    TE's corner radius through the plate."""
    b = c.box
    body = L.box(b[0], b[1], b[2], c.yf, D.cz1, b[5])
    flange = L.box(c.fl[0], c.fl[1], c.yf - P["DT13_FLANGE_T"], c.yf, c.fl[2], c.fl[3])
    h = c.housing
    nose = L.rrect_xz(h[1] - h[0], h[3] - h[2], c.te["r"], c.X, c.Z, c.yf, c.tip)
    return L.fuse([body, flange, nose])


def build_insides(P, D, src, standin=False):
    """Everything inside the case and on its face, as named solids. `kind` is `part`, `carrier`
    (the board's own solids) or `keepout` (room kept clear, not a thing)."""
    oc = P["OVERCUT"]
    out = []

    # ---- the bezel plate (P121): the window, the button's hole, the screws' holes
    face = L.box(0.0, D.face_w, 0.0, D.y_face, 0.0, D.face_h)
    w = D.window
    holes = [L.box(w[0], w[1], -oc, D.y_face + oc, w[2], w[3])]
    if D.button:
        holes.append(L.cyl_y(P["BUTTON_HOLE_D"] / 2.0, D.bX, D.bZ, -oc, D.y_face + oc))
    holes += [L.cyl_y(P["BEZEL_SCREW_CLEAR"] / 2.0, x, z, -oc, D.y_face + oc)
              for (x, z) in D.bezel_screws]
    out.append(_item("bezel plate (P121)", L.cut(face, holes)))

    # ---- the display (P118), its flex's room, the page button (P120)
    d = D.disp
    out.append(_item("display module (P118, placeholder)",
                     L.box(d[0], d[1], D.y_disp0, D.y_disp1, d[2], d[3])))
    out.append(_item("keep-out: the display's flex", _bx(D.flex), "keepout"))
    if D.button:
        btn = L.fuse([L.cyl_y(P["BUTTON_HEAD_D"] / 2.0, D.bX, D.bZ, -P["BUTTON_PROUD"], 0.0),
                      L.cyl_y(P["BUTTON_HOLE_D"] / 2.0 - 0.1, D.bX, D.bZ, 0.0, D.y_face),
                      L.cyl_y(P["BUTTON_BODY_D"] / 2.0, D.bX, D.bZ, D.y_face, D.y_button)])
        out.append(_item("page button (P120, placeholder)", btn))

    # ---- the BT817 board (P117) and the driver boards, on the display plate
    bt = D.bt
    slab = L.box(bt.x0, bt.x1, bt.yb0, bt.yb1, bt.z0, bt.z1)
    slab = L.cut(slab, [L.cyl_y(P["SCREW_CLEAR"] / 2.0, x, z, bt.yb0 - oc, bt.yb1 + oc)
                        for (x, z) in bt.holes])
    out.append(_item("BT817 board (P117, placeholder)", slab))
    parts = L.fuse([L.box(bt.x0, bt.x1, bt.yb1, bt.yb1 + P["BT_PARTS_H"], bt.z0, bt.z1),
                    _bx(bt.cn8)])
    out.append(_item("BT817 parts and CN8 (placeholder)", parts))
    out.append(_item("keep-out: mated ribbon plug on CN8", _bx(bt.cn8_plug), "keepout"))
    for it in D.drivers:
        out.append(_item("%s (%s, placeholder)" % (it.name, it.what.split(" (")[-1].rstrip(")")),
                         L.box(it.x0, it.x1, it.y0, it.y1, it.z0, it.z1)))

    # ---- the carrier: the board's STEP when it is there, stand-in blocks otherwise
    real = bool(src["step"]) and bool(P["CARRIER_STEP"]) and not standin
    if not standin:
        D.carrier_real = real
    dt = {c.ref: c for c in D.conns}
    if real:
        mv = V(D.dx, D.dy, D.cz0)
        for ref, s in src["step"]:
            t = s.translated(mv)
            if ref in dt:
                out.append(_item("%s %s (%s)" % (ref, dt[ref].name, dt[ref].part), t, "carrier",
                                 ref=ref, dt13=True))
            else:
                out.append(_item("carrier: " + ref, t, "carrier", ref=ref,
                                 group="carrier board" if ref == "board" else "carrier parts"))
    else:
        out.append(_item("carrier board (stand-in)",
                         L.box(D.cx0, D.cx1, D.cy0, D.cy1, D.cz0, D.cz1), "carrier", ref="board"))
        for c in D.conns:
            out.append(_item("%s %s (%s, stand-in)" % (c.ref, c.name, c.part),
                             _standin_dt13(P, D, c), "carrier", ref=c.ref, dt13=True))
        for ref, b in sorted(D.ref_boxes.items()):
            if ref in dt:
                continue
            out.append(_item("carrier: %s (stand-in)" % ref, _bx(b), "carrier", ref=ref,
                             group="carrier parts"))
    out.append(_item("keep-out: above the carrier",
                     L.box(D.cx0, D.cx1, D.cy0, D.cy1, D.cz1, D.ktop), "keepout"))
    if P["CARRIER_BOT_H"] > 0:
        under = L.box(D.cx0, D.cx1, D.cy0, D.cy1, D.cz0 - P["CARRIER_BOT_H"], D.cz0)
        r = P["BOSS_D"] / 2.0                          # the bosses stand in this room: square
        under = L.cut(under, [L.box(x - r, x + r, y - r, y + r,    # notches, no slivers
                                    D.cz0 - P["CARRIER_BOT_H"] - oc, D.cz0 + oc)
                              for (_, x, y) in D.holes])
        out.append(_item("keep-out: below the carrier", under, "keepout"))

    # ---- the mated plugs: room, not parts
    for c in D.conns:
        out.append(_item("keep-out: mated plug on %s" % c.name,
                         L.box(c.plug[0], c.plug[1], D.y_plate1, D.y_plugs, c.plug[2], c.plug[3]),
                         "keepout"))
    return out


# --------------------------------------------------------------------------------------- case --
def build_case(P, D):
    """The four printed parts: body, rear plate, lid, front frame. Also returns, per part, its
    named features (label, box, the parameters that move it) so an interference can say where."""
    oc = P["OVERCUT"]
    WL, PT = P["WALL"], P["PLATE"]
    bx0, bx1, ix0, ix1 = D.bx0, D.bx1, D.ix0, D.ix1
    zb, zf, z_rim = D.zb, D.zf, D.z_rim
    G = P["GAP"]
    feats = {"body": [], "rear_plate": [], "lid": [], "front_frame": []}
    pocket = D.rf_pocket
    on = P["RF_WINDOW_ON"]

    # ---- body: floor, side walls, the beam under the lid's front edge, open front and rear
    shell = L.box(bx0, bx1, D.y_frame, D.y_end, zb, z_rim)
    z_beam = z_rim - P["RIM_H"]
    inner = [L.box(ix0, ix1, D.y_frame - oc, D.y_frame + WL, zf, z_beam),
             L.box(ix0, ix1, D.y_frame + WL, D.y_end + oc, zf, z_rim + oc)]
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
    cuts = [channel] + bores
    if on in ("left", "right", "floor"):
        cuts.append(_bx(pocket))
    body = L.cut(L.fuse([shell] + adds), cuts)
    fb += [("the beam under the lid's front edge", [ix0, ix1, D.y_frame, D.y_frame + WL, z_beam,
                                                    z_rim], "RIM_H, or what stands on the "
                                                            "display plate (BT_Z, DRIVER_BOARDS)"),
           ("floor", [bx0, bx1, D.y_frame, D.y_end, zb, zf], "BOSS_H, FLOOR"),
           ("left wall", [bx0, ix0, D.y_frame, D.y_end, zb, z_rim], "FACE_W, WALL, GAP"),
           ("right wall", [ix1, bx1, D.y_frame, D.y_end, zb, z_rim], "FACE_W, WALL, GAP")]

    # ---- rear plate: both DT13s through TE's cut-out
    plate = L.box(ix0 - sd + sc / 2.0, ix1 + sd - sc / 2.0, D.y_plate0, D.y_plate1,
                  zf - P["FLOOR_GROOVE"] + sc / 2.0, z_rim)
    cuts = []
    for c in D.conns:
        t = c.te
        w, h = c.cut[1] - c.cut[0], c.cut[3] - c.cut[2]
        cuts.append(L.rrect_xz(w, h, t["r"], c.X, c.Z, D.y_plate0 - oc, D.y_plate1 + oc))
        cuts += [L.cyl_y(t["hole"] / 2.0, x, c.Z, D.y_plate0 - oc, D.y_plate1 + oc)
                 for x in c.holes]
        feats["rear_plate"].append(("the plate round %s's cut-out" % c.name,
                                    [c.fl[0], c.fl[1], D.y_plate0, D.y_plate1, c.fl[2], c.fl[3]],
                                    "CUTOUT_CLEAR, or the carrier"))
    if on == "rear":
        cuts.append(_bx(pocket))
    plate = L.cut(plate, cuts)

    # ---- lid: flat, from the front frame to the rear lip; the gasket groove over the walls'
    #      centre lines, the beam and the plate
    lid = L.box(bx0, bx1, D.y_frame, D.y_end, z_rim, D.z_lid)
    gw, gd = P["GASKET_GROOVE_W"], P["GASKET_GROOVE_D"]
    mx0, mx1 = bx0 + WL / 2.0, bx1 - WL / 2.0
    my0, my1 = D.y_frame + WL / 2.0, D.y_plate0 + PT / 2.0
    outer = L.rrect_prism(mx1 - mx0 + gw, my1 - my0 + gw, P["GASKET_R"] + gw / 2.0,
                          (mx0 + mx1) / 2.0, (my0 + my1) / 2.0, z_rim - oc, z_rim + gd)
    inner_ = L.rrect_prism(mx1 - mx0 - gw, my1 - my0 - gw, max(gw / 2.0, P["GASKET_R"] - gw / 2.0),
                           (mx0 + mx1) / 2.0, (my0 + my1) / 2.0, z_rim - 2 * oc, z_rim + gd + oc)
    cuts = [outer.cut(inner_)] + [L.cyl(P["SCREW_CLEAR"] / 2.0, x, y, z_rim - oc, D.z_lid + oc)
                                  for (x, y) in D.lugs]
    if on == "lid":
        cuts.append(_bx(pocket))
    lid = L.cut(lid, cuts)
    feats["lid"].append(("lid", [bx0, bx1, D.y_frame, D.y_end, z_rim, D.z_lid], "TOP_GAP"))

    # ---- front frame: the ring round the display, the display plate behind it (the flex's slot,
    #      the button's hole), the BT817 board's standoffs, the bezel's screw pilots
    ring = L.box(bx0, bx1, D.y_face, D.y_frame, zb, D.z_lid).cut(
        L.box(ix0, ix1, D.y_face - oc, D.y_frame + oc, zf, z_rim))
    plate_ = L.box(ix0, ix1, D.y_bulk0, D.y_bulk1, zf, z_rim)
    s = P["FLEX_SLOT_CLEAR"]
    f = D.flex
    plate_ = L.cut(plate_, [
        L.box(f[0] - s, f[1] + s, D.y_bulk0 - oc, D.y_bulk1 + oc, f[4] - s, f[5] + s)] + ([
        L.cyl_y(P["BUTTON_BODY_D"] / 2.0 + P["BUTTON_HOLE_CLEAR"], D.bX, D.bZ, D.y_bulk0 - oc,
                D.y_bulk1 + oc)] if D.button else []))
    adds, bores = [ring, plate_], []
    bt = D.bt
    rr = P["BT_STANDOFF_D"] / 2.0
    for k, (x, z) in enumerate(bt.holes):
        adds.append(L.cyl_y(rr, x, z, D.y_bulk1 - 0.01, bt.yb0))
        bores.append(L.cyl_y(P["INSERT_BORE"] / 2.0, x, z, bt.yb0 - P["INSERT_DEPTH"], bt.yb0 + oc))
        feats["front_frame"].append(("BT817 standoff %d" % (k + 1),
                                     [x - rr, x + rr, D.y_bulk1, bt.yb0, z - rr, z + rr],
                                     "BT_HOLE_INSET, BT_STANDOFF, BT_X, BT_Z"))
    pr = P["BEZEL_PILOT"] / 2.0
    bores += [L.cyl_y(pr, x, z, D.y_face - oc, D.y_face + P["BEZEL_PILOT_DEPTH"])
              for (x, z) in D.bezel_screws]
    frame = L.cut(L.fuse(adds), bores)
    feats["front_frame"] += [
        ("the display plate", [ix0, ix1, D.y_bulk0, D.y_bulk1, zf, z_rim],
         "DISP_BACK_CLEAR, BULKHEAD, FLEX_SLOT_CLEAR, BUTTON_HOLE_CLEAR"),
        ("frame ring", [bx0, bx1, D.y_face, D.y_frame, zb, D.z_lid],
         "DISP_CLEAR, WALL, FLOOR, LID, or the page button")]
    return {"body": body, "rear_plate": plate, "lid": lid, "front_frame": frame}, feats


def metal(P, D):
    """Every piece of metal the case puts near the radio, as (name, box): inserts, screws, the
    DT13s' contacts."""
    out = []
    ib, idp = P["INSERT_BORE"] / 2.0, P["INSERT_DEPTH"]
    for (ref, x, y) in D.holes:
        out.append(("carrier insert " + ref, [x - ib, x + ib, y - ib, y + ib, D.cz0 - idp, D.cz0]))
    for k, (x, y) in enumerate(D.lugs):
        out.append(("lid insert %d" % (k + 1), [x - ib, x + ib, y - ib, y + ib, D.z_rim - idp,
                                                D.z_lid]))
    for (side, y, z) in D.side_bosses:
        x0, x1 = (D.bx0, D.bx0 + idp) if side == "left" else (D.bx1 - idp, D.bx1)
        out.append(("side screw insert, %s wall, (Y %s, Z %s)" % (side, n(y), n(z)),
                    [x0, x1, y - ib, y + ib, z - ib, z + ib]))
    bt = D.bt
    for k, (x, z) in enumerate(bt.holes):
        out.append(("BT817 standoff insert %d" % (k + 1), [x - ib, x + ib, bt.yb0 - idp, bt.yb1,
                                                         z - ib, z + ib]))
    r = P["BEZEL_SCREW_CLEAR"] / 2.0
    for k, (x, z) in enumerate(D.bezel_screws):
        out.append(("bezel screw %d" % (k + 1), [x - r, x + r, 0.0, D.y_face +
                                                P["BEZEL_PILOT_DEPTH"], z - r, z + r]))
    if D.button:
        out.append(("the page button", [D.bX - P["BUTTON_BODY_D"] / 2.0,
                                        D.bX + P["BUTTON_BODY_D"] / 2.0, 0.0, D.y_button,
                                        D.bZ - P["BUTTON_BODY_D"] / 2.0,
                                        D.bZ + P["BUTTON_BODY_D"] / 2.0]))
    for c in D.conns:
        out.append(("%s's contacts" % c.name, [c.box[0], c.box[1], c.box[2], c.tip, c.box[4],
                                              c.box[5]]))
    return out


# ------------------------------------------------------------------------------------- checks --
def _common(P, a, b):
    """(volume, thinnest extent, box, pieces) of what two shapes share, or None."""
    if not a.BoundBox.intersect(b.BoundBox):
        return None
    com = a.common(b)
    if com.isNull() or com.Volume <= P["VOLUME_EPS"]:
        return None
    cb = com.optimalBoundingBox()
    pieces = []
    for s in (com.Solids if len(com.Solids) > 1 else []):
        bb = s.BoundBox
        pieces.append([bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax])
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
    mine = [it for it in insides if it["kind"] != "carrier"]
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

    # ---- the RF window: no copper between the radio and it, no metal near it
    path = _bx(D.rf_path) if min(D.rf_path[1] - D.rf_path[0], D.rf_path[3] - D.rf_path[2],
                                 D.rf_path[5] - D.rf_path[4]) > P["EPS"] else None
    inway = []
    if path is not None:
        for it in real:
            if it.get("ref") == P["RF_REF"]:
                continue
            c = _common(P, path, it["shape"])
            if c and c[1] >= L.CONTACT and it["name"] not in inway:
                inway.append(it["name"])
    add("RF window (%s): nothing between the radio and it" % P["RF_WINDOW_ON"], not inway,
        "clear - %s from the radio's %s to the window" % (n(D.rf_reach), P["RF_REF"])
        if not inway else "in the way: " + ", ".join(inway) + " - choose another RF_WINDOW_ON, "
        "or move the carrier (CARRIER_X)")
    near = sorted((_box_gap(b, D.rf), name) for name, b in metal(P, D))
    D.rf_metal = near[0] if near else None
    close = [(d, name) for (d, name) in near if d < P["RF_KEEPOUT"] - P["EPS"]]
    add("RF window: no metal within RF_KEEPOUT %s" % n(P["RF_KEEPOUT"]), not close,
        ("nearest is %s, %s away" % (near[0][1], n(near[0][0]))) if not close else
        "too near: " + "; ".join("%s at %s" % (name, n(d)) for d, name in close) +
        " - move them (SIDE_SCREWS, LID_LUGS, BEZEL_SCREWS_AT) or the window")

    # ---- can it go in from the front
    add("front install", True, front_install(P, D).split(": ", 1)[1])

    # ---- the envelope
    if D.env is None:
        add("envelope (C4 depth, M-1 aperture)", None,
            "not measured - ENVELOPE is None, nothing checked (confirm)")
    else:
        for name, ok, msg in D.env:
            add("envelope: " + name, ok, msg)
    return checks


def front_install(P, D):
    """The one line that says whether it goes into the binnacle from the front, like a head
    unit: always one height, so yes against an aperture its own size; against a measured
    ENVELOPE, yes or no."""
    base = ("one height front to back, %s x %s; it passes an aperture that size and the %s x %s "
            "face covers it by BEZEL_OVERLAP %s a side" % (n(D.body_w), n(D.body_h), n(D.face_w),
                                                          n(D.face_h), n(P["BEZEL_OVERLAP"])))
    if D.get("env"):
        ok = all(e[1] for e in D.env)
        return "front install: %s - %s%s" % ("yes" if ok else "no", base,
                                             "" if ok else "; the measured aperture refuses it")
    return "front install: yes - " + base


# ------------------------------------------------------------------------------------ one run --
def numbers(P, D):
    """The derived dimensions the report lists."""
    rf = D.rf
    out = {
        "face_w": D.face_w, "face_h": D.face_h,
        "face_w_is": "typed" if D.face_w_typed else "derived",
        "face_h_is": "typed" if D.face_h_typed else "derived",
        "face_borders_round_the_display": D.borders,
        "width_set_by": D.width_set_by, "height_set_by": D.height_set_by,
        "body_w": D.body_w, "body_h": D.body_h,
        "front_install_line": front_install(P, D),
        "box_depth": D.y_end, "depth_to_plate_outer_face": D.y_plate1,
        "depth_to_receptacle_tips": D.y_tip, "depth_with_plugs": D.y_plugs,
        "depth_behind_the_face_with_plugs": D.y_plugs - D.y_face,
        "display_plate_back_face_y": D.y_bulk1,
        "carrier_layout": P["CARRIER_LAYOUT"],
        "carrier_front_edge_y": D.cy0, "carrier_underside_z": D.cz0,
        "carrier_left_edge_x": D.cx0,
        "carrier": "the board's STEP" if D.get("carrier_real") else "stand-in blocks",
        "bt817_board": {"x": [D.bt.x0, D.bt.x1], "z": [D.bt.z0, D.bt.z1],
                        "y_front_face": D.bt.yb0},
        "driver_boards": [{"name": it.name, "x": [it.x0, it.x1], "z": [it.z0, it.z1],
                           "y": [it.y0, it.y1]} for it in D.drivers],
        "display": {"x": D.disp[:2], "z": D.disp[2:], "y": [D.y_disp0, D.y_disp1]},
        "bezel_window": D.window, "active_area": D.active,
        "page_button": {"x": D.bX, "z": D.bZ, "from_display_centre": list(D.button_rel)},
        "flex_straight_line_at_least": D.flex_len, "flex_to": P["FLEX_TO"],
        "ribbon_straight_line": D.ribbon,
        "button_lead_straight_line": D.button_lead,
        "rf_window": {"on": P["RF_WINDOW_ON"], "x": rf[:2], "y": rf[2:4], "z": rf[4:],
                      "radio_to_window": D.rf_reach,
                      "nearest_metal": list(D.rf_metal) if D.get("rf_metal") else None},
        "cutouts": [{"name": c.name, "ref": c.ref, "part": c.part, "x": c.X, "z": c.Z,
                     "w": c.te["w"], "h": c.te["h"], "r": c.te["r"],
                     "screw_pitch": c.te["pitch"], "screw_hole": c.te["hole"],
                     "te_page": c.te["page"]} for c in D.conns],
    }

    def tidy(v):
        if isinstance(v, float):
            return round(v, 3)
        if isinstance(v, (list, tuple)):
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
    """icu-unit.FCStd (groups Insides > Keepouts, Case), one STEP per case part, and the
    assembly STEP (parts only: the kept-clear rooms are in the FCStd, not the STEP)."""
    files = []
    doc = FreeCAD.newDocument("icu_unit")
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
        path = os.path.join(outdir, "%s-%s.step" % (NAME, name))
        s.exportStep(path)
        files.append(path)
    doc.recompute()
    path = os.path.join(outdir, "%s.FCStd" % NAME)
    if os.path.exists(path):
        os.remove(path)                                # or FreeCAD keeps a .FCBak of every build
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
    display's active area in orange. Drawn from stand-in blocks for the carrier: TE's connector
    models make the projection fail."""
    import TechDraw
    Mx = FreeCAD.Matrix
    looks = {   # the unit's (X, Y, Z) -> the picture's (right, up, toward the eye)
        "front": Mx(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1),
        "back": Mx(-1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1),
        "side": Mx(0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1),
        "top": Mx(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1),
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
               "<title>ICU unit mock-up - %s</title>" % view,
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
            x0, x1, z0, z1 = D.active
            svg.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" '
                       'stroke="#d9730d" stroke-width="%.2f" stroke-dasharray="%.2f %.2f"/>'
                       % (x0, flip - z1, x1 - x0, z1 - z0, sw, 8 * sw, 4 * sw))
            extra = "; orange = the display's active area (%s x %s)" % (
                n(P["ACTIVE_W"]), n(P["ACTIVE_H"]))
        for k, line in enumerate((
                "ICU unit, mock-up: %s (%s), %.1f x %.1f mm. Carrier %s."
                % (view, said[view], bb.XLength, bb.YLength, P["CARRIER_LAYOUT"]),
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
        "what": "ICU unit mock-up (D-491, D-270, D-268, Y19) - provisional, nothing measured",
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
    print("ICU unit - MOCK-UP (D-491, D-270, D-268, Y19) - provisional, nothing measured (R11)")
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
    b = D.borders
    print("FACE: %s x %s (%s), round a %s x %s display: borders left %s, right %s, bottom %s, "
          "top %s. The width is set by %s (left) and %s (right); the height by %s (below) and %s "
          "(above)." % (n(D.face_w), n(D.face_h), "typed" if D.face_w_typed or D.face_h_typed
                        else "derived", n(P["DISP_W"]), n(P["DISP_H"]), n(b["left"]),
                        n(b["right"]), n(b["bottom"]), n(b["top"]), D.width_set_by[0],
                        D.width_set_by[1], D.height_set_by[0], D.height_set_by[1]))
    print("DEPTH: bezel %s + tape %s + display %s + %s + display plate %s = %s to the plate's "
          "back; carrier '%s' from Y %s; rear plate's outer face at %s."
          % (n(P["FACE_T"]), n(P["DISP_TAPE"]), n(P["DISP_T"]), n(P["DISP_BACK_CLEAR"]),
             n(P["BULKHEAD"]), n(D.y_bulk1), P["CARRIER_LAYOUT"], n(D.cy0), n(D.y_plate1)))
    print()
    rf = D.rf
    rows = [("face (W x H)", "%s x %s" % (n(D.face_w), n(D.face_h))),
            ("body (W x H, one height front to back)", "%s x %s" % (n(D.body_w), n(D.body_h))),
            ("box depth (face front to the rear lip)", n(D.y_end)),
            ("  to the rear plate's outer face", n(D.y_plate1)),
            ("  to the receptacles' tips", n(D.y_tip)),
            ("depth with plugs (PLUG_L + CABLE_BEND)", "%s (%s behind the face)"
             % (n(D.y_plugs), n(D.y_plugs - D.y_face))),
            ("display flex, straight line, at least", "%s (bottom edge to the %s)"
             % (n(D.flex_len), P["FLEX_TO"])),
            ("ribbon CN8 - J4, straight line", "%s (header face to header face)" % n(D.ribbon)),
            ("page button lead to SW1, straight line", n(D.button_lead) if D.button else
             "no page button (D-580)"),
            ("RF window", "%s: X %s..%s, Y %s..%s, Z %s..%s, %s from the %s" % (
                P["RF_WINDOW_ON"], n(rf[0]), n(rf[1]), n(rf[2]), n(rf[3]), n(rf[4]), n(rf[5]),
                n(D.rf_reach), P["RF_REF"])),
            ("page button", "X %s, Z %s (%s, %s from the display's centre)"
             % (n(D.bX), n(D.bZ), n(D.button_rel[0]), n(D.button_rel[1])) if D.button else
             "not fitted (BUTTON_FITTED False, D-580)"),
            ("BT817 board", "X %s..%s, Z %s..%s, front face Y %s" % (
                n(D.bt.x0), n(D.bt.x1), n(D.bt.z0), n(D.bt.z1), n(D.bt.yb0))),
            ("carrier", "%s; left edge X %s, front edge Y %s, underside Z %s"
             % (N["carrier"], n(D.cx0), n(D.cy0), n(D.cz0)))]
    for it in D.drivers:
        rows.append((it.name + " (placeholder)", "X %s..%s, Z %s..%s, Y %s..%s" % (
            n(it.x0), n(it.x1), n(it.z0), n(it.z1), n(it.y0), n(it.y1))))
    for k, v in rows:
        print("  %-42s %s" % (k, v))
    print()
    print("rear plate, seen from behind (X is the unit's, 0 = the face's left from the seat):")
    for c in sorted(D.conns, key=lambda c: -c.X):
        print("  %-9s %-9s X %7s  Z %6s  TE cut-out %s x %s R%s, screws %s apart "
              "(114-151046 p.%d)" % (c.name, c.part, n(c.X), n(c.Z), n(c.te["w"]), n(c.te["h"]),
                                     n(c.te["r"]), n(c.te["pitch"]), c.te["page"]))
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
        size = "face %s x %s, body %s x %s, depth %s / %s with plugs, ribbon %s, flex %s" % (
            n(N["face_w"]), n(N["face_h"]), n(N["body_w"]), n(N["body_h"]), n(N["box_depth"]),
            n(N["depth_with_plugs"]), n(N["ribbon_straight_line"]),
            n(N["flex_straight_line_at_least"]))
        rows.append((label, want, "BUILT, FAILS" if fails else "BUILT CLEAR", size,
                     ["%s: %s" % (c["name"], c["detail"]) for c in fails]))
    print("=" * 96)
    print("ICU unit mock-up - self-test: %d parameter sets" % len(rows))
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
