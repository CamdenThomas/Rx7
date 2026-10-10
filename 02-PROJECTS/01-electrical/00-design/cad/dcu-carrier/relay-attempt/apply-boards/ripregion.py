import pcbnew,sys
T=pcbnew.ToMM
b=pcbnew.LoadBoard(sys.argv[1]); x0,y0,x1,y1=map(float,sys.argv[3:7])
n=0; keep=0
for tr in list(b.GetTracks()):
    pts=[tr.GetPosition()] if tr.Type()==pcbnew.PCB_VIA_T else [tr.GetStart(),tr.GetEnd()]
    if any(x0<=T(p.x)<=x1 and y0<=T(p.y)<=y1 for p in pts):
        if tr.IsLocked() and tr.GetNetname() not in ("/PNL_SDA","/PNL_SCL","/+5V_PNL","/ENC_SEAT_PASS_A","+5V") : keep+=1; continue
        b.Remove(tr); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("ripped",n,"kept locked",keep)
