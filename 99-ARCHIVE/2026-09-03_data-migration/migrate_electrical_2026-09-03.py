#!/usr/bin/env python3
"""One-off migration, 2026-09-03: parse the hand-maintained electrical-build
documents into data/*.csv + templates/*.md for tools/rx7.py.

Run once from the repo root:  python tools/migrate_electrical_2026-09-03.py
Afterwards this script is history — the CSVs are the record.
"""
import csv, re, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJ = ROOT / "02-PROJECTS" / "electrical-build"
DATA = PROJ / "data"
TPL = PROJ / "templates"
SRC_DESIGN = PROJ / "01-DESIGN" / "DESIGN.md"
SRC_SHOP = PROJ / "02-SHOPPING" / "SHOPPING-LIST.md"
SRC_INSTALL = PROJ / "03-INSTALL" / "INSTALL.md"
SRC_WIRE = PROJ / "03-INSTALL" / "WIRE-TABLES.md"
SRC_PMU = PROJ / "03-INSTALL" / "PMU-CONFIG-SHEET.md"
SRC_GLOSS = PROJ / "01-DESIGN" / "GLOSSARY.md"
SRC_README = PROJ / "README.md"

# ----------------------------------------------------------------- helpers

def read(p):
    return p.read_text(encoding="utf-8").splitlines()

def split_row(line):
    line = line.strip()
    if line.startswith("|"): line = line[1:]
    if line.endswith("|"): line = line[:-1]
    cells, cur, i = [], "", 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur += "\\|"; i += 2; continue
        if c == "|":
            cells.append(cur.strip()); cur = ""; i += 1; continue
        cur += c; i += 1
    cells.append(cur.strip())
    return cells

def tables(lines):
    """Yield (start_line_index, header, rows) for every markdown table."""
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            header = split_row(lines[i]); rows = []; j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(split_row(lines[j])); j += 1
            yield i, header, rows
            i = j
        else:
            i += 1

def table_after(lines, pattern, nth=0):
    """First table after the first line matching pattern (regex)."""
    idx = [k for k, l in enumerate(lines) if re.search(pattern, l)]
    if not idx: raise SystemExit(f"anchor not found: {pattern}")
    start = idx[nth]
    for s, h, r in tables(lines):
        if s > start: return s, h, r
    raise SystemExit(f"no table after: {pattern}")

