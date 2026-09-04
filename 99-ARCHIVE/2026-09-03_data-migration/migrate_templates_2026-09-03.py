#!/usr/bin/env python3
"""One-off, 2026-09-03: turn the six hand-maintained documents into templates by
replacing every data table with a {{view}} placeholder. Prose is kept verbatim.
Run after migrate_electrical_2026-09-03.py, from the repo root."""
import re, sys
from pathlib import Path


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

ROOT = Path(__file__).resolve().parent.parent
PROJ = ROOT / "02-PROJECTS" / "electrical-build"
TPL = PROJ / "templates"
TPL.mkdir(exist_ok=True)


def preceding_bold(lines, s, pat):
    for k in range(s - 1, max(s - 6, -1), -1):
        m = re.match(pat, lines[k])
        if m:
            return k, m
    return None, None


def preceding_heading(lines, s, pat):
    for k in range(s - 1, -1, -1):
        m = re.match(pat, lines[k])
        if m:
            return k, m
    return None, None


def templatize(src, out_rel, classify):
    lines = read(src)
    regions = []  # (start, end_exclusive, replacement)
    for s, h, rows in tables(lines):
        e = s + 2 + len(rows)
        r = classify(lines, s, h)
        if r is None:
            continue
        start, placeholder = r
        regions.append((start, e, placeholder))
    regions.sort()
    out, i = [f"<!-- out: {out_rel} -->"], 0
    for start, e, ph in regions:
        out.extend(lines[i:start]); out.append(ph); i = e
    out.extend(lines[i:])
    text = "\n".join(out) + "\n"
    name = Path(out_rel).name
    (TPL / name).write_text(text, encoding="utf-8")
    print(f"  templates/{name}  ({len(regions)} tables replaced)")


# ---------------------------------------------------------------- DESIGN
def cls_design(L, s, h):
    sig = tuple(h[:2])
    simple = {("Element", "Count"): "counts", ("Run", "Cable"): "backbone", ("Fuse", "Rating"): "fuses",
              ("Block", "Input"): "fuse_blocks", ("Pin", "Cav"): "pins", ("Colour", "Family"): "colours",
              ("Relay", "Function"): "relays", ("From", "To"): "node_conductors", ("Series", "Contact"): "series",
              ("Code", "Leg"): "housings", ("Channel", "Expression"): "logic", ("Rule", "Definition"): "rules",
              ("Zone", "Return"): "grounds", ("Circuit", "Ch"): "loads", ("Zone", "Device"): "devices"}
    if sig in simple:
        return s, "{{" + simple[sig] + "}}"
    if sig == ("Cav", "Circuit"):
        k, m = preceding_bold(L, s, r"^\*\*([A-Z0-9-]+)\*\*")
        if m:
            return k, "{{cavities:" + m.group(1) + "}}"
        k, m = preceding_heading(L, s, r"^###\s*(?:7\.1 · )?(DP-[A-Z]+)")
        return s, "{{cavities:" + m.group(1) + "}}"
    if sig[0] == "State":
        k, m = preceding_bold(L, s, r"^\*\*(A\d+) · ")
        return k, "{{ladder:" + m.group(1) + "}}"
    return None


templatize(PROJ / "01-DESIGN" / "DESIGN.md", "01-DESIGN/DESIGN.md", cls_design)


# ---------------------------------------------------------------- WIRE-TABLES
GROUP = {"L1 Engine": "L1", "L2 Front": "L2", "L3 Dash": "L3", "L4 Rear": "L4", "Sill — doors": "Sill", "Drops": "Drops"}


def cls_wire(L, s, h):
    if h[0] == "Cav": return s, "{{pmu_connector}}"
    if h[0] == "From": return s, "{{node_conductors_check}}"
    if h[0] == "Cavity":
        k, m = preceding_heading(L, s, r"^### (.+)$")
        return s, "{{cut_list:" + GROUP[m.group(1)] + "}}"
    if h[0] == "Zone": return s, "{{grounds_check}}"
    if h[0] == "Run": return s, "{{cables}}"
    return None


templatize(PROJ / "03-INSTALL" / "WIRE-TABLES.md", "03-INSTALL/WIRE-TABLES.md", cls_wire)


