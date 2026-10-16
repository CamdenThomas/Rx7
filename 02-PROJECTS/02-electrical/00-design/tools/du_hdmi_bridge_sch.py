#!/usr/bin/env python3
"""du_hdmi_bridge_sch.py (was gen_bridge.py) - draws the display bridge board's KiCad project (work row Y46, D-550, part P119).

The Display Unit's BT817 board (ME817EV, P117) gives its picture as 24-bit parallel RGB on CN1, a
50-way 0.5 mm flat-cable connector; the 12.3-inch HannStar panel kit (P118) takes HDMI. This board
is the bridge between them: a TI TFP410 DVI transmitter, set by its pins (no I2C), a 50-way
connector for the flat cable, an HDMI socket, and a 3.3 V regulator from a 5 V input.

Owns (R6) nothing in the record; it is drawn FROM:
  parts      P119 (this board), P117 (the BT817 board), P118 (the panel kit)
  sources    S-500 (Bridgetek DS_ME817EV v1.1, Table 3-3: CN1's pins), TI SLDS145D (TFP410, rev. Feb 2024:
             Table 4-1 the pins, Table 6-1 the input modes, 5.3 RTFADJ 510 ohm)
and nothing here is measured (R11): the cable's length and twist, the panel kit's HDMI board and the
board's place in the Display Unit's case are not known.

The cable: CN1 on the ME817EV is bottom-contact. This board's J1 is a Hirose FH12-50S-0.5SH, also
bottom-contact, and the two are joined by a 50-way 0.5 mm flat cable with its contacts on the SAME
side at both ends (type A), the two connectors mouth to mouth. Conductor n then lands on J1 pin
51 - n, so J1 pin k carries CN1 pin 51 - k - the sheet's nets are named by CN1's own pin names.

Run with KiCad's own Python, from anywhere:
    <kicad python> du_hdmi_bridge_sch.py sch     writes the symbols, the sheet, the project, the lib tables
    <kicad python> du_hdmi_bridge_sch.py pcb     reads the netlist kicad-cli exports, places, routes (freerouting), pours
"""
import json
import os
import re
import sys
import uuid as uuidlib

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
from check import parse_sexpr, kid, val  # noqa: E402
import parts as layout  # noqa: E402  (the module; parts() below is the part list)

NAME = "du-hdmi-bridge"
HERE = layout.cad_dir(NAME)          # the KiCad project's folder: everything this writes goes there
KICAD_SYMS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
KICAD_FPS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
ROOT_UUID = "b5f0c3a2-7d41-4e6b-9c1f-2a8e5d3b7c90"
REV = "0.01"
DATE = "2026-10-13"
DS_TFP410 = "https://www.ti.com/lit/ds/symlink/tfp410.pdf"


def uid(seed):
    return str(uuidlib.uuid5(uuidlib.NAMESPACE_URL, "rx7/bridge-board/" + seed))


def block(text, start):
    depth, i, n, instr = 0, start, len(text), False
    while i < n:
        c = text[i]
        if instr:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                instr = False
        elif c == '"':
            instr = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise ValueError("unbalanced")


def lib_symbol(path, name):
    text = open(path, encoding="utf-8").read()
    m = re.search(r'\(symbol "%s"\s' % re.escape(name), text)
    if not m:
        raise KeyError(name)
    t = block(text, m.start())
    e = re.search(r'\(extends "([^"]+)"\)', t)
    if e:                                    # a derived symbol: the parent's body under this name
        base = lib_symbol(path, e.group(1))
        base = base.replace('(symbol "%s"' % e.group(1), '(symbol "%s"' % name, 1)
        base = base.replace('(symbol "%s_' % e.group(1), '(symbol "%s_' % name)
        base = re.sub(r'\(property "Value" "[^"]*"', '(property "Value" "%s"' % name, base, count=1)
        return base
    return t


