#!/usr/bin/env python3
"""check.py - the five KiCad sheets against the record and the datasheets (work row Y3).

Reads (never writes) the record's tables - these are the facts it holds the drawings to:
  ../../data/icu_channels.csv   id, kind, at_the_drop, teensy_pin  (the ICU carrier, J5)
  ../../data/dcu_channels.csv   the same for the DCU carrier (J10, expander U12)
  ../../data/panel_ribbon.csv   pin, signal, panel_side             (DCU J4, the panel's J1, the upper board's J8)
  ../../data/cavities.csv       housing, cav, state, src_note,      (which board-edge pins must be wired, and where to)
                                circuit, lands_on                   (the left plate's wink lead, L3-S1 9-11)
and this folder's pin_tables.csv (part, package, pin, name, source_url), the vendor pin tables
of every IC whose symbol was drawn as a functional block.

For each sheet it runs `kicad-cli sch export netlist --format kicadsexpr`, parses the
s-expression itself (no packages beyond the standard library, Python 3.9) and checks:

  * every pin the record puts on the Teensy (`teensy_pin`) is on the socket pad for that
    pin - pads are numbered as the Teensy41_Socket footprint numbers them, DIP-style, from the
    PJRC Teensy 4.1 card (www.pjrc.com/teensy/card11a_rev4_web.pdf) - and that pad's net is
    the one the sheet names for the channel, reaching the part the record says it reaches;
  * every expander port the record names (P00-P17 on the TCA9539-Q1) likewise;
  * every drop cavity a channel names (`at_the_drop`: DP-ICU-A 1, DP-DCU-B 5-8 ...) is wired
    on the board-edge connector and, walking through the board's parts, reaches that
    channel's processor pin; a cavity the record has LIVE or CAPPED is wired, a PLUG is not;
  * the ribbon header, pin by pin, against `panel_ribbon` - net names on both boards, and on
    the panel which keys, encoders and thumbstick pins hang off each conductor;
  * the panel matrix diodes: cathode to the row, anode toward the column (control-unit/cad/panel/README.md); a
    window switch's poles as two keys (COM_n to its diode, UP_n / DN_n to the column, D-492);
  * the panel's plate header J3, DP-DCU-E cavity n on pin n, as its src_note's panel_ribbon line,
    and the keys the record puts on the left plate held to the cavities that name them (D-492);
  * the two rules CONVENTIONS.md §5 asks for: the two 12 V inputs share no part (and on the
    DCU no part but the INA180 touches both GND and PGND), and every BAT54S has A on GND and
    K on +3V3;
  * each functional-block symbol's pin number -> name against pin_tables.csv, and each
    transistor's and each tabled diode's the same way (Y42: a SOT-23 FET's gate / source / drain,
    a SOT-23 zener's anode / unused / cathode, a one-way TVS's cathode on the footprint's mark);
  * on the upper connector board (Y15, no processor), DP-DCU-D and DP-DCU-E cavity by cavity: wired
    or a plug as `state` says, no two cavities joined, and on the header `src_note` names - the
    carrier header's lead (J6-J8, J5, J3) pin for pin, or the panel_ribbon line, named as that line;
  * on the left plate (Y21, D-492), its cable header J1 against DP-DCU-E cavity by cavity, the keys
    the cavities name on their row and column through their diodes, the stick on panel_ribbon 1 and
    17-20 (the push to GND), and the bus reaching the plate's LED driver; its wink lead J2 against the
    L3-S1 cavities whose lands_on name it (D-499, D-504) - each NC pole and common on its pin, the
    commons apart from the plate's GND, and the wink resistors at the values cavity 11 names.

Exit codes: 0 everything matches; 1 any mismatch (each printed as
`board:ref:pin expected X got Y`); 3 kicad-cli missing or a file unreadable. Notes (things
worth a look that are not contradictions) print with a `note` prefix and never fail.

    python3 check.py [-v] [--board icu|dcu|panel|upper|left-plate] [--netlists DIR]

`--netlists DIR` reads DIR/<board>.net instead of exporting (kicad-cli still runs one sheet
at a time otherwise). The expected net names below are the sheets' own vocabulary; the
record's pins, roles and drops are read live, so moving a pin in the record moves the check.
"""
import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
AREA = os.path.normpath(os.path.join(HERE, "..", ".."))
DESIGN = os.path.dirname(HERE)          # 00-design: each board's sheet is under its unit (D-496)
DATA = os.path.join(AREA, "data")
PIN_TABLES = os.path.join(HERE, "pin_tables.csv")

KICAD_CLI_CANDIDATES = [
    "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    "/usr/bin/kicad-cli",
]

# --------------------------------------------------------------------------------------------
# The Teensy 4.1 socket. Both carriers use the Teensy41_Socket footprint, pads 1-48 numbered
# DIP-style: 1-24 down the left edge from the USB end, 25-48 up the right edge. The labels are
# the PJRC card's (front side, rev 4): left GND, 0-12, 3.3V, 24-32; right (from the USB end)
# VIN, GND, 3.3V, 23-13, GND, 41-33.
# --------------------------------------------------------------------------------------------
def teensy41_pads():
    left = ["GND"] + [str(n) for n in range(0, 13)] + ["3V3"] + [str(n) for n in range(24, 33)]
    right = [str(n) for n in range(33, 42)] + ["GND"] + [str(n) for n in range(13, 24)] + ["3V3", "GND", "VIN"]
    return {str(i + 1): label for i, label in enumerate(left + right)}


TEENSY_PADS = teensy41_pads()                       # pad number -> Teensy label
TEENSY_PAD_OF = {v: k for k, v in TEENSY_PADS.items() if v not in ("GND", "3V3")}  # label -> pad

# --------------------------------------------------------------------------------------------
# What each record pin is called on the sheet, in the order the record lists the pins.
# An entry is "NET" or ("NET", "REF.PINNAME" | "REF#PINNUMBER"): the pad must sit on NET and,
# when a far end is given, NET must reach that pin through nothing but two-pin passives.
# A channel absent here with pins in the record is a mismatch, so a new pin cannot slip by.
# --------------------------------------------------------------------------------------------
EXPECT = {
    "icu": {
        "IC01": ["IC01_ADC"], "IC02": ["IC02_ADC"], "IC03": ["IC03_ADC"],
        "IC04": [("IC04_CAP", "U4#1")],                 # LM393 comparator 1 output
        "IC05": ["IC05_ADC"], "IC06": ["IC06_DIG"], "IC07": ["IC07_ADC"],
        "IC08": [("IC08_CAP", "U5#4")],                 # 74LVC1G17 Y
        "IC09": ["IC09_DIG"], "IC10": ["IC10_DIG"], "IC11": ["IC11_DIG"],
        "IC12": [("PG_5V", "U1.PG")],
        "IC13": ["BL_EN"],
        "IC14": ["IC14_ADC"],
        "IC15": [],
        "IC16": [("CAN_TXD", "U3.TXD"), ("CAN_RXD", "U3.RXD"), ("CAN_STB", "U3.STB")],
        "IC21": [("SPI_CS", "J4.QSPI_CS"), ("SPI_MOSI", "J4.QSPI_IO0"), ("SPI_MISO", "J4.QSPI_IO1"),
                 ("SPI_SCK", "J4.QSPI_SCK"), ("BT817_PD", "J4.PD"), ("BT817_INT", "J4.INT"),
                 ("BT_IO2", "J4.QSPI_IO2"), ("BT_IO3", "J4.QSPI_IO3")],
        "IC22": ["PAGE_BTN"],
        "IC23": [("I2C_SDA", "U7.SDA"), ("I2C_SCL", "U7.SCL"), ("IMU_INT", "U7.INT1")],
        # The record's "RX 7" is the Teensy's receive pin, fed by the radio's TX: the sheet
        # names a UART net by its driver, so pin 7 is RADIO_TX and must land on the XIAO's TX.
        # U8 carries Seeed's castellation names (F9); EN is a power-cycle through the NPN Q4 and
        # the P-FET on VBUS, so RADIO_EN ends at Q4's base; BOOT lands on D9 / GPIO9 (IC24).
        "IC24": [("RADIO_TX", "U8.D6/TX"), ("RADIO_RX", "U8.D7/RX"), ("RADIO_EN", "Q4.B"), ("RADIO_BOOT", "U8.D9/MISO")],
    },
    "dcu": {
        "SN24": ["+5V"],
        "SN25": [], "SN27": [],
        "SN26": [("CAN_RXD", "U3.RXD"), ("CAN_TXD", "U3.TXD")],
        "SN11": ["CABIN_ADC"], "SN12": ["OAT_ADC"], "SN13": [("CUR_ADC", "U4.OUT")],
        "SN14": [("BLOWER_T", "J5.Pin_1")],
        "SN15": [("SRV_MODE_T", "J6.Pin_1"), ("SRV_BLEND_T", "J7.Pin_1"), ("SRV_RECIRC_T", "J8.Pin_1")],
        "SN16": [("SH_DRV_IN", "U5.IN"), ("SH_PASS_IN", "U6.IN"), ("SC_DRV_IN", "U7.IN"),
                 ("SC_PASS_IN", "U8.IN"), ("MH_IN_T", "U9.IN")],
        "SN17": [("I2C_SDA", "U12.SDA"), ("I2C_SCL", "U12.SCL"), ("EXP_INT", "U12.INT"), ("EXP_RESET", "U12.RESET")],
        "SN18": [("JOY_X", "J4.17"), ("JOY_Y", "J4.18"), ("JOY_PRESS", "J4.19")],
        # D-492: ROW4 on ribbon 12 (Teensy 35, was the temperature encoder B); the centre knob's
        # A / B on 9 / 10 (Teensy 40 / 41) and its push on 11 (Teensy 34).
        "SN19": [("ROW1", "J4.3"), ("ROW2", "J4.4"), ("ROW3", "J4.5"), ("ROW4", "J4.12"),
                 ("COL1", "J4.6"), ("COL2", "J4.7"), ("COL3", "J4.8")],
        "SN20": [("ENC_CENTRE_A", "J4.9"), ("ENC_CENTRE_B", "J4.10"), ("ENC_CENTRE_PUSH", "J4.11"),
                 ("ENC_SEAT_DRV_A", "J4.13"), ("ENC_SEAT_DRV_B", "J4.14"), ("ENC_SEAT_PASS_A", "J4.15"),
                 ("ENC_SEAT_PASS_B", "J4.16")],
        "SN21": [("WAKE_T", "Q4.B")],
        "SN22": [("WIN_IN0", "U10.IN0"), ("WIN_IN1", "U10.IN1"), ("WIN_IN2", "U10.IN2"), ("WIN_IN3", "U10.IN3")],
        "SN23": [("REL_HATCH_T", "Q1.G"), ("REL_FUEL_T", "Q2.G")],
        # Y11 provisions: the A/C clutch stage is driven from expander U12 P17 only; the pressure
        # transducer (U15, over I2C) and the radar alert (U13 P01) have no Teensy pin of their own.
        "SN28": [], "SN29": [], "SN30": [],
    },
}
# Expander ports the record names, in the order it names them (SN17 "P00-P05 IN1/EN1-IN3/EN3" ...).
EXPECT_EXPANDER = {
    "dcu": {
        "SN24": [("PG_5V", "U1.PG")],
        "SN26": [("CAN_STB", "U3.STB")],
        "SN16": [("MH_DEN", "U9.DEN")],
        "SN17": [("MIR_IN1", "U11.IN1"), ("MIR_EN1", "U11.EN1"), ("MIR_IN2", "U11.IN2"), ("MIR_EN2", "U11.EN2"),
                 ("MIR_IN3", "U11.IN3"), ("MIR_EN3", "U11.EN3"), ("MIR_EN4", "U11.EN4"),
                 ("MIR_nSLEEP", "U11.nSLEEP"), ("MIR_nFAULT", "U11.nFAULT")],
        "SN22": [("WIN_DEN", "U10.DEN"), ("WIN_DSEL0", "U10.DSEL0"), ("WIN_DSEL1", "U10.DSEL1")],
        "SN28": [("AC_CLUTCH_CMD", "U14.IN")],
    },
}

