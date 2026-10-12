"""DCU board rev 0.04 (Y12, D-458, D-465): placement, rip-up and the drawn routes (v11).

Placement
  J4   the 2 x 13, three pitches (7.62 mm) LEFT of the 2 x 10: its right end, and the gap to the Teensy's
       USB end, stay where they were (new pins 7..26 sit on the old pads 1..20).
  H1   down to (4, 15), under the header's left end.
  F1 / R72 / R71 / TP1  at the header's right end, by pins 21-26, in the gap to the Teensy.
  R52 / R54 between H1 and U12, R53 / R3 / C24 below H1, R51 above U12 on the SDA trunk.
Drawn here, locked: see the comments in the routes section. Left for the router: ENC_FAN_A, ENC_TEMP_B,
ENC_SEAT_DRV_A/B, ENC_SEAT_PASS_B, JOY_X / JOY_Y / JOY_PRESS (the pins east of column 4).

argv: src.kicad_pcb netlist out.kicad_pcb"""
import pcbnew, sys, re, math
MM = pcbnew.FromMM; T = pcbnew.ToMM
SRC, NET, OUT = sys.argv[1:4]
K = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
F, B = pcbnew.F_Cu, pcbnew.B_Cu


def V(x, y): return pcbnew.VECTOR2I(MM(x), MM(y))


def parse(s):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s); st = [[]]
    for t in toks:
        if t == '(': st.append([])
        elif t == ')': x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return st[0][0]


def find(n, k): return [c for c in n if isinstance(c, list) and c and c[0] == k]


def val(n, k):
    f = find(n, k); return f[0][1] if f and len(f[0]) > 1 else None


t = parse(open(NET).read())
comps = {}
for c in find(find(t, 'components')[0], 'comp'):
    props = {val(p, 'name'): (val(p, 'value') or "") for p in find(c, 'property')}
    comps[val(c, 'ref')] = dict(value=val(c, 'value'), fp=val(c, 'footprint'), uuid=val(c, 'tstamps'), dnp='dnp' in props, note=props.get('Note'))
pinnet = {}
for n in find(find(t, 'nets')[0], 'net'):
    for x in find(n, 'node'): pinnet[(val(x, 'ref'), val(x, 'pin'))] = val(n, 'name')

b = pcbnew.LoadBoard(SRC)


def net(name):
    ni = b.FindNet(name)
    if ni is None: ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni)
    return ni


fps = {f.GetReference(): f for f in b.GetFootprints()}
sheetname, sheetfile = fps["U12"].GetSheetname(), fps["U12"].GetSheetfile()


def load(fpid):
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(K + lib + ".pretty", name); assert fp is not None, fpid
    fp.SetFPID(pcbnew.LIB_ID(lib, name)); return fp


def make(ref):
    c = comps[ref]; fp = load(c["fp"])
    fp.SetReference(ref); fp.SetValue(c["value"]); fp.SetPath(pcbnew.KIID_PATH("/" + c["uuid"]))
    fp.SetSheetname(sheetname); fp.SetSheetfile(sheetfile); fp.SetDNP(c["dnp"])
    if c["note"]:
        fld = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, "Note"); fld.SetText(c["note"]); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab); fp.Add(fld)
    b.Add(fp); return fp


# ---------------------------------------------------------------- placement
J4X, PT = 14.0 - 3 * 2.54, 2.54


def col(k): return J4X + k * PT          # column k of the header, 0..12


def gap(k): return J4X + (k + 0.5) * PT  # between columns k and k+1


TOP, BOT = 5.06, 7.6                     # the header's two rows (even pins / odd pins)
old = fps["J4"]; o_path = old.GetPath(); vis = old.Reference().IsVisible(); b.Remove(old)
j4 = make("J4"); j4.SetOrientationDegrees(90); j4.SetPosition(V(J4X, BOT)); j4.SetPath(o_path)
j4.Reference().SetVisible(vis)
fps["J4"] = j4

