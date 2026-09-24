#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diagrams.py - the two drawings of every harness leg (D-385), called by `rx7.py diagrams`.

Writes 02-PROJECTS/00-electrical/00-design/diagrams/<leg>/A-pin-ladder.svg and B-route-map.svg, and nothing
else. Like DECISIONS.md they are a pure, read-only projection of the record: rebuilt whole, never
edited, never looked at by `check`, never a reason to refuse a commit.

  A  pin ladder  one block per housing, one row per cavity, every wire a straight line from its
                 cavity to what it lands on. Crossings are impossible by construction.
  B  route map   the leg as it runs in the car, drawn like a transit map: every wire its own line,
                 stacked in the order its branch leaves the bundle, so wires peel off the outside
                 and never cross. 45-degree bends only.

Owns no facts. Reads (00-electrical):
  housings   code, leg, leg_side, where          which housings make up a leg
  cavities   housing, cav, circuit, src, awg,    every row of the ladder; colour is the ink
             colour, state, lands_on
  devices    id, device, terminals, route        "<terminal> -> <housing> <cav>" in terminals ties a
                                                 cavity to its device; route places the device
  routes     id, leg, from_node, to_node, via, ft  the tree the map is drawn along

THE OVERLAP RULE. Every label is measured with the real font (Noto Sans) before it is placed. A
label touching another label, or sitting on a wire, refuses the sheet: it is not written, the
reason is printed, and the exit code is 2. Nothing is ever drawn that has not passed.

Exit codes as rx7.py: 0 written, 2 a sheet was refused (the others are still written), 3 a crash.
Needs Pillow (python3-pillow) for font metrics.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AREA = ROOT / "02-PROJECTS" / "00-electrical"
OUT = AREA / "00-design" / "diagrams"
FONT = Path("/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf")

LEGS = [("L1 Engine", "L1-engine"), ("L2 Front", "L2-front"), ("L3 Dash", "L3-dash"), ("L4 Rear", "L4-rear")]

# insulation colour -> (ink, readable name). A thin dark outline under every wire keeps pale
# colours visible on paper.
INK = {"RED": "#d32f2f", "GRY": "#8d949e", "BLU": "#1e63c6", "ORN": "#ef6c00", "BLK": "#1b1b1b",
       "GRN": "#2e8b3e", "YEL": "#f2c318", "PNK": "#e8559c", "shielded": "#6b7280", "": "#b8bec6"}
TEXT, MUTED, FAINT, RULE, PANEL = "#1f2328", "#57606a", "#8c959f", "#d0d7de", "#f6f8fa"

try:
    from PIL import ImageFont
except ImportError:  # pragma: no cover
    print("diagrams: needs Pillow (sudo dnf install python3-pillow) - nothing written (rc 3)")
    sys.exit(3)

_fonts = {}


