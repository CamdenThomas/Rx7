#!/usr/bin/env python3
"""gen_left_plate.py - draws the left plate's KiCad project (work rows Y21 and Y22, D-492, D-499).

Owns (R6) nothing in the record; it is drawn FROM these rows of ../../../../data/ and must follow them:
  cavities   DP-DCU-E 1-12   - J1 pin n is cavity n, net named as the panel_ribbon line its src_note names
             L3-S1 9, 10, 11 - the wink lead: J2 pins 1-3, the commons on pin 4 to dash ground (DV24, G20)
  panel_ribbon 1, 3, 7, 8, 17-22, 24, 26 - the net names
  parts      P204 (the winks, SPDT under lit caps - placeholder footprint), P156 (the stick, placeholder),
             P198, P199, P200
  devices    DV24 (the winks' lines and their 18 k / 33 k ladder resistors, on this board since D-499), DV62
and the DCU firmware's plate channel map (../../firmware/dcu/lights.h): OUT1 wink L, OUT2 wink R,
OUT3 hatch, OUT4 fuel door, OUT5 mirror. Positions are the sketch's plate (../../../panel-concept.html,
plate(): 100 x 56, keys 17 x 15 at (20,19) (39,19) (20,37) (39,37), the stick at (74.5, 28) in a
14 mm-radius well). Nothing here is measured (R11).

Run with KiCad's own Python (pcbnew), from anywhere:
    <kicad python> gen_left_plate.py sch      writes the symbols, the sheet, the footprints, the lib tables
    <kicad python> gen_left_plate.py pcb      reads the netlist kicad-cli exports, places, routes, pours
    <kicad python> gen_left_plate.py pro      (re)writes left-plate.kicad_pro from the panel's rules
FLIP = True draws the sketch's 'flip': the stick on the door side, the four keys on the wheel side.
"""
import json
import math
import os
import re
import subprocess
import sys
import uuid as uuidlib

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(CAD)), "tools"))  # 00-design/tools: check.py
from check import parse_sexpr, kids, kid, val  # noqa: E402

NAME = "left-plate"
FLIP = False                     # the sketch's default: the stick on the steering-wheel side
KICAD_SYMS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
KICAD_FPS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
PANEL_SYM = os.path.join(CAD, "panel", "panel.kicad_sym")
ROOT_UUID = "6c1e7a52-3f0d-4b8e-9a2c-1d5e0f7b2a21"     # fixed so re-runs keep the footprint links
REV = "0.02"
DATE = "2026-10-13"


def uid(seed):
    return str(uuidlib.uuid5(uuidlib.NAMESPACE_URL, "rx7/left-plate/" + seed))


# ============================================================================================
# The geometry: millimetres from the plate's top-left corner seen from the front (the driver's
# side of the board is F.Cu), x toward the steering wheel, y down. The sketch's plate().
# ============================================================================================
W, H = 100.0, 56.0
CORNER_R = 3.0
HOLES = [(4, 4), (96, 4), (4, 52), (96, 52)]
K1 = 59.0 if FLIP else 20.0      # first key column (the sketch: k1 = flip ? 610 : 200, /10)
K2 = K1 + 19.0
WINK_Y, KEY_Y = 19.0, 37.0       # the sketch's two key rows: the winks above, the releases below
STICK = (25.5 if FLIP else 74.5, 28.0)
WELL_R = 14.0
KEY_LED_DX = 5.75                # a key's symbol LED inside its 17 x 15 cap, beside the 6 x 6 switch
WINK_LED_DX = 7.0                # a wink's LED inside its cap, beside the 12 mm placeholder body (confirm)
WINK_BODY = 12.0                 # the P204 placeholder's body square (confirm: no part chosen)
J1_X = 6.5 if FLIP else 94.5     # J1's odd-pin column, on the back, at the edge nearest the climate unit
J2_X, J2_Y = (5.0 if FLIP else 95.0), 44.0   # J2, the wink lead's header: pin 1, on the back, its row
                                 # along the bottom of J1's shroud on the same edge, clear of it and of H4
                                 # (confirm: the lead's run to the dash post is not measured)


