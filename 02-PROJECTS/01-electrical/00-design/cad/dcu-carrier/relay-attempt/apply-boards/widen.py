import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); n=0
for t in b.GetTracks():
    if t.Type()!=pcbnew.PCB_VIA_T and t.GetWidth()<pcbnew.FromMM(0.2): t.SetWidth(pcbnew.FromMM(0.2)); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("widened",n)
