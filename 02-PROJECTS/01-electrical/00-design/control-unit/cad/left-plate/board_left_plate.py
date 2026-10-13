"""board_left_plate.py - the left plate's board (Y21): placement from the sketch, a small grid
router (no freerouting on this machine), the GND pour. Called as `gen_left_plate.py pcb` with
KiCad's own Python; reads the netlist kicad-cli exports from left-plate.kicad_sch, so the board's
footprints, values and nets are the sheet's (schematic parity), and writes left-plate.kicad_pcb.

Owns nothing in the record (R6): the geometry constants are gen_left_plate.py's, from the sketch.
"""
import heapq
import json
import math
import os
import random
import subprocess
import sys
from array import array

import pcbnew

import gen_left_plate as G
from check import parse_sexpr, kids, kid, val

MM = pcbnew.FromMM
TOMM = pcbnew.ToMM
KICAD_CLI = "/opt/homebrew/bin/kicad-cli"


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


# --------------------------------------------------------------------------------------------
# Placement: (ref, x, y, rotation, side). Keys by their cap's centre (the footprint origin is
# pad 1, 3.25 / 2.25 mm up-left of it); everything else by its footprint origin.
# --------------------------------------------------------------------------------------------
def placement():
    k1, k2, (sx, sy) = G.K1, G.K2, G.STICK
    # U1 on the back, between the hatch key and the stick, turned so OUT1-OUT5 face the keys (-x) and
    # pins 1-6 (R_EXT, VCC, GND, SDA, SCL) face down toward the bus from J1
    ux, uy = 58.0, 36.0
    jy = 28.0 - 6.35                           # J1 pin 1, so the header is centred on the plate's height
    return [
        ("SW1", k2 - 3.25, 37 - 2.25, 0, "F"),          # hatch key (the sketch: k2, row 2)
        ("SW2", k1 - 3.25, 37 - 2.25, 0, "F"),          # fuel-door key (k1, row 2)
        ("JS1", sx, sy, 0, "F"),
        ("LED1", k1, G.WINK_LED_Y, 0, "F"),              # wink left face, above its button
        ("LED2", k2, G.WINK_LED_Y, 0, "F"),              # wink right face
        ("LED3", k2 + G.KEY_LED_DX, 37, 90, "F"),        # hatch symbol, inside the hatch cap
        ("LED4", k1 + G.KEY_LED_DX, 37, 90, "F"),        # fuel-door symbol, inside its cap
        ("LED5", sx, sy - G.WELL_R - 1.5, 0, "F"),       # mirror symbol, at the top of the stick's well
        ("J1", G.J1_X, jy, 0, "B"),
        ("U1", ux, uy, 90, "B"),
        ("C2", ux + 0.25, uy + 5.0, 0, "B"),            # 100 nF at VCC (pin 3, below)
        ("C1", ux + 0.25, uy + 7.0, 0, "B"),            # 1 uF
        ("R1", ux + 4.5, uy + 3.5, 90, "B"),            # R_EXT (pin 2)
        ("R2", ux + 4.5, uy - 0.5, 90, "B"),            # SDB pull-up (pin 24, right side)
        ("D1", k2, 43.75, 0, "B"),                       # hatch diode, under its key
        ("D2", k1, 43.75, 0, "B"),                       # fuel-door diode
    ]


BOARD_ONLY = [  # (ref, lib, name, x, y, value)
    ("H1", "MountingHole", "MountingHole_3.2mm_M3", 4, 4, "M3"),
    ("H2", "MountingHole", "MountingHole_3.2mm_M3", 96, 4, "M3"),
    ("H3", "MountingHole", "MountingHole_3.2mm_M3", 4, 52, "M3"),
    ("H4", "MountingHole", "MountingHole_3.2mm_M3", 96, 52, "M3"),
    ("H5", "left-plate", "WinkSwitch_P083_Clearance_D%s" % G.fmt(G.WINK_HOLE_D), G.K1, 19, "wink L (P083) - clearance, no nets"),
    ("H6", "left-plate", "WinkSwitch_P083_Clearance_D%s" % G.fmt(G.WINK_HOLE_D), G.K2, 19, "wink R (P083) - clearance, no nets"),
]


