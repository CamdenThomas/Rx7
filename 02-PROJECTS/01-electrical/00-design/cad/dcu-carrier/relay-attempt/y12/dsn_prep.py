"""dsn_prep.py in.kicad_pcb out.dsn NET,NET.. : a Specctra DSN for freerouting in which ONLY the named nets exist
as nets. The GND pours are dropped (they give way and are refilled later). Every other net is cut down to one
pin, and its tracks and vias are turned into keepouts, so the router sees them as copper to stay clear of and
never as something to connect (it does not follow KiCad's T-junctions or pours, and otherwise spends its
passes on connections that are not open). The other pours become keepouts too; the project's clearances get
+0.05 mm (freerouting lands a few hundredths under a rule); the named nets' own copper is locked -> 'fix'."""
import pcbnew, sys, re, math
src, dst = sys.argv[1:3]
keep = set(sys.argv[3].split(","))
T = pcbnew.ToMM
b = pcbnew.LoadBoard(src)
zones = []
for z in list(b.Zones()):
    if z.GetIsRuleArea(): continue
    if z.GetNetname() == "GND":
        b.Remove(z); continue
    o = z.Outline()
    zones.append((z.GetLayerName(), [(T(o.CVertex(i).x), T(o.CVertex(i).y)) for i in range(o.TotalVertices())]))
for t in b.GetTracks(): t.SetLocked(True)
tmp = dst + ".raw"
print("export", pcbnew.ExportSpecctraDSN(b, tmp))
t = open(tmp).read()
t = re.sub(r'\(clearance (\d+(?:\.\d+)?)\)', lambda m: '(clearance %g)' % (float(m.group(1)) + 50), t)
t = re.sub(r'\(class ([^ ,()]+),Default ', r'(class \1 ', t)


def poly(layer, pts): return '(polygon %s 0 %s)' % (layer, ' '.join('%d %d' % (round(x * 1000), round(-y * 1000)) for x, y in pts))


add = ['    (keepout "" %s)' % poly(l, p) for l, p in zones]
W, H, e = 180.0, 80.0, 0.6
for L in ('F.Cu', 'B.Cu'):
    for P in ([(0, 0), (W, 0), (W, e), (0, e)], [(0, H - e), (W, H - e), (W, H), (0, H)], [(0, 0), (e, 0), (e, H), (0, H)], [(W - e, 0), (W, 0), (W, H), (W - e, H)]):
        add.append('    (keepout "" %s)' % poly(L, P))
    add.append('    (keepout "" %s)' % poly(L, [(4.0 + 3.5 * math.cos(a * math.pi / 12), 15.0 + 3.5 * math.sin(a * math.pi / 12)) for a in range(24)]))   # H1's screw head

# ---- wires and vias of the nets that are not being routed -> keepouts (DSN units: um, y up)
NAME = r'(?:"([^"]+)"|([^\s()]+))'
kw = kv = 0


def capsule(layer, w, x1, y1, x2, y2):
    r = w / 2.0
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6: ux, uy = 1.0, 0.0
    else: ux, uy = dx / L, dy / L
    a0 = math.atan2(uy, ux)
    pts = []
    for k in range(7):      # cap round (x2, y2)
        a = a0 - math.pi / 2 + k * math.pi / 6
        pts.append((x2 + r * math.cos(a), y2 + r * math.sin(a)))
    for k in range(7):      # cap round (x1, y1)
        a = a0 + math.pi / 2 + k * math.pi / 6
        pts.append((x1 + r * math.cos(a), y1 + r * math.sin(a)))
    return '(polygon %s 0 %s)' % (layer, ' '.join('%d %d' % (round(x), round(y)) for x, y in pts))


def wire(m):
    global kw
    net = m.group(4) or m.group(5)
    if net in keep: return m.group(0)
    c = [float(v) for v in m.group(3).split()]
    for j in range(0, len(c) - 2, 2):
        add.append('    (keepout "" %s)' % capsule(m.group(1), float(m.group(2)), c[j], c[j + 1], c[j + 2], c[j + 3]))
    kw += 1
    return ''


def viar(m):
    global kv
    net = m.group(4) or m.group(5)
    if net in keep: return m.group(0)
    d = float(m.group(1))
    for L in ('F.Cu', 'B.Cu'):
        add.append('    (keepout "" (circle %s %g %s %s))' % (L, d, m.group(2), m.group(3)))
    kv += 1
    return ''


t = re.sub(r'[ \t]*\(wire \(path (\S+) ([\d.]+)((?:\s+-?[\d.]+)+)\s*\)\(net ' + NAME + r'\)\(type \w+\)\)\n', wire, t)
t = re.sub(r'[ \t]*\(via "Via\[0-1\]_(\d+):\d+_um"\s+(-?[\d.]+) (-?[\d.]+) \(net ' + NAME + r'\)\(type \w+\)\)\n', viar, t)
print("to keepouts: wires", kw, "vias", kv)
i = t.index('    (via ')
t = t[:i] + '\n'.join(add) + '\n' + t[i:]
NETRE = re.compile(r'\(net ("?)([^\s")]+)("?)\s*\(pins ([^)]*)\)')


def one(m):
    name = m.group(2)
    pins = m.group(4).split()
    if len(pins) < 2 or name in keep: return m.group(0)
    return '(net %s%s%s\n      (pins %s)' % (m.group(1), name, m.group(3), pins[0])


t, nn = NETRE.subn(one, t)
print("nets seen", nn, "routable", len(keep))
print("wires left", t.count('(wire'), "vias left", len(re.findall(r'\n\s+\(via "', t)) - 0, "keepouts", t.count('(keepout'))
open(dst, 'w').write(t)