BOARDS = {
    "icu": dict(sch="display-unit/cad/icu-carrier/icu-carrier.kicad_sch", channels="icu_channels.csv", teensy="J5",
                drops={"DP-ICU-A": "J1", "DP-ICU-B": "J3"}, rails=("+12V_LOGIC", "+12V_BL"),
                grounds=(), ground_bridge=()),
    "dcu": dict(sch="control-unit/cad/dcu-carrier/dcu-carrier.kicad_sch", channels="dcu_channels.csv", teensy="J10",
                expander="U12", ribbon="J4",
                drops={"DP-DCU": "J1", "DP-DCU-B": "J9", "DP-DCU-C": "J2"}, rails=("+12V_LOGIC", "+12V_CMF"),
                grounds=("GND", "PGND"), ground_bridge=("U4",)),
    # The panel board (Y20, D-492): J1 the ribbon; J3 the left plate's header, DP-DCU 36-47 pin for pin (D-582)
    # (the plate's keys and the stick are reached through it, not drawn here).
    "panel": dict(sch="control-unit/cad/panel/panel.kicad_sch", ribbon="J1", matrix=True, plate=("DP-DCU", "J3", 36)),
    # The climate unit's upper connector board (Y15, D-480, D-492): no processor, so each housing
    # is held against its cavities' src_note - the carrier header a lead goes to (carrier ref ->
    # this board's header for it), or the panel_ribbon line a conductor is, carried pin for pin.
    "upper": dict(sch="control-unit/cad/upper-board/upper-board.kicad_sch",
                  relay={"DP-DCU-D": ("J1", {"J6": "J3", "J7": "J4", "J8": "J5", "J5": "J6", "J3": "J7"}),
                         "DP-DCU-E": ("J2", "J8")}),
    # The left plate (Y21, D-492): J1 its cable header, DP-DCU-E pin for pin; the keys a DP-DCU-E
    # cavity names, on their rows and columns through their diodes; the stick on panel_ribbon 1, 17-20.
    # Its winks (Y22, D-499, D-504): J2 the wink lead, held to the L3-S1 cavities whose lands_on name it.
    "left-plate": dict(sch="control-unit/cad/left-plate/left-plate.kicad_sch", plate_board=("DP-DCU", "J1", 36),
                       winks=("L3-S1", "J2")),
}

# Symbol pin names and datasheet pin names that mean the same pin.
NAME_CLASSES = [
    {"VCC", "V+", "VDD"}, {"GND", "V-"}, {"IN+", "+"}, {"IN-", "-"},
    {"PAD", "THERMALPAD", "EP", "EPAD"}, {"NC", "N.C."},
    {"RESET", "NRESET", "/RESET"}, {"DRAIN", "D"}, {"SOURCE", "S"},
]


# --------------------------------------------------------------------------------------------
# The s-expression netlist
# --------------------------------------------------------------------------------------------
_TOK = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')


def parse_sexpr(text):
    stack = [[]]
    pos, n = 0, len(text)
    while pos < n:
        m = _TOK.match(text, pos)
        if not m or m.end() == pos:
            break
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            done = stack.pop()
            stack[-1].append(done)
        elif m.group(3) is not None:
            stack[-1].append(m.group(3).replace('\\"', '"'))
        else:
            stack[-1].append(m.group(4))
    if len(stack) != 1 or not stack[0]:
        raise ValueError("unbalanced s-expression")
    return stack[0][0]


def kids(node, key):
    return [k for k in node[1:] if isinstance(k, list) and k and k[0] == key]


def kid(node, key):
    ks = kids(node, key)
    return ks[0] if ks else None


def val(node, key, default=None):
    k = kid(node, key) if node is not None else None
    return k[1] if k and len(k) > 1 and not isinstance(k[1], list) else default


class Netlist:
    """comps: ref -> {value, part}; pins: ref -> {num: (name, type)};
    net_of: (ref, num) -> net; nets: net -> [(ref, num, name)]."""

    def __init__(self, text):
        root = parse_sexpr(text)
        self.comps, self.pins, self.net_of, self.nets = {}, {}, {}, {}
        lib = {}
        for lp in kids(kid(root, "libparts") or [], "libpart"):
            table = {}
            for p in kids(kid(lp, "pins") or [], "pin"):
                table[val(p, "num")] = (val(p, "name", ""), val(p, "type", ""))
            lib[(val(lp, "lib"), val(lp, "part"))] = table
        for c in kids(kid(root, "components") or [], "comp"):
            ref = val(c, "ref")
            src = kid(c, "libsource")
            key = (val(src, "lib"), val(src, "part"))
            self.comps[ref] = {"value": val(c, "value", ""), "part": key[1] or ""}
            self.pins[ref] = dict(lib.get(key, {}))
        for net in kids(kid(root, "nets") or [], "net"):
            name = val(net, "name")
            nodes = []
            for node in kids(net, "node"):
                ref, num = val(node, "ref"), val(node, "pin")
                self.net_of[(ref, num)] = name
                # the libpart's pin name, not the node's pinfunction (KiCad 10 suffixes that)
                nodes.append((ref, num, self.pin_name(ref, num) or val(node, "pinfunction", "")))
            self.nets[name] = nodes

    def pin_name(self, ref, num):
        return self.pins.get(ref, {}).get(num, ("", ""))[0]

    def net(self, ref, num):
        """The net a pin is on, or None when it is unconnected."""
        n = self.net_of.get((ref, num))
        if n is None or n.startswith("unconnected-"):
            return None
        return n

    def find_pin(self, spec):
        """'REF.NAME' or 'REF#NUM' -> (ref, num) or None."""
        if "#" in spec:
            ref, num = spec.split("#", 1)
            return (ref, num) if num in self.pins.get(ref, {}) else None
        ref, name = spec.split(".", 1)
        for num, (pname, _t) in self.pins.get(ref, {}).items():
            if pname == name:
                return (ref, num)
        return None


def bare(net):
    return net[1:] if net and net.startswith("/") else net


def is_power_net(net):
    return net is None or net.startswith("+") or "GND" in net.upper() or net.startswith("unconnected-")


def prefix(ref):
    return re.match(r"[A-Za-z]+", ref).group(0) if re.match(r"[A-Za-z]+", ref) else ref


# --------------------------------------------------------------------------------------------
# Walking the board: from a net, through parts, to see what a signal reaches.
# --------------------------------------------------------------------------------------------
PASSIVE = {"R", "C", "L", "F", "FB", "D", "JP", "SW", "RV"}


def channel_digit(name):
    """IN0 / OUT0 / EN1 / IPROPI3 -> the channel digit a multi-channel part's pin carries."""
    m = re.match(r"^[A-Za-z]+(\d)$", name or "")
    return m.group(1) if m else None