# ---------------------------------------------------------------- PMU-CONFIG
def cls_pmu(L, s, h):
    if h[0] == "Pin": return s, "{{channel_names}}"
    if h[0] == "State":
        k, m = preceding_bold(L, s, r"^\*\*(A\d+) `")
        return k, "{{decode:" + m.group(1) + "}}"
    if h[0] == "Channel": return s, "{{logic:config}}"
    if h[0] == "Rule": return s, "{{rules}}"
    if h[0] == "Ch": return s, "{{enable_at}}"
    return None


templatize(PROJ / "03-INSTALL" / "PMU-CONFIG-SHEET.md", "03-INSTALL/PMU-CONFIG-SHEET.md", cls_pmu)


# ---------------------------------------------------------------- INSTALL
def cls_install(L, s, h):
    if h[0] == "Position": return s, "{{plan_labels}}"
    if h[0] == "#": return s, "{{migration_log}}"
    return None


templatize(PROJ / "03-INSTALL" / "INSTALL.md", "03-INSTALL/INSTALL.md", cls_install)


# ---------------------------------------------------------------- SHOPPING
def cls_shop(L, s, h):
    if h[0] == "Store" and h[1] == "Lines": return s, "{{shopping_totals}}"
    if h[0] == "Waytek #": return s, "{{parts:Waytek}}"
    if h[0] == "AWG" and len(h) == 4: return s, "{{parts:WireBarn}}"
    if h[0] == "AWG" and len(h) == 5: return s, "{{parts_to_add:WireBarn}}"
    if h[0] == "Kit": return s, "{{deutsch_kits}}"
    if h[0] == "Part": return s, "{{deutsch_contacts}}"
    if h[0] == "Item" and h[1] == "Spec":
        k, m = preceding_heading(L, s, r"^##+ (?:\d · )?(.+)$")
        sec = m.group(1)
        if sec.startswith("Vehicle parts"): return s, "{{parts:Vehicle parts}}"
        return s, "{{parts:Amazon/" + sec + "}}"
    if h[0] == "Item" and h[1] == "Note": return s, "{{parts:Hardware store}}"
    if h[0] == "Store" and h[1] == "Item": return s, "{{gaps}}"
    if h[0] == "Value": return s, "{{blade_fuses}}"
    return None


templatize(PROJ / "02-SHOPPING" / "SHOPPING-LIST.md", "02-SHOPPING/SHOPPING-LIST.md", cls_shop)
# cart lines and the arrival counts become inline placeholders
p = TPL / "SHOPPING-LIST.md"
t = p.read_text(encoding="utf-8")
t = re.sub(r"^https://www\.waytekwire\.com/ · \*\*cart .*$", "{{cart_line:Waytek}}", t, flags=re.M)
t = re.sub(r"^https://www\.wirebarn\.com/\S+ · \*\*cart .*$", "{{cart_line:WireBarn}}", t, flags=re.M)
t = re.sub(r"^https://www\.deutschconnector\.com/ · \*\*cart .*$", "{{cart_line:DeutschConnector.com}}, 188 pieces", t, flags=re.M)
t = re.sub(r"^https://www\.amazon\.com/ · \*\*cart .*?\*\*\.", "{{cart_line:Amazon}}.", t, flags=re.M)
t = t.replace("Housings: 21 codes", "Housings: {{n_housings}} codes")
t = re.sub(r"Contacts: .*? 3 dust caps\.", "{{arrival}}.", t)
p.write_text(t, encoding="utf-8")

# ---------------------------------------------------------------- README + GLOSSARY
r = (PROJ / "README.md").read_text(encoding="utf-8")
r = r.replace("About $3,200 all-in", "About {{total_all}} all-in")
(TPL / "README.md").write_text("<!-- out: README.md -->\n" + r, encoding="utf-8")
print("  templates/README.md")


def cls_gloss(L, s, h):
    if h == ["Colour", "Family"]: return s, "{{colours_gloss}}"
    return None


templatize(PROJ / "01-DESIGN" / "GLOSSARY.md", "01-DESIGN/GLOSSARY.md", cls_gloss)
