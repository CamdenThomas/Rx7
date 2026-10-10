"""Y11 board step 1: the new parts onto the Y5 board.
argv: orig.kicad_pcb net.net out.kicad_pcb
- nets from the sheet's netlist onto every pad (existing parts: U12 20, J9 12, J2 8 change);
- U9 and its locked neck up 3 mm, R38-R41 left, to open room for the clutch stage U14;
- unlocked copper ripped where parts land and where the clutch stage's power path runs;
- the new footprints placed; U14's OUT neck, AC_CLUTCH to DP-DCU-B 12 and the VS feed drawn locked;
- the GND pours removed (ses_import re-adds them), the comfort pours kept.
"""
import pcbnew, sys, re
sys.path.insert(0, "/private/tmp/claude-501/-Users-crash-dev-Rx7/8e1ab075-e500-475a-9e35-5ee237612812/scratchpad/y6")
MM = pcbnew.FromMM; T = pcbnew.ToMM
SRC, NET, OUT = sys.argv[1:4]
FULL = len(sys.argv) > 4 and sys.argv[4] == "full"
MIN = len(sys.argv) > 4 and sys.argv[4] == "min"
K = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
PLIB = "/Users/crash/dev/Rx7/02-PROJECTS/01-electrical/00-design/cad/dcu-carrier/dcu-carrier.pretty"
F, B = pcbnew.F_Cu, pcbnew.B_Cu


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


# ---------------------------------------------------------------- netlist
def parse(s):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s); st = [[]]
    for t in toks:
        if t == '(':
            st.append([])
        elif t == ')':
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
    return st[0][0]


def find(n, k):
    return [c for c in n if isinstance(c, list) and c and c[0] == k]


def val(n, k):
    f = find(n, k); return f[0][1] if f and len(f[0]) > 1 else None


t = parse(open(NET).read())
comps = {}
for c in find(find(t, 'components')[0], 'comp'):
    props = {}
    for p in find(c, 'property'):
        nm = val(p, 'name'); v = val(p, 'value')
        props[nm] = v if v is not None else ""
    comps[val(c, 'ref')] = dict(value=val(c, 'value'), fp=val(c, 'footprint'), uuid=val(c, 'tstamps'),
                                dnp='dnp' in props, note=props.get('Note'), ds=val(c, 'datasheet') or "")
pinnet = {}
for n in find(find(t, 'nets')[0], 'net'):
    for x in find(n, 'node'):
        pinnet[(val(x, 'ref'), val(x, 'pin'))] = val(n, 'name')

b = pcbnew.LoadBoard(SRC)
nets = {}


def net(name):
    ni = b.FindNet(name)
    if ni is None:
        ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni)
    return ni


# ---------------------------------------------------------------- existing parts: net changes
fps = {f.GetReference(): f for f in b.GetFootprints()}
changed = []
for ref, f in fps.items():
    if ref.startswith("H"):
        continue
    for p in f.Pads():
        want = pinnet.get((ref, p.GetNumber()))
        have = p.GetNetname()
        if want is None:
            if have and not have.startswith("unconnected-"):
                changed.append((ref, p.GetNumber(), have, "(none)"))
            continue
        if want != have:
            changed.append((ref, p.GetNumber(), have, want))
            p.SetNet(net(want))
print("net changes on existing parts:", changed)
gone = set(comps) - set(fps)
print("new parts:", sorted(gone, key=lambda r: (r[0], int(re.sub(r"\D", "", r)))))

# ---------------------------------------------------------------- moves
dy_u9 = 0.0
u9 = fps["U9"]
u9_bb = u9.GetBoundingBox(False)
old_pads = {p.GetNumber(): (T(p.GetPosition().x), T(p.GetPosition().y)) for p in u9.Pads()}
locked_u9 = []
for tr in list(b.GetTracks()):
    if tr.IsLocked() and tr.GetNetname() in ("/MIRROR_HEAT",):
        s = tr.GetStart() if tr.Type() != pcbnew.PCB_VIA_T else tr.GetPosition()
        if 60 < T(s.x) < 71 and 44 < T(s.y) < 50:
            locked_u9.append(tr)
u9.Move(V(0, dy_u9))
for tr in locked_u9:
    tr.Move(V(0, dy_u9))
print("U9 moved with", len(locked_u9), "locked tracks")