def reach(nl, start, stop_refs, through_actives):
    """Nets reachable from `start` without crossing a power net, as {net: (prev_net, ref, depth)}.
    Two-pin passives always pass; U and Q parts pass when through_actives, except the refs in
    stop_refs (the processor side), and inside a multi-channel part a pin stays in its channel:
    OUT0 reaches IN0 and DEN, never IN1."""
    seen = {start: (None, None, 0)}
    q = deque([start])
    while q:
        net = q.popleft()
        depth = seen[net][2]
        for ref, num, name in nl.nets.get(net, []):
            pfx = prefix(ref)
            if ref in stop_refs or pfx == "J":
                continue
            passes = (pfx in PASSIVE and len(nl.pins.get(ref, {})) <= 2) or \
                     (through_actives and pfx in ("U", "Q", "D", "JP", "SW"))
            if not passes:
                continue
            chan = channel_digit(name)
            for other, (oname, _t) in nl.pins.get(ref, {}).items():
                if other == num:
                    continue
                ochan = channel_digit(oname)
                if chan and ochan and chan != ochan:
                    continue
                nxt = nl.net_of.get((ref, other))
                if nxt is None or nxt in seen or is_power_net(nxt):
                    continue
                seen[nxt] = (net, ref, depth + 1)
                q.append(nxt)
    return seen


def path(seen, net):
    out = []
    while net is not None and seen.get(net) is not None and seen[net][0] is not None:
        prev, ref, _d = seen[net]
        out.append("%s -%s-> %s" % (bare(prev), ref, bare(net)))
        net = prev
    return " ; ".join(reversed(out))


# --------------------------------------------------------------------------------------------
# Reading the record
# --------------------------------------------------------------------------------------------
def read_csv(name):
    p = os.path.join(DATA, name)
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


_COMMENT = re.compile(r"\((?:not |D-\d|ribbon\b|ROW\d)[^()]*\)")  # a negation, a decision cite, a ribbon line
_MOVED = re.compile(r"\bTeensy\s+\d+\s+went\s+to\b[^·;]*")      # "Teensy 35 went to ROW4 (SN19)": another channel's pin
_DECISION = re.compile(r"\bD-\d+\b")
_UNIT = re.compile(r"\b\d+(?:\.\d+)?\s*(?:k?Hz|m?V|m?A|m?Ω|W|%)\b")
_PIN = re.compile(r"(?<![\w.])(\d{1,2})(?![\w.])")
_PORT = re.compile(r"\bP(\d{2})(?:\s*-\s*P(\d{2}))?\b")


_VIN = re.compile(r"\b(?:\d+\s+VIN|VIN\s+\d+|VIN)\b")


def record_pins(text):
    """The Teensy pins a `teensy_pin` cell names, in order: standalone numbers 0-54 after
    dropping decision cites, parentheses that negate ("(not ...)"), and numbers with a unit.
    'VIN' (the record writes the socket's pad, "48 VIN") comes through as the label VIN.
    A cell that opens with "none" names no pin, whatever candidates it goes on to list."""
    if re.match(r"\s*(none|nothing|—|-|GND)\b", text or ""):
        return []
    t = _UNIT.sub(" ", _DECISION.sub(" ", _COMMENT.sub(" ", _MOVED.sub(" ", text or ""))))
    t = _VIN.sub(" <VIN> ", t)
    out = []
    for m in re.finditer(r"<VIN>|" + _PIN.pattern, t):
        if m.group(0) == "<VIN>":
            out.append("VIN")
        elif int(m.group(1)) <= 54:
            out.append(m.group(1))
    return out


_STOP = set("a an and the to on in of at its own from into through out digital input output pwm adc "
            "command select return coil feed line signal node sense high side dcu timer apart servos "
            "expander with for by is as k".split())
_ALIAS = {"driver": "drv", "passenger": "pass", "fuel-door": "fuel", "left": "l", "right": "r"}


def words(text):
    """The words of a record cell that tell one pin or cavity from another."""
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z0-9-]*", (text or "").lower()):
        w = _ALIAS.get(w, w)
        if w not in _STOP and len(w) > 1:
            out.add(w)
    return out


def record_pin_words(text):
    """{pin: words} - the fragment of a `teensy_pin` cell that names each pin ("22 DRV up")."""
    if re.match(r"\s*(none|nothing|—|-|GND)\b", text or ""):
        return {}
    t = _UNIT.sub(" ", _DECISION.sub(" ", _COMMENT.sub(" ", _MOVED.sub(" ", text or ""))))
    t = _VIN.sub(" ", t)
    out = {}
    for frag in re.split(r"[·;,/]", t):
        frag = frag.split(" - ")[0]
        pins = [n for n in _PIN.findall(frag) if int(n) <= 54]
        if len(pins) == 1:
            out[pins[0]] = words(_PIN.sub(" ", frag))
    return out


def record_ports(text):
    """The expander ports a cell names (P00-P05 expands), in order."""
    out = []
    for a, b in _PORT.findall(_COMMENT.sub(" ", text or "")):
        lo, hi = int(a), int(b) if b else int(a)
        for n in range(lo, hi + 1):
            if n % 10 <= 7:
                out.append("P%02d" % n)
    return out


_DROP = re.compile(r"\b(DP-(?:ICU|DCU)(?:-[ABC])?)\s+(\d+)(?:\s*[-–]\s*(\d+)|((?:\s*/\s*\d+)+))?")


def record_drops(text):
    """(housing, cavity) pairs a cell names: 'DP-DCU 4 / 5', 'DP-DCU-B 5-8', 'DP-ICU-A 1'."""
    out = []
    for housing, a, b, slashes in _DROP.findall(text or ""):
        if b:
            out += [(housing, str(n)) for n in range(int(a), int(b) + 1)]
        elif slashes:
            out += [(housing, a)] + [(housing, n) for n in re.findall(r"\d+", slashes)]
        else:
            out.append((housing, a))
    return out


# --------------------------------------------------------------------------------------------
# The checks
# --------------------------------------------------------------------------------------------
class Report:
    def __init__(self, board, verbose):
        self.board, self.verbose = board, verbose
        self.mismatches, self.notes, self.checked = [], [], 0

    def ok(self, what):
        self.checked += 1
        if self.verbose:
            print("  ok   %s" % what)

    def bad(self, ref, pin, expected, got):
        self.checked += 1
        line = "%s:%s:%s expected %s got %s" % (self.board, ref, pin, expected, got)
        self.mismatches.append(line)
        print(line)

    def note(self, text):
        self.notes.append(text)
        print("note %s: %s" % (self.board, text))


def same_name(sym, ds):
    """A symbol pin name against a datasheet pin name: equal after normalising, or in one
    NAME_CLASSES set, or any '/'-separated part equal ('TX' matches 'D6/TX')."""
    def norm(s):
        s = s.strip().upper().replace("−", "-").replace("–", "-").replace(" ", "")
        s = re.sub(r"^[12](?=(IN[+-]|OUT)$)", "", s)      # 1IN+, 2OUT -> IN+, OUT
        return s
    a, b = {norm(x) for x in sym.split("/")}, {norm(x) for x in ds.split("/")}
    if a & b:
        return True
    for cls in NAME_CLASSES:
        if a & cls and b & cls:
            return True
    return False


def check_pin_on_net(rep, nl, ref, num, label, expected, far_end):
    """One record pin: the pad (ref, num) must be on `expected`, reaching `far_end`."""
    got = nl.net(ref, num)
    where = "%s(pin %s)" % (num, label)
    if got is None:
        rep.bad(ref, where, expected, "unconnected")
        return False
    if bare(got) != expected:
        rep.bad(ref, where, expected, bare(got))
        return False
    if far_end:
        target = nl.find_pin(far_end)
        if target is None:
            rep.bad(ref, where, "%s reaching %s" % (expected, far_end), "no such pin on the sheet")
            return False
        seen = reach(nl, got, set(), False)
        tnet = nl.net_of.get(target)
        if tnet not in seen:
            rep.bad(ref, where, "%s reaching %s" % (expected, far_end), "%s does not reach it" % bare(got))
            return False
        via = path(seen, tnet)
        rep.ok("%s %s = %s -> %s%s" % (ref, where, expected, far_end, (" via " + via) if via else ""))
        return True
    rep.ok("%s %s = %s" % (ref, where, expected))
    return True


