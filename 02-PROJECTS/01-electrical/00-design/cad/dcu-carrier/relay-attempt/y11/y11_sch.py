#!/usr/bin/env python3
"""Y11 step 1: the DCU sheet gets the open blocks' worst case (D-455).

U13 (second TCA9539-Q1, 0x75, fitted) takes SEAT_STATUS (P00) and the radar alert (P01); U12 P17 drives the A/C clutch stage U14 (BTT6050-1ERA, DNP) out on DP-DCU-B 12;
U15 ADS1115-Q1 (0x48, DNP) reads the A/C pressure transducer and the sensor supply
from U16 TPS7B4250-Q1 (DNP); J2 pin 8 lands on PGND (01.26 (a)). Text-level S-expression surgery,
coordinates on the 2.54 mm grid, the same helpers as Y5's y5_sch.py.
"""
import re, uuid, os

D = "/Users/crash/dev/Rx7/02-PROJECTS/01-electrical/00-design/cad/dcu-carrier"
SCH = os.path.join(D, "dcu-carrier.kicad_sch")
LIB = os.path.join(D, "dcu-carrier.kicad_sym")
SHEET_UUID = "9652d84f-b171-4144-b035-f61cf665afb4"
POWER = {"GND", "+3V3", "+12V_LOGIC", "+12V_CMF", "+5V", "+5V_SERVO", "PGND"}
TI = "https://www.ti.com/lit/ds/symlink/"
DS = {"ADS1115-Q1": TI + "ads1115-q1.pdf", "TPS7B4250-Q1": TI + "tps7b4250-q1.pdf",
      "TCA9539-Q1": TI + "tca9539-q1.pdf", "BTT6050-1ERA": "https://www.farnell.com/datasheets/2873425.pdf"}


def U():
    return str(uuid.uuid4())


def f(v):
    s = "%.2f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s


# ------------------------------------------------------------------ new library symbols
def pin(name, num, x, y, rot):
    return ('\t\t\t(pin passive line (at %s %s %d) (length 2.54) (name "%s" (effects (font (size 1.27 1.27)))) '
            '(number "%s" (effects (font (size 1.27 1.27)))))\n' % (f(x), f(y), rot, name, num))


def symbol(name, desc, halfw, top, bottom, left, right, ds, fp):
    s = '\t(symbol "%s"\n\t\t(pin_names (offset 1.016))\n\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)\n' % name
    s += '\t\t(property "Reference" "U" (at 0 %s 0) (effects (font (size 1.27 1.27))))\n' % f(top + 1.27)
    s += '\t\t(property "Value" "%s" (at 0 %s 0) (effects (font (size 1.27 1.27))))\n' % (name, f(bottom - 1.27))
    s += '\t\t(property "Footprint" "%s" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n' % fp
    s += '\t\t(property "Datasheet" "%s" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n' % ds
    s += '\t\t(property "Description" "%s" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n' % desc
    s += '\t\t(symbol "%s_0_1"\n\t\t\t(rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) (fill (type background)))\n\t\t)\n' % (
        name, f(-halfw), f(top), f(halfw), f(bottom))
    s += '\t\t(symbol "%s_1_1"\n' % name
    for n, num, y in left:
        s += pin(n, num, -(halfw + 2.54), y, 0)
    for n, num, y in right:
        s += pin(n, num, halfw + 2.54, y, 180)
    s += '\t\t)\n\t)\n'
    return s


def col(items, ytop):
    return [(n, num, ytop - 2.54 * i) for i, (n, num) in enumerate(items)]


