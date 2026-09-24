"""Option B: route map (transit-map style). The leg drawn as it runs in the car: trunk, grommet,
junction, breakouts. Each wire is its own coloured line inside the bundle, stacked in the order the
branches leave, so every wire peels off the outside and nothing crosses. 45-degree bends only."""
from common import *

SP = 13                       # centre spacing between parallel wires
order = [("RT02", [6]), ("RT03", [2]), ("RT04", [3, 4]), ("RT05", [1, 11])]
shift = {"RT02": -170, "RT03": -60, "RT04": 60, "RT05": 185}
by_cav = {w[0]: w for w in WIRES}
X0, XG, XJ, XE = 150, 360, 600, 980
BASE = 330
s = Svg(1340, 640, "metro")
s.text(30, 36, "L1 ENGINE · route map · housing L1-S1", 20, weight=700)
s.text(30, 60, "Where each wire physically goes. Bundle order = branch order, so wires peel off the outside.", 13, fill="#57606a")

n = sum(len(c) for _, c in order)
top = BASE - (n - 1) * SP / 2
i = 0
ends = {}
for rt, cavs in order:
    dy = shift[rt]
    for k, cav in enumerate(cavs):
        y = top + i * SP
        xb = XJ + 90  # all wires of a group bend together
        fan = k * 14          # a second 45-degree jog spreads a group so each end label has room
        yy = y + dy
        pts = [(X0, y), (xb, y), (xb + abs(dy), yy), (XE - 90, yy), (XE - 90 + fan, yy + fan), (XE, yy + fan)]
        s.wire(pts, by_cav[cav][3])
        ends.setdefault(rt, []).append((cav, yy + fan))
        i += 1

# housing at the dash post
hb = (top - 22, top + (n - 1) * SP + 22)
s.add(f'<rect x="{X0 - 110}" y="{hb[0]}" width="110" height="{hb[1] - hb[0]}" rx="6" fill="#f6f8fa" stroke="#1f2328" stroke-width="1.5"/>')
s.text(X0 - 55, hb[0] - 10, "L1-S1", 14, anchor="middle", weight=700)
s.text(X0 - 55, hb[1] + 18, "dash post", 11, anchor="middle", fill="#57606a")
for j, (rt, cavs) in enumerate(order):
    pass
i = 0
for rt, cavs in order:
    for cav in cavs:
        s.text(X0 - 12, top + i * SP + 4, str(cav), 10, anchor="end", weight=700, pad=0)
        i += 1

# grommet and junction marks
for x, name, sub in ((XG, "Firewall grommet", "pass. side"), (XJ, "Engine-bay junction", "")):
    s.add(f'<rect x="{x - 7}" y="{hb[0] + 4}" width="14" height="{hb[1] - hb[0] - 8}" rx="7" fill="none" stroke="#1f2328" stroke-width="2.5"/>')
    s.text(x, hb[0] - 10, name, 12, anchor="middle", weight=600)
    if sub:
        s.text(x, hb[1] + 18, sub, 11, anchor="middle", fill="#57606a")

# segment labels on the trunk
s.text((X0 + XG) / 2, hb[1] + 40, "RT01a · length measured at M-2", 11, anchor="middle", fill="#57606a")
s.text((XG + XJ) / 2, hb[1] + 40, "RT01b · length measured at M-2", 11, anchor="middle", fill="#57606a")

# branch ends
names = {r[0]: r[2] for r in ROUTES}
via = {r[0]: r[3] for r in ROUTES}
for rt, pts in ends.items():
    ys = [y for _, y in pts]
    y0, y1 = min(ys) - 16, max(ys) + 16
    s.add(f'<rect x="{XE}" y="{y0}" width="8" height="{y1 - y0}" fill="#1f2328"/>')
    s.text(XE + 18, y0 - 8, f"{rt} · {names[rt]}", 12, weight=700, fill="#0b5cad")
    s.text(XE + 18, y1 + 14, via[rt], 11, fill="#57606a")
    for cav, y in pts:
        w = by_cav[cav]
        extra = f"  via {w[9]}" if w[9] else ""
        s.text(XE + 18, y + 4, f"{w[6]} {w[7]}", 12, weight=700)
        s.text(XE + 18 + tw(f"{w[6]} {w[7]}", 12) + 10, y + 4, f"{w[5]} · cav {cav}{extra}", 12, fill="#57606a")

ly = 600
x = 30
for c, name in (("RED", "RED power / switched"), ("GRY", "GRY analog input"), ("SHLD", "shielded core")):
    s.wire([(x, ly), (x + 40, ly)], c)
    x += 50 + s.text(x + 50, ly + 5, name, 12) + 30
s.save("opt_metro.svg")
