"""copy every track/via of the SES-imported board into the base board. argv: base imported out"""
import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1]); s=pcbnew.LoadBoard(sys.argv[2])
n=0
for t in s.GetTracks():
    nm=t.GetNetname(); ni=b.FindNet(nm)
    if t.Type()==pcbnew.PCB_VIA_T:
        v=pcbnew.PCB_VIA(b); v.SetPosition(t.GetPosition()); v.SetWidth(t.GetWidth(pcbnew.F_Cu)); v.SetDrill(t.GetDrillValue())
        v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetNet(ni); b.Add(v)
    else:
        c=pcbnew.PCB_TRACK(b); c.SetStart(t.GetStart()); c.SetEnd(t.GetEnd()); c.SetWidth(t.GetWidth()); c.SetLayer(t.GetLayer()); c.SetNet(ni); b.Add(c)
    n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[3]); print("merged",n)