NEWSYMS = {
    "ADS1115-Q1": symbol(
        "ADS1115-Q1",
        "TI ADS1115-Q1 16-bit 4-channel I2C ADC, VSSOP-10 (DGS): 1 ADDR, 2 ALERT/RDY, 3 GND, 4-7 AIN0-AIN3, 8 VDD, 9 SDA, 10 SCL (SBAS563E table 5-1); ADDR to GND = 0x48 (table 8-2)",
        7.62, 7.62, -10.16,
        col([("VDD", "8"), ("GND", "3"), ("ADDR", "1"), ("SDA", "9"), ("SCL", "10"), ("ALERT/RDY", "2")], 5.08),
        col([("AIN0", "4"), ("AIN1", "5"), ("AIN2", "6"), ("AIN3", "7")], 5.08),
        DS["ADS1115-Q1"], "Package_SO:MSOP-10_3x3mm_P0.5mm"),
    "TPS7B4250-Q1": symbol(
        "TPS7B4250-Q1",
        "TI TPS7B4250-Q1 50 mA 40 V voltage-tracking LDO for off-board sensors, SOT-23-5 (DBV): 1 ADJ/EN, 2 GND, 3 VIN, 4 VOUT, 5 GND (SLVSCA0C p.4); short-to-battery and reverse-polarity proof",
        7.62, 5.08, -7.62,
        col([("VIN", "3"), ("ADJ/EN", "1"), ("GND", "2"), ("GND", "5")], 2.54),
        col([("VOUT", "4")], 2.54),
        DS["TPS7B4250-Q1"], "Package_TO_SOT_SMD:SOT-23-5"),
}

lib = open(LIB).read()
for name, text in NEWSYMS.items():
    assert '(symbol "%s"' % name not in lib, name
    k = lib.rstrip().rfind(")")
    lib = lib[:k].rstrip("\n") + "\n" + text + ")\n"
open(LIB, "w").write(lib)


def lib_pins(name):
    m = re.search(r'\n\t\(symbol "%s"\n.*?\n\t\)\n' % re.escape(name), lib, re.S)
    return [(pn, num, float(x), float(y), int(r)) for x, y, r, pn, num in
            re.findall(r'\(pin \w+ line \(at ([-\d.]+) ([-\d.]+) (\d+)\) \(length [\d.]+\)\s*\(name "([^"]*)"[^\n]*?\(number "([^"]*)"', m.group(0))]


# ------------------------------------------------------------------ sheet helpers
sch = open(SCH).read()

# the cached copies in lib_symbols
i = sch.index("(lib_symbols")
depth, k = 0, i
while True:
    c = sch[k]
    if c == "(":
        depth += 1
    elif c == ")":
        depth -= 1
        if depth == 0:
            break
    k += 1
cache = ""
for name, text in NEWSYMS.items():
    t = text.replace('\t(symbol "%s"\n' % name, '\t(symbol "dcu-carrier:%s"\n' % name, 1)
    cache += "".join("\t" + ln + "\n" for ln in t.rstrip("\n").split("\n"))
sch = sch[:k] + cache + "\t" + sch[k:]


def blocks(text):
    out, i = [], 0
    while True:
        j = text.find("\n\t(", i)
        if j < 0:
            break
        j += 2
        depth, k, n = 0, j, len(text)
        while k < n:
            c = text[k]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        out.append((j, k + 1))
        i = k + 1
    return out


def stub(net, x, y, side):
    if side == "L":
        x2 = x - 2.54
        w = '\t(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (f(x), f(y), f(x2), f(y), U())
        if net in POWER:
            l = '\t(global_label "%s" (shape passive) (at %s %s 180) (effects (font (size 1.27 1.27)) (justify right)) (uuid "%s"))\n' % (net, f(x2), f(y), U())
        else:
            l = '\t(label "%s" (at %s %s 180) (effects (font (size 1.27 1.27)) (justify right bottom)) (uuid "%s"))\n' % (net, f(x2), f(y), U())
    else:
        x2 = x + 2.54
        w = '\t(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (f(x), f(y), f(x2), f(y), U())
        if net in POWER:
            l = '\t(global_label "%s" (shape passive) (at %s %s 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "%s"))\n' % (net, f(x2), f(y), U())
        else:
            l = '\t(label "%s" (at %s %s 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "%s"))\n' % (net, f(x2), f(y), U())
    return w + l


def nc(x, y):
    return '\t(no_connect (at %s %s) (uuid "%s"))\n' % (f(x), f(y), U())


