#!/usr/bin/env python3
"""check.py - the three KiCad sheets against the record and the datasheets (work row Y3).

Reads (never writes) the record's tables - these are the facts it holds the drawings to:
  ../../data/icu_channels.csv   id, kind, at_the_drop, teensy_pin  (the ICU carrier, J5)
  ../../data/dcu_channels.csv   the same for the DCU carrier (J10, expander U12)
  ../../data/panel_ribbon.csv   pin, signal, panel_side             (DCU J4 and the panel's J1)
  ../../data/cavities.csv       housing, cav, state                 (which board-edge pins must be wired)
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
  * the panel matrix diodes: cathode to the row, anode toward the column (panel/README.md);
  * the two rules CONVENTIONS.md §5 asks for: the two 12 V inputs share no part (and on the
    DCU no part but the INA180 touches both GND and PGND), and every BAT54S has A on GND and
    K on +3V3;
  * each functional-block symbol's pin number -> name against pin_tables.csv.

Exit codes: 0 everything matches; 1 any mismatch (each printed as
`board:ref:pin expected X got Y`); 3 kicad-cli missing or a file unreadable. Notes (things
worth a look that are not contradictions) print with a `note` prefix and never fail.

    python3 check.py [-v] [--board icu|dcu|panel] [--netlists DIR]

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
        "SN19": [("ROW1", "J4.3"), ("ROW2", "J4.4"), ("ROW3", "J4.5"), ("COL1", "J4.6"), ("COL2", "J4.7"), ("COL3", "J4.8")],
        "SN20": [("ENC_FAN_A", "J4.9"), ("ENC_FAN_B", "J4.10"), ("ENC_TEMP_A", "J4.11"), ("ENC_TEMP_B", "J4.12"),
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
    "icu": dict(sch="icu-carrier/icu-carrier.kicad_sch", channels="icu_channels.csv", teensy="J5",
                drops={"DP-ICU-A": "J1", "DP-ICU-B": "J3"}, rails=("+12V_LOGIC", "+12V_BL"),
                grounds=(), ground_bridge=()),
    "dcu": dict(sch="dcu-carrier/dcu-carrier.kicad_sch", channels="dcu_channels.csv", teensy="J10",
                expander="U12", ribbon="J4",
                drops={"DP-DCU": "J1", "DP-DCU-B": "J9", "DP-DCU-C": "J2"}, rails=("+12V_LOGIC", "+12V_CMF"),
                grounds=("GND", "PGND"), ground_bridge=("U4",)),
    "panel": dict(sch="panel/panel.kicad_sch", ribbon="J1", matrix=True),
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


_COMMENT = re.compile(r"\((?:not |D-\d)[^()]*\)")               # a negation or a decision cite
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
    t = _UNIT.sub(" ", _DECISION.sub(" ", _COMMENT.sub(" ", text or "")))
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
    t = _UNIT.sub(" ", _DECISION.sub(" ", _COMMENT.sub(" ", text or "")))
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


def parts_on(nl, net, pfx=None):
    return [(ref, num, name) for ref, num, name in nl.nets.get(net, []) if pfx is None or prefix(ref) == pfx]


def key_name(nl, ref):
    v = nl.comps.get(ref, {}).get("value", "")
    return re.sub(r"^(key|encoder)\s*-\s*", "", v).strip().lower()


def check_panel(rep, nl, cfg, ribbon):
    """What hangs off each conductor on the panel, and the matrix diodes' orientation."""
    hdr = cfg["ribbon"]
    rows_keys = {}                                      # ROWn -> [key names in column order]
    for row in ribbon:
        sig, side, pin = row["signal"], row["panel_side"], row["pin"]
        net = nl.net(hdr, pin)
        if net is None:
            continue
        m = re.match(r"keys:\s*(.*)", side)
        if m:
            want = [k.strip().lower() for k in m.group(1).split("·")]
            rows_keys[sig] = want
            # row net -> diode cathodes -> anode nets -> one key each, whose other pin is COLi
            found = {}
            for dref, dnum, dname in parts_on(nl, net, "D"):
                if dname != "K":
                    rep.bad(dref, dnum, "K on %s (cathode to the row)" % sig, "%s on %s" % (dname, sig))
                    continue
                anum = [n for n in nl.pins[dref] if n != dnum][0]
                anet = nl.net(dref, anum)
                keys = parts_on(nl, anet, "SW") if anet else []
                if len(keys) != 1:
                    rep.bad(dref, anum, "one key on the anode net", "%d" % len(keys))
                    continue
                sref, snum, _ = keys[0]
                onum = [n for n in nl.pins[sref] if n != snum][0]
                col = bare(nl.net(sref, onum) or "")
                found[key_name(nl, sref)] = col
            for i, k in enumerate(want, 1):
                if k not in found:
                    rep.bad(hdr, pin, "key '%s' on %s" % (k, sig), "not on this row (keys found: %s)" % ", ".join(sorted(found)) or "none")
                elif found[k] != "COL%d" % i:
                    rep.bad(hdr, pin, "key '%s' in column COL%d" % (k, i), found[k])
                else:
                    rep.ok("%s %s: key '%s' via its diode to COL%d" % (hdr, sig, k, i))
            for k in found:
                if k not in want:
                    rep.bad(hdr, pin, "only the record's keys on %s" % sig, "also '%s'" % k)
        elif "encoder" in side and not side.startswith("encoder commons"):
            name = side.split("encoder")[0].strip().lower()
            phase = side.split()[-1].strip().upper()
            hits = [(r, n, pn) for r, n, pn in parts_on(nl, net, "SW") if key_name(nl, r) == name and pn == phase]
            if hits:
                rep.ok("%s %s: %s encoder %s" % (hdr, sig, name, phase))
            else:
                rep.bad(hdr, pin, "%s encoder pin %s on %s" % (name, phase, sig), ", ".join("%s.%s" % (r, pn) for r, n, pn in parts_on(nl, net)) or "nothing")
        elif side.startswith("encoder commons"):
            encs = [r for r in nl.comps if r.startswith("SW") and nl.comps[r]["value"].lower().startswith("encoder")]
            for r in encs:
                cnum = [n for n, (pn, _t) in nl.pins[r].items() if pn == "C"]
                if not cnum or nl.net(r, cnum[0]) != net:
                    rep.bad(r, "C", "on %s" % sig, bare(nl.net(r, cnum[0]) if cnum else None) or "unconnected")
                else:
                    rep.ok("%s %s: %s common" % (hdr, sig, key_name(nl, r)))
        elif "thumbstick" in side:
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
            m2 = re.search(r"column (\d)", side)
            col = int(m2.group(1)) if m2 else None
            keys = sorted(key_name(nl, r) for r, n, pn in parts_on(nl, net, "SW"))
            rep.ok("%s %s: keys %s" % (hdr, sig, ", ".join(keys)))
            if col and len(keys) != 3:
                rep.bad(hdr, pin, "three keys on COL%d" % col, "%d (%s)" % (len(keys), ", ".join(keys)))
    # every matrix diode, whichever row it is on
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
        if len(sws) != 1 or not re.match(r"COL\d$", bare(nl.net(sws[0][0], [n for n in nl.pins[sws[0][0]] if n != sws[0][1]][0]) or "")):
            rep.bad(ref, anum[0], "A to one key whose other pin is a COL net", bare(anet) if anet else "unconnected")


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
    """Each functional-block symbol's pin number -> name against the vendor table."""
    keys = sorted(tables, key=len, reverse=True)
    for ref in sorted(nl.comps, key=lambda r: (prefix(r), int(re.sub(r"\D", "", r) or 0))):
        if prefix(ref) != "U":
            continue
        value, part = nl.comps[ref]["value"], nl.comps[ref]["part"]
        hit = None
        for k in keys:
            if norm_part(value).startswith(norm_part(k)) or norm_part(part).startswith(norm_part(k)):
                hit = k
                break
        if hit is None:
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
            sch = os.path.join(HERE, cfg["sch"])
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
                check_panel(rep, nl, cfg, ribbon)
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
        print("%d mismatch%s - the record is right and the sheet is stale (cad/README.md)" % (total_bad, "" if total_bad == 1 else "es"))
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