def tw(s: str, size: float, weight: int = 400) -> float:
    """Rendered width of s in Noto Sans at this size and weight, with a 3% safety margin."""
    k = (size, weight)
    if k not in _fonts:
        f = ImageFont.truetype(str(FONT), size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        _fonts[k] = f
    return _fonts[k].getlength(s) * 1.03


def wrap(s: str, width: float, size: float, weight: int = 400) -> list[str]:
    out, line = [], ""
    for word in s.split():
        t = f"{line} {word}".strip()
        if tw(t, size, weight) <= width or not line:
            line = t
        else:
            out.append(line)
            line = word
    return out + ([line] if line else [])


def shorten(s: str, width: float, size: float, weight: int = 400) -> str:
    """s cut at a word boundary to fit width, with an ellipsis when cut."""
    if tw(s, size, weight) <= width:
        return s
    out = ""
    for word in s.split():
        if tw(f"{out} {word} …".strip(), size, weight) > width:
            break
        out = f"{out} {word}".strip()
    return out + " …"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class Refused(Exception):
    pass


class Sheet:
    """An SVG under construction that refuses any label collision (the overlap rule)."""

    def __init__(self, title: str):
        self.title, self.parts, self.boxes, self.segs = title, [], [], []
        self.w = self.h = 0

    def add(self, s: str):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill=PANEL, stroke=TEXT, sw=1.5, rx=5, dash=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=12, anchor="start", weight=400, fill=TEXT, pad=2):
        w = tw(s, size, weight)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        box = (x0 - pad, y - size * 0.78 - pad, x0 + w + pad, y + size * 0.24 + pad, s)
        for b in self.boxes:
            if box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3]:
                raise Refused(f"label {s!r} collides with {b[4]!r}")
        self.boxes.append(box)
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
                 f'font-weight="{weight}" fill="{fill}">{esc(s)}</text>')
        return w

    def wire(self, pts, colour, width=5, dash=False):
        self.segs += [(a, b, width / 2 + 1) for a, b in zip(pts, pts[1:])]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        ink = INK.get(colour, INK[""])
        extra = ' stroke-dasharray="8 5"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{TEXT}" stroke-width="{width + 2}" '
                 f'stroke-linejoin="round"{extra}/>')
        self.add(f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{width}" stroke-linejoin="round"{extra}/>')
        if colour == "shielded":
            self.add(f'<path d="{d}" fill="none" stroke="#e5e7eb" stroke-width="2" stroke-dasharray="3 3"/>')

    def legend(self, x, y, colours):
        for c in colours:
            self.wire([(x, y), (x + 36, y)], c)
            x += 46 + self.text(x + 46, y + 4, c if c != "shielded" else "shielded core", 11) + 26
        return x

    def check_wires(self):
        for (ax, ay), (bx, by), r in self.segs:
            n = max(1, int(max(abs(bx - ax), abs(by - ay)) / 2))
            for i in range(n + 1):
                x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                for b in self.boxes:
                    if b[0] - r < x < b[2] + r and b[1] - r < y < b[3] + r:
                        raise Refused(f"label {b[4]!r} sits on a wire at {x:.0f},{y:.0f}")

    def svg(self) -> str:
        self.check_wires()
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.0f}" height="{self.h:.0f}" '
                f'viewBox="0 0 {self.w:.0f} {self.h:.0f}" font-family="Noto Sans, sans-serif">\n'
                f'<title>{esc(self.title)}</title>\n<rect width="100%" height="100%" fill="#fff"/>\n'
                + "\n".join(self.parts) + "\n</svg>\n")


# ---------------------------------------------------------------- the record

def table(name):
    with open(AREA / "data" / f"{name}.csv", newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f)]


CAV_RE = re.compile(r"\b((?:L\d-[A-Z0-9]+)|D[12])\s+(\d+)\b(?!\s*[–-]\s*\d)")
INLINE_RE = re.compile(r"\b\d+(?:\.\d+)?\s*k(?:Ω|Ohm)", re.I)


def device_ends():
    """{(housing, cav): [(device row, terminal, inline parts)]} from devices.terminals."""
    ends = {}
    for d in table("devices"):
        for line in re.split(r"<br>|\n", d.get("terminals") or ""):
            term = re.split(r"\s*(?:→|←|->|<-)\s*", line, maxsplit=1)[0].strip()
            inline = INLINE_RE.findall(line)
            for h, c in CAV_RE.findall(line):
                ends.setdefault((h, int(c)), []).append((d, term, inline))
    return ends


def load_leg(leg):
    housings = [h for h in table("housings") if (h.get("leg") or "").startswith(leg)]
    codes = [h["code"] for h in housings]
    cavs = [c for c in table("cavities") if c["housing"] in codes]
    cavs.sort(key=lambda c: (codes.index(c["housing"]), int(c["cav"] or 0)))
    return housings, cavs


def route_tree(leg):
    """The leg's routes as a tree rooted at the dash post: a route hangs under the route whose
    to_node its from_node begins (RT16 'Rear node' under RT15 'Rear node, cargo bin')."""
    rows = table("routes")
    mine = [r for r in rows if r["leg"] == leg]
    ids = {r["id"] for r in mine}
    changed = True
    while changed:  # pull in branches hung off this leg's nodes (the Sill run hangs off RT19)
        changed = False
        for r in rows:
            if r["id"] in ids:
                continue
            if any(r["from_node"] and m["to_node"].startswith(r["from_node"]) for m in mine):
                mine.append(r); ids.add(r["id"]); changed = True
    parent = {}
    for r in mine:
        for p in mine:
            if p is not r and r["from_node"] != "Dash post" and p["to_node"].startswith(r["from_node"]):
                parent[r["id"]] = p["id"]
    return mine, parent


# ---------------------------------------------------------------- A: pin ladder

