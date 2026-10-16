"""cur_board_pcb.py - the CUR board (Y71, D-615): placement from the ruled face (D-602), a small grid
router (no freerouting on this machine), the GND pour. Called as `cur_board_sch.py pcb` with
KiCad's own Python; reads the netlist kicad-cli exports from cur-board.kicad_sch, so the board's
footprints, values and nets are the sheet's (schematic parity), and writes cur-board.kicad_pcb.

Owns nothing in the record (R6): the geometry constants are cur_board_sch.py's, from the sketch.
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

import cur_board_sch as G
from check import parse_sexpr, kids, kid, val

MM = pcbnew.FromMM
TOMM = pcbnew.ToMM
KICAD_CLI = "/opt/homebrew/bin/kicad-cli"


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


# --------------------------------------------------------------------------------------------
# Placement: (ref, x, y, rotation, side). Every switch on its cap's centre (the footprints' origin),
# from the face's geometry (cur_board_sch.py, D-602); the chips behind, clear of every through-hole pin.
# --------------------------------------------------------------------------------------------
def placement():
    k1, k2, (sx, sy), (kx, ky), (hx, hy) = G.K1, G.K2, G.STICK, G.KNOB, G.HAZ
    wy, ry = G.WINK_Y, G.KEY_Y
    d = G.CAP_LED_DX
    return [
        # the face's controls (F.Cu, toward the driver)
        ("ENC1", kx, ky, 0, "F"),                        # the screen knob's encoder, its shaft on the knob's axis
        ("SW6", sx, sy, 0, "F"),                         # the mirror control, in its well
        ("SW5", hx, hy, 0, "F"),                         # the hazard, under the top row's wide cap
        ("SW3", k1, wy, 0, "F"),                         # wink left
        ("SW4", k2, wy, 0, "F"),                         # wink right
        ("SW2", k1, ry, 0, "F"),                         # fuel door, below wink left
        ("SW1", k2, ry, 0, "F"),                         # hatch, below wink right
        ("LED1", k1 + d, wy, 90, "F"),                   # wink left face, inside its cap
        ("LED2", k2 + d, wy, 90, "F"),
        ("LED4", k1 + d, ry, 90, "F"),                   # fuel-door symbol
        ("LED3", k2 + d, ry, 90, "F"),                   # hatch symbol
        ("LED5", sx, sy - 5.0, 0, "F"),                  # mirror symbol, inside the control's well
        ("LED6", hx + G.HAZ_LED_DX, hy, 90, "F"),        # the hazard's red triangle
        # the pigtail's pads, on the row between the winks and the keys, wired from the back
        ("J1", G.J1_AT[0] + 8 * G.J1_PITCH, G.J1_AT[1], 0, "B"),   # on the back the row mirrors: pad 1 at the right, seen from the front
        # behind (B.Cu): the regulator under the knob, the LED driver and the expander under the top row
        ("U3", kx - 1.0, ky - 2.0, 0, "B"),
        ("C4", kx - 4.0, ky + 2.5, 90, "B"),
        ("C5", kx + 2.0, ky + 2.5, 90, "B"),
        # the LED driver beside the LEDs it drives (top right), the expander beside the switches it reads (behind the
        # mirror control, bottom left), so neither's lines cross the board; chips on the 0.25 mm routing grid
        ("U1", 31.0, 6.5, 0, "B"),
        ("R1", 34.75, 5.0, 90, "B"),                     # R_EXT straight beside its pin (pad 2)
        ("C2", 34.75, 8.5, 90, "B"),                     # 100 nF at VCC (pad 3)
        ("R2", 33.0, 2.0, 0, "B"),                       # SDB (pad 24)
        ("C1", 28.0, 10.25, 0, "B"),                     # 1 uF on +5V_PNL
        ("U2", 6.0, 20.5, 0, "B"),
        ("C3", 4.5, 15.25, 0, "B"),                      # U2's VDD decoupler, above its VDD pin (24)
        ("R3", 15.8, 25.4, 0, "B"),                      # 18k, wink left
        ("R4", 20.6, 25.4, 0, "B"),                      # 33k, wink right
        ("R5", 26.6, 25.4, 0, "B"),                      # 4.7k, the hazard
        ("R6", 31.4, 25.4, 0, "B"),                      # 47k, the hazard's baseline
    ]


BOARD_ONLY = []   # no mounting holes: the board sits on a ledge in the case's walls, the rear cover's posts hold it (D-615)


def lib_path(lib):
    if lib == "cur-board":
        return os.path.join(G.HERE, "cur-board.pretty")
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
GRID = 0.125                         # fine enough for 0.2 mm tracks at 0.15 mm space between THT pins (Y71)
TW = 0.2             # track width - the CUR's own rules (cur_board_sch.gen_pro, Y71)
VIA_D, VIA_DRILL = 0.5, 0.25
CLR = 0.15           # copper clearance
HCLR = 0.2           # copper to hole
EDGE = 0.5           # copper to edge
MARGIN = 0.02
NX, NY = int(G.W / GRID), int(G.H / GRID)
FREE, BLOCK = -1, -2
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)          # the routing layers; the two inner ones are planes (Y71)
PLANE_NETS = {"GND": pcbnew.In1_Cu, "/+5V_PNL": pcbnew.In2_Cu}
FIRST = ()                                   # nets routed before the rest (none: span order did best)


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
    if pad.GetShape(layer) == pcbnew.PAD_SHAPE_OVAL:    # a stadium: a rect's corners are not copper
        if w >= h:                                      # (J2's JST pads, 1.7 x 2.0)
            return ("seg", cx - (w - h) / 2, cy, cx + (w - h) / 2, cy, h / 2)
        return ("seg", cx, cy - (h - w) / 2, cx, cy + (h - w) / 2, w / 2)
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
    order = sorted((c for c in groups if len(groups[c]) > 1 and names[c] not in PLANE_NETS), key=span)
    first = [c for c in order if names[c] in FIRST]                # the bus crosses the board: before the local nets
    order = first + [c for c in order if c not in first]
    if order_seed is not None:                                     # another order for the rest, the bus still first
        rest = [c for c in order if c not in first]
        random.Random(order_seed).shuffle(rest)
        order = first + rest
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


def plane(board, net, layer):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetIsRuleArea(False)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in ((0.3, 0.3), (G.W - 0.3, 0.3), (G.W - 0.3, G.H - 0.3), (0.3, G.H - 0.3)):
        ol.Append(MM(x), MM(y))
    z.SetLocalClearance(MM(0.3))
    z.SetMinThickness(MM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(MM(0.3))
    z.SetThermalReliefSpokeWidth(MM(0.3))
    board.Add(z)


def pour(board, gnd):
    for name, layer in PLANE_NETS.items():           # the two inner planes, whole-board
        plane(board, board.FindNet(name), layer)
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


FREEROUTING = os.path.expanduser("~/.local/share/freerouting/freerouting.jar")
FR_ONLY = False                      # the grid router first, freerouting and the grid finish after (Y71)
FR_PASSES = "8"
FR_TIMEOUT = 900


def finish_with_freerouting(board):
    """What the grid router leaves, freerouting 1.9 finishes (Y62, 2026-10-14): the tracks already laid are its
    starting point (it may move them), a 0.6 mm band inside the edge kept free (the router does not read KiCad's edge clearance), the
    board has no pour yet so GND is routed as a signal, and the router's ends - left a micron apart - are
    snapped together after the import. Returns the connections still open."""
    if not os.path.exists(FREEROUTING):
        return None
    for t in board.GetTracks():
        t.SetLocked(False)          # a starting point it may move: locked, the last LED line is boxed in
    band = []
    for (x0, y0, x1, y1) in ((0, 0, G.W, 0.6), (0, G.H - 0.6, G.W, G.H), (0, 0, 0.6, G.H), (G.W - 0.6, 0, G.W, G.H)):
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowZoneFills(False)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET()
        for li in LAYERS:
            ls.AddLayer(li)
        z.SetLayerSet(ls)
        o = z.Outline()
        o.NewOutline()
        for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            o.Append(MM(x), MM(y))
        board.Add(z)
        band.append(z)
    dsn = os.path.join(G.HERE, G.NAME + ".dsn")
    ses = os.path.join(G.HERE, G.NAME + ".ses")
    pcbnew.ExportSpecctraDSN(board, dsn)
    try:                                    # its optimiser can run on for half an hour: five minutes, then the next try
        subprocess.call(["java", "-jar", FREEROUTING, "-de", dsn, "-do", ses, "-mp", FR_PASSES],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=FR_TIMEOUT)
    except subprocess.TimeoutExpired:
        subprocess.call(["pkill", "-f", "freerouting.jar"])
    ok = os.path.exists(ses) and pcbnew.ImportSpecctraSES(board, ses)
    for f in (dsn, ses):
        if os.path.exists(f):
            os.remove(f)
    for z in band:
        board.RemoveNative(z)
    if not ok:
        return None
    tol = MM(0.01)
    tracks = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK"]
    anchors = [(p.GetPosition(), p.GetNetCode()) for fp in board.GetFootprints() for p in fp.Pads()]
    anchors += [(t.GetPosition(), t.GetNetCode()) for t in board.GetTracks() if t.GetClass() == "PCB_VIA"]
    for t in tracks:
        t.SetLocked(False)
        for get, put in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
            q = get()
            for a, net in anchors:
                if net == t.GetNetCode() and a != q and abs(a.x - q.x) <= tol and abs(a.y - q.y) <= tol:
                    put(pcbnew.VECTOR2I(a.x, a.y))
                    break
    for t in [t for t in tracks if t.GetStart() == t.GetEnd()]:
        board.RemoveNative(t)
    board.BuildConnectivity()
    return board.GetConnectivity().GetUnconnectedCount(False)


def _copper(board):
    """Every copper item by net: [(layer index, shape, kind)] - pads, tracks, vias - in grid millimetres."""
    out = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            code = pad.GetNetCode()
            if code <= 0 or pad.GetNetname().startswith("unconnected-"):
                continue
            for li in range(2):
                if pad.IsOnLayer(LAYERS[li]):
                    out.setdefault(code, []).append((li, pad_shape(pad, li), "pad"))
    for t in board.GetTracks():
        code = t.GetNetCode()
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            for li in range(2):
                out.setdefault(code, []).append((li, ("circ", TOMM(p.x), TOMM(p.y), TOMM(t.GetWidth(pcbnew.F_Cu)) / 2), "via"))
        else:
            a, b = t.GetStart(), t.GetEnd()
            li = LAYERS.index(t.GetLayer())
            out.setdefault(code, []).append((li, ("seg", TOMM(a.x), TOMM(a.y), TOMM(b.x), TOMM(b.y), TOMM(t.GetWidth()) / 2), "track"))
    return out


def _touch(a, b):
    """Two copper shapes on one layer meet: sample a's outline-ish points against b."""
    pts = []
    k = a[0]
    if k == "seg":
        _, x1, y1, x2, y2, hw = a
        pts = [(x1, y1), (x2, y2), ((x1 + x2) / 2, (y1 + y2) / 2)]
        r = hw
    elif k == "circ":
        pts, r = [(a[1], a[2])], a[3]
    else:
        pts, r = [(a[1], a[2])], min(a[3], a[4])
    return any(dist(b, x, y) <= r + 0.01 for x, y in pts) or (b[0] != "seg" and dist(a, b[1], b[2]) <= 0.01)


def finish_with_grid(board, verbose=True):
    """What freerouting leaves (Y71): each net's copper grouped by contact, the groups joined by the grid router's
    A* through every other net's copper. Returns the joins it could not make."""
    grid = Grid()
    cop = _copper(board)
    for code, items in cop.items():
        for li, shp, kind in items:
            grid.mark(li, shp, code, CLR)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() <= 0 or pad.GetNetname().startswith("unconnected-"):
                for li in range(2):                       # a pin no net uses is still copper: nothing crosses it
                    if pad.IsOnLayer(LAYERS[li]):
                        grid.mark(li, pad_shape(pad, li), BLOCK, CLR)
            if pad.HasHole():
                q = pad.GetPosition()
                for li in range(2):
                    grid.mark(li, ("circ", TOMM(q.x), TOMM(q.y), TOMM(pad.GetDrillSize().x) / 2), BLOCK if pad.GetNetCode() <= 0 else pad.GetNetCode(), HCLR)
    failed = []
    added = []
    for code, items in sorted(cop.items()):
        if board.FindNet(code).GetNetname() in PLANE_NETS:
            continue                                    # a plane's net: its pins reach their plane by fanout()
        n = len(items)
        parent = list(range(n))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(n):
            for j in range(i + 1, n):
                li, a, ka = items[i]
                lj, b, kb = items[j]
                same_spot = ka in ("via", "pad") and kb in ("via", "pad") and a[0] != "seg" and b[0] != "seg" and \
                    abs(a[1] - b[1]) < 0.01 and abs(a[2] - b[2]) < 0.01           # one via / THT pad on both layers
                if same_spot or (li == lj and (_touch(a, b) or _touch(b, a))):
                    parent[find(i)] = find(j)
        groups = {}
        for i in range(n):
            groups.setdefault(find(i), []).append(i)
        clusters = list(groups.values())
        if len(clusters) < 2:
            continue

        def cells(idx):
            out = set()
            for i in idx:
                li, shp, _k = items[i]
                got = grid.inside(shp)
                if not got and shp[0] != "seg":           # a pad smaller than a cell: the cell at its centre
                    got = [int(round(shp[2] / GRID)) * NX + int(round(shp[1] / GRID))]
                for c in got:
                    out.add((li, c))
                if shp[0] == "seg":                     # a thin track: its centre line's cells
                    _, x1, y1, x2, y2, _hw = shp
                    steps = max(1, int(max(abs(x2 - x1), abs(y2 - y1)) / GRID))
                    for s in range(steps + 1):
                        x, y = x1 + (x2 - x1) * s / steps, y1 + (y2 - y1) * s / steps
                        out.add((li, int(round(y / GRID)) * NX + int(round(x / GRID))))
            return out
        tree = cells(clusters[0])
        rest = clusters[1:]
        while rest:
            tgt = set()
            for cl in rest:
                tgt |= cells(cl)
            tpts = list({(c % NX, c // NX) for _l, c in tgt})[:200]
            path = astar(grid, code, tree, tgt, tpts) if tpts and tree else None
            if path is None:
                failed.append(board.FindNet(code).GetNetname())
                if verbose:
                    print("  grid finish FAILED %s" % board.FindNet(code).GetNetname())
                break
            end = path[-1]
            hit = next(cl for cl in rest if end in cells(cl))
            rest.remove(hit)
            tree |= cells(hit)
            for (la, ca), (lb, cb) in zip(path, path[1:]):
                xa, ya = (ca % NX) * GRID, (ca // NX) * GRID
                xb, yb = (cb % NX) * GRID, (cb // NX) * GRID
                if la == lb:
                    grid.mark(la, ("seg", xa, ya, xb, yb, TW / 2), code, CLR)
                else:
                    for k in (0, 1):
                        grid.mark(k, ("circ", xa, ya, VIA_D / 2), code, CLR)
            tree |= set(path)
            added.append((code, path))
    nseg, nvia = add_tracks(board, added)
    if verbose:
        print("  grid finish: %d joins, %d segments, %d vias, %d failed %s" % (len(added), nseg, nvia, len(failed), failed))
    return failed


def fanout(board, verbose=True):
    """Every surface pin of a plane's net (GND, +5V_PNL) gets a short stub to a via of its own beside it, the via
    landing on the net's inner plane (In1 GND, In2 +5V_PNL); through-hole pins meet their plane directly."""
    grid = Grid()
    for code, items in _copper(board).items():
        for li, shp, kind in items:
            grid.mark(li, shp, code, CLR)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() <= 0 or pad.GetNetname().startswith("unconnected-"):
                for li in range(2):
                    if pad.IsOnLayer(LAYERS[li]):
                        grid.mark(li, pad_shape(pad, li), BLOCK, CLR)
            if pad.HasHole():
                q = pad.GetPosition()
                for li in range(2):
                    grid.mark(li, ("circ", TOMM(q.x), TOMM(q.y), TOMM(pad.GetDrillSize().x) / 2), BLOCK if pad.GetNetCode() <= 0 else pad.GetNetCode(), HCLR)
    added, missed, vias = [], [], set()
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            name = pad.GetNetname()
            if name not in PLANE_NETS or pad.HasHole():
                continue
            code = pad.GetNetCode()
            li = 0 if pad.IsOnLayer(pcbnew.F_Cu) else 1
            p = pad.GetPosition()
            px, py = TOMM(p.x), TOMM(p.y)
            starts = set((li, c) for c in grid.inside(pad_shape(pad, li))) or \
                {(li, int(round(py / GRID)) * NX + int(round(px / GRID)))}
            best = None
            r = int(2.5 / GRID)
            cx, cy = int(round(px / GRID)), int(round(py / GRID))
            cands = sorted(((dx * dx + dy * dy, cx + dx, cy + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)
                            if 0 <= cx + dx < NX and 0 <= cy + dy < NY), key=lambda z: z[0])
            for _d, x, y in cands:
                c = y * NX + x
                if not all(grid.via[k][c] in (FREE, code) for k in (0, 1)) or grid.trk[1 - li][c] not in (FREE, code):
                    continue
                path = astar(grid, code, starts, {(li, c)}, [(x, y)])
                if path is not None and len(path) <= 2 * r + 4 and all(l_ == li for l_, _c in path):
                    best = (c, path)
                    break
            if best is None:
                missed.append("%s.%s" % (fp.GetReference(), pad.GetNumber()))
                continue
            c, path = best
            for (la, ca), (lb, cb) in zip(path, path[1:]):
                grid.mark(la, ("seg", (ca % NX) * GRID, (ca // NX) * GRID, (cb % NX) * GRID, (cb // NX) * GRID, TW / 2), code, CLR)
            for k in (0, 1):
                grid.mark(k, ("circ", (c % NX) * GRID, (c // NX) * GRID, VIA_D / 2), code, CLR)
            added.append((code, path + ([] if c in vias else [(1 - li, c)])))     # a via already there is shared
            vias.add(c)
    nseg, nvia = add_tracks(board, added)
    if verbose:
        print("  fanout: %d pins to their planes, %d segments, %d vias; missed %s" % (len(added), nseg, nvia, missed or "none"))
    return missed


def stitch(board, gnd, pitch=3.0):
    """GND vias on a lattice wherever one clears every other net's copper and the edge, so the two pours join
    (main() drops any the fill leaves dangling). Freerouting's boards have none of their own."""
    items = []
    for t in board.GetTracks():
        if t.GetNetCode() == gnd.GetNetCode() and t.GetClass() != "PCB_VIA":
            continue                                    # its own tracks it may touch; no via sits on another
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            items.append(("circ", TOMM(p.x), TOMM(p.y), TOMM(t.GetWidth(pcbnew.F_Cu)) / 2))
        else:
            a, b = t.GetStart(), t.GetEnd()
            items.append(("seg", TOMM(a.x), TOMM(a.y), TOMM(b.x), TOMM(b.y), TOMM(t.GetWidth()) / 2))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() == gnd.GetNetCode() and not pad.HasHole():
                continue
            for li in range(2):
                if pad.IsOnLayer(LAYERS[li]) or pad.HasHole():
                    items.append(pad_shape(pad, li))
            if pad.HasHole():
                q = pad.GetPosition()
                items.append(("circ", TOMM(q.x), TOMM(q.y), TOMM(pad.GetDrillSize().x) / 2 + HCLR))
    need = VIA_D / 2 + CLR + MARGIN
    y = pitch / 2
    n = 0
    while y < G.H - EDGE - VIA_D / 2:
        x = pitch / 2
        while x < G.W - EDGE - VIA_D / 2:
            if min(x, y, G.W - x, G.H - y) >= EDGE + VIA_D / 2 and all(dist(s, x, y) > need for s in items):
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(V(x, y))
                v.SetDrill(MM(VIA_DRILL))
                v.SetWidth(MM(VIA_D))
                v.SetNet(gnd)
                board.Add(v)
                items.append(("circ", x, y, VIA_D / 2))
                n += 1
            x += pitch
        y += pitch
    return n


def build(seed=None, do_pour=True):
    sch = os.path.join(G.HERE, G.NAME + ".kicad_sch")
    netf = os.path.join(G.HERE, G.NAME + ".net")
    subprocess.check_call([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", netf, sch])
    comps, nets = read_netlist(netf)
    os.remove(netf)
    board = pcbnew.NewBoard(os.path.join(G.HERE, G.NAME + ".kicad_pcb"))
    board.SetCopperLayerCount(4)                 # In1 the GND plane, In2 the +5V_PNL plane (Y71)
    for layer in PLANE_NETS.values():
        board.SetLayerType(layer, pcbnew.LT_POWER)   # freerouting reads them as planes, never routes on them
    tb = board.GetTitleBlock()
    tb.SetTitle("CUR board (D-597, D-602, D-604, D-615, Y71) - placeholders confirm")
    tb.SetRevision(G.REV)
    tb.SetDate(G.DATE)
    tb.SetCompany("RX-7 FB electrical build")
    tb.SetComment(0, "%.2f x %.2f: the D-602 face's control area; nothing measured (R11)" % (G.W, G.H))
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
    if FR_ONLY:                      # Y71: the CUR's 38 x 27 board, populated both sides, is freerouting's from the start
        routes, failed, nseg, nvia = [], ["everything"], 0, 0
    else:
        routes, failed = route_board(board, seed)
        nseg, nvia = add_tracks(board, routes)
    missed = fanout(board)           # every power pin to its plane first: the routers then see the planes' vias
    if failed:
        failed = finish_with_grid(board)
    if failed:
        for name, layer in PLANE_NETS.items():      # the planes, so freerouting's design knows the pins joined
            plane(board, board.FindNet(name), layer)
        left = finish_with_freerouting(board)
        for z in [z for z in board.Zones() if z.GetLayer() in PLANE_NETS.values()]:
            board.RemoveNative(z)
        print("  freerouting finished the %d left: %s connection(s) still open" % (len(failed), left))
        board.BuildConnectivity()
        failed = finish_with_grid(board)
    failed = failed + missed
    if do_pour:
        stitch(board, netobj["GND"])
        pour(board, netobj["GND"])
    silk(board, "CUR rev %s" % G.REV, 6.4, 25.6, pcbnew.B_SilkS, 0.8)
    silk(board, "DP-CUR 1-9", G.J1_AT[0] + 4 * G.J1_PITCH, G.J1_AT[1] + 2.0, pcbnew.B_SilkS, 0.8)
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
