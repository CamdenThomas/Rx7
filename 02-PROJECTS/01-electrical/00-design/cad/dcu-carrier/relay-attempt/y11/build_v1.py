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
dy_u9 = -5.7
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
fps["R41"].SetOrientationDegrees(90); fps["R41"].SetPosition(V(47.6, 53.6))

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


# the clutch stage over DP-DCU-B 12's corner: pins 1-7 (IN/DEN/IS/GND) up, 8-14 (OUT) down to the connector
put("U14", 65.2, 52.6, -90)
put("R62", 62.75, 46.2, 180)
put("R63", 67.4, 46.2, 0)
put("R61", 63.2, 43.6, 180)
# the clutch command's series resistor and pull-down on the bottom side, under the end of U12 P17's old route
for _r, _y in (("R59", 30.7), ("R60", 33.0)):
    _f = make(_r); _f.SetPosition(V(67.4, _y)); _f.Flip(_f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT); _f.SetOrientationDegrees(0)
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


track("/AC_CLUTCH", [o10, o12], 0.45)
x, y = o11
track("/AC_CLUTCH", [(x, y), (x, y + 1.3)], 0.8)
track("/AC_CLUTCH", [(x, y + 1.3), (x, j12[1]), j12], 1.5)
track("/V12C_RAW", [(tx + 2.9, ty), (71.2, ty)], 2.0)


def via(n, x, y, d=0.6, dr=0.3):
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetWidth(MM(d)); v.SetDrill(MM(dr))
    v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(F, B); v.SetNet(net(n)); v.SetLocked(True); b.Add(v)


# U14's four signals fan out between R62 and R63: IS, GND and DEN straight to their resistors, IN to a via
track("/AC_IS", [(63.9, 49.75), (63.9, 47.3), (63.66, 47.06), (63.66, 46.2)], 0.25)
track("/AC_GND", [(65.85, 49.75), (65.85, 47.6), (66.49, 46.96), (66.49, 46.2)], 0.25)
track("/AC_DEN_R", [(64.55, 49.75), (64.55, 45.0), (64.11, 44.56), (64.11, 43.6)], 0.25)
track("/AC_IN", [(65.2, 49.75), (65.2, 45.2), (65.35, 44.85)], 0.25)
via("/AC_IN", 65.35, 44.85)
# U9 (moved up 5.7 mm): its four top-row signals fan out left in parallel, the mirror-heat neck drops to a via
for _n, _x, _y in (("/MH_IS", 64.2, 34.3), ("/MH_DEN_R", 64.85, 33.65), ("/MH_IN", 65.5, 33.0), ("/MH_GND", 66.15, 32.35)):
    track(_n, [(_x, 35.45), (_x, _y), (61.0, _y)], 0.25)
track("/MIRROR_HEAT", [(65.5, 42.705), (65.5, 43.4)], 0.8)
via("/MIRROR_HEAT", 65.5, 43.4, 0.8, 0.4)

# ---------------------------------------------------------------- GND pours out (re-added after routing)
if not MIN:
    for z in gnd_zones:
        b.Remove(z)
b.Save(OUT)
print("saved", OUT)