def remove_at(text, kinds, pt):
    """drop the top-level element of one of `kinds` whose first (at x y) / (xy x y) is pt."""
    for a, b in blocks(text):
        blk = text[a:b]
        kind = blk[1:].split(None, 1)[0]
        if kind not in kinds:
            continue
        m = re.search(r'\((?:at|xy) ([-\d.]+) ([-\d.]+)', blk)
        if (round(float(m.group(1)), 2), round(float(m.group(2)), 2)) == pt:
            return text[:a - 2] + text[b:]
    raise KeyError((kinds, pt))


pwr_n = [max(int(x) for x in re.findall(r'"#PWR(\d+)"', sch))]


def power_symbol(net, x, y):
    pwr_n[0] += 1
    ref = "#PWR%03d" % pwr_n[0]
    vy = y + 4.5 if net in ("GND", "PGND") else y - 4.5
    return ('\t(symbol (lib_id "dcu-carrier:%s") (at %s %s 0) (unit 1) (body_style 1)\n'
            '\t\t(exclude_from_sim no) (in_bom no) (on_board yes) (in_pos_files yes) (dnp no)\n'
            '\t\t(uuid "%s")\n'
            '\t\t(property "Reference" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
            '\t\t(property "Value" "%s" (at %s %s 0) (effects (font (size 1.1 1.1))))\n'
            '\t\t(property "Footprint" "" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
            '\t\t(property "Datasheet" "" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
            '\t\t(pin "1" (uuid "%s"))\n'
            '\t\t(instances (project "dcu-carrier" (path "/%s" (reference "%s") (unit 1))))\n'
            '\t)\n' % (net, f(x), f(y), U(), ref, f(x), f(y), net, f(x), f(vy), f(x), f(y), f(x), f(y), U(), SHEET_UUID, ref))


def instance(lib_id, ref, value, fp, x, y, pins, dnp, note, ds="", ref_at=None, val_at=None, just="left"):
    ra = ref_at or (x + 3, y - 1.2)
    va = val_at or (x + 3, y + 1.6)
    j = " (justify left)" if just == "left" else ""
    s = ('\t(symbol (lib_id "dcu-carrier:%s") (at %s %s 0) (unit 1) (body_style 1)\n'
         '\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes) (dnp %s)\n'
         '\t\t(uuid "%s")\n'
         '\t\t(property "Reference" "%s" (at %s %s 0) (effects (font (size 1.1 1.1))%s))\n'
         '\t\t(property "Value" "%s" (at %s %s 0) (effects (font (size 1.1 1.1))%s))\n'
         '\t\t(property "Footprint" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
         '\t\t(property "Datasheet" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
         '\t\t(property "Note" "%s" (at %s %s 0) (effects (font (size 1.1 1.1)) (hide yes)))\n'
         % (lib_id, f(x), f(y), "yes" if dnp else "no", U(), ref, f(ra[0]), f(ra[1]), j, value, f(va[0]), f(va[1]), j,
            fp, f(x), f(y), ds, f(x), f(y), note, f(x), f(y)))
    s += ''.join('\t\t(pin "%s" (uuid "%s"))\n' % (p, U()) for p in pins)
    s += '\t\t(instances (project "dcu-carrier" (path "/%s" (reference "%s") (unit 1))))\n\t)\n' % (SHEET_UUID, ref)
    return s


R08 = "Resistor_SMD:R_0805_2012Metric"
C08 = "Capacitor_SMD:C_0805_2012Metric"


def two_pin(lib_id, ref, value, fp, x, y, top, bottom, dnp, note):
    s = instance(lib_id, ref, value, fp, x, y, ["1", "2"], dnp, note)
    for net, y1, y2, ang, just in ((top, y - 3.81, y - 6.35, 90, "left bottom"), (bottom, y + 3.81, y + 6.35, 270, "right bottom")):
        s += '\t(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (f(x), f(y1), f(x), f(y2), U())
        if net in POWER:
            s += power_symbol(net, x, y2)
        else:
            s += '\t(label "%s" (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))\n' % (net, f(x), f(y2), ang, just, U())
    return s


