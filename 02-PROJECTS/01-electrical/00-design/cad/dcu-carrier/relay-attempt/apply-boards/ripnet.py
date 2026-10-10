import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); nets=sys.argv[3].split(",")
n=0
for t in list(b.GetTracks()):
    if t.GetNetname() in nets and not t.IsLocked(): b.Remove(t); n+=1
if len(sys.argv)>5:
    f=b.FindFootprintByReference("TP1"); f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(float(sys.argv[4])),pcbnew.FromMM(float(sys.argv[5]))))
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("ripped",n)
