"""board_bridge.py - the display bridge board's board (Y46): placement, routing by freerouting through
the Specctra DSN / SES round trip, the GND pours. Called as `gen_bridge.py pcb` with KiCad's own
Python; reads the netlist kicad-cli exports from bridge-board.kicad_sch, so the board's footprints,
values and nets are the sheet's (schematic parity), and writes bridge-board.kicad_pcb.

The router: freerouting (Java), named in FREEROUTING or found at ~/.local/share/freerouting/freerouting.jar
(1.9.0 runs on Java 17). Owns nothing in the record (R6); nothing here is measured (R11).
"""
import json
import math
import os
import subprocess
import sys

import pcbnew

import gen_bridge as G
from check import parse_sexpr, kids, kid, val

MM = pcbnew.FromMM
TOMM = pcbnew.ToMM
KICAD_CLI = os.environ.get("KICAD_CLI", "/opt/homebrew/bin/kicad-cli")
FREEROUTING = os.environ.get("FREEROUTING", os.path.expanduser("~/.local/share/freerouting/freerouting.jar"))
W, H = 62.0, 46.0
CORNER_R = 2.0
HOLES = [(3.5, 3.5), (W - 3.5, 3.5), (3.5, H - 3.5), (W - 3.5, H - 3.5)]
UX, UY = 30.0, 22.0                 # the TFP410's centre


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def placement():
    """(ref, x, y, rotation, side). U1 turned 90 so its data pins (49-64 and 33-48) face J1 and the
    top edge, the TMDS outputs (17-32) face J2, the configuration pins (1-16) the bottom."""
    P = [("J1", 4.95, H / 2, 270, "F"),          # FH12: the mouth on the left edge
         ("U1", UX, UY, 90, "F"),
         ("J2", W - 8.0, UY, 0, "F"),            # HDMI: the mouth on the right edge
         ("J3", 10.5, H - 4.0, 0, "F"),
         ("U2", 20.5, H - 4.5, 0, "F"),
         ("C1", 17.0, H - 8.0, 0, "F"),
         ("C2", 25.5, H - 4.5, 0, "F"),
         ("C9", W - 13.0, UY + 10.0, 0, "F"),
         ("R1", UX + 8.5, UY + 6.0, 90, "F"),     # TFADJ, pin 19 (the right side once turned)
         ("R2", UX - 4.0, UY + 10.0, 90, "F"),    # MSEN, pin 11 (the bottom once turned)
         ("R3", UX - 1.5, UY + 10.0, 90, "F"),    # PD, pin 10
         ("R4", UX + 1.0, UY + 10.0, 90, "F"),    # EDGE, pin 9
         ("JP1", UX + 4.5, UY + 13.0, 0, "F"),
         ("JP2", UX - 1.5, UY + 14.5, 0, "F"),
         ("TP1", 13.0, 4.0, 0, "F"),
         ("TP2", UX - 6.5, UY + 13.5, 0, "F"),
         ("TP3", W - 13.0, UY + 14.0, 0, "F")]
    # the six 100 nF on the back, under their pins' row: (cap, TFP410 pin)
    return P, [("C3", "1"), ("C4", "12"), ("C5", "33"), ("C6", "18"), ("C7", "23"), ("C8", "29")]


BOARD_ONLY = [("H%d" % (i + 1), "MountingHole", "MountingHole_3.2mm_M3", x, y, "M3") for i, (x, y) in enumerate(HOLES)]


def lib_path(lib):
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


def outline(board):
    r = CORNER_R

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
    line((r, 0), (W - r, 0))
    line((W, r), (W, H - r))
    line((W - r, H), (r, H))
    line((0, H - r), (0, r))
    arc((W - r, r), 270)
    arc((W - r, H - r), 0)
    arc((r, H - r), 90)
    arc((r, r), 180)