def check_processor(rep, nl, cfg, rows):
    """Teensy pads and expander ports against teensy_pin, channel by channel."""
    sock, exp = cfg["teensy"], cfg.get("expander")
    expect, expect_x = EXPECT.get(rep.board, {}), EXPECT_EXPANDER.get(rep.board, {})
    claimed_pads, claimed_ports = {}, {}
    processor_nets = {}                      # channel -> {net: (pin label, record words)}
    for row in rows:
        cid = row["id"]
        pins = record_pins(row.get("teensy_pin", ""))
        ports = record_ports(row.get("teensy_pin", "")) if exp else []
        pin_words = record_pin_words(row.get("teensy_pin", ""))
        want, want_x = expect.get(cid), expect_x.get(cid, [])
        nets = {}
        if want is None:
            if pins:
                rep.bad(cid, "teensy_pin", "an EXPECT entry in check.py for pins %s" % ",".join(pins), "none")
            continue
        if len(pins) != len(want):
            rep.bad(cid, "teensy_pin", "%d pins in check.py's EXPECT (%s)" % (len(want), ", ".join(e if isinstance(e, str) else e[0] for e in want)),
                    "%d in the record (%s)" % (len(pins), ", ".join(pins)))
            continue
        for pin, entry in zip(pins, want):
            net, far = (entry, None) if isinstance(entry, str) else entry
            pad = TEENSY_PAD_OF.get(pin)
            if pad is None:
                rep.bad(cid, pin, "a Teensy 4.1 edge pin", "pin %s is not on the socket" % pin)
                continue
            if pad in claimed_pads:
                rep.bad(sock, "%s(pin %s)" % (pad, pin), "one channel", "%s and %s" % (claimed_pads[pad], cid))
            claimed_pads[pad] = cid
            if check_pin_on_net(rep, nl, sock, pad, pin, net, far):
                nets[nl.net(sock, pad)] = ("pin " + pin, pin_words.get(pin, set()))
        if exp:
            if len(ports) != len(want_x):
                rep.bad(cid, "teensy_pin", "%d expander ports in check.py's EXPECT_EXPANDER" % len(want_x),
                        "%d in the record (%s)" % (len(ports), ", ".join(ports)))
            else:
                for port, (net, far) in zip(ports, want_x):
                    pnum = None
                    for num, (name, _t) in nl.pins.get(exp, {}).items():
                        if name == port:
                            pnum = num
                    if pnum is None:
                        rep.bad(exp, port, "a port pin named %s" % port, "none")
                        continue
                    if port in claimed_ports:
                        rep.bad(exp, port, "one channel", "%s and %s" % (claimed_ports[port], cid))
                    claimed_ports[port] = cid
                    if check_pin_on_net(rep, nl, exp, pnum, port, net, far):
                        nets[nl.net(exp, pnum)] = (exp + " " + port, set())
        processor_nets[cid] = nets
    # Pads the sheet wires that no channel claims, and the DCU's self-naming pads (24_WIN_IN2).
    for pad, label in TEENSY_PADS.items():
        net = nl.net(sock, pad)
        name = nl.pin_name(sock, pad)
        m = re.match(r"(\d+)_", name or "")
        if m and m.group(1) != label:
            rep.bad(sock, pad, "a pin name starting %s_ (the card's pin for this pad)" % label, name)
        if label in ("GND", "3V3", "VIN"):
            want = {"GND": "GND", "3V3": "+3V3", "VIN": "+5V"}[label]
            if net != want:
                rep.bad(sock, "%s(%s)" % (pad, label), want, net or "unconnected")
            else:
                rep.ok("%s %s(%s) = %s" % (sock, pad, label, net))
            continue
        if net is not None and pad not in claimed_pads:
            rep.note("%s pad %s (pin %s) is wired to %s but no channel's teensy_pin names pin %s" % (sock, pad, label, bare(net), label))
    if exp:
        for num, (name, _t) in sorted(nl.pins.get(exp, {}).items(), key=lambda kv: int(kv[0])):
            if re.match(r"P[01][0-7]$", name) and name not in claimed_ports and nl.net(exp, num) is not None:
                rep.note("%s port %s is wired to %s but no channel names it" % (exp, name, bare(nl.net(exp, num))))
    return processor_nets


def check_drops(rep, nl, cfg, rows, cavities, processor_nets):
    """Board-edge connectors against at_the_drop and the cavities table."""
    stop = {cfg["teensy"], cfg.get("expander")} - {None}
    by_pin = {}
    for row in rows:
        for housing, cav in record_drops(row.get("at_the_drop", "")):
            by_pin.setdefault((housing, cav), []).append(row)
    # Cavities whose src names a channel (DP-DCU-C 1-4 -> SN16) count as that channel's drops.
    ids = {r["id"]: r for r in rows}
    for c in cavities:
        if c["housing"] in cfg["drops"]:
            for m in re.findall(r"\b(?:IC|SN)\d\d\b", c.get("src", "") + " " + c.get("circuit", "")):
                if m in ids and ids[m] not in by_pin.setdefault((c["housing"], c["cav"]), []):
                    by_pin[(c["housing"], c["cav"])].append(ids[m])
    for housing, conn in cfg["drops"].items():
        if conn not in nl.pins:
            rep.bad(conn, "-", "connector %s for %s" % (conn, housing), "no such part on the sheet")
            continue
        states = {c["cav"]: c["state"] for c in cavities if c["housing"] == housing}
        for num in sorted(nl.pins[conn], key=int):
            net = nl.net(conn, num)
            state = states.get(num)
            claimants = by_pin.get((housing, num), [])
            pin = "%s(%s %s)" % (num, housing, num)
            if state is None:
                rep.note("%s pin %s: no cavity row %s %s in the record" % (conn, num, housing, num))
            elif state == "PLUG":
                if net is not None and not claimants:
                    rep.bad(conn, pin, "unconnected (the cavity is a sealing plug no channel names)", bare(net))
                elif net is not None:
                    rep.note("%s pin %s is wired to %s behind a sealing plug - %s's footprint-only stage" % (
                        conn, pin, bare(net), ",".join(r["id"] for r in claimants)))
                else:
                    rep.ok("%s %s unconnected, a plug" % (conn, pin))
            elif net is None:
                live = [r for r in claimants if record_pins(r.get("teensy_pin", ""))]
                if live:
                    rep.bad(conn, pin, "wired (%s names it)" % ",".join(r["id"] for r in live), "unconnected")
                elif claimants:
                    rep.note("%s pin %s is unconnected; %s names the cavity (%s) but has no processor pin" % (
                        conn, pin, ",".join(r["id"] for r in claimants), state))
                else:
                    rep.note("%s pin %s is unconnected; the record has the cavity %s (%s)" % (conn, pin, state, states and "no channel names it"))
            else:
                rep.ok("%s %s = %s (%s)" % (conn, pin, bare(net), state))
            for row in claimants:
                if net is None:
                    continue
                if row.get("kind") == "power" or not processor_nets.get(row["id"]):
                    rep.ok("%s %s wired for %s (%s, no front end to walk)" % (conn, pin, row["id"], row.get("kind")))
                    continue
                targets = processor_nets[row["id"]]
                seen = reach(nl, net, stop, True)
                # where the record's words tell the channel's pins apart, the cavity must land
                # on the pin whose words match its circuit best (DRV up on "DRV up", not "DRV down")
                cav_words = words(next((c["circuit"] for c in cavities if c["housing"] == housing and c["cav"] == num), ""))
                score = {n: len(cav_words & w) for n, (_l, w) in targets.items()}
                hits = sorted(((-score[n], seen[n][2], n) for n in targets if n in seen))
                if not hits:
                    rep.bad(conn, pin, "a path to %s's processor pins (%s)" % (row["id"], ",".join(bare(n) for n in sorted(targets))),
                            "%s reaches none of them" % bare(net))
                    continue
                hit = hits[0][2]
                label = targets[hit][0]
                best = max(score.values())
                if best and score[hit] < best:
                    want = ", ".join("%s (%s)" % (targets[n][0], bare(n)) for n, s in sorted(score.items()) if s == best)
                    rep.bad(conn, pin, "%s - the record's words for the cavity" % want, "%s (%s)" % (label, bare(hit)))
                else:
                    rep.ok("%s %s reaches %s %s at %s via %s" % (conn, pin, row["id"], label, bare(hit), path(seen, hit) or "direct"))


def check_ribbon(rep, nl, cfg, ribbon):
    """The ribbon header (26-way since D-458) against panel_ribbon: pin n is on the conductor's signal net."""
    hdr = cfg["ribbon"]
    on_dcu = rep.board == "dcu"
    for row in ribbon:
        pin, sig = row["pin"], row["signal"]
        net = nl.net(hdr, pin)
        want = sig if sig.startswith("+") or sig == "GND" else sig
        if sig == "AGND" and on_dcu:
            want = "GND"                  # "analog ground, joined to GND at the carrier"
        if net is None:
            rep.bad(hdr, pin, want, "unconnected")
        elif bare(net) != want:
            rep.bad(hdr, pin, want, bare(net))
        else:
            rep.ok("%s %s = %s" % (hdr, pin, want))
    for num in nl.pins.get(hdr, {}):
        if num not in {r["pin"] for r in ribbon} and nl.net(hdr, num) is not None:
            rep.bad(hdr, num, "no conductor (panel_ribbon has no pin %s)" % num, bare(nl.net(hdr, num)))


_CARRIER_PIN = re.compile(r"\bJ(\d+)(?:\s*-\s*J(\d+))?\s+pin\s+(\d+)")
_RIBBON_LINE = re.compile(r"\bpanel_ribbon\s+(\d+)")


