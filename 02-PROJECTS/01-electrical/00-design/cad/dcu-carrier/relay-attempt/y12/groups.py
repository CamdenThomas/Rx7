"""groups.py board NET : connected groups of a net's pads/tracks/vias (copper contact only, pours ignored),
each with its pads and bounding box; and with -near x0 y0 x1 y1: every item of every net in that window, by layer."""
import pcbnew, sys
T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
name = sys.argv[2]
F, B = pcbnew.F_Cu, pcbnew.B_Cu
if name == "-near":
    x0, y0, x1, y1 = map(float, sys.argv[3:7])
    lay = sys.argv[7] if len(sys.argv) > 7 else None
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if x0 <= T(p.x) <= x1 and y0 <= T(p.y) <= y1: print("V  %-18s %.2f,%.2f" % (t.GetNetname(), T(p.x), T(p.y)))
        else:
            L = "F" if t.GetLayer() == F else "B"
            if lay and L != lay: continue
            a, c = t.GetStart(), t.GetEnd()
            ax, ay, cx, cy = T(a.x), T(a.y), T(c.x), T(c.y)
            if max(ax, cx) < x0 or min(ax, cx) > x1 or max(ay, cy) < y0 or min(ay, cy) > y1: continue
            print("%s  %-18s %.2f,%.2f > %.2f,%.2f w%.2f" % (L, t.GetNetname(), ax, ay, cx, cy, T(t.GetWidth())))
    for p in b.GetPads():
        q = p.GetPosition()
        if x0 <= T(q.x) <= x1 and y0 <= T(q.y) <= y1:
            print("P  %-18s %s.%s %.2f,%.2f" % (p.GetNetname(), p.GetParentFootprint().GetReference(), p.GetNumber(), T(q.x), T(q.y)))
    sys.exit()
ni = b.FindNet(name); nc = ni.GetNetCode()
items = [p for p in b.GetPads() if p.GetNetCode() == nc] + [t for t in b.GetTracks() if t.GetNetCode() == nc]
if '-cut' in sys.argv:      # -cut x0 y0 x1 y1 : ignore tracks lying wholly inside this window
    k = sys.argv.index('-cut'); cx0, cy0, cx1, cy1 = map(float, sys.argv[k + 1:k + 5])
    def inside(t):
        if isinstance(t, pcbnew.PAD): return False
        pts = [t.GetPosition()] if t.Type() == pcbnew.PCB_VIA_T else [t.GetStart(), t.GetEnd()]
        return all(cx0 <= T(q.x) <= cx1 and cy0 <= T(q.y) <= cy1 for q in pts)
    items = [t for t in items if not inside(t)]
n = len(items); par = list(range(n))


def f(i):
    while par[i] != i:
        par[i] = par[par[i]]; i = par[i]
    return i


for i in range(n):
    for j in range(i + 1, n):
        a, c = items[i], items[j]
        for L in (F, B):
            if a.IsOnLayer(L) and c.IsOnLayer(L):
                try:
                    if a.GetEffectiveShape(L).Collide(c.GetEffectiveShape(L), 0):
                        par[f(i)] = f(j); break
                except Exception:
                    pass
g = {}
for i in range(n): g.setdefault(f(i), []).append(items[i])
for grp in sorted(g.values(), key=len, reverse=True):
    pads = [p.GetParentFootprint().GetReference() + "." + p.GetNumber() for p in grp if isinstance(p, pcbnew.PAD)]
    xs = []; ys = []
    for it in grp:
        bb = it.GetBoundingBox(); xs += [T(bb.GetLeft()), T(bb.GetRight())]; ys += [T(bb.GetTop()), T(bb.GetBottom())]
    print(len(grp), "items  bbox %.1f,%.1f..%.1f,%.1f  pads:" % (min(xs), min(ys), max(xs), max(ys)), " ".join(sorted(pads)))