# ============================================================================================
# Symbols
# ============================================================================================
def block(text, start):
    """The balanced s-expression starting at text[start] == '('."""
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
    return block(text, m.start())


THUMBSTICK = '''(symbol "THUMBSTICK_2AXIS_SW"
		(pin_names (offset 1.016))
		(exclude_from_sim no) (in_bom yes) (on_board yes)
		(property "Reference" "JS" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
		(property "Value" "THUMBSTICK_2AXIS_SW" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Description" "Two-axis analog thumbstick with push (P156, ALPS RKJXV class): two pots and a normally-open push. Functional block - pin numbers are the placeholder footprint's, not a part's" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(symbol "THUMBSTICK_2AXIS_SW_0_1"
			(rectangle (start -10.16 7.62) (end 10.16 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))
		)
		(symbol "THUMBSTICK_2AXIS_SW_1_1"
			(pin passive line (at -12.7 5.08 0) (length 2.54) (name "X_VCC" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -12.7 2.54 0) (length 2.54) (name "X_WIPER" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -12.7 0 0) (length 2.54) (name "X_GND" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -12.7 -2.54 0) (length 2.54) (name "Y_VCC" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 12.7 5.08 180) (length 2.54) (name "Y_WIPER" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 12.7 2.54 180) (length 2.54) (name "Y_GND" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 12.7 0 180) (length 2.54) (name "SW_A" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 12.7 -2.54 180) (length 2.54) (name "SW_B" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
		)
	)'''


def symbols():
    """name -> library text (unprefixed), every symbol the sheet uses."""
    out = {}
    for n in ("GND", "+3V3", "PWR_FLAG", "Conn_02x06", "Conn_01x04", "SW_Push", "D", "LED", "R", "C"):
        out[n] = lib_symbol(PANEL_SYM, n)
    out["IS31FL3218-QF"] = lib_symbol(KICAD_SYMS + "Driver_LED.kicad_sym", "IS31FL3218-QF")
    # KiCad's SPDT momentary: pin 1 A = the contact the pole rests on (NC), 2 B = common, 3 C = NO
    out["SW_Push_SPDT"] = lib_symbol(KICAD_SYMS + "Switch.kicad_sym", "SW_Push_SPDT")
    out["THUMBSTICK_2AXIS_SW"] = THUMBSTICK
    return out


def pins_of(symtext):
    """[(number, name, x, y, angle)] in library coordinates (y up)."""
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


# ============================================================================================
# The sheet
# ============================================================================================
# (ref, symbol, value, footprint, (x, y), {pin number: net or "GND"/"+3V3" power or None = no-connect}, confirm)
FP_LED = "LED_SMD:LED_0603_1608Metric"
FP_R = "Resistor_SMD:R_0603_1608Metric"
FP_C = "Capacitor_SMD:C_0603_1608Metric"
FP_WINK = "left-plate:WinkSwitch_P204_SPDT_Placeholder"
FP_J2 = "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
DS_3218 = "https://www.lumissil.com/assets/pdf/core/IS31FL3218_DS.pdf"

# DP-DCU-E cavity n on J1 pin n (cavities.csv src_note -> panel_ribbon signal)
J1_NETS = {"1": "ROW1", "2": "COL2", "3": "COL3", "4": "JOY_X", "5": "JOY_Y", "6": "JOY_PRESS",
           "7": "+3V3", "8": "AGND", "9": "PNL_SDA", "10": "PNL_SCL", "11": "GND", "12": "+5V_PNL"}

# the wink lead (DV24, D-499): J2 pin n -> the L3-S1 cavity at the dash post, the commons on pin 4
J2_NETS = {"1": "WINK_L_NC", "2": "WINK_R_NC", "3": "WINK_REQ", "4": "WINK_COM"}
J2_CAVS = {"1": "L3-S1 9", "2": "L3-S1 10", "3": "L3-S1 11", "4": "dash ground (G20)"}
WINK_R_OHMS = {"L": "18k", "R": "33k"}       # L3-S1 11: wink L NO through 18 k, wink R NO through 33 k