for ref, f in fps.items():
    if ref.startswith("H"): continue
    if ref in comps and f.GetValue() != comps[ref]["value"]:
        print("value", ref, f.GetValue(), "->", comps[ref]["value"]); f.SetValue(comps[ref]["value"])
    for p in f.Pads():
        w = pinnet.get((ref, p.GetNumber()))
        if w and w != p.GetNetname(): p.SetNet(net(w))
for ref in ("R39", "R41"):
    c = comps[ref]; f = fps[ref]
    if c["note"] and not any(fl.GetName() == "Note" for fl in f.GetFields()):
        fld = pcbnew.PCB_FIELD(f, pcbnew.FIELD_T_USER, "Note"); fld.SetText(c["note"]); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab); f.Add(fld)

fps["H1"].SetPosition(V(4.0, 15.0))
moves = {
    "R52": (8.55, 14.225, 90),    # SCL pull-up: its old junction (via 8.10,13.70 and both F tracks) still lands in its pads
    "R54": (8.55, 18.7, 90),      # EXP_RESET pull-down, beside U12 pin 3's via
    "R53": (2.495, 20.45, 90),    # EXP_INT pull-up, below H1
    "R3": (5.245, 20.45, 90),     # PG_5V pull-up, below H1
    "C24": (2.525, 24.5, 270),    # U12's decoupling, below R53 (the strip above U12 carries two signal tails now)
    "R51": (19.4, 13.65, 90),     # SDA pull-up, its pad 2 on the SDA trunk
}
for r, (x, y, rot) in moves.items():
    fps[r].SetOrientationDegrees(rot); fps[r].SetPosition(V(x, y))


def put(ref, x, y, rot=0, bottom=False):
    f = make(ref)
    f.SetPosition(V(x, y))
    if bottom: f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot)
    for p in f.Pads():
        n = pinnet.get((ref, p.GetNumber()))
        if n: p.SetNet(net(n))
    f.Reference().SetVisible(False)
    fps[ref] = f


put("F1", 43.75, 3.6, 270)        # pad 1 under the +5V track along the top edge, pad 2 level with pin 26
put("R72", 44.9, 7.3, 180)        # pad 2 PNL_SCL toward J4, pad 1 I2C_SCL toward the Teensy
put("R71", 44.9, 11.76, 90)       # astride the +3V3 trunk (it passes between the pads): pad 1 on the SDA trunk below it, pad 2 PNL_SDA above
put("TP1", 39.0, 7.6, 0, True)    # bottom side, beside pin 25
for p in j4.Pads():
    n = pinnet.get(("J4", p.GetNumber()))
    if n: p.SetNet(net(n))

# ---------------------------------------------------------------- rip-up
J4N = set('/' + n for n in 'ROW1 ROW2 ROW3 COL1 COL2 COL3 ENC_FAN_A ENC_FAN_B ENC_TEMP_A ENC_TEMP_B ENC_SEAT_DRV_A ENC_SEAT_DRV_B ENC_SEAT_PASS_A ENC_SEAT_PASS_B JOY_X JOY_Y JOY_PRESS'.split())
WX, WY = 48.2, 13.0


def inside(x, y): return x < WX and y < WY


def P(v): return (T(v.x), T(v.y))


def pts_of(tr): return [P(tr.GetPosition())] if tr.Type() == pcbnew.PCB_VIA_T else [P(tr.GetStart()), P(tr.GetEnd())]


def clip(a, c):
    n = 400; keep = []; run = None
    for i in range(n + 1):
        s = i / n; x, y = a[0] + (c[0] - a[0]) * s, a[1] + (c[1] - a[1]) * s
        if not inside(x, y):
            if run is None: run = [(x, y), (x, y)]
            else: run[1] = (x, y)
        elif run is not None:
            keep.append(run); run = None
    if run is not None: keep.append(run)
    return [(p, q) for p, q in keep if math.hypot(q[0] - p[0], q[1] - p[1]) > 0.15]


ALL = list(b.GetTracks())      # taken once: pcbnew's GetTracks() breaks after the first Remove
DEAD = set()
ADD = []                       # (net, [points], width, layer, locked)
VIAS = []                      # (net, x, y, dia, drill)


