"""Option A: pin ladder. No layout engine — a fixed grid. One row per cavity, every wire a straight
horizontal line from its cavity to its device pin. Crossings are impossible by construction."""
from common import *

ROW, TOP, HX, HW, DX, DW = 34, 115, 30, 300, 820, 300
by_cav = {w[0]: w for w in WIRES}
rows = list(range(1, 13))
H = TOP + ROW * len(rows) + 120
s = Svg(DX + DW + 30, H, "ladder")
s.text(30, 36, "L1 ENGINE · housing L1-S1 → engine-bay devices", 20, weight=700)
s.text(30, 60, "Pin ladder: one row per cavity, wires run straight across. Read left to right.", 13, fill="#57606a")

# housing
s.add(f'<rect x="{HX}" y="{TOP - 30}" width="{HW}" height="{ROW * len(rows) + 30}" rx="6" fill="#f6f8fa" stroke="#1f2328" stroke-width="1.5"/>')
s.text(HX + 10, TOP - 10, f"{HOUSING[0]}  ·  {HOUSING[1]}", 14, weight=700)
for i, cav in enumerate(rows):
    y = TOP + i * ROW
    s.add(f'<line x1="{HX}" y1="{y}" x2="{HX + HW}" y2="{y}" stroke="#d0d7de"/>')
    cy = y + ROW / 2 + 5
    s.add(f'<circle cx="{HX + 20}" cy="{y + ROW / 2}" r="11" fill="#fff" stroke="#1f2328"/>')
    s.text(HX + 20, cy, str(cav), 12, anchor="middle", weight=700, pad=0)
    if cav in by_cav:
        w = by_cav[cav]
        s.text(HX + 40, cy, w[1], 13)
        s.text(HX + HW - 10, cy, w[2], 11, anchor="end", fill="#57606a")
        # wire
        wy = y + ROW / 2
        s.wire([(HX + HW, wy), (DX, wy)], w[3])
        label = f"L1-S1-{cav}  ·  {w[4].replace(" sh","")} AWG {w[3] if w[3] != "SHLD" else "shielded"}  ·  {w[8]}"
        s.text(HX + HW + 20, wy - 10, label, 11, fill="#57606a")
        if w[9]:
            rx = DX - 110
            s.add(f'<rect x="{rx}" y="{wy - 8}" width="44" height="16" rx="3" fill="#fff" stroke="#1f2328" stroke-width="1.5"/>')
            s.text(rx + 22, wy - 14, w[9], 11, anchor="middle", weight=700)
        # device
        s.add(f'<rect x="{DX}" y="{y + 3}" width="{DW}" height="{ROW - 6}" rx="5" fill="#fff" stroke="#1f2328" stroke-width="1.5"/>')
        s.text(DX + 10, cy, f"{w[6]}  {w[5]}", 13, weight=600)
        s.text(DX + DW - 10, cy, w[7], 12, anchor="end", weight=700)
    else:
        s.text(HX + 40, cy, "sealing plug", 12, fill="#8c959f")

# legend
ly = TOP + ROW * len(rows) + 40
x = 30
for c, name in (("RED", "RED  power / switched feed"), ("GRY", "GRY  analog input"), ("SHLD", "shielded core")):
    s.wire([(x, ly), (x + 40, ly)], c)
    x += 50 + s.text(x + 50, ly + 5, name, 12) + 30
s.text(30, ly + 40, "Every label measured against the real font at render time; an overlap refuses the build.", 11, fill="#57606a")
s.save("opt_ladder.svg")
