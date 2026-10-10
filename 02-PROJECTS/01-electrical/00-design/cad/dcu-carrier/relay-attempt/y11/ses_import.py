"""Import freerouting's SES onto the pre-routed board, drop anything it laid on the pour-only
nets, add the GND pours (B.Cu and F.Cu, lowest priority), fill, save."""
import pcbnew, sys
MM=pcbnew.FromMM
b=pcbnew.LoadBoard(sys.argv[1])
ok=pcbnew.ImportSpecctraSES(b, sys.argv[2]); print('import',ok)
pour_only={'/V12C_RAW','/SH_DRV_RTN','/SH_PASS_RTN','/SC_DRV_RTN','/SC_PASS_RTN','/CMF_RTN','PGND'}
drop=[t for t in b.GetTracks() if t.GetNetname() in pour_only and not t.IsLocked()]
for t in drop: b.Remove(t)
print('dropped on pour-only nets',len(drop))
def zone(n,layer,prio,clr,name):
    z=pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet(n)); z.SetZoneName(name)
    o=z.Outline(); o.NewOutline()
    for x,y in ((0,0),(180,0),(180,80),(0,80)): o.Append(MM(x),MM(y))
    z.SetLocalClearance(MM(clr)); z.SetMinThickness(MM(0.25)); z.SetAssignedPriority(prio)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetThermalReliefGap(MM(0.3)); z.SetThermalReliefSpokeWidth(MM(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
if len(sys.argv)<4 or sys.argv[3]!='nopour':
    zone('GND',pcbnew.B_Cu,0,0.3,'GND pour, bottom'); zone('GND',pcbnew.F_Cu,0,0.3,'GND pour, top')
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[-1] if len(sys.argv)>4 else sys.argv[3] if len(sys.argv)>3 and sys.argv[3]!='nopour' else sys.argv[1].replace('.kicad_pcb','_r.kicad_pcb'))