def kill(tr): DEAD.add(id(tr))


def near(p, x, y, r=0.03): return math.hypot(p[0] - x, p[1] - y) < r


gone = clipped = 0
for tr in ALL:
    if tr.GetNetname() not in J4N: continue
    if tr.Type() == pcbnew.PCB_VIA_T:
        if inside(*P(tr.GetPosition())): kill(tr); gone += 1
        continue
    a, c = P(tr.GetStart()), P(tr.GetEnd())
    if not inside(*a) and not inside(*c): continue
    parts = clip(a, c)
    if not parts: kill(tr); gone += 1; continue
    p, q = parts[0]
    tr.SetStart(V(*p)); tr.SetEnd(V(*q)); clipped += 1
    for p, q in parts[1:]:
        ADD.append((tr.GetNetname(), [p, q], T(tr.GetWidth()), tr.GetLayer(), False))
# ENC_TEMP_A ran on through the strip above U12 where C24 / R51 now sit: back to its trunk's end at (20.46, 15.34)
for tr in ALL:
    if tr.GetNetname() == "/ENC_TEMP_A" and id(tr) not in DEAD and all(p[0] < 20.47 and p[1] < 16 for p in pts_of(tr)):
        kill(tr); gone += 1
for tr in ALL:                                   # its trunk now starts at the new via (21.2, 15.34)
    if tr.GetNetname() == "/ENC_TEMP_A" and id(tr) not in DEAD and tr.Type() != pcbnew.PCB_VIA_T:
        a, c = pts_of(tr)
        if near(a, 20.46, 15.34, 0.05): tr.SetStart(V(21.2, 15.34))
        elif near(c, 20.46, 15.34, 0.05): tr.SetEnd(V(21.2, 15.34))
for tr in ALL:
    if tr.GetNetname() == "/ENC_FAN_B" and id(tr) not in DEAD and all(p[0] < 27.28 and 12.9 < p[1] < 13.8 for p in pts_of(tr)):
        kill(tr); gone += 1
print("header nets: removed", gone, "clipped", clipped)


def rip(netname, pred):
    n = 0
    for tr in ALL:
        if tr.GetNetname() != netname or id(tr) in DEAD: continue
        if pred(pts_of(tr), tr): kill(tr); n += 1
    print("rip", netname, n)


def isF(tr): return tr.Type() != pcbnew.PCB_VIA_T and tr.GetLayer() == F


def isB(tr): return tr.Type() != pcbnew.PCB_VIA_T and tr.GetLayer() == B


# +3V3: what met at the old pin 1 (F to the trunk's end at 19.31,11.76; B down to 17.55,13.36), the chain round the old H1 corner
rip("+3V3", lambda pts, tr: any(near(p, 14.0, 7.6) for p in pts)
    or (isF(tr) and all(p[0] < 19.4 and p[1] < 11.9 for p in pts))
    or (isB(tr) and all(p[0] < 17.6 and p[1] < 13.4 for p in pts) and any(near(p, 14.0, 9.81) for p in pts))
    or (isF(tr) and all(p[0] < 8.05 and p[1] > 14.0 for p in pts))
    or (isF(tr) and all(p[0] <= 8.05 and 15.0 < p[1] < 21 for p in pts)))