# the plate's channel map, the firmware's (lights.h LQ_*): OUTn -> (LED ref, what it lights)
CHANNELS = [(1, "LED1", "wink left face", "LED_WINK_L"),
            (2, "LED2", "wink right face", "LED_WINK_R"),
            (3, "LED3", "hatch release symbol", "LED_HATCH"),
            (4, "LED4", "fuel-door release symbol", "LED_FUEL"),
            (5, "LED5", "mirror stick symbol", "LED_MIRROR")]


def parts():
    P = []
    P.append(("J1", "Conn_02x06", "plate cable header 2x6 shrouded (DP-DCU-E 1-12, P200)",
              "Connector_IDC:IDC-Header_2x06_P2.54mm_Vertical", (60.96, 71.12), dict(J1_NETS),
              "the cable's plate end (P200): pin n = DP-DCU-E n; IDC or crimp 2 x 6, length about 1 m - confirm"))
    P.append(("SW1", "SW_Push", "key - hatch", "Button_Switch_THT:SW_PUSH_6mm", (152.4, 50.8),
              {"1": "COL2", "2": "KEY_HATCH"},
              "6 x 6 mm THT tactile under the faceplate's 17 x 15 cap (P199, luxury D-488); actuator height against the cap - confirm"))
    P.append(("D1", "D", "1N4148W", "Diode_SMD:D_SOD-123", (195.58, 50.8), {"2": "KEY_HATCH", "1": "ROW1"},
              "part number - confirm (P199)"))
    P.append(("SW2", "SW_Push", "key - fuel door", "Button_Switch_THT:SW_PUSH_6mm", (152.4, 63.5),
              {"1": "COL3", "2": "KEY_FUEL"},
              "6 x 6 mm THT tactile under the faceplate's 17 x 15 cap (P199, luxury D-488); actuator height against the cap - confirm"))
    P.append(("D2", "D", "1N4148W", "Diode_SMD:D_SOD-123", (195.58, 63.5), {"2": "KEY_FUEL", "1": "ROW1"},
              "part number - confirm (P199)"))
    P.append(("JS1", "THUMBSTICK_2AXIS_SW", "mirror stick (P156) - placeholder",
              "left-plate:Thumbstick_P156_Placeholder_2x04_P2.54mm", (165.1, 101.6),
              {"1": "+3V3", "2": "JOY_X", "3": "AGND", "4": "+3V3", "5": "JOY_Y", "6": "AGND",
               "7": "JOY_PRESS", "8": "GND"},
              "no part chosen (P156): ALPS RKJXV class, 2-axis with push; footprint, pins, body and well from the part's drawing - confirm"))
    U = {"5": "PNL_SDA", "6": "PNL_SCL", "24": "LED_SDB", "2": "LED_REXT", "3": "+5V_PNL", "4": "GND", "25": "GND"}
    for out_n in range(1, 19):
        pin = str(out_n + 6) if out_n <= 17 else "1"
        U[pin] = None
    for out_n, ref, what, net in CHANNELS:
        U[str(out_n + 6)] = net
    P.append(("U1", "IS31FL3218-QF", "IS31FL3218-QFLS2-TR", "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
              (279.4, 83.82), U,
              "the plate's LED driver (P199): fixed I2C address 0x54; VCC 2.7-5.5 V on +5V_PNL, VIH 1.4 V so the 3.3 V bus reads (Lumissil Rev G p.4); footprint KiCad's QFN-24 4x4 - confirm against the package drawing"))
    P.append(("C1", "C", "1uF", FP_C, (238.76, 50.8), {"1": "+5V_PNL", "2": "GND"}, "X7R 10 V or more - confirm"))
    P.append(("C2", "C", "100nF", FP_C, (238.76, 60.96), {"1": "+5V_PNL", "2": "GND"}, "X7R - confirm"))
    P.append(("R1", "R", "10k", FP_R, (238.76, 101.6), {"1": "LED_REXT", "2": "GND"},
              "R_EXT: IMAX = 58.5 x 1.3 V / 10k = 7.6 mA a channel (Lumissil p.10), the panel's D-458 current - 1 %"))
    P.append(("R2", "R", "100k", FP_R, (238.76, 111.76), {"1": "+5V_PNL", "2": "LED_SDB"},
              "holds SDB high: the driver is on and blank until written, as the panel's U2 - confirm"))
    for i, (out_n, ref, what, net) in enumerate(CHANNELS):
        P.append((ref, "LED", "LED 0603 - %s (OUT%d)" % (what, out_n), FP_LED, (342.9, 58.42 + i * 12.7),
                  {"2": "+5V_PNL", "1": net},
                  "colour, brightness and part number - confirm (I-006: the wink faces green; the rest LP20's)"))
    # the winks (D-499): SPDT momentary under lit caps, the ladder resistors beside them, the lead on J2
    for side, ref, rref, y in (("L", "SW3", "R3", 177.8), ("R", "SW4", "R4", 203.2)):
        name = "left" if side == "L" else "right"
        P.append((ref, "SW_Push_SPDT", "wink - %s (P204)" % name, FP_WINK, (60.96, y),
                  {"1": "WINK_%s_NC" % side, "2": "WINK_COM", "3": "WINK_%s_NO" % side},
                  "P204: board-mount SPDT momentary under a lit 17 x 15 cap, C&K 8125 class - no part chosen; the placeholder footprint's pins (1 NC, 2 COM, 3 NO) and body from the part's drawing - confirm"))
        P.append((rref, "R", WINK_R_OHMS[side], FP_R, (111.76, y), {"1": "WINK_%s_NO" % side, "2": "WINK_REQ"},
                  "the wink %s ladder resistor (DV24, L3-S1 11), on the plate since D-499 - 1 %%" % name))
    P.append(("J2", "Conn_01x04", "wink lead header 1x4 (L3-S1 9 / 10 / 11, commons)", FP_J2, (165.1, 190.5),
              dict(J2_NETS),
              "the wink lead's plate end (DV24, D-499): pin 1 = L3-S1 9, 2 = L3-S1 10, 3 = L3-S1 11, 4 = the commons to dash ground (G20); JST XH 4-way, locking - housing and crimps confirm, the lead's run to the dash post not measured"))
    return P


