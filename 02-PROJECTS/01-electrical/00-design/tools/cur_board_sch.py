#!/usr/bin/env python3
"""cur_board_sch.py - draws the CUR board's KiCad project (work row Y71; D-597, D-602, D-604, D-615).

Owns (R6) nothing in the record; it is drawn FROM these rows of ../../data/ and must follow them:
  cavities   DP-CUR 1-9   - J1, the pigtail's solder pads: pad n is cavity n (1-4 the CU's I2C link,
                            5-9 the winks' and the hazard's lines to the PMU box)
  devices    DV21 (the hazard), DV24 (the winks and their 18 k / 33 k), DV62 (the CUR board)
  parts      P156 (the mirror control), P198 (the board), P199 (the LED driver and its LEDs), P204
             (the winks), P219 (the screen knob's encoder), P226 (the hazard), P250 (the I/O expander
             and its 3.3 V regulator), P249 (the pigtail's DRC 24)
and the CU firmware's plate channel map (../control-unit/firmware/cu/lights.h): OUT1 wink L, OUT2 wink R,
OUT3 hatch, OUT4 fuel door, OUT6 hazard, OUT13 mirror.

The face is the CUR face concept's second pass, ruled by D-602 (cur-face-concept.html, geo() at a face
height of 32 mm): the screen knob over the mirror control on the steering-wheel side, then the hazard
across the top and the winks and releases in a 2 x 2 grid, one 1.6 mm gap everywhere. The board is the
face's control area, 38.11 x 27.0 mm, its top-left corner at the face's (2.5, 2.5): every switch sits on
its cap's centre. Nothing here is measured or bought (R11): every part is a class with `confirm`.

Run with KiCad's own Python (pcbnew), from anywhere:
    <kicad python> cur_board_sch.py sch      writes the symbols, the sheet, the footprints, the lib tables
    <kicad python> cur_board_sch.py pcb      reads the netlist kicad-cli exports, places, routes, pours
    <kicad python> cur_board_sch.py pro      (re)writes cur-board.kicad_pro from the face board's rules
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

NAME = "cur-board"
HERE = layout.cad_dir(NAME)          # the KiCad project's folder: everything this writes goes there
KICAD_SYMS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
KICAD_FPS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
PANEL_SYM = layout.board_file("cu-face-board", "kicad_sym")
ROOT_UUID = "6c1e7a52-3f0d-4b8e-9a2c-1d5e0f7b2a21"     # fixed so re-runs keep the footprint links
REV = "1.00"
DATE = "2026-10-15"


def uid(seed):
    return str(uuidlib.uuid5(uuidlib.NAMESPACE_URL, "rx7/left-plate/" + seed))


# ============================================================================================
# The geometry, from the face (D-602): cur-face-concept.html geo(32). Face millimetres from its
# top-left seen from the driver; the board's origin is the face's (EDGE, EDGE), x toward the
# centre stack, y down. F.Cu faces the driver.
# ============================================================================================
FACE_H = 32.0
EDGE, GAP, KEY_RATIO = 2.5, 1.6, 1.4
INNER = FACE_H - 2 * EDGE
KEY_H = (INNER - 2 * GAP) / 3                    # 7.933
KEY_W = KEY_H * KEY_RATIO                        # 11.107
HAZ_W = 2 * KEY_W + GAP                          # 23.813
KNOB_D = (INNER - GAP) / 2                       # 12.7, the screen knob and the mirror control's well
FACE_W = 2 * EDGE + KNOB_D + GAP + HAZ_W         # 43.113
W, H = FACE_W - 2 * EDGE, INNER                  # the board: the face's control area, 38.113 x 27.0


def at_face(x, y):
    """Face millimetres -> board millimetres."""
    return (x - EDGE, y - EDGE)


_col = EDGE + KNOB_D / 2
_x0 = EDGE + KNOB_D + GAP
KNOB = at_face(_col, EDGE + KNOB_D / 2)                          # (6.35, 6.35)
STICK = at_face(_col, EDGE + KNOB_D + GAP + KNOB_D / 2)          # (6.35, 20.65)
_r0 = EDGE + KEY_H / 2
_r1 = _r0 + KEY_H + GAP
_r2 = _r1 + KEY_H + GAP
K1 = _x0 + KEY_W / 2 - EDGE                      # left key column (19.853)
K2 = _x0 + KEY_W + GAP + KEY_W / 2 - EDGE        # right key column (32.560)
HAZ = (_x0 + HAZ_W / 2 - EDGE, _r0 - EDGE)       # (26.207, 3.967)
WINK_Y, KEY_Y = _r1 - EDGE, _r2 - EDGE           # 13.5, 23.033
WELL_R = KNOB_D / 2
CORNER_R = 1.0
CAP_LED_DX = 4.3                                 # a key's symbol LED inside its cap, beside the switch body
HAZ_LED_DX = 6.5                                 # the hazard's LED, inside its wide cap
J1_AT = (12.8, 18.3)                             # the pigtail's pad 1, on the row between the winks and the keys
J1_PITCH = 2.54

# The parts' classes (placeholders until bought - confirm): body sizes drawn on F.Fab
WINK_BODY = (6.5, 3.5)       # P204: a subminiature SPDT momentary (Omron D2FS / ultra-subminiature class)
HAZ_BODY = (5.8, 5.8)        # P226: a 5.8 mm self-locking (latching) push switch
KEY_BODY = (4.2, 3.2)        # the releases: a TL3342-class 4.2 x 3.2 SMD tactile
STICK_BODY = (7.5, 7.5)      # P156: an ALPS SKRH-class 4-direction switch with centre push
ENC_BODY = (9.7, 10.0)       # P219: a 9 mm encoder with push (Bourns PEC09 / ALPS EC09 class)


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
    t = block(text, m.start())
    e = re.search(r'\(extends "([^"]+)"\)', t)
    if e:                                    # a derived symbol: the parent's body under this name
        base = lib_symbol(path, e.group(1))
        base = base.replace('(symbol "%s"' % e.group(1), '(symbol "%s"' % name, 1)
        base = base.replace('(symbol "%s_' % e.group(1), '(symbol "%s_' % name)
        base = re.sub(r'\(property "Value" "[^"]*"', '(property "Value" "%s"' % name, base, count=1)
        return base
    return t


SW_4WAY = '''(symbol "SW_4WAY_PUSH"
		(pin_names (offset 1.016))
		(exclude_from_sim no) (in_bom yes) (on_board yes)
		(property "Reference" "SW" (at 0 8.89 0) (effects (font (size 1.27 1.27))))
		(property "Value" "SW_4WAY_PUSH" (at 0 -8.89 0) (effects (font (size 1.27 1.27))))
		(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(property "Description" "Four-direction switch with centre push (P156, ALPS SKRH class): each direction and the push close to the common. Pin numbers are the placeholder footprint's, not a part's" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
		(symbol "SW_4WAY_PUSH_0_1"
			(rectangle (start -7.62 6.35) (end 7.62 -6.35) (stroke (width 0.254) (type default)) (fill (type background)))
		)
		(symbol "SW_4WAY_PUSH_1_1"
			(pin passive line (at -10.16 2.54 0) (length 2.54) (name "UP" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -10.16 0 0) (length 2.54) (name "COM" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
			(pin passive line (at -10.16 -2.54 0) (length 2.54) (name "DOWN" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 10.16 2.54 180) (length 2.54) (name "RIGHT" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 10.16 0 180) (length 2.54) (name "PUSH" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
			(pin passive line (at 10.16 -2.54 180) (length 2.54) (name "LEFT" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
		)
	)'''


def symbols():
    """name -> library text (unprefixed), every symbol the sheet uses."""
    out = {}
    for n in ("GND", "+3V3", "PWR_FLAG", "SW_Push", "LED", "R", "C"):
        out[n] = lib_symbol(PANEL_SYM, n)
    out["Conn_01x09"] = lib_symbol(KICAD_SYMS + "Connector_Generic.kicad_sym", "Conn_01x09")
    out["SW_SPST"] = lib_symbol(KICAD_SYMS + "Switch.kicad_sym", "SW_SPST")         # the latching hazard
    # KiCad's SPDT momentary: pin 1 A = the contact the pole rests on (NC), 2 B = common, 3 C = NO
    out["SW_Push_SPDT"] = lib_symbol(KICAD_SYMS + "Switch.kicad_sym", "SW_Push_SPDT")
    out["IS31FL3218-QF"] = lib_symbol(KICAD_SYMS + "Driver_LED.kicad_sym", "IS31FL3218-QF")
    out["PCA9555PW"] = lib_symbol(KICAD_SYMS + "Interface_Expansion.kicad_sym", "PCA9555PW")
    out["AP2112K-3.3"] = lib_symbol(KICAD_SYMS + "Regulator_Linear.kicad_sym", "AP2112K-3.3")
    out["RotaryEncoder_Switch"] = lib_symbol(KICAD_SYMS + "Device.kicad_sym", "RotaryEncoder_Switch")
    out["SW_4WAY_PUSH"] = SW_4WAY
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
# The sheet: (ref, symbol, value, footprint, (x, y), {pin number: net, "GND"/"+3V3" power, None = no
# connect}, confirm)
# ============================================================================================
FP_LED = "LED_SMD:LED_0603_1608Metric"
FP_R = "Resistor_SMD:R_0603_1608Metric"
FP_C = "Capacitor_SMD:C_0603_1608Metric"
DS_3218 = "https://www.lumissil.com/assets/pdf/core/IS31FL3218_DS.pdf"
DS_9555 = "https://www.nxp.com/docs/en/data-sheet/PCA9555.pdf"
DS_2112 = "https://www.diodes.com/assets/Datasheets/AP2112.pdf"

# J1, the pigtail's solder pads: pad n = DP-CUR n (the record's cavities, D-597, D-604, D-615)
J1_NETS = {"1": "PNL_SDA", "2": "PNL_SCL", "3": "GND", "4": "+5V_PNL",
           "5": "WINK_L_NC", "6": "WINK_R_NC", "7": "WINK_REQ", "8": "WINK_COM", "9": "HAZ_LADDER"}
J1_CAVS = {"1": "DP-CUR 1 (DP-DCU 44)", "2": "DP-CUR 2 (DP-DCU 45)", "3": "DP-CUR 3 (DP-DCU 46)",
           "4": "DP-CUR 4 (DP-DCU 47)", "5": "DP-CUR 5 (K2's switch input)", "6": "DP-CUR 6 (K1's switch input)",
           "7": "DP-CUR 7 (A8)", "8": "DP-CUR 8 (the PMU box's star)", "9": "DP-CUR 9 (A8)"}
HAZ_R, HAZ_BASE = "4.7k", "47k"
WINK_R_OHMS = {"L": "18k", "R": "33k"}       # DP-CUR 7: wink L NO through 18 k, wink R NO through 33 k

# the plate's channel map, the firmware's (lights.h LQ_*): OUTn -> (LED ref, what it lights, net)
CHANNELS = [(1, "LED1", "wink left face", "LED_WINK_L"),
            (2, "LED2", "wink right face", "LED_WINK_R"),
            (3, "LED3", "hatch release symbol", "LED_HATCH"),
            (4, "LED4", "fuel-door release symbol", "LED_FUEL"),
            (13, "LED5", "mirror symbol, in the control's well", "LED_MIRROR"),
            (6, "LED6", "hazard red triangle", "LED_HAZARD")]

# the I/O expander's inputs (D-604): every key, the four directions and both pushes, read over I2C by the
# CU; each closes to GND, the PCA9555's own 100 k pull-ups hold it high
# - each input on the pin nearest its switch on the board (U2 sits behind the mirror control)
EXPANDER = {"4": "MIR_RIGHT", "5": "KNOB_B", "6": "KNOB_PUSH", "7": "MIR_PUSH", "8": "KEY_HATCH",
            "9": "KEY_FUEL", "10": "MIR_LEFT", "15": "MIR_DOWN", "19": "MIR_UP", "20": "KNOB_A"}


def parts():
    P = []
    P.append(("J1", "Conn_01x09", "pigtail solder pads 1x9 (DP-CUR 1-9)", "cur-board:Pigtail_SolderPads_1x09_P2.54mm",
              (40.64, 66.04), dict(J1_NETS),
              "the CUR's sealed pigtail (P200, D-615): nine 20 AWG conductors soldered here, out through the rear "
              "grommet, about 150 mm to the inline DRC 24 receptacle that mates the harness's DP-CUR plug; pad n = "
              "DP-CUR n - length and conductor confirm"))
    # the releases: SMD tactiles under the face's 11.1 x 7.9 caps, read by the expander
    P.append(("SW1", "SW_Push", "key - hatch", "cur-board:SW_PUSH_TL3342_Placeholder", (114.3, 50.8),
              {"1": "KEY_HATCH", "2": "GND"},
              "a TL3342-class 4.2 x 3.2 SMD tactile under the hatch cap (P199): actuator height against the cap - confirm"))
    P.append(("SW2", "SW_Push", "key - fuel door", "cur-board:SW_PUSH_TL3342_Placeholder", (114.3, 66.04),
              {"1": "KEY_FUEL", "2": "GND"},
              "a TL3342-class 4.2 x 3.2 SMD tactile under the fuel-door cap (P199) - confirm"))
    P.append(("SW6", "SW_4WAY_PUSH", "mirror control - 4 way + push (P156)", "cur-board:Thumbstick_SKRH_4Way_Push_Placeholder",
              (114.3, 91.44), {"1": "MIR_UP", "2": "GND", "3": "MIR_DOWN", "4": "MIR_RIGHT", "5": "MIR_PUSH", "6": "MIR_LEFT"},
              "P156 (D-615): an ALPS SKRH-class 4-direction switch with centre push, about 7.5 x 7.5, under a small knob in the "
              "face's 12.7 mm well; pad map from the part's drawing - confirm"))
    P.append(("ENC1", "RotaryEncoder_Switch", "screen knob - 9 mm encoder with push (P219)", "cur-board:ScreenKnob_Encoder9mm_Placeholder",
              (114.3, 121.92), {"A": "KNOB_A", "B": "KNOB_B", "C": "GND", "S1": "KNOB_PUSH", "S2": "GND"},
              "P219 (D-580, D-615): a 9 mm encoder with push (Bourns PEC09 / ALPS EC09 class) on this board, its shaft "
              "through the face; pin map and bushing from the part's drawing - confirm"))
    U = {"5": "PNL_SDA", "6": "PNL_SCL", "24": "LED_SDB", "2": "LED_REXT", "3": "+5V_PNL", "4": "GND", "25": "GND"}
    for out_n in range(1, 19):
        pin = str(out_n + 6) if out_n <= 17 else "1"
        U[pin] = None
    for out_n, ref, what, net in CHANNELS:
        U[str(out_n + 6)] = net
    P.append(("U1", "IS31FL3218-QF", "IS31FL3218-QFLS2-TR", "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
              (213.36, 76.2), U,
              "the CUR's LED driver (P199): fixed I2C address 0x54; VCC 2.7-5.5 V on +5V_PNL, VIH 1.4 V so the 3.3 V bus "
              "reads (Lumissil Rev G p.4); footprint KiCad's QFN-24 4x4 - confirm against the package drawing"))
    P.append(("C1", "C", "1uF", FP_C, (182.88, 129.54), {"1": "+5V_PNL", "2": "GND"}, "X7R 10 V or more - confirm"))
    P.append(("C2", "C", "100nF", FP_C, (213.36, 129.54), {"1": "+5V_PNL", "2": "GND"}, "X7R - confirm"))
    P.append(("R1", "R", "10k", FP_R, (182.88, 144.78), {"1": "LED_REXT", "2": "GND"},
              "R_EXT: IMAX = 58.5 x 1.3 V / 10k = 7.6 mA a channel (Lumissil p.10), the face board's current - 1 %"))
    P.append(("R2", "R", "100k", FP_R, (213.36, 144.78), {"1": "+5V_PNL", "2": "LED_SDB"},
              "holds SDB high: the driver is on and blank until written, as the face board's - confirm"))
    X = {"1": None, "2": "GND", "3": "GND", "21": "GND", "12": "GND", "24": "+3V3", "22": "PNL_SCL", "23": "PNL_SDA"}
    for pin in ("4", "5", "6", "7", "8", "9", "10", "11", "13", "14", "15", "16", "17", "18", "19", "20"):
        X[pin] = EXPANDER.get(pin)
    P.append(("U2", "PCA9555PW", "PCA9555PW", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", (213.36, 203.2), X,
              "the I/O expander (P250, D-604): address 0x20 (A0-A2 low), its 100 k pull-ups on every input, VDD 3.3 V "
              "so its VIH (0.7 VDD) reads the CU's 3.3 V bus; INT not wired - the CU polls it - confirm (NXP PCA9555 rev 9)"))
    P.append(("C3", "C", "100nF", FP_C, (182.88, 254.0), {"1": "+3V3", "2": "GND"}, "X7R, at U2's VDD - confirm"))
    P.append(("U3", "AP2112K-3.3", "AP2112K-3.3TRG1", "Package_TO_SOT_SMD:SOT-23-5", (358.14, 66.04),
              {"1": "+5V_PNL", "2": "GND", "3": "+5V_PNL", "4": None, "5": "+3V3"},
              "Diodes Inc AP2112K-3.3, 600 mA LDO, 1 uF in and out (its sheet); the expander takes under 1 mA - confirm"))
    P.append(("C4", "C", "1uF", FP_C, (342.9, 93.98), {"1": "+5V_PNL", "2": "GND"}, "X7R 10 V - the LDO's input"))
    P.append(("C5", "C", "1uF", FP_C, (373.38, 93.98), {"1": "+3V3", "2": "GND"}, "X7R 10 V - the LDO's output"))
    for i, (out_n, ref, what, net) in enumerate(CHANNELS):
        P.append((ref, "LED", "LED 0603 - %s (OUT%d)" % (what, out_n), FP_LED, (284.48, 50.8 + i * 15.24),
                  {"2": "+5V_PNL", "1": net},
                  "colour, brightness and part number - confirm (I-006: the wink faces green; the hazard red)"))
    # the winks (D-499): SPDT momentary under lit caps, the ladder resistors beside them, their lines on J1
    for side, ref, rref, y in (("L", "SW3", "R3", 182.88), ("R", "SW4", "R4", 208.28)):
        name = "left" if side == "L" else "right"
        P.append((ref, "SW_Push_SPDT", "wink - %s (P204)" % name, "cur-board:WinkSwitch_P204_SPDT_Placeholder", (40.64, y),
                  {"1": "WINK_%s_NC" % side, "2": "WINK_COM", "3": "WINK_%s_NO" % side},
                  "P204 (D-615): a subminiature SPDT momentary (Omron D2FS class) under the wink's lit 11.1 x 7.9 cap; "
                  "pins 1 NC, 2 COM, 3 NO and the body from the part's drawing - confirm"))
        P.append((rref, "R", WINK_R_OHMS[side], FP_R, (81.28, y), {"1": "WINK_%s_NO" % side, "2": "WINK_REQ"},
                  "the wink %s ladder resistor (DV24, DP-CUR 7), on the board since D-499 - 1 %%" % name))
    # the hazard (D-586, D-589): a latching push button under the lit red-triangle cap across the top row
    P.append(("SW5", "SW_SPST", "hazard - latching (P226)", "cur-board:HazardSwitch_P226_Latching_Placeholder", (40.64, 241.3),
              {"1": "HAZ_SW", "2": "WINK_COM"},
              "P226 (D-615): a 5.8 mm self-locking push switch under the hazard's 23.8 x 7.9 red-triangle cap; pins and body "
              "from the part's drawing - confirm"))
    P.append(("R5", "R", HAZ_R, FP_R, (81.28, 241.3), {"1": "HAZ_LADDER", "2": "HAZ_SW"},
              "the hazard's ladder resistor (DV21, D-368, D-586): HAZARD on A8 when the button is in - 1 %"))
    P.append(("R6", "R", HAZ_BASE, FP_R, (81.28, 256.54), {"1": "HAZ_LADDER", "2": "WINK_COM"},
              "the hazard's 47 k baseline (D-368): the PMU reads the wire present with the button out - 1 %"))
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
		(title "CUR board - the Control Unit Remote (D-602, D-615)")
		(date "%s")
		(rev "%s")
		(company "RX-7 FB electrical build")
		(comment 1 "From the record: DP-CUR 1-9, DV21 / DV24 / DV62, P156-P250. The row wins.")
		(comment 2 "Keys on a PCA9555 (0x20), lights on an IS31FL3218 (0x54).")
		(comment 3 "Winks and hazard: own lines to the PMU box (they wake the car).")
		(comment 4 "R11: nothing measured or bought. Rev %s (Y71).")
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

    ds = {"U1": DS_3218, "U2": DS_9555, "U3": DS_2112}
    taken = {}                  # every sheet point a pin or a stub touches -> (net, who): two nets never share one

    def claim(x, y, net, who):
        k = (round(x, 3), round(y, 3))
        if k in taken and taken[k][0] != net:
            raise ValueError("%s (%s) touches %s (%s) at %s - move a part on the sheet" % (who, net, taken[k][1], taken[k][0], k))
        taken.setdefault(k, (net, who))
    for ref, sym, value, fp, (X, Y), nets, confirm in parts():
        plist = pins[sym]
        o.append('\t(symbol (lib_id "%s:%s") (at %s %s 0) (unit 1) (body_style 1)' % (NAME, sym, fmt(X), fmt(Y)))
        o.append('\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)')
        o.append('\t\t(uuid "%s")' % uid("sym" + ref))
        ys = [Y - p[3] for p in plist]
        top, bot = min(ys), max(ys)
        rx, ry, vx_, vy_ = X, top - 3.81, X, bot + 3.81
        if ref in ("U1", "U2", "U3"):                         # clear of the stubs above and below
            rx, ry, vx_, vy_ = X - 7.62, top - 6.35, X + 10.16, bot + 8.89
        o.append('\t\t(property "Reference" "%s" (at %s %s 0) (effects (font (size 1.27 1.27))))' % (ref, fmt(rx), fmt(ry)))
        o.append('\t\t(property "Value" "%s" (at %s %s 0) (effects (font (size 1.1 1.1))))' % (value, fmt(vx_), fmt(vy_)))
        o.append('\t\t(property "Footprint" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (fp, fmt(X), fmt(Y)))
        o.append('\t\t(property "Datasheet" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))' % (ds.get(ref, ""), fmt(X), fmt(Y)))
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
            for k in range(0, 3):
                claim(sx + d[0] * 1.27 * k, sy + d[1] * 1.27 * k, net, "%s pin %s" % (ref, num))
            o.append(wire(sx, sy, ex, ey))
            if net in POWER:
                o.append(power_sym(net, ex, ey, d))
            else:
                o.append(label(net, ex, ey, d))
    # the power flags: +5V_PNL and GND reach this board only through J1's passive pads; +3V3 is U3's
    for i, net in enumerate(("GND", "+5V_PNL")):
        x, y = 342.9 + i * 15.24, 139.7
        o.append(wire(x, y, x, y + 5.08))
        o.append(power_sym("PWR_FLAG", x, y))
        if net in POWER:
            o.append(power_sym(net, x, y + 5.08))
        else:
            o.append(label(net, x, y + 5.08, (0, 1)))
    notes = [
        (20.32, 20.32, 1.8, True, "J1 - THE PIGTAIL TO DP-CUR"),
        (20.32, 24.13, 1.3, False, "D-597, D-615. Pad n = DP-CUR n."),
        (20.32, 26.67, 1.3, False, "1-4: the CU's I2C link (DP-DCU 44-47)."),
        (20.32, 29.21, 1.3, False, "5-9: the winks and the hazard, to the PMU box."),
        (20.32, 31.75, 1.3, False, "Nine 20 AWG wires out through the rear grommet,"),
        (20.32, 34.29, 1.3, False, "~150 mm to an inline DRC 24 - confirm."),
        (96.52, 20.32, 1.8, True, "THE KEYS, THE MIRROR CONTROL, THE KNOB"),
        (96.52, 24.13, 1.3, False, "D-604, D-615. Each closes to GND; U2 reads it."),
        (96.52, 26.67, 1.3, False, "The CU polls U2 over the bus: no INT wire."),
        (172.72, 20.32, 1.8, True, "U1 - THE LIGHTS: IS31FL3218 at 0x54"),
        (172.72, 24.13, 1.3, False, "OUT1 wink L, OUT2 wink R, OUT3 hatch, OUT4 fuel,"),
        (172.72, 26.67, 1.3, False, "OUT6 hazard, OUT13 mirror (lights.h). 7.6 mA."),
        (266.7, 20.32, 1.8, True, "THE SYMBOL LEDS"),
        (266.7, 24.13, 1.3, False, "Anodes on +5V_PNL, each in its cap or the well."),
        (330.2, 20.32, 1.8, True, "U3 - 3.3 V FOR THE EXPANDER"),
        (330.2, 24.13, 1.3, False, "AP2112K from +5V_PNL; under 1 mA drawn."),
        (172.72, 152.4, 1.8, True, "U2 - THE I/O EXPANDER: PCA9555 at 0x20, on +3V3"),
        (172.72, 156.21, 1.3, False, "IO0_0 mirror right, 0_1 knob B, 0_2 knob push, 0_3 mirror push,"),
        (172.72, 158.75, 1.3, False, "0_4 hatch, 0_5 fuel door, 0_6 mirror left; IO1_2 mirror down,"),
        (172.72, 161.29, 1.3, False, "1_6 mirror up, 1_7 knob A. Its own 100 k pull-ups hold each high."),
        (20.32, 162.56, 1.8, True, "THE WINKS AND THE HAZARD (D-499, D-586, D-589)"),
        (20.32, 166.37, 1.3, False, "NC poles to DP-CUR 5 / 6, NO poles through 18k / 33k as WINK_REQ (DP-CUR 7),"),
        (20.32, 168.91, 1.3, False, "the commons on DP-CUR 8 - the PMU box's star, NOT this board's GND."),
        (20.32, 171.45, 1.3, False, "Hazard: DP-CUR 9 -> 4.7k -> latching button -> commons; 47k across (D-368)."),
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
# Footprints drawn here: every one a PLACEHOLDER for a class, its body on F.Fab (solid), its cap or
# well on F.Fab (dashed) - the mock-up (tools/cur_assembly.py) reads the face from those
# ============================================================================================
def _fp(name, gen, descr, tags, attr, body_wh, cap_wh=None, well_r=None, pads="", extra=""):
    bw, bh = body_wh[0] / 2, body_wh[1] / 2
    u = lambda k: uid("%s.%s" % (name, k))
    g = []
    g.append('\t(fp_rect (start -%s -%s) (end %s %s) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "%s"))' % (fmt(bw), fmt(bh), fmt(bw), fmt(bh), u("body")))
    if cap_wh:
        cw, ch = cap_wh[0] / 2, cap_wh[1] / 2
        g.append('\t(fp_rect (start -%s -%s) (end %s %s) (stroke (width 0.1) (type dash)) (fill no) (layer "F.Fab") (uuid "%s"))' % (fmt(cw), fmt(ch), fmt(cw), fmt(ch), u("cap")))
    if well_r:
        g.append('\t(fp_circle (center 0 0) (end %s 0) (stroke (width 0.1) (type dash)) (fill no) (layer "F.Fab") (uuid "%s"))' % (fmt(well_r), u("well")))
    if attr != "smd":           # an SMD class's pads stand outside its body: its outline would cross them
        g.append('\t(fp_rect (start -%s -%s) (end %s %s) (stroke (width 0.1) (type solid)) (fill no) (layer "F.SilkS") (uuid "%s"))' % (fmt(bw + 0.1), fmt(bh + 0.1), fmt(bw + 0.1), fmt(bh + 0.1), u("silk")))
    return '''(footprint "%s"
	(version 20260206)
	(generator "%s")
	(layer "F.Cu")
	(descr "%s")
	(tags "%s")
	(property "Reference" "REF**" (at 0 -%s 0) (layer "F.Fab") (uuid "%s") (effects (font (size 0.8 0.8) (thickness 0.12))))
	(property "Value" "%s" (at 0 %s 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 0.8 0.8) (thickness 0.12))))
	(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Description" "PLACEHOLDER - confirm" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(attr %s)
%s
%s
%s
)
''' % (name, gen, descr, tags, fmt(bh + 1.0), u("r"), name, fmt(bh + 1.0), u("v"), u("d"), u("ds"), attr,
       "\n".join(g), extra, pads)


def _crtyd(name, x0, y0, x1, y1):
    return '\t(fp_rect (start %s %s) (end %s %s) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "%s"))' % (
        fmt(x0), fmt(y0), fmt(x1), fmt(y1), uid(name + ".crtyd"))


def _tht(name, num, x, y, size, drill, rect=False):
    return '\t(pad "%s" thru_hole %s (at %s %s) (size %s %s) (drill %s) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "%s"))' % (
        num, "rect" if rect else "circle", fmt(x), fmt(y), fmt(size), fmt(size), fmt(drill), uid("%s.pad%s.%s.%s" % (name, num, x, y)))


def _smd(name, num, x, y, w, h):
    return '\t(pad "%s" smd roundrect (at %s %s) (size %s %s) (layers "F.Cu" "F.Mask" "F.Paste") (roundrect_rratio 0.25) (uuid "%s"))' % (
        num, fmt(x), fmt(y), fmt(w), fmt(h), uid("%s.pad%s.%s.%s" % (name, num, x, y)))


def wink_fp():
    n = "WinkSwitch_P204_SPDT_Placeholder"
    pads = "\n".join(_tht(n, k, x, 0, 1.2, 0.7, rect=(k == "1")) for k, x in (("1", -2.0), ("2", 0.0), ("3", 2.0)))
    return _fp(n, "rx7-y71", "PLACEHOLDER - confirm. Wink switch P204 (D-499, D-615): a subminiature SPDT momentary "
               "(Omron D2FS class), its plunger under the wink's lit %s x %s cap. Three 0.7 mm holes on 2.0 mm (1.2 mm pads, room for a track between): 1 NC (the contact "
               "the pole rests on), 2 common, 3 NO. The %s x %s body on F.Fab (solid), the cap on F.Fab (dashed), lit by the 0603 "
               "beside the body. Origin = the cap's centre. Replace with the chosen part's drawn footprint. No 3D model"
               % (fmt(KEY_W), fmt(KEY_H), fmt(WINK_BODY[0]), fmt(WINK_BODY[1])),
               "wink SPDT subminiature placeholder P204", "through_hole", WINK_BODY, cap_wh=(KEY_W, KEY_H), pads=pads,
               extra=_crtyd(n, -WINK_BODY[0] / 2 - 0.25, -WINK_BODY[1] / 2 - 0.25, WINK_BODY[0] / 2 + 0.25, WINK_BODY[1] / 2 + 0.25))


def hazard_fp():
    n = "HazardSwitch_P226_Latching_Placeholder"
    pads = "\n".join(_tht(n, k, x, 0, 1.5, 0.9, rect=(k == "1")) for k, x in (("1", -1.5), ("2", 1.5)))
    return _fp(n, "rx7-y71", "PLACEHOLDER - confirm. Hazard switch P226 (D-586, D-589, D-615): a 5.8 mm self-locking push "
               "switch under the hazard's lit %s x %s red-triangle cap across the top row. Two 0.9 mm holes: the one contact. "
               "The body on F.Fab (solid), the cap on F.Fab (dashed). Origin = the cap's centre. No 3D model"
               % (fmt(HAZ_W), fmt(KEY_H)),
               "hazard latching self-lock placeholder P226", "through_hole", HAZ_BODY, cap_wh=(HAZ_W, KEY_H), pads=pads,
               extra=_crtyd(n, -HAZ_BODY[0] / 2 - 0.25, -HAZ_BODY[1] / 2 - 0.25, HAZ_BODY[0] / 2 + 0.25, HAZ_BODY[1] / 2 + 0.25))


def key_fp():
    n = "SW_PUSH_TL3342_Placeholder"
    pads = "\n".join(_smd(n, k, x, y, 1.0, 0.8) for k, x, y in (("1", -2.55, -0.95), ("1", -2.55, 0.95), ("2", 2.55, -0.95), ("2", 2.55, 0.95)))
    return _fp(n, "rx7-y71", "PLACEHOLDER - confirm. A release key: a TL3342-class 4.2 x 3.2 SMD tactile under the face's "
               "%s x %s cap (P199); pads 1 / 2 each twice, as the class. Origin = the switch's centre. No 3D model" % (fmt(KEY_W), fmt(KEY_H)),
               "tactile SMD release key placeholder", "smd", KEY_BODY, pads=pads,
               extra=_crtyd(n, -3.3, -1.85, 3.3, 1.85))


def stick_fp():
    n = "Thumbstick_SKRH_4Way_Push_Placeholder"
    pads = []
    for k, x, y in (("1", -4.3, -2.25), ("2", -4.3, 0.0), ("3", -4.3, 2.25), ("4", 4.3, -2.25), ("5", 4.3, 0.0), ("6", 4.3, 2.25)):
        pads.append(_smd(n, k, x, y, 1.2, 0.9))
    return _fp(n, "rx7-y71", "PLACEHOLDER - confirm. The mirror control P156 (D-615): an ALPS SKRH-class 4-direction switch "
               "with centre push, about 7.5 x 7.5, under a small knob in the face's %s mm well (dashed circle). Pads 1 UP, 2 COM, "
               "3 DOWN down the left, 4 RIGHT, 5 PUSH, 6 LEFT down the right - from the part's drawing, confirm. Origin = the "
               "control's axis. No 3D model" % fmt(KNOB_D),
               "4-way switch push mirror placeholder P156", "smd", STICK_BODY, well_r=WELL_R, pads="\n".join(pads),
               extra=_crtyd(n, -5.15, -3.95, 5.15, 3.95))


def encoder_fp():
    n = "ScreenKnob_Encoder9mm_Placeholder"
    pads = [_tht(n, "A", -2.5, 6.2, 1.5, 1.0, rect=True), _tht(n, "C", 0.0, 6.2, 1.5, 1.0), _tht(n, "B", 2.5, 6.2, 1.5, 1.0),
            _tht(n, "S1", 6.2, -2.5, 1.5, 1.0), _tht(n, "S2", 6.2, 2.5, 1.5, 1.0)]
    return _fp(n, "rx7-y71", "PLACEHOLDER - confirm. The screen knob P219 (D-580, D-615): a 9 mm encoder with push (Bourns "
               "PEC09 / ALPS EC09 class) on this board, its shaft on the origin through the face to the %s mm knob. A / C / B "
               "below the body, the push S1 / S2 at its side - the part's own pin map and bushing from its drawing" % fmt(KNOB_D),
               "encoder 9mm push screen knob placeholder P219", "through_hole", ENC_BODY, pads="\n".join(pads),
               extra=_crtyd(n, -5.1, -5.25, 7.2, 7.2))


def pigtail_fp():
    n = "Pigtail_SolderPads_1x09_P2.54mm"
    pads = [_tht(n, str(i + 1), i * J1_PITCH, 0, 1.8, 1.1, rect=(i == 0)) for i in range(9)]
    w = 8 * J1_PITCH
    return '''(footprint "%s"
	(version 20260206)
	(generator "rx7-y71")
	(layer "F.Cu")
	(descr "The CUR's pigtail (P200, D-615): nine 20 AWG conductors soldered into 1.1 mm plated holes on 2.54 mm, entered from the back, pad n = DP-CUR n; strain relief by the rear grommet and potting - confirm. Origin = pad 1")
	(tags "pigtail solder wire pads")
	(property "Reference" "REF**" (at %s -2.2 0) (layer "F.Fab") (uuid "%s") (effects (font (size 0.8 0.8) (thickness 0.12))))
	(property "Value" "%s" (at %s 2.2 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 0.8 0.8) (thickness 0.12))))
	(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))
	(attr through_hole)
	(fp_rect (start -1.2 -1.2) (end %s 1.2) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "%s"))
	(fp_rect (start -1.1 -1.1) (end %s 1.1) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab") (uuid "%s"))
%s
)
''' % (n, fmt(w / 2), uid(n + "r"), n, fmt(w / 2), uid(n + "v"), uid(n + "d"), uid(n + "ds"),
       fmt(w + 1.2), uid(n + "cy"), fmt(w + 1.1), uid(n + "fab"), "\n".join(pads))


def write(path, text):
    with open(os.path.join(HERE, path), "w", encoding="utf-8") as f:
        f.write(text)


OLD_FPS = ("Thumbstick_P156_Placeholder_2x04_P2.54mm", "ScreenKnob_P219_Board_Placeholder")


def gen_sch():
    write(NAME + ".kicad_sym", sym_lib_text())
    write(NAME + ".kicad_sch", sch_text())
    for fp_name in OLD_FPS:                     # the plate's placeholders the D-602 face retired
        p = os.path.join(HERE, "cur-board.pretty", fp_name + ".kicad_mod")
        if os.path.exists(p):
            os.remove(p)
    write("cur-board.pretty/WinkSwitch_P204_SPDT_Placeholder.kicad_mod", wink_fp())
    write("cur-board.pretty/HazardSwitch_P226_Latching_Placeholder.kicad_mod", hazard_fp())
    write("cur-board.pretty/SW_PUSH_TL3342_Placeholder.kicad_mod", key_fp())
    write("cur-board.pretty/Thumbstick_SKRH_4Way_Push_Placeholder.kicad_mod", stick_fp())
    write("cur-board.pretty/ScreenKnob_Encoder9mm_Placeholder.kicad_mod", encoder_fp())
    write("cur-board.pretty/Pigtail_SolderPads_1x09_P2.54mm.kicad_mod", pigtail_fp())
    write("sym-lib-table", '(sym_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.kicad_sym")(options "")(descr "Every symbol this schematic uses, kept with the project"))\n)\n' % (NAME, NAME))
    write("fp-lib-table", '(fp_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.pretty")(options "")(descr "Footprints drawn for the CUR - placeholders for the parts not yet chosen, and the pigtail pads"))\n)\n' % (NAME, NAME))
    gen_pro()


def gen_pro():
    """The face board's project file, its rules kept, renamed, one net class (Default, 0.25 mm, 0.6 / 0.3 vias)."""
    pro = json.load(open(layout.board_file("cu-face-board", "kicad_pro"), encoding="utf-8"))
    pro["meta"]["filename"] = NAME + ".kicad_pro"
    pro["net_settings"]["classes"] = [c for c in pro["net_settings"]["classes"] if c["name"] == "Default"]
    # the CUR's board is 38 x 27, both sides populated: finer rules than the face board's, inside a standard
    # two-layer process (JLCPCB: 0.127 mm track and space, 0.3 / 0.15 mm vias) - Y71
    for c in pro["net_settings"]["classes"]:
        c.update({"clearance": 0.15, "track_width": 0.2, "via_diameter": 0.5, "via_drill": 0.25})
    rules = pro["board"]["design_settings"]["rules"]
    rules.update({"min_clearance": 0.15, "min_track_width": 0.15, "min_via_diameter": 0.45, "min_through_hole_diameter": 0.25,
                  "min_hole_clearance": 0.2, "min_hole_to_hole": 0.25})
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
        import cur_board_pcb  # noqa: F401  (the board half, below)
        cur_board_pcb.main()
    else:
        print(__doc__)
        sys.exit(3)
