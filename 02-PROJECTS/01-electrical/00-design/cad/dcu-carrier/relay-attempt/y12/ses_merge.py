"""ses_merge.py base.kicad_pcb session.ses out.kicad_pcb NET[,NET..] : add the session's wires and vias for the
named nets to the base board (nothing else is touched; the base's own tracks all stay)."""
import pcbnew, sys, re
MM = pcbnew.FromMM
base, ses, out = sys.argv[1:4]
want = set(sys.argv[4].split(","))
t = open(ses).read()
res = re.search(r'\(resolution (\w+) (\d+)\)', t)
k = 1.0 / int(res.group(2)) / (1000.0 if res.group(1) == 'um' else 1.0)   # session units -> mm
b = pcbnew.LoadBoard(base)
F, B = pcbnew.F_Cu, pcbnew.B_Cu
i = t.index('(network_out')
# split into nets
nets = re.split(r'\(net ', t[i:])[1:]
nw = nv = 0
for blk in nets:
    name = blk.split()[0].strip('"')
    if name not in want: continue
    ni = b.FindNet(name)
    for m in re.finditer(r'\(wire\s*\(path (\S+) (\d+)((?:\s+-?\d+)+)\s*\)', blk):
        layer = F if m.group(1) == 'F.Cu' else B
        w = int(m.group(2)) * k
        c = [int(v) * k for v in m.group(3).split()]
        pts = [(c[j], -c[j + 1]) for j in range(0, len(c), 2)]
        for a, d in zip(pts, pts[1:]):
            if a == d: continue
            tr = pcbnew.PCB_TRACK(b); tr.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); tr.SetEnd(pcbnew.VECTOR2I(MM(d[0]), MM(d[1])))
            tr.SetWidth(MM(w)); tr.SetLayer(layer); tr.SetNet(ni); b.Add(tr); nw += 1
    for m in re.finditer(r'\(via "?Via\[0-1\]_(\d+):(\d+)_um"?\s+(-?\d+)\s+(-?\d+)', blk):
        v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(MM(int(m.group(3)) * k), MM(-int(m.group(4)) * k)))
        v.SetWidth(MM(int(m.group(1)) / 1000.0)); v.SetDrill(MM(int(m.group(2)) / 1000.0)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(F, B); v.SetNet(ni); b.Add(v); nv += 1
print("added", nw, "segments", nv, "vias")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(out)