def lib_path(lib):
    if lib == "left-plate":
        return os.path.join(G.HERE, "left-plate.pretty")
    return G.KICAD_FPS + lib + ".pretty"


def read_netlist(path):
    root = parse_sexpr(open(path, encoding="utf-8").read())
    comps = {}
    for c in kids(kid(root, "components"), "comp"):
        props = {val(p, "name"): val(p, "value", "") for p in kids(c, "property")}
        fields = {}
        for f in kids(kid(c, "fields") or [], "field"):
            fields[val(f, "name")] = f[2] if len(f) > 2 and isinstance(f[2], str) else ""
        comps[val(c, "ref")] = dict(value=val(c, "value"), footprint=val(c, "footprint"), confirm=props.get("Confirm", ""),
                                    datasheet=fields.get("Datasheet", ""), description=fields.get("Description", ""))
    nets = {}
    for n in kids(kid(root, "nets"), "net"):
        nets[val(n, "name")] = [(val(x, "ref"), val(x, "pin")) for x in kids(n, "node")]
    return comps, nets


# --------------------------------------------------------------------------------------------
# The router
# --------------------------------------------------------------------------------------------
GRID = 0.25
TW = 0.25            # track width
VIA_D, VIA_DRILL = 0.6, 0.3
CLR = 0.2            # copper clearance
HCLR = 0.25          # copper to hole
EDGE = 0.5           # copper to edge
MARGIN = 0.02
NX, NY = int(G.W / GRID), int(G.H / GRID)
FREE, BLOCK = -1, -2
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)


def dist(shape, x, y):
    k = shape[0]
    if k == "rect":
        _, cx, cy, hw, hh = shape
        ex, ey = abs(x - cx) - hw, abs(y - cy) - hh
        if ex <= 0 and ey <= 0:
            return max(ex, ey)                  # inside: negative, the depth
        return math.hypot(max(ex, 0.0), max(ey, 0.0))
    if k == "circ":
        _, cx, cy, r = shape
        return math.hypot(x - cx, y - cy) - r
    _, x1, y1, x2, y2, hw = shape
    vx, vy = x2 - x1, y2 - y1
    L = vx * vx + vy * vy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((x - x1) * vx + (y - y1) * vy) / L))
    return math.hypot(x - (x1 + t * vx), y - (y1 + t * vy)) - hw


def bbox(shape):
    k = shape[0]
    if k == "rect":
        _, cx, cy, hw, hh = shape
        return cx - hw, cy - hh, cx + hw, cy + hh
    if k == "circ":
        _, cx, cy, r = shape
        return cx - r, cy - r, cx + r, cy + r
    _, x1, y1, x2, y2, hw = shape
    return min(x1, x2) - hw, min(y1, y2) - hw, max(x1, x2) + hw, max(y1, y2) + hw


class Grid:
    def __init__(self):
        n = NX * NY
        self.trk = [array("i", [FREE]) * n for _ in LAYERS]   # who may put a track centre here
        self.via = [array("i", [FREE]) * n for _ in LAYERS]   # who may put a via centre here
        for li in range(2):
            for iy in range(NY):
                for ix in range(NX):
                    x, y = ix * GRID, iy * GRID
                    e = min(x, y, G.W - x, G.H - y)
                    i = iy * NX + ix
                    if e < EDGE + TW / 2 + MARGIN:
                        self.trk[li][i] = BLOCK
                    if e < EDGE + VIA_D / 2 + MARGIN:
                        self.via[li][i] = BLOCK
        # the rounded corners carry the M3 holes; the holes block them

    def mark(self, li, shape, net, clr):
        """Every cell a track (or via) centre of another net may not take near `shape`."""
        x0, y0, x1, y1 = bbox(shape)
        for arr, extra in ((self.trk[li], clr + TW / 2 + MARGIN), (self.via[li], clr + VIA_D / 2 + MARGIN)):
            ix0, ix1 = max(0, int((x0 - extra) / GRID) - 1), min(NX - 1, int((x1 + extra) / GRID) + 1)
            iy0, iy1 = max(0, int((y0 - extra) / GRID) - 1), min(NY - 1, int((y1 + extra) / GRID) + 1)
            for iy in range(iy0, iy1 + 1):
                y = iy * GRID
                base = iy * NX
                for ix in range(ix0, ix1 + 1):
                    if dist(shape, ix * GRID, y) <= extra:
                        i = base + ix
                        cur = arr[i]
                        if cur == FREE:
                            arr[i] = net
                        elif cur != net:
                            arr[i] = BLOCK

    def inside(self, shape):
        """Cells whose centre lies in the copper of `shape` (a pad), well inside."""
        x0, y0, x1, y1 = bbox(shape)
        out = []
        for iy in range(max(0, int(y0 / GRID) - 1), min(NY - 1, int(y1 / GRID) + 1) + 1):
            for ix in range(max(0, int(x0 / GRID) - 1), min(NX - 1, int(x1 / GRID) + 1) + 1):
                if dist(shape, ix * GRID, iy * GRID) <= -0.05:
                    out.append(iy * NX + ix)
        return out


DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
STEP, BEND, VIA_COST = 10, 25, 120


def astar(grid, net, starts, targets, tpts):
    """starts / targets: sets of (layer, cell). Returns [(layer, cell)] from a start to a target."""
    openh = []
    best = {}
    came = {}

    def h(cell):
        x, y = cell % NX, cell // NX
        return STEP * min(abs(x - tx) + abs(y - ty) for tx, ty in tpts)

    for li, c in starts:
        if grid.trk[li][c] not in (FREE, net):
            continue
        s = (li, c, 4)
        best[s] = 0
        heapq.heappush(openh, (h(c), 0, s))
    while openh:
        f, g, s = heapq.heappop(openh)
        if best.get(s, 1 << 60) < g:
            continue
        li, c, d = s
        if (li, c) in targets:
            out = [(li, c)]
            while s in came:
                s = came[s]
                if (s[0], s[1]) != out[-1]:
                    out.append((s[0], s[1]))
            return out[::-1]
        x, y = c % NX, c // NX
        for nd, (dx, dy) in enumerate(DIRS):
            nx_, ny_ = x + dx, y + dy
            if not (0 <= nx_ < NX and 0 <= ny_ < NY):
                continue
            nc = ny_ * NX + nx_
            o = grid.trk[li][nc]
            if o != FREE and o != net:
                continue
            ng = g + STEP + (BEND if d != 4 and d != nd else 0)
            ns = (li, nc, nd)
            if ng < best.get(ns, 1 << 60):
                best[ns] = ng
                came[ns] = s
                heapq.heappush(openh, (ng + h(nc), ng, ns))
        ol = 1 - li
        if all(grid.via[k][c] in (FREE, net) for k in (0, 1)) and grid.trk[ol][c] in (FREE, net):
            ng = g + VIA_COST
            ns = (ol, c, d)
            if ng < best.get(ns, 1 << 60):
                best[ns] = ng
                came[ns] = s
                heapq.heappush(openh, (ng + h(c), ng, ns))
    return None


def pad_shape(pad, li):
    pos = pad.GetPosition()
    cx, cy = TOMM(pos.x), TOMM(pos.y)
    layer = LAYERS[li]
    size = pad.GetSize(layer)
    w, h = TOMM(size.x), TOMM(size.y)
    ang = pad.GetOrientation().AsDegrees() % 180
    if abs(ang - 90) < 1:
        w, h = h, w
    if pad.GetShape(layer) == pcbnew.PAD_SHAPE_CIRCLE:
        return ("circ", cx, cy, w / 2)
    return ("rect", cx, cy, w / 2, h / 2)