# ---------------------------------------------------------------- new footprints
def load(fpid):
    lib, name = fpid.split(":")
    path = PLIB if lib == "dcu-carrier" else (K + lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    assert fp is not None, fpid
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


sheetname, sheetfile = u9.GetSheetname(), u9.GetSheetfile()
placed = []


def crt(f):
    bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    return [T(bb.GetLeft()), T(bb.GetTop()), T(bb.GetRight()), T(bb.GetBottom())]


for f in fps.values():
    f.BuildCourtyardCaches()
    if f.GetCourtyard(pcbnew.F_CrtYd).OutlineCount():
        placed.append((f.GetReference(), crt(f)))


def hitr(r, g=0.25):
    for nm, q in placed:
        if r[0] < q[2] + g and r[2] > q[0] - g and r[1] < q[3] + g and r[3] > q[1] - g:
            hitr.last = nm
            return True
    return r[0] < 0.5 or r[1] < 0.5 or r[2] > 179.5 or r[3] > 79.5


newfp = {}


def make(ref):
    c = comps[ref]
    fp = load(c["fp"])
    fp.SetReference(ref); fp.SetValue(c["value"])
    fp.SetPath(pcbnew.KIID_PATH("/" + c["uuid"]))
    fp.SetSheetname(sheetname); fp.SetSheetfile(sheetfile)
    fp.SetDNP(c["dnp"])
    fp.GetField(pcbnew.FIELD_T_DATASHEET).SetText(c["ds"])
    if c["note"]:
        fld = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, "Note"); fld.SetText(c["note"]); fld.SetVisible(False)
        fld.SetLayer(pcbnew.F_Fab); fp.Add(fld)
    b.Add(fp)
    for p in fp.Pads():
        n = pinnet.get((ref, p.GetNumber()))
        if n:
            p.SetNet(net(n))
    newfp[ref] = fp
    return fp


def put(ref, x, y, rot=0, check=True):
    fp = newfp.get(ref) or make(ref)
    fp.SetOrientationDegrees(rot); fp.SetPosition(V(x, y))
    r = crt(fp)
    if check and hitr(r):
        print("OVERLAP", ref, ["%.2f" % v for v in r], "with", hitr.last)
    placed.append((ref, r))


def pack(refs, x0, y0, x1, y1, rot=0, step=0.25, g=0.25):
    for ref in refs:
        fp = newfp.get(ref) or make(ref)
        fp.SetOrientationDegrees(rot); fp.SetPosition(V(0, 0))
        c = crt(fp); w = c[2] - c[0]; h = c[3] - c[1]
        done = False
        y = y0
        while y + h <= y1 + 1e-6 and not done:
            x = x0
            while x + w <= x1 + 1e-6:
                r = [x, y, x + w, y + h]
                if not hitr(r, g):
                    fp.SetPosition(V(x - c[0], y - c[1])); placed.append((ref, r)); done = True; break
                x += step
            y += step
        if not done:
            print("PACK FAIL", ref, (x0, y0, x1, y1)); fp.SetPosition(V(x0 - c[0], y0 - c[1]))


# the clutch stage on the bottom side, under DP-DCU-B's body right of its pins: OUT (8-14) left toward
# DP-DCU-B 12, IN / DEN / IS / GND (1-7) right toward their resistors, the tab fed from the comfort pour by vias


def bput(ref, x, y, rot=0):
    f_ = newfp.get(ref) or make(ref)
    f_.SetPosition(V(x, y)); f_.Flip(f_.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT); f_.SetOrientationDegrees(rot)
    return f_


bput("U14", 62.5, 74.6, 180)
for _r, _x in (("R62", 67.4), ("R61", 69.6), ("R63", 71.8)):
    _f = bput(_r, _x, 77.9, 90)
    _sig = [p_ for p_ in _f.Pads() if p_.GetNetname() != "GND"][0]
    if T(_sig.GetPosition().y) > 77.9:
        _f.SetOrientationDegrees(270)
# the clutch command's series resistor and pull-down on the bottom side, under the end of U12 P17's old route
bput("R59", 67.4, 30.7, 0); bput("R60", 67.4, 33.0, 0)
# the second expander at the right, between the switches' STATUS line, the radar input and the ADC
put("U13", 160.0, 41.0, 0)
put("C38", 154.9, 41.0, 90)
# the radar input at the top right
put("J12", 166.5, 3.4, 0)
pack(["D11"], 164.0, 8.3, 179.5, 12.6)
pack(["R68", "R69", "R70", "C45"], 164.0, 8.3, 179.5, 12.6, rot=90)
# the ADC and its front ends along the top right, under the servo headers' row
put("U15", 150.0, 15.5, 0)
pack(["C39"], 153.2, 12.2, 156.2, 19.6, rot=90)
pack(["D9"], 156.2, 12.2, 166.0, 18.75)
pack(["R64", "R65"], 156.2, 12.2, 166.0, 18.75, rot=90)
put("C43", 158.2, 17.3, 0)
pack(["D10"], 166.0, 12.2, 179.5, 19.4)
pack(["R66", "R67", "C44"], 166.0, 12.2, 179.5, 19.4, rot=90)
# the transducer lead on the right edge, its tracker beside it
pack(["J11"], 171.0, 30.0, 179.5, 45.0, rot=90)
pack(["U16"], 164.2, 35.6, 171.0, 46.5)
pack(["C40", "C41", "C42"], 164.2, 35.6, 171.0, 46.5, rot=90)
left = set(comps) - set(fps) - set(newfp)
print("unplaced", left)
for ref in sorted(newfp):
    print("  %s %s %.2f,%.2f %s" % (ref, newfp[ref].GetValue()[:24], T(newfp[ref].GetPosition().x), T(newfp[ref].GetPosition().y),
                                   ["%.1f" % v for v in crt(newfp[ref])]))


