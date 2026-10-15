#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""box_sheets.py - one plan sheet per box and one overview of them all (D-613), called by
`rx7.py diagrams` with the leg drawings. Like them, a pure, read-only projection of the record:
rebuilt whole, never edited, never looked at by `check`, the same overlap rule.

  <part>/diagrams/<slug>-plan.svg      per box: where it sits, what it holds, its fuses and switches,
                                       every plug's cavities (the leg sheets' housing block), its heavy
                                       cables, and for the PMU box every inside connection
  00-design/diagrams/boxes-plan.svg    every box in its zone, the wires and cables between them

Owns no facts. Reads (01-electrical): boxes (the sheet per row; `part` is the folder), housings
(box, series), cavities, devices, fuses (box), relays (box), node_conductors, cables, work (the
box's CAD-pass row: an open agent row whose item starts 'CAD pass' and names the box).
"""
from __future__ import annotations

import re
from pathlib import Path

import diagrams as D
from diagrams import FAINT, MUTED, RULE, TEXT, Refused, Sheet, shorten, table, tw, wrap

DESIGN = D.AREA / "00-design"
W = D.DX + D.RW + 30            # every box sheet is as wide as a leg's pin ladder
SLUG = {"PMU-BOX": "pmu-box", "DU": "du", "CU": "cu", "CUR": "cur", "BIN-BOX": "bin-box",
        "BAY-JCT": "bay-junction", "AMP-DOCK": "amp-dock"}


def slug(box):
    return SLUG.get(box["id"], box["id"].lower())


def cad_row(box):
    """The open CAD-pass work row that names this box (Y69 to Y75)."""
    name = box["name"].lower()
    for w in table("work"):
        item = w.get("item") or ""
        if w.get("state") == "open" and item.startswith("CAD pass") and (
                re.search(rf"\bthe {re.escape(box['id'])}\b", item) or name in item.lower()):
            return w
    return None


def para(s, x, y, label, text, width, size=12):
    """A labelled paragraph: the label in small capitals on its own line, then the text wrapped."""
    s.text(x, y, label.upper(), 10, weight=700, fill=MUTED)
    y += 18
    for line in wrap(text or "—", width, size):
        s.text(x, y, line, size)
        y += size + 6
    return y + 10


def grid(s, x, y, cols, rows, size=11, title=""):
    """A table: cols [(heading, width)], rows of cell strings, each cell wrapped to its column."""
    if title:
        s.text(x, y, title.upper(), 10, weight=700, fill=MUTED)
        y += 12
    width = sum(w for _, w in cols)
    s.rect(x, y, width, 26, fill=D.PANEL, stroke=RULE, sw=1, rx=0)
    cx = x
    for head, w in cols:
        s.text(cx + 8, y + 17, head, 11, weight=700)
        cx += w
    y += 26
    for row in rows:
        cells = [wrap(str(v or "—"), w - 16, size) for v, (_, w) in zip(row, cols)]
        h = max(len(c) for c in cells) * (size + 6) + 10
        s.add(f'<line x1="{x}" y1="{y + h:.1f}" x2="{x + width}" y2="{y + h:.1f}" stroke="{RULE}"/>')
        cx = x
        for lines, (_, w) in zip(cells, cols):
            for i, t in enumerate(lines):
                s.text(cx + 8, y + size + 4 + i * (size + 6), t, size)
            cx += w
        y += h
    return y + 24


def cable_ids(box):
    return sorted(set(re.findall(r"\bC\d{2}\b", (box.get("joins") or "") + " " + (box.get("holds") or ""))),
                  key=lambda c: int(c[1:]))


def box_sheet(box):
    housings = [h for h in table("housings") if (h.get("box") or "") == box["id"]]
    codes = [h["code"] for h in housings]
    cavs = [c for c in table("cavities") if c["housing"] in codes]
    cavs.sort(key=lambda c: (codes.index(c["housing"]), int(c["cav"] or 0)))
    by_h = {}
    for c in cavs:
        rows = by_h.setdefault(c["housing"], [])
        # a run of empty cavities is one row on a box sheet: the plug's spares at a glance
        if c["state"] == "PLUG" and not c["circuit"] and rows and rows[-1].get("spares") \
                and rows[-1].get("contact") == c.get("contact"):
            rows[-1]["spares"].append(c["cav"])
        elif c["state"] == "PLUG" and not c["circuit"]:
            rows.append(dict(c, spares=[c["cav"]]))
        else:
            rows.append(c)
    for rows in by_h.values():
        for r in rows:
            sp = r.get("spares")
            if sp and len(sp) > 1:
                r.update(cav="", circuit=f"{sp[0]}–{sp[-1]}: spare, sealing plugs")
    fuses = [f for f in table("fuses") if (f.get("box") or "") == box["id"]]
    relays = [r for r in table("relays") if (r.get("box") or "") == box["id"]]
    row = cad_row(box)

    s = Sheet(f"{box['name']} - plan sheet")
    s.text(30, 40, f"{box['name'].upper()} · PLAN SHEET", 20, weight=700)
    state = (box.get("state") or "planned")
    sub = f"State: {state}" + (f" - its CAD is {row['id']}" if row and state == "planned" else "") + \
        f".  Rulings: {box.get('decided') or '—'}.  Part folder: 00-design/{box['part']}/"
    s.text(30, 64, shorten(sub, W - 60, 12), 12, fill=MUTED)
    y = 100
    half = (W - 90) // 2
    y1 = para(s, 30, y, "Where it sits", box.get("where"), half)
    y2 = para(s, 60 + half, y, "Note", box.get("note"), half)
    y = max(y1, y2)
    y = para(s, 30, y, "What it holds", box.get("holds"), W - 60)
    y = para(s, 30, y, "How it joins the harness", box.get("joins"), W - 60)
    others = sorted(p.name for p in (DESIGN / box["part"] / "diagrams").glob("*.html"))
    if others:
        y = para(s, 30, y, "Also in its diagrams folder", " · ".join(others), W - 60)

    if fuses:
        y = grid(s, 30, y, [("Fuse", 90), ("Rating", 90), ("Feeds", 640), ("Fed from", 330)],
                 [(f["id"], f.get("rating"), f.get("feeds"), f.get("fed_from")) for f in fuses], title="Fuses in the box")
    if relays:
        y = grid(s, 30, y, [("Id", 60), ("What it does", 360), ("Kind", 330), ("Control", 200), ("Contact", 200)],
                 [(r["id"], r.get("function"), (r.get("type") or "").split(" - ")[0],
                   " / ".join(x for x in (r.get("c86"), r.get("c85")) if x),
                   " → ".join(x for x in (r.get("c30"), r.get("c87")) if x)) for r in relays],
                 title="Switches and relays in the box")
    cids = cable_ids(box)
    if cids:
        cab = {c["id"]: c for c in table("cables")}
        y = grid(s, 30, y, [("Cable", 70), ("Run", 760), ("AWG", 70), ("Note", 350)],
                 [(i, cab[i]["run"], cab[i]["awg"], cab[i].get("note")) for i in cids if i in cab],
                 title="Its heavy cables")

    ends = D.device_ends()
    route_of = {d["id"]: (d.get("route") or "").strip() for d in table("devices")}
    used = set()
    if housings:
        s.text(30, y, "ITS PLUGS, CAVITY BY CAVITY", 10, weight=700, fill=MUTED)
        y += 16
        for h in housings:
            y = D.housing_block(s, h, by_h.get(h["code"], []), ends, route_of, used, y)
    if box["id"] == "PMU-BOX":
        nc = table("node_conductors")
        y = grid(s, 30, y, [("Id", 60), ("From", 430), ("To", 470), ("AWG", 70), ("Colour", 80), ("Note", 140)],
                 [(n["id"], n["src"], n["dst"], n["awg"], n["colour"], shorten(n.get("note") or "", 124, 11))
                  for n in nc], title=f"Inside the box: every connection ({len(nc)}, node_conductors)")
    if used:
        s.legend(30, y, [c for c in D.INK if c in used])
        y += 30
    s.text(30, y, "Solid wire: live. Dashed: run and capped. #12 / #16 / #20: a circular's contact size. "
                  "Nothing here is measured (R11). Generated by rx7.py diagrams from the record - do not edit.",
           10, fill=MUTED)
    s.w, s.h = W, y + 30
    return s


# ---------------------------------------------------------------- the overview

def other_end(c, own, hbox, hcodes):
    """Which box (or 'car') a cavity's far end is in: its source first, then where it lands."""
    src, lands = (c.get("src") or "").strip(), c.get("lands_on") or ""

    def from_text(t):
        for m in re.finditer(rf"(?<![\w-])({hcodes})\s+\d+", t):
            b = hbox.get(m.group(1))
            if b and b != own:
                return b
        if "PMU box" in t:
            return "PMU-BOX"
        if re.search(r"\bCUR\b", t) and own != "CUR":
            return "CUR"
        return None
    if re.match(r"^(O\d+|F\d+|K\d+|A\d+|N\d+|GND|CAN2|WAKE)", src):
        return "PMU-BOX" if own != "PMU-BOX" else None
    if src.startswith("SN"):
        if own != "CU":
            return "CU"
        return from_text(lands) or "car"
    return from_text(src) or from_text(lands) or "car"


def overview():
    boxes = {b["id"]: b for b in table("boxes")}
    hs = table("housings")
    hbox = {h["code"]: (h.get("box") or "") for h in hs}
    hcodes = "|".join(re.escape(c) for c in sorted(hbox, key=len, reverse=True))
    links, plugs = {}, {}
    for c in table("cavities"):
        own = hbox.get(c["housing"])
        if not own or c["state"] not in ("LIVE", "CAPPED"):
            continue
        plugs.setdefault(own, {}).setdefault(c["housing"], 0)
        plugs[own][c["housing"]] += 1
        far = other_end(c, own, hbox, hcodes)
        if far and far != "car" and far != own:
            # counted from each side apart: a wire between two plugs is a cavity at both ends
            links.setdefault(tuple(sorted((own, far))), {}).setdefault(own, set()).add(c["id"])
    # cables between boxes: a cable named in two boxes' joins / holds
    cab = {c["id"]: c for c in table("cables")}
    clinks = {}
    for i, c in cab.items():   # a cable whose run names two boxes joins them
        bs = sorted(b for b, row in boxes.items() if row["name"].lower() in (c.get("run") or "").lower())
        if len(bs) == 2:
            clinks.setdefault(tuple(bs), []).append(f"{i} {c['awg']} AWG")

    # where each box is drawn: layout only, no fact - the zones follow boxes.where
    POS = {"BAY-JCT": (50, 420, 250, 170), "DU": (420, 130, 330, 150), "CUR": (860, 130, 290, 150),
           "PMU-BOX": (420, 430, 330, 230), "CU": (860, 470, 290, 170),
           "BIN-BOX": (1290, 400, 350, 170), "AMP-DOCK": (1290, 690, 350, 150)}
    s = Sheet("The boxes - overview")
    s.text(30, 40, "THE BOXES · OVERVIEW", 20, weight=700)
    s.text(30, 64, "Every box of the overhaul in its zone, with the wires and cables that join them (D-596 to D-612). "
                   "Each box's own sheet is in its part folder. Generated by rx7.py diagrams - do not edit.", 12, fill=MUTED)
    for x, w, name in ((30, 300, "ENGINE BAY"), (380, 800, "DASH ZONE · wire only"), (1260, 410, "PASSENGER-SIDE CARGO BIN")):
        s.rect(x, 96, w, 800, fill="none", stroke=FAINT, sw=1.2, rx=10, dash="5 5")
        s.text(x + 14, 118, name, 11, weight=700, fill=MUTED)

    def card(bid):
        x, y, w, h = POS[bid]
        b = boxes[bid]
        s.rect(x, y, w, h, fill="#fff", stroke=TEXT, sw=2.5, rx=8)
        s.text(x + 14, y + 26, b["name"], 16, weight=700)
        yy = y + 48
        for code, n in sorted(plugs.get(bid, {}).items()):
            hh = next(h for h in hs if h["code"] == code)
            kind = {"HD": "circular", "HW": "hard-wired bundle"}.get(hh.get("series") or "", hh.get("leg_side") or "")
            s.text(x + 14, yy, shorten(f"{code} · {kind} · {n} of {hh.get('cavs')} in use", w - 28, 11), 11, fill=TEXT)
            yy += 16
        room = int((y + h - 12 - yy) / 16)
        for line in wrap(b.get("holds") or "", w - 28, 11)[:max(room, 0)]:
            s.text(x + 14, yy + 4, line, 11, fill=MUTED)
            yy += 16
    for bid in POS:
        if bid in boxes:
            card(bid)

    def label(x, y, lines, anchor="start"):
        for i, t in enumerate(lines):
            s.text(x, y + i * 17, t, 11, anchor=anchor, weight=700 if i == 0 else 400, fill=TEXT if i == 0 else MUTED)

    def n(a, b):
        return max((len(v) for v in links.get(tuple(sorted((a, b))), {}).values()), default=0)

    def cl(a, b):
        return clinks.get(tuple(sorted((a, b))), [])
    # PMU box - DU
    s.wire([(585, 430), (585, 280)], "", width=4)
    label(600, 345, [f"{n('PMU-BOX', 'DU')} wires", "hard-wired at the box", "DP-ICU at the DU"])
    # PMU box - CU
    s.wire([(750, 560), (860, 560)], "", width=4)
    label(805, 590, [f"{n('PMU-BOX', 'CU')} wires", "DP-DCU, DP-DCU-P"], anchor="middle")
    # PMU box - CUR
    s.wire([(750, 450), (900, 450), (900, 280)], "", width=4)
    label(915, 345, [f"{n('PMU-BOX', 'CUR')} wires", "winks · hazard"])
    # CU - CUR
    s.wire([(1090, 470), (1090, 280)], "", width=4)
    label(1105, 380, [f"{n('CU', 'CUR')} wires", "I²C"])
    # bin box - PMU box: the feed
    s.wire([(700, 660), (700, 700), (1220, 700), (1220, 500), (1290, 500)], "RED", width=6)
    label(960, 726, [" · ".join(cl("BIN-BOX", "PMU-BOX")) or "the feed", "the PMU box's feed"], anchor="middle")
    # bin box - amplifier dock
    s.wire([(1465, 570), (1465, 690)], "RED", width=6)
    label(1480, 620, [" · ".join(cl("AMP-DOCK", "BIN-BOX")) or "two leads", "two bolted leads"])
    # bin box - bay junction: under the car
    s.wire([(175, 590), (175, 870), (1655, 870), (1655, 485), (1640, 485)], "RED", width=6)
    label(915, 828, [" · ".join(cl("BAY-JCT", "BIN-BOX")) or "starter feed", "forward under the car: the starter feed and the cranking return"], anchor="middle")
    # out to the car
    s.wire([(420, 600), (330, 600)], "GRY", width=4)
    label(345, 625, ["engine", "L1-E1 to E3"])
    s.wire([(420, 470), (330, 470)], "GRY", width=4)
    label(345, 455, ["front, rear"])
    s.w, s.h = 1700, 930
    s.text(30, 920, "Grey: signal and switched wiring. Red: heavy cable. Counts are the record's live and capped cavities "
                    "whose far end is in the other box.", 10, fill=MUTED)
    return s


def main() -> int:
    rc = 0
    sheets = [(DESIGN / b["part"] / "diagrams" / f"{slug(b)}-plan.svg", lambda b=b: box_sheet(b)) for b in table("boxes")]
    sheets.append((DESIGN / "diagrams" / "boxes-plan.svg", overview))
    for path, fn in sheets:
        try:
            svg = fn().svg()
        except Refused as e:
            print(f"REFUSED {path.relative_to(D.ROOT)}: {e} - not written")
            rc = 2
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(svg, encoding="utf-8")
        print(f"wrote {path.relative_to(D.ROOT)}")
    return rc