def check_relay(rep, nl, cfg, cavities, ribbon):
    """A board with no processor (the upper connector board): every cavity of each housing on its
    receptacle pin - wired when the record has it LIVE or CAPPED, bare when a PLUG - on a net of
    its own (no two cavities joined, so a return never shares another's conductor), and reaching
    what its src_note names: 'the carrier's J6 pin 1' / 'J6-J8 pin 2' on this board's header for
    that carrier header, pin for pin; 'panel_ribbon 3' on the straight-through header's same pin,
    the net named as panel_ribbon names the line."""
    signal = {r["pin"]: r["signal"] for r in ribbon}
    for housing, (conn, far) in cfg["relay"].items():
        rows = sorted((c for c in cavities if c["housing"] == housing), key=lambda c: int(c["cav"]))
        if conn not in nl.pins:
            rep.bad(conn, "-", "connector %s for %s" % (conn, housing), "no such part on the sheet")
            continue
        if not rows:
            rep.bad(conn, "-", "cavity rows for %s in the record" % housing, "none")
            continue
        owner = {}
        carried = set()
        for c in rows:
            cav, state = c["cav"], c["state"]
            pin = "%s(%s %s)" % (cav, housing, cav)
            net = nl.net(conn, cav)
            if state == "PLUG":
                if net is None:
                    rep.ok("%s %s unconnected, a plug" % (conn, pin))
                else:
                    rep.bad(conn, pin, "unconnected (the cavity is a sealing plug)", bare(net))
                continue
            if net is None:
                rep.bad(conn, pin, "wired (the cavity is %s)" % state, "unconnected")
                continue
            if net in owner:
                rep.bad(conn, pin, "a net of its own", "%s, joined to cavity %s" % (bare(net), owner[net]))
            owner[net] = cav
            carried.add(net)
            note = c.get("src_note", "")
            if isinstance(far, dict):
                hits = []
                for a, b, p in _CARRIER_PIN.findall(note):
                    for n in range(int(a), int(b or a) + 1):
                        hits.append(("J%d" % n, p))
                if not hits:
                    rep.bad(conn, pin, "a carrier header pin in src_note", repr(note))
                for carrier_ref, p in hits:
                    hdr = far.get(carrier_ref)
                    if hdr is None:
                        rep.bad(conn, pin, "a header on this board for the carrier's %s" % carrier_ref, "none in check.py")
                    elif nl.net(hdr, p) != net:
                        rep.bad(hdr, p, "%s (%s %s, to the carrier's %s pin %s)" % (bare(net), housing, cav, carrier_ref, p),
                                bare(nl.net(hdr, p) or "") or "unconnected")
                    else:
                        rep.ok("%s %s = %s -> %s.%s (the carrier's %s pin %s)" % (conn, pin, bare(net), hdr, p, carrier_ref, p))
            else:
                lines = _RIBBON_LINE.findall(note)
                if len(lines) != 1 or lines[0] not in signal:
                    rep.bad(conn, pin, "one panel_ribbon line in src_note", repr(note))
                    continue
                want = signal[lines[0]]
                if bare(net) != want:
                    rep.bad(conn, pin, "%s (panel_ribbon %s)" % (want, lines[0]), bare(net))
                elif nl.net(far, cav) != net:
                    rep.bad(far, cav, "%s, straight through from %s %s" % (want, conn, cav),
                            bare(nl.net(far, cav) or "") or "unconnected")
                else:
                    rep.ok("%s %s = %s (panel_ribbon %s) -> %s.%s" % (conn, pin, want, lines[0], far, cav))
        for num in nl.pins[conn]:
            if num not in {c["cav"] for c in rows} and nl.net(conn, num) is not None:
                rep.bad(conn, num, "no cavity row %s %s in the record" % (housing, num), bare(nl.net(conn, num)))
        for hdr in (far.values() if isinstance(far, dict) else [far]):
            for num in nl.pins.get(hdr, {}):
                n = nl.net(hdr, num)
                if n is not None and n not in carried:
                    rep.bad(hdr, num, "a net one of %s's cavities carries" % housing, bare(n))


def parts_on(nl, net, pfx=None):
    return [(ref, num, name) for ref, num, name in nl.nets.get(net, []) if pfx is None or prefix(ref) == pfx]


def key_name(nl, ref):
    v = nl.comps.get(ref, {}).get("value", "")
    return re.sub(r"^(key|encoder)\s*-\s*", "", v).strip().lower()


def _side(text):
    """A panel_side cell without its parentheses and its ' - ' commentary."""
    t = re.sub(r"\([^()]*\)", " ", text or "")
    return re.sub(r"\s+", " ", t.split(" - ")[0]).strip()


def _key(k):
    return re.sub(r"[\s-]+", " ", k.strip().lower())


def key_contacts(nl, ref):
    """{pin on the diode side: (key name, pin on the column side)} for one matrix switch: a plain
    key's two pins either way round, or a window switch's poles (D-492) - COM_n to its diode and
    whichever of UP_n / DN_n is wired to the column, the key named '<value> up' or '<value> down'."""
    pins = nl.pins.get(ref, {})
    base = _key(key_name(nl, ref))
    if len(pins) == 2:
        a, b = list(pins)
        return {a: (base, b), b: (base, a)}
    out = {}
    for num, (pname, _t) in pins.items():
        m = re.match(r"COM_(\d+)$", pname)
        if not m:
            continue
        wired = [(n2, pn2) for n2, (pn2, _t2) in pins.items()
                 if re.match(r"(UP|DN)_%s$" % m.group(1), pn2) and nl.net(ref, n2) is not None]
        if len(wired) == 1:
            out[num] = ("%s %s" % (base, "up" if wired[0][1].startswith("UP") else "down"), wired[0][0])
    return out


def board_keys(nl):
    """{key name: (row net, column net, ref)} for every key reached row -> diode K..A -> switch -> column."""
    out = {}
    for ref in nl.comps:
        if prefix(ref) != "SW" or nl.comps[ref]["value"].lower().startswith("encoder"):
            continue
        for snum, (kname, cnum) in key_contacts(nl, ref).items():
            anet = nl.net(ref, snum)
            ds = parts_on(nl, anet, "D") if anet else []
            if len(ds) != 1 or ds[0][2] != "A":
                continue
            knum = [n for n, (pn, _t) in nl.pins[ds[0][0]].items() if pn == "K"]
            out[kname] = (bare(nl.net(ds[0][0], knum[0]) or "") if knum else "", bare(nl.net(ref, cnum) or ""), ref)
    return out


def _plate(t):
    """(housing, header, first cavity) from a plate config: header pin n is cavity first + n - 1
    (D-582: the CUR's lines are DP-DCU 36-47 in the Control Unit's one plug; before it DP-DCU-E 1-12)."""
    return t[0], t[1], int(t[2]) if len(t) > 2 else 1


def _in_plate(c, housing, lo):
    return c["housing"] == housing and lo <= int(c["cav"]) <= lo + 11


def _pin(cav, lo):
    return str(int(cav) - lo + 1)


def plate_keys(cavities, housing, signal, lo=1):
    """{key name: (header pin, the panel_ribbon signal it carries)} for each '... - the <name> key'
    cavity."""
    out = {}
    for c in cavities:
        if not _in_plate(c, housing, lo):
            continue
        m = re.search(r"\bthe ([\w -]+?) key\b", c.get("circuit", ""))
        lines = _RIBBON_LINE.findall(c.get("src_note", ""))
        if m and len(lines) == 1:
            out[_key(m.group(1))] = (_pin(c["cav"], lo), signal.get(lines[0]))
    return out


def check_plate(rep, nl, cfg, cavities, ribbon):
    """The plate header (D-492): pin n is DP-DCU-E cavity n, on the net of the panel_ribbon line its
    src_note names - the same net as that ribbon pin on J1 (AGND stays AGND on the panel)."""
    housing, conn, lo = _plate(cfg["plate"])
    hdr = cfg["ribbon"]
    signal = {r["pin"]: r["signal"] for r in ribbon}
    rows = sorted((c for c in cavities if _in_plate(c, housing, lo)), key=lambda c: int(c["cav"]))
    if conn not in nl.pins:
        rep.bad(conn, "-", "the plate header for %s" % housing, "no such part on the sheet")
        return
    if not rows:
        rep.bad(conn, "-", "cavity rows for %s in the record" % housing, "none")
        return
    for c in rows:
        cav = c["cav"]
        pin = _pin(cav, lo)
        lines = _RIBBON_LINE.findall(c.get("src_note", ""))
        if len(lines) != 1 or lines[0] not in signal:
            rep.bad(conn, pin, "one panel_ribbon line in %s %s's src_note" % (housing, cav), repr(c.get("src_note", "")))
            continue
        want = signal[lines[0]]
        got = nl.net(conn, pin)
        if got is None or bare(got) != want:
            rep.bad(conn, "%s(%s %s)" % (pin, housing, cav), "%s (panel_ribbon %s)" % (want, lines[0]), bare(got) or "unconnected")
        elif nl.net(hdr, lines[0]) != got:
            rep.bad(conn, "%s(%s %s)" % (pin, housing, cav), "the same net as %s %s" % (hdr, lines[0]), bare(nl.net(hdr, lines[0])) or "unconnected")
        else:
            rep.ok("%s %s(%s %s) = %s = %s %s" % (conn, pin, housing, cav, want, hdr, lines[0]))
    for num in nl.pins[conn]:
        if num not in {_pin(c["cav"], lo) for c in rows} and nl.net(conn, num) is not None:
            rep.bad(conn, num, "no cavity row %s %s in the record" % (housing, int(num) + lo - 1), bare(nl.net(conn, num)))