def pour(board, gnd):
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetIsRuleArea(False)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in ((0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)):
            ol.Append(MM(x), MM(y))
        z.SetLocalClearance(MM(0.25))
        z.SetMinThickness(MM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(MM(0.3))
        z.SetThermalReliefSpokeWidth(MM(0.35))
        z.SetAssignedPriority(0)
        board.Add(z)


def silk(board, text, x, y, layer, size=1.0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(V(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(0.15))
    if layer in (pcbnew.B_SilkS, pcbnew.B_Fab):
        t.SetMirrored(True)
    board.Add(t)


def add_fp(board, ref, c, netobj, pin_net):
    lib, name = c["footprint"].split(":", 1)
    fp = pcbnew.FootprintLoad(lib_path(lib), name)
    fp.SetFPIDAsString(c["footprint"])
    fp.SetReference(ref)
    fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH("/" + G.uid("sym" + ref)))
    for f in fp.GetFields():
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
    board.Add(fp)
    for pad in fp.Pads():
        n = pin_net.get((ref, pad.GetNumber()))
        if n:
            pad.SetNet(netobj[n])
    return fp


def build():
    sch = os.path.join(G.HERE, G.NAME + ".kicad_sch")
    netf = os.path.join(G.HERE, G.NAME + ".net")
    subprocess.check_call([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", netf, sch],
                          stdout=subprocess.DEVNULL)
    comps, nets = read_netlist(netf)
    os.remove(netf)
    board = pcbnew.NewBoard(os.path.join(G.HERE, G.NAME + ".kicad_pcb"))
    board.SetCopperLayerCount(2)
    tb = board.GetTitleBlock()
    tb.SetTitle("Display bridge board (P119, D-550, Y46) - provisional")
    tb.SetRevision(G.REV)
    tb.SetDate(G.DATE)
    tb.SetCompany("RX-7 FB electrical build")
    tb.SetComment(0, "62 x 46, 2 layers - its place in the Display Unit is not drawn yet (confirm, R11)")
    netobj = {}
    for name in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        n.thisown = False
        board.Add(n)
        netobj[name] = n
    pin_net = {(ref, pin): name for name, nodes in nets.items() for ref, pin in nodes}
    places, caps = placement()
    fps = {}
    for ref, x, y, rot, side in places:
        fp = add_fp(board, ref, comps[ref], netobj, pin_net)
        fp.SetPosition(V(x, y))
        fp.SetOrientationDegrees(rot)
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.Reference().SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)
        fps[ref] = fp
    u1 = fps["U1"]
    for ref, pin in caps:                         # under the pin's row, on the back, parallel to the side
        p = [q for q in u1.Pads() if q.GetNumber() == pin][0].GetPosition()
        px, py = TOMM(p.x), TOMM(p.y)
        dx, dy = px - UX, py - UY
        horiz = abs(dy) > abs(dx)                 # the pin is on the top or bottom side
        cx = px if horiz else UX + math.copysign(9.6 if ref == "C7" else 7.6, dx)
        cy = UY + math.copysign(7.6, dy) if horiz else py
        fp = add_fp(board, ref, comps[ref], netobj, pin_net)
        fp.SetPosition(V(cx, cy))
        fp.SetOrientationDegrees(0 if horiz else 90)
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.Reference().SetLayer(pcbnew.B_Fab)
        fps[ref] = fp
    missing = sorted(set(comps) - set(fps))
    assert not missing, missing
    # nine 0.6 / 0.3 vias in the exposed pad to the back pour: the TFP410's heat path (TI's PowerPAD
    # guidance; the 0.2 mm vias of KiCad's ThermalVias variant are under the fab's 0.3 mm minimum)
    for dx in (-2.0, 0.0, 2.0):
        for dy in (-2.0, 0.0, 2.0):
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(V(UX + dx, UY + dy))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetWidth(pcbnew.F_Cu, MM(0.6))
            v.SetDrill(MM(0.3))
            v.SetNet(netobj["GND"])
            board.Add(v)
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
    silk(board, "DISPLAY BRIDGE  Y46  rev %s" % G.REV, W / 2, H - 1.6, pcbnew.F_SilkS, 0.9)
    silk(board, "J1 pin k = ME817EV CN1 pin 51-k (type-A FFC)", W / 2, 1.6, pcbnew.F_SilkS, 0.8)
    return board, netobj


def route(board):
    out = os.path.join(G.HERE, G.NAME + ".kicad_pcb")
    dsn = os.path.join(G.HERE, G.NAME + ".dsn")
    ses = os.path.join(G.HERE, G.NAME + ".ses")
    pcbnew.SaveBoard(out, board)
    G.gen_pro()
    board = pcbnew.LoadBoard(out)
    assert pcbnew.ExportSpecctraDSN(board, dsn), "DSN export failed"
    assert os.path.exists(FREEROUTING), "no freerouting at " + FREEROUTING
    if os.path.exists(ses):
        os.remove(ses)
    subprocess.call(["java", "-jar", FREEROUTING, "-de", dsn, "-do", ses, "-mp", "40"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)
    assert os.path.exists(ses), "freerouting wrote no SES"
    assert pcbnew.ImportSpecctraSES(board, ses), "SES import failed"
    return board


def main():
    board, netobj = build()
    board = route(board)
    gnd = board.FindNet("GND")
    pour(board, gnd)
    out = os.path.join(G.HERE, G.NAME + ".kicad_pcb")
    pcbnew.SaveBoard(out, board)
    G.gen_pro()
    subprocess.call([KICAD_CLI, "pcb", "drc", "--refill-zones", "--save-board", "--schematic-parity", "--severity-all",
                     "-o", os.path.join(G.HERE, G.NAME + "-drc.rpt"), out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    G.gen_pro()
    n = sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_TRACK")
    v = sum(1 for t in board.GetTracks() if t.GetClass() == "PCB_VIA")
    print("routed: %d segments, %d vias; DRC report %s-drc.rpt" % (n, v, G.NAME))
