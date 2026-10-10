import pcbnew, sys
MM=pcbnew.FromMM
b=pcbnew.LoadBoard(sys.argv[1]); g=b.FindNet('GND')
for (x0,y0),(x1,y1) in (((147.9,15.5),(149.6,15.5)),((152.1,16.0),(150.4,16.0))):
    t=pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(MM(x0),MM(y0))); t.SetEnd(pcbnew.VECTOR2I(MM(x1),MM(y1))); t.SetWidth(MM(0.25)); t.SetLayer(pcbnew.F_Cu); t.SetNet(g); t.SetLocked(True); b.Add(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print('ok')