def pin_ladder(leg, folder):
    housings, cavs = load_leg(leg)
    ends = device_ends()
    route_of = {d["id"]: (d.get("route") or "").strip() for d in table("devices")}
    by_h = {}
    for c in cavs:
        by_h.setdefault(c["housing"], []).append(c)

    HX, HW, MID, RW = 30, 360, 330, 560
    DX = HX + HW + MID
    s = Sheet(f"{leg} - pin ladder")
    s.text(30, 40, f"{leg.upper()} · A · PIN LADDER", 20, weight=700)
    s.text(30, 64, "One block per housing, one row per cavity. Every wire runs straight "
                   "from its cavity to where it lands. Read left to right.", 12, fill=MUTED)
    y = 110
    used = set()
    for h in housings:
        rows = by_h.get(h["code"], [])
        title = f"{h['code']}  ·  {h['leg_side']}  ·  {h.get('where') or ''}".rstrip(" ·")
        layout = []
        for c in rows:
            left = wrap(c["circuit"] or ("sealing plug" if c["state"] == "PLUG" else "—"),
                        HW - 64 - tw(c["src"] or "", 10), 12)
            right = wrap(c["lands_on"] or "", RW - 20, 11)
            layout.append((c, left, right, max(34, 17 * len(left) + 14, 16 * len(right) + 12)))
        top = y + 34
        total = sum(r[3] for r in layout)
        s.rect(HX, y, HW, 34 + total)
        s.text(HX + 12, y + 22, title, 13, weight=700)
        ry = top
        for c, left, right, rh in layout:
            s.add(f'<line x1="{HX}" y1="{ry:.1f}" x2="{HX + HW}" y2="{ry:.1f}" stroke="{RULE}"/>')
            cy = ry + rh / 2
            live = c["state"] in ("LIVE", "CAPPED")
            s.add(f'<circle cx="{HX + 20}" cy="{cy:.1f}" r="11" fill="#fff" stroke="{TEXT}"/>')
            s.text(HX + 20, cy + 4, c["cav"], 11, anchor="middle", weight=700, pad=0)
            lcol = TEXT if live else FAINT
            ly0 = cy - (len(left) - 1) * 8.5 + 4
            for i, t in enumerate(left):
                s.text(HX + 40, ly0 + 17 * i, t, 12, fill=lcol)
            if c["src"]:
                s.text(HX + HW - 10, cy + 4, c["src"], 10, anchor="end", fill=MUTED)
            if live:
                colour = c["colour"] or ""
                used.add(colour)
                s.wire([(HX + HW, cy), (DX, cy)], colour, dash=c["state"] == "CAPPED")
                devs = ends.get((c["housing"], int(c["cav"])), [])
                rts = sorted({route_of.get(d["id"], "") for d, _, _ in devs} - {""}) or \
                    [r for r in [(c.get("route") or "").strip()] if r]
                awg = (c["awg"] or "").replace(" sh", "")
                bits = [f"{c['housing']}-{c['cav']}", f"{awg} AWG {colour}".strip()]
                if rts:
                    bits.append("/".join(rts))
                if c["state"] == "CAPPED":
                    bits.append("capped at the far end")
                s.text(HX + HW + 16, cy - 10, "  ·  ".join(bits), 10, fill=MUTED)
                inline = sorted({p for _, _, parts in devs for p in parts})
                if len(inline) == 1:
                    bx = DX - 70
                    s.rect(bx, cy - 7, 44, 14, fill="#fff", rx=3)
                    s.text(bx + 22, cy + 18, inline[0], 10, anchor="middle", weight=700)
                s.rect(DX, ry + 3, RW, rh - 6, fill="#fff")
            else:
                label = {"PLUG": "sealing plug", "RESERVED": "reserved - no wire in the leg"}.get(c["state"], c["state"])
                s.text(HX + HW + 16, cy + 4, label, 10, fill=FAINT)
            ty0 = cy - (len(right) - 1) * 8 + 4
            for i, t in enumerate(right):
                s.text(DX + 10, ty0 + 16 * i, t, 11, fill=TEXT if live else FAINT)
            ry += rh
        y = top + total + 36
    s.w, s.h = DX + RW + 30, y + 60
    s.legend(30, y + 10, [c for c in INK if c in used])
    s.text(30, y + 40, "Solid wire: live. Dashed: run and capped at the far end. A box on a wire is an inline "
                       "resistor. Generated by rx7.py diagrams - do not edit.", 10, fill=MUTED)
    return s


# ---------------------------------------------------------------- B: route map

