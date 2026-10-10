import pcbnew, sys
b=pcbnew.LoadBoard(sys.argv[1]); MM=pcbnew.FromMM
n=0
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_TRACE_T and t.GetWidth()<MM(0.2): t.SetWidth(MM(0.2)); n+=1
print('widened',n)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2])