# +5V: the wrap round the old left end and its via; the top-edge track from the Teensy stays
rip("+5V", lambda pts, tr: (isF(tr) and all(p[0] < 16.3 and p[1] < 10.3 for p in pts)) or (isF(tr) and all(p[1] < 3.0 for p in pts)))
# I2C_SDA: the old R51 link along y 12.37
rip("/I2C_SDA", lambda pts, tr: len(pts) == 2 and all(p[0] < 18.22 and p[1] < 13.4 for p in pts) and not all(abs(p[0] - 18.21) < 0.01 for p in pts))
# EXP_INT / EXP_RESET / PG_5V: the old runs west to R53 / R54 / R3
rip("/EXP_INT", lambda pts, tr: len(pts) == 2 and all(p[0] < 9.66 for p in pts))
rip("/EXP_RESET", lambda pts, tr: isF(tr) and all(p[0] < 9.82 and p[1] > 17.7 for p in pts))
rip("/PG_5V", lambda pts, tr: isF(tr) and all(p[0] < 9.75 for p in pts))
# GND: the locked rail of the old pins 2 / 20, the vias under the new header and the new H1, the old C24 / R54 stubs
n = 0
for tr in ALL:
    if tr.GetNetname() != "GND" or id(tr) in DEAD: continue
    pts = pts_of(tr)
    k = all(p[0] < 40 and p[1] < 6 for p in pts)
    k = k or any(math.hypot(p[0] - 4.0, p[1] - 15.0) < 4.3 for p in pts)
    k = k or any(near(p, 7.25, 8.32, 0.05) or near(p, 19.28, 15.47, 0.05) or near(p, 22.32, 14.50, 0.05) for p in pts)
    if k: kill(tr); n += 1
print("rip GND", n)

# ---------------------------------------------------------------- the drawn routes (v11)
# Everything that used to go round the header's left end still does, on B.Cu, nested: ENC_FAN_B, ENC_TEMP_A,
# ENC_SEAT_PASS_A and I2C_SCL run back along the top of the header, round pins 2 / 1 and on under the bottom
# row to their old runs south-west of it. No column gap is used by them, so no pin is boxed in.
# The six west signals: COL2 / COL3 on B.Cu from their pins (they end as the southmost lanes), ROW1 / ROW2 /
# ROW3 / COL1 on F.Cu over them, dropping to B.Cu in a staircase of vias north-east of the +5V diagonal.


def track(netname, pts, w=0.25, layer=F, lock=True): ADD.append((netname, pts, w, layer, lock))


def via(netname, x, y, d=0.6, dr=0.3): VIAS.append((netname, x, y, d, dr))


W2 = 0.2
# ---- +5V: a new top-edge track (0.4 mm further out, to leave a lane for the GND rail) - down column gap 1-2
# (0.4 mm between the pads) - east under the bottom row - its OLD via
g = gap(1)
track("+5V", [(50.0, 2.76), (48.16, 0.92), (g + 0.41, 0.92), (g, 1.33), (g, 3.6)], 0.6)
track("+5V", [(g, 3.6), (g, 9.05)], 0.4)
track("+5V", [(g, 9.05), (g, 9.44), (10.9, 10.15), (16.26, 10.15)], 0.6)
track("+5V", [(43.75, 0.92), (43.75, 2.2)], 0.6)                                # F1 pad 1
track("/+5V_PNL", [(43.75, 5.0), (43.69, 5.06), (col(12), TOP)], 0.6)           # F1 pad 2 - pin 26

# ---- the four nested B.Cu runs: along the top (y), down the left (x), under the bottom row (y)
#                 top   left  bottom
NEST = {"/ENC_FAN_B": (3.8, 5.1, 9.0), "/ENC_TEMP_A": (3.4, 4.7, 9.4), "/ENC_SEAT_PASS_A": (3.0, 4.3, 9.8), "/I2C_SCL": (2.6, 3.9, 10.2)}


def wrap(name):
    yt, xl, yb = NEST[name]
    k = 3.8 - yt                          # how far out this lane sits from the innermost
    return [(6.0 - k * 0.4142, yt), (xl, 4.7 - k * 0.4142), (xl, 8.6 + k * 0.75), (xl + 0.4 + k * 0.25, yb)]