def ic(name, ref, value, fp, x, y, nets, dnp, note):
    """nets: {(pinname, number): net or None (no-connect)}"""
    pins = lib_pins(name)
    top = max(py for _, _, _, py, _ in pins)
    bot = min(py for _, _, _, py, _ in pins)
    s = instance(name, ref, value, fp, x, y, [num for _, num, _, _, _ in pins], dnp, note, DS.get(name, ""),
                 ref_at=(x, y - top - 3.81), val_at=(x, y - bot + 3.81), just="centre")
    for pn, num, px, py, r in pins:
        net = nets.get((pn, num), nets.get(pn, "MISSING"))
        assert net != "MISSING", (ref, pn, num)
        if net is None:
            s += nc(x + px, y - py)
        else:
            s += stub(net, x + px, y - py, "L" if r == 0 else "R")
    return s


def bat54s(ref, x, y, net, dnp, note):
    s = instance("BAT54S", ref, "BAT54S", "Package_TO_SOT_SMD:SOT-23", x, y, ["1", "2", "3"], dnp, note)
    s += stub("GND", x - 7.62, y, "L") + stub("+3V3", x + 7.62, y, "R")
    s += '\t(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (f(x), f(y + 5.08), f(x), f(y + 7.62), U())
    s += '\t(label "%s" (at %s %s 270) (effects (font (size 1.27 1.27)) (justify right bottom)) (uuid "%s"))\n' % (net, f(x), f(y + 7.62), U())
    return s


def conn(lib_id, ref, value, fp, x, y, nets, dnp, note):
    n = len(nets)
    s = instance(lib_id, ref, value, fp, x, y, [str(i + 1) for i in range(n)], dnp, note,
                 ref_at=(x, y - 6.35), val_at=(x, y + 2.54 * n + 1.27), just="centre")
    for i, net in enumerate(nets):
        s += stub(net, x - 7.62, y - 2.54 + 2.54 * i, "L")
    return s


def text(s, x, y, size=1.5, bold=False):
    b = " (bold yes)" if bold else ""
    return ('\t(text "%s" (exclude_from_sim no) (at %s %s 0) (effects (font (size %s %s)%s) (justify left top)) (uuid "%s"))\n'
            % (s, f(x), f(y), f(size), f(size), b, U()))


add = []
CL = "02.15 (b) only - DNP until engine block 02.15 answers; "
RD = "luxury 03.12 / Z-002 only - DNP until the receiver is chosen; "

# ---- the block
add.append('\t(rectangle (start 580 236) (end 1040 486) (stroke (width 0.2032) (type dash)) (fill (type none)) (uuid "%s"))\n' % U())
add.append(text("PROVISIONS (Y11) - the open blocks' worst case, drawn in so an answer is a fitting change, not a redesign (D-455)", 583, 239, 3.2, True))

# ---- U13: the second expander
add.append(text("U13  second expander TCA9539-Q1 at 0x75 (A0 high, A1 low) - FITTED: P00 SEAT_STATUS (moved from U12 P17), P01 the radar alert", 584, 249, 1.5, True))
add.append(text("Same I2C bus as U12 (R51 / R52). INT wired-OR on EXP_INT (both open-drain, one pull-up R53, Teensy 12); RESET shared on EXP_RESET (R54 holds both in reset):", 584, 253.5))
add.append(text("one pin left on the Teensy for neither, and a reset must leave every output stage off on both expanders at once. P02-P17 unused: firmware sets them outputs, low.", 584, 257))
u13 = {"VCC": "+3V3", "GND": "GND", "A0": "+3V3", "A1": "GND", "SDA": "I2C_SDA", "SCL": "I2C_SCL", "INT": "EXP_INT",
       "RESET": "EXP_RESET", "P00": "SEAT_STATUS", "P01": "RADAR_ALERT"}
for p in ("P02", "P03", "P04", "P05", "P06", "P07", "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17"):
    u13[p] = None
add.append(ic("TCA9539-Q1", "U13", "TCA9539-Q1", "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", 622.3, 289.56, u13, False,
              "Y11: second expander, address 0x75 (A0 high, A1 low; U12 is 0x74) - confirm on the bus scan; fitted, it carries SEAT_STATUS"))
