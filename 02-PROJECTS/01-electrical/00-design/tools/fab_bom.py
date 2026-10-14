#!/usr/bin/env python3
"""fab_bom.py DESIGN_DIR [--write]  - Y42 (kept in the tree since Y44): hold each carrier's fab BOM (fab/<board>-revA-bom.csv) to
its sheet's BOM export and to the two cart files, and say what the cart lacks.

For every fitted row of a fab BOM: its refs must be exactly a set of fitted refs of the sheet
export, each ref once; the value becomes the sheet's (where the row holds one value); the mpn
becomes the cart line's that buys it (MPN below, by the row's first ref) - a cart line is the part
number, a `class:` description is not. Then the cart's quantity of each part number is held to the
places the four boards fit it. Prints every disagreement; exit 1 on any. --write saves the two
carriers' fab BOMs and copies the panel's sheet BOM to its fab BOM."""
import csv
import os
import re
import shutil
import sys

R = "RC0805FR-07"
MPN = {
    "dcu": {
        "C1": "EEE-FK1J680UP", "C2": "CGA6M3X7S2A475K200AB", "C3": "C0805C224K1RACTU", "C4": "CL21B104KBCNNNC",
        "C5": "CL21B105KAFNNNE", "C6": "CL21C200JBANNNC", "C7": "CL31A226KOHNNNE", "C12": "CL21B472KBANNNC",
        "C13": "CL21C470JBANNNC", "C14": "GRM32ER71A476KE15L", "C25": "C0805C104K1RACTU", "C26": "CL21B105KAFNNNE",
        "C28": "CL21B105KAFNNNE", "C31": "EEE-FK1C471P", "C36": "C0805C103K1RACTU",
        "D1": "SL310A-TP", "D2": "SMBJ33A", "D3": "B560C-13-F", "D6": "BAT54SLT1G", "D7": "SMAJ40A",
        "F1": "1206L050YR", "J1": "DT13-06PA", "J2": "DT13-08PA", "J9": "DT13-12PA", "J3": "B2B-XH-A(LF)(SN)",
        "J4": "SBH11-PBPC-D13-ST-BK", "J6": "PRPC040SAAN-RC", "J10": "PPPC241LFBN-RC", "L1": "XAL4020-222MEC",
        "L2": "XAL7030-682MEC", "Q1": "SQ2364EES-T1_GE3", "Q3": "SQ2361ES-T1_GE3", "Q4": "MMBT5551LT1G",
        "R1": R + "100KL", "R2": R + "24K9L", "R4": R + "243KL", "R5": R + "52K3L", "R6": R + "10KL",
        "R7": R + "16K9L", "R9": "RC0805JR-070RL", "R15": "CRA2512-FZ-R010ELF", "R21": R + "4K7L",
        "R24": R + "1K2L", "R25": R + "47RL", "R37": R + "1K5L", "R38": R + "100RL", "R43": R + "18KL",
        "R48": R + "330RL", "U1": "LMR36015FSCQRNXRQ1", "U2": "TPS54560BQDDARQ1", "U3": "TCAN1042HVDRQ1",
        "U4": "INA180A1QDBVRQ1", "U5": "BTS3011TEATMA1", "U9": "BTT60501ERAXUMA1", "U10": "BTT62004ESAXUMA1",
        "U11": "DRV8962QDDWRQ1", "U12": "TCA9539QPWRQ1",
    },
    "icu": {
        "C1": "EEE-FK1J680UP", "C2": "CL31A226KOHNNNE", "C3": "CL21B104KBCNNNC", "C19": "CL21B106KOQNNNE",
        "C20": "CGA6M3X7S2A475K200AB", "C21": "C0805C224K1RACTU", "C23": "CL31A226KOHNNNE", "C25": "CL21B105KAFNNNE",
        "C26": "CL21C200JBANNNC", "D1": "BAT54SLT1G", "D20": "BZX84C5V1LT1G", "D23": "SL310A-TP", "D24": "SMBJ33A", "D27": "MM3Z15VT1G",
        "F1": "0466004.NR", "J1": "DT13-06PA", "J3": "DT13-12PA", "J2": "PRPC040SAAN-RC", "J4": "PPPC082LFBN-RC",
        "J5": "PPPC241LFBN-RC", "L2": "XAL4020-222MEC", "Q1": "SQD50P06-15L_GE3", "Q2": "MMBT5551LT1G", "Q4": "MMBT3904LT1G",
        "Q3": "DMG3415U-7", "R1": R + "10KL", "R2": R + "4K7L", "R16": R + "1KL", "R21": R + "22KL", "R4": R + "100KL", "R6": "RC2512FK-07100RL",
        "R7": R + "15KL", "R14": R + "47KL", "R18": R + "1KL / " + R + "1K5L / " + R + "2K2L (one of the three, Q-308)",
        "R29": "RC1210FR-07100KL", "R31": R + "39KL", "R32": R + "12KL", "R33": R + "1M2L", "R35": R + "4K7L",
        "R42": R + "24K9L", "R44": "RC0805JR-070RL", "SW1": "B2B-XH-A(LF)(SN)", "U1": "LMR36015FSCQRNXRQ1",
        "U3": "TCAN1042HVDRQ1", "U4": "LM393DR", "U5": "SN74LVC1G17DBVR", "U7": "4517", "U8": "113991054",
    },
}
# rows of a fab BOM that are not a sheet reference: what they are bought as
EXTRA = {
    "icu": {"JP1,JP2,JP8A1|JP8B1": "QPC02SXGN-RC", "U7 (sockets)": "PPPC061LFBN-RC + PPPC051LFBN-RC",
            "U8 (sockets)": "PPPC071LFBN-RC"},
    "dcu": {},
}
# the panel's and the upper board's places, by cart part number (their BOMs carry no mpn column)
OTHER = {
    "CL21B106KOQNNNE": 1, "CL10B105KA8NNNC": 1, "CL10B104KB8NNNC": 1, "1N4148W-7-F": 8, "SBH11-PBPC-D13-ST-BK": 1,
    "LTST-C191TGKT": 12, "LTST-C191TBKT": 6, "LTST-C191KRKT": 6, "RC0603FR-0710KL": 1, "RC0603FR-07100KL": 1,
    "TS02-66-130-BK-160-LCR-D": 4, "B28AP": 2, "PEC11R-4220F-S0024": 1, "PEC11R-4220F-N0024": 2,
    "IS31FL3236A-TQLS4-TR": 1, "DT13-12PA": 1, "B2B-XH-A(LF)(SN)": 2,
}
PER_STRIP = {"PRPC040SAAN-RC"}          # bought by the strip, cut to the places
PATHS = {"dcu": "control-unit/cad/dcu-carrier/dcu-carrier", "icu": "display-unit/cad/icu-carrier/icu-carrier"}
bad = []