def write_csv(name, header, rows):
    DATA.mkdir(parents=True, exist_ok=True)
    with open(DATA / f"{name}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            r = list(r) + [""] * (len(header) - len(r))
            w.writerow(r)
    print(f"  data/{name}.csv  {len(rows)} rows")

def dash(v):
    return "" if v in ("—", "-", "–") else v

# ----------------------------------------------------------------- DESIGN
D = read(SRC_DESIGN)

# --- pins §4.1
s, h, rows = table_after(D, r"^### 4\.1")
pins = []
for r in rows:
    pin, cav, ch, name, awg, colour, circuit, goes, est, enable, inrush, state = r
    name = name.strip("`")
    ch = dash(ch)
    typ = ("output" if ch.startswith("O") else "input" if ch.startswith("A") else
           {"+12V SW": "WAKE", "+5V OUT": "REF", "CAN1H": "CAN1", "CAN1L": "CAN1",
            "CAN2H": "CAN2", "CAN2L": "CAN2", "GND": "GND", "+12V BATT": "MAIN"}[name])
    # enable "25.0 cap" / "**4.0 meas**" / "—"
    en_a, en_b = "", ""
    m = re.match(r"\**([\d.]+)\s*(cap|meas)\**", enable)
    if m: en_a, en_b = m.group(1), m.group(2)
    ix, ims = "", ""
    m = re.match(r"([\d.]+)×\s*([\d]+)\s*ms", inrush)
    if m: ix, ims = m.group(1), m.group(2)
    fixed = goes if typ in ("WAKE", "REF", "CAN1", "CAN2", "GND", "MAIN") or ch in ("A7",) else ""
    pins.append([pin, cav, ch, name, typ, awg, colour, circuit, fixed, dash(est), en_a, en_b, ix, ims, state, ""])
write_csv("pins", ["pin", "cav_size", "ch", "name", "type", "awg", "colour", "circuit", "goes_to_fixed",
                   "est_a", "enable_a", "enable_basis", "inrush_x", "inrush_ms", "state", "note"], pins)
CH2PIN = {r[2]: r[0] for r in pins if r[2]}
NAME2PIN = {r[3]: r[0] for r in pins}

# --- fuses §3
s, h, rows = table_after(D, r"^## 3 ")
fuses = []
for r in rows:
    fid, rating, where, feeds, fed, state = r
    block, pos = "", ""
    m = re.search(r"block ([AB])", where)
    if m: block = m.group(1)
    fuses.append([fid, dash(rating), where, block, pos, feeds, fed, state, ""])
# block positions from the block table
s, h, rows = table_after(D, r"^### Fuse blocks")
for r in rows:
    blk = r[0].split()[-1]
    for p, cell in enumerate(r[2:], start=1):
        m = re.match(r"(F\d+)", cell)
        if m:
            for f in fuses:
                if f[0] == m.group(1): f[3], f[4] = blk, str(p)
write_csv("fuses", ["id", "rating", "location", "block", "pos", "feeds", "fed_from", "state", "label"], fuses)

# --- relays §5.1
s, h, rows = table_after(D, r"^### 5\.1")
relays = []
def term(txt, t):
    m = re.search(rf"(?:^|·\s*){t} (?:←|→) ([^·]+)", txt)
    return m.group(1).strip() if m else ""
for r in rows:
    rid, fn, typ, where, coil, contacts, state = r
    relays.append([rid, fn, dash(typ), where, term(coil, "86"), term(coil, "85"),
                   term(contacts, "30"), term(contacts, "87"), term(contacts, "87a"), state, ""])
write_csv("relays", ["id", "function", "type", "location", "c86", "c85", "c30", "c87", "c87a", "state", "label"], relays)

# --- node conductors §5.3
s, h, rows = table_after(D, r"^### 5\.3")
node = [[f"N{i:02d}", *r] for i, r in enumerate(rows, start=1)]
write_csv("node_conductors", ["id", "src", "dst", "awg", "colour", "note"], node)

# --- backbone §2
s, h, rows = table_after(D, r"^## 2 ")
write_csv("backbone", ["id", "run", "cable", "protection", "why"], [[f"B{i}", *r] for i, r in enumerate(rows, 1)])

# --- housings §6 schedule
s, h, rows = table_after(D, r"^\*\*Housing schedule")
housings = []
for r in rows:
    code, leg, cls, ls, bs, cav, used, wl, where, note = r
    housings.append([code, leg, cls, ls, bs, cav, wl, where, note])
write_csv("housings", ["code", "leg", "class", "leg_side", "box_side", "cavs", "wedgelocks", "where", "note"], housings)
HOUSING_CODES = [hh[0] for hh in housings]

# --- cavities: every table whose header starts with "Cav | Circuit | From"
def norm_src(txt, state):
    """Turn the free-text 'From' cell into (src, src_note)."""
    t = txt.strip()
    if t in ("—", "", "-"): return "", ""
    # capped / spare
    if t.lower().startswith("capped at the post"): return "", ""
    if t.lower().startswith("capped at the sill"): return "", ""
    # derived (upstream) end of a link: "→ DP-CLU 5 (post splice; DP-ICU 6 tap capped)" / "→ L4-M 9"
    if t.startswith("→"): return "", ""
    # link from another cavity: "← L1-S1 3", "← L1-S1 6 (shielded)", "← L1-S2 1 + L3-S2 11", "← L4-S 1 (A7 taps this conductor)"
    m = re.match(r"←\s*([A-Z0-9-]+ \d+(?: \+ [A-Z0-9-]+ \d+)*)\s*(?:\((.*)\))?$", t)
    if m: return m.group(1), (m.group(2) or "")
    m = re.match(r"tap on (?:the )?([A-Z0-9-]+ \d+)(?: node)?$", t)
    if m: return "tap " + m.group(1), ""
    m = re.match(r"(O\d+) \(pin \d+\)(?: splice|, (.*))?$", t)
    if m: return m.group(1), ("splice" if "splice" in t else (m.group(2) or ""))
    m = re.match(r"(A\d+)(?: node)? \(pin \d+\)(?:, (.*))?$", t)
    if m: return m.group(1), (m.group(2) or "")
    m = re.match(r"(CAN[12][HL]) \(pin \d+\)$", t)
    if m: return m.group(1), ""
    m = re.match(r"(F\d+) \([\d.]+ A\)(?: ← .*)?$", t)
    if m: return m.group(1), ""
    m = re.match(r"(K\d+) (87|85) ?(?:\(.*\))?(?: ← .*)?$", t)
    if m: return f"{m.group(1)} {m.group(2)}", ""
    m = re.match(r"Wake strip input (\d)$", t)
    if m: return f"WAKE {m.group(1)}", ""
    if t == "DP-GND": return "GND", ""
    if t == "Sill ground stud": return "SILL-GND", ""
    m = re.match(r"(K\d/K\d) at the sill", t)
    if m: return m.group(1), ""
    m = re.match(r"(F14) at the sill", t)
    if m: return "F14", ""
    raise SystemExit(f"unparsed From: {t!r}")

cavities = []
for s, h, rows in tables(D):
    if h[:3] != ["Cav", "Circuit", "From"] and h[:3] != ["Cav", "Circuit", "From (box side)"]:
        continue
    # housing code is on the nearest preceding bold line "**L1-P** · ..." or "### 7.1 · DP-CLU"
    code = None
    for k in range(s - 1, s - 12, -1):
        m = re.match(r"^\*\*([A-Z0-9-]+)\*\*", D[k]) or re.match(r"^###\s*(?:7\.1 · )?(DP-[A-Z]+)", D[k])
        if m: code = m.group(1); break
    assert code in HOUSING_CODES, (code, D[s - 3:s])
    for r in rows:
        cav, circuit, frm, awg, colour, state, lands = r
        src, note = norm_src(frm, state)
        cavities.append([f"{code} {cav}", code, cav, dash(circuit) if state != "PLUG" else "",
                         src, note, dash(awg), dash(colour), state, lands])
write_csv("cavities", ["id", "housing", "cav", "circuit", "src", "src_note", "awg", "colour", "state", "lands_on"], cavities)

# --- ladders §8
inputs, ladders = [], []
i = 0
while i < len(D):
    m = re.match(r"^\*\*(A\d+) · (.+?)\*\* — window ± (\d+)(?: counts)? · (.*)$", D[i])
    if m:
        a, title, win, rest = m.groups()
        kind = "12v" if a in ("A15", "A16") else "ground"
        inputs.append([a, title, kind, win, rest])
        s, h, rows = table_after(D[i:], r".")
        for r in rows:
            if kind == "ground":
                st, rr, adc = r
                ladders.append([f"{a} {st}", a, st, rr])
            else:
                st, rr, v, adc = r
                ladders.append([f"{a} {st}", a, st, rr])
        i += 1 + s + 2 + len(rows)
    else:
        i += 1
write_csv("inputs", ["id", "title", "kind", "window", "fault_rule"], inputs)
write_csv("ladders", ["id", "input", "state", "r"], ladders)

# --- logic §9 + rules
s, h, rows = table_after(D, r"^## 9 ")
write_csv("logic", ["id", "channel", "expression", "inrush", "retry"], [[r[0], *r] for r in rows])
s, h, rows = table_after(D, r"^### Rules")
write_csv("rules", ["id", "rule", "definition"], [[r[0].replace(" ", "-").lower(), *r] for r in rows])

# --- grounds §10
s, h, rows = table_after(D, r"^## 10 ")
write_csv("grounds", ["id", "zone", "return", "awg", "qty", "ft"], [[f"G{i:02d}", *r] for i, r in enumerate(rows, 1)])

# --- loads §11
s, h, rows = table_after(D, r"^## 11 ")
write_csv("loads", ["id", "circuit", "ch", "rated", "design_a", "measured_a", "basis"],
          [[f"LD{i:02d}", r[0], r[1], r[2], r[3], dash(r[4]).strip("*"), r[5]] for i, r in enumerate(rows, 1)])

# --- devices §12
s, h, rows = table_after(D, r"^## 12 ")
devs = []
for i, r in enumerate(rows, 1):
    zone, dev, terms, gnd = r
    m = re.match(r"\*\*(.+?)\*\*(?: — (.*))?$", dev)
    devs.append([f"DV{i:02d}", zone, m.group(1), m.group(2) or "", terms, dash(gnd)])
write_csv("devices", ["id", "zone", "device", "ident", "terminals", "ground"], devs)

# --- colour families §4.3
s, h, rows = table_after(D, r"^### 4\.3")
write_csv("colours", ["id", "family", "gauges"], [[r[0].strip("*"), r[1], r[2]] for r in rows])

# --- contact series §6
s, h, rows = table_after(D, r"^## 6 ")
write_csv("series", ["id", "contact", "wire", "rated", "used_for"], [[r[0].replace("Deutsch ", ""), *r[1:]] for r in rows])

# ----------------------------------------------------------------- WIRE-TABLES §E cables
W = read(SRC_WIRE)
s, h, rows = table_after(W, r"^## E ")
write_csv("cables", ["id", "run", "awg", "ft", "colour"], [[f"C{i:02d}", *r[:4]] for i, r in enumerate(rows, 1)])

# ----------------------------------------------------------------- INSTALL §C migration order
I = read(SRC_INSTALL)
s, h, rows = table_after(I, r"^## C ")
write_csv("migration", ["id", "seq", "circuit", "ch"], [[f"MG{int(r[0]):02d}", r[0], r[1], r[2]] for r in rows])

# ----------------------------------------------------------------- SHOPPING
S = read(SRC_SHOP)
parts, carts = [], []
s, h, rows = table_after(S, r"^## Totals")
for r in rows:
    if r[0] in ("Waytek", "WireBarn", "DeutschConnector.com", "Amazon"):
        carts.append([r[0], r[2].replace("$", "").replace(",", "")])
URLS = {"Waytek": "https://www.waytekwire.com/", "WireBarn": "https://www.wirebarn.com/GXL-Wire-By-The-Foot_c_4.html",
        "DeutschConnector.com": "https://www.deutschconnector.com/", "Amazon": "https://www.amazon.com/"}
write_csv("carts", ["store", "total_usd", "url", "note"],
          [[c[0], c[1], URLS[c[0]], "" if c[0] != "WireBarn" else "The site showed \"Hello, Guest\" at review — sign in before checkout or the cart is lost"] for c in carts])

pid = 0
def add_part(store, section, sku, item, spec, qty, unit, usd, basis, used, status, need=""):
    global pid
    pid += 1
    parts.append([f"P{pid:03d}", store, section, sku, item, spec, qty, unit, usd, basis, used, status, need])

# Waytek
s, h, rows = table_after(S, r"^## 1 · Waytek")
for r in rows:
    sku, item, qty, used = r
    m = re.match(r"(.+?) — (.*)$", item)
    add_part("Waytek", "Fuse blocks, relays, sockets, busbar, 16 AWG spools", sku, item, "", qty, "ea", "", "cart", used, "cart")
# WireBarn
s, h, rows = table_after(S, r"^## 2 · WireBarn")
for r in rows:
    awg, col, ft, used = r
    add_part("WireBarn", "GXL by the foot", "", f"GXL {awg} AWG {col}", "", ft, "ft", "", "cart", used, "cart")
s, h, rows = table_after(S, r"^\*\*To add at WireBarn")
for r in rows:
    awg, col, ft, used, st = r
    add_part("WireBarn", "GXL by the foot", "", f"GXL {awg} AWG {col}", "", ft, "ft", "", "cart", used, "to add")
# Deutsch contacts etc. (kits are derived from housings)
s, h, rows = table_after(S, r"^### Contacts, plugs, clips")
NEED = {"0462-209-16141": "contacts14", "0460-215-16141": "contacts14", "114017": "plugs16", "0413-204-2005": "plugs12",
        "1027-003-1200": "clips", "DT12P-DC": "", "DT6P-DC": "", "DT4P-DC": ""}
for r in rows:
    sku, item, qty, need_txt, st = r
    status = "cart" if st == "cart" else ("to add" if "add" in st else "raise")
    add_part("DeutschConnector.com", "Contacts, plugs, clips, caps, tools", sku, item, "", qty, "ea", "", "cart",
             need_txt.replace("**", ""), st.replace("**", ""), NEED.get(sku, ""))
# Amazon sections
for sec in ["Tools", "Power backbone and battery", "Dash node and electronics", "Consumables and labels", "Switches"]:
    s, h, rows = table_after(S, rf"^### {sec}$")
    for r in rows:
        item, spec, qty, usd, note = r
        add_part("Amazon", sec, "", item.replace("**", ""), spec.replace("**", ""), qty, "", usd, "est", note, "cart")
# vehicle parts
s, h, rows = table_after(S, r"^## 6 · Vehicle parts")
for r in rows:
    item, spec, qty, usd, note = r
    add_part("Vehicle parts", "RockAuto / PartsGeek / Mazda specialist", "", item, spec, qty, "", usd, "est", note, "not carted")
# hardware store
s, h, rows = table_after(S, r"^## 7 · Hardware store")
for r in rows:
    item, note = r
    add_part("Hardware store", "After the measurement day", "", item, "", "", "", "", "", note, "later")
write_csv("parts", ["id", "store", "section", "sku", "item", "spec", "qty", "unit", "unit_usd", "basis", "used_for", "status", "need_rule"], parts)

print("data written:", DATA)