# ENC_FAN_B: pin 10 - top - left - under the row - down at x 15.27 to the strip above U12 - F.Cu - B.Cu under the
# SDA riser and R51 - F.Cu onto its trunk's west end
yt, xl, yb = NEST["/ENC_FAN_B"]
track("/ENC_FAN_B", [(col(4), TOP), (col(4), 4.2), (col(4) - 0.4, yt)] + wrap("/ENC_FAN_B") + [(11.9, yb), (15.27, 12.37), (15.27, 13.45)], W2, B)
via("/ENC_FAN_B", 15.27, 13.45)
track("/ENC_FAN_B", [(15.27, 13.45), (16.6, 13.45), (17.55, 14.4)])
via("/ENC_FAN_B", 17.55, 14.4)
track("/ENC_FAN_B", [(17.55, 14.4), (17.75, 14.6), (22.3, 14.6)], W2, B)
via("/ENC_FAN_B", 22.3, 14.6)
track("/ENC_FAN_B", [(22.3, 14.6), (26.46, 14.6), (27.27, 13.79)])
# ENC_TEMP_A: pin 11 - up gap 5-6 - top - left - under the row - its old run at x 12.73 - its old via - F.Cu - B.Cu - trunk
yt, xl, yb = NEST["/ENC_TEMP_A"]
track("/ENC_TEMP_A", [(col(5), BOT), (gap(5), 6.33), (gap(5), yt + 0.7), (gap(5) - 0.7, yt)] + wrap("/ENC_TEMP_A") + [(10.6, yb), (12.73, 11.53), (12.73, 13.10), (13.11, 13.48)], W2, B)
via("/ENC_TEMP_A", 13.11, 13.48)
track("/ENC_TEMP_A", [(13.11, 13.48), (13.83, 14.2), (16.4, 14.2), (17.55, 15.35)])
via("/ENC_TEMP_A", 17.55, 15.35)
track("/ENC_TEMP_A", [(17.55, 15.35), (17.8, 15.1), (20.96, 15.1), (21.2, 15.34)], W2, B)
via("/ENC_TEMP_A", 21.2, 15.34)
# ENC_SEAT_PASS_A: pin 15 - up gap 6-7 - top - left - under the row - its old run at x 9.02
yt, xl, yb = NEST["/ENC_SEAT_PASS_A"]
track("/ENC_SEAT_PASS_A", [(col(7), BOT), (gap(6), 6.33), (gap(6), yt + 0.7), (gap(6) - 0.7, yt)] + wrap("/ENC_SEAT_PASS_A") + [(7.3, yb), (9.02, 11.52), (9.02, 13.08)], W2, B)
# I2C_SCL: R72 pad 1 - a via - along the whole top - left - under the row - R52's junction via
yt, xl, yb = NEST["/I2C_SCL"]
track("/I2C_SCL", [(45.6, 3.0), (45.3, 3.3), (24.4, 3.3), (23.7, yt)] + wrap("/I2C_SCL") + [(6.2, yb), (8.10, 12.1), (8.10, 13.70)], W2, B)
via("/I2C_SCL", 45.6, 3.0)
track("/I2C_SCL", [(45.6, 3.0), (45.6, 7.3), (45.81, 7.3)])

# ---- the panel lines, the spare
track("/PNL_SCL", [(43.99, 7.3), (43.02, 6.33), (gap(11), 6.33), (col(11), TOP)])
track("/PNL_SDA", [(44.9, 10.85), (44.4, 10.35), (42.95, 8.9), (gap(10) + 0.45, 8.9), (gap(10), 8.45), (gap(10), 6.33), (col(10), TOP)])
track("/SPARE", [(col(12), BOT), (39.0, BOT)], 0.25, B)

# ---- +3V3: pin 1 - under the header's left end - the rail above U12 - on to the trunk from the Teensy's 3V3
track("+3V3", [(col(0), BOT), (col(0), 10.93), (7.9, 12.45), (9.5, 12.45), (9.75, 12.7), (17.2, 12.7), (18.14, 11.76), (19.31, 11.76)])
track("+3V3", [(12.0, 12.7), (12.0, 14.93)])
via("+3V3", 20.75, 13.96)                                                       # R51 pad 1 - the B.Cu +3V3 line under it
track("+3V3", [(20.75, 13.66), (20.75, 13.96)], 0.25, B)
track("+3V3", [(20.75, 13.96), (20.15, 14.56), (19.4, 14.56)])
# R53 / R3 / C24 below H1: from R52 pad 1, a via, B.Cu down the left of the SCL run
track("+3V3", [(8.55, 15.14), (7.75, 15.14), (7.35, 15.35)])
via("+3V3", 7.35, 15.35)
track("+3V3", [(7.35, 15.35), (6.9, 15.8), (6.9, 22.2)], 0.25, B)
via("+3V3", 6.9, 22.2)
track("+3V3", [(6.9, 22.2), (6.06, 21.36), (2.495, 21.36)])
track("+3V3", [(2.495, 21.36), (2.525, 23.55)])                                 # C24 pad 1

