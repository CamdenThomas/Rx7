import pcbnew,sys
MM=pcbnew.FromMM
b=pcbnew.LoadBoard(sys.argv[1])
f=b.FindFootprintByReference("TP1"); f.SetPosition(pcbnew.VECTOR2I(MM(float(sys.argv[3])),MM(float(sys.argv[4]))))
for t in list(b.GetTracks()):
    if t.GetNetname()=="/SPARE" and not t.IsLocked(): b.Remove(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("moved")