add.append(two_pin("C", "C38", "100n  U13 VCC", C08, 655.32, 279.4, "+3V3", "GND", False, "U13 bypass"))

# ---- U14: the A/C clutch high side
add.append(text("A/C CLUTCH  block 02.15 (b) - DNP: U12 P17 -> U14 BTT6050-1ERA high side, fed from V12C_RAW, out on DP-DCU-B 12", 690, 262, 1.5, True))
add.append(text("Fed from the comfort input ahead of D3 (the B560C carries only the servo rail and mirror heat); the coil returns at the compressor body (engine ground),", 690, 266.5))
add.append(text("never through the DCU. F29 is 7.5 A for servo + mirror heat today: with a ~4 A coil it needs 10 A - confirm (V-101). The coil carries its own diode (EAS 60 mJ).", 690, 270))
u14 = {"VS": "V12C_RAW", "IN": "AC_IN", "DEN": "AC_DEN_R", "IS": "AC_IS", "GND": "AC_GND", "OUT": "AC_CLUTCH"}
add.append(ic("BTT6050-1ERA", "U14", "BTT6050-1ERA", "dcu-carrier:Infineon_PG-TSDSO-14-22", 721.36, 284.48, u14, True,
              CL + "A/C clutch high side: IL(NOM) 4.5 A at 85 C against a ~4 A coil - confirm the coil current; a lower-RON PROFET if it is over 3.5 A; the coil must carry its own suppression diode (EAS 60 mJ) - confirm"))
for ref, val, x, top, bot, note in (
        ("R59", "4.7k", 749.3, "AC_CLUTCH_CMD", "AC_IN", "IN series, as R21"),
        ("R60", "10k  off at reset", 769.62, "AC_CLUTCH_CMD", "GND", "holds IN low while the expander ports are inputs"),
        ("R61", "4.7k  DEN low", 789.94, "AC_DEN_R", "GND", "DEN held low: diagnostics off, IS unread - as U9 / U10 (D-452)"),
        ("R62", "1.2k  IS unread", 810.26, "AC_IS", "GND", "R_IS, as R24: the IS pin is never left open"),
        ("R63", "47R  PROFET ground", 830.58, "AC_GND", "GND", "PROFET ground resistor, as R25")):
    add.append(two_pin("R", ref, val, R08, x, 297.18, top, bot, True, CL + note))

# ---- the A/C pressure transducer
add.append(text("A/C PRESSURE  block 02.15 (b) - DNP: J11 transducer lead (0.5-4.5 V ratiometric, confirm) -> 10k / 20k -> U15 ADS1115-Q1 at 0x48; its 5 V from U16, which tracks +5V", 584, 316, 1.5, True))
add.append(text("No Teensy ADC pin is free (all 42 edge pins used, D-452), so the reading goes over I2C. AIN0 pressure, AIN2 the sensor supply (ratio = AIN0 / AIN2); AIN1 and AIN3 grounded, spare.", 584, 320.5))
add.append(text("J11 is a PLACEHOLDER: 02.15 (b) gives the transducer's three wires no drop cavity (DP-DCU 1-6 used, DP-DCU-B 12 taken by the clutch) - confirm the harness path.", 584, 324))
u15 = {"VDD": "+3V3", "GND": "GND", "ADDR": "GND", "SDA": "I2C_SDA", "SCL": "I2C_SCL", "ALERT/RDY": None,
       "AIN0": "AC_PRESS_ADC", "AIN1": "GND", "AIN2": "SENS_5V_ADC", "AIN3": "GND"}
add.append(ic("ADS1115-Q1", "U15", "ADS1115-Q1", "Package_SO:MSOP-10_3x3mm_P0.5mm", 622.3, 350.52, u15, True,
              CL + "I2C ADC, VSSOP-10 (DGS), 0x48 with ADDR on GND (SBAS563E table 8-2), 3.3 V supply - confirm the package against the part in hand"))