def expand(refs):
    out = []
    for tok in re.split(r"[,\s]+", refs.strip()):
        if not tok:
            continue
        m = re.match(r"^([A-Za-z]+)(\d+)-(?:[A-Za-z]+)?(\d+)$", tok)
        if m:
            out += ["%s%d" % (m.group(1), i) for i in range(int(m.group(2)), int(m.group(3)) + 1)]
        else:
            out.append(tok)
    return out


def sheet(path):
    fitted, dnp = {}, {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            refs = row.get("Ref") or row.get("Refs")
            for r in expand(refs):
                (dnp if row["DNP"] else fitted)[r] = (row["Value"], row["Footprint"])
    return fitted, dnp


def cart(d):
    lines = {}
    for name in ("bench-revA-digikey-cart.csv", "bench-revA-mouser-cart.csv"):
        with open(os.path.join(d, name), newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                lines[row["mpn"]] = int(row["qty"])
    return lines


def board(d, key, need, lines, write):
    base = os.path.join(d, PATHS[key])
    fitted, dnp = sheet(base + "-bom.csv")
    fab = os.path.join(os.path.dirname(base), "fab", os.path.basename(base) + "-revA-bom.csv")
    with open(fab, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    head, seen, in_dnp, changed = rows[0], set(), False, 0
    ci = {n: i for i, n in enumerate(head)}
    for row in rows[1:]:
        if not row or not any(row):
            continue
        if row[0].startswith("NOT FITTED"):
            in_dnp = True
            continue
        refs = row[ci["refs"]]
        if refs in EXTRA[key]:
            mp = EXTRA[key][refs]
            if row[ci["mpn"]] != mp:
                row[ci["mpn"]] = mp
                changed += 1
            for part in mp.split(" + "):
                need[part] = need.get(part, 0) + (int(row[ci["qty"]]) if "socket" not in refs else (2 if "071" in part else 1))
            continue
        if "(" in refs:                                   # the module that sits in a socket: not on the sheet
            continue
        rl = expand(refs)
        pool = dnp if in_dnp else fitted
        for r in rl:
            if r not in pool:
                bad.append("%s fab BOM: %s is not a %s ref of the sheet" % (key, r, "DNP" if in_dnp else "fitted"))
            if r in seen:
                bad.append("%s fab BOM: %s twice" % (key, r))
            seen.add(r)
        if in_dnp:
            continue
        if int(row[ci["qty"]]) != len(rl):
            bad.append("%s fab BOM: %s qty %s, %d refs" % (key, refs, row[ci["qty"]], len(rl)))
        vals = {fitted[r][0] for r in rl if r in fitted}
        fps = {fitted[r][1] for r in rl if r in fitted}
        if len(fps) == 1 and row[ci["footprint"]] != list(fps)[0]:
            bad.append("%s fab BOM: %s footprint %s, sheet %s" % (key, refs, row[ci["footprint"]], list(fps)[0]))
        if len(vals) == 1 and row[ci["value"]] != list(vals)[0] and rl[0] in RESET_VALUE[key]:
            row[ci["value"]] = list(vals)[0]
            changed += 1
        mp = MPN[key].get(rl[0])
        if mp is None:
            bad.append("%s fab BOM: no cart line named for %s" % (key, refs))
            continue
        if row[ci["mpn"]] != mp:
            row[ci["mpn"]] = mp
            changed += 1
        first = mp.split(" / ")[0]
        if first not in lines and "one of the three" not in mp:
            bad.append("%s fab BOM: %s -> %s is in neither cart file" % (key, refs, mp))
        n = len(rl) * (2 if rl[0] in ("J10", "J5") and "PPPC241" in mp else 1)
        if "one of the three" in mp:
            for part in mp.split(" (")[0].split(" / "):
                need[part] = need.get(part, 0) + 1
        elif rl[0] in ("J2", "J6"):
            need[first] = need.get(first, 0)              # cut from a strip
        else:
            need[first] = need.get(first, 0) + n
    for r in fitted:
        if r not in seen:
            bad.append("%s fab BOM: fitted %s of the sheet is on no row" % (key, r))
    for r in dnp:
        if r not in seen:
            bad.append("%s fab BOM: DNP %s of the sheet is on no row" % (key, r))
    print("%s: %d fitted refs, %d DNP, %d cells changed -> %s" % (key, len(fitted), len(dnp), changed, os.path.relpath(fab, d)))
    if write:
        with open(fab, "w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(rows)


RESET_VALUE = {"dcu": {"C1", "C31", "Q1", "Q3", "Q4", "D1", "R43"}, "icu": {"C1", "R2", "Q2", "D23", "D27"}}


def main():
    d = sys.argv[1]
    write = "--write" in sys.argv
    lines = cart(d)
    need = dict(OTHER)
    for key in ("dcu", "icu"):
        board(d, key, need, lines, write)
    for mp, n in sorted(need.items()):
        have = lines.get(mp)
        if have is None:
            bad.append("cart: no line for %s (%d places)" % (mp, n))
        elif have < n and mp not in PER_STRIP:
            bad.append("cart: %s qty %d, the boards fit %d" % (mp, have, n))
    spare = sorted(set(lines) - set(need))
    print("cart lines no board BOM row names (%d): %s" % (len(spare), ", ".join(spare)))
    if write:
        p = os.path.join(d, "control-unit/cad/panel")
        shutil.copyfile(os.path.join(p, "panel-bom.csv"), os.path.join(p, "fab", "panel-revA-bom.csv"))
        print("panel: fab/panel-revA-bom.csv = panel-bom.csv")
    for b in bad:
        print("BAD", b)
    print("%d disagreements" % len(bad))
    sys.exit(1 if bad else 0)


main()