# --------------------------------------------------------------------------------------------
# The TFP410 symbol (TI SLDS145D Table 4-1): a functional block, every pin passive
# --------------------------------------------------------------------------------------------
TFP_LEFT = ([("DATA%d" % i, str({23: 36, 22: 37, 21: 38, 20: 39, 19: 40, 18: 41, 17: 42, 16: 43, 15: 44, 14: 45,
                                  13: 46, 12: 47, 11: 50, 10: 51, 9: 52, 8: 53, 7: 54, 6: 55, 5: 58, 4: 59, 3: 60,
                                  2: 61, 1: 62, 0: 63}[i])) for i in range(23, -1, -1)]
            + [("IDCK+", "57"), ("IDCK-", "56"), ("DE", "2"), ("HSYNC", "4"), ("VSYNC", "5"),
               ("A3/DK3", "6"), ("CTL2/A2/DK2", "7"), ("CTL1/A1/DK1", "8")])
TFP_RIGHT = [("TX2+", "31"), ("TX2-", "30"), ("TX1+", "28"), ("TX1-", "27"), ("TX0+", "25"), ("TX0-", "24"),
             ("TXC+", "22"), ("TXC-", "21"), None, ("TFADJ", "19"), ("MSEN/PO1", "11"), None,
             ("ISEL/RST", "13"), ("BSEL/SCL", "15"), ("DSEL/SDA", "14"), ("EDGE/HTPLG", "9"), ("DKEN", "35"),
             ("VREF", "3"), ("PD", "10"), ("RESERVED", "34"), ("NC", "49")]
TFP_TOP = [("DVDD", "1"), ("DVDD", "12"), ("DVDD", "33"), ("PVDD", "18"), ("TVDD", "23"), ("TVDD", "29")]
TFP_BOTTOM = [("DGND", "16"), ("DGND", "48"), ("DGND", "64"), ("PGND", "17"), ("TGND", "20"), ("TGND", "26"),
              ("TGND", "32"), ("PAD", "65")]