def padxy(f, num):
    for p in f.Pads():
        if p.GetNumber() == num:
            q = p.GetPosition(); return T(q.x), T(q.y)
    raise KeyError(num)


o10, o11, o12 = padxy(newfp["U14"], "10"), padxy(newfp["U14"], "11"), padxy(newfp["U14"], "12")
tx, ty = padxy(newfp["U14"], "TAB")
j12 = padxy(fps["J9"], "12")
print("U14 OUT pads", o10, o11, o12, "TAB", (tx, ty), "J9.12", j12)

gnd_zones = [z for z in [b.GetArea(i) for i in range(b.GetAreaCount())] if not z.GetIsRuleArea() and z.GetNetname() == "GND"]

# ---------------------------------------------------------------- rip unlocked copper
RIP = [(58, 33.5, 72.5, 57.5),      # U9 old and new, U14
       (47, 50.0, 66.5, 71.0),      # R38-R41, the AC_CLUTCH path to DP-DCU-B 12
       (0, 22.0, 10.0, 40.0),       # U13, C38, R61
       (139.5, 7.0, 180, 22.8),     # U15, its front ends, J12 and the radar input
       (153.0, 29.0, 180, 47.0)]    # J11, U16
gone_tr = 0
for tr in list(b.GetTracks()):
    if tr.IsLocked():
        continue
    pts = [tr.GetPosition()] if tr.Type() == pcbnew.PCB_VIA_T else [tr.GetStart(), tr.GetEnd(), (tr.GetStart() + tr.GetEnd()) / 2]
    hit = FULL or (not MIN and tr.GetNetname() in ("/SEAT_STATUS", "/AC_CLUTCH_CMD"))
    for x0, y0, x1, y1 in ([] if MIN else RIP):
        for p in pts:
            if x0 <= T(p.x) <= x1 and y0 <= T(p.y) <= y1:
                hit = True
    if hit:
        b.Remove(tr); gone_tr += 1
print("ripped", gone_tr)

# ---------------------------------------------------------------- locked copper for the clutch stage
def track(n, pts, w, layer=F):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        tr = pcbnew.PCB_TRACK(b); tr.SetStart(V(x0, y0)); tr.SetEnd(V(x1, y1)); tr.SetWidth(MM(w))
        tr.SetLayer(layer); tr.SetNet(net(n)); tr.SetLocked(True); b.Add(tr)


track("/AC_CLUTCH", [o10, o12], 0.45, B)
x, y = o11
track("/AC_CLUTCH", [(x, y), (x - 1.35, y)], 0.8, B)
track("/AC_CLUTCH", [(x - 1.35, y), (x - 1.35 - (y - j12[1]) + 1.2, j12[1] + 1.2), (j12[0] + 1.2, j12[1] + 1.2), j12], 1.5, B)





def via(n, x, y, d=0.6, dr=0.3):
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetWidth(MM(d)); v.SetDrill(MM(dr))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(F, B); v.SetNet(net(n)); v.SetLocked(True); b.Add(v)


# U14's signals: nested Ls to the three resistors below-right (IS nearest, GND farthest), IN to a via
_top = {}
for _r in ("R61", "R62", "R63"):
    _sig = [p_ for p_ in newfp[_r].Pads() if p_.GetNetname() != "GND"][0]
    _top[_r] = (T(_sig.GetPosition().x), T(_sig.GetPosition().y))
track("/AC_IS", [(65.35, 75.9), _top["R62"][0:1] + (75.9,), _top["R62"]], 0.25, B)
track("/AC_DEN_R", [(65.35, 75.25), (_top["R61"][0], 75.25), _top["R61"]], 0.25, B)
track("/AC_GND", [(65.35, 73.95), (_top["R63"][0], 73.95), _top["R63"]], 0.25, B)
track("/AC_IN", [(65.34, 74.6), (66.6, 74.6)], 0.25, B)
track("/V12C_RAW", [(tx, ty - 3.0), (tx, 70.2), (72.6, 70.2)], 2.0, B)
for _vx in (70.9, 72.1):
    for _vy in (69.7, 70.7):
        via("/V12C_RAW", _vx, _vy, 0.8, 0.4)
via("/AC_IN", 66.6, 74.6)

# ---------------------------------------------------------------- GND pours out (re-added after routing)
if not MIN:
    for z in gnd_zones:
        b.Remove(z)
b.Save(OUT)
print("saved", OUT)
for _r in ("U14", "R59", "R60", "R61", "R62", "R63"):
    print(_r, [(p.GetNumber(), "%.2f,%.2f" % (T(p.GetPosition().x), T(p.GetPosition().y)), p.GetNetname()) for p in newfp[_r].Pads() if p.GetNetname() and not p.GetNetname().startswith("unconnected")])
