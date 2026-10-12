"""widen.py in out [width=0.25] [below=0.2] : every track narrower than `below` becomes `width` (freerouting's necks)."""
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
w = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
lim = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2
for t in b.GetTracks():
    if t.Type() != pcbnew.PCB_VIA_T and t.GetWidth() < pcbnew.FromMM(lim) - 10:
        t.SetWidth(pcbnew.FromMM(w)); n += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("widened", n)