POWER = {"GND", "+3V3"}


def fmt(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def sch_text():
    syms = symbols()
    pins = {n: pins_of(t) for n, t in syms.items()}
    o = []
    o.append('(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")')
    o.append('\t(uuid "%s")\n\t(paper "A3")' % ROOT_UUID)
    o.append('''	(title_block
		(title "Left plate - the panel's second face, left of the steering wheel (D-492, D-499)")
		(date "%s")
		(rev "%s")
		(company "RX-7 FB electrical build")
		(comment 1 "From the record: DP-DCU-E 1-12, L3-S1 9-11, panel_ribbon, DV24 / DV62, P156 P198-P200 P204. The row wins.")
		(comment 2 "J1 pin n = DP-DCU-E n; keys on ROW1 via 1N4148W; stick on 17-20; IS31FL3218 at 0x54.")
		(comment 3 "The winks (P204, D-499): SPDT under lit caps, 18k / 33k on the board, the lead on J2 to the dash post (L3-S1 9 / 10 / 11).")
		(comment 4 "R11: nothing here has been measured or bought. Rev %s (Y22).")
	)''' % (DATE, REV, REV))
    o.append("\t(lib_symbols")
    for n, t in syms.items():
        t = t.replace('(symbol "%s"' % n, '(symbol "%s:%s"' % (NAME, n), 1)
        o.append("\t\t" + t)
    o.append("\t)")
    pwr = [0]
    flg = [0]

    def power_sym(kind, x, y, d=(0, 1)):
        if kind == "PWR_FLAG":
            flg[0] += 1
            ref = "#FLG%02d" % flg[0]
        else:
            pwr[0] += 1
            ref = "#PWR%03d" % pwr[0]
        if kind == "PWR_FLAG":
            rot, vx, vy = 0, x, y - 4.5
        else:
            # turn the symbol so its graphic points along the stub, away from the part
            rot = {"GND": {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270},
                   "+3V3": {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}}[kind][d]
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
        o.append('\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)')
        o.append('\t\t(uuid "%s")' % uid("sym" + ref))
        ys = [Y - p[3] for p in plist]
        top, bot = min(ys), max(ys)
        rx, ry, vx_, vy_ = X, top - 3.81, X, bot + 3.81
        if ref == "U1":                         # clear of the VCC stub above and GND below
            rx, ry, vx_, vy_ = X - 7.62, top + 1.27, X + 10.16, bot + 8.89
        o.append('\t\t(property "Reference" "%s" (at %s %s 0) (effects (font (size 1.27 1.27))))' % (ref, fmt(rx), fmt(ry)))
        o.append('\t\t(property "Value" "%s" (at %s %s 0) (effects (font (size 1.1 1.1))))' % (value, fmt(vx_), fmt(vy_)))
        o.append('\t\t(property "Footprint" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (fp, fmt(X), fmt(Y)))
        ds = DS_3218 if ref == "U1" else ""
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
            body = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[ang]   # toward the body, sheet coords
            d = (-body[0], -body[1])
            ex, ey = sx + d[0] * 2.54, sy + d[1] * 2.54
            o.append(wire(sx, sy, ex, ey))
            if net in POWER:
                o.append(power_sym(net, ex, ey, d))
            else:
                o.append(label(net, ex, ey, d))
    # the power flags: the rails reach this board only through J1, a passive pin
    fx = 60.96
    for i, net in enumerate(("GND", "+3V3", "+5V_PNL")):
        x = fx + i * 15.24
        y = 121.92
        o.append(wire(x, y, x, y + 5.08))
        o.append(power_sym("PWR_FLAG", x, y))
        if net in POWER:
            o.append(power_sym(net, x, y + 5.08))
        else:
            o.append(label(net, x, y + 5.08, (0, 1)))
    notes = [
        (25.4, 25.4, 2.0, True, "J1 - THE CABLE TO DP-DCU-E (P200)"),
        (25.4, 30.48, 1.5, False, "pin n = cavity n, on the net its panel_ribbon line names"),
        (139.7, 25.4, 2.0, True, "THE KEYS (matrix, D-492)"),
        (139.7, 34.29, 1.5, False, "ROW1 -> 1N4148W K..A -> key -> column"),
        (139.7, 30.48, 1.5, False, "hatch COL2 (DP-DCU-E 2), fuel door COL3 (DP-DCU-E 3)"),
        (139.7, 81.28, 2.0, True, "THE MIRROR STICK (P156, placeholder - no part chosen)"),
        (139.7, 86.36, 1.5, False, "pots across +3V3 / AGND (D-380: its own return), wipers JOY_X / JOY_Y, the push JOY_PRESS to GND (panel_ribbon 19)"),
        (228.6, 25.4, 2.0, True, "THE LIGHTS: IS31FL3218 at 0x54, five symbols at 7.6 mA"),
        (228.6, 30.48, 1.5, False, "OUT1 wink L face, OUT2 wink R face, OUT3 hatch, OUT4 fuel door, OUT5 mirror stick - the DCU firmware's map (lights.h, F-018)"),
        (228.6, 34.29, 1.5, False, "OUT6-OUT18 open. The bus pull-ups are on the carrier (R51 / R52, 4.7k to +3V3); none here."),
        (25.4, 152.4, 2.0, True, "THE WINK SWITCHES (P204, D-499) AND THEIR LEAD J2 TO THE DASH POST"),
        (25.4, 157.48, 1.5, False, "Two SPDT momentary pushbuttons under lit caps (the faces are LED1 / LED2 on the driver). Their lines are the harness's (DV24, D-189, D-482), unchanged:"),
        (25.4, 161.29, 1.5, False, "NC poles to L3-S1 9 / 10 (J2 pins 1 / 2), NO poles through 18k / 33k joined as WINK_REQ to L3-S1 11 (J2 pin 3), the commons to dash ground (J2 pin 4, G20)."),
        (25.4, 165.1, 1.5, False, "WINK_COM is NOT this board's GND: the winks return to the dash post as today, the plate's electronics on DP-DCU-E 8 and 11 (DV62). Symbol pins: 1 A = NC, 2 B = common, 3 C = NO."),
    ]
    for x, y, sz, bold, t in notes:
        o.append('\t(text "%s" (exclude_from_sim no) (at %s %s 0) (effects (font (size %s %s)%s) (justify left top)) (uuid "%s"))' % (
            t, fmt(x), fmt(y), sz, sz, " (bold yes)" if bold else "", uid("txt" + t[:40])))
    o.append('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
    return "\n".join(o)


def sym_lib_text():
    syms = symbols()
    body = "\n".join("\t" + t for t in syms.values())
    return '(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "kicad_symbol_editor")\n\t(generator_version "10.0")\n%s\n)\n' % body


# ============================================================================================
# Footprints drawn here
# ============================================================================================
def stick_fp():
    """The panel's Y6 placeholder (kept for this board), the RKJXV-class envelope."""
    pads = []
    for i, (x, y) in enumerate([(-1.27, -3.81), (-1.27, -1.27), (-1.27, 1.27), (-1.27, 3.81),
                                (1.27, -3.81), (1.27, -1.27), (1.27, 1.27), (1.27, 3.81)]):
        n = i + 1
        shape = "rect" if n == 1 else "circle"
        pads.append('\t(pad "%d" thru_hole %s (at %s %s) (size 1.6 1.6) (drill 1.0) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "%s"))' % (
            n, shape, fmt(x), fmt(y), uid("stickpad%d" % n)))
    return '''(footprint "Thumbstick_P156_Placeholder_2x04_P2.54mm"
	(version 20260206)
	(generator "rx7-y21")
	(layer "F.Cu")
	(descr "PLACEHOLDER - confirm. Mirror stick P156 is not chosen (ALPS RKJXV class, 2-axis with push). Eight 1.0 mm holes on a 2.54 mm 2 x 4 grid carry the symbol's functional pins 1-4 (X_VCC, X_WIPER, X_GND, Y_VCC) down the left and 5-8 (Y_WIPER, Y_GND, SW_A, SW_B) down the right, so a stick on a small breakout or on leads can be fitted now; the 26 x 26 mm courtyard reserves the body, the 28 mm circle on F.Fab is the faceplate's well (radius 14, the sketch). Origin = the stick's axis. Replace with the chosen part's drawn footprint. No 3D model. From the panel's Y6 placeholder")
	(tags "joystick thumbstick placeholder")
	(property "Reference" "REF**" (at 0 -14.5 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Value" "Thumbstick_P156_Placeholder_2x04_P2.54mm" (at 0 15.5 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Description" "PLACEHOLDER - confirm (P156)" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(attr through_hole)
	(fp_rect (start -13 -13) (end 13 13) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "%s"))
	(fp_circle (center 0 0) (end 14 0) (stroke (width 0.1) (type dash)) (fill no) (layer "F.Fab") (uuid "%s"))
	(fp_text user "P156 - confirm" (at 0 -11 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.12))))
	(fp_text user "${REFERENCE}" (at 0 11 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.12))))
	(fp_rect (start -13.11 -13.11) (end 13.11 13.11) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS") (uuid "%s"))
	(fp_rect (start -13.25 -13.25) (end 13.25 13.25) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "%s"))
%s
)
''' % tuple([uid("stick%d" % i) for i in range(10)] + ["\n".join(pads)])


def wink_fp():
    """The P204 placeholder: an SPDT momentary pushbutton body under a 17 x 15 lit cap, no part chosen.
    Three 1.0 mm holes on 2.54 mm carry the symbol's pins (1 NC, 2 COM, 3 NO) so a switch on leads or
    a small breakout fits now; the 12 mm square is a board-mount button's body (confirm), the dashed
    17 x 15 on F.Fab is the sketch's cap. Origin = the cap's centre."""
    hb = WINK_BODY / 2
    pads = []
    for n, x in ((1, -2.54), (2, 0.0), (3, 2.54)):
        shape = "rect" if n == 1 else "circle"
        pads.append('\t(pad "%d" thru_hole %s (at %s 0) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "%s"))' % (
            n, shape, fmt(x), uid("winkpad%d" % n)))
    return '''(footprint "WinkSwitch_P204_SPDT_Placeholder"
	(version 20260206)
	(generator "rx7-y22")
	(layer "F.Cu")
	(descr "PLACEHOLDER - confirm. Wink switch P204 (D-499): a board-mount SPDT momentary pushbutton under a lit 17 x 15 key cap, C&K 8125 class, no part chosen. Three 1.0 mm holes on a 2.54 mm row carry the symbol's pins - 1 NC (the contact the pole rests on), 2 common, 3 NO - so a switch on leads or a small breakout fits now; the %s mm square is the body (confirm), the dashed 17 x 15 on F.Fab is the sketch's cap, lit by the 0603 LED beside the body. Origin = the cap's centre. Replace with the chosen part's drawn footprint; if the part carries its own LED the face LED moves onto its pins. No 3D model")
	(tags "wink pushbutton SPDT placeholder P204")
	(property "Reference" "REF**" (at 0 -8.5 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Value" "WinkSwitch_P204_SPDT_Placeholder" (at 0 8.5 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Description" "PLACEHOLDER - confirm (P204)" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(attr through_hole)
	(fp_rect (start -%s -%s) (end %s %s) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "%s"))
	(fp_rect (start -8.5 -7.5) (end 8.5 7.5) (stroke (width 0.1) (type dash)) (fill no) (layer "F.Fab") (uuid "%s"))
	(fp_text user "P204 - confirm" (at 0 -4 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.12))))
	(fp_text user "${REFERENCE}" (at 0 4 0) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.12))))
	(fp_rect (start -%s -%s) (end %s %s) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS") (uuid "%s"))
	(fp_rect (start -%s -%s) (end %s %s) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "%s"))
%s
)
''' % (fmt(WINK_BODY), uid("wk0"), uid("wk1"), uid("wk2"), uid("wk3"),
       fmt(hb), fmt(hb), fmt(hb), fmt(hb), uid("wk4"), uid("wk5"), uid("wk6"), uid("wk7"),
       fmt(hb + 0.11), fmt(hb + 0.11), fmt(hb + 0.11), fmt(hb + 0.11), uid("wk8"),
       fmt(hb + 0.25), fmt(hb + 0.25), fmt(hb + 0.25), fmt(hb + 0.25), uid("wk9"),
       "\n".join(pads))


def write(path, text):
    with open(os.path.join(HERE, path), "w", encoding="utf-8") as f:
        f.write(text)


def gen_sch():
    write(NAME + ".kicad_sym", sym_lib_text())
    write(NAME + ".kicad_sch", sch_text())
    write("left-plate.pretty/Thumbstick_P156_Placeholder_2x04_P2.54mm.kicad_mod", stick_fp())
    write("left-plate.pretty/WinkSwitch_P204_SPDT_Placeholder.kicad_mod", wink_fp())
    write("sym-lib-table", '(sym_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.kicad_sym")(options "")(descr "Every symbol this schematic uses, kept with the project"))\n)\n' % (NAME, NAME))
    write("fp-lib-table", '(fp_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.pretty")(options "")(descr "Footprints drawn for the plate - the stick and wink switch placeholders"))\n)\n' % (NAME, NAME))
    gen_pro()


def gen_pro():
    """The panel's project file, its rules kept, renamed, one net class (Default, 0.25 mm, 0.6 / 0.3 vias)."""
    pro = json.load(open(os.path.join(CAD, "panel", "panel.kicad_pro"), encoding="utf-8"))
    pro["meta"]["filename"] = NAME + ".kicad_pro"
    pro["net_settings"]["classes"] = [c for c in pro["net_settings"]["classes"] if c["name"] == "Default"]
    pro["net_settings"]["netclass_patterns"] = []
    pro["schematic"]["top_level_sheets"] = [{"filename": NAME + ".kicad_sch", "name": NAME, "uuid": ROOT_UUID}]
    pro["schematic"]["used_designators"] = ""
    pro["sheets"] = [[ROOT_UUID, NAME]]
    pro["board"]["design_settings"]["drc_exclusions"] = []
    with open(os.path.join(HERE, NAME + ".kicad_pro"), "w", encoding="utf-8") as f:
        json.dump(pro, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "sch"
    if what == "sch":
        gen_sch()
    elif what == "pro":
        gen_pro()
    elif what == "pcb":
        import board_left_plate  # noqa: F401  (the board half, below)
        board_left_plate.main()
    else:
        print(__doc__)
        sys.exit(3)