def route_map(leg, folder):
    housings, cavs = load_leg(leg)
    ends = device_ends()
    routes, parent = route_tree(leg)
    rmap = {r["id"]: r for r in routes}
    route_of = {d["id"]: (d.get("route") or "").strip() for d in table("devices")}
    kids = {}
    for r in routes:
        kids.setdefault(parent.get(r["id"], "ROOT"), []).append(r["id"])

    # every wire that leaves the post: which route does it end on? The device's route when the far
    # end is a device, else the cavity's own (a node, a receptacle, a socket).
    at_post = {h["code"] for h in housings if h.get("where") == "Dash post"}
    wires = {}
    for c in cavs:
        if c["state"] not in ("LIVE", "CAPPED") or c["housing"] not in at_post:
            continue
        devs = ends.get((c["housing"], int(c["cav"])), [])
        placed = [(d, t) for d, t, _ in devs if route_of.get(d["id"]) in rmap]
        own = (c.get("route") or "").strip()
        leaf = route_of[placed[0][0]["id"]] if placed else (own if own in rmap else "UNROUTED")
        also = sorted({route_of[d["id"]] for d, _ in placed} - {leaf})
        if placed:
            d, t = placed[0]
            end = f"{d['device']} · {t}" if t else d["device"]
        else:
            end = shorten(c["lands_on"] or "", 380, 11, 700)
        wires.setdefault(leaf, []).append((c, end, also))

    # a route that has branches AND wires of its own: those wires stop at its node, drawn as a
    # stub branch ("ends at") so they peel off like any other
    def carries(rid):
        return bool(wires.get(rid)) or any(carries(k) for k in kids.get(rid, []))
    for rid in list(wires):
        if rid in rmap and any(carries(k) for k in kids.get(rid, [])):
            stub = rid + "@"
            wires[stub] = wires.pop(rid)
            kids[rid].insert(0, stub)
            parent[stub] = rid
            rmap[stub] = dict(rmap[rid], to_node="ends at " + rmap[rid]["to_node"].split(",")[0], stub=True)
    if "UNROUTED" in wires:
        kids.setdefault("ROOT", []).append("UNROUTED")
        rmap["UNROUTED"] = {"id": "", "to_node": "No route in the record yet",
                            "via": "neither devices.route nor cavities.route says - lands_on names the far end",
                            "ft": "", "stub": True}
    depth = {}

    def walk(rid, d):
        depth[rid] = d
        for k in kids.get(rid, []):
            walk(k, d + 1)
    for k in kids.get("ROOT", []):
        walk(k, 1)

    def leaves(rid):
        ks = [k for k in kids.get(rid, []) if count(k)]
        return [rid] if not ks else [x for k in ks for x in leaves(k)]

    def count(rid):
        return len(wires.get(rid, [])) + sum(count(k) for k in kids.get(rid, []))

    order = [x for k in kids.get("ROOT", []) if count(k) for x in leaves(k)]
    SP, GAP, COL = 18, 70, 250
    maxd = max((depth[l] for l in order), default=1)
    X0 = 200
    XE = X0 + COL * maxd + 60

    # leaf bands top to bottom; a leaf's wires sit at SP spacing inside its band
    y, band = 150, {}
    for l in order:
        n = len(wires.get(l, []))
        band[l] = (y, [y + 30 + i * SP for i in range(n)])
        y += 30 + n * SP + GAP
    H = y
    # the start stack at the post: every wire in leaf order, packed tight
    stack = [(l, i) for l in order for i in range(len(wires.get(l, [])))]
    total = len(stack) * SP
    sy0 = max(150, (H - total) / 2)
    start_y = {k: sy0 + j * SP for j, k in enumerate(stack)}

    # a wire's height on each route along its path: the centre of that route's wires, packed
    def path(l):
        p = [l]
        while parent.get(p[-1]):
            p.append(parent[p[-1]])
        return list(reversed(p))

    def ys_on(rid):
        ls = [l for l in order if rid in path(l)]
        ks = [(l, i) for l in ls for i in range(len(wires.get(l, [])))]
        if len(path(ls[0])) == depth[rid] and ls == [rid]:
            return {k: band[rid][1][k[1]] for k in ks}
        # internal route: centred on the middle of its leaves' bands
        mid = (band[ls[0]][1][0] + band[ls[-1]][1][-1]) / 2
        return {k: mid - (len(ks) - 1) * SP / 2 + j * SP for j, k in enumerate(ks)}

    s = Sheet(f"{leg} - route map")
    s.text(30, 40, f"{leg.upper()} · B · ROUTE MAP", 20, weight=700)
    s.text(30, 64, "Where every wire physically runs. Bundle order is branch order, so each wire peels off "
                   "the outside of the bundle and nothing crosses. Lengths come from routes.ft once measured (M-2).",
           12, fill=MUTED)

    used = set()
    route_y = {rid: ys_on(rid) for rid in depth if count(rid)}
    for l in order:
        for i, (c, end, also) in enumerate(wires.get(l, [])):
            k = (l, i)
            pts = [(X0, start_y[k])]
            x = X0
            for rid in path(l):
                ty = route_y[rid][k]
                x0 = X0 + COL * (depth[rid] - 1) + 40
                dy = ty - pts[-1][1]
                pts += [(x0, pts[-1][1]), (x0 + abs(dy), ty)]
            pts.append((XE, band[l][1][i]))
            colour = c["colour"] or ""
            used.add(colour)
            s.wire(pts, colour, dash=c["state"] == "CAPPED")

    # the post: one box, each wire named by housing and cavity where it starts
    s.rect(X0 - 150, sy0 - 34, 150, total + 50)
    s.text(X0 - 75, sy0 - 14, "Dash post", 13, anchor="middle", weight=700)
    for (l, i) in stack:
        c = wires[l][i][0]
        s.text(X0 - 10, start_y[(l, i)] + 4, f"{c['housing']} {c['cav']}", 10, anchor="end", weight=700, pad=0)

    # internal routes: a marker where the bundle splits, tagged on its left, above the bundle
    # (the wires only diverge to its right); via and length go in the route table below
    for rid, yy in route_y.items():
        if rid in order:
            continue
        top, bot = min(yy.values()), max(yy.values())
        nx = X0 + COL * depth[rid] + 20      # just upstream of where its branches split
        s.rect(nx - 6, top - 9, 12, bot - top + 18, fill="none", sw=2.5, rx=6)
        s.text(nx - 14, top - 16, f"{rid} → {rmap[rid]['to_node'].split(',')[0]}", 11, anchor="end", weight=600)

    # leaf ends: the branch's name, then one line per wire
    for l in order:
        r = rmap[l]
        ys = band[l][1]
        s.rect(XE, ys[0] - 12, 8, ys[-1] - ys[0] + 24, fill=TEXT, stroke=TEXT, rx=1,
               dash="4 3" if l == "UNROUTED" else "")
        ft = f"{r['ft']} ft" if r.get("ft") else "length at M-2"
        head = f"{r['id']} · {r['to_node']}" if r["id"] else r["to_node"]
        s.text(XE + 20, ys[0] - 18, head, 12, weight=700, fill="#0b5cad")
        for (c, end, also), yy in zip(wires[l], ys):
            w = s.text(XE + 20, yy + 4, end, 11, weight=700)
            tail = f"{c['housing']} {c['cav']} · {c['circuit']}"
            if also:
                tail += f" · also on {'/'.join(also)}"
            if c["state"] == "CAPPED":
                tail += " · capped"
            s.text(XE + 20 + w + 10, yy + 4, tail, 11, fill=MUTED)
        if r["id"] and not r.get("stub"):
            s.text(XE + 20, ys[-1] + 24, f"{r['via']} · {ft}", 10, fill=MUTED)
        elif not r["id"]:
            s.text(XE + 20, ys[-1] + 24, r["via"], 10, fill=MUTED)
    # the route table: every run on this sheet, where it goes, what it follows, how long
    ty = H + 10
    s.text(30, ty, "ROUTES", 11, weight=700, fill=MUTED)
    for r in sorted((rmap[x] for x in depth if x in rmap and not rmap[x].get("stub") and count(x)), key=lambda r: r["id"]):
        ty += 20
        ft = f"{r['ft']} ft measured" if r.get("ft") else "length: measure at M-2"
        s.text(30, ty, r["id"], 11, weight=700)
        s.text(80, ty, f"{r['from_node']} → {r['to_node']}  ·  via {r['via']}  ·  {ft}", 11)
    H = ty + 30
    s.w = max(b[2] for b in s.boxes) + 30
    s.h = H + 60
    s.legend(30, H + 10, [c for c in INK if c in used])
    s.text(30, H + 40, "Solid: live. Dashed: run and capped. Only wires that leave the post are drawn; "
                       "sealing plugs and reserved cavities are on sheet A. Generated by rx7.py diagrams - do not edit.",
           10, fill=MUTED)
    return s


def main() -> int:
    rc = 0
    for leg, folder in LEGS:
        d = OUT / folder
        d.mkdir(parents=True, exist_ok=True)
        for name, fn in (("A-pin-ladder.svg", pin_ladder), ("B-route-map.svg", route_map)):
            try:
                svg = fn(leg, folder).svg()
            except Refused as e:
                print(f"REFUSED {folder}/{name}: {e} - not written")
                rc = 2
                continue
            (d / name).write_text(svg, encoding="utf-8")
            print(f"wrote {d.relative_to(ROOT)}/{name}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