# ---- EXP_RESET, EXP_INT, PG_5V
track("/EXP_RESET", [(9.81, 17.82), (9.6, 18.6), (9.0, 19.3), (8.55, 19.61)])


def arc(r, angs): return [(4.0 + r * math.cos(math.radians(a)), 15.0 + r * math.sin(math.radians(a))) for a in angs]


track("/EXP_INT", [(9.64, 16.22), (9.47, 16.05), (7.475, 16.05)] + arc(3.63, (30, 45, 60, 75, 90, 105)) + [(2.495, 19.3), (2.495, 19.54)])
track("/PG_5V", [(9.70, 16.96), (9.59, 16.85), (7.692, 16.85)] + arc(4.13, (30, 45, 60, 72)) + [(5.245, 19.3), (5.245, 19.54)])

# ---- the six west signals
# B.Cu lanes between the bus and the +5V run, x 21 - 25 (0.2 mm tracks on 0.41):   then east of x 26:
S = {"COL1": 10.33, "ROW3": 10.74, "ROW1": 11.15, "COL2": 11.56, "COL3": 11.97, "ROW2": 12.38}
L = {"COL1": 10.65, "ROW3": 11.11, "ROW1": 11.56, "COL2": 12.01, "COL3": 12.46}
# COL3: pin 8 - down gap 2-3 on B.Cu - east under the row - south-east beside the +5V diagonal - its old lane
track("/COL3", [(col(3), TOP), (gap(2), 6.33), (gap(2), 8.6), (13.43, 9.3), (17.9, 9.3), (17.9 + S["COL3"] - 9.3, S["COL3"]), (25.3, S["COL3"]),
                (25.3 + L["COL3"] - S["COL3"], L["COL3"]), (45.2, L["COL3"]), (45.55, 12.11), (48.23, 12.11)], W2, B)
# COL2: pin 7 on B.Cu
track("/COL2", [(col(3), BOT), (col(3), 8.4), (14.45, 8.85), (18.05, 8.85), (18.05 + S["COL2"] - 8.85, S["COL2"]), (25.5, S["COL2"]),
                (25.5 + L["COL2"] - S["COL2"], L["COL2"]), (44.6, L["COL2"]), (45.01, 11.60), (48.26, 11.60)], W2, B)
# ROW2: pin 4 - down gap 0-1 on F.Cu - south of the +5V run - a via beside the +5V diagonal - B.Cu to its old diagonal
track("/ROW2", [(col(1), TOP), (gap(0), 6.33), (gap(0), 10.6), (8.4, 11.35), (17.2, 11.35), (17.45, 11.1), (18.75, 11.1)], W2)
via("/ROW2", 18.75, 11.1)
track("/ROW2", [(18.75, 11.1), (18.75 + S["ROW2"] - 11.1, S["ROW2"]), (24.86, S["ROW2"]), (25.5, 13.02), (25.52, 13.02)], W2, B)
# ROW1: pin 3 on F.Cu - south of the +5V run - a via - B.Cu
track("/ROW1", [(col(1), BOT), (col(1), 10.2), (9.62, 10.9), (16.9, 10.9), (17.35, 10.45), (20.55, 10.45), (20.6, 10.5)], W2)
via("/ROW1", 20.6, 10.5)
track("/ROW1", [(20.6, 10.5), (20.6 + S["ROW1"] - 10.5, S["ROW1"]), (25.7, S["ROW1"]), (25.7 + L["ROW1"] - S["ROW1"], L["ROW1"]),
                (44.0, L["ROW1"]), (44.46, 11.10), (48.27, 11.10)], W2, B)
