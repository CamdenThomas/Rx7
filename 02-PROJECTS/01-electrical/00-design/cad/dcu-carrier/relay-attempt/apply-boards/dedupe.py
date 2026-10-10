import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); seen=set(); rm=[]
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_VIA_T: k=("v",t.GetPosition().x,t.GetPosition().y,t.GetNetCode())
    else:
        a,c=t.GetStart(),t.GetEnd(); k=("t",t.GetLayer(),min((a.x,a.y),(c.x,c.y)),max((a.x,a.y),(c.x,c.y)),t.GetNetCode())
    if k in seen: rm.append(t)
    else: seen.add(k)
for t in rm: b.Remove(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("dupes",len(rm))