def tfp410_symbol():
    def pin(name, num, x, y, ang):
        return ('\t\t\t(pin passive line (at %s %s %d) (length 2.54) (name "%s" (effects (font (size 1.27 1.27)))) '
                '(number "%s" (effects (font (size 1.27 1.27)))))' % (fmt(x), fmt(y), ang, name, num))
    P = []
    for i, (n, num) in enumerate(TFP_LEFT):
        P.append(pin(n, num, -20.32, 39.37 - i * 2.54, 0))
    for i, e in enumerate(TFP_RIGHT):
        if e:
            P.append(pin(e[0], e[1], 20.32, 39.37 - i * 2.54, 180))
    for i, (n, num) in enumerate(TFP_TOP):
        P.append(pin(n, num, -6.35 + i * 2.54, 45.72, 270))
    for i, (n, num) in enumerate(TFP_BOTTOM):
        P.append(pin(n, num, -8.89 + i * 2.54, -45.72, 90))
    return ('(symbol "TFP410"\n\t\t(pin_names (offset 1.016))\n\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n'
            '\t\t(property "Reference" "U" (at 0 46.99 0) (effects (font (size 1.27 1.27))))\n'
            '\t\t(property "Value" "TFP410" (at 0 -46.99 0) (effects (font (size 1.27 1.27))))\n'
            '\t\t(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            '\t\t(property "Datasheet" "%s" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            '\t\t(property "Description" "TI TFP410 PanelBus DVI transmitter, 64-pin HTQFP (PAP), pins from SLDS145D Table 4-1; pad 65 the exposed thermal pad, to ground" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            '\t\t(symbol "TFP410_0_1"\n\t\t\t(rectangle (start -17.78 43.18) (end 17.78 -43.18) (stroke (width 0.254) (type default)) (fill (type background)))\n\t\t)\n'
            '\t\t(symbol "TFP410_1_1"\n%s\n\t\t)\n\t)') % (DS_TFP410, "\n".join(P))


def symbols():
    out = {}
    for n in ("GND", "+3V3", "+5V", "PWR_FLAG"):
        out[n] = lib_symbol(KICAD_SYMS + "power.kicad_sym", n)
    for n in ("R", "C"):
        out[n] = lib_symbol(KICAD_SYMS + "Device.kicad_sym", n)
    for n in ("Conn_01x50", "Conn_01x02"):
        out[n] = lib_symbol(KICAD_SYMS + "Connector_Generic.kicad_sym", n)
    out["HDMI_A"] = lib_symbol(KICAD_SYMS + "Connector.kicad_sym", "HDMI_A")
    out["TestPoint"] = lib_symbol(KICAD_SYMS + "Connector.kicad_sym", "TestPoint")
    out["SolderJumper_2_Open"] = lib_symbol(KICAD_SYMS + "Jumper.kicad_sym", "SolderJumper_2_Open")
    out["AP2112K-3.3"] = lib_symbol(KICAD_SYMS + "Regulator_Linear.kicad_sym", "AP2112K-3.3")
    out["TFP410"] = tfp410_symbol()
    return out


def pins_of(symtext):
    tree = parse_sexpr(symtext)
    out = []

    def walk(node):
        for k in node[1:]:
            if not isinstance(k, list) or not k:
                continue
            if k[0] == "pin":
                at = kid(k, "at")
                out.append((val(k, "number"), val(k, "name"), float(at[1]), float(at[2]), int(float(at[3]))))
            elif k[0] == "symbol":
                walk(k)
    walk(tree)
    return out


# --------------------------------------------------------------------------------------------
# The parts and their nets
# --------------------------------------------------------------------------------------------
FP_R = "Resistor_SMD:R_0603_1608Metric"
FP_C = "Capacitor_SMD:C_0603_1608Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_JP = "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm"
FP_TP = "TestPoint:TestPoint_Pad_D1.0mm"

# CN1 of the ME817EV (S-500 Table 3-3): pin -> the net it carries here; None = left open
CN1 = {5: "GND", 36: "GND", 38: "GND", 48: "GND", 9: "DE", 10: "VS", 11: "HS", 37: "DCLK", 44: "DISP"}
for _i, _p in enumerate(range(12, 20)):
    CN1[_p] = "B%d" % (7 - _i)
for _i, _p in enumerate(range(20, 28)):
    CN1[_p] = "G%d" % (7 - _i)
for _i, _p in enumerate(range(28, 36)):
    CN1[_p] = "R%d" % (7 - _i)


def j1_nets():
    """J1 pin k carries CN1 pin 51 - k (type-A cable, connectors mouth to mouth)."""
    return {str(k): CN1.get(51 - k) for k in range(1, 51)}


def u1_nets():
    n = {}
    colour = {23: "R7", 22: "R6", 21: "R5", 20: "R4", 19: "R3", 18: "R2", 17: "R1", 16: "R0",
              15: "G7", 14: "G6", 13: "G5", 12: "G4", 11: "G3", 10: "G2", 9: "G1", 8: "G0",
              7: "B7", 6: "B6", 5: "B5", 4: "B4", 3: "B3", 2: "B2", 1: "B1", 0: "B0"}
    for name, num in TFP_LEFT:
        if name.startswith("DATA"):
            n[num] = colour[int(name[4:])]
    n.update({"57": "DCLK", "56": "GND", "2": "DE", "4": "HS", "5": "VS", "6": None, "7": None, "8": None,
              "31": "TMDS_D2_P", "30": "TMDS_D2_N", "28": "TMDS_D1_P", "27": "TMDS_D1_N",
              "25": "TMDS_D0_P", "24": "TMDS_D0_N", "22": "TMDS_CK_P", "21": "TMDS_CK_N",
              "19": "TFADJ", "11": "MSEN", "13": "GND", "15": "+3V3", "14": "GND", "9": "EDGE", "35": "GND",
              "3": "+3V3", "10": "PD", "34": "GND", "49": None})
    for _n, num in TFP_TOP:
        n[num] = "+3V3"
    for _n, num in TFP_BOTTOM:
        n[num] = "GND"
    return n


def parts():
    P = []
    P.append(("J1", "Conn_01x50", "FPC 50-way 0.5 mm, bottom contact - from the BT817 board's CN1",
              "Connector_FFC-FPC:Hirose_FH12-50S-0.5SH_1x50-1MP_P0.50mm_Horizontal", (40.64, 50.8), j1_nets(),
              "Hirose FH12-50S-0.5SH(55), bottom contact; pin k carries ME817EV CN1 pin 51-k through a 50-way 0.5 mm "
              "flat cable with contacts on the same side (type A), the connectors mouth to mouth - confirm the cable "
              "and continuity of a ground pin before power"))
    P.append(("U1", "TFP410", "TFP410PAP", "Package_QFP:Texas_TQFP-64-1EP_10x10mm_P0.5mm_EP8x8mm_Mask4.44x4.44mm",
              (121.92, 83.82), u1_nets(),
              "TI TFP410PAP (SLDS145D): 24-bit single-edge, 3.3 V CMOS inputs (VREF = DVDD, BSEL high), I2C off "
              "(ISEL low); the footprint is KiCad's TI TQFP-64 with an 8 x 8 pad - confirm against TI's PAP drawing"))
    P.append(("J2", "HDMI_A", "HDMI type A receptacle - to the panel kit's driver board",
              "Connector_Video:HDMI_A_Molex_208658-1001_Horizontal", (205.74, 83.82),
              {"1": "TMDS_D2_P", "2": "GND", "3": "TMDS_D2_N", "4": "TMDS_D1_P", "5": "GND", "6": "TMDS_D1_N",
               "7": "TMDS_D0_P", "8": "GND", "9": "TMDS_D0_N", "10": "TMDS_CK_P", "11": "GND", "12": "TMDS_CK_N",
               "13": None, "14": None, "15": None, "16": None, "17": "GND", "18": "+5V", "19": "HPD", "SH": "GND"},
              "Molex 2086581001, horizontal; DVI over HDMI, no DDC (the source reads no EDID) - confirm the part against Molex's drawing"))
    P.append(("J3", "Conn_01x02", "5 V in, JST XH 2-way", "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
              (40.64, 147.32), {"1": "+5V", "2": "GND"},
              "5 V for the bridge and the HDMI 5 V pin: about 0.2 A; from the Display Unit's +5V - where it comes from is not drawn yet, confirm"))
    P.append(("U2", "AP2112K-3.3", "AP2112K-3.3TRG1", "Package_TO_SOT_SMD:SOT-23-5", (81.28, 147.32),
              {"1": "+5V", "2": "GND", "3": "+5V", "4": None, "5": "+3V3"},
              "Diodes Inc AP2112K-3.3, 600 mA LDO, 1 uF in and out (its sheet); the TFP410 takes about 0.1 A - confirm"))
    P.append(("C1", "C", "1uF", FP_C, (66.04, 160.02), {"1": "+5V", "2": "GND"}, "X7R 10 V - the LDO's input"))
    P.append(("C2", "C", "10uF", FP_C0805, (96.52, 160.02), {"1": "+3V3", "2": "GND"}, "X7R 10 V - the LDO's output and the 3.3 V bulk"))
    for i, pinname in enumerate(("DVDD 1", "DVDD 12", "DVDD 33", "PVDD 18", "TVDD 23", "TVDD 29")):
        P.append(("C%d" % (3 + i), "C", "100nF", FP_C, (101.6 + i * 7.62, 33.02), {"1": "+3V3", "2": "GND"},
                  "X7R - at TFP410 pin %s" % pinname))
    P.append(("C9", "C", "1uF", FP_C, (190.5, 132.08), {"1": "+5V", "2": "GND"}, "X7R 10 V - at the HDMI 5 V pin"))
    P.append(("R1", "R", "510R", FP_R, (167.64, 116.84), {"1": "+3V3", "2": "TFADJ"},
              "RTFADJ 510 ohm 1 %: DVI swing 400-600 mV (SLDS145D 5.3)"))
    P.append(("R2", "R", "4.7k", FP_R, (167.64, 132.08), {"1": "+3V3", "2": "MSEN"},
              "MSEN's pull-up: the sheet asks 5 k to VDD; 4.7 k - confirm"))
    P.append(("R3", "R", "10k", FP_R, (167.64, 147.32), {"1": "+3V3", "2": "PD"},
              "holds PD high: the transmitter on whenever it has power"))
    P.append(("R4", "R", "10k", FP_R, (167.64, 162.56), {"1": "+3V3", "2": "EDGE"},
              "EDGE high: data latched on the clock's rising edge"))
    P.append(("JP1", "SolderJumper_2_Open", "EDGE to GND: falling edge", FP_JP, (182.88, 162.56),
              {"1": "EDGE", "2": "GND"},
              "closed only if the BT817's REG_PCLK_POL is set to the falling edge - open as made"))
    P.append(("JP2", "SolderJumper_2_Open", "PD from DISP", FP_JP, (182.88, 147.32), {"1": "PD", "2": "DISP"},
              "closed lets the BT817's DISP line power the transmitter down with the screen - open as made"))
    P.append(("TP1", "TestPoint", "DISP", FP_TP, (40.64, 30.48), {"1": "DISP"}, "the BT817's DISP line"))
    P.append(("TP2", "TestPoint", "MSEN", FP_TP, (182.88, 132.08), {"1": "MSEN"}, "high = a powered receiver on the HDMI lead"))
    P.append(("TP3", "TestPoint", "HPD", FP_TP, (190.5, 116.84), {"1": "HPD"}, "the HDMI hot-plug line from the panel's board"))
    return P


POWER = {"GND", "+3V3", "+5V"}


def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def sch_text():
    syms = symbols()
    pins = {n: pins_of(t) for n, t in syms.items()}
    o = ['(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")',
         '\t(uuid "%s")\n\t(paper "A3")' % ROOT_UUID,
         '''	(title_block
		(title "Display bridge board - the BT817 board's RGB to HDMI (P119, D-550)")
		(date "%s")
		(rev "%s")
		(company "RX-7 FB electrical build")
		(comment 1 "From S-500 (ME817EV CN1) and TI SLDS145D (TFP410). J1 pin k = CN1 pin 51-k (type-A cable, mouth to mouth).")
		(comment 2 "TFP410 by pins: ISEL low, BSEL high (24-bit), VREF = DVDD (3.3 V CMOS), EDGE high (rising; JP1 for falling), DKEN low.")
		(comment 3 "DVI on an HDMI socket: no DDC; +5V on pin 18 for the sink. Power: 5 V on J3, AP2112K-3.3 for the TFP410.")
		(comment 4 "R11: nothing here has been measured or bought. Rev %s (Y46).")
	)''' % (DATE, REV, REV),
         "\t(lib_symbols"]
    for n, t in syms.items():
        o.append("\t\t" + t.replace('(symbol "%s"' % n, '(symbol "%s:%s"' % (NAME, n), 1))
    o.append("\t)")
    count = {"pwr": 0, "flg": 0}

    def power_sym(kind, x, y, d=(0, 1)):
        if kind == "PWR_FLAG":
            count["flg"] += 1
            ref = "#FLG%02d" % count["flg"]
            rot, vx, vy = 0, x, y - 4.5
        else:
            count["pwr"] += 1
            ref = "#PWR%03d" % count["pwr"]
            up = {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}
            down = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}
            rot = (down if kind == "GND" else up)[d]
            vx, vy = x + d[0] * 6.0, y + d[1] * 4.5 + (0.6 if d[1] == 0 else 0)
        return ('\t(symbol (lib_id "%s:%s") (at %s %s %d) (unit 1) (body_style 1)\n'
                '\t\t(exclude_from_sim no) (in_bom no) (on_board yes) (in_pos_files yes) (dnp no)\n'
                '\t\t(uuid "%s")\n'
                '\t\t(property "Reference" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
                '\t\t(property "Value" "%s" (at %s %s 0) (effects (font (size 1.1 1.1))))\n'
                '\t\t(property "Footprint" "" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
                '\t\t(property "Datasheet" "" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
                '\t\t(pin "1" (uuid "%s"))\n'
                '\t\t(instances (project "%s" (path "/%s" (reference "%s") (unit 1))))\n\t)') % (
            NAME, kind, fmt(x), fmt(y), rot, uid(ref), ref, fmt(x), fmt(y), kind, fmt(vx), fmt(vy),
            fmt(x), fmt(y), fmt(x), fmt(y), uid(ref + "p1"), NAME, ROOT_UUID, ref)

    def label(net, x, y, d):
        ang, just = {(-1, 0): (180, "right bottom"), (1, 0): (0, "left bottom"),
                     (0, -1): (90, "left bottom"), (0, 1): (270, "right bottom")}[d]
        return '\t(label "%s" (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))' % (
            net, fmt(x), fmt(y), ang, just, uid("lbl%s%s%s" % (net, x, y)))

    def wire(x1, y1, x2, y2):
        return '\t(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid "%s"))' % (
            fmt(x1), fmt(y1), fmt(x2), fmt(y2), uid("w%s%s%s%s" % (x1, y1, x2, y2)))

    for ref, sym, value, fp, (X, Y), nets, confirm in parts():
        plist = pins[sym]
        o.append('\t(symbol (lib_id "%s:%s") (at %s %s 0) (unit 1) (body_style 1)' % (NAME, sym, fmt(X), fmt(Y)))
        o.append('\t\t(exclude_from_sim no) (in_bom %s) (on_board yes) (in_pos_files yes) (dnp no)' % ('no' if sym in ('TestPoint', 'SolderJumper_2_Open') else 'yes'))
        o.append('\t\t(uuid "%s")' % uid("sym" + ref))
        ys = [Y - p[3] for p in plist]
        xs = [X + p[2] for p in plist]
        top, bot = min(ys), max(ys)
        rx, ry, vx_, vy_ = X, top - 3.81, X, bot + 3.81
        if sym in ("TFP410", "Conn_01x50"):
            rx, ry, vx_, vy_ = X, top - 6.35, X, bot + 6.35
        o.append('\t\t(property "Reference" "%s" (at %s %s 0) (effects (font (size 1.27 1.27))))' % (ref, fmt(rx), fmt(ry)))
        o.append('\t\t(property "Value" "%s" (at %s %s 0) (effects (font (size 1.1 1.1))))' % (value, fmt(vx_), fmt(vy_)))
        o.append('\t\t(property "Footprint" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (fp, fmt(X), fmt(Y)))
        ds = DS_TFP410 if ref == "U1" else ""
        o.append('\t\t(property "Datasheet" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (ds, fmt(X), fmt(Y)))
        o.append('\t\t(property "Confirm" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (confirm, fmt(X), fmt(Y)))
        for num, _n, _x, _y, _a in plist:
            o.append('\t\t(pin "%s" (uuid "%s"))' % (num, uid("pin%s.%s" % (ref, num))))
        o.append('\t\t(instances (project "%s" (path "/%s" (reference "%s") (unit 1))))\n\t)' % (NAME, ROOT_UUID, ref))
        done = set()
        for num, _name, px, py, ang in plist:
            sx, sy = X + px, Y - py
            if (sx, sy) in done:
                continue
            done.add((sx, sy))
            net = nets.get(num, "MISSING")
            if net == "MISSING":
                raise KeyError("%s pin %s has no net in parts()" % (ref, num))
            if net is None:
                o.append('\t(no_connect (at %s %s) (uuid "%s"))' % (fmt(sx), fmt(sy), uid("nc%s%s" % (ref, num))))
                continue
            body = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[ang]
            d = (-body[0], -body[1])
            ex, ey = sx + d[0] * 2.54, sy + d[1] * 2.54
            o.append(wire(sx, sy, ex, ey))
            if net in POWER:
                o.append(power_sym(net, ex, ey, d))
            else:
                o.append(label(net, ex, ey, d))
    for i, net in enumerate(("GND", "+5V")):          # +3V3 is driven by U2's output pin
        x, y = 40.64 + i * 15.24, 172.72
        o.append(wire(x, y, x, y + 5.08))
        o.append(power_sym("PWR_FLAG", x, y))
        o.append(power_sym(net, x, y + 5.08, (0, 1)))
    notes = [
        (12.7, 17.78, 2.0, True, "J1 - FROM THE BT817 BOARD'S CN1 (ME817EV, S-500 Table 3-3)"),
        (12.7, 22.86, 1.5, False, "J1 pin k = CN1 pin 51-k: a 50-way 0.5 mm FFC, contacts on the same side (type A), the two bottom-contact connectors mouth to mouth."),
        (12.7, 26.67, 1.5, False, "Nets named by CN1: R7-R0 = CN1 28-35, G7-G0 = 20-27, B7-B0 = 12-19, DE 9, VS 10, HS 11, DCLK 37, DISP 44, GND 5 / 36 / 38 / 48. LEDA / LEDK, DVDD, VCOM, VGH / VGL / AVDD left open."),
        (91.44, 17.78, 2.0, True, "U1 - TFP410, SET BY ITS PINS (TI SLDS145D)"),
        (91.44, 22.86, 1.5, False, "ISEL low (no I2C), BSEL high (24-bit single edge), VREF = DVDD (3.3 V CMOS), DKEN low, EDGE high = rising edge (JP1 closed = falling)."),
        (91.44, 26.67, 1.5, False, "DATA[23:16] red, [15:8] green, [7:0] blue (Table 6-2); IDCK+ the clock, IDCK- to ground (single-ended); TFADJ 510 ohm to TVDD."),
        (167.64, 60.96, 2.0, True, "J2 - DVI ON AN HDMI SOCKET"),
        (167.64, 66.04, 1.5, False, "TMDS straight to the socket, the sink terminates (DC-coupled). No DDC: SCL / SDA / CEC open. +5V on pin 18, HPD to TP3."),
        (12.7, 134.62, 2.0, True, "POWER: 5 V ON J3, 3.3 V FROM U2"),
        (12.7, 139.7, 1.5, False, "About 0.1 A at 3.3 V for the TFP410 at a 100 MHz pixel clock; where the 5 V comes from in the Display Unit is not drawn yet (confirm)."),
    ]
    for x, y, sz, bold, t in notes:
        o.append('\t(text "%s" (exclude_from_sim no) (at %s %s 0) (effects (font (size %s %s)%s) (justify left top)) (uuid "%s"))' % (
            t, fmt(x), fmt(y), sz, sz, " (bold yes)" if bold else "", uid("txt" + t[:40])))
    o.append('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
    return "\n".join(o)


def sym_lib_text():
    body = "\n".join("\t" + t for t in symbols().values())
    return '(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "kicad_symbol_editor")\n\t(generator_version "10.0")\n%s\n)\n' % body


def write(path, text):
    with open(os.path.join(HERE, path), "w", encoding="utf-8") as f:
        f.write(text)


def gen_pro():
    """The panel's project file, its rules kept, renamed; net classes Default (0.2 mm) and PWR (0.4 mm)."""
    pro = json.load(open(layout.board_file("cu-face-board", "kicad_pro"), encoding="utf-8"))
    pro["meta"]["filename"] = NAME + ".kicad_pro"
    classes = [c for c in pro["net_settings"]["classes"] if c["name"] == "Default"]
    d = dict(classes[0])
    d["track_width"] = 0.2
    d["clearance"] = 0.15
    pwr = dict(d)
    pwr["name"] = "PWR"
    pwr["track_width"] = 0.25
    pwr["clearance"] = 0.15
    tmds = dict(d)
    tmds["name"] = "TMDS"
    tmds["track_width"] = 0.25
    tmds["clearance"] = 0.15
    pro["net_settings"]["classes"] = [d, pwr, tmds]
    pro["net_settings"]["netclass_patterns"] = (
        [{"netclass": "PWR", "pattern": p} for p in ("+3V3", "+5V")]
        + [{"netclass": "TMDS", "pattern": "TMDS_*"}])
    pro["schematic"]["top_level_sheets"] = [{"filename": NAME + ".kicad_sch", "name": NAME, "uuid": ROOT_UUID}]
    pro["schematic"]["used_designators"] = ""
    pro["sheets"] = [[ROOT_UUID, NAME]]
    pro["board"]["design_settings"]["drc_exclusions"] = []
    rules = pro["board"]["design_settings"]["rules"]
    rules["min_clearance"] = 0.15
    rules["min_track_width"] = 0.15
    with open(os.path.join(HERE, NAME + ".kicad_pro"), "w", encoding="utf-8") as f:
        json.dump(pro, f, indent=2)
        f.write("\n")


def gen_sch():
    write(NAME + ".kicad_sym", sym_lib_text())
    write(NAME + ".kicad_sch", sch_text())
    write("sym-lib-table", '(sym_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.kicad_sym")(options "")(descr "Every symbol this schematic uses, kept with the project"))\n)\n' % (NAME, NAME))
    gen_pro()


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "sch"
    if what == "sch":
        gen_sch()
    elif what == "pro":
        gen_pro()
    elif what == "pcb":
        import du_hdmi_bridge_pcb
        du_hdmi_bridge_pcb.main()
    else:
        print(__doc__)
        sys.exit(3)