def check_panel(rep, nl, cfg, ribbon, cavities=()):
    """What hangs off each conductor on the panel, and the matrix diodes' orientation. A key the
    record puts on the left plate is held to the plate header instead: a DP-DCU-E cavity names it
    ('the hatch key') on the column the record gives it, and the header carries the row too."""
    hdr = cfg["ribbon"]
    housing, plate, lo = _plate(cfg["plate"]) if cfg.get("plate") else (None, None, 1)
    signal = {r["pin"]: r["signal"] for r in ribbon}
    pkeys = plate_keys(cavities, housing, signal, lo) if housing else {}
    found = board_keys(nl)
    placed = set()
    for row in ribbon:
        sig, side, pin = row["signal"], row["panel_side"], row["pin"]
        net = nl.net(hdr, pin)
        if net is None:
            continue
        if plate:
            for cav in re.findall(r"\b%s\s+(\d+)" % re.escape(housing), side):
                hp = _pin(cav, lo)
                if nl.net(plate, hp) == net:
                    rep.ok("%s %s: on %s %s (%s %s)" % (hdr, sig, plate, hp, housing, cav))
                else:
                    rep.bad(plate, hp, "%s (panel_ribbon %s names %s %s)" % (sig, pin, housing, cav), bare(nl.net(plate, hp)) or "unconnected")
        m = re.match(r"keys:\s*(.*)", side)
        enc = re.match(r"(.*?)\s*encoder\s+(A|B|push)\b", _side(side), re.I)
        if m:
            want = [_key(k) for k in _side(m.group(1)).split("·")]
            for i, k in enumerate(want, 1):
                col = "COL%d" % i
                if k == "spare":
                    extra = [n for n, (r, c, _ref) in found.items() if r == sig and c == col]
                    if extra:
                        rep.bad(hdr, pin, "nothing at %s / %s (a spare)" % (sig, col), ", ".join(extra))
                    else:
                        rep.ok("%s %s: %s spare" % (hdr, sig, col))
                elif k in found:
                    placed.add(k)
                    r, c, ref = found[k]
                    if r != sig or c != col:
                        rep.bad(ref, "-", "key '%s' at %s / %s" % (k, sig, col), "%s / %s" % (r, c))
                    else:
                        rep.ok("%s %s: key '%s' (%s) via its diode to %s" % (hdr, sig, k, ref, col))
                elif k in pkeys and plate:
                    cav, csig = pkeys[k]
                    rnets = {nl.net(plate, n) for n in nl.pins.get(plate, {})}
                    if csig != col:
                        rep.bad(plate, cav, "key '%s' on %s (%s %s)" % (k, col, housing, cav), csig)
                    elif bare(nl.net(plate, cav) or "") != col:
                        rep.bad(plate, cav, "%s for the plate's key '%s'" % (col, k), bare(nl.net(plate, cav)) or "unconnected")
                    elif net not in rnets:
                        rep.bad(plate, "-", "%s on the plate header for its key '%s'" % (sig, k), "not on %s" % plate)
                    else:
                        rep.ok("%s %s: key '%s' on the left plate, %s %s = %s" % (hdr, sig, k, plate, cav, col))
                else:
                    rep.bad(hdr, pin, "key '%s' at %s / %s" % (k, sig, col),
                            "not on this board (keys found: %s) nor named by a %s cavity" % (", ".join(sorted(found)) or "none", housing))
        elif enc and not side.startswith("encoder commons"):
            name, phase = enc.group(1).strip().lower(), enc.group(2)
            if phase.lower() == "push":
                hits = [(r, n, pn) for r, n, pn in parts_on(nl, net, "SW") if key_name(nl, r) == name and pn in ("S1", "S2")]
                other = [n for r, n0, pn in hits for n, (pn2, _t) in nl.pins[r].items() if pn2 in ("S1", "S2") and n != n0]
                ok = bool(hits) and all(nl.net(hits[0][0], n) == "GND" for n in other) and other
                if ok:
                    rep.ok("%s %s: %s encoder push, the other side on GND" % (hdr, sig, name))
                else:
                    rep.bad(hdr, pin, "%s encoder push (S1 / S2) between %s and GND" % (name, sig),
                            ", ".join("%s.%s" % (r, pn) for r, n, pn in parts_on(nl, net)) or "nothing")
            else:
                hits = [(r, n, pn) for r, n, pn in parts_on(nl, net, "SW") if key_name(nl, r) == name and pn == phase.upper()]
                if hits:
                    rep.ok("%s %s: %s encoder %s" % (hdr, sig, name, phase.upper()))
                else:
                    rep.bad(hdr, pin, "%s encoder pin %s on %s" % (name, phase.upper(), sig), ", ".join("%s.%s" % (r, pn) for r, n, pn in parts_on(nl, net)) or "nothing")
        elif side.startswith("encoder commons"):
            encs = [r for r in nl.comps if r.startswith("SW") and nl.comps[r]["value"].lower().startswith("encoder")]
            for r in encs:
                cnum = [n for n, (pn, _t) in nl.pins[r].items() if pn == "C"]
                if not cnum or nl.net(r, cnum[0]) != net:
                    rep.bad(r, "C", "on %s" % sig, bare(nl.net(r, cnum[0]) if cnum else None) or "unconnected")
                else:
                    rep.ok("%s %s: %s common" % (hdr, sig, key_name(nl, r)))
        elif "thumbstick" in side and "left plate" not in side:
            want = {"X wiper": ["X_WIPER"], "Y wiper": ["Y_WIPER"], "push switch": ["SW_A", "SW_B"],
                    "pot supply": ["X_VCC", "Y_VCC"], "pot ground": ["X_GND", "Y_GND"]}
            for phrase, pins in want.items():
                if phrase in side:
                    names = {pn for r, n, pn in parts_on(nl, net, "U")}
                    if names & set(pins):
                        rep.ok("%s %s: thumbstick %s" % (hdr, sig, "/".join(sorted(names & set(pins)))))
                    else:
                        rep.bad(hdr, pin, "thumbstick %s on %s" % ("/".join(pins), sig), ", ".join(sorted(names)) or "nothing")
        elif "column" in side:
            keys = sorted(k for k, (r, c, _ref) in found.items() if c == sig)
            rep.ok("%s %s: keys %s" % (hdr, sig, ", ".join(keys) or "none on this board"))
    for k, (r, c, ref) in sorted(found.items()):
        if k not in placed:
            rep.bad(ref, "-", "only the record's keys on the board", "also '%s' at %s / %s" % (k, r, c))
    # every matrix diode, whichever row it is on: K on a row, A to one switch contact whose
    # column side is a COL net
    for ref in nl.comps:
        if prefix(ref) != "D" or len(nl.pins.get(ref, {})) != 2:
            continue
        knum = [n for n, (pn, _t) in nl.pins[ref].items() if pn == "K"]
        anum = [n for n, (pn, _t) in nl.pins[ref].items() if pn == "A"]
        if not knum or not anum:
            continue
        knet, anet = bare(nl.net(ref, knum[0]) or ""), nl.net(ref, anum[0])
        if not re.match(r"ROW\d$", knet):
            rep.bad(ref, knum[0], "K on a ROW net", knet or "unconnected")
        sws = parts_on(nl, anet, "SW") if anet else []
        cols = []
        if len(sws) == 1:
            kc = key_contacts(nl, sws[0][0]).get(sws[0][1])
            cols = [bare(nl.net(sws[0][0], kc[1]) or "")] if kc else []
        if len(sws) != 1 or not cols or not re.match(r"COL\d$", cols[0]):
            rep.bad(ref, anum[0], "A to one key whose other pin is a COL net", bare(anet) if anet else "unconnected")
        else:
            rep.ok("%s K on %s, A to %s.%s -> %s" % (ref, knet, sws[0][0], sws[0][2], cols[0]))