def route_board(board, order_seed=None, verbose=True):
    grid = Grid()
    netpads = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            code = pad.GetNetCode()
            name = pad.GetNetname()
            pos = pad.GetPosition()
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                r = TOMM(pad.GetDrillSize().x) / 2
                for li in range(2):
                    grid.mark(li, ("circ", TOMM(pos.x), TOMM(pos.y), r), BLOCK, HCLR)
                continue
            net = code if code > 0 and not name.startswith("unconnected-") else BLOCK
            if pad.HasHole():
                r = TOMM(pad.GetDrillSize().x) / 2
            for li in range(2):
                if not pad.IsOnLayer(LAYERS[li]):
                    continue
                shp = pad_shape(pad, li)
                grid.mark(li, shp, net if net != BLOCK else BLOCK, CLR)
                if net != BLOCK:
                    netpads.setdefault(code, []).append((pad, li, shp))
    # nets in routing order: short local nets first, ROW1 and GND last
    names = {code: board.FindNet(code).GetNetname() for code in netpads}
    groups = {}
    for code, lst in netpads.items():
        groups.setdefault(code, {})
        for pad, li, shp in lst:
            # each pad on its own: a tactile switch's two pads of one number are joined in copper too
            key = (pad.GetParentFootprint().GetReference(), pad.GetNumber(), TOMM(pad.GetPosition().x), TOMM(pad.GetPosition().y))
            groups[code].setdefault(key, []).append((li, shp))

    def span(code):
        pts = [(s[1], s[2]) for k in groups[code].values() for li, s in k]
        return max(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a in pts for b in pts)
    order = sorted((c for c in groups if len(groups[c]) > 1), key=span)
    late = [c for c in order if names[c] in ("GND", "/ROW1")]
    order = [c for c in order if c not in late] + late
    if order_seed is not None:
        rnd = random.Random(order_seed)
        rnd.shuffle(order)
    routes = []
    failed = []
    for code in order:
        pins = list(groups[code].items())
        # greedy: start from the first pin, add the nearest unconnected pin each time
        tree_cells = set()
        tree_pts = []
        first = pins.pop(0)
        for li, shp in first[1]:
            for c in grid.inside(shp):
                tree_cells.add((li, c))
            tree_pts.append((int(round(shp[1] / GRID)), int(round(shp[2] / GRID))))
        while pins:
            def near(p):
                shp = p[1][0][1]
                return min(abs(shp[1] / GRID - tx) + abs(shp[2] / GRID - ty) for tx, ty in tree_pts)
            pins.sort(key=near)
            key, lst = pins.pop(0)
            starts = set()
            for li, shp in lst:
                for c in grid.inside(shp):
                    starts.add((li, c))
            if starts & tree_cells:
                path = [next(iter(starts & tree_cells))]
            else:
                path = astar(grid, code, starts, tree_cells, tree_pts[-60:] if len(tree_pts) > 60 else tree_pts)
            if path is None:
                failed.append((names[code], key))
                if verbose:
                    print("  FAILED %s to %s" % (names[code], key))
                continue
            routes.append((code, path))
            # occupy it
            for (la, ca), (lb, cb) in zip(path, path[1:]):
                xa, ya = (ca % NX) * GRID, (ca // NX) * GRID
                xb, yb = (cb % NX) * GRID, (cb // NX) * GRID
                if la == lb:
                    grid.mark(la, ("seg", xa, ya, xb, yb, TW / 2), code, CLR)
                else:
                    for k in (0, 1):
                        grid.mark(k, ("circ", xa, ya, VIA_D / 2), code, CLR)
            for li, c in path:
                tree_cells.add((li, c))
                tree_pts.append((c % NX, c // NX))
            for li, shp in lst:
                for c in grid.inside(shp):
                    tree_cells.add((li, c))
    # GND stitching: a via on a 6 mm lattice wherever one fits, so the two pours join through the
    # pockets the tracks fence off (main() drops any that end up dangling after the fill)
    gnd = next((c for c, n in names.items() if n == "GND"), None)
    stitches = []
    if gnd is not None:
        for iy in range(int(3.0 / GRID), NY - int(3.0 / GRID), int(6.0 / GRID)):
            for ix in range(int(3.0 / GRID), NX - int(3.0 / GRID), int(6.0 / GRID)):
                c = iy * NX + ix
                if all(grid.via[k][c] == FREE and grid.trk[k][c] == FREE for k in (0, 1)):
                    stitches.append(c)
                    for k in (0, 1):
                        grid.mark(k, ("circ", ix * GRID, iy * GRID, VIA_D / 2), gnd, CLR)
        routes.extend((gnd, [(0, c), (1, c)]) for c in stitches)
    return routes, failed


def add_tracks(board, routes):
    nseg = nvia = 0
    for code, path in routes:
        net = board.FindNet(code)
        if len(path) < 2:
            continue
        # split into same-layer runs; a layer change is a via
        run = [path[0]]
        runs = []
        vias = []
        for p in path[1:]:
            if p[0] != run[-1][0]:
                runs.append(run)
                vias.append(p[1])
                run = [p]
            else:
                run.append(p)
        runs.append(run)
        for run in runs:
            pts = [((c % NX) * GRID, (c // NX) * GRID) for _l, c in run]
            li = run[0][0]
            # keep corners only
            keep = [pts[0]]
            for a, b, c in zip(pts, pts[1:], pts[2:]):
                if (b[0] - a[0]) * (c[1] - b[1]) != (b[1] - a[1]) * (c[0] - b[0]):
                    keep.append(b)
            if len(pts) > 1:
                keep.append(pts[-1])
            for a, b in zip(keep, keep[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(V(*a))
                t.SetEnd(V(*b))
                t.SetWidth(MM(TW))
                t.SetLayer(LAYERS[li])
                t.SetNet(net)
                board.Add(t)
                nseg += 1
        for c in vias:
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(V((c % NX) * GRID, (c // NX) * GRID))
            v.SetDrill(MM(VIA_DRILL))
            v.SetWidth(MM(VIA_D))
            v.SetNet(net)
            board.Add(v)
            nvia += 1
    return nseg, nvia


# --------------------------------------------------------------------------------------------
def outline(board):
    r, w, h = G.CORNER_R, G.W, G.H

    def line(a, b):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*a))
        s.SetEnd(V(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.05))
        board.Add(s)

    def arc(c, a0):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        p = lambda ang: (c[0] + r * math.cos(math.radians(ang)), c[1] + r * math.sin(math.radians(ang)))
        s.SetArcGeometry(V(*p(a0)), V(*p(a0 + 45)), V(*p(a0 + 90)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.05))
        board.Add(s)
    line((r, 0), (w - r, 0))
    line((w, r), (w, h - r))
    line((w - r, h), (r, h))
    line((0, h - r), (0, r))
    arc((w - r, r), 270)
    arc((w - r, h - r), 0)
    arc((r, h - r), 90)
    arc((r, r), 180)


def pour(board, gnd):
    for layer in LAYERS:
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetIsRuleArea(False)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in ((0.3, 0.3), (G.W - 0.3, 0.3), (G.W - 0.3, G.H - 0.3), (0.3, G.H - 0.3)):
            ol.Append(MM(x), MM(y))
        z.SetLocalClearance(MM(0.3))
        z.SetMinThickness(MM(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)          # solid, as the panel's pour
        z.SetThermalReliefGap(MM(0.4))
        z.SetThermalReliefSpokeWidth(MM(0.4))
        z.SetAssignedPriority(0)
        board.Add(z)
    # filled by kicad-cli after the save (main), with the project's rules


def silk(board, text, x, y, layer, size=1.2):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(V(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.15))
    if layer in (pcbnew.B_SilkS, pcbnew.B_Fab):
        t.SetMirrored(True)
    board.Add(t)


def build(seed=None, do_pour=True):
    if G.FLIP:
        raise NotImplementedError("FLIP: the board is drawn for the sketch's default only (stick on the wheel side)")
    sch = os.path.join(G.HERE, G.NAME + ".kicad_sch")
    netf = os.path.join(G.HERE, G.NAME + ".net")
    subprocess.check_call([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", netf, sch])
    comps, nets = read_netlist(netf)
    os.remove(netf)
    board = pcbnew.NewBoard(os.path.join(G.HERE, G.NAME + ".kicad_pcb"))
    board.SetCopperLayerCount(2)
    tb = board.GetTitleBlock()
    tb.SetTitle("Left plate (D-492, Y21) - provisional")
    tb.SetRevision("0.01")
    tb.SetDate("2026-10-13")
    tb.SetCompany("RX-7 FB electrical build")
    tb.SetComment(0, "100 x 56 from the sketch's plate - confirm (R11, nothing measured left of the wheel)")
    netobj = {}
    for name in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        netobj[name] = n
    pin_net = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pin_net[(ref, pin)] = name
    place = {p[0]: p[1:] for p in placement()}
    for ref, c in sorted(comps.items()):
        lib, name = c["footprint"].split(":", 1)
        fp = pcbnew.FootprintLoad(lib_path(lib), name)
        fp.SetFPIDAsString(c["footprint"])
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        fp.SetPath(pcbnew.KIID_PATH("/" + G.uid("sym" + ref)))
        for f in fp.GetFields():                 # the sheet's Datasheet / Description, for parity
            if f.GetName() == "Datasheet":
                f.SetText(c["datasheet"])
            elif f.GetName() == "Description":
                f.SetText(c["description"])
        if c["confirm"]:
            f = pcbnew.PCB_FIELD(fp, fp.GetNextFieldOrdinal(), "Confirm")
            f.SetText(c["confirm"])
            f.SetVisible(False)
            f.SetLayer(pcbnew.F_Fab)
            fp.Add(f)
        x, y, rot, side = place[ref]
        board.Add(fp)
        fp.SetPosition(V(x, y))
        fp.SetOrientationDegrees(rot)
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netobj[n])
        r = fp.Reference()
        r.SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)
    for ref, lib, name, x, y, value in BOARD_ONLY:
        fp = pcbnew.FootprintLoad(lib_path(lib), name)
        fp.SetFPIDAsString("%s:%s" % (lib, name))
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetBoardOnly(True)
        board.Add(fp)
        fp.SetPosition(V(x, y))
        fp.Reference().SetLayer(pcbnew.F_Fab)
    outline(board)
    routes, failed = route_board(board, seed)
    nseg, nvia = add_tracks(board, routes)
    if do_pour:
        pour(board, netobj["GND"])
    silk(board, "LEFT PLATE  Y21  rev 0.01", 50.0, 53.4, pcbnew.B_SilkS, 1.0)
    silk(board, "D-492 - provisional, confirm", 50.0, 51.6, pcbnew.B_SilkS, 0.8)
    return board, failed, nseg, nvia


def main():
    args = sys.argv[2:]
    seed = next((int(a) for a in args if a.isdigit()), None)
    board, failed, nseg, nvia = build(seed, "nopour" not in args)
    out = os.path.join(G.HERE, G.NAME + ".kicad_pcb")
    pcbnew.SaveBoard(out, board)
    G.gen_pro()                     # SaveBoard may have rewritten the project with defaults
    rpt = os.path.join(G.HERE, G.NAME + "-drc.json")
    for _round in range(3):
        subprocess.call([KICAD_CLI, "pcb", "drc", "--refill-zones", "--save-board", "--format", "json",
                         "--severity-all", "-o", rpt, out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        G.gen_pro()
        rep = json.load(open(rpt, encoding="utf-8"))
        dead = set()
        for v in rep.get("violations", []) + rep.get("unconnected_items", []):
            if v.get("type") in ("via_dangling", "unconnected_items", "isolated_copper"):
                for it in v.get("items", []):
                    if it.get("description", "").startswith("Via"):
                        p = it["pos"]
                        dead.add((round(p["x"], 3), round(p["y"], 3)))
        if not dead:
            break
        b2 = pcbnew.LoadBoard(out)
        gone = 0
        for t in list(b2.GetTracks()):
            if t.GetClass() == "PCB_VIA" and t.GetNetname() == "GND":
                q = t.GetPosition()
                if (round(TOMM(q.x), 3), round(TOMM(q.y), 3)) in dead:
                    b2.Remove(t)
                    gone += 1
        pcbnew.SaveBoard(out, b2)
        G.gen_pro()
        print("  dropped %d dangling stitching vias" % gone)
    os.remove(rpt)
    print("routed: %d segments, %d vias, %d failed %s" % (nseg, nvia, len(failed), failed))
    if failed:
        sys.exit(1)