# ROW3: pin 5 on F.Cu north of the +5V run - a via - B.Cu
track("/ROW3", [(col(2), BOT), (col(2), 9.0), (11.88, 9.42), (16.67, 9.42), (16.9, 9.65), (21.0, 9.65), (21.35, 10.0)], W2)
via("/ROW3", 21.35, 10.0)
track("/ROW3", [(21.35, 10.0), (21.35 + S["ROW3"] - 10.0, S["ROW3"]), (25.9, S["ROW3"]), (25.9 + L["ROW3"] - S["ROW3"], L["ROW3"]),
                (41.77, L["ROW3"]), (43.08, 9.79), (48.10, 9.79), (48.24, 9.93)], W2, B)
# COL1: pin 6 - down gap 2-3 on F.Cu - a via - B.Cu
track("/COL1", [(col(2), TOP), (gap(2), 6.33), (gap(2), 8.5), (13.23, 9.0), (17.05, 9.0), (17.3, 9.25), (21.75, 9.25), (22.15, 9.65)], W2)
via("/COL1", 22.15, 9.65)
track("/COL1", [(22.15, 9.65), (22.15 + S["COL1"] - 9.65, S["COL1"]), (26.1, S["COL1"]), (26.1 + L["COL1"] - S["COL1"], L["COL1"]),
                (41.58, L["COL1"]), (43.03, 9.20), (47.97, 9.20), (48.23, 8.94)], W2, B)


# ---- GND for the header's own ground pins (2, 20, 21, 23): the fan-out rings them in on both layers, so they get a
# rail: pin 2 - north-west corner - under the +5V neck on B.Cu (two vias) - along the top between +5V and the signal
# lanes - down to pin 20 - across to pin 21 between the rows - pin 23 on B.Cu.
GW = 0.3
track("GND", [(col(0), TOP), (col(0), 3.9), (8.28, 2.0), (9.2, 2.0)], GW)
via("GND", 9.2, 2.0)
track("GND", [(9.2, 2.0), (11.6, 2.0)], GW, B)
via("GND", 11.6, 2.0)
track("GND", [(11.6, 2.0), (12.0, 1.6), (30.2, 1.6), (30.6, 2.0), (30.6, 3.7), (col(9), TOP)], GW)
track("GND", [(col(9), TOP), (col(10), BOT)], GW)
track("GND", [(col(10), BOT), (col(11), BOT)], GW, B)
# ---------------------------------------------------------------- apply: additions first, removals last
for netname, pts, w, layer, lock in ADD:
    for a, c in zip(pts, pts[1:]):
        tr = pcbnew.PCB_TRACK(b); tr.SetStart(V(*a)); tr.SetEnd(V(*c)); tr.SetWidth(MM(w)); tr.SetLayer(layer)
        tr.SetNet(net(netname)); tr.SetLocked(lock); b.Add(tr)
for netname, x, y, d, dr in VIAS:
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetWidth(MM(d)); v.SetDrill(MM(dr)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(F, B); v.SetNet(net(netname)); v.SetLocked(True); b.Add(v)
for tr in ALL:
    if id(tr) in DEAD: b.Remove(tr)
print("added", sum(len(a[1]) - 1 for a in ADD), "segments", len(VIAS), "vias; removed", len(DEAD))
for d in b.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT) and d.GetText().startswith('DCU carrier H-002'):
        d.SetText('DCU carrier H-002 rev 0.04 (Y12)\nPROVISIONAL OUTLINE 180 x 80 - confirm at V-102 (D-455)')
for r in ('F1', 'TP1', 'R71', 'R72', 'R52', 'R54', 'R53', 'R3', 'C24', 'R51'):
    f = b.FindFootprintByReference(r)
    print(r, ' '.join('%s:%s@%.2f,%.2f' % (p.GetNumber(), p.GetNetname(), T(p.GetPosition().x), T(p.GetPosition().y)) for p in f.Pads()))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(OUT); print("saved", OUT)