def check_plate_board(rep, nl, cfg, cavities, ribbon):
    """The left plate itself (Y21, D-492). Its cable header: DP-DCU-E cavity n on pin n, on the net the
    cavity's src_note panel_ribbon line names, each on a net of its own. Its keys: every key a DP-DCU-E
    cavity names ('the hatch key') reached row -> 1N4148W K..A -> key -> column, on the row panel_ribbon's
    'keys:' line puts it and the column its cavity carries, both on the header, and no other key on the
    board. Its stick: the pins panel_ribbon gives the thumbstick on the plate (X / Y wiper, the push to
    GND, the pot supply, the pot ground) on those lines. Its lights: the bus lines reach a driver's SDA /
    SCL. The wink switches are check_winks' (J2, D-504)."""
    housing, conn, lo = _plate(cfg["plate_board"])
    signal = {r["pin"]: r["signal"] for r in ribbon}
    rows = sorted((c for c in cavities if _in_plate(c, housing, lo)), key=lambda c: int(c["cav"]))
    if conn not in nl.pins:
        rep.bad(conn, "-", "the plate's cable header for %s" % housing, "no such part on the sheet")
        return
    if not rows:
        rep.bad(conn, "-", "cavity rows for %s in the record" % housing, "none")
        return
    owner = {}
    for c in rows:
        cav = c["cav"]
        pin = "%s(%s %s)" % (_pin(cav, lo), housing, cav)
        got = nl.net(conn, _pin(cav, lo))
        if c["state"] == "PLUG":
            if got is None:
                rep.ok("%s %s unconnected, a plug" % (conn, pin))
            else:
                rep.bad(conn, pin, "unconnected (the cavity is a sealing plug)", bare(got))
            continue
        lines = _RIBBON_LINE.findall(c.get("src_note", ""))
        if len(lines) != 1 or lines[0] not in signal:
            rep.bad(conn, pin, "one panel_ribbon line in src_note", repr(c.get("src_note", "")))
            continue
        want = signal[lines[0]]
        if got is None or bare(got) != want:
            rep.bad(conn, pin, "%s (panel_ribbon %s)" % (want, lines[0]), bare(got) or "unconnected")
        elif got in owner:
            rep.bad(conn, pin, "a net of its own", "%s, joined to cavity %s" % (bare(got), owner[got]))
        else:
            rep.ok("%s %s = %s (panel_ribbon %s)" % (conn, pin, want, lines[0]))
        owner[got] = cav
    for num in nl.pins[conn]:
        if num not in {_pin(c["cav"], lo) for c in rows} and nl.net(conn, num) is not None:
            rep.bad(conn, num, "no cavity row %s %s in the record" % (housing, int(num) + lo - 1), bare(nl.net(conn, num)))
    on_hdr = {bare(nl.net(conn, n)) for n in nl.pins[conn] if nl.net(conn, n)}
    # the keys
    pkeys = plate_keys(cavities, housing, signal, lo)
    found = board_keys(nl)
    key_row = {}
    for r in ribbon:
        m = re.match(r"keys:\s*(.*)", r["panel_side"])
        if m:
            for k in _side(m.group(1)).split("·"):
                key_row[_key(k)] = r["signal"]
    if not pkeys:
        rep.bad(conn, "-", "the keys %s's cavities name ('the ... key')" % housing, "none in the record")
    for k, (cav, col) in sorted(pkeys.items()):
        row = key_row.get(k)
        if k not in found:
            rep.bad(conn, cav, "key '%s' on the board: %s -> diode -> key -> %s" % (k, row, col),
                    "not found (keys found: %s)" % (", ".join(sorted(found)) or "none"))
            continue
        r, c, ref = found[k]
        if r != row or c != col:
            rep.bad(ref, "-", "key '%s' at %s / %s" % (k, row, col), "%s / %s" % (r, c))
        elif row not in on_hdr or col not in on_hdr:
            rep.bad(conn, "-", "%s and %s on %s for the key '%s'" % (row, col, conn, k), "not both")
        else:
            rep.ok("key '%s' (%s) on %s / %s, %s %s" % (k, ref, row, col, housing, cav))
    for k, (r, c, ref) in sorted(found.items()):
        if k not in pkeys:
            rep.bad(ref, "-", "only the keys %s names" % housing, "also '%s' at %s / %s" % (k, r, c))
    for ref in nl.comps:
        if prefix(ref) != "D" or len(nl.pins.get(ref, {})) != 2:
            continue
        knum = [n for n, (pn, _t) in nl.pins[ref].items() if pn == "K"]
        anum = [n for n, (pn, _t) in nl.pins[ref].items() if pn == "A"]
        if not knum or not anum:
            continue
        knet = bare(nl.net(ref, knum[0]) or "")
        sws = parts_on(nl, nl.net(ref, anum[0]), "SW") if nl.net(ref, anum[0]) else []
        if not re.match(r"ROW\d$", knet) or len(sws) != 1:
            rep.bad(ref, knum[0], "K on a ROW net, A to one key", "%s / %d keys" % (knet or "unconnected", len(sws)))
        else:
            rep.ok("%s K on %s, A to %s" % (ref, knet, sws[0][0]))
    # the stick
    sticks = [r for r in nl.comps if {"X_WIPER", "Y_WIPER"} <= {pn for pn, _t in nl.pins[r].values()}]
    if len(sticks) != 1:
        rep.bad("-", "-", "one thumbstick (X_WIPER / Y_WIPER pins)", "%d" % len(sticks))
    else:
        st = sticks[0]
        net_of = {pn: bare(nl.net(st, num) or "") for num, (pn, _t) in nl.pins[st].items()}
        want = {"X wiper": ["X_WIPER"], "Y wiper": ["Y_WIPER"], "pot supply": ["X_VCC", "Y_VCC"],
                "pot ground": ["X_GND", "Y_GND"]}
        for r in ribbon:
            side, sig = r["panel_side"], r["signal"]
            if "thumbstick" not in side or "left plate" not in side:
                continue
            for phrase, pins in want.items():
                if phrase in side:
                    if all(net_of.get(p) == sig for p in pins):
                        rep.ok("%s %s on %s (panel_ribbon %s)" % (st, "/".join(pins), sig, r["pin"]))
                    else:
                        rep.bad(st, "/".join(pins), "%s (panel_ribbon %s, %s)" % (sig, r["pin"], phrase),
                                "/".join(net_of.get(p) or "unconnected" for p in pins))
            if "push switch" in side:
                ends = sorted([net_of.get("SW_A") or "", net_of.get("SW_B") or ""])
                other = "GND" if "to GND" in side else None
                if sig in ends and (other is None or other in ends) and ends[0] != ends[1]:
                    rep.ok("%s push between %s and %s" % (st, sig, other or "its other side"))
                else:
                    rep.bad(st, "SW_A/SW_B", "%s and %s (panel_ribbon %s)" % (sig, other, r["pin"]), "/".join(e or "unconnected" for e in ends))
    # the lights' bus
    for sig, pname in (("PNL_SDA", "SDA"), ("PNL_SCL", "SCL")):
        net = next((n for n in nl.nets if bare(n) == sig), None)
        hits = [ref for ref, _n, pn in (parts_on(nl, net, "U") if net else []) if pn == pname]
        if hits:
            rep.ok("%s reaches %s.%s" % (sig, hits[0], pname))
        else:
            rep.bad("-", sig, "the plate's LED driver %s" % pname, "nothing")


# The wink switches' contacts, as KiCad's SW_Push_SPDT draws them: the pole B rests on A (NC), C is NO.
SPDT_ROLE = {"NC": "A", "common": "B", "NO": "C"}
_HDR_PIN = re.compile(r"\b(J\d+) pin (\d+)\b")
_WINK_SIDE = re.compile(r"\bwink\s+(left|right|l|r)\b", re.I)
_WINK_RES = re.compile(r"\bwink\s+(left|right|l|r)\s+NO\s+through\s+(\d+(?:\.\d+)?)\s*([kM]?)\s*(?:Ω|ohm)", re.I)