add.append(two_pin("C", "C39", "100n  U15 VDD", C08, 655.32, 345.44, "+3V3", "GND", True, CL + "U15 bypass"))
u16 = {"VIN": "+12V_LOGIC", "ADJ/EN": "+5V", "GND": "GND", "VOUT": "SENS_5V"}
add.append(ic("TPS7B4250-Q1", "U16", "TPS7B4250-Q1", "Package_TO_SOT_SMD:SOT-23-5", 721.36, 350.52, u16, True,
              CL + "the transducer's 5 V: tracks +5V within 5 mV, 50 mA, survives a short to battery or ground on the lead (SLVSCA0C) - confirm"))
for ref, val, x, top, bot, note in (
        ("C40", "1u 50V", 749.3, "+12V_LOGIC", "GND", "U16 VIN"),
        ("C41", "100n", 764.54, "+5V", "GND", "U16 ADJ/EN, at the pin"),
        ("C42", "2.2u", 779.78, "SENS_5V", "GND", "U16 VOUT, 1-50 uF any ESR (SLVSCA0C)")):
    add.append(two_pin("C", ref, val, C08, x, 350.52, top, bot, True, CL + note))
add.append(conn("Conn_01x03", "J11", "A/C pressure transducer lead - PLACEHOLDER", "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical",
                830.58, 350.52, ["SENS_5V", "AC_PRESS_IN", "GND"], True,
                CL + "PLACEHOLDER - confirm: 1 sensor 5 V, 2 signal (0.5-4.5 V ratiometric, confirm the transducer), 3 sensor ground; no drop cavity is free for it"))
for ref, val, x, top, bot, note in (
        ("R64", "10k", 863.6, "AC_PRESS_IN", "AC_PRESS_ADC", "divider top: 4.5 V -> 3.0 V; 14 V on the lead is 1 mA into D9"),
        ("R65", "20k", 878.84, "AC_PRESS_ADC", "GND", "divider bottom: an open lead reads 0 V, under the 0.5 V floor = fault"),
        ("C43", "100n", 894.08, "AC_PRESS_ADC", "GND", "AIN0 filter"),
        ("R66", "10k", 909.32, "SENS_5V", "SENS_5V_ADC", "supply divider top"),
        ("R67", "20k", 924.56, "SENS_5V_ADC", "GND", "supply divider bottom: 5.0 V -> 3.33 V"),
        ("C44", "100n", 939.8, "SENS_5V_ADC", "GND", "AIN2 filter")):
    add.append(two_pin("R" if ref.startswith("R") else "C", ref, val, R08 if ref.startswith("R") else C08, x, 350.52, top, bot, True, CL + note))
add.append(bat54s("D9", 878.84, 370.84, "AC_PRESS_ADC", True, CL + "AIN0 clamp"))
add.append(bat54s("D10", 924.56, 370.84, "SENS_5V_ADC", True, CL + "AIN2 clamp"))

# ---- the radar alert input
add.append(text("RADAR ALERT  luxury 03.12 / Z-002 - DNP: J12 the receiver's alert lead -> 47k / 22k, 100n, BAT54S -> U13 P01; R68 wets an open-collector output", 584, 398, 1.5, True))
add.append(text("The receiver sits behind the dash on its own feed (N103, A16); its alert line is local, not on a drop. Output type unknown: active-high 12 V reads high through the divider;", 584, 402.5))
add.append(text("an open-collector output needs R68 fitted and reads low when it alerts. 12 V -> 3.8 V clamped by D11; 8 V still reads high (VIH 2.31 V at 3.3 V). J12 is a PLACEHOLDER - confirm.", 584, 406))
add.append(conn("Conn_01x02", "J12", "radar alert lead - PLACEHOLDER", "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
                609.6, 429.26, ["RADAR_IN", "GND"], True,
                RD + "PLACEHOLDER - confirm: 1 the receiver's alert output (type unknown), 2 ground"))
