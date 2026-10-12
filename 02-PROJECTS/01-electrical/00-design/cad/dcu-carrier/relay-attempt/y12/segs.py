"""segs.py board x0 y0 x1 y1 NET[,NET..] : the segments and vias of the nets touching the window"""
import pcbnew, sys
T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
x0, y0, x1, y1 = map(float, sys.argv[2:6])
nets = set(sys.argv[6].split(",")) if len(sys.argv) > 6 else None
def inw(p): return x0 <= T(p.x) <= x1 and y0 <= T(p.y) <= y1
out = {}
for t in b.GetTracks():
    n = t.GetNetname()
    if nets and n not in nets and n.lstrip("/") not in nets: continue
    if t.Type() == pcbnew.PCB_VIA_T:
        if inw(t.GetPosition()):
            out.setdefault(n, []).append("  V  %.2f,%.2f%s" % (T(t.GetPosition().x), T(t.GetPosition().y), " L" if t.IsLocked() else ""))
    elif inw(t.GetStart()) or inw(t.GetEnd()):
        out.setdefault(n, []).append("  %s %.2f,%.2f > %.2f,%.2f w%.2f%s" % ("F" if t.GetLayer() == pcbnew.F_Cu else "B", T(t.GetStart().x), T(t.GetStart().y),
                                     T(t.GetEnd().x), T(t.GetEnd().y), T(t.GetWidth()), " L" if t.IsLocked() else ""))
for n in sorted(out):
    print(n, len(out[n]))
    if "-q" not in sys.argv:
        for l in sorted(out[n]): print(l)