def ohms(text):
    """'18k', '18 kΩ', '4.7k', '100' -> ohms as a float, or None."""
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*([kKmM]?)", text or "")
    if not m:
        return None
    return float(m.group(1)) * {"": 1, "k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6}[m.group(2)]


def _wside(text):
    m = _WINK_SIDE.search(text or "")
    return m.group(1)[0].upper() if m else None


def check_winks(rep, nl, cfg, cavities):
    """The left plate's wink switches and their lead (D-499, D-504). Every cavity of the wink lead's
    housing whose lands_on names a pin of the plate's wink header ('J2 pin 1') is held to it, fragment
    by fragment (split on ';'): an NC terminal is that side's SPDT A pin on that header pin, a common is
    its B pin there - a net of its own, never the plate's GND or a J1 line (the winks return to the dash
    post) - and 'the wink resistors ... on J2 pin n' means each 'wink L NO through 18 kΩ' the row names
    is one resistor of that value from that side's C pin (nothing else on it) to that header pin. No
    other pin of the header is wired, and no wink switch the record does not name is on the board."""
    housing, hdr = cfg["winks"]
    if hdr not in nl.pins:
        rep.bad(hdr, "-", "the wink lead's header for %s" % housing, "no such part on the sheet")
        return
    sw = {}
    for ref in nl.comps:
        names = {pn for pn, _t in nl.pins.get(ref, {}).values()}
        if prefix(ref) == "SW" and names == set(SPDT_ROLE.values()) and "wink" in nl.comps[ref]["value"].lower():
            m = re.search(r"\b(left|right)\b", nl.comps[ref]["value"], re.I)      # 'wink - left (P204)'
            side = m.group(1)[0].upper() if m else None
            if side in sw:
                rep.bad(ref, "-", "one wink switch a side", "%s and %s both on %s" % (sw[side], ref, side))
            sw[side] = ref

    def pin_net(ref, role):
        num = [n for n, (pn, _t) in nl.pins[ref].items() if pn == SPDT_ROLE[role]]
        return nl.net(ref, num[0]) if num else None

    plate_hdr = cfg.get("plate_board", (None, None))[1]
    plate_nets = {nl.net(plate_hdr, n) for n in nl.pins.get(plate_hdr, {})} - {None}
    named, sides = set(), set()
    rows = [c for c in cavities if c["housing"] == housing and any(
        h == hdr for h, _p in _HDR_PIN.findall(c.get("lands_on", "")))]
    if not rows:
        rep.bad(hdr, "-", "%s cavities whose lands_on names %s" % (housing, hdr), "none in the record")
        return
    for c in sorted(rows, key=lambda c: int(c["cav"])):
        for frag in c["lands_on"].split(";"):
            hits = [p for h, p in _HDR_PIN.findall(frag) if h == hdr]
            if len(hits) != 1:
                continue
            pin = hits[0]
            where = "%s(%s %s)" % (pin, housing, c["cav"])
            named.add(pin)
            hnet = nl.net(hdr, pin)
            if hnet is None:
                rep.bad(hdr, where, "wired (%s)" % frag.strip(), "unconnected")
                continue
            side = _wside(frag) or _wside(c["circuit"])
            if re.search(r"\bresistors?\b", frag):
                want = [(m[0][0].upper(), ohms(m[1] + m[2])) for m in _WINK_RES.findall(c["circuit"] + " " + c["lands_on"])]
                if not want:
                    rep.bad(hdr, where, "'wink L NO through <value>' in %s %s" % (housing, c["cav"]), "none")
                for s, r_ohms in want:
                    sides.add(s)
                    if s not in sw:
                        rep.bad(hdr, where, "a wink %s switch for its %g Ω" % (s, r_ohms), "none on the board")
                        continue
                    no = pin_net(sw[s], "NO")
                    rs = [ref for ref, _n, _pn in parts_on(nl, hnet, "R") if no and
                          no in {nl.net(ref, k) for k in nl.pins[ref]} and len(nl.pins[ref]) == 2]
                    vals = [ohms(nl.comps[r]["value"]) for r in rs]
                    if len(rs) != 1:
                        rep.bad(hdr, where, "one resistor from %s NO to it" % sw[s], ", ".join(rs) or "none")
                    elif vals[0] != r_ohms:
                        rep.bad(rs[0], "-", "%g Ω (%s %s: wink %s NO through it)" % (r_ohms, housing, c["cav"], s), nl.comps[rs[0]]["value"])
                    elif len(nl.nets.get(no, [])) != 2:
                        rep.bad(sw[s], SPDT_ROLE["NO"], "only %s on its NO" % rs[0], ", ".join("%s.%s" % (r, n) for r, n, _p in nl.nets[no]))
                    else:
                        rep.ok("%s %s: wink %s NO (%s.C) through %s %s" % (hdr, where, s, sw[s], rs[0], nl.comps[rs[0]]["value"]))
                continue
            role = "NC" if re.search(r"\bNC\b", frag) else "common" if re.search(r"\bcommons?\b", frag) else None
            if role is None or side is None:
                rep.bad(hdr, where, "a wink side and contact (NC, common) or the resistors", repr(frag.strip()))
                continue
            sides.add(side)
            if side not in sw:
                rep.bad(hdr, where, "a wink %s switch (SPDT, A / B / C)" % side, "none on the board")
                continue
            got = pin_net(sw[side], role)
            if got != hnet:
                rep.bad(sw[side], SPDT_ROLE[role], "%s on %s %s (%s %s)" % (role, hdr, pin, housing, c["cav"]), bare(got) or "unconnected")
            elif role == "common" and (bare(hnet) == "GND" or hnet in plate_nets):
                rep.bad(hdr, where, "the winks' own return to the dash post", "%s, the plate's own" % bare(hnet))
            else:
                rep.ok("%s %s: wink %s %s (%s.%s) on %s" % (hdr, where, side, role, sw[side], SPDT_ROLE[role], bare(hnet)))
    for num in nl.pins[hdr]:
        if num not in named and nl.net(hdr, num) is not None:
            rep.bad(hdr, num, "a pin some %s cavity's lands_on names" % housing, bare(nl.net(hdr, num)))
    for s, ref in sorted(sw.items()):
        if s not in sides:
            rep.bad(ref, "-", "only the winks %s names" % housing, "also a wink %s" % s)


def check_conventions(rep, nl, cfg):
    """CONVENTIONS.md §5: the rails never meet; every BAT54S A on GND, K on +3V3."""
    rails = cfg.get("rails", ())
    grounds = cfg.get("grounds", ())
    for ref, pins in nl.pins.items():
        nets = {nl.net_of.get((ref, n)) for n in pins} - {None}
        if rails and set(rails) <= nets:
            rep.bad(ref, "-", "pins on at most one of %s" % "/".join(rails), "both")
        if grounds and set(grounds) <= nets and ref not in cfg.get("ground_bridge", ()):
            rep.bad(ref, "-", "pins on at most one of %s" % "/".join(grounds), "both")
    for ref, c in nl.comps.items():
        if "BAT54S" not in c["value"].upper() and "BAT54S" not in c["part"].upper():
            continue
        a, k = nl.net(ref, "1"), nl.net(ref, "2")
        if a != "GND":
            rep.bad(ref, "1(A)", "GND", a or "unconnected")
        if k != "+3V3":
            rep.bad(ref, "2(K)", "+3V3", k or "unconnected")
        if a == "GND" and k == "+3V3":
            rep.ok("%s BAT54S A on GND, K on +3V3" % ref)
    if rails:
        rep.ok("no part on both %s and %s" % rails)


def load_pin_tables():
    tables = {}
    if not os.path.exists(PIN_TABLES):
        return tables
    with open(PIN_TABLES, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tables.setdefault(row["part"], []).append(row)
    return tables


def norm_part(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def check_pin_tables(rep, nl, tables):
    """Each functional-block symbol's pin number -> name against the vendor table. A transistor
    or a diode (Q, D) is held to its table too when pin_tables.csv has one for its value (Y42:
    a P-FET drawn gate / drain / source on a SOT-23, a zener's cathode on the package's unused
    pin and six one-way TVS diodes drawn with two anodes were each found by hand); one with no
    table: a transistor is noted, as an IC is (its pin order is the thing that goes wrong); a
    diode is passed over - most are two-pin parts whose direction the netlist checks hold."""
    keys = sorted(tables, key=len, reverse=True)
    for ref in sorted(nl.comps, key=lambda r: (prefix(r), int(re.sub(r"\D", "", r) or 0))):
        if prefix(ref) not in ("U", "Q", "D"):
            continue
        value, part = nl.comps[ref]["value"], nl.comps[ref]["part"]
        hit = None
        for k in keys:
            if norm_part(value).startswith(norm_part(k)) or norm_part(part).startswith(norm_part(k)):
                hit = k
                break
        if hit is None:
            if prefix(ref) in ("U", "Q"):
                rep.note("%s (%s) has no pin table in pin_tables.csv" % (ref, value))
            continue
        rows = tables[hit]
        package = rows[0]["package"]
        ds = {r["pin"]: r["name"] for r in rows}
        # PAD / TAB rows are unnumbered in the datasheet: matched by name, not by number
        unnumbered = {num: name for num, name in ds.items() if not num.isdigit()}
        sym = nl.pins.get(ref, {})
        bad = 0
        for num in sorted(sym, key=lambda n: (len(n), n)):
            sname = sym[num][0]
            if num in ds:
                if sname and not same_name(sname, ds[num]):
                    rep.bad(ref, num, "%s (%s %s)" % (ds[num], hit, package), sname)
                    bad += 1
            elif sname and any(same_name(sname, n) for n in unnumbered.values()) and not num.isdigit():
                pass
            elif sname and any(same_name(sname, n) and same_name(n, "PAD") for n in unnumbered.values()):
                pass                                    # the symbol's thermal pad, numbered by KiCad
            else:
                rep.bad(ref, num, "no pin %s on the %s (%s)" % (num, hit, package), sname or "(unnamed)")
                bad += 1
        for num, name in ds.items():
            if num.isdigit():
                if num not in sym and not same_name("NC", name):
                    rep.bad(ref, num, "%s (%s %s)" % (name, hit, package), "no such pin on the symbol")
                    bad += 1
            elif not any(same_name(sname, name) for sname, _t in sym.values()):
                rep.note("%s has no %s pin for the %s's %s" % (ref, name, hit, num))
        if not bad:
            rep.ok("%s pins match the %s %s table" % (ref, hit, package))


# --------------------------------------------------------------------------------------------
def export_netlist(cli, sch, out):
    cmd = [cli, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out, sch]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return "kicad-cli failed: %s" % e
    if r.returncode != 0 or not os.path.exists(out):
        return "kicad-cli rc %d: %s" % (r.returncode, (r.stderr or b"").decode("utf-8", "replace").strip()[-400:])
    return None


def find_kicad_cli():
    p = shutil.which("kicad-cli")
    if p:
        return p
    for c in KICAD_CLI_CANDIDATES:
        if os.access(c, os.X_OK):
            return c
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("-v", "--verbose", action="store_true", help="print every check that passed")
    ap.add_argument("--board", choices=sorted(BOARDS), action="append", help="only this board (repeatable)")
    ap.add_argument("--netlists", metavar="DIR", help="read DIR/<board>.net instead of running kicad-cli")
    ap.add_argument("--kicad-cli", metavar="PATH", help="the kicad-cli to run")
    args = ap.parse_args(argv)
    boards = args.board or sorted(BOARDS)

    for name in ("icu_channels.csv", "dcu_channels.csv", "panel_ribbon.csv", "cavities.csv"):
        if not os.path.exists(os.path.join(DATA, name)):
            print("cannot read %s" % os.path.join(DATA, name))
            return 3
    cli = None
    if not args.netlists:
        cli = args.kicad_cli or find_kicad_cli()
        if cli is None:
            print("kicad-cli not found - the schematics were not checked against the record")
            return 3
    try:
        ribbon = read_csv("panel_ribbon.csv")
        cavities = read_csv("cavities.csv")
        tables = load_pin_tables()
    except OSError as e:
        print("cannot read the record: %s" % e)
        return 3

    tmp = tempfile.mkdtemp(prefix="rx7-cad-check-")
    total_bad, total_notes, rc = 0, 0, 0
    try:
        for board in boards:
            cfg = BOARDS[board]
            sch = os.path.join(DESIGN, cfg["sch"])
            if args.netlists:
                netfile = os.path.join(args.netlists, board + ".net")
            else:
                if not os.path.exists(sch):
                    print("%s: cannot read %s" % (board, sch))
                    return 3
                netfile = os.path.join(tmp, board + ".net")
                err = export_netlist(cli, sch, netfile)
                if err:
                    print("%s: %s" % (board, err))
                    return 3
            try:
                with open(netfile, encoding="utf-8") as f:
                    nl = Netlist(f.read())
            except (OSError, ValueError) as e:
                print("%s: cannot read the netlist: %s" % (board, e))
                return 3
            rep = Report(board, args.verbose)
            if "channels" in cfg:
                rows = read_csv(cfg["channels"])
                pnets = check_processor(rep, nl, cfg, rows)
                check_drops(rep, nl, cfg, rows, cavities, pnets)
            if cfg.get("ribbon"):
                check_ribbon(rep, nl, cfg, ribbon)
            if cfg.get("matrix"):
                check_panel(rep, nl, cfg, ribbon, cavities)
            if cfg.get("plate"):
                check_plate(rep, nl, cfg, cavities, ribbon)
            if cfg.get("relay"):
                check_relay(rep, nl, cfg, cavities, ribbon)
            if cfg.get("plate_board"):
                check_plate_board(rep, nl, cfg, cavities, ribbon)
            if cfg.get("winks"):
                check_winks(rep, nl, cfg, cavities)
            check_conventions(rep, nl, cfg)
            check_pin_tables(rep, nl, tables)
            n = len(rep.mismatches)
            total_bad += n
            total_notes += len(rep.notes)
            print("%s: %d checks, %d mismatch%s, %d note%s (%s: %d parts, %d nets)" % (
                board, rep.checked, n, "" if n == 1 else "es", len(rep.notes), "" if len(rep.notes) == 1 else "s",
                os.path.basename(cfg["sch"]), len(nl.comps), len(nl.nets)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if total_bad:
        print("%d mismatch%s - the record is right and the sheet is stale (00-design/README.md)" % (total_bad, "" if total_bad == 1 else "es"))
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