for ref, val, x, top, bot, note in (
        ("R68", "10k", 640.08, "+12V_LOGIC", "RADAR_IN", "fit only if the alert output is open-collector or open-drain - confirm"),
        ("R69", "47k", 655.32, "RADAR_IN", "RADAR_ALERT", "series: limits the clamp current to 0.3 mA at 16 V"),
        ("R70", "22k", 670.56, "RADAR_ALERT", "GND", "divider bottom and the pull-down while nothing is plugged in"),
        ("C45", "100n", 685.8, "RADAR_ALERT", "GND", "filter")):
    add.append(two_pin("R" if ref.startswith("R") else "C", ref, val, R08 if ref.startswith("R") else C08, x, 429.26, top, bot, True, RD + note))
add.append(bat54s("D11", 716.28, 424.18, "RADAR_ALERT", True, RD + "U13 P01 clamp"))

# ---- the comfort grounds and the free cavities
add.append(text("DP-DCU-C 8 (J2 pin 8) is wired to PGND: block 01.26 (a), the third comfort ground (about 10 A per pin). The record keeps the cavity a sealing plug until 01.26 answers -", 584, 456, 1.5, True))
add.append(text("the copper is there either way, the contact and its 14 AWG wire are fitted with the answer. DP-DCU-B 12 carries AC_CLUTCH (02.15 (b)); it stays a plug until then.", 584, 460.5))
add.append(text("Every part in this box but U13 and C38 is DNP; each carries its reason in its Note field. Nothing here touches +12V_CMF; U14 and the GND / PGND rule (CONVENTIONS 5) hold.", 584, 465))

# ---- edits to what is there
# U12 P17: the wired-OR status line moves to U13 P00; P17 now commands the clutch stage
sch, n = re.subn(r'\(label "SEAT_STATUS" \(at 739\.14 83\.82 0\)', '(label "AC_CLUTCH_CMD" (at 739.14 83.82 0)', sch)
assert n == 1
# DP-DCU-B 12 and DP-DCU-C 8 lose their no-connects
sch = remove_at(sch, ("no_connect",), (419.1, 723.9))
add.append(stub("AC_CLUTCH", 419.1, 723.9, "L"))
sch = remove_at(sch, ("no_connect",), (35.56, 127.0))
add.append(stub("PGND", 35.56, 127.0, "L"))


def set_text(text_, old_prefix, new):
    pat = re.compile(r'\(text "%s[^"]*"' % re.escape(old_prefix))
    text_, n_ = pat.subn('(text "%s"' % new, text_, count=1)
    assert n_ == 1, old_prefix
    return text_


sch = set_text(sch, "SN16  seat heat driver",
               "SN16  seat heat driver - the four BTS3011TE STATUS pins (open-drain, latched thermal fault) are wired-OR on SEAT_STATUS to expander U13 P00 through R58 (Y11)")
sch = set_text(sch, "- BTS3011TE STATUS x4 wired-OR",
               "- BTS3011TE STATUS x4 wired-OR to U13 P00 with one 10k pull-up: a latched thermal fault reads low; clearing it needs P00 driven high (3-7 mA per faulted part) with IN low - confirm the expander's drive.")
sch = set_text(sch, "- The two PROFET IS lines are not read",
               "- The two PROFET IS lines (U9, U10) are not read: all 42 Teensy edge pins are used. Diagnostics stay off (DEN low), and so on the clutch stage U14 (Y11).")
sch = set_text(sch, "- The enclosure: V-102 is unmeasured",
               "- The enclosure: V-102 is unmeasured, so the board outline is PROVISIONAL (180 x 80 mm, four M3; sized by the three DT13 flanges) - confirm.")
sch = set_text(sch, "NO-CONNECTS: DP-DCU-B 12",
               "NO-CONNECTS: TPS54560B EN floats high on its internal pull-up; U13 P03-P17 and U15 ALERT/RDY are unused. DP-DCU-B 12 (AC_CLUTCH) and DP-DCU-C 8 (PGND) are wired for blocks 02.15 / 01.26 (Y11).")
sch = sch.replace('(rev "0.02")', '(rev "0.03")')

k = sch.rfind("\n\t(sheet_instances")
sch = sch[:k + 1] + ''.join(add) + sch[k + 1:]
open(SCH, "w").write(sch)
print("ok", len(add))
